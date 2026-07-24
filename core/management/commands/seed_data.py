"""
Seeds the database with schemes, hospitals, bed records, disease info and tips.

    python manage.py seed_data           # add anything missing
    python manage.py seed_data --reset   # wipe and rebuild

SCHEME DATA was checked against government and scheme-aggregator sources in
July 2026. Verify again before your submission — amounts change.

HOSPITAL DATA uses real hospital names in Nashik and Pune so the demo feels
real, but every bed number is invented. The UI says so on every page.
"""

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from core.models import HealthTip
from hospitals.models import BedAvailability, Hospital, Specialisation
from hospitals.pune_district import EXTRA_SPECIALISATIONS
from hospitals.pune_district import as_seed_rows as pune_hospital_rows
from ml_model.disease_data import DISEASES, SPECIALISATIONS, as_seed_rows
from prediction.models import DiseaseInfo
from schemes.models import Scheme

VERIFIED = date(2026, 7, 23)

# ---------------------------------------------------------------------------
# SCHEMES
# ---------------------------------------------------------------------------
SCHEMES = [
    {
        "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
        "short_name": "AB PM-JAY",
        "level": "central", "category": "insurance", "eligible_cards": "yellow",
        "display_order": 1,
        "headline_benefit": "Rs 5 lakh of cashless hospital treatment per family, every year",
        "description": (
            "The largest government-funded health assurance scheme in the world. Eligible families get "
            "cashless treatment for secondary and tertiary care at empanelled government and private "
            "hospitals anywhere in India.\n\n"
            "There is no premium to pay, no cap on family size, no age limit within the family, and no "
            "waiting period — pre-existing conditions are covered from day one. It covers roughly 1,900 "
            "procedures including surgery, cancer treatment, dialysis and neonatal care, plus 3 days of "
            "pre-hospitalisation and 15 days of post-hospitalisation costs."
        ),
        "eligibility": (
            "Your family appears in the SECC 2011 deprivation database (this is already decided in "
            "government records — you do not apply to be included)\n"
            "Rural families in categories such as: only one room with kutcha walls and roof; no adult "
            "member aged 16 to 59; no adult male member aged 16 to 59; landless households earning "
            "mainly from manual casual labour\n"
            "Urban families in any of the 11 listed occupational categories, such as rag picker, "
            "domestic worker, street vendor, construction worker, sweeper, home-based worker\n"
            "Anyone aged 70 or above is eligible regardless of income, under the Ayushman Vay Vandana "
            "card, with a separate Rs 5 lakh cover not shared with the family"
        ),
        "documents": (
            "Aadhaar card\nRation card\nMobile number linked to Aadhaar\n"
            "Any government photo ID\nProof of age for the 70+ category"
        ),
        "application_steps": (
            "Check eligibility on pmjay.gov.in using your mobile number, or call the helpline 14555.\n"
            "If you are not sure, visit any empanelled hospital and ask for the Arogya Mitra desk — "
            "they check eligibility for free.\n"
            "Complete Aadhaar-based e-KYC, either on the Ayushman App or at the hospital desk. Face "
            "authentication is available if fingerprints do not work.\n"
            "Once verified, download your Ayushman Card from the app or portal, or collect the printed "
            "card from the Common Service Centre.\n"
            "Carry the card to any empanelled hospital. Treatment is cashless — you should not be asked "
            "to pay a deposit."
        ),
        "where_to_apply": "Any empanelled hospital, Common Service Centre, or the Ayushman App",
        "official_link": "https://pmjay.gov.in",
        "helpline": "14555",
    },
    {
        "name": "Mahatma Jyotirao Phule Jan Arogya Yojana",
        "short_name": "MJPJAY",
        "level": "state", "category": "insurance", "eligible_cards": "orange",
        "display_order": 2,
        "headline_benefit": "Rs 5 lakh cashless cover per family per year, for every family in Maharashtra",
        "description": (
            "Maharashtra's own health assurance scheme, run by the State Health Assurance Society. It "
            "began in 2012 as the Rajiv Gandhi Jeevandayee Arogya Yojana and was renamed in 2017.\n\n"
            "Since 1 July 2024 MJPJAY and Ayushman Bharat operate as one unified cover in Maharashtra, "
            "raising the limit to Rs 5 lakh per family per year and extending it to all families in the "
            "state rather than only low-income households. Treatment is cashless at empanelled "
            "government and private hospitals."
        ),
        "eligibility": (
            "Families holding a Yellow, Orange, Antyodaya Anna Yojana, or Annapurna ration card\n"
            "White ration card holders are also covered under the unified scheme since July 2024\n"
            "Farmers from the state's agriculturally distressed districts, with a white ration card and "
            "a 7/12 extract\n"
            "Construction workers registered with the Maharashtra Building and Other Construction "
            "Workers Welfare Board\n"
            "Road traffic accident victims injured on roads in Maharashtra, including visitors\n"
            "Journalists and their dependants, as recognised by the DGIPR"
        ),
        "documents": (
            "Ration card (yellow, orange, white, Antyodaya or Annapurna)\nAadhaar card\n"
            "Any government photo ID with the same name\n"
            "7/12 extract, for farmers applying under the distressed-district category\n"
            "Registration card, for construction workers"
        ),
        "application_steps": (
            "Go to any empanelled government or private hospital and find the Arogya Mitra help desk near "
            "the entrance.\n"
            "Show your ration card and photo ID. The Arogya Mitra checks your name against the scheme "
            "database at no cost.\n"
            "If eligible, the Arogya Mitra registers you and raises the pre-authorisation request to the "
            "State Health Assurance Society.\n"
            "Wait for approval, which is usually same-day for planned procedures and immediate for "
            "emergencies.\n"
            "Get treated cashless. You should not pay for covered procedures, medicines, or diagnostics "
            "during the admission."
        ),
        "where_to_apply": "Arogya Mitra desk at any empanelled hospital",
        "official_link": "https://www.jeevandayee.gov.in",
        "helpline": "155388",
    },
    {
        "name": "Ayushman Vay Vandana Card for Senior Citizens",
        "short_name": "Vay Vandana",
        "level": "central", "category": "senior", "eligible_cards": "senior70",
        "display_order": 3,
        "headline_benefit": "Rs 5 lakh cover for anyone aged 70 or above, whatever their income",
        "description": (
            "An expansion of PM-JAY introduced in late 2024. Every citizen aged 70 and above is covered, "
            "regardless of income or ration card colour.\n\n"
            "If the family is already a PM-JAY beneficiary, the senior gets an additional Rs 5 lakh that "
            "is theirs alone and is not shared with the rest of the family pool. If the family is not a "
            "beneficiary, the senior still gets Rs 5 lakh of their own."
        ),
        "eligibility": (
            "Aged 70 years or above on the date of application\n"
            "Indian citizen with a valid Aadhaar card\n"
            "Income is not considered — this applies regardless of financial status\n"
            "Existing CGHS or ECHS members may choose this instead, but cannot claim both at once"
        ),
        "documents": (
            "Aadhaar card showing date of birth\nMobile number linked to Aadhaar\nRation card, if available"
        ),
        "application_steps": (
            "Open the Ayushman App or go to beneficiary.nha.gov.in and select the senior citizen category.\n"
            "Enter the Aadhaar number and complete e-KYC using OTP or face authentication.\n"
            "Confirm the date of birth shown on Aadhaar is 70 years or more — if it is wrong, correct "
            "Aadhaar first at an enrolment centre.\n"
            "Download the Ayushman Vay Vandana Card once approved.\n"
            "Alternatively, take the Aadhaar card to any empanelled hospital and ask the Arogya Mitra to "
            "complete this for you."
        ),
        "where_to_apply": "Ayushman App, beneficiary portal, or an empanelled hospital",
        "official_link": "https://beneficiary.nha.gov.in",
        "helpline": "14555",
    },
    {
        "name": "Janani Suraksha Yojana",
        "short_name": "JSY",
        "level": "central", "category": "maternal", "eligible_cards": "yellow",
        "display_order": 4,
        "headline_benefit": "Cash assistance for giving birth in a hospital instead of at home",
        "description": (
            "A safe motherhood scheme under the National Health Mission that pays cash to encourage "
            "delivery in a health facility rather than at home, where complications cannot be handled.\n\n"
            "The money is paid directly into the mother's bank account after delivery. An ASHA worker "
            "accompanies the mother and also receives an incentive for the support she provides."
        ),
        "eligibility": (
            "Pregnant women from BPL households, Scheduled Caste and Scheduled Tribe families\n"
            "The delivery must take place in a government facility or an accredited private facility\n"
            "The pregnancy must be registered at an Anganwadi or health sub-centre\n"
            "Amounts differ between rural and urban areas, and between high and low performing states"
        ),
        "documents": (
            "Mother and Child Protection card (MCP card)\nAadhaar card\n"
            "Bank passbook in the mother's name\nBPL or caste certificate where applicable\n"
            "Delivery certificate from the facility"
        ),
        "application_steps": (
            "Register the pregnancy at your nearest Anganwadi centre or Primary Health Centre as early "
            "as possible — ideally in the first three months.\n"
            "Collect the Mother and Child Protection card and attend the free antenatal check-ups.\n"
            "Give the ASHA worker your Aadhaar and bank account details so the transfer can be set up.\n"
            "Deliver at a government hospital or an accredited private facility.\n"
            "The cash is transferred to your bank account after the delivery is recorded. Follow up with "
            "the ASHA worker if it does not arrive."
        ),
        "where_to_apply": "Anganwadi centre, Primary Health Centre, or through your ASHA worker",
        "official_link": "https://nhm.gov.in",
        "helpline": "104",
    },
    {
        "name": "Janani Shishu Suraksha Karyakram",
        "short_name": "JSSK",
        "level": "central", "category": "maternal", "eligible_cards": "any",
        "display_order": 5,
        "headline_benefit": "Delivery, caesarean, medicines and transport free at government hospitals",
        "description": (
            "Removes the out-of-pocket cost of childbirth completely at public health facilities. Every "
            "pregnant woman is entitled, regardless of income or card.\n\n"
            "It covers normal delivery and caesarean section, all drugs and consumables, diagnostics, "
            "diet during the stay, blood if needed, and free transport from home to the facility, "
            "between facilities, and back home again. Sick newborns up to one year are covered on the "
            "same terms."
        ),
        "eligibility": (
            "Every pregnant woman delivering at a public health facility — no income test\n"
            "Every sick infant up to one year of age, at public health facilities\n"
            "Applies to both rural and urban areas across India"
        ),
        "documents": (
            "Mother and Child Protection card\nAadhaar card, if available\n"
            "No income proof or ration card is required"
        ),
        "application_steps": (
            "Go to any government hospital, Community Health Centre or Primary Health Centre for delivery.\n"
            "Tell the staff you are claiming under JSSK. There is no separate form to fill in advance.\n"
            "Call 102 for free transport to the facility when labour begins.\n"
            "Delivery, medicines, tests, blood and food during the stay are free — do not pay for them.\n"
            "Free transport home is also part of the entitlement. Ask for it before you are discharged.\n"
            "If any staff member asks you to buy medicines or pay a charge, report it on the helpline 104."
        ),
        "where_to_apply": "Directly at any government health facility",
        "official_link": "https://nhm.gov.in",
        "helpline": "104",
    },
    {
        "name": "Pradhan Mantri Surakshit Matritva Abhiyan",
        "short_name": "PMSMA",
        "level": "central", "category": "maternal", "eligible_cards": "any",
        "display_order": 6,
        "headline_benefit": "Free specialist antenatal check-up on the 9th of every month",
        "description": (
            "On the 9th of every month, government health facilities run a dedicated antenatal clinic "
            "where a gynaecologist or trained doctor examines pregnant women in their second and third "
            "trimester, free of charge.\n\n"
            "The aim is to catch high-risk pregnancies early — anaemia, high blood pressure, gestational "
            "diabetes, poor foetal growth — while there is still time to act. Women identified as high "
            "risk are marked with a red sticker on their MCP card and followed up closely."
        ),
        "eligibility": (
            "All pregnant women in their 2nd and 3rd trimester\n"
            "No income test, no card requirement\n"
            "Available at government facilities and at private clinics of doctors who have volunteered"
        ),
        "documents": ("Mother and Child Protection card\nAny previous test reports and scans"),
        "application_steps": (
            "Note the date: the clinic runs on the 9th of every month. If the 9th is a holiday, it runs "
            "the next working day.\n"
            "Go to your nearest Primary Health Centre, Community Health Centre or district hospital that "
            "day. No appointment is needed.\n"
            "Carry your MCP card and any earlier reports.\n"
            "You get a full check-up, blood and urine tests, an ultrasound where available, and iron and "
            "calcium tablets — all free.\n"
            "If you receive a red sticker, attend every follow-up. It means something needs watching."
        ),
        "where_to_apply": "Any government health facility on the 9th of the month",
        "official_link": "https://pmsma.mohfw.gov.in",
        "helpline": "104",
    },
    {
        "name": "Ni-kshay Poshan Yojana",
        "short_name": "NPY",
        "level": "central", "category": "disease", "eligible_cards": "any",
        "display_order": 7,
        "headline_benefit": "Rs 1,000 a month for nutrition, for as long as TB treatment lasts",
        "description": (
            "TB treatment is already completely free in India. This scheme adds direct cash for food, "
            "because recovery depends heavily on nutrition and many patients cannot afford to eat well "
            "while unable to work.\n\n"
            "The monthly amount was doubled from Rs 500 to Rs 1,000 in late 2024. Underweight patients "
            "with a BMI below 18.5 also receive energy-dense nutritional supplements for the first two "
            "months. Under the Ni-kshay Mitra initiative, household contacts of patients can receive "
            "food baskets too."
        ),
        "eligibility": (
            "Any TB patient notified on the Ni-kshay portal on or after 1 April 2018\n"
            "Applies to patients treated in both government and private facilities\n"
            "No income test — every notified patient qualifies\n"
            "Payment continues for the full duration of treatment"
        ),
        "documents": (
            "Aadhaar card\nBank account details, with the account in the patient's name\n"
            "TB diagnosis and notification details from the treating facility"
        ),
        "application_steps": (
            "Get tested at any government DOTS centre if you have had a cough for more than two weeks, "
            "or fever with weight loss and night sweats. The sputum test is free.\n"
            "Once TB is confirmed, your treating doctor notifies you on the Ni-kshay portal. This applies "
            "to private doctors too — notification is legally required.\n"
            "Give the health worker your Aadhaar and bank account details so the transfer can be linked.\n"
            "The money arrives by Direct Benefit Transfer each month of treatment.\n"
            "Never stop treatment early. Stopping causes drug-resistant TB, which is far harder to cure."
        ),
        "where_to_apply": "Any government DOTS centre or TB unit",
        "official_link": "https://www.nikshay.in",
        "helpline": "1800-11-6666",
    },
    {
        "name": "Pradhan Mantri National Dialysis Programme",
        "short_name": "PMNDP",
        "level": "central", "category": "disease", "eligible_cards": "yellow",
        "display_order": 8,
        "headline_benefit": "Free dialysis at district hospitals for people below the poverty line",
        "description": (
            "Kidney failure needs dialysis two or three times a week, indefinitely. In the private sector "
            "that cost destroys a family's savings within months.\n\n"
            "This programme, run under the National Health Mission, provides free haemodialysis at "
            "district hospitals across the country for BPL patients, including the dialyser, tubing and "
            "consumables. Many centres also offer peritoneal dialysis."
        ),
        "eligibility": (
            "Diagnosed end-stage renal disease requiring maintenance dialysis\n"
            "Below Poverty Line status, usually shown by a yellow or Antyodaya ration card\n"
            "Referral from a government hospital nephrologist or physician\n"
            "Non-BPL patients are treated at subsidised rates at many centres"
        ),
        "documents": (
            "BPL or Antyodaya ration card\nAadhaar card\n"
            "Nephrologist's prescription and diagnosis report\nRecent kidney function test reports"
        ),
        "application_steps": (
            "Get a diagnosis and dialysis prescription from a government hospital physician or "
            "nephrologist.\n"
            "Ask at the district hospital for the PMNDP dialysis unit — most district hospitals in "
            "Maharashtra have one.\n"
            "Submit the ration card, Aadhaar and medical reports at the unit to register.\n"
            "Once registered, you are given a fixed dialysis schedule. Attend every session.\n"
            "If your district unit has no free slot, ask to be referred to the nearest centre that does."
        ),
        "where_to_apply": "Dialysis unit at your district hospital",
        "official_link": "https://nhm.gov.in",
        "helpline": "104",
    },
    {
        "name": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
        "short_name": "PMBJP",
        "level": "central", "category": "medicine", "eligible_cards": "any",
        "display_order": 9,
        "headline_benefit": "Quality generic medicines at 50 to 90 percent below branded prices",
        "description": (
            "Janaushadhi Kendras are government-supported shops selling generic medicines that are "
            "chemically identical to branded ones but cost a fraction of the price.\n\n"
            "They stock over 2,000 medicines and around 300 surgical items, covering cardiovascular "
            "drugs, diabetes medicines, antibiotics, painkillers and cancer drugs. All products are "
            "tested at NABL-accredited laboratories. Anyone can buy — there is no card or eligibility "
            "check at all."
        ),
        "eligibility": (
            "Open to every citizen without exception\n"
            "No card, income proof or registration required\n"
            "You only need a valid doctor's prescription, exactly as at any pharmacy"
        ),
        "documents": ("A doctor's prescription\nNothing else is required"),
        "application_steps": (
            "Find your nearest Janaushadhi Kendra using the Janaushadhi Sugam app or janaushadhi.gov.in.\n"
            "Take your doctor's prescription to the counter.\n"
            "Ask the pharmacist for the generic equivalent of each medicine prescribed. They will show "
            "you the price difference.\n"
            "If a medicine is out of stock, ask when it will arrive rather than buying the branded "
            "version elsewhere by default.\n"
            "For long-term medicines such as BP or diabetes tablets, this is where the savings add up "
            "most over a year."
        ),
        "where_to_apply": "Any Pradhan Mantri Bhartiya Janaushadhi Kendra",
        "official_link": "https://janaushadhi.gov.in",
        "helpline": "1800-180-8080",
    },
    {
        "name": "Rashtriya Bal Swasthya Karyakram",
        "short_name": "RBSK",
        "level": "central", "category": "child", "eligible_cards": "any",
        "display_order": 10,
        "headline_benefit": "Free health screening and treatment for children up to 18",
        "description": (
            "Mobile health teams screen children at Anganwadi centres and government schools for four "
            "categories of problem: birth defects, deficiencies, childhood diseases, and developmental "
            "delays including disability.\n\n"
            "Children found to need care are referred upward and treated free, including surgery for "
            "conditions such as congenital heart disease, cleft lip and palate, clubfoot and cataract at "
            "tertiary centres."
        ),
        "eligibility": (
            "All children from birth to 6 years registered at Anganwadi centres\n"
            "All children aged 6 to 18 enrolled in government and government-aided schools\n"
            "No income test or card requirement\n"
            "Newborns are screened at the delivery facility itself"
        ),
        "documents": (
            "Birth certificate or Aadhaar, if available\nSchool identity card, for school-age children\n"
            "Mother and Child Protection card, for young children"
        ),
        "application_steps": (
            "Screening happens automatically — the mobile health team visits Anganwadi centres and "
            "government schools on a schedule.\n"
            "If your child does not attend either, take them to the nearest Primary Health Centre and ask "
            "for an RBSK screening.\n"
            "If a condition is found, the team gives you a referral card to a District Early Intervention "
            "Centre or a higher hospital.\n"
            "Attend the referral. Treatment, including surgery, is free under the programme.\n"
            "Keep the referral card safe — it is what identifies the child as an RBSK case at the "
            "referral hospital."
        ),
        "where_to_apply": "Anganwadi centre, government school, or Primary Health Centre",
        "official_link": "https://rbsk.mohfw.gov.in",
        "helpline": "104",
    },
    {
        "name": "Ayushman Bharat Digital Mission",
        "short_name": "ABDM / ABHA",
        "level": "central", "category": "digital", "eligible_cards": "any",
        "display_order": 11,
        "headline_benefit": "A free digital health ID that keeps all your records in one place",
        "description": (
            "The ABHA number is a 14-digit health ID that links your prescriptions, lab reports, "
            "discharge summaries and scans across hospitals, so you do not have to carry a plastic bag "
            "of old files to every appointment.\n\n"
            "It is voluntary and free, and you control who sees your records — consent is required for "
            "each access. Note that ABHA is not the same thing as an Ayushman Card: ABHA is a records "
            "ID for everyone, while the Ayushman Card is the treatment cover for eligible families."
        ),
        "eligibility": (
            "Every Indian citizen, at any age\n"
            "No income test, no card requirement\n"
            "Completely voluntary — health services cannot be refused for not having one"
        ),
        "documents": ("Aadhaar card with a linked mobile number, or a driving licence"),
        "application_steps": (
            "Go to abha.abdm.gov.in or install the ABHA app.\n"
            "Choose to create an ABHA using Aadhaar or a driving licence.\n"
            "Enter the number and verify with the OTP sent to your linked mobile.\n"
            "Choose an ABHA address, which looks like an email address, for example yourname@abdm.\n"
            "Link records by giving your ABHA number at hospitals and labs that participate. You approve "
            "each request before anyone can view your records."
        ),
        "where_to_apply": "abha.abdm.gov.in, the ABHA app, or any participating hospital",
        "official_link": "https://abdm.gov.in",
        "helpline": "1800-11-4477",
    },
    {
        "name": "National Programme for Prevention and Control of Non-Communicable Diseases",
        "short_name": "NP-NCD",
        "level": "central", "category": "disease", "eligible_cards": "any",
        "display_order": 12,
        "headline_benefit": "Free screening and medicines for BP, diabetes and common cancers",
        "description": (
            "Free population-level screening for hypertension, diabetes, and oral, breast and cervical "
            "cancer for everyone over 30, delivered through Ayushman Arogya Mandirs (formerly Health and "
            "Wellness Centres) and NCD clinics at district and sub-district hospitals.\n\n"
            "Once diagnosed, monthly medicines for blood pressure and diabetes are supplied free at these "
            "centres. This matters because these conditions are lifelong, and it is the recurring cost of "
            "tablets rather than the diagnosis that makes people stop treatment."
        ),
        "eligibility": (
            "Everyone aged 30 and above is eligible for free screening\n"
            "No income test or ration card requirement\n"
            "Free follow-up medicines for those diagnosed with hypertension or diabetes\n"
            "Cancer screening for women includes breast and cervical cancer"
        ),
        "documents": ("Aadhaar card, if available\nAny previous prescriptions or reports"),
        "application_steps": (
            "Visit your nearest Ayushman Arogya Mandir or the NCD clinic at a government hospital.\n"
            "Ask for NCD screening. Blood pressure and blood sugar are checked on the spot.\n"
            "If a reading is abnormal, you are enrolled in the NCD register and given a treatment card.\n"
            "Collect your monthly medicines free from the same centre and attend the follow-up checks.\n"
            "Women should also ask specifically for oral, breast and cervical cancer screening, which is "
            "part of the same programme."
        ),
        "where_to_apply": "Ayushman Arogya Mandir or the NCD clinic at any government hospital",
        "official_link": "https://nhm.gov.in",
        "helpline": "104",
    },
]

# ---------------------------------------------------------------------------
# HOSPITALS — real names, invented bed numbers
# ---------------------------------------------------------------------------
HOSPITALS = [
    ("Dr. Vasantrao Pawar Medical College & Hospital", "trust", "Vasantdada Nagar, Adgaon", "Adgaon", "Nashik", "422003", 20.0450, 73.8570, "0253-2303100", True, True,
     ["General Medicine", "Cardiology", "Neurology", "Orthopaedics", "Pulmonology", "Gastroenterology", "Urology", "Endocrinology", "Dermatology", "ENT", "Ophthalmology"], 450),
    ("Nashik Civil Hospital (District Hospital)", "govt", "Trimbak Road, Nashik", "Trimbak Road", "Nashik", "422002", 19.9975, 73.7898, "0253-2572001", True, True,
     ["General Medicine", "Orthopaedics", "Pulmonology", "Gastroenterology", "Urology", "ENT", "Ophthalmology", "Dermatology"], 380),
    ("Wockhardt Hospitals, Nashik", "private", "Wadala Road, Near Ganpati Mandir", "Wadala Road", "Nashik", "422011", 19.9820, 73.7960, "0253-6633333", True, True,
     ["Cardiology", "Neurology", "Orthopaedics", "General Medicine", "Urology", "Gastroenterology"], 180),
    ("Apollo Hospitals, Nashik", "private", "Swami Vivekanand Nagar, Mumbai Naka", "Mumbai Naka", "Nashik", "422001", 19.9690, 73.7620, "0253-6669999", True, True,
     ["Cardiology", "Neurology", "Endocrinology", "General Medicine", "Orthopaedics", "Pulmonology"], 210),
    ("Six Sigma Medicare & Research Centre", "private", "Mahatma Nagar, Trimbak Road", "Mahatma Nagar", "Nashik", "422007", 20.0010, 73.7500, "0253-2311000", True, False,
     ["General Medicine", "Orthopaedics", "Gastroenterology", "Urology", "ENT"], 120),
    ("Sahyadri Super Speciality Hospital, Nashik", "private", "Mumbai Naka, Nashik", "Mumbai Naka", "Nashik", "422001", 19.9710, 73.7655, "0253-6604000", True, True,
     ["Cardiology", "Neurology", "Gastroenterology", "Urology", "Orthopaedics", "General Medicine"], 160),
    ("Nashik Municipal Corporation Bitco Hospital", "municipal", "Nashik Road", "Nashik Road", "Nashik", "422101", 19.9490, 73.8380, "0253-2461101", True, True,
     ["General Medicine", "Orthopaedics", "ENT", "Ophthalmology", "Dermatology"], 150),
    ("Suyash Hospital", "private", "College Road, Nashik", "College Road", "Nashik", "422005", 20.0030, 73.7690, "0253-2311200", True, False,
     ["General Medicine", "Pulmonology", "Endocrinology", "Dermatology", "ENT"], 90),
    ("Sancheti Hospital", "trust", "16, Shivajinagar, Pune", "Shivajinagar", "Pune", "411005", 18.5310, 73.8470, "020-25533333", True, True,
     ["Orthopaedics", "General Medicine", "Neurology"], 300),
    ("Sassoon General Hospital", "govt", "Near Pune Railway Station", "Sassoon Road", "Pune", "411001", 18.5290, 73.8740, "020-26128000", True, True,
     ["General Medicine", "Cardiology", "Neurology", "Orthopaedics", "Pulmonology", "Gastroenterology", "Urology", "Endocrinology", "Dermatology", "ENT", "Ophthalmology"], 1300),
    ("Ruby Hall Clinic", "trust", "40, Sassoon Road, Pune", "Sassoon Road", "Pune", "411001", 18.5320, 73.8790, "020-66455100", True, True,
     ["Cardiology", "Neurology", "Gastroenterology", "Urology", "Endocrinology", "General Medicine", "Pulmonology"], 550),
    ("Deenanath Mangeshkar Hospital", "trust", "Erandwane, Pune", "Erandwane", "Pune", "411004", 18.5050, 73.8230, "020-40151000", True, True,
     ["Cardiology", "Neurology", "Orthopaedics", "Gastroenterology", "Endocrinology", "General Medicine", "Ophthalmology"], 600),
    ("Jehangir Hospital", "private", "32, Sassoon Road, Pune", "Sassoon Road", "Pune", "411001", 18.5300, 73.8760, "020-66819999", True, True,
     ["Cardiology", "Neurology", "Orthopaedics", "General Medicine", "Dermatology", "ENT"], 350),
    ("Bharati Vidyapeeth Medical College Hospital", "trust", "Katraj-Dhankawadi, Pune", "Katraj", "Pune", "411043", 18.4570, 73.8560, "020-24374126", True, True,
     ["General Medicine", "Orthopaedics", "Pulmonology", "Urology", "Dermatology", "ENT", "Ophthalmology"], 800),
    ("Pune Municipal Corporation Kamla Nehru Hospital", "municipal", "Mangalwar Peth, Pune", "Mangalwar Peth", "Pune", "411011", 18.5230, 73.8600, "020-26058176", True, False,
     ["General Medicine", "Pulmonology", "Dermatology", "ENT"], 200),
]

TIPS = [
    ("A cough lasting over two weeks needs a test, not a syrup",
     "It is the single clearest warning sign of TB. The sputum test at a government DOTS centre is free, takes minutes, and treatment is free too. Waiting is what makes TB dangerous, both for you and everyone around you.", "lungs", 1),
    ("Nobody can feel high blood pressure",
     "It causes no symptoms until it causes a stroke. If you are over 30, get it measured — it is free at any Ayushman Arogya Mandir and takes under a minute.", "heart", 2),
    ("Do not pay a deposit at an empanelled hospital",
     "If you hold a valid Ayushman or MJPJAY entitlement, covered treatment is cashless. Ask for the Arogya Mitra desk before you pay anything, and report demands for money on 14555.", "shield", 3),
    ("Steroid creams make fungal infections worse",
     "The itch settles for a few days, then comes back larger and harder to treat. Ring-shaped itchy patches need an antifungal, not whatever cream the shop recommends.", "drop", 4),
    ("Start ORS before the dehydration, not after",
     "For loose motions, ORS is the treatment — not an afterthought. It is free at government health centres. Small sips, often, beats a large glass all at once.", "drop", 5),
    ("Ask for the generic version of every long-term medicine",
     "For BP, diabetes or thyroid tablets taken daily for years, a Janaushadhi Kendra can cut the annual cost by half or more. Same molecule, tested, far cheaper.", "plate", 6),
]


class Command(BaseCommand):
    help = "Seed schemes, hospitals, bed data, disease info and health tips."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(7)

        if options["reset"]:
            self.stdout.write("Clearing existing data...")
            BedAvailability.objects.all().delete()
            Hospital.objects.all().delete()
            Specialisation.objects.all().delete()
            Scheme.objects.all().delete()
            DiseaseInfo.objects.all().delete()
            HealthTip.objects.all().delete()

        # --- Schemes --------------------------------------------------------
        made = 0
        for row in SCHEMES:
            data = dict(row)
            data["slug"] = slugify(data["short_name"] or data["name"])[:220]
            data["last_verified"] = VERIFIED
            _, created = Scheme.objects.update_or_create(slug=data["slug"], defaults=data)
            made += created
        self.stdout.write(self.style.SUCCESS(f"Schemes:      {Scheme.objects.count()} total ({made} new)"))

        # --- Specialisations ------------------------------------------------
        all_specs = sorted({d["specialisation"] for d in DISEASES.values()}
                           | set(EXTRA_SPECIALISATIONS))
        for name in all_specs:
            Specialisation.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS(f"Departments:  {Specialisation.objects.count()}"))

        # --- Hospitals + beds ------------------------------------------------
        # A handful of Pune hospitals appear in both lists under slightly
        # different names. Keyed by name, the district list wins, and the
        # aliases below stop near-duplicates becoming two separate records.
        ALIASES = {
            "Deenanath Mangeshkar Hospital": "Deenanath Mangeshkar Hospital & Research Centre",
            "Pune Municipal Corporation Kamla Nehru Hospital": "PMC Kamla Nehru Hospital",
        }
        merged = {}
        for row in HOSPITALS:
            merged[ALIASES.get(row[0], row[0])] = row
        for row in pune_hospital_rows():
            merged[ALIASES.get(row[0], row[0])] = row

        for (name, htype, address, area, city, pin, lat, lng, phone,
             emergency, ambulance, specs, total) in merged.values():
            hospital, _ = Hospital.objects.update_or_create(
                name=name,
                defaults={
                    "hospital_type": htype, "address": address, "area": area,
                    "city": city, "district": city, "pincode": pin,
                    "latitude": lat, "longitude": lng,
                    "contact_number": phone,
                    "emergency_number": phone if emergency else "",
                    "has_emergency": emergency, "has_ambulance": ambulance,
                    "accepts_pmjay": htype in ("govt", "municipal", "trust") or rng.random() < 0.5,
                    "is_active": True,
                },
            )
            hospital.specialisations.set(Specialisation.objects.filter(name__in=specs))

            # Invented occupancy: government hospitals run fuller than private ones.
            pressure = 0.90 if htype in ("govt", "municipal") else 0.76
            free_total = max(0, int(total * (1 - pressure) * rng.uniform(0.4, 1.9)))
            icu = int(free_total * rng.uniform(0.05, 0.14))
            oxygen = int(free_total * rng.uniform(0.08, 0.18))
            vent = int(free_total * rng.uniform(0.01, 0.05))
            general = max(0, free_total - icu - oxygen - vent)

            BedAvailability.objects.update_or_create(
                hospital=hospital,
                defaults={
                    "total_beds": total,
                    "general_available": general,
                    "icu_available": icu,
                    "oxygen_available": oxygen,
                    "ventilator_available": vent,
                    "updated_by": "Seed script (demonstration data)",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Hospitals:    {Hospital.objects.count()} with bed records"))

        # --- Disease info ----------------------------------------------------
        # Every specialisation referenced by a condition must exist, or the
        # referral lookup on the result page silently returns nothing.
        for spec in SPECIALISATIONS:
            Specialisation.objects.get_or_create(name=spec)

        for row in as_seed_rows():
            DiseaseInfo.objects.update_or_create(
                name=row["name"],
                defaults={
                    "about": row["about"],
                    "precautions": row["precautions"],
                    "avoid": row["avoid"],
                    "tests": row["tests"],
                    "specialisation": row["specialisation"],
                    "urgency": row["urgency"],
                    "sensitive": row["sensitive"],
                },
            )
        with_warnings = DiseaseInfo.objects.exclude(avoid="").count()
        self.stdout.write(self.style.SUCCESS(
            f"Conditions:   {DiseaseInfo.objects.count()} "
            f"({with_warnings} with drug safety warnings)"))

        # --- Health tips ------------------------------------------------------
        for title, body, icon, order in TIPS:
            HealthTip.objects.update_or_create(
                title=title,
                defaults={"body": body, "icon": icon, "display_order": order, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS(f"Health tips:  {HealthTip.objects.count()}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
        self.stdout.write("Next: python manage.py createsuperuser, then runserver.")
