"""
engine.py  (v2)
---------------
The five layers of the symptom checker, in execution order.

    Layer 0   red flags + critical lab values   hard override, model not consulted
    Layer 1   ML model                          probability distribution
    Layer 2   adaptive questionnaire            chosen by information gain
    Layer 3   ML model re-run                   with the new answers
    Layer 4   context modifiers                 explained to the user, never silent

URGENCY IS THE PRIMARY OUTPUT. The condition name is secondary and is presented
as "what this could be", never as a diagnosis.

URGENCY POLICY (measured, not guessed - see model_meta.json)
Urgency is taken as the worst case among candidates scoring at least 50% of the
leader's probability, plus any emergency-level candidate above 5%. On the held
out test set that moves under-calling from 5.66% to 2.45% and missed
emergencies from 12.50% to 3.75%, while over-calling stays at 15% rather than
the 44% a plain top-3 rule produces.

ASYMMETRIC EVIDENCE
Lab values may raise urgency. They may never lower it. See escalate().
"""

import json
import math
import threading

import numpy as np
import pandas as pd
from django.conf import settings

from ml_model.disease_data import DISEASES, SENSITIVE_CONDITIONS
from ml_model.knowledge_base import (
    CONTEXT_MODIFIERS, CONTEXT_QUESTIONS, EMERGENCY_NUMBER, LAB_TESTS,
    MENTAL_HEALTH_HELPLINE, PREGNANCY_ESCALATE, SYMPTOM_GROUPS, SYMPTOM_LABELS,
    URGENCY_INFO, check_red_flags, context_to_features, escalate,
)

_lock = threading.Lock()
_bundle = None
_meta = None

LEADER_FRACTION = 0.50   # candidate counts if p >= this share of the leader
EMERGENCY_FLOOR = 0.05   # an emergency candidate counts from this probability up
MAX_QUESTIONS = 5


# ---------------------------------------------------------------------------
# model loading
# ---------------------------------------------------------------------------

def _load():
    global _bundle, _meta
    if _bundle is not None:
        return _bundle
    with _lock:
        if _bundle is None:
            import joblib
            if not settings.ML_MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Trained model not found at {settings.ML_MODEL_PATH}. "
                    "Run:  python ml_model/train_model.py"
                )
            _bundle = joblib.load(settings.ML_MODEL_PATH)
            if settings.ML_META_PATH.exists():
                _meta = json.loads(settings.ML_META_PATH.read_text())
    return _bundle


def model_metadata():
    _load()
    return _meta or {}


def model_is_ready():
    try:
        _load()
        return True
    except Exception:
        return False


def symptom_groups():
    return SYMPTOM_GROUPS


def label_for(key):
    return SYMPTOM_LABELS.get(key, key.replace("_", " ").capitalize())


# ---------------------------------------------------------------------------
# feature vector assembly
# ---------------------------------------------------------------------------

def _vector(features, active):
    active = set(active)
    return pd.DataFrame([[1 if f in active else 0 for f in features]], columns=features)


def _distribution(active):
    """Layer 1 / Layer 3. Returns [(condition, probability)] sorted desc."""
    bundle = _load()
    model, features = bundle["model"], bundle["features"]
    proba = model.predict_proba(_vector(features, active))[0]
    return sorted(zip(model.classes_, proba), key=lambda t: -t[1])


# ---------------------------------------------------------------------------
# Layer 2 - adaptive questionnaire, chosen by information gain
# ---------------------------------------------------------------------------

def _entropy(probs):
    return -sum(p * math.log(p + 1e-12, 2) for p in probs if p > 0)


def next_questions(active, asked, limit=3, candidate_pool=8):
    """
    Pick the symptoms worth asking about next.

    For each unanswered symptom we estimate how much the answer would reduce
    uncertainty over the current candidate conditions:

        gain = H(D) - [ P(s) * H(D | s=yes) + (1-P(s)) * H(D | s=no) ]

    Candidates are restricted to symptoms that actually appear in the leading
    conditions, which keeps this to a few dozen model calls.
    """
    bundle = _load()
    model, features = bundle["model"], bundle["features"]

    ranked = _distribution(active)
    top = [name for name, p in ranked[:candidate_pool] if p > 0.01]
    if len(top) < 2:
        return []

    base_probs = [p for _, p in ranked[:candidate_pool]]
    total = sum(base_probs) or 1.0
    base_probs = [p / total for p in base_probs]
    base_h = _entropy(base_probs)
    if base_h < 0.35:            # already confident, stop asking
        return []

    active_set = set(active)
    asked_set = set(asked)

    pool = []
    for name in top:
        profile = DISEASES[name]
        for s in profile["primary"] + profile["secondary"]:
            if s not in active_set and s not in asked_set:
                pool.append(s)
    pool = list(dict.fromkeys(pool))
    if not pool:
        return []

    # how likely each candidate symptom is, weighted by current beliefs
    weights = dict(zip(top, base_probs))
    prior = {}
    for s in pool:
        prior[s] = sum(
            w * (0.86 if s in DISEASES[d]["primary"]
                 else 0.34 if s in DISEASES[d]["secondary"] else 0.02)
            for d, w in weights.items()
        )

    def conditional_entropy(extra_on, extra_off):
        vec = _vector(features, active_set | extra_on)
        p = model.predict_proba(vec)[0]
        idx = [list(model.classes_).index(t) for t in top]
        sub = np.array([p[i] for i in idx])
        s = sub.sum() or 1.0
        return _entropy(sub / s)

    scored = []
    for s in pool[:45]:
        p_yes = min(max(prior[s], 0.03), 0.97)
        h_yes = conditional_entropy({s}, set())
        h_no = base_h                      # cheap approximation for "no"
        gain = base_h - (p_yes * h_yes + (1 - p_yes) * h_no)
        scored.append((gain, s))

    scored.sort(reverse=True)
    picked = [s for gain, s in scored[:limit] if gain > 0.02]

    # explain *why* we are asking: which conditions this would separate
    out = []
    for s in picked:
        has = [d for d in top[:4] if s in DISEASES[d]["primary"] + DISEASES[d]["secondary"]]
        hasnt = [d for d in top[:4] if d not in has]
        if has and hasnt:
            why = f"this helps tell {has[0]} apart from {hasnt[0]}"
        elif has:
            why = f"this would support {has[0]}"
        else:
            why = "this narrows down the possibilities"
        out.append({"key": s, "label": label_for(s), "why": why})
    return out


# ---------------------------------------------------------------------------
# lab values
# ---------------------------------------------------------------------------

def interpret_labs(values):
    """
    Turn {'haemoglobin': 9.2} into flags, plain-language notes and any critical
    escalation. Values already outside the plausible range are rejected upstream.
    """
    flags, notes, critical = [], [], []
    for key, raw in (values or {}).items():
        test = LAB_TESTS.get(key)
        if test is None or raw is None:
            continue
        value = float(raw)
        low, high = test["normal"]

        if value < low:
            direction = "low"
            verdict = "below the usual range"
        elif value > high:
            direction = "high"
            verdict = "above the usual range"
        else:
            direction = "normal"
            verdict = "within the usual range"

        flag = test.get("flags", {}).get(direction)
        if flag:
            flags.append(flag)

        notes.append({
            "key": key,
            "label": test["label"],
            "value": value,
            "unit": test["unit"],
            "direction": direction,
            "verdict": verdict,
            "normal_text": test["normal_text"],
            "plain": test["plain"],
        })

        cl, ch = test.get("critical_low"), test.get("critical_high")
        if cl is not None and value <= cl:
            critical.append(f"{key}_low")
        if ch is not None and value >= ch:
            critical.append(f"{key}_high")

    return {"flags": flags, "notes": notes, "critical": critical}


# ---------------------------------------------------------------------------
# Layer 4 - explainable modifiers
# ---------------------------------------------------------------------------

def _apply_modifiers(ranked, context_features, lab_flags):
    scores = dict(ranked)
    explanations = []

    for mod in CONTEXT_MODIFIERS:
        if mod["disease"] not in scores:
            continue
        if not all(n in context_features for n in mod["needs"]):
            continue
        before = scores[mod["disease"]]
        if before < 0.005:
            continue
        scores[mod["disease"]] = before * mod["factor"]
        explanations.append({
            "disease": mod["disease"], "reason": mod["reason"],
            "direction": "up" if mod["factor"] > 1 else "down",
            "before": round(before * 100, 1),
        })

    # lab evidence, expressed through the same explainable mechanism
    from ml_model.disease_data import LAB_ASSOCIATIONS
    for disease, assoc in LAB_ASSOCIATIONS.items():
        if disease not in scores:
            continue
        for flag, strength in assoc.items():
            if flag in lab_flags and strength >= 0.5 and scores[disease] > 0.005:
                before = scores[disease]
                scores[disease] = before * (1 + strength)
                explanations.append({
                    "disease": disease,
                    "reason": f"your lab result ({flag.replace('_', ' ')}) fits this",
                    "direction": "up", "before": round(before * 100, 1),
                })

    total = sum(scores.values()) or 1.0
    normalised = sorted(((k, v / total) for k, v in scores.items()), key=lambda t: -t[1])

    # Attach the resulting percentage, then keep only explanations the user can
    # act on: a note saying "chronic cough raised TB" is confusing on a page
    # where TB is not shown and the person has no cough.
    final = dict(normalised)
    visible = {name for name, p in normalised[:4] if p > 0.02}
    for e in explanations:
        e["after"] = round(final.get(e["disease"], 0) * 100, 1)
    explanations = [e for e in explanations
                    if e["disease"] in visible and abs(e["after"] - e["before"]) >= 1.0]
    return normalised, explanations


# ---------------------------------------------------------------------------
# urgency
# ---------------------------------------------------------------------------

def _urgency_from(ranked, context_answers):
    """Worst case among plausible candidates. See the module docstring."""
    if not ranked:
        return "prompt", []
    leader = ranked[0][1]
    considered = []
    for name, p in ranked[:6]:
        u = DISEASES[name]["urgency"]
        if p >= LEADER_FRACTION * leader:
            considered.append((name, p, u))
        elif u == "emergency" and p >= EMERGENCY_FLOOR:
            considered.append((name, p, u))

    if not considered:
        considered = [(ranked[0][0], ranked[0][1], DISEASES[ranked[0][0]]["urgency"])]

    level = "routine"
    for _, _, u in considered:
        level = escalate(level, u)

    reasons = []
    top_name = ranked[0][0]
    for name, p, u in considered:
        if name != top_name and URGENCY_INFO[u]["rank"] > URGENCY_INFO[DISEASES[top_name]["urgency"]]["rank"]:
            reasons.append(
                f"{name} is also possible ({p*100:.0f}%) and would need attention sooner"
            )

    # pregnancy escalation
    preg = (context_answers or {}).get("pregnancy") in ("yes", "maybe")
    if preg:
        for name, _, _ in considered:
            if name in PREGNANCY_ESCALATE:
                new = escalate(level, "urgent")
                if new != level:
                    reasons.append(
                        f"pregnancy makes {name} more serious, so this has been raised"
                    )
                level = new
                break
    return level, reasons


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------

def assess(symptoms, context=None, labs=None, asked=None):
    """
    Run the full assessment.

    Returns a dict with 'kind' one of:
        empty      nothing selected
        emergency  Layer 0 fired - symptom red flag or critical lab value
        result     a normal assessment
    """
    selected = [s for s in (symptoms or []) if s in SYMPTOM_LABELS]
    context = context or {}
    labs = labs or {}

    if not selected and not labs:
        return {"kind": "empty"}

    lab_read = interpret_labs(labs)

    # ---- Layer 0a: symptom red flags --------------------------------------
    flag = check_red_flags(selected)
    if flag:
        return {
            "kind": "emergency", "source": "symptoms", "flag": flag,
            "number": EMERGENCY_NUMBER, "selected": selected,
            "selected_labels": [label_for(s) for s in selected],
            "labs": lab_read,
        }

    # ---- Layer 0b: critical lab values ------------------------------------
    if lab_read["critical"]:
        from ml_model.knowledge_base import LAB_CRITICAL_MESSAGES
        code = lab_read["critical"][0]
        title, message = LAB_CRITICAL_MESSAGES.get(
            code, ("Abnormal lab result", "This result needs a doctor's attention today.")
        )
        return {
            "kind": "emergency", "source": "lab",
            "flag": {"code": code, "title": title, "message": message},
            "number": EMERGENCY_NUMBER, "selected": selected,
            "selected_labels": [label_for(s) for s in selected],
            "labs": lab_read,
        }

    # ---- Layers 1 and 3 ----------------------------------------------------
    ctx_features = context_to_features(context)
    active = list(selected) + ctx_features + lab_read["flags"]
    ranked = _distribution(active)

    # ---- Layer 4 -----------------------------------------------------------
    ranked, explanations = _apply_modifiers(ranked, set(ctx_features), set(lab_read["flags"]))

    urgency, urgency_reasons = _urgency_from(ranked, context)

    results = [{"disease": n, "confidence": round(p * 100, 1)}
               for n, p in ranked[:4] if p > 0.02]
    if not results:
        results = [{"disease": ranked[0][0], "confidence": round(ranked[0][1] * 100, 1)}]

    top = results[0]
    spread = (results[0]["confidence"] - results[1]["confidence"]) if len(results) > 1 else 100
    low_information = len(selected) < 3 or spread < 12

    questions = next_questions(active, asked or [], limit=3) if len(selected) >= 1 else []

    return {
        "kind": "result",
        "urgency": urgency,
        "urgency_info": URGENCY_INFO[urgency],
        "urgency_reasons": urgency_reasons,
        "results": results,
        "top": top,
        "alternatives": results[1:],
        "explanations": explanations,
        "labs": lab_read,
        "selected": selected,
        "selected_labels": [label_for(s) for s in selected],
        "symptom_count": len(selected),
        "low_information": low_information,
        "questions": questions,
        # The mental-health support panel is only shown when the signal is real.
        # Surfacing it off a 2% guess would be both alarming and useless.
        "sensitive": (top["disease"] in SENSITIVE_CONDITIONS
                      and top["confidence"] >= 15.0),
        "mental_health_helpline": MENTAL_HEALTH_HELPLINE,
        "context": context,
    }
