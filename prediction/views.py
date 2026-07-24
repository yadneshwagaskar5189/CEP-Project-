"""
Views for the symptom checker.

The assessment is a four-step flow held in the session:

    symptoms  ->  context (+ optional lab report)  ->  follow-up questions  ->  result

Nothing personal is stored. Uploaded images are read in memory and discarded in
the same request; only the confirmed numeric values move forward, and only after
the user has confirmed them against the cropped image.
"""

from django.contrib import messages
from django.shortcuts import redirect, render

from hospitals.models import Hospital
from ml_model.knowledge_base import CONTEXT_QUESTIONS, LAB_TESTS

from . import engine, report_ocr
from .models import DiseaseInfo, SymptomCheck

SESSION_KEY = "assessment"


# ---------------------------------------------------------------------------
# session helpers
# ---------------------------------------------------------------------------

def _state(request):
    return request.session.get(SESSION_KEY) or {
        "symptoms": [], "context": {}, "labs": {}, "asked": [],
        "city": "", "used_ocr": False, "answered": 0,
    }


def _save(request, state):
    request.session[SESSION_KEY] = state
    request.session.modified = True


def _cities():
    return (Hospital.objects.filter(is_active=True)
            .values_list("city", flat=True).distinct().order_by("city"))


def _recommend_hospitals(specialisation, city="", limit=4):
    qs = (Hospital.objects.filter(is_active=True, specialisations__name=specialisation)
          .prefetch_related("bed_records", "specialisations").distinct())
    in_city = list(qs.filter(city__iexact=city)) if city else []
    hospitals = in_city or list(qs)
    # Largest capacity first - matches what the bed panel now shows, since
    # free-bed count is no longer displayed.
    hospitals.sort(key=lambda h: (h.beds.total_beds if h.beds else -1), reverse=True)
    return hospitals[:limit]


# ---------------------------------------------------------------------------
# Step 1 - symptoms
# ---------------------------------------------------------------------------

def start(request):
    state = _state(request)

    if request.method == "POST":
        selected = request.POST.getlist("symptoms")
        if not selected:
            messages.error(request, "Choose at least one symptom so the checker has "
                                    "something to work with.")
        else:
            state.update({"symptoms": selected, "asked": [], "answered": 0})
            state["city"] = request.POST.get("city", "")
            _save(request, state)
            return redirect("prediction:context")

    return render(request, "prediction/step_symptoms.html", {
        "groups": engine.symptom_groups(),
        "selected": state["symptoms"],
        "cities": _cities(),
        "selected_city": state.get("city", ""),
        "model_ready": engine.model_is_ready(),
        "step": 1,
    })


# ---------------------------------------------------------------------------
# Step 2 - context and lab report
# ---------------------------------------------------------------------------

def context(request):
    state = _state(request)
    if not state["symptoms"]:
        return redirect("prediction:start")

    if request.method == "POST":
        answers = {}
        for q in CONTEXT_QUESTIONS:
            if q.get("multi"):
                values = request.POST.getlist(q["key"])
                if values:
                    answers[q["key"]] = values
            else:
                value = request.POST.get(q["key"])
                if value:
                    answers[q["key"]] = value
        state["context"] = answers
        _save(request, state)
        return redirect("prediction:questions")

    answers = state.get("context", {})
    labs = state.get("labs", {})

    # Options carry their own checked state. Working it out in the template
    # would mean indexing a dict by a loop variable, which Django cannot do.
    question_rows = []
    for q in CONTEXT_QUESTIONS:
        chosen = answers.get(q["key"]) or []
        if isinstance(chosen, str):
            chosen = [chosen]
        question_rows.append({
            "key": q["key"],
            "question": q["question"],
            "why": q["why"],
            "multi": bool(q.get("multi")),
            "options": [
                {"value": value, "label": label, "checked": value in chosen}
                for value, label in q["options"]
            ],
        })

    lab_rows = [
        {
            "label": LAB_TESTS[key]["label"] if key in LAB_TESTS else key,
            "unit": LAB_TESTS.get(key, {}).get("unit", ""),
            "value": value,
        }
        for key, value in labs.items()
    ]

    return render(request, "prediction/step_context.html", {
        "questions": question_rows,
        "labs": labs,
        "lab_rows": lab_rows,
        "ocr_available": report_ocr.ocr_available(),
        "step": 2,
    })


# ---------------------------------------------------------------------------
# Step 2b - lab report upload, OCR, confirmation, manual entry
# ---------------------------------------------------------------------------

def labs(request):
    """
    Upload path and manual path share one screen and one schema, because the
    manual form IS the confirmation UI for OCR. OCR only ever pre-fills.
    """
    state = _state(request)
    existing = state.get("labs", {})

    def manual_rows(skip=()):
        """
        Rows for the type-it-in table.

        Tests already shown in the OCR confirmation block are skipped. Both
        blocks live in one <form> and use the same field names, so rendering a
        test twice would put two `value_<key>` inputs in the same POST - and a
        QueryDict returns the *last* one, meaning an untouched manual field
        would silently wipe out the value the user just confirmed.
        """
        return [
            {
                "key": key,
                "label": test["label"],
                "unit": test.get("unit", ""),
                "normal_text": test.get("normal_text", ""),
                "value": existing.get(key, ""),
            }
            for key, test in LAB_TESTS.items()
            if key not in skip
        ]

    ctx = {
        "lab_tests": LAB_TESTS,
        "ocr_available": report_ocr.ocr_available(),
        "existing": existing,
        "manual_rows": manual_rows(),
        "step": 2,
    }

    if request.method == "POST":
        action = request.POST.get("action")

        # ---- run OCR on an uploaded photo ---------------------------------
        if action == "extract":
            upload = request.FILES.get("report")
            if not upload:
                messages.error(request, "Choose a photo of the report first.")
                return render(request, "prediction/step_labs.html", ctx)
            if upload.size > 12 * 1024 * 1024:
                messages.error(request, "That image is too large. Please use a photo "
                                        "under 12 MB.")
                return render(request, "prediction/step_labs.html", ctx)

            result = report_ocr.extract_from_image(upload)
            if result.get("error"):
                messages.error(request, result["error"])
            elif not result["found"]:
                messages.warning(
                    request,
                    "No values could be read from that photo. Try again in better light "
                    "with the page flat, or type the values in below."
                )
            ctx["extracted"] = result
            ctx["manual_rows"] = manual_rows(
                skip={hit["test"] for hit in result.get("found", [])}
            )
            state["used_ocr"] = True
            _save(request, state)
            return render(request, "prediction/step_labs.html", ctx)

        # ---- accept confirmed values ---------------------------------------
        values, warnings = report_ocr.confirmed_values(request.POST)
        for w in warnings:
            messages.warning(request, w)
        state["labs"] = values
        _save(request, state)
        if values:
            messages.success(request, f"{len(values)} lab value"
                                      f"{'s' if len(values) != 1 else ''} added.")
        return redirect("prediction:context")

    return render(request, "prediction/step_labs.html", ctx)


# ---------------------------------------------------------------------------
# Step 3 - adaptive follow-up questions
# ---------------------------------------------------------------------------

def questions(request):
    state = _state(request)
    if not state["symptoms"]:
        return redirect("prediction:start")

    if request.method == "POST":
        # The radio itself carries the answer. An earlier version mirrored it
        # into a hidden checkbox with JavaScript, which meant every "yes" was
        # silently dropped on any device with JS turned off - the wrong way to
        # fail for the people this is built for.
        shown = request.POST.getlist("shown")
        for key in shown:
            if request.POST.get(f"a_{key}") == "yes" and key not in state["symptoms"]:
                state["symptoms"].append(key)
            if key not in state["asked"]:
                state["asked"].append(key)
        state["answered"] = state.get("answered", 0) + len(shown)
        _save(request, state)

        if request.POST.get("more") == "1" and state["answered"] < engine.MAX_QUESTIONS:
            return redirect("prediction:questions")
        return redirect("prediction:result")

    outcome = engine.assess(state["symptoms"], state.get("context"),
                            state.get("labs"), state.get("asked"))

    # emergencies skip straight past the questionnaire
    if outcome["kind"] != "result" or not outcome.get("questions"):
        return redirect("prediction:result")
    if state.get("answered", 0) >= engine.MAX_QUESTIONS:
        return redirect("prediction:result")

    return render(request, "prediction/step_questions.html", {
        "outcome": outcome,
        "questions": outcome["questions"],
        "answered": state.get("answered", 0),
        "max_questions": engine.MAX_QUESTIONS,
        "step": 3,
    })


# ---------------------------------------------------------------------------
# Step 4 - result
# ---------------------------------------------------------------------------

def result(request):
    state = _state(request)
    if not state["symptoms"] and not state.get("labs"):
        return redirect("prediction:start")

    outcome = engine.assess(state["symptoms"], state.get("context"),
                            state.get("labs"), state.get("asked"))
    city = state.get("city", "")

    if outcome["kind"] == "empty":
        return redirect("prediction:start")

    if outcome["kind"] == "emergency":
        SymptomCheck.objects.create(
            symptoms=",".join(state["symptoms"]),
            red_flag=outcome["flag"]["code"], urgency="emergency",
            used_labs=bool(state.get("labs")), used_ocr=state.get("used_ocr", False),
            answered_questions=state.get("answered", 0), city=city,
        )
        qs = Hospital.objects.filter(is_active=True, has_emergency=True)
        if city:
            qs = qs.filter(city__iexact=city) or qs
        return render(request, "prediction/emergency.html", {
            "outcome": outcome,
            "emergency_hospitals": qs.prefetch_related("bed_records")[:4],
        })

    top = outcome["top"]
    SymptomCheck.objects.create(
        symptoms=",".join(state["symptoms"]),
        predicted_disease=top["disease"], confidence=top["confidence"],
        urgency=outcome["urgency"], used_labs=bool(state.get("labs")),
        used_ocr=state.get("used_ocr", False),
        answered_questions=state.get("answered", 0), city=city,
    )

    info = DiseaseInfo.objects.filter(name=top["disease"]).first()
    alt_info = {d.name: d for d in DiseaseInfo.objects.filter(
        name__in=[r["disease"] for r in outcome["alternatives"]])}

    # flattened for the template - Django templates cannot index a dict by a
    # variable key, so the join is done here instead
    alternatives = [
        {
            "disease": row["disease"],
            "confidence": row["confidence"],
            "specialisation": getattr(alt_info.get(row["disease"]), "specialisation", ""),
        }
        for row in outcome["alternatives"]
    ]

    return render(request, "prediction/result.html", {
        "outcome": outcome,
        "info": info,
        "alternatives": alternatives,
        "context_display": _context_display(state.get("context")),
        "hospitals": _recommend_hospitals(info.specialisation, city) if info else [],
        "step": 4,
    })


def _context_display(answers):
    """
    Turn {'duration': 'chronic', 'history': ['diabetes']} into readable rows.

    The raw codes are meaningless to a user, and a string answer must not be
    passed through Django's `join` filter - it would split it into letters.
    """
    rows = []
    for q in CONTEXT_QUESTIONS:
        value = (answers or {}).get(q["key"])
        if not value:
            continue
        chosen = value if isinstance(value, (list, tuple)) else [value]
        labels = [dict(q["options"]).get(code, code) for code in chosen]
        rows.append({"question": q["question"], "answer": ", ".join(labels)})
    return rows


def reset(request):
    request.session.pop(SESSION_KEY, None)
    return redirect("prediction:start")
