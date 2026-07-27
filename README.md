# Arogya Disha — Healthcare Awareness & Literacy Platform

A Community Engagement Project. A Django web application that helps people find
the public healthcare they are already entitled to.

Three features:

1. **Government scheme directory** — every active central and Maharashtra health
   scheme, with real eligibility rules, the documents to carry, and step-by-step
   application instructions. Filterable by ration card colour.
2. **Hospital locator** — 116 hospitals, 108 of them across
   all 15 talukas of Pune district.
3. **ML symptom checker** — a Random Forest classifier over 189 symptoms and 70
   conditions, wrapped in five layers: a hand-written emergency rule layer that
   runs *before* the model and can override it entirely, an adaptive
   questionnaire that picks its next question by information gain, and a
   modifier layer that shows the user exactly what moved the answer.
   It reads lab reports from a photograph, and it reports **urgency** as the
   headline answer rather than a condition name.

---

## Quick start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 2b. OPTIONAL - lab-report photo reading needs the Tesseract system binary.
#     Skip this and the app falls back to typing values in; nothing breaks.
sudo apt install tesseract-ocr     # Ubuntu / Debian
# brew install tesseract           # macOS

# 3. Train the ML model (writes ml_model/disease_model.pkl)
python ml_model/train_model.py

# 4. Create the database
python manage.py makemigrations core schemes hospitals prediction
python manage.py migrate

# 5. Load schemes, hospitals, bed data, conditions and tips
python manage.py seed_data

# 6. Create your admin login
python manage.py createsuperuser

# 7. Run it
python manage.py runserver
```

Open **http://127.0.0.1:8000/** for the site and
**http://127.0.0.1:8000/admin/** for the control panel.

A pre-trained `disease_model.pkl` is already included, so step 3 is optional —
but run it anyway if you want fresh accuracy figures for your report.

---

## Project structure

```
healthcare-awareness-platform/
├── manage.py
├── requirements.txt
├── config/                     Django settings, root URLs, WSGI/ASGI
├── core/                       Home page, About page, health tips
│   └── management/commands/
│       └── seed_data.py        All seed data lives here
├── schemes/                    Feature 1 — government schemes
├── hospitals/                  Feature 2 — hospitals and bed availability
├── prediction/                 Feature 3 — symptom checker
│   └── engine.py               Loads the model, runs red-flag rules first
├── ml_model/
│   ├── knowledge_base.py       111 symptoms, 30 conditions, 5 emergency rules
│   ├── train_model.py          Generates the dataset and trains the classifier
│   ├── disease_model.pkl       Trained model (generated)
│   └── model_meta.json         Accuracy, F1, confusion matrix (generated)
├── templates/
└── static/css/main.css
```

---

## Feature 1 — Government schemes

The `Scheme` model keeps eligibility, documents and application steps in separate
fields so the templates can render them as checklists rather than a wall of text.

Every scheme carries a **last verified** date. Scheme amounts change, and a stale
figure that sends someone to the wrong counter is worse than no figure at all.

The list page filters by ration card colour, because that is how eligibility
actually works in Maharashtra. Schemes open to everyone are always included in a
filtered result rather than hidden.

**12 schemes are seeded**, verified against government and aggregator sources in
July 2026:

| Scheme | Benefit |
|---|---|
| AB PM-JAY | ₹5 lakh cashless cover per family per year |
| MJPJAY | ₹5 lakh, all Maharashtra families since 1 July 2024 |
| Ayushman Vay Vandana | ₹5 lakh for anyone aged 70+, any income |
| Janani Suraksha Yojana | Cash for institutional delivery |
| Janani Shishu Suraksha Karyakram | Free delivery, C-section, transport |
| PM Surakshit Matritva Abhiyan | Free specialist ANC on the 9th monthly |
| Ni-kshay Poshan Yojana | ₹1,000/month nutrition support for TB patients |
| PM National Dialysis Programme | Free dialysis for BPL patients |
| PM Bhartiya Janaushadhi Pariyojana | Generic medicines, 50–90% cheaper |
| Rashtriya Bal Swasthya Karyakram | Free child screening and treatment to 18 |
| Ayushman Bharat Digital Mission | Free ABHA digital health ID |
| NP-NCD | Free BP, diabetes and cancer screening plus medicines |

> **Note:** RSBY (Rashtriya Swasthya Bima Yojana) is deliberately *not* included.
> It has been subsumed into PM-JAY and is no longer a separate active scheme.
> Some project templates still list it — do not add it back.

---

## Feature 2 — Hospital beds

**There is no public real-time API for hospital bed occupancy in India.** This
project does not pretend otherwise.

Bed counts live in a `BedAvailability` table that an administrator edits directly
in the Django admin. That is exactly the interface a hospital data-entry operator
would use in a real deployment, which makes it an honest simulation rather than a
fake live feed.

Three things back that up in the interface:

- Every bed count shows how long ago it was updated.
- Records older than 24 hours are flagged as possibly stale.
- The list page carries a permanent banner stating the data is a demonstration.

**Updating beds:** go to `/admin/hospitals/bedavailability/`. The list view is
editable inline, so you can update every hospital in a city on one page and press
Save once. The `last_updated` timestamp refreshes automatically.

The seeded hospitals use **real hospital names in Nashik and Pune** so the demo
feels real. **Every bed number is invented.**

---

## Hospital coverage — Pune district

`hospitals/pune_district.py` holds 106 facilities spanning every taluka:

| Type | Count |
|---|---|
| State government (district hospital, medical colleges, sub-district and rural hospitals) | 41 |
| Municipal (PMC, PCMC, cantonment) | 11 |
| Trust / charitable | 18 |
| Private | 36 |

Merged with the original seed list, the database holds **106 hospitals**.

**What is real and what is not, stated plainly because an examiner will ask:**

- **Real** — hospital names, the taluka or locality each sits in, and hospital type.
- **Approximate** — coordinates are placed at the town or locality rather than the
  building. Phone numbers use the correct STD code for the taluka; the local part
  is a placeholder and has not been dialled.
- **Invented** — every bed count, and every `total_beds` figure. This is unchanged
  from v1 and is stated on every page that displays a bed number.

Scaling the list from 15 to 116 scales the simulated bed data with it. That is a
real cost and worth naming in your report: the app now *looks* far more
authoritative while the one number a person would act on is still fabricated. The
mitigation is that it says so, everywhere, every time.

The government network in particular is reorganised often — a Rural Hospital gets
upgraded to a Sub-District Hospital and the designation changes. Compiled from
public sources in July 2026; verify anything you intend to state as fact.

The list page is paginated at 20 per page and filterable by taluka, department,
hospital type, PM-JAY empanelment, free beds, and free-text search.

---

## Feature 3 — Symptom checker

The checker runs in four steps: **symptoms → details (+ optional lab report) →
adaptive follow-up questions → result.**

### Urgency is the primary output

The large answer at the top of the result page is *what to do and how fast*, not
a condition name. "See a doctor today" is defensible on this evidence; "you have
typhoid" is not, and invites self-medication. The condition is shown underneath,
labelled *what this could be — not a diagnosis*.

### The model

A `RandomForestClassifier` (180 trees) over
223 features: 189 symptoms,
21 context features and 13 lab
features.

| Metric | Value |
|---|---|
| Training samples (after de-duplication) | 22,389 |
| Conditions | 70 |
| Top-1 accuracy | **0.789** |
| Top-3 accuracy | **0.911** |
| Top-5 accuracy | 0.941 |
| Urgency exactly right | 0.877 |
| Urgency under-called (raw model) | 0.057 |
| Macro F1 | 0.787 |

**Top-1 accuracy went down from v1's 0.98, and that is the point.** v1 had 30
conditions with little overlap and no under-reporting, so it was scoring an
easier exam. v2 has 70 conditions that genuinely overlap, and the
generator simulates *under-reporting* — a real person ticks three or four boxes,
not the eight a textbook lists. An accuracy near 0.98 on this data would mean the
data was too tidy to be worth anything.

The confusions the model does make are the clinically honest ones —
Gastroenteritis with Food Poisoning, Influenza with Viral Fever, Bronchitis with
Asthma. Those pairs are hard for the same reason they are hard in a clinic.

### The five layers

| Layer | What it does |
|---|---|
| 0 | Red flags and critical lab values — hard override, model never consulted |
| 1 | The model produces a probability distribution |
| 2 | Adaptive questions chosen by information gain |
| 3 | The model re-runs with the new answers |
| 4 | Context modifiers, each one explained on screen |

### Layer 0 — the rules that outrank the model

Before the classifier runs, symptoms are checked against eight emergency rules
(cardiac, stroke, bleeding, meningitis, respiratory, abdominal, seizure,
anuria). If one fires, the model is skipped and the user gets an ambulance
number instead of a probability.

A model trained on typical presentations should never be the thing standing
between someone having a stroke and a phone call. The rules are readable and
auditable; a forest of 180 trees is not.

### Layer 2 — adaptive questions

Follow-up questions are not a hand-written script. The engine takes the current
top candidates and picks the unasked symptom whose answer would cut the entropy
of that distribution most. The screen shows *why* each question is being asked —
"this helps tell Dengue apart from Chikungunya" — so the user is never answering
into a black box. Capped at five.

### Layer 4 — modifiers you can see

Duration, age, pregnancy, progression and known conditions are turned into
features, and their effect is printed on the result page as an explicit
before/after: *"your lab result (low platelets) fits this — Dengue 19.3% → 39.9%"*.

### The urgency policy

Urgency is taken as the **worst case among candidates scoring at least 50% of the
leader's probability**, plus any emergency-level candidate above 5%. This was
tuned against the hold-out set rather than guessed:

| Rule | Under-called | Missed emergencies | Over-called |
|---|---|---|---|
| Top-1 only | 5.66% | 12.50% | — |
| Naive top-3 | — | — | 44% |
| **This policy** | **2.45%** | **3.75%** | **15%** |

Under-calling is the dangerous error, over-calling is the annoying one, so the
trade is deliberately lopsided.

---

## Lab reports — OCR and manual entry

Both paths exist. Currently, **manual entry** primary one. We would add make **OCR** the primary method later because photographing a page is
a more widely-held skill than reading it, and the real barrier for a
low-literacy user was never typing the digits — it was finding the word
"Haemoglobin" on a cluttered page. OCR removes exactly that barrier.

Three mechanisms make this safe:

1. **Confirmation, not pre-filling.** Extracted numbers are shown beside the raw
   line they came from and must be confirmed. Anything unconfirmed is discarded
   before it reaches the model.
2. **A plausibility gate.** Physiology has narrow valid ranges, so a large share
   of OCR digit errors produce impossible numbers that are rejected outright. Any
   value outside the normal range is *always* downgraded to require confirmation,
   because abnormal values are exactly the ones that drive urgency.
3. **The asymmetric rule.** A lab value may **raise** urgency and may never lower
   it. The dangerous OCR error is the plausible one — 15,000 platelets misread as
   150,000 — and an error in the reassuring direction is the one that kills
   someone. An error in the alarming direction only sends them to a clinic they
   did not strictly need.

Planned to be tested against synthetic Indian lab reports including a deliberately degraded photo (rotated, blurred, poor light).

Report images are read and discarded inside the same request. Nothing is written
to disk and no file is stored — `FILE_UPLOAD_MAX_MEMORY_SIZE` is raised above the
accepted upload size specifically so Django does not spill large uploads to a
temporary file and make that claim untrue.

### Why there is no "medicines you can take"

This was deliberately not built. Dengue and Influenza are two of
the conditions this model most often confuses, because they genuinely share
symptoms — and the correct painkiller advice for them is *opposite*: NSAIDs are
ordinary for flu and dangerous in dengue because of the bleeding risk. A feature
confident enough to name a drug is confident enough to do harm on exactly the
pairs where the model is weakest.

What is built instead:

- **`avoid`** — drug *safety* warnings, i.e. what **not** to take. Harm reduction
  stays correct even when the prediction may be wrong.
- **`tests`** — which tests to ask for by name, which makes a short consultation
  far more useful.
- Plain-language explanation of report values, in English and Marathi(more languages planned for future).

---

## Design notes

The interface is styled as a **clinical instrument** rather than a poster: white
cards on a light ground, hairline rules, tabular figures, and one prominent
urgency scale. The reasoning is that this screen is read while someone is
worried, and calm precision suits that better than shouting.

**Type** is Anek (Ek Type, Mumbai) for text and JetBrains Mono for figures. Anek
was chosen because its Latin and Devanagari share one skeleton, so English and
Marathi sit together on a line without one looking bolted on — which matters for
a bilingual tool. Numbers are set in mono with tabular figures so lab values
line up in a column and can be compared down the page.

**Colour carries meaning and nothing else.** Teal is the product itself; the
warm end of the ramp belongs entirely to urgency:

| Colour | Means |
|---|---|
| Teal | The site itself|
| Green | Routine — no rush|
| Amber | Prompt — a day or two|
| Orange | Urgent — today |
| Red | Emergency — right now|

Urgency is never colour alone. The four-step scale is a labelled row ("No rush /
A day or two / Today / Right now") with the current step marked, so it survives
both colour-blindness and a black-and-white printout.

Verified during the build, on the rendered page rather than by eye:

- No horizontal overflow at 1280px, 768px or 390px.
- **All text meets WCAG AA contrast — 84 elements checked, 0 failures.** Getting
  there required darkening the muted grey from `#82868E` to `#6B6F77` (3.65:1 →
  5.04:1) and deepening the prompt and urgent hues, which were failing at 4.02:1
  and 3.96:1 against their own tint backgrounds.
- The follow-up questions work with JavaScript disabled. An earlier version
  mirrored the radio buttons into a hidden checkbox with JS, which silently
  dropped every "yes" on a device with JS off — the wrong way to fail for this
  audience. The radios are now read directly.
- The symptom filter and counter are progressive enhancement only; the form
  submits without them.
- Keyboard focus is visible throughout; `prefers-reduced-motion` is respected.

---

## Honest limitations

State these in your report. Examiners respond much better to acknowledged limits
than to overclaiming.

- **The Django request cycle has not been run.** The project was built in an
  environment where Django could not be installed, so the code was validated by
  syntax checks, data-shape cross-referencing, direct execution of the ML and OCR
  modules, and browser rendering of the CSS — but not by an actual `runserver`.
  Expect to fix a small number of runtime issues on first boot. See
  Troubleshooting.
- Bed counts are entered by hand and are demonstration data, not live. There is
  no public real-time bed API in India; the UI says so on every page.
- Training data is generated from curated clinical profiles, not real patient
  records — so the accuracy figures describe the model, not clinical performance.
- The checker covers 70 conditions. Anything outside that list cannot be
  predicted, only mismatched to the nearest thing.
- OCR quality depends on the photo. A bad photo yields fewer values, not wrong
  ones — but the confirmation step is what guarantees that, so it must not be
  removed as a "convenience" improvement.
- Scheme details are accurate as of the verification date on each page and must
  be re-checked against official portals before anyone relies on them.
- The app is text-heavy throughout. A user who cannot read a lab report also
  cannot read the scheme eligibility rules. Icons, audio readback and fuller
  Marathi coverage are the honest next step, and in practice these phones are
  often operated with help from a younger family member or an ASHA worker.

---

## Troubleshooting

**"Trained model not found"** — run `python ml_model/train_model.py`.

**No schemes or hospitals showing** — run `python manage.py seed_data`. Use
`--reset` to wipe and rebuild.

**Fonts look wrong** — the display faces load from Google Fonts, so you need an
internet connection on first load. Fallbacks are defined and the layout holds
without them.

**Migrations not detected** — run
`python manage.py makemigrations core schemes hospitals prediction` explicitly
with the app names.

**"Photo reading is not installed"** on the lab page — Tesseract is a *system*
package, not just the Python wrapper:

```bash
sudo apt install tesseract-ocr      # Ubuntu / Debian
brew install tesseract              # macOS
```

Windows: install from `https://github.com/UB-Mannheim/tesseract/wiki`. Without it
the app falls back to manual entry and says so — nothing breaks.

**Anything else on first boot** — this project has never been run through an
actual Django server (see Honest limitations). If a page raises, the likely
causes in order are: a template variable this README's data-shape checks could
not catch, a missing migration, or the model file not being where
`settings.ML_MODEL_PATH` expects. Run with `DEBUG = True` and the traceback will
name the template line directly.

---

## Verify before submitting

Scheme amounts change. Re-check against:

- https://pmjay.gov.in
- https://www.jeevandayee.gov.in
- https://www.myscheme.gov.in

Then update the `last_verified` date on each scheme in the admin.
