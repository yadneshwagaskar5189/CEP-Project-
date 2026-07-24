"""
knowledge_base.py  (v2)
-----------------------
Vocabulary and rules for the symptom checker.

Layers, in the order they execute:

    Layer 0   RED_FLAGS + LAB_CRITICAL   hard override, no model involved
    Layer 1   ML model                   probability distribution over conditions
    Layer 2   question selection         information gain over Layer 1 candidates
    Layer 3   ML model, re-run           with the extra answers
    Layer 4   CONTEXT_MODIFIERS          duration / age / pregnancy / labs, explained

Layer 0 is deliberately first and deliberately dumb. A model trained on typical
presentations must never sit between someone having a stroke and a phone call.

SAFETY POLICY - ASYMMETRIC EVIDENCE
Evidence that arrives with uncertainty attached (OCR-extracted lab values in
particular) may RAISE urgency but may never LOWER it. A misread that sends
someone to hospital unnecessarily is an inconvenience. A misread that reassures
someone who is bleeding internally is not.
"""

# ---------------------------------------------------------------------------
# 1. SYMPTOM VOCABULARY
# ---------------------------------------------------------------------------

SYMPTOM_GROUPS = {
    "Fever and whole body": [
        ("fever", "Fever"),
        ("high_fever", "High fever (above 39C / 102F)"),
        ("low_grade_fever", "Mild fever that keeps coming back"),
        ("chills", "Chills or shivering"),
        ("night_sweats", "Sweating at night"),
        ("fatigue", "Feeling very tired"),
        ("weakness", "Weakness"),
        ("body_ache", "Body ache"),
        ("weight_loss", "Losing weight without trying"),
        ("weight_gain", "Gaining weight without trying"),
        ("loss_of_appetite", "Not feeling hungry"),
        ("excessive_thirst", "Feeling thirsty all the time"),
        ("excessive_hunger", "Feeling hungry all the time"),
        ("cold_intolerance", "Feeling cold when others do not"),
        ("heat_intolerance", "Feeling hot when others do not"),
        ("dehydration", "Dry mouth, passing very little urine"),
        ("swollen_glands", "Swollen glands in neck or armpit"),
        ("general_swelling", "Swelling in face, hands or feet"),
    ],
    "Head, nerves and balance": [
        ("headache", "Headache"),
        ("severe_headache", "Very severe headache"),
        ("headache_band", "Tight band feeling around the head"),
        ("dizziness", "Dizziness"),
        ("vertigo", "Room spinning around you"),
        ("fainting", "Fainting"),
        ("confusion", "Confusion"),
        ("memory_problems", "Forgetting things"),
        ("neck_stiffness", "Stiff neck, hard to bend chin down"),
        ("slurred_speech", "Slurred or unclear speech"),
        ("facial_droop", "One side of the face drooping"),
        ("sudden_weakness_one_side", "Sudden weakness on one side of body"),
        ("loss_of_balance", "Loss of balance"),
        ("tingling_hands_feet", "Tingling or numbness in hands or feet"),
        ("burning_feet", "Burning feeling in the feet"),
        ("tremor", "Shaking hands"),
        ("seizure", "Fits or convulsions"),
        ("blackout", "Losing awareness for a short time"),
        ("sensitivity_to_light", "Light hurts your eyes"),
        ("sensitivity_to_sound", "Sound feels too loud"),
        ("aura_before_headache", "Flashing lights or spots before a headache"),
    ],
    "Eyes": [
        ("blurred_vision", "Blurred vision"),
        ("red_eyes", "Red eyes"),
        ("watery_eyes", "Watery eyes"),
        ("itchy_eyes", "Itchy eyes"),
        ("eye_discharge", "Discharge from eyes"),
        ("swollen_eyelids", "Swollen eyelids"),
        ("eye_pain", "Pain in the eye"),
        ("night_vision_trouble", "Trouble seeing at night"),
        ("cloudy_vision", "Vision looks cloudy or faded"),
        ("double_vision", "Seeing double"),
        ("yellow_eyes", "Yellow eyes"),
        ("halos_around_lights", "Rings or halos around lights"),
    ],
    "Ears, nose and throat": [
        ("sore_throat", "Sore throat"),
        ("severe_sore_throat", "Very painful throat, hard to swallow"),
        ("runny_nose", "Runny nose"),
        ("blocked_nose", "Blocked nose"),
        ("sneezing", "Frequent sneezing"),
        ("hoarse_voice", "Hoarse voice"),
        ("facial_pain", "Pain around cheeks or forehead"),
        ("loss_of_smell", "Cannot smell properly"),
        ("loss_of_taste", "Cannot taste properly"),
        ("post_nasal_drip", "Mucus dripping down the throat"),
        ("ear_pain", "Ear pain"),
        ("ear_discharge", "Discharge from the ear"),
        ("hearing_loss", "Reduced hearing"),
        ("ringing_in_ears", "Ringing sound in the ears"),
        ("white_patches_throat", "White patches on the tonsils"),
        ("swollen_jaw", "Swelling in front of the ear or jaw"),
        ("nosebleed", "Nose bleeding"),
        ("mouth_ulcers", "Mouth ulcers"),
        ("bleeding_gums", "Bleeding gums"),
    ],
    "Chest, heart and breathing": [
        ("cough", "Cough"),
        ("dry_cough", "Dry cough"),
        ("cough_with_phlegm", "Cough with phlegm"),
        ("chronic_cough", "Cough lasting more than two weeks"),
        ("coughing_blood", "Coughing up blood"),
        ("chest_pain", "Chest pain"),
        ("chest_pain_on_exertion", "Chest pain when walking or climbing stairs"),
        ("chest_tightness", "Tightness in the chest"),
        ("breathlessness", "Shortness of breath"),
        ("breathless_lying_down", "Breathless when lying flat"),
        ("breathless_on_exertion", "Breathless on walking or climbing"),
        ("wheezing", "Whistling sound while breathing"),
        ("rapid_breathing", "Breathing very fast"),
        ("palpitations", "Heart beating fast or irregular"),
        ("pain_radiating_to_arm", "Pain spreading to arm, jaw or back"),
        ("cold_sweat", "Sudden cold sweat"),
        ("ankle_swelling", "Swollen ankles or feet"),
        ("blue_lips", "Lips or fingertips looking blue"),
    ],
    "Stomach and digestion": [
        ("abdominal_pain", "Stomach pain"),
        ("upper_abdominal_pain", "Pain in upper stomach"),
        ("lower_abdominal_pain", "Pain in lower stomach"),
        ("right_lower_abdominal_pain", "Pain in lower right side of stomach"),
        ("right_upper_abdominal_pain", "Pain in upper right side of stomach"),
        ("cramping_pain", "Cramping pain that comes and goes"),
        ("nausea", "Feeling like vomiting"),
        ("vomiting", "Vomiting"),
        ("vomiting_blood", "Vomiting blood"),
        ("diarrhoea", "Loose motions"),
        ("bloody_diarrhoea", "Loose motions with blood or mucus"),
        ("constipation", "Constipation"),
        ("bloating", "Bloated stomach"),
        ("acidity", "Acidity"),
        ("heartburn", "Burning feeling in the chest after eating"),
        ("belching", "Frequent burping"),
        ("indigestion", "Indigestion"),
        ("blood_in_stool", "Blood in stool"),
        ("black_stool", "Black, tarry stool"),
        ("pain_passing_stool", "Pain while passing stool"),
        ("lump_at_anus", "Lump or swelling at the back passage"),
        ("pale_stool", "Pale or clay coloured stool"),
        ("dark_urine", "Very dark urine"),
        ("worms_in_stool", "Worms seen in stool"),
        ("itching_around_anus", "Itching around the back passage"),
        ("pain_after_fatty_food", "Pain after eating oily food"),
        ("early_fullness", "Feeling full after eating very little"),
    ],
    "Urine and kidneys": [
        ("burning_urination", "Burning while passing urine"),
        ("frequent_urination", "Passing urine very often"),
        ("urgency_to_urinate", "Sudden urge to pass urine"),
        ("night_urination", "Getting up at night to pass urine"),
        ("blood_in_urine", "Blood in urine"),
        ("cloudy_urine", "Cloudy or foul-smelling urine"),
        ("flank_pain", "Sharp pain in the side of the back"),
        ("reduced_urine", "Passing very little urine"),
        ("weak_urine_stream", "Weak or slow urine stream"),
        ("dribbling_urine", "Dribbling after passing urine"),
        ("incomplete_emptying", "Feeling the bladder is not fully empty"),
        ("frothy_urine", "Frothy or bubbly urine"),
    ],
    "Skin, hair and nails": [
        ("rash", "Rash"),
        ("itching", "Itching"),
        ("night_itching", "Itching that is worse at night"),
        ("red_spots", "Red spots on skin"),
        ("blisters", "Blisters"),
        ("ring_shaped_rash", "Ring shaped itchy patch"),
        ("dry_skin", "Very dry skin"),
        ("skin_peeling", "Skin peeling"),
        ("scaly_patches", "Thick scaly silvery patches"),
        ("yellow_skin", "Yellow skin"),
        ("pale_skin", "Pale skin"),
        ("hair_loss", "Hair falling out"),
        ("brittle_nails", "Brittle nails"),
        ("bruising_easily", "Bruising easily"),
        ("slow_healing_wounds", "Wounds healing slowly"),
        ("pimples", "Pimples on face, chest or back"),
        ("oily_skin", "Very oily skin"),
        ("raised_itchy_welts", "Raised itchy welts that move around"),
        ("skin_burrows_between_fingers", "Itchy lines between the fingers"),
        ("excess_facial_hair", "Unwanted hair on face or chin"),
        ("dark_neck_patches", "Dark velvety patches on the neck"),
    ],
    "Muscles, bones and joints": [
        ("joint_pain", "Joint pain"),
        ("joint_swelling", "Swollen joints"),
        ("joint_stiffness", "Stiff joints, especially in the morning"),
        ("small_joint_pain", "Pain in the small joints of hands or feet"),
        ("symmetric_joint_pain", "Same joints painful on both sides"),
        ("big_toe_pain", "Sudden severe pain in the big toe"),
        ("muscle_pain", "Muscle pain"),
        ("calf_pain", "Pain in the calf muscles"),
        ("back_pain", "Back pain"),
        ("lower_back_pain", "Lower back pain"),
        ("neck_pain", "Neck pain"),
        ("knee_pain", "Knee pain"),
        ("shoulder_pain", "Shoulder pain"),
        ("restricted_movement", "Cannot move a joint fully"),
        ("pain_down_the_leg", "Pain shooting down the back of the leg"),
        ("cramps", "Muscle cramps"),
        ("bone_pain", "Bone pain or tenderness"),
        ("frequent_fractures", "Bones breaking easily"),
        ("difficulty_climbing_stairs", "Difficulty climbing stairs"),
    ],
    "Sleep, mood and thinking": [
        ("anxiety", "Feeling anxious or on edge"),
        ("panic_episodes", "Sudden episodes of intense fear"),
        ("irritability", "Irritability"),
        ("mood_swings", "Mood swings"),
        ("low_mood", "Feeling low or sad most of the day"),
        ("loss_of_interest", "No interest in things you used to enjoy"),
        ("difficulty_sleeping", "Difficulty sleeping"),
        ("excessive_sleep", "Sleeping too much"),
        ("poor_concentration", "Difficulty concentrating"),
        ("restlessness", "Restlessness"),
        ("excessive_worry", "Worrying you cannot control"),
        ("hopelessness", "Feeling hopeless about the future"),
    ],
    "Women's health": [
        ("irregular_periods", "Irregular periods"),
        ("heavy_periods", "Very heavy periods"),
        ("painful_periods", "Painful periods"),
        ("missed_periods", "Missed periods"),
        ("pelvic_pain", "Pain in the pelvis"),
        ("vaginal_discharge", "Unusual vaginal discharge"),
        ("difficulty_conceiving", "Difficulty getting pregnant"),
        ("breast_pain", "Breast pain or tenderness"),
    ],
    "Men's health": [
        ("prostate_symptoms", "Straining to start passing urine"),
        ("scrotal_pain", "Pain or swelling in the scrotum"),
    ],
}

SYMPTOMS = [key for group in SYMPTOM_GROUPS.values() for key, _ in group]
SYMPTOM_LABELS = {k: v for group in SYMPTOM_GROUPS.values() for k, v in group}
SYMPTOM_GROUP_OF = {k: name for name, group in SYMPTOM_GROUPS.items() for k, _ in group}


# ---------------------------------------------------------------------------
# 2. LAYER 0 - EMERGENCY RED FLAGS (symptom based)
# ---------------------------------------------------------------------------

RED_FLAGS = [
    {
        "code": "cardiac",
        "title": "Possible heart emergency",
        "trigger": ["chest_pain", "chest_pain_on_exertion"],
        "support": ["pain_radiating_to_arm", "breathlessness", "cold_sweat",
                    "palpitations", "fainting", "vomiting", "blue_lips"],
        "min_support": 1,
        "message": "Chest pain with these symptoms can mean a heart attack. Do not wait, "
                   "and do not drive yourself.",
    },
    {
        "code": "stroke",
        "title": "Possible stroke",
        "trigger": ["facial_droop", "slurred_speech", "sudden_weakness_one_side"],
        "support": [],
        "min_support": 0,
        "message": "These are stroke warning signs. Treatment works best within the first "
                   "few hours, so go now. Note the time the symptoms started.",
    },
    {
        "code": "bleeding",
        "title": "Internal bleeding warning",
        "trigger": ["vomiting_blood", "coughing_blood", "black_stool"],
        "support": [],
        "min_support": 0,
        "message": "Blood in vomit, cough or stool needs to be examined by a doctor today.",
    },
    {
        "code": "meningitis",
        "title": "Possible brain or spinal infection",
        "trigger": ["neck_stiffness"],
        "support": ["high_fever", "severe_headache", "sensitivity_to_light", "confusion",
                    "seizure", "vomiting"],
        "min_support": 2,
        "message": "A stiff neck with high fever and headache can mean a brain or spinal "
                   "infection. This gets worse quickly.",
    },
    {
        "code": "respiratory",
        "title": "Severe breathing difficulty",
        "trigger": ["breathlessness", "blue_lips"],
        "support": ["rapid_breathing", "chest_tightness", "confusion", "fainting",
                    "blue_lips"],
        "min_support": 2,
        "message": "Difficulty breathing this severe needs oxygen and monitoring at a "
                   "hospital.",
    },
    {
        "code": "abdomen",
        "title": "Possible surgical emergency in the abdomen",
        "trigger": ["right_lower_abdominal_pain"],
        "support": ["fever", "vomiting", "loss_of_appetite", "nausea"],
        "min_support": 2,
        "message": "Severe pain in the lower right abdomen with fever and vomiting can "
                   "mean appendicitis, which may need surgery. Do not eat or drink "
                   "anything until a doctor has seen you.",
    },
    {
        "code": "seizure",
        "title": "Fits need medical assessment",
        "trigger": ["seizure"],
        "support": [],
        "min_support": 0,
        "message": "A first fit, or a fit lasting more than five minutes, needs emergency "
                   "care. Do not put anything in the person's mouth. Turn them on their "
                   "side and clear the area around them.",
    },
    {
        "code": "anuria",
        "title": "Kidneys may have stopped working",
        "trigger": ["reduced_urine"],
        "support": ["general_swelling", "breathlessness", "confusion", "vomiting"],
        "min_support": 2,
        "message": "Passing very little urine along with swelling or breathlessness can "
                   "mean the kidneys are failing. This needs assessment today.",
    },
]

EMERGENCY_NUMBER = "108"
MENTAL_HEALTH_HELPLINE = "14416"


def check_red_flags(selected):
    """Return the first matching red flag rule, or None."""
    chosen = set(selected)
    for rule in RED_FLAGS:
        if not chosen.intersection(rule["trigger"]):
            continue
        if len(chosen.intersection(rule["support"])) >= rule["min_support"]:
            return rule
    return None


# ---------------------------------------------------------------------------
# 3. LAYER 4 - CONTEXT QUESTIONS
# ---------------------------------------------------------------------------

CONTEXT_QUESTIONS = [
    {
        "key": "duration",
        "question": "How long have you had these symptoms?",
        "why": "Duration separates conditions that look identical on day one.",
        "options": [
            ("acute", "Less than 3 days"),
            ("subacute", "3 days to 2 weeks"),
            ("chronic", "More than 2 weeks"),
            ("very_chronic", "More than 2 months"),
        ],
    },
    {
        "key": "age_band",
        "question": "Roughly how old is the person?",
        "why": "The same symptoms mean different things at 8, 35 and 75.",
        "options": [
            ("child", "Under 12"),
            ("teen", "12 to 18"),
            ("adult", "19 to 45"),
            ("middle", "46 to 64"),
            ("senior", "65 and above"),
        ],
    },
    {
        "key": "progression",
        "question": "Are the symptoms changing?",
        "why": "Something getting rapidly worse is treated differently.",
        "options": [
            ("worse_fast", "Getting worse quickly"),
            ("worse_slow", "Getting worse slowly"),
            ("same", "About the same"),
            ("better", "Slowly improving"),
        ],
    },
    {
        "key": "pregnancy",
        "question": "Is the person pregnant, or possibly pregnant?",
        "why": "Pregnancy changes which conditions are dangerous and which medicines "
               "are safe.",
        "options": [
            ("no", "No"),
            ("yes", "Yes"),
            ("maybe", "Not sure"),
            ("na", "Not applicable"),
        ],
    },
    {
        "key": "history",
        "question": "Any of these already diagnosed?",
        "why": "Existing conditions change what new symptoms are likely to mean.",
        "multi": True,
        "options": [
            ("diabetes", "Diabetes"),
            ("hypertension", "High blood pressure"),
            ("heart", "Heart disease"),
            ("asthma", "Asthma or COPD"),
            ("kidney", "Kidney disease"),
            ("tb_past", "TB in the past"),
            ("thyroid", "Thyroid problem"),
        ],
    },
]

CONTEXT_FEATURES = [
    "ctx_duration_acute", "ctx_duration_subacute", "ctx_duration_chronic",
    "ctx_duration_very_chronic",
    "ctx_age_child", "ctx_age_teen", "ctx_age_adult", "ctx_age_middle", "ctx_age_senior",
    "ctx_worse_fast", "ctx_worse_slow", "ctx_stable", "ctx_improving",
    "ctx_pregnant",
    "ctx_hx_diabetes", "ctx_hx_hypertension", "ctx_hx_heart", "ctx_hx_asthma",
    "ctx_hx_kidney", "ctx_hx_tb", "ctx_hx_thyroid",
]

_CTX_MAP = {
    ("duration", "acute"): "ctx_duration_acute",
    ("duration", "subacute"): "ctx_duration_subacute",
    ("duration", "chronic"): "ctx_duration_chronic",
    ("duration", "very_chronic"): "ctx_duration_very_chronic",
    ("age_band", "child"): "ctx_age_child",
    ("age_band", "teen"): "ctx_age_teen",
    ("age_band", "adult"): "ctx_age_adult",
    ("age_band", "middle"): "ctx_age_middle",
    ("age_band", "senior"): "ctx_age_senior",
    ("progression", "worse_fast"): "ctx_worse_fast",
    ("progression", "worse_slow"): "ctx_worse_slow",
    ("progression", "same"): "ctx_stable",
    ("progression", "better"): "ctx_improving",
    ("pregnancy", "yes"): "ctx_pregnant",
    ("pregnancy", "maybe"): "ctx_pregnant",
    ("history", "diabetes"): "ctx_hx_diabetes",
    ("history", "hypertension"): "ctx_hx_hypertension",
    ("history", "heart"): "ctx_hx_heart",
    ("history", "asthma"): "ctx_hx_asthma",
    ("history", "kidney"): "ctx_hx_kidney",
    ("history", "tb_past"): "ctx_hx_tb",
    ("history", "thyroid"): "ctx_hx_thyroid",
}


def context_to_features(answers):
    """Turn {'duration': 'chronic', 'history': ['diabetes']} into feature keys."""
    out = []
    for key, value in (answers or {}).items():
        values = value if isinstance(value, list) else [value]
        for v in values:
            feature = _CTX_MAP.get((key, v))
            if feature:
                out.append(feature)
    return out


# ---------------------------------------------------------------------------
# 4. LAYER 4 - EXPLAINABLE MODIFIERS
# ---------------------------------------------------------------------------

CONTEXT_MODIFIERS = [
    {"disease": "Tuberculosis (TB)", "needs": ["ctx_duration_chronic"], "factor": 2.4,
     "reason": "a cough lasting more than two weeks is the strongest TB signal in India"},
    {"disease": "Tuberculosis (TB)", "needs": ["ctx_duration_very_chronic"], "factor": 3.0,
     "reason": "symptoms lasting more than two months raise the chance of TB sharply"},
    {"disease": "Tuberculosis (TB)", "needs": ["ctx_hx_tb"], "factor": 2.0,
     "reason": "TB in the past raises the chance of it returning"},
    {"disease": "Common Cold", "needs": ["ctx_duration_chronic"], "factor": 0.25,
     "reason": "a common cold does not last more than about ten days"},
    {"disease": "Influenza (Flu)", "needs": ["ctx_duration_chronic"], "factor": 0.30,
     "reason": "flu does not usually last beyond two weeks"},
    {"disease": "Dengue", "needs": ["ctx_duration_chronic"], "factor": 0.30,
     "reason": "dengue fever runs its course in about a week"},
    {"disease": "Gastroenteritis", "needs": ["ctx_duration_chronic"], "factor": 0.35,
     "reason": "a stomach infection lasting weeks needs a different explanation"},
    {"disease": "Type 2 Diabetes", "needs": ["ctx_hx_diabetes"], "factor": 2.5,
     "reason": "diabetes is already diagnosed"},
    {"disease": "Hypertension (High BP)", "needs": ["ctx_hx_hypertension"], "factor": 2.5,
     "reason": "high blood pressure is already diagnosed"},
    {"disease": "Angina (Heart Artery Disease)", "needs": ["ctx_hx_heart"], "factor": 2.6,
     "reason": "existing heart disease makes cardiac causes more likely"},
    {"disease": "Angina (Heart Artery Disease)", "needs": ["ctx_age_senior"], "factor": 1.8,
     "reason": "cardiac causes are more likely over 65"},
    {"disease": "Angina (Heart Artery Disease)", "needs": ["ctx_age_child"], "factor": 0.05,
     "reason": "coronary disease is very rare in children"},
    {"disease": "Bronchial Asthma", "needs": ["ctx_hx_asthma"], "factor": 2.6,
     "reason": "asthma or COPD is already diagnosed"},
    {"disease": "COPD", "needs": ["ctx_hx_asthma"], "factor": 2.2,
     "reason": "an existing airway condition is known"},
    {"disease": "COPD", "needs": ["ctx_age_child"], "factor": 0.03,
     "reason": "COPD does not occur in children"},
    {"disease": "Chronic Kidney Disease", "needs": ["ctx_hx_kidney"], "factor": 2.8,
     "reason": "kidney disease is already diagnosed"},
    {"disease": "Hypothyroidism", "needs": ["ctx_hx_thyroid"], "factor": 2.4,
     "reason": "a thyroid problem is already diagnosed"},
    {"disease": "Hyperthyroidism", "needs": ["ctx_hx_thyroid"], "factor": 2.2,
     "reason": "a thyroid problem is already diagnosed"},
    {"disease": "Osteoarthritis", "needs": ["ctx_age_child"], "factor": 0.05,
     "reason": "wear-and-tear arthritis does not occur in children"},
    {"disease": "Osteoarthritis", "needs": ["ctx_age_senior"], "factor": 1.7,
     "reason": "joint wear is common over 65"},
    {"disease": "Benign Prostate Enlargement", "needs": ["ctx_age_child"], "factor": 0.02,
     "reason": "this does not occur in children"},
    {"disease": "Benign Prostate Enlargement", "needs": ["ctx_age_teen"], "factor": 0.05,
     "reason": "this does not occur at this age"},
    {"disease": "Benign Prostate Enlargement", "needs": ["ctx_age_senior"], "factor": 1.9,
     "reason": "prostate enlargement is very common in older men"},
    {"disease": "Chickenpox", "needs": ["ctx_age_child"], "factor": 1.8,
     "reason": "chickenpox is most common in children"},
    {"disease": "Measles", "needs": ["ctx_age_child"], "factor": 2.0,
     "reason": "measles is most common in unvaccinated children"},
    {"disease": "Cataract", "needs": ["ctx_age_senior"], "factor": 2.2,
     "reason": "cataract is common over 65"},
    {"disease": "Cataract", "needs": ["ctx_age_child"], "factor": 0.08,
     "reason": "cataract is rare in children"},
    {"disease": "Osteoporosis", "needs": ["ctx_age_senior"], "factor": 2.0,
     "reason": "bone thinning is common in older adults"},
    {"disease": "Osteoporosis", "needs": ["ctx_age_child"], "factor": 0.05,
     "reason": "this is not a childhood condition"},
    {"disease": "Acne", "needs": ["ctx_age_teen"], "factor": 2.0,
     "reason": "acne is most common in the teenage years"},
    {"disease": "Acne", "needs": ["ctx_age_senior"], "factor": 0.2,
     "reason": "acne is uncommon in older adults"},
]

# Conditions where pregnancy raises urgency without changing the diagnosis.
PREGNANCY_ESCALATE = {
    "Dengue", "Malaria", "Typhoid", "Urinary Tract Infection", "Pneumonia",
    "Hepatitis A (Jaundice)", "Hypertension (High BP)", "Anaemia",
    "Hypothyroidism", "Tuberculosis (TB)", "Chickenpox", "Measles",
    "Type 2 Diabetes", "Food Poisoning",
}


# ---------------------------------------------------------------------------
# 5. LAB VALUES
# ---------------------------------------------------------------------------

LAB_TESTS = {
    "haemoglobin": {
        "label": "Haemoglobin (Hb)",
        "unit": "g/dL",
        "normal": (12.0, 17.0),
        "normal_text": "12 to 17 g/dL for adults, women slightly lower than men",
        "plausible": (2.0, 25.0),
        "critical_low": 7.0,
        "critical_high": None,
        "aliases": ["haemoglobin", "hemoglobin", "hb", "hgb"],
        "flags": {"low": "anaemic_range", "high": "high_haemoglobin"},
        "plain": "Haemoglobin carries oxygen around your body. When it is low you feel "
                 "tired and breathless. That is anaemia.",
    },
    "platelets": {
        "label": "Platelet count",
        "unit": "/cumm",
        "normal": (150000, 450000),
        "normal_text": "1.5 to 4.5 lakh per cumm",
        "plausible": (5000, 1500000),
        "critical_low": 50000,
        "critical_high": None,
        "aliases": ["platelet", "platelets", "plt", "platelet count", "thrombocyte"],
        "flags": {"low": "low_platelets", "high": "high_platelets"},
        "plain": "Platelets help your blood clot. A falling platelet count is the main "
                 "danger in dengue.",
        "lakh_notation": True,
    },
    "wbc": {
        "label": "White cell count (WBC / TLC)",
        "unit": "/cumm",
        "normal": (4000, 11000),
        "normal_text": "4,000 to 11,000 per cumm",
        "plausible": (100, 200000),
        "critical_low": 2000,
        "critical_high": 30000,
        "aliases": ["wbc", "tlc", "total leucocyte", "total leukocyte",
                    "white blood cell", "leucocyte count", "w.b.c"],
        "flags": {"low": "low_wbc", "high": "high_wbc"},
        "plain": "White cells fight infection. A high count usually means a bacterial "
                 "infection. A very low count means the body cannot fight one well.",
    },
    "fasting_glucose": {
        "label": "Fasting blood sugar",
        "unit": "mg/dL",
        "normal": (70, 99),
        "normal_text": "70 to 99 mg/dL fasting",
        "plausible": (20, 900),
        "critical_low": 60,
        "critical_high": 300,
        "aliases": ["fasting blood sugar", "fbs", "fasting glucose", "glucose fasting",
                    "blood sugar fasting", "sugar fasting"],
        "flags": {"low": "low_blood_sugar", "high": "high_blood_sugar"},
        "plain": "Fasting sugar of 126 mg/dL or more on two occasions means diabetes. "
                 "100 to 125 is pre-diabetes, which can still be reversed.",
    },
    "hba1c": {
        "label": "HbA1c",
        "unit": "%",
        "normal": (4.0, 5.6),
        "normal_text": "below 5.7% normal, 5.7 to 6.4% pre-diabetes, 6.5% and above "
                       "suggests diabetes",
        "plausible": (3.0, 20.0),
        "critical_low": None,
        "critical_high": 10.0,
        "aliases": ["hba1c", "glycated haemoglobin", "glycosylated haemoglobin", "a1c"],
        "flags": {"high": "high_hba1c"},
        "plain": "HbA1c is your average blood sugar over three months. Fasting the night "
                 "before does not change it.",
    },
    "creatinine": {
        "label": "Serum creatinine",
        "unit": "mg/dL",
        "normal": (0.6, 1.3),
        "normal_text": "0.6 to 1.3 mg/dL",
        "plausible": (0.1, 25.0),
        "critical_low": None,
        "critical_high": 2.5,
        "aliases": ["creatinine", "serum creatinine", "s. creatinine", "s.creatinine"],
        "flags": {"high": "high_creatinine"},
        "plain": "Creatinine shows how well your kidneys are filtering. A rising value "
                 "means they are struggling.",
    },
    "bilirubin": {
        "label": "Total bilirubin",
        "unit": "mg/dL",
        "normal": (0.2, 1.2),
        "normal_text": "0.2 to 1.2 mg/dL",
        "plausible": (0.0, 50.0),
        "critical_low": None,
        "critical_high": 5.0,
        "aliases": ["bilirubin", "total bilirubin", "s. bilirubin", "serum bilirubin"],
        "flags": {"high": "high_bilirubin"},
        "plain": "Bilirubin builds up when the liver is inflamed or blocked. It is what "
                 "turns skin and eyes yellow.",
    },
    "tsh": {
        "label": "TSH",
        "unit": "mIU/L",
        "normal": (0.4, 4.0),
        "normal_text": "0.4 to 4.0 mIU/L",
        "plausible": (0.001, 150.0),
        "critical_low": None,
        "critical_high": None,
        "aliases": ["tsh", "thyroid stimulating hormone"],
        "flags": {"low": "low_tsh", "high": "high_tsh"},
        "plain": "A high TSH means an underactive thyroid. A low TSH means an overactive "
                 "one. It works the opposite way round to what most people expect.",
    },
}

LAB_FEATURES = sorted({
    flag for test in LAB_TESTS.values() for flag in test.get("flags", {}).values()
})

LAB_CRITICAL_MESSAGES = {
    "platelets_low": ("Dangerously low platelet count",
                      "A platelet count this low carries a serious bleeding risk. This "
                      "needs a doctor today, not tomorrow."),
    "haemoglobin_low": ("Severe anaemia",
                        "Haemoglobin this low means your blood is carrying far too little "
                        "oxygen. This needs assessment today and may need a transfusion."),
    "fasting_glucose_high": ("Very high blood sugar",
                             "Blood sugar this high can lead to a diabetic emergency. "
                             "Get seen today."),
    "fasting_glucose_low": ("Blood sugar too low",
                            "Low blood sugar can cause collapse. If the person is awake "
                            "and able to swallow, give sugar or juice now, then get help."),
    "creatinine_high": ("Kidney function significantly reduced",
                        "A creatinine this high means the kidneys are not filtering "
                        "properly. See a doctor promptly."),
    "wbc_high": ("Very high white cell count",
                 "This usually means a significant infection that needs treatment now."),
    "wbc_low": ("Very low white cell count",
                "The body's ability to fight infection is reduced. Avoid crowds and see "
                "a doctor promptly."),
    "bilirubin_high": ("Significant jaundice",
                       "Bilirubin this high means the liver needs urgent assessment."),
    "hba1c_high": ("Blood sugar badly out of control",
                   "An HbA1c this high means sustained high sugar and a real risk of "
                   "damage to eyes, kidneys and nerves. See a doctor this week."),
}


# ---------------------------------------------------------------------------
# 6. URGENCY - the primary output of this tool
# ---------------------------------------------------------------------------

URGENCY_LEVELS = ["routine", "prompt", "urgent", "emergency"]

URGENCY_INFO = {
    "routine": {
        "rank": 0,
        "headline": "Worth seeing a doctor, but no rush",
        "detail": "Book an appointment in the next week or two, or visit your nearest "
                  "Ayushman Arogya Mandir. Consultation there is free.",
        "mr": "डॉक्टरांना दाखवा, पण घाई नाही",
    },
    "prompt": {
        "rank": 1,
        "headline": "See a doctor in the next day or two",
        "detail": "Do not leave this until next week. A government health centre visit "
                  "costs nothing.",
        "mr": "एक-दोन दिवसांत डॉक्टरांना भेटा",
    },
    "urgent": {
        "rank": 2,
        "headline": "See a doctor today",
        "detail": "Go to a hospital or clinic today. Carry any previous reports with you.",
        "mr": "आजच डॉक्टरांना भेटा",
    },
    "emergency": {
        "rank": 3,
        "headline": "Go to hospital now",
        "detail": "Call 108 for a free ambulance. Do not drive yourself.",
        "mr": "ताबडतोब रुग्णालयात जा",
    },
}


def escalate(current, target):
    """Urgency may only ever go up. This one function is the safety policy."""
    if URGENCY_INFO[target]["rank"] > URGENCY_INFO[current]["rank"]:
        return target
    return current


# ---------------------------------------------------------------------------
# 7. FEATURE ORDER - this order IS the model's input contract
# ---------------------------------------------------------------------------

ALL_FEATURES = SYMPTOMS + CONTEXT_FEATURES + LAB_FEATURES


def validate():
    """Check the knowledge base for internal contradictions."""
    from .disease_data import DISEASES

    problems = []
    vocab = set(SYMPTOMS)
    for name, profile in DISEASES.items():
        for key in profile["primary"] + profile["secondary"]:
            if key not in vocab:
                problems.append(f"{name}: unknown symptom '{key}'")
        if profile["urgency"] not in URGENCY_LEVELS:
            problems.append(f"{name}: bad urgency '{profile['urgency']}'")

    known = set(DISEASES)
    for mod in CONTEXT_MODIFIERS:
        if mod["disease"] not in known:
            problems.append(f"modifier targets unknown disease '{mod['disease']}'")
    for name in PREGNANCY_ESCALATE:
        if name not in known:
            problems.append(f"pregnancy escalation targets unknown disease '{name}'")
    return problems
