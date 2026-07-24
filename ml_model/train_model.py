"""
train_model.py  (v2)
--------------------
Trains the symptom -> condition classifier.

    python ml_model/train_model.py

Outputs into ml_model/:
    disease_model.pkl   trained model + the exact feature order it expects
    model_meta.json     top-1 / top-3 accuracy, per-class scores, confusion matrix

WHY THE ACCURACY IS LOWER THAN THE v1 MODEL
-------------------------------------------
v1 had 30 conditions and scored 98%. This has 70, and scores lower. That is the
correct direction. More conditions means more genuine overlap - a great many
things present as fever plus fatigue - and a model that still scored 98% across
70 classes would be telling you the generated data is too tidy, not that the
model is good.

Two things are done here to keep the number honest:

1. EXACT DUPLICATE ROWS ARE REMOVED before the split. The widely used public
   symptom-disease datasets contain heavy duplication, which is why projects
   built on them routinely report 100% accuracy. A duplicate row appearing in
   both train and test is memorisation being scored as skill.

2. TOP-3 ACCURACY IS REPORTED ALONGSIDE TOP-1. The results page shows
   alternatives, so top-3 is the metric that matches what the user actually
   sees. It is also the honest one for a triage tool.

URGENCY ACCURACY is reported too, and it matters more than either. Getting the
condition wrong but the urgency right still sends the person to the right place
at the right time.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml_model.disease_data import CONTEXT_PRIORS, DISEASES, LAB_ASSOCIATIONS  # noqa: E402
from ml_model.knowledge_base import (  # noqa: E402
    ALL_FEATURES, CONTEXT_FEATURES, CONTEXT_MODIFIERS, LAB_FEATURES, SYMPTOMS,
    URGENCY_INFO,
)

HERE = Path(__file__).resolve().parent

SAMPLES_PER_DISEASE = 320
P_PRIMARY = 0.86
P_SECONDARY = 0.34
P_NOISE = 0.014
P_CTX_DEFAULT = 0.12
P_LAB_NOISE = 0.02
RANDOM_STATE = 42

# --- UNDER-REPORTING ------------------------------------------------------
# A textbook case lists eight symptoms. A real person ticks three or four -
# they forget some, do not think others are relevant, and do not know the
# clinical vocabulary for the rest. Generating textbook-complete cases makes
# the classes artificially separable and inflates accuracy.
#
# Each generated case therefore gets its own "thoroughness", drawn from a beta
# distribution: most people report partially, a few report almost everything.
# This single change is what makes the reported accuracy believable.
REPORTING_ALPHA = 4.0
REPORTING_BETA = 2.2
MIN_REPORTED = 2


def build_dataset():
    """Generate the binary feature matrix and label vector."""
    rng = np.random.default_rng(RANDOM_STATE)
    idx = {name: i for i, name in enumerate(ALL_FEATURES)}
    n = len(ALL_FEATURES)

    ctx_idx = [idx[f] for f in CONTEXT_FEATURES]
    lab_idx = [idx[f] for f in LAB_FEATURES]
    sym_idx = [idx[f] for f in SYMPTOMS]

    rows, labels = [], []
    for disease, profile in DISEASES.items():
        primary = [idx[s] for s in profile["primary"]]
        secondary = [idx[s] for s in profile["secondary"]]
        ctx_prior = CONTEXT_PRIORS.get(disease, {})
        lab_prior = LAB_ASSOCIATIONS.get(disease, {})

        for _ in range(SAMPLES_PER_DISEASE):
            row = np.zeros(n, dtype=np.int8)

            # background noise across symptoms only
            noise = rng.random(len(sym_idx)) < P_NOISE
            row[np.array(sym_idx)[noise]] = 1

            row[primary] = (rng.random(len(primary)) < P_PRIMARY).astype(np.int8)
            row[secondary] = np.maximum(
                row[secondary], (rng.random(len(secondary)) < P_SECONDARY).astype(np.int8)
            )

            # context: informative where we have a prior, weak elsewhere
            for f in CONTEXT_FEATURES:
                p = ctx_prior.get(f, P_CTX_DEFAULT)
                if rng.random() < p:
                    row[idx[f]] = 1

            # labs: most checks are simply not done, so these stay mostly zero
            for f in LAB_FEATURES:
                p = lab_prior.get(f, P_LAB_NOISE)
                if rng.random() < p:
                    row[idx[f]] = 1

            # --- apply under-reporting to the symptom columns only ---------
            thoroughness = rng.beta(REPORTING_ALPHA, REPORTING_BETA)
            present = [i for i in sym_idx if row[i] == 1]
            for i in present:
                if rng.random() > thoroughness:
                    row[i] = 0

            # never emit a case with nothing reported at all
            if row[sym_idx].sum() < MIN_REPORTED:
                for i in rng.permutation(primary)[:MIN_REPORTED]:
                    row[i] = 1

            rows.append(row)
            labels.append(disease)

    X = pd.DataFrame(np.array(rows), columns=ALL_FEATURES)
    y = pd.Series(labels, name="condition")
    return X, y


def top_k_accuracy(model, X_test, y_test, k=3):
    proba = model.predict_proba(X_test)
    classes = np.array(model.classes_)
    top_k = classes[np.argsort(-proba, axis=1)[:, :k]]
    return float(np.mean([truth in row for truth, row in zip(y_test, top_k)]))


def main():
    print("Generating dataset (with under-reporting simulation)...")
    X, y = build_dataset()
    print(f"  raw samples : {len(X)}")

    # --- remove exact duplicates -------------------------------------------
    combined = X.copy()
    combined["__label"] = y.values
    before = len(combined)
    combined = combined.drop_duplicates()
    removed = before - len(combined)
    y = combined.pop("__label")
    X = combined.reset_index(drop=True)
    y = y.reset_index(drop=True)
    print(f"  duplicates removed : {removed} ({100*removed/before:.2f}%)")
    print(f"  usable samples     : {len(X)}")
    print(f"  features           : {X.shape[1]}  "
          f"({len(SYMPTOMS)} symptoms + {len(CONTEXT_FEATURES)} context + "
          f"{len(LAB_FEATURES)} lab)")
    print(f"  classes            : {y.nunique()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    print("\nTraining Random Forest...")
    model = RandomForestClassifier(
        n_estimators=180, min_samples_leaf=4, max_depth=26,
        class_weight="balanced",
        random_state=RANDOM_STATE, n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    top1 = accuracy_score(y_test, y_pred)
    top3 = top_k_accuracy(model, X_test, y_test, 3)
    top5 = top_k_accuracy(model, X_test, y_test, 5)

    # --- urgency accuracy: the metric that actually matters -----------------
    urgency_of = {n: p["urgency"] for n, p in DISEASES.items()}
    true_u = [urgency_of[c] for c in y_test]
    pred_u = [urgency_of[c] for c in y_pred]
    urgency_exact = accuracy_score(true_u, pred_u)
    rank = {k: v["rank"] for k, v in URGENCY_INFO.items()}
    under = float(np.mean([rank[p] < rank[t] for t, p in zip(true_u, pred_u)]))

    print(f"  Top-1 accuracy       : {top1:.4f}")
    print(f"  Top-3 accuracy       : {top3:.4f}")
    print(f"  Top-5 accuracy       : {top5:.4f}")
    print(f"  Urgency exact match  : {urgency_exact:.4f}")
    print(f"  Urgency UNDER-called : {under:.4f}   <- the number that matters for safety")

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    labels_sorted = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)

    importances = sorted(zip(ALL_FEATURES, model.feature_importances_),
                         key=lambda t: t[1], reverse=True)[:20]

    # most confused pairs, useful for the report
    confusions = []
    for i, a in enumerate(labels_sorted):
        for j, b in enumerate(labels_sorted):
            if i != j and cm[i][j] > 0:
                confusions.append((int(cm[i][j]), a, b))
    confusions.sort(reverse=True)

    import joblib
    bundle = {"model": model, "features": ALL_FEATURES,
              "classes": list(model.classes_), "version": 2}
    model_path = HERE / "disease_model.pkl"
    joblib.dump(bundle, model_path, compress=3)

    meta = {
        "algorithm": "RandomForestClassifier",
        "n_estimators": 180,
        "samples_generated": int(before),
        "duplicates_removed": int(removed),
        "samples_used": int(len(X)),
        "features_total": int(X.shape[1]),
        "features_symptoms": len(SYMPTOMS),
        "features_context": len(CONTEXT_FEATURES),
        "features_lab": len(LAB_FEATURES),
        "classes": int(y.nunique()),
        "top1_accuracy": round(float(top1), 4),
        "top3_accuracy": round(float(top3), 4),
        "top5_accuracy": round(float(top5), 4),
        "urgency_exact": round(float(urgency_exact), 4),
        "urgency_under_called": round(float(under), 4),
        "macro_f1": round(float(report["macro avg"]["f1-score"]), 4),
        "weighted_f1": round(float(report["weighted avg"]["f1-score"]), 4),
        "top_features": [{"feature": f, "importance": round(float(v), 5)}
                         for f, v in importances],
        "top_confusions": [{"count": c, "true": a, "predicted": b}
                           for c, a, b in confusions[:15]],
        "per_class": {k: {"precision": round(v["precision"], 3),
                          "recall": round(v["recall"], 3),
                          "f1": round(v["f1-score"], 3),
                          "support": int(v["support"])}
                      for k, v in report.items() if k in labels_sorted},
        "confusion_matrix_labels": labels_sorted,
        "confusion_matrix": cm.tolist(),
    }
    (HERE / "model_meta.json").write_text(json.dumps(meta, indent=2))

    print(f"\nSaved disease_model.pkl ({os.path.getsize(model_path)/1024:.0f} KB)")
    print("Saved model_meta.json")
    print("\nMost informative features:")
    for f, v in importances[:10]:
        print(f"  {v:.4f}  {f}")
    print("\nMost confused pairs (these are the clinically similar ones):")
    for c, a, b in confusions[:6]:
        print(f"  {c:>3}x  {a}  ->  {b}")


if __name__ == "__main__":
    main()
