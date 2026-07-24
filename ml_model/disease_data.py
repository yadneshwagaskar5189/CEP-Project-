"""
disease_data.py
---------------
Condition profiles for the symptom checker.

Each entry carries:
    primary        symptoms present in most cases          (sampled at p=0.86)
    secondary      symptoms present in some cases          (sampled at p=0.34)
    specialisation matched against Hospital.specialisations for referral
    urgency        routine | prompt | urgent | emergency
    about          one plain-language paragraph
    precautions    what to actually do
    avoid          DRUG SAFETY: what NOT to take. See note below.
    tests          what to ask the doctor to check
    sensitive      True for mental health, which is presented differently

WHY THERE IS NO "MEDICINES TO TAKE" FIELD
-----------------------------------------
This tool deliberately never names a medicine to take.

The clearest reason is dengue and flu. They share fever, body ache, headache and
fatigue, so they are among the pairs this model most often confuses. Ibuprofen is
ordinary for flu and dangerous in dengue, because of the bleeding risk. The
correct advice is opposite for the two conditions that are hardest to tell apart.

An app confident enough to name a drug is confident enough to cause harm that
way. So the `avoid` field exists instead: harm reduction rather than prescribing.
Telling someone what not to swallow is safe even when the prediction is wrong.
"""

DISEASES = {

    # ---------------------------------------------------------------- fevers
    "Common Cold": {
        "primary": ["runny_nose", "sneezing", "sore_throat", "blocked_nose", "cough"],
        "secondary": ["headache", "fatigue", "body_ache", "low_grade_fever",
                      "loss_of_smell", "post_nasal_drip"],
        "specialisation": "General Medicine", "urgency": "routine",
        "about": "A mild viral infection of the nose and throat. It clears on its own in "
                 "about a week and does not need any medicine to cure it.",
        "precautions": [
            "Rest and drink plenty of warm fluids.",
            "Steam inhalation eases a blocked nose.",
            "Cover your mouth when coughing and wash hands often.",
            "See a doctor if fever lasts beyond 3 days or breathing becomes difficult.",
        ],
        "avoid": ["Antibiotics do nothing for a cold. Taking them adds side effects and "
                  "contributes to antibiotic resistance."],
        "tests": ["Usually none. A cold is diagnosed by its pattern."],
    },
    "Influenza (Flu)": {
        "primary": ["fever", "body_ache", "fatigue", "headache", "dry_cough", "chills"],
        "secondary": ["sore_throat", "runny_nose", "weakness", "loss_of_appetite",
                      "muscle_pain", "high_fever"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A viral infection that arrives faster and harder than a cold, with "
                 "fever and heavy body ache.",
        "precautions": [
            "Rest at home and stay away from others while you have fever.",
            "Drink fluids regularly to avoid dehydration.",
            "Seek care urgently if breathing becomes difficult or chest pain starts.",
        ],
        "avoid": ["Antibiotics do not work on flu. Only take them if a doctor finds a "
                  "separate bacterial infection."],
        "tests": ["Usually none. A doctor may test if you are elderly, pregnant or have "
                  "a lung condition."],
    },
    "COVID-19": {
        "primary": ["fever", "dry_cough", "fatigue", "sore_throat"],
        "secondary": ["loss_of_smell", "loss_of_taste", "body_ache", "headache",
                      "breathlessness", "diarrhoea", "blocked_nose"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A viral respiratory infection. Most cases are mild, but loss of smell "
                 "or taste is a distinctive clue.",
        "precautions": [
            "Isolate at home while you have symptoms.",
            "Monitor your breathing. Seek care if you become breathless at rest.",
            "Rest and stay hydrated.",
        ],
        "avoid": ["Do not take steroids at home without a doctor. Taken too early they "
                  "make viral infections worse."],
        "tests": ["RT-PCR or rapid antigen test if testing is available and you are "
                  "high risk."],
    },
    "Dengue": {
        "primary": ["high_fever", "severe_headache", "joint_pain", "muscle_pain", "rash"],
        "secondary": ["nausea", "vomiting", "fatigue", "red_spots", "bruising_easily",
                      "sensitivity_to_light", "eye_pain", "bleeding_gums", "nosebleed"],
        "specialisation": "General Medicine", "urgency": "urgent",
        "about": "A mosquito-borne viral fever, common in Maharashtra during and after "
                 "the monsoon. The danger is not the fever itself but falling platelets "
                 "and fluid loss.",
        "precautions": [
            "Get a blood test today. Platelet count needs monitoring, sometimes daily.",
            "Drink fluids constantly. Dehydration is the main cause of deterioration.",
            "Go to hospital immediately if there is bleeding, severe stomach pain, "
            "vomiting that will not stop, or drowsiness.",
            "Remove standing water around your home to stop mosquito breeding.",
        ],
        "avoid": ["Do NOT take aspirin, ibuprofen or other NSAID painkillers. They "
                  "increase bleeding risk, which is exactly the danger in dengue. Ask a "
                  "doctor which painkiller is safe for you."],
        "tests": ["CBC with platelet count", "Dengue NS1 antigen (first few days) or "
                  "IgM antibody (after day 5)"],
    },
    "Malaria": {
        "primary": ["fever", "chills", "headache", "night_sweats", "vomiting"],
        "secondary": ["nausea", "muscle_pain", "fatigue", "diarrhoea", "abdominal_pain",
                      "pale_skin", "yellow_eyes"],
        "specialisation": "General Medicine", "urgency": "urgent",
        "about": "A mosquito-borne parasitic infection, with a typical cycle of fever, "
                 "then violent chills, then heavy sweating.",
        "precautions": [
            "Get a blood smear or rapid test the same day. Early treatment matters.",
            "Complete the full course even after you feel better.",
            "Use mosquito nets and repellents.",
            "Return to hospital immediately if confusion or breathing trouble develops.",
        ],
        "avoid": ["Never take leftover antimalarial tablets from a previous illness. "
                  "The parasite type determines the drug."],
        "tests": ["Peripheral blood smear", "Rapid malaria antigen test"],
    },
    "Typhoid": {
        "primary": ["fever", "abdominal_pain", "weakness", "headache", "loss_of_appetite"],
        "secondary": ["constipation", "diarrhoea", "rash", "nausea", "body_ache",
                      "fatigue", "low_grade_fever"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A bacterial infection from contaminated food or water. The fever "
                 "characteristically climbs a little higher each day.",
        "precautions": [
            "Drink only boiled or filtered water.",
            "Complete the full antibiotic course exactly as prescribed.",
            "Eat soft, easily digestible food while recovering.",
            "Wash hands with soap before eating and after using the toilet.",
        ],
        "avoid": ["Do not stop antibiotics when the fever settles. Stopping early causes "
                  "relapse and drug resistance."],
        "tests": ["Blood culture (most reliable)", "Widal test", "CBC"],
    },
    "Chikungunya": {
        "primary": ["fever", "joint_pain", "joint_swelling", "muscle_pain", "rash"],
        "secondary": ["headache", "fatigue", "nausea", "joint_stiffness",
                      "restricted_movement", "small_joint_pain"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A mosquito-borne viral illness. The joint pain often continues for "
                 "weeks or months after the fever has gone.",
        "precautions": [
            "Rest, fluids, and gentle movement of stiff joints.",
            "Get tested to rule out dengue, which looks similar but is more dangerous.",
            "Clear standing water near your home.",
        ],
        "avoid": ["Until dengue has been ruled out, avoid aspirin and ibuprofen. The two "
                  "look alike early on and the bleeding risk in dengue is real."],
        "tests": ["Chikungunya IgM", "Dengue NS1 to rule out dengue", "CBC"],
    },
    "Leptospirosis": {
        "primary": ["fever", "calf_pain", "headache", "red_eyes"],
        "secondary": ["muscle_pain", "vomiting", "yellow_skin", "yellow_eyes",
                      "chills", "abdominal_pain", "reduced_urine"],
        "specialisation": "General Medicine", "urgency": "urgent",
        "about": "A bacterial infection caught from water contaminated by animal urine. "
                 "It appears after wading through flood water, which makes it a monsoon "
                 "illness in Maharashtra.",
        "precautions": [
            "Tell the doctor if you waded through flood or drain water recently. That "
            "history is what makes them test for it.",
            "Get treated early. Late leptospirosis damages the kidneys and liver.",
            "Wear boots if you must walk through standing water.",
        ],
        "avoid": ["Do not delay. This is one where waiting to see if the fever settles "
                  "is genuinely dangerous."],
        "tests": ["Leptospira IgM ELISA", "Kidney and liver function tests", "CBC"],
    },
    "Viral Fever": {
        "primary": ["fever", "body_ache", "fatigue", "headache"],
        "secondary": ["sore_throat", "cough", "loss_of_appetite", "chills", "nausea",
                      "weakness"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A general viral fever with no single distinguishing feature. Most "
                 "settle in three to five days on their own.",
        "precautions": [
            "Rest and drink fluids.",
            "If fever continues past 3 days, get tested for dengue, malaria and typhoid.",
            "Watch for warning signs: bleeding, breathlessness, drowsiness, severe pain.",
        ],
        "avoid": ["Antibiotics are useless against viruses and are massively overused in "
                  "India for exactly this. Do not ask a chemist for them."],
        "tests": ["CBC", "Dengue and malaria tests if the fever lasts beyond 3 days"],
    },
    "Chickenpox": {
        "primary": ["rash", "blisters", "fever", "itching"],
        "secondary": ["fatigue", "headache", "loss_of_appetite", "body_ache",
                      "sore_throat", "red_spots"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A very contagious viral infection: fever first, then itchy blisters "
                 "that appear in waves.",
        "precautions": [
            "Stay isolated until every blister has crusted over.",
            "Do not scratch. Keep nails short to avoid scarring and infection.",
            "See a doctor urgently if the patient is pregnant, an adult, or has "
            "breathing difficulty or confusion.",
        ],
        "avoid": ["Do NOT give aspirin to a child with chickenpox. It can cause Reye's "
                  "syndrome, which damages the brain and liver."],
        "tests": ["Usually diagnosed by looking at the rash. No test needed."],
    },
    "Measles": {
        "primary": ["fever", "rash", "cough", "red_eyes", "runny_nose"],
        "secondary": ["high_fever", "loss_of_appetite", "diarrhoea", "mouth_ulcers",
                      "sensitivity_to_light", "swollen_glands"],
        "specialisation": "General Medicine", "urgency": "urgent",
        "about": "A highly contagious viral infection that is largely preventable by "
                 "vaccination. The rash starts at the face and spreads downward.",
        "precautions": [
            "Isolate the child and inform the school or Anganwadi.",
            "Vitamin A is given as part of standard treatment. Ask the doctor.",
            "Measles vaccination is free under the national immunisation programme.",
            "Return immediately if breathing becomes fast or the child becomes drowsy.",
        ],
        "avoid": ["Do not treat this at home alone. Measles complications, especially "
                  "pneumonia, develop fast in young children."],
        "tests": ["Measles IgM if confirmation is needed", "Usually a clinical diagnosis"],
    },
    "Mumps": {
        "primary": ["swollen_jaw", "fever", "swollen_glands"],
        "secondary": ["headache", "body_ache", "loss_of_appetite", "ear_pain",
                      "severe_sore_throat", "fatigue"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "A viral infection causing painful swelling of the salivary glands in "
                 "front of the ears.",
        "precautions": [
            "Soft food and cold compresses ease the pain.",
            "Stay away from others for about five days after the swelling starts.",
            "See a doctor urgently if there is severe headache, neck stiffness, or "
            "testicular pain in a male patient.",
        ],
        "avoid": ["Avoid sour foods and citrus, which trigger painful gland spasms."],
        "tests": ["Usually a clinical diagnosis", "Mumps IgM if uncertain"],
    },
    "Tuberculosis (TB)": {
        "primary": ["chronic_cough", "cough_with_phlegm", "weight_loss", "night_sweats",
                    "low_grade_fever"],
        "secondary": ["coughing_blood", "chest_pain", "loss_of_appetite", "weakness",
                      "breathlessness", "fatigue", "swollen_glands"],
        "specialisation": "Pulmonology", "urgency": "urgent",
        "about": "A bacterial infection, usually of the lungs. Any cough lasting more "
                 "than two weeks should be tested for TB. Treatment is free everywhere "
                 "in India and it is curable.",
        "precautions": [
            "Get a free sputum test at any government DOTS centre. No referral needed.",
            "Never stop treatment early. Stopping causes drug-resistant TB, which is far "
            "harder and longer to cure.",
            "Notified patients receive Rs 1,000 per month under Ni-kshay Poshan Yojana.",
            "Everyone in the household should be screened.",
            "Keep rooms ventilated and cover your mouth when coughing.",
        ],
        "avoid": ["Do not take random cough syrups for weeks hoping it passes. That delay "
                  "is how TB spreads through a household."],
        "tests": ["Sputum microscopy or CBNAAT / NAAT (free at DOTS centres)",
                  "Chest X-ray"],
    },
    "Pneumonia": {
        "primary": ["fever", "cough_with_phlegm", "breathlessness", "chest_pain", "chills"],
        "secondary": ["rapid_breathing", "fatigue", "confusion", "loss_of_appetite",
                      "night_sweats", "nausea", "blue_lips"],
        "specialisation": "Pulmonology", "urgency": "urgent",
        "about": "Infection of the lung tissue. It can become serious quickly in young "
                 "children and older adults.",
        "precautions": [
            "See a doctor the same day. A chest X-ray is usually needed.",
            "Complete the full antibiotic course.",
            "Go to hospital immediately if lips or fingertips look blue, or breathing "
            "is very fast.",
            "Pneumococcal and flu vaccines reduce the risk in older adults.",
        ],
        "avoid": ["Do not rely on cough suppressants. Suppressing a productive cough in "
                  "pneumonia keeps infected phlegm in the lungs."],
        "tests": ["Chest X-ray", "CBC", "Oxygen saturation (pulse oximeter)"],
    },
    "Bronchitis": {
        "primary": ["cough_with_phlegm", "chest_tightness", "fatigue"],
        "secondary": ["low_grade_fever", "wheezing", "breathlessness", "sore_throat",
                      "body_ache", "chest_pain"],
        "specialisation": "Pulmonology", "urgency": "routine",
        "about": "Inflammation of the airways, usually following a viral infection. The "
                 "cough can linger for weeks after everything else has settled.",
        "precautions": [
            "Rest, fluids and steam inhalation.",
            "Stop smoking and avoid smoke exposure entirely while recovering.",
            "If the cough passes two weeks, get tested for TB.",
        ],
        "avoid": ["Most bronchitis is viral, so antibiotics usually do nothing. Do not "
                  "buy them over the counter."],
        "tests": ["Usually none", "Chest X-ray if the cough persists"],
    },
    "Hepatitis A (Jaundice)": {
        "primary": ["yellow_skin", "yellow_eyes", "fatigue", "loss_of_appetite", "nausea"],
        "secondary": ["abdominal_pain", "vomiting", "fever", "itching", "weakness",
                      "right_upper_abdominal_pain", "dark_urine", "pale_stool"],
        "specialisation": "Gastroenterology", "urgency": "urgent",
        "about": "Liver inflammation, usually spread through contaminated food or water. "
                 "It turns the skin and eyes yellow and the urine dark.",
        "precautions": [
            "Get liver function tests done and rest as advised.",
            "Drink only boiled or filtered water. Avoid roadside food.",
            "Go to hospital immediately if there is confusion, drowsiness or vomiting "
            "of blood.",
        ],
        "avoid": ["Avoid alcohol completely. Do not take paracetamol, herbal remedies or "
                  "any other medicine without asking a doctor first, because a damaged "
                  "liver cannot process them safely."],
        "tests": ["Liver function tests (LFT) including bilirubin",
                  "Hepatitis A IgM", "Hepatitis B and E if indicated"],
    },
    "Amoebic Dysentery": {
        "primary": ["bloody_diarrhoea", "abdominal_pain", "cramping_pain"],
        "secondary": ["fever", "weakness", "loss_of_appetite", "bloating", "nausea",
                      "weight_loss"],
        "specialisation": "Gastroenterology", "urgency": "prompt",
        "about": "A parasitic infection of the large intestine, from contaminated food "
                 "or water, causing loose motions with blood or mucus.",
        "precautions": [
            "Get a stool test to confirm before treatment.",
            "Drink ORS to replace what you are losing.",
            "Boil drinking water and wash vegetables well.",
        ],
        "avoid": ["Do not take anti-diarrhoeal drugs that stop motions when there is "
                  "blood or fever. Trapping the infection makes it worse."],
        "tests": ["Stool routine and microscopy", "Stool for ova and cysts"],
    },
    "Worm Infestation": {
        "primary": ["itching_around_anus", "abdominal_pain", "worms_in_stool"],
        "secondary": ["loss_of_appetite", "weight_loss", "fatigue", "pale_skin",
                      "nausea", "difficulty_sleeping", "irritability"],
        "specialisation": "General Medicine", "urgency": "routine",
        "about": "Intestinal worms, very common in children. A major hidden cause of "
                 "anaemia and poor growth.",
        "precautions": [
            "Deworming tablets are given free to all children under the National "
            "Deworming Day programme, twice a year.",
            "Treat the whole household at the same time.",
            "Cut nails short, wash hands before eating, and wear footwear outdoors.",
        ],
        "avoid": ["Do not repeat deworming tablets more often than advised."],
        "tests": ["Stool for ova and cysts", "Haemoglobin, since worms cause anaemia"],
    },

    # ------------------------------------------------------------ digestion
    "Gastroenteritis": {
        "primary": ["diarrhoea", "vomiting", "abdominal_pain", "nausea"],
        "secondary": ["fever", "weakness", "loss_of_appetite", "cramps", "bloating",
                      "headache", "dehydration"],
        "specialisation": "Gastroenterology", "urgency": "prompt",
        "about": "Infection or irritation of the stomach and intestines, usually from "
                 "contaminated food or water. Dehydration is the real risk, not the "
                 "infection.",
        "precautions": [
            "Start ORS early. It is free at government health centres and it is the "
            "actual treatment, not an optional extra.",
            "Small sips often, rather than a big glass at once.",
            "Go to hospital if there is blood in stool, very little urine, or you cannot "
            "keep any fluid down.",
        ],
        "avoid": ["Do not take drugs that stop motions if there is fever or blood. Avoid "
                  "milk, oily and spicy food until you recover."],
        "tests": ["Usually none", "Stool test if there is blood or it lasts beyond 3 days"],
    },
    "Food Poisoning": {
        "primary": ["vomiting", "diarrhoea", "abdominal_pain", "nausea"],
        "secondary": ["fever", "weakness", "cramps", "headache", "dehydration", "chills"],
        "specialisation": "Gastroenterology", "urgency": "prompt",
        "about": "Sudden illness from contaminated food, usually starting within hours "
                 "of eating and settling within a day or two.",
        "precautions": [
            "ORS and fluids. Rest the stomach for a few hours, then eat plain food.",
            "If several people who ate the same meal are ill, tell the doctor.",
            "Seek care if there is blood, high fever, or signs of dehydration.",
        ],
        "avoid": ["Do not force food. Do not take antibiotics unless prescribed."],
        "tests": ["Usually none", "Stool culture if severe or prolonged"],
    },
    "Acid Reflux (GERD)": {
        "primary": ["heartburn", "acidity", "belching", "upper_abdominal_pain"],
        "secondary": ["nausea", "sore_throat", "hoarse_voice", "cough",
                      "difficulty_sleeping", "chest_pain", "bloating", "early_fullness"],
        "specialisation": "Gastroenterology", "urgency": "routine",
        "about": "Stomach acid flowing back into the food pipe, causing a burning feeling "
                 "in the chest, typically after meals or on lying down.",
        "precautions": [
            "Do not lie down for 2 to 3 hours after eating.",
            "Smaller meals. Avoid very oily and spicy food and late dinners.",
            "Raise the head end of the bed slightly.",
            "Chest pain is not always acidity. Get it checked if it is new, severe, or "
            "comes with sweating or breathlessness.",
        ],
        "avoid": ["Reduce tobacco, alcohol and caffeine, which all relax the valve that "
                  "is supposed to keep acid down."],
        "tests": ["Usually diagnosed from the history", "Endoscopy if there is weight "
                  "loss, difficulty swallowing, or it does not settle"],
    },
    "Peptic Ulcer": {
        "primary": ["upper_abdominal_pain", "bloating", "nausea", "indigestion"],
        "secondary": ["vomiting", "loss_of_appetite", "black_stool", "weight_loss",
                      "heartburn", "belching", "early_fullness"],
        "specialisation": "Gastroenterology", "urgency": "prompt",
        "about": "A sore in the lining of the stomach or upper intestine, most often "
                 "caused by H. pylori bacteria or long-term painkiller use.",
        "precautions": [
            "Get tested for H. pylori. It is treatable with a short course.",
            "Cut down smoking, alcohol and very spicy food.",
            "Go to hospital immediately if you vomit blood or pass black tarry stool.",
        ],
        "avoid": ["Avoid painkillers of the ibuprofen and diclofenac family, especially "
                  "on an empty stomach. They are a leading cause of ulcers and can cause "
                  "one to bleed."],
        "tests": ["H. pylori test (breath, stool or endoscopy)", "Endoscopy", "CBC"],
    },
    "Irritable Bowel Syndrome": {
        "primary": ["abdominal_pain", "bloating", "cramping_pain"],
        "secondary": ["diarrhoea", "constipation", "belching", "nausea", "anxiety",
                      "early_fullness", "indigestion"],
        "specialisation": "Gastroenterology", "urgency": "routine",
        "about": "A long-term gut disorder where the bowel is oversensitive. Symptoms "
                 "come and go, often worse with stress, and there is no damage visible "
                 "on tests.",
        "precautions": [
            "Keep a food diary to identify your own triggers.",
            "Regular meal timings and regular sleep help more than any single food rule.",
            "Stress management genuinely reduces symptoms here.",
            "Any weight loss, bleeding or night-time symptoms means this is not IBS. "
            "Get investigated.",
        ],
        "avoid": ["Do not self-diagnose IBS if you are over 45 with new symptoms. Rule "
                  "out other causes first."],
        "tests": ["Tests are mainly to exclude other conditions: CBC, thyroid, coeliac "
                  "screen, stool test"],
    },
    "Piles (Haemorrhoids)": {
        "primary": ["blood_in_stool", "pain_passing_stool", "lump_at_anus"],
        "secondary": ["constipation", "itching_around_anus", "abdominal_pain"],
        "specialisation": "General Surgery", "urgency": "routine",
        "about": "Swollen veins around the back passage, causing bright red bleeding "
                 "after passing stool and sometimes a lump.",
        "precautions": [
            "Increase fibre and water. Hard stool is the root cause.",
            "Do not sit straining on the toilet for long periods.",
            "Warm sitz baths ease the pain.",
            "Any rectal bleeding still needs a doctor's confirmation. Do not assume "
            "piles, especially over 45.",
        ],
        "avoid": ["Avoid long-term laxative use without advice."],
        "tests": ["Clinical examination", "Colonoscopy if you are over 45 or the bleeding "
                  "pattern is unusual"],
    },
    "Appendicitis": {
        "primary": ["right_lower_abdominal_pain", "loss_of_appetite", "nausea", "fever"],
        "secondary": ["vomiting", "abdominal_pain", "constipation", "cramping_pain",
                      "restlessness"],
        "specialisation": "General Surgery", "urgency": "emergency",
        "about": "Inflammation of the appendix. The pain classically starts near the "
                 "navel and then settles in the lower right side. It usually needs "
                 "surgery, and a burst appendix is dangerous.",
        "precautions": [
            "Go to a hospital with surgical facilities now.",
            "Do not eat or drink anything, in case surgery is needed.",
            "Do not apply a hot water bottle to the abdomen.",
        ],
        "avoid": ["Do NOT take painkillers to push through this. Masking the pain delays "
                  "diagnosis, and a delayed appendix can burst."],
        "tests": ["Clinical examination by a surgeon", "Ultrasound abdomen", "CBC"],
    },
    "Gallstones": {
        "primary": ["right_upper_abdominal_pain", "pain_after_fatty_food", "nausea"],
        "secondary": ["vomiting", "bloating", "indigestion", "fever", "yellow_eyes",
                      "belching", "upper_abdominal_pain"],
        "specialisation": "General Surgery", "urgency": "prompt",
        "about": "Hard stones in the gallbladder. Pain typically comes in attacks after "
                 "oily meals, in the upper right abdomen.",
        "precautions": [
            "Get an ultrasound. It is the definitive test and it is cheap.",
            "Reduce fatty and fried food while awaiting review.",
            "Go to hospital if there is fever with the pain, or the eyes turn yellow.",
        ],
        "avoid": ["Do not ignore repeated attacks. An inflamed or blocked gallbladder is "
                  "a surgical emergency."],
        "tests": ["Ultrasound abdomen", "Liver function tests"],
    },
    "Constipation": {
        "primary": ["constipation", "bloating", "abdominal_pain"],
        "secondary": ["pain_passing_stool", "loss_of_appetite", "nausea", "early_fullness",
                      "lump_at_anus"],
        "specialisation": "Gastroenterology", "urgency": "routine",
        "about": "Difficulty passing stool, or passing it less often than usual. Usually "
                 "diet and fluid related, sometimes a side effect of medicines.",
        "precautions": [
            "More water, more fibre, more movement. In that order.",
            "Do not ignore the urge when it comes.",
            "New constipation over the age of 45, or with weight loss or bleeding, needs "
            "investigation.",
        ],
        "avoid": ["Avoid regular stimulant laxatives. The bowel becomes dependent on them."],
        "tests": ["Usually none", "Thyroid test and CBC if it is persistent"],
    },

    # -------------------------------------------------------- heart & blood
    "Hypertension (High BP)": {
        "primary": ["headache", "dizziness", "blurred_vision"],
        "secondary": ["chest_pain", "palpitations", "breathlessness", "fatigue",
                      "confusion", "general_swelling", "nosebleed"],
        "specialisation": "Cardiology", "urgency": "prompt",
        "about": "Persistently raised blood pressure. It usually causes no symptoms at "
                 "all, which is exactly why it goes undetected until it causes a stroke "
                 "or heart attack.",
        "precautions": [
            "Get your BP measured. It is free at any Ayushman Arogya Mandir and takes "
            "one minute.",
            "Reduce salt, especially papad, pickle and packaged snacks.",
            "Walk 30 minutes on most days.",
            "Free BP medicines are available under the NP-NCD programme.",
        ],
        "avoid": ["Never stop BP medicines because you feel fine. Feeling fine is the "
                  "normal state of treated high blood pressure."],
        "tests": ["Blood pressure measured on 2 or 3 separate days", "Kidney function",
                  "Blood sugar and lipid profile", "ECG"],
    },
    "Angina (Heart Artery Disease)": {
        "primary": ["chest_pain_on_exertion", "chest_tightness", "breathless_on_exertion"],
        "secondary": ["pain_radiating_to_arm", "fatigue", "palpitations", "cold_sweat",
                      "nausea", "dizziness"],
        "specialisation": "Cardiology", "urgency": "urgent",
        "about": "Narrowed heart arteries. Chest tightness appears on exertion and eases "
                 "with rest. It is a warning sign that a heart attack could follow.",
        "precautions": [
            "See a cardiologist promptly, even if the pain settles with rest.",
            "If chest pain comes at rest, lasts more than a few minutes, or comes with "
            "sweating, call 108 immediately.",
            "Stop smoking. This single change matters more than any other.",
        ],
        "avoid": ["Do not push through chest pain to finish a task. Do not drive yourself "
                  "to hospital during an episode."],
        "tests": ["ECG", "Treadmill or stress test", "Echocardiogram",
                  "Lipid profile and blood sugar"],
    },
    "Heart Failure": {
        "primary": ["breathless_on_exertion", "ankle_swelling", "fatigue",
                    "breathless_lying_down"],
        "secondary": ["palpitations", "cough", "weight_gain", "reduced_urine",
                      "night_urination", "general_swelling", "loss_of_appetite"],
        "specialisation": "Cardiology", "urgency": "urgent",
        "about": "The heart cannot pump strongly enough, so fluid backs up into the lungs "
                 "and legs. Being breathless lying flat is a characteristic sign.",
        "precautions": [
            "See a doctor promptly. This is manageable with the right medicines.",
            "Weigh yourself daily. A sudden gain of 2 kg in a few days means fluid.",
            "Restrict salt strictly.",
            "Sleep propped up on extra pillows if lying flat is difficult.",
        ],
        "avoid": ["Avoid NSAID painkillers, which make the body hold fluid and worsen "
                  "heart failure."],
        "tests": ["Echocardiogram", "ECG", "Chest X-ray", "Kidney function", "NT-proBNP"],
    },
    "Anaemia": {
        "primary": ["fatigue", "weakness", "pale_skin", "breathless_on_exertion"],
        "secondary": ["dizziness", "headache", "palpitations", "hair_loss",
                      "cold_intolerance", "brittle_nails", "heavy_periods",
                      "poor_concentration"],
        "specialisation": "General Medicine", "urgency": "prompt",
        "about": "Too few healthy red blood cells to carry oxygen. Extremely common in "
                 "Indian women and adolescent girls, and very often untreated.",
        "precautions": [
            "Get a haemoglobin test. It is free at government health centres.",
            "Eat iron-rich food: green leafy vegetables, jaggery, dates, ragi, pulses.",
            "Take vitamin C, such as lemon or amla, with iron-rich meals. It roughly "
            "doubles iron absorption.",
            "Free iron and folic acid tablets are given under Anaemia Mukt Bharat.",
        ],
        "avoid": ["Do not drink tea or coffee with meals. Both block iron absorption, "
                  "which is a common and easily fixed mistake."],
        "tests": ["CBC with haemoglobin", "Serum ferritin", "Stool for occult blood if "
                  "the cause is unclear"],
    },

    # ------------------------------------------------------------ endocrine
    "Type 2 Diabetes": {
        "primary": ["excessive_thirst", "frequent_urination", "fatigue", "excessive_hunger"],
        "secondary": ["weight_loss", "blurred_vision", "slow_healing_wounds",
                      "tingling_hands_feet", "itching", "weakness", "night_urination",
                      "dark_neck_patches", "burning_feet"],
        "specialisation": "Endocrinology", "urgency": "prompt",
        "about": "The body cannot use sugar properly, so blood sugar stays high. Very "
                 "common in India and usually found years after it actually began.",
        "precautions": [
            "Get a fasting blood sugar and HbA1c test.",
            "Cut sugar, sweets and refined flour. Increase vegetables and whole grains.",
            "Walk daily and check your feet regularly for cuts you cannot feel.",
            "Free screening and medicines are available under NP-NCD at government "
            "health centres.",
        ],
        "avoid": ["Never stop diabetes medicines on your own. Be very cautious with "
                  "unregulated 'sugar cure' remedies, which sometimes contain hidden "
                  "steroids or undeclared drugs."],
        "tests": ["Fasting blood sugar", "HbA1c", "Post-meal blood sugar",
                  "Kidney function and urine protein", "Eye check"],
    },
    "Hypothyroidism": {
        "primary": ["fatigue", "weight_gain", "cold_intolerance", "dry_skin"],
        "secondary": ["hair_loss", "constipation", "memory_problems", "muscle_pain",
                      "excessive_sleep", "irregular_periods", "heavy_periods",
                      "general_swelling", "low_mood"],
        "specialisation": "Endocrinology", "urgency": "routine",
        "about": "An underactive thyroid gland, so everything in the body slows down. "
                 "Common, easily tested, and easily treated.",
        "precautions": [
            "Get a TSH blood test. It is simple and widely available.",
            "Take thyroid medicine on an empty stomach at the same time each day.",
            "Repeat the test as advised so the dose can be adjusted.",
            "Tell your doctor if you become pregnant. The dose usually needs increasing.",
        ],
        "avoid": ["Do not stop the medicine when you feel better. It is usually lifelong. "
                  "Do not take iron or calcium tablets within 4 hours of it."],
        "tests": ["TSH", "Free T4", "Thyroid antibodies if indicated"],
    },
    "Hyperthyroidism": {
        "primary": ["weight_loss", "palpitations", "heat_intolerance", "tremor", "anxiety"],
        "secondary": ["excessive_hunger", "difficulty_sleeping", "irritability", "fatigue",
                      "diarrhoea", "hair_loss", "muscle_pain", "irregular_periods",
                      "restlessness"],
        "specialisation": "Endocrinology", "urgency": "prompt",
        "about": "An overactive thyroid gland, so everything speeds up: heart rate, "
                 "appetite, bowels, and often mood.",
        "precautions": [
            "Get a thyroid function test.",
            "Reduce caffeine, which worsens palpitations and restlessness.",
            "See a doctor promptly if the heartbeat is very fast or irregular.",
        ],
        "avoid": ["Avoid iodine supplements and kelp products unless a doctor advises "
                  "them. They can make this worse."],
        "tests": ["TSH", "Free T3 and Free T4", "Thyroid scan if advised"],
    },
    "Vitamin B12 Deficiency": {
        "primary": ["fatigue", "tingling_hands_feet", "weakness", "poor_concentration"],
        "secondary": ["pale_skin", "memory_problems", "mouth_ulcers", "loss_of_balance",
                      "burning_feet", "low_mood", "irritability"],
        "specialisation": "General Medicine", "urgency": "routine",
        "about": "B12 is needed for nerves and red blood cells. Deficiency is very common "
                 "in vegetarian diets, and the nerve damage can become permanent if left "
                 "too long.",
        "precautions": [
            "Get a serum B12 test.",
            "Vegetarians should include dairy and fortified foods. B12 is not available "
            "from plant foods in useful amounts.",
            "Do not delay treatment if there is numbness or tingling.",
        ],
        "avoid": ["Do not assume tiredness is 'just weakness'. Untreated B12 deficiency "
                  "damages nerves permanently."],
        "tests": ["Serum vitamin B12", "CBC", "Homocysteine if borderline"],
    },
    "Vitamin D Deficiency": {
        "primary": ["bone_pain", "muscle_pain", "fatigue"],
        "secondary": ["difficulty_climbing_stairs", "low_mood", "weakness", "cramps",
                      "hair_loss", "frequent_fractures", "back_pain"],
        "specialisation": "General Medicine", "urgency": "routine",
        "about": "Very common in India despite the sunshine, because most people work "
                 "indoors and cover up outdoors. Causes aching bones and muscles.",
        "precautions": [
            "15 to 20 minutes of direct sunlight on arms and legs, several times a week.",
            "Get a vitamin D level checked if symptoms persist.",
            "Include milk, curd, eggs and fortified foods.",
        ],
        "avoid": ["Do not take high-dose vitamin D sachets repeatedly without testing. "
                  "Vitamin D overdose causes dangerously high calcium."],
        "tests": ["Serum 25-hydroxy vitamin D", "Serum calcium"],
    },

    # ---------------------------------------------------------- respiratory
    "Bronchial Asthma": {
        "primary": ["wheezing", "breathlessness", "chest_tightness", "cough"],
        "secondary": ["dry_cough", "difficulty_sleeping", "rapid_breathing", "fatigue",
                      "anxiety", "breathless_on_exertion"],
        "specialisation": "Pulmonology", "urgency": "prompt",
        "about": "The airways narrow and tighten in episodes, making breathing difficult. "
                 "It is very controllable with the right inhaler technique.",
        "precautions": [
            "Avoid known triggers: dust, smoke, strong perfume, cold air.",
            "Use inhalers exactly as prescribed. Inhalers are safe and not addictive, "
            "and delivering medicine straight to the lungs means a far lower dose.",
            "Always carry your reliever inhaler.",
            "Go to hospital immediately if you cannot speak a full sentence in one breath.",
        ],
        "avoid": ["Some people with asthma react badly to aspirin and ibuprofen. Ask your "
                  "doctor. Also avoid beta-blocker medicines unless a doctor has "
                  "specifically cleared them."],
        "tests": ["Spirometry (lung function test)", "Peak flow monitoring",
                  "Allergy testing if triggers are unclear"],
    },
    "COPD": {
        "primary": ["chronic_cough", "breathless_on_exertion", "cough_with_phlegm",
                    "wheezing"],
        "secondary": ["chest_tightness", "fatigue", "weight_loss", "ankle_swelling",
                      "blue_lips", "frequent_fractures"],
        "specialisation": "Pulmonology", "urgency": "prompt",
        "about": "Long-term airway damage, from smoking or from years of biomass smoke "
                 "exposure. In India, chulha smoke is a major cause in women who have "
                 "never smoked.",
        "precautions": [
            "Stop smoking. Nothing else slows this down as much.",
            "Switch from a chulha to LPG if at all possible. Ujjwala provides "
            "subsidised connections.",
            "Get flu and pneumococcal vaccination.",
            "Learn correct inhaler technique from your doctor and check it yearly.",
        ],
        "avoid": ["Avoid cough suppressants, which trap phlegm. Avoid sedatives, which "
                  "reduce your drive to breathe."],
        "tests": ["Spirometry", "Chest X-ray", "Oxygen saturation"],
    },
    "Allergic Rhinitis": {
        "primary": ["sneezing", "runny_nose", "itchy_eyes", "blocked_nose"],
        "secondary": ["watery_eyes", "post_nasal_drip", "cough", "headache",
                      "difficulty_sleeping", "loss_of_smell", "itching"],
        "specialisation": "ENT", "urgency": "routine",
        "about": "An allergic reaction in the nose to dust, pollen, smoke or animal hair. "
                 "There is no fever, which is what separates it from a cold.",
        "precautions": [
            "Identify and avoid your trigger. Dust and smoke are the commonest in "
            "Indian cities.",
            "Saline nasal rinses help more than most people expect.",
            "Keep bedding clean and sun-dried.",
        ],
        "avoid": ["Avoid long-term use of decongestant nose drops. After a few days they "
                  "cause worse blockage than the problem you started with."],
        "tests": ["Usually none", "Allergy testing if symptoms are severe or year-round"],
    },
    "Sinusitis": {
        "primary": ["facial_pain", "blocked_nose", "headache", "post_nasal_drip"],
        "secondary": ["low_grade_fever", "cough", "loss_of_smell", "sore_throat",
                      "fatigue", "ear_pain", "swollen_eyelids"],
        "specialisation": "ENT", "urgency": "routine",
        "about": "Inflammation of the air spaces around the nose, causing pressure and "
                 "pain across the cheeks and forehead, often worse on bending forward.",
        "precautions": [
            "Steam inhalation two or three times a day.",
            "Saline nasal rinses.",
            "Warm fluids to thin the mucus.",
            "See a doctor if pain is severe, vision changes, or it lasts beyond 10 days.",
        ],
        "avoid": ["Most sinusitis is viral. Antibiotics on day two are usually pointless."],
        "tests": ["Usually clinical", "CT sinuses if it keeps returning"],
    },

    # -------------------------------------------------------------- neuro
    "Migraine": {
        "primary": ["severe_headache", "nausea", "sensitivity_to_light",
                    "sensitivity_to_sound"],
        "secondary": ["vomiting", "blurred_vision", "dizziness", "irritability",
                      "fatigue", "aura_before_headache"],
        "specialisation": "Neurology", "urgency": "routine",
        "about": "A recurring headache, often one-sided and throbbing, made worse by "
                 "light, sound and movement.",
        "precautions": [
            "Rest in a dark quiet room during an attack.",
            "Keep a diary of triggers. Skipped meals, poor sleep and stress are the "
            "commonest.",
            "Keep regular sleep and meal timings, including on holidays.",
            "See a doctor if the pattern changes or attacks become more frequent.",
        ],
        "avoid": ["Do not take painkillers more than about twice a week. Overuse causes "
                  "rebound headaches that are worse than the migraine itself."],
        "tests": ["Usually none", "Brain imaging only if the pattern is unusual or "
                  "there are neurological signs"],
    },
    "Tension Headache": {
        "primary": ["headache_band", "headache", "neck_pain"],
        "secondary": ["fatigue", "difficulty_sleeping", "poor_concentration",
                      "irritability", "shoulder_pain", "anxiety"],
        "specialisation": "Neurology", "urgency": "routine",
        "about": "A tight band of pressure around the head, usually related to posture, "
                 "screen time, eye strain or stress. Not throbbing, not one-sided.",
        "precautions": [
            "Take a screen break every 30 minutes.",
            "Check your posture and screen height.",
            "Get your eyes tested if headaches come with reading or screen work.",
            "Regular sleep and hydration.",
        ],
        "avoid": ["Same warning as migraine: frequent painkiller use creates its own "
                  "daily headache."],
        "tests": ["Usually none", "Eye check"],
    },
    "Vertigo (BPPV)": {
        "primary": ["vertigo", "dizziness", "loss_of_balance", "nausea"],
        "secondary": ["vomiting", "blurred_vision", "headache", "ear_pain", "anxiety",
                      "ringing_in_ears"],
        "specialisation": "ENT", "urgency": "prompt",
        "about": "A spinning sensation triggered by head movement, from loose crystals "
                 "in the inner ear balance system. Alarming but usually harmless.",
        "precautions": [
            "Move your head slowly and sit up gradually from lying down.",
            "Sit or lie down when the spinning starts, to avoid a fall.",
            "An ENT doctor can perform simple repositioning manoeuvres that often fix it "
            "in one visit.",
            "Get checked urgently if it comes with slurred speech, double vision, or "
            "weakness. That is not BPPV.",
        ],
        "avoid": ["Avoid driving or climbing ladders until it settles."],
        "tests": ["Dix-Hallpike positional test by an ENT doctor", "Hearing test"],
    },
    "Sciatica": {
        "primary": ["pain_down_the_leg", "lower_back_pain", "tingling_hands_feet"],
        "secondary": ["back_pain", "restricted_movement", "muscle_pain", "cramps",
                      "difficulty_climbing_stairs", "weakness"],
        "specialisation": "Orthopaedics", "urgency": "prompt",
        "about": "Pain from a compressed nerve in the lower back, shooting down the back "
                 "of one leg, sometimes with numbness or tingling.",
        "precautions": [
            "Stay gently active. Complete bed rest makes it worse, not better.",
            "Avoid lifting and forward bending while it is acute.",
            "See a physiotherapist for specific exercises.",
            "Go urgently if you lose bladder or bowel control, or both legs go weak. "
            "That is a surgical emergency.",
        ],
        "avoid": ["Avoid aggressive massage or manipulation by untrained practitioners "
                  "while a nerve is compressed."],
        "tests": ["Clinical examination", "MRI lumbar spine if it persists or there is "
                  "weakness"],
    },
    "Epilepsy": {
        "primary": ["seizure", "blackout", "confusion"],
        "secondary": ["headache", "memory_problems", "fatigue", "mouth_ulcers",
                      "muscle_pain", "irritability", "loss_of_balance"],
        "specialisation": "Neurology", "urgency": "urgent",
        "about": "A tendency to recurrent seizures. It is very treatable, and most people "
                 "on the right medicine become seizure-free.",
        "precautions": [
            "See a neurologist. Do not treat a first fit as a one-off.",
            "During a fit: turn the person on their side, clear the area, time it. "
            "Never put anything in their mouth.",
            "Call 108 if a fit lasts more than 5 minutes or a second follows immediately.",
            "Avoid swimming alone, cooking over open flame alone, and driving until "
            "cleared by a doctor.",
        ],
        "avoid": ["Never stop epilepsy medicine suddenly. Abrupt stopping can trigger "
                  "prolonged seizures that are life threatening."],
        "tests": ["EEG", "MRI brain", "Blood sugar, calcium and sodium"],
    },

    # ------------------------------------------------------ musculoskeletal
    "Osteoarthritis": {
        "primary": ["joint_pain", "joint_stiffness", "knee_pain", "restricted_movement"],
        "secondary": ["joint_swelling", "back_pain", "muscle_pain", "cramps",
                      "difficulty_sleeping", "difficulty_climbing_stairs"],
        "specialisation": "Orthopaedics", "urgency": "routine",
        "about": "Wear-and-tear damage to joint cartilage, most often the knees. Stiffness "
                 "is worst after rest and eases with gentle movement.",
        "precautions": [
            "Keep moving. Gentle walking and prescribed exercise help more than rest.",
            "Reduce excess weight. Every kilogram lost takes several kilograms of load "
            "off the knee.",
            "Avoid sitting cross-legged on the floor and prolonged squatting.",
            "See a physiotherapist for a quadriceps strengthening programme.",
        ],
        "avoid": ["Avoid long-term daily painkillers without review. They damage the "
                  "stomach and kidneys over time."],
        "tests": ["X-ray of the affected joint", "Usually a clinical diagnosis"],
    },
    "Rheumatoid Arthritis": {
        "primary": ["small_joint_pain", "symmetric_joint_pain", "joint_stiffness",
                    "joint_swelling"],
        "secondary": ["fatigue", "low_grade_fever", "weight_loss", "loss_of_appetite",
                      "restricted_movement", "weakness", "dry_skin"],
        "specialisation": "Rheumatology", "urgency": "prompt",
        "about": "An autoimmune disease attacking the joint linings, typically the small "
                 "joints of both hands, with morning stiffness lasting over an hour.",
        "precautions": [
            "See a rheumatologist early. Early treatment prevents permanent joint damage, "
            "and the window for that matters.",
            "Keep joints moving with gentle exercise.",
            "This is not the same as ordinary age-related arthritis. It needs different "
            "medicines.",
        ],
        "avoid": ["Do not rely on painkillers alone. They mask symptoms while the joint "
                  "damage continues underneath."],
        "tests": ["Rheumatoid factor (RF)", "Anti-CCP antibodies", "ESR and CRP",
                  "X-ray of hands and feet"],
    },
    "Gout": {
        "primary": ["big_toe_pain", "joint_swelling", "joint_pain"],
        "secondary": ["restricted_movement", "low_grade_fever", "red_spots",
                      "knee_pain", "difficulty_climbing_stairs"],
        "specialisation": "Rheumatology", "urgency": "prompt",
        "about": "Uric acid crystals in a joint, causing sudden severe pain, usually in "
                 "the big toe, often starting at night. The joint becomes red, hot and "
                 "too tender to touch.",
        "precautions": [
            "Rest and elevate the joint during an attack.",
            "Drink plenty of water.",
            "Reduce red meat, organ meat, seafood and alcohol, especially beer.",
            "Get uric acid tested, but note it can read normal during an acute attack.",
        ],
        "avoid": ["Avoid aspirin, which raises uric acid. Do not start uric-acid-lowering "
                  "medicine during an acute attack unless a doctor directs it."],
        "tests": ["Serum uric acid", "Joint fluid examination if uncertain",
                  "Kidney function"],
    },
    "Cervical Spondylosis": {
        "primary": ["neck_pain", "joint_stiffness", "headache", "tingling_hands_feet"],
        "secondary": ["dizziness", "back_pain", "restricted_movement", "muscle_pain",
                      "weakness", "loss_of_balance", "shoulder_pain"],
        "specialisation": "Orthopaedics", "urgency": "routine",
        "about": "Age or posture-related wear in the neck bones, causing neck pain and "
                 "sometimes tingling down the arms.",
        "precautions": [
            "Keep screens at eye level and break every 30 minutes.",
            "Use a thin pillow. Avoid sleeping on your stomach.",
            "Do neck exercises taught by a physiotherapist.",
            "See a doctor urgently if there is hand weakness or difficulty walking.",
        ],
        "avoid": ["Avoid neck cracking by untrained people. Avoid heavy weights overhead."],
        "tests": ["X-ray cervical spine", "MRI if there is weakness or numbness"],
    },
    "Low Back Pain (Mechanical)": {
        "primary": ["lower_back_pain", "back_pain", "restricted_movement"],
        "secondary": ["muscle_pain", "cramps", "difficulty_sleeping",
                      "difficulty_climbing_stairs", "neck_pain"],
        "specialisation": "Orthopaedics", "urgency": "routine",
        "about": "Ordinary back strain from posture, lifting or prolonged sitting. The "
                 "large majority settle within six weeks.",
        "precautions": [
            "Stay active. Prolonged bed rest delays recovery.",
            "Learn to lift with your knees, not your back.",
            "Core strengthening exercises prevent recurrence.",
            "Red flags needing urgent review: fever, weight loss, night pain, leg "
            "weakness, or loss of bladder control.",
        ],
        "avoid": ["Avoid prolonged bed rest and avoid spinal manipulation from untrained "
                  "practitioners."],
        "tests": ["Usually none in the first 6 weeks",
                  "X-ray or MRI if red flags are present"],
    },
    "Frozen Shoulder": {
        "primary": ["shoulder_pain", "restricted_movement", "joint_stiffness"],
        "secondary": ["difficulty_sleeping", "muscle_pain", "neck_pain", "weakness"],
        "specialisation": "Orthopaedics", "urgency": "routine",
        "about": "The shoulder capsule thickens and tightens, so the joint becomes both "
                 "painful and genuinely stuck. Strongly associated with diabetes.",
        "precautions": [
            "Physiotherapy is the mainstay. It is slow, and consistency matters more "
            "than intensity.",
            "Get your blood sugar checked. Frozen shoulder is far more common in "
            "diabetes.",
            "Keep using the arm within a comfortable range.",
        ],
        "avoid": ["Do not force the joint through pain. Aggressive stretching sets "
                  "recovery back."],
        "tests": ["Clinical examination", "X-ray to exclude other causes",
                  "Blood sugar and HbA1c"],
    },
    "Osteoporosis": {
        "primary": ["bone_pain", "frequent_fractures", "back_pain"],
        "secondary": ["muscle_pain", "restricted_movement", "difficulty_climbing_stairs",
                      "weakness"],
        "specialisation": "Orthopaedics", "urgency": "routine",
        "about": "Bones become thin and fragile, so they break after minor falls. It has "
                 "no symptoms at all until a fracture happens.",
        "precautions": [
            "Get a bone density (DEXA) scan if you are postmenopausal or over 65.",
            "Calcium and vitamin D, with sunlight exposure.",
            "Weight-bearing exercise like walking builds bone.",
            "Make the house fall-safe: lighting, bathroom mats, no loose wires.",
        ],
        "avoid": ["Reduce smoking and alcohol, which both accelerate bone loss."],
        "tests": ["DEXA bone density scan", "Serum calcium and vitamin D",
                  "Thyroid function"],
    },

    # ------------------------------------------------------------- urinary
    "Urinary Tract Infection": {
        "primary": ["burning_urination", "frequent_urination", "urgency_to_urinate",
                    "cloudy_urine"],
        "secondary": ["lower_abdominal_pain", "fever", "blood_in_urine", "lower_back_pain",
                      "nausea", "night_urination"],
        "specialisation": "Urology", "urgency": "prompt",
        "about": "A bacterial infection of the urinary system. Much more common in women "
                 "because of anatomy, not hygiene.",
        "precautions": [
            "Drink plenty of water throughout the day.",
            "Do not hold urine for long periods.",
            "Get a urine test and complete the prescribed course.",
            "See a doctor urgently if fever with back pain develops. That means the "
            "infection has reached the kidney.",
        ],
        "avoid": ["Do not take leftover antibiotics from a previous infection. The wrong "
                  "antibiotic breeds resistance and delays real treatment."],
        "tests": ["Urine routine and microscopy", "Urine culture and sensitivity"],
    },
    "Kidney Stones": {
        "primary": ["flank_pain", "lower_back_pain", "blood_in_urine", "nausea"],
        "secondary": ["vomiting", "burning_urination", "frequent_urination",
                      "abdominal_pain", "cloudy_urine", "fever", "restlessness"],
        "specialisation": "Urology", "urgency": "urgent",
        "about": "Hard deposits formed in the kidney. The pain comes in severe waves in "
                 "the side of the back, and people typically cannot sit still with it.",
        "precautions": [
            "Drink 3 to 4 litres of water daily unless a doctor has told you otherwise.",
            "Get an ultrasound to check the size and position.",
            "Go to hospital if pain is unbearable, there is fever, or you cannot pass "
            "urine at all.",
            "Reduce salt. Follow specific diet advice once the stone type is known.",
        ],
        "avoid": ["Do not cut out calcium from your diet. Low dietary calcium actually "
                  "increases the commonest type of stone."],
        "tests": ["Ultrasound KUB", "Non-contrast CT KUB if needed",
                  "Urine routine", "Kidney function"],
    },
    "Chronic Kidney Disease": {
        "primary": ["general_swelling", "fatigue", "frothy_urine", "reduced_urine"],
        "secondary": ["ankle_swelling", "nausea", "loss_of_appetite", "itching",
                      "breathlessness", "night_urination", "pale_skin", "cramps",
                      "difficulty_sleeping", "weakness"],
        "specialisation": "Nephrology", "urgency": "urgent",
        "about": "Gradual loss of kidney function, most often from long-standing diabetes "
                 "or high blood pressure. It is silent until it is quite advanced.",
        "precautions": [
            "See a nephrologist. Early treatment slows the decline substantially.",
            "Control blood sugar and blood pressure tightly. These are the main causes.",
            "Restrict salt. Ask a dietitian about protein and potassium.",
            "Free dialysis is available for BPL patients under PMNDP at district "
            "hospitals if it ever comes to that.",
        ],
        "avoid": ["Avoid NSAID painkillers entirely. Avoid contrast dye scans unless the "
                  "radiologist knows about your kidneys. Avoid unregulated herbal "
                  "remedies, several of which are directly toxic to kidneys."],
        "tests": ["Serum creatinine and eGFR", "Urine protein / albumin-creatinine ratio",
                  "Ultrasound KUB", "Haemoglobin"],
    },
    "Benign Prostate Enlargement": {
        "primary": ["weak_urine_stream", "prostate_symptoms", "night_urination",
                    "incomplete_emptying"],
        "secondary": ["frequent_urination", "urgency_to_urinate", "dribbling_urine",
                      "burning_urination", "lower_abdominal_pain"],
        "specialisation": "Urology", "urgency": "routine",
        "about": "The prostate enlarges with age and presses on the urine passage. Very "
                 "common in men over 50 and usually not cancer.",
        "precautions": [
            "Reduce fluids in the 2 hours before bed to cut night-time trips.",
            "Reduce caffeine and alcohol, which irritate the bladder.",
            "See a urologist. Effective medicines exist and surgery is not always needed.",
            "Go urgently if you cannot pass urine at all. That needs immediate relief.",
        ],
        "avoid": ["Avoid cold and allergy medicines containing decongestants. They can "
                  "cause complete urinary blockage in men with an enlarged prostate."],
        "tests": ["Ultrasound with post-void residual volume", "PSA blood test",
                  "Urine routine", "Uroflowmetry"],
    },

    # ---------------------------------------------------------------- skin
    "Fungal Skin Infection": {
        "primary": ["ring_shaped_rash", "itching", "rash", "skin_peeling"],
        "secondary": ["red_spots", "dry_skin", "blisters", "night_itching"],
        "specialisation": "Dermatology", "urgency": "routine",
        "about": "A fungal infection of the skin, very common in hot humid weather and in "
                 "skin folds. Classically a ring-shaped itchy patch that spreads outward.",
        "precautions": [
            "Keep the area clean and completely dry. Change clothes after sweating.",
            "Wash and sun-dry clothes and towels separately from the family's.",
            "Complete the full antifungal course, which often runs several weeks past "
            "the point where it looks better.",
            "Treat all affected family members together, or it circulates.",
        ],
        "avoid": ["Do NOT use over-the-counter steroid creams or combination creams. They "
                  "calm the itch for a few days and then make the infection dramatically "
                  "worse and much harder to treat. This is one of the commonest and most "
                  "damaging self-medication mistakes in India."],
        "tests": ["Usually clinical", "KOH mount of skin scraping if uncertain"],
    },
    "Scabies": {
        "primary": ["night_itching", "itching", "skin_burrows_between_fingers", "rash"],
        "secondary": ["red_spots", "blisters", "difficulty_sleeping", "skin_peeling"],
        "specialisation": "Dermatology", "urgency": "prompt",
        "about": "A mite burrowing under the skin. The itching is characteristically far "
                 "worse at night, and it spreads through close contact and shared bedding.",
        "precautions": [
            "Everyone in the household must be treated at the same time, even those "
            "without symptoms. Otherwise it comes straight back.",
            "Wash all bedding and clothes in hot water and sun-dry them.",
            "Apply the prescribed cream from the neck down, everywhere, not just the "
            "itchy spots.",
            "Itching can continue for 2 weeks after successful treatment. That is not "
            "failure.",
        ],
        "avoid": ["Do not use steroid creams, which mask it and let it spread further."],
        "tests": ["Clinical diagnosis", "Skin scraping if uncertain"],
    },
    "Eczema (Dermatitis)": {
        "primary": ["itching", "dry_skin", "rash", "skin_peeling"],
        "secondary": ["red_spots", "blisters", "difficulty_sleeping", "general_swelling",
                      "night_itching"],
        "specialisation": "Dermatology", "urgency": "routine",
        "about": "Long-term inflammation of the skin causing dry, itchy patches that come "
                 "and go. Often runs in families alongside asthma and allergies.",
        "precautions": [
            "Moisturise daily, especially within minutes of bathing.",
            "Lukewarm water and mild soap. Hot water strips the skin.",
            "Avoid scratching. Keep nails short.",
            "See a dermatologist if the skin cracks, weeps or becomes infected.",
        ],
        "avoid": ["Use steroid creams only as prescribed and only for the period advised. "
                  "Long unsupervised use thins the skin permanently."],
        "tests": ["Usually clinical", "Patch testing if a contact allergy is suspected"],
    },
    "Psoriasis": {
        "primary": ["scaly_patches", "itching", "rash", "skin_peeling"],
        "secondary": ["joint_pain", "brittle_nails", "dry_skin", "red_spots",
                      "small_joint_pain"],
        "specialisation": "Dermatology", "urgency": "routine",
        "about": "An immune condition where skin cells build up into thick silvery scaly "
                 "patches, usually on elbows, knees and scalp. It is not contagious.",
        "precautions": [
            "Moisturise heavily and regularly.",
            "Some sunlight exposure helps, but avoid burning.",
            "Tell your doctor about any joint pain. Psoriasis can affect joints too.",
            "Stress and infections commonly trigger flares.",
        ],
        "avoid": ["Do not stop strong topical treatments abruptly. Avoid skin injury and "
                  "scratching, which triggers new patches at the site."],
        "tests": ["Clinical diagnosis", "Skin biopsy occasionally", "Joint assessment"],
    },
    "Urticaria (Hives)": {
        "primary": ["raised_itchy_welts", "itching", "rash"],
        "secondary": ["general_swelling", "swollen_eyelids", "red_spots",
                      "breathlessness", "abdominal_pain"],
        "specialisation": "Dermatology", "urgency": "prompt",
        "about": "Raised itchy welts that appear, move around and fade within hours. "
                 "Usually an allergic or post-viral reaction.",
        "precautions": [
            "Note what you ate, took or touched in the few hours before it started.",
            "Cool compresses help the itch.",
            "Call 108 immediately if there is swelling of the lips, tongue or throat, or "
            "any difficulty breathing. That is anaphylaxis.",
        ],
        "avoid": ["Avoid aspirin and NSAIDs during a flare, which commonly worsen hives."],
        "tests": ["Usually none for a single episode",
                  "Allergy testing if it keeps recurring"],
    },
    "Acne": {
        "primary": ["pimples", "oily_skin"],
        "secondary": ["red_spots", "itching", "skin_peeling", "excess_facial_hair"],
        "specialisation": "Dermatology", "urgency": "routine",
        "about": "Blocked oil glands causing pimples on the face, chest and back. Very "
                 "common in the teenage years and usually settles with time.",
        "precautions": [
            "Wash gently twice daily. Scrubbing harder makes it worse.",
            "Do not squeeze. That is what causes the scars.",
            "Use non-comedogenic products.",
            "See a dermatologist for severe or scarring acne. Effective treatment exists "
            "and early treatment prevents permanent scarring.",
        ],
        "avoid": ["Avoid unregulated skin-lightening creams. Many contain steroids or "
                  "mercury and cause lasting damage."],
        "tests": ["Usually none", "Hormone tests if acne comes with irregular periods "
                  "and excess hair"],
    },

    # ------------------------------------------------------------ eye & ENT
    "Conjunctivitis": {
        "primary": ["red_eyes", "eye_discharge", "itchy_eyes", "watery_eyes"],
        "secondary": ["swollen_eyelids", "sensitivity_to_light", "blurred_vision",
                      "eye_pain"],
        "specialisation": "Ophthalmology", "urgency": "prompt",
        "about": "Infection or irritation of the outer surface of the eye. Commonly "
                 "called eye flu, and it spreads through touch very easily.",
        "precautions": [
            "Do not share towels, pillows or eye drops with anyone.",
            "Wash hands often and avoid touching your eyes.",
            "See an eye doctor if vision blurs or pain increases.",
        ],
        "avoid": ["Do NOT use steroid eye drops without an eye doctor. If the cause is a "
                  "herpes infection, steroids can damage the cornea and cost you vision. "
                  "Also avoid home remedies like breast milk or kajal in the eye."],
        "tests": ["Usually clinical", "Eye swab if severe or not settling"],
    },
    "Cataract": {
        "primary": ["cloudy_vision", "blurred_vision", "night_vision_trouble"],
        "secondary": ["halos_around_lights", "sensitivity_to_light", "double_vision",
                      "headache"],
        "specialisation": "Ophthalmology", "urgency": "routine",
        "about": "The lens of the eye gradually clouds, so vision becomes hazy, colours "
                 "fade and lights develop halos. It is the leading cause of avoidable "
                 "blindness in India, and surgery cures it.",
        "precautions": [
            "Get an eye check. Cataract surgery is highly effective and quick.",
            "Free or subsidised cataract surgery is available through the National "
            "Programme for Control of Blindness.",
            "Wear sunglasses outdoors to slow progression.",
            "Do not drive at night if lights dazzle you.",
        ],
        "avoid": ["No eye drop dissolves a cataract, whatever a shop tells you. Surgery "
                  "is the only treatment."],
        "tests": ["Eye examination with slit lamp", "Vision testing"],
    },
    "Otitis Media (Ear Infection)": {
        "primary": ["ear_pain", "hearing_loss", "fever"],
        "secondary": ["ear_discharge", "irritability", "difficulty_sleeping",
                      "ringing_in_ears", "blocked_nose", "sore_throat"],
        "specialisation": "ENT", "urgency": "prompt",
        "about": "Infection of the middle ear, very common in children, often following "
                 "a cold. Discharge means the eardrum has perforated.",
        "precautions": [
            "See a doctor, especially for a child under 2 or with discharge.",
            "Keep the ear dry if there is discharge.",
            "Complete any antibiotic course prescribed.",
            "Get hearing checked afterwards if it keeps recurring. Repeated infections "
            "affect speech development in young children.",
        ],
        "avoid": ["Do NOT pour oil, breast milk or any home remedy into the ear. Do not "
                  "insert cotton buds."],
        "tests": ["Ear examination with otoscope", "Hearing test if recurrent"],
    },
    "Tonsillitis": {
        "primary": ["severe_sore_throat", "white_patches_throat", "fever",
                    "swollen_glands"],
        "secondary": ["ear_pain", "headache", "loss_of_appetite", "hoarse_voice",
                      "body_ache", "mouth_ulcers"],
        "specialisation": "ENT", "urgency": "prompt",
        "about": "Infection of the tonsils. White patches with fever and tender neck "
                 "glands suggest a bacterial cause needing antibiotics.",
        "precautions": [
            "Warm salt water gargles and plenty of fluids.",
            "See a doctor. Untreated streptococcal tonsillitis can damage the heart "
            "valves, which still happens in India.",
            "Complete the full antibiotic course if one is prescribed.",
        ],
        "avoid": ["Do not stop antibiotics early. This is the specific infection where "
                  "stopping early risks rheumatic heart disease years later."],
        "tests": ["Throat examination", "Rapid strep test or throat swab", "CBC"],
    },

    # -------------------------------------------------------- women's health
    "PCOS": {
        "primary": ["irregular_periods", "excess_facial_hair", "weight_gain", "pimples"],
        "secondary": ["difficulty_conceiving", "hair_loss", "dark_neck_patches",
                      "missed_periods", "oily_skin", "mood_swings", "fatigue"],
        "specialisation": "Gynaecology", "urgency": "routine",
        "about": "A hormonal condition causing irregular periods, excess hair growth and "
                 "difficulty conceiving. It also raises the long-term risk of diabetes, "
                 "which is the part most people are never told.",
        "precautions": [
            "See a gynaecologist. This is very manageable.",
            "Weight loss of even 5 to 10 percent often restores regular cycles.",
            "Get screened for diabetes. The risk is substantially higher with PCOS.",
            "Regular exercise improves the hormonal picture directly.",
        ],
        "avoid": ["Be cautious with unregulated 'hormone balancing' supplements sold "
                  "online. Several contain undeclared hormones."],
        "tests": ["Pelvic ultrasound", "Blood sugar and HbA1c", "Thyroid function",
                  "Testosterone, LH and FSH"],
    },
    "Painful Periods (Dysmenorrhoea)": {
        "primary": ["painful_periods", "lower_abdominal_pain", "cramping_pain"],
        "secondary": ["nausea", "headache", "back_pain", "fatigue", "diarrhoea",
                      "heavy_periods", "irritability"],
        "specialisation": "Gynaecology", "urgency": "routine",
        "about": "Cramping pain during periods. Common, but pain severe enough to stop "
                 "you attending school or work is not something to simply endure.",
        "precautions": [
            "Heat on the lower abdomen genuinely helps.",
            "Regular exercise reduces period pain over time.",
            "See a gynaecologist if pain is severe, worsening, or new. It could be "
            "endometriosis or fibroids.",
        ],
        "avoid": ["Do not accept 'this is normal for women' as an answer if the pain is "
                  "disabling. It is worth investigating."],
        "tests": ["Usually none", "Pelvic ultrasound if pain is severe or worsening"],
    },

    # -------------------------------------------------------- mental health
    "Anxiety Disorder": {
        "primary": ["anxiety", "excessive_worry", "restlessness", "difficulty_sleeping"],
        "secondary": ["palpitations", "poor_concentration", "irritability", "fatigue",
                      "muscle_pain", "panic_episodes", "breathlessness", "nausea",
                      "tremor", "dizziness"],
        "specialisation": "Psychiatry", "urgency": "prompt", "sensitive": True,
        "about": "Persistent worry and physical tension that is hard to control and gets "
                 "in the way of daily life. It is common, it is a real medical condition, "
                 "and it responds well to treatment.",
        "precautions": [
            "Talking to a professional helps. Tele-MANAS is free on 14416, in Marathi "
            "and other Indian languages, 24 hours a day.",
            "Regular sleep, regular meals and regular movement all measurably reduce "
            "anxiety symptoms.",
            "Reduce caffeine, which mimics and worsens anxiety symptoms.",
            "Talk to someone you trust. Isolation makes this heavier.",
        ],
        "avoid": ["Alcohol seems to calm anxiety and reliably makes it worse over time. "
                  "Do not take sedative tablets bought without prescription."],
        "tests": ["Thyroid function, since an overactive thyroid mimics anxiety closely",
                  "Assessment by a mental health professional"],
    },
    "Depression": {
        "primary": ["low_mood", "loss_of_interest", "fatigue", "difficulty_sleeping"],
        "secondary": ["poor_concentration", "loss_of_appetite", "weight_loss",
                      "hopelessness", "excessive_sleep", "irritability", "weakness",
                      "body_ache", "headache"],
        "specialisation": "Psychiatry", "urgency": "prompt", "sensitive": True,
        "about": "Persistent low mood and loss of interest in things you used to enjoy, "
                 "lasting more than two weeks. It is a medical condition, not a weakness "
                 "of character, and it is treatable.",
        "precautions": [
            "Please talk to someone. Tele-MANAS is free on 14416, available 24 hours a "
            "day in Marathi and other Indian languages.",
            "A doctor or counsellor can help. Treatment works for most people.",
            "Tell someone you trust how you are feeling. Carrying it alone makes it "
            "heavier.",
            "Keep a routine where you can: sleep, meals, some daylight, some movement. "
            "Small and regular beats ambitious and abandoned.",
        ],
        "avoid": ["Alcohol makes depression worse, not better. Do not stop prescribed "
                  "medication without talking to your doctor first."],
        "tests": ["Thyroid function and haemoglobin, since both can mimic depression",
                  "Vitamin B12 and D", "Assessment by a mental health professional"],
    },
}


def as_seed_rows():
    """Rows for the DiseaseInfo table."""
    rows = []
    for name, p in DISEASES.items():
        rows.append({
            "name": name,
            "about": p["about"],
            "precautions": "\n".join(p["precautions"]),
            "avoid": "\n".join(p.get("avoid", [])),
            "tests": "\n".join(p.get("tests", [])),
            "specialisation": p["specialisation"],
            "urgency": p["urgency"],
            "sensitive": p.get("sensitive", False),
        })
    return rows


DISEASE_NAMES = sorted(DISEASES)
SPECIALISATIONS = sorted({d["specialisation"] for d in DISEASES.values()})
SENSITIVE_CONDITIONS = {n for n, d in DISEASES.items() if d.get("sensitive")}


# ---------------------------------------------------------------------------
# LAB ASSOCIATIONS
# ---------------------------------------------------------------------------
# Probability that a given lab flag is present when a condition is the true
# cause. Used to generate the lab columns of the training data, so the model
# learns to use lab evidence rather than having it bolted on afterwards.
# ---------------------------------------------------------------------------

LAB_ASSOCIATIONS = {
    "Dengue":                    {"low_platelets": 0.80, "low_wbc": 0.55},
    "Malaria":                   {"low_platelets": 0.55, "anaemic_range": 0.45},
    "Typhoid":                   {"low_wbc": 0.45, "high_wbc": 0.15},
    "Chikungunya":               {"low_platelets": 0.25, "low_wbc": 0.30},
    "Leptospirosis":             {"high_wbc": 0.50, "high_bilirubin": 0.45,
                                  "high_creatinine": 0.40, "low_platelets": 0.35},
    "Pneumonia":                 {"high_wbc": 0.70},
    "Tonsillitis":               {"high_wbc": 0.55},
    "Urinary Tract Infection":   {"high_wbc": 0.50},
    "Appendicitis":              {"high_wbc": 0.70},
    "Amoebic Dysentery":         {"high_wbc": 0.30},
    "Anaemia":                   {"anaemic_range": 0.92},
    "Worm Infestation":          {"anaemic_range": 0.45},
    "Type 2 Diabetes":           {"high_blood_sugar": 0.85, "high_hba1c": 0.80},
    "Hypothyroidism":            {"high_tsh": 0.88},
    "Hyperthyroidism":           {"low_tsh": 0.88},
    "Hepatitis A (Jaundice)":    {"high_bilirubin": 0.90},
    "Gallstones":                {"high_bilirubin": 0.30},
    "Chronic Kidney Disease":    {"high_creatinine": 0.90, "anaemic_range": 0.60},
    "Kidney Stones":             {"high_creatinine": 0.20},
    "Heart Failure":             {"high_creatinine": 0.30},
    "Tuberculosis (TB)":         {"anaemic_range": 0.40, "low_wbc": 0.20},
    "Rheumatoid Arthritis":      {"anaemic_range": 0.35},
    "Vitamin B12 Deficiency":    {"anaemic_range": 0.55},
    "PCOS":                      {"high_blood_sugar": 0.30, "high_hba1c": 0.25},
    "Depression":                {"high_tsh": 0.10},
    "Anxiety Disorder":          {"low_tsh": 0.10},
}


# ---------------------------------------------------------------------------
# CONTEXT PRIORS
# ---------------------------------------------------------------------------
# How often each context feature is true when a condition is the true cause.
# Anything not listed falls back to a flat prior in the generator.
# ---------------------------------------------------------------------------

CONTEXT_PRIORS = {
    "Common Cold":               {"ctx_duration_acute": 0.75, "ctx_improving": 0.45},
    "Influenza (Flu)":           {"ctx_duration_acute": 0.70},
    "COVID-19":                  {"ctx_duration_acute": 0.60},
    "Dengue":                    {"ctx_duration_acute": 0.70, "ctx_worse_fast": 0.45},
    "Malaria":                   {"ctx_duration_acute": 0.55, "ctx_duration_subacute": 0.35},
    "Typhoid":                   {"ctx_duration_subacute": 0.65, "ctx_worse_slow": 0.45},
    "Food Poisoning":            {"ctx_duration_acute": 0.90},
    "Gastroenteritis":           {"ctx_duration_acute": 0.75},
    "Appendicitis":              {"ctx_duration_acute": 0.85, "ctx_worse_fast": 0.70},
    "Viral Fever":               {"ctx_duration_acute": 0.75},
    "Tuberculosis (TB)":         {"ctx_duration_chronic": 0.55, "ctx_duration_very_chronic": 0.35,
                                  "ctx_worse_slow": 0.55, "ctx_hx_tb": 0.20},
    "COPD":                      {"ctx_duration_very_chronic": 0.70, "ctx_age_middle": 0.40,
                                  "ctx_age_senior": 0.40, "ctx_hx_asthma": 0.45},
    "Bronchial Asthma":          {"ctx_hx_asthma": 0.55},
    "Chronic Kidney Disease":    {"ctx_duration_very_chronic": 0.65, "ctx_hx_kidney": 0.50,
                                  "ctx_hx_diabetes": 0.45, "ctx_hx_hypertension": 0.45},
    "Type 2 Diabetes":           {"ctx_duration_chronic": 0.40, "ctx_duration_very_chronic": 0.40,
                                  "ctx_hx_diabetes": 0.35, "ctx_age_middle": 0.40},
    "Hypertension (High BP)":    {"ctx_hx_hypertension": 0.45, "ctx_age_middle": 0.40},
    "Angina (Heart Artery Disease)": {"ctx_hx_heart": 0.45, "ctx_age_middle": 0.35,
                                      "ctx_age_senior": 0.40, "ctx_hx_diabetes": 0.30},
    "Heart Failure":             {"ctx_hx_heart": 0.55, "ctx_age_senior": 0.50,
                                  "ctx_duration_chronic": 0.50},
    "Osteoarthritis":            {"ctx_duration_very_chronic": 0.70, "ctx_age_senior": 0.45,
                                  "ctx_age_middle": 0.35},
    "Osteoporosis":              {"ctx_age_senior": 0.65, "ctx_duration_very_chronic": 0.55},
    "Cataract":                  {"ctx_age_senior": 0.65, "ctx_duration_very_chronic": 0.60},
    "Benign Prostate Enlargement": {"ctx_age_senior": 0.55, "ctx_age_middle": 0.35,
                                    "ctx_duration_chronic": 0.55},
    "Chickenpox":                {"ctx_age_child": 0.55, "ctx_duration_acute": 0.70},
    "Measles":                   {"ctx_age_child": 0.70, "ctx_duration_acute": 0.65},
    "Mumps":                     {"ctx_age_child": 0.55, "ctx_duration_acute": 0.60},
    "Worm Infestation":          {"ctx_age_child": 0.50, "ctx_duration_chronic": 0.45},
    "Acne":                      {"ctx_age_teen": 0.60, "ctx_duration_chronic": 0.55},
    "PCOS":                      {"ctx_duration_very_chronic": 0.60, "ctx_age_adult": 0.60},
    "Hypothyroidism":            {"ctx_duration_chronic": 0.55, "ctx_hx_thyroid": 0.35},
    "Hyperthyroidism":           {"ctx_duration_chronic": 0.50, "ctx_hx_thyroid": 0.35},
    "Depression":                {"ctx_duration_chronic": 0.60, "ctx_duration_very_chronic": 0.30},
    "Anxiety Disorder":          {"ctx_duration_chronic": 0.55},
    "Irritable Bowel Syndrome":  {"ctx_duration_very_chronic": 0.70},
    "Psoriasis":                 {"ctx_duration_very_chronic": 0.65},
    "Eczema (Dermatitis)":       {"ctx_duration_chronic": 0.55},
    "Rheumatoid Arthritis":      {"ctx_duration_chronic": 0.50, "ctx_duration_very_chronic": 0.35},
    "Cervical Spondylosis":      {"ctx_duration_chronic": 0.60, "ctx_age_middle": 0.40},
    "Migraine":                  {"ctx_duration_chronic": 0.45},
    "Scabies":                   {"ctx_duration_subacute": 0.55},
    "Epilepsy":                  {"ctx_duration_acute": 0.40},
}
