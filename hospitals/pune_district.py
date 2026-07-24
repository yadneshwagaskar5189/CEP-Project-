"""
pune_district.py
----------------
Hospitals across Pune district, for seeding.

SCOPE
Pune district is 15 talukas: two city talukas (Pune City, Pimpri-Chinchwad) and
13 rural ones (Ambegaon, Baramati, Bhor, Daund, Haveli, Indapur, Junnar, Khed,
Maval, Mulshi, Purandar, Shirur, Velha). This file covers:

  * state government facilities  - district hospital, medical colleges, the
                                   sub-district and rural hospital network
  * municipal facilities         - PMC, PCMC and the cantonment boards
  * trust / charitable hospitals - the large teaching and mission hospitals
  * private hospitals            - the major multi-speciality centres, weighted
                                   towards those empanelled for PM-JAY / MJPJAY

WHAT IS REAL AND WHAT IS NOT
-----------------------------------------------------------------------------
REAL      hospital names, the taluka or area each sits in, and hospital type.
APPROX    coordinates are placed at the town or locality, not the building, and
          are good enough to sort by area but not to navigate with.
APPROX    phone numbers follow the correct STD code for the taluka; the local
          part is NOT dialled-and-checked. Treat them as placeholders.
INVENTED  every bed count, and total_beds. See the note in BedAvailability.

VERIFY BEFORE SUBMISSION
This list was compiled from public sources in July 2026. Facilities open, close,
change name and get de-empanelled. The government network in particular is
reorganised often - a Rural Hospital is upgraded to a Sub-District Hospital and
the designation changes. Check anything you intend to state as fact, and say in
your report that you did.

Rows are (name, type, address, area, city, pin, lat, lng, phone,
          emergency, ambulance, [specialisations], total_beds).
"""

# Shorthand for the department bundles, so the rows below stay readable.
GEN = ["General Medicine"]
BASIC = ["General Medicine", "Orthopaedics", "ENT", "Ophthalmology"]
RURAL = ["General Medicine", "Orthopaedics", "Paediatrics", "Gynaecology"]
DISTRICT = ["General Medicine", "Orthopaedics", "Paediatrics", "Gynaecology",
            "ENT", "Ophthalmology", "Dermatology", "Pulmonology", "Psychiatry"]
TEACHING = ["General Medicine", "Cardiology", "Neurology", "Orthopaedics", "Pulmonology",
            "Gastroenterology", "Urology", "Endocrinology", "Dermatology", "ENT",
            "Ophthalmology", "Paediatrics", "Gynaecology", "Psychiatry",
            "Nephrology", "Oncology"]
MULTI = ["General Medicine", "Cardiology", "Neurology", "Orthopaedics", "Gastroenterology",
         "Urology", "Pulmonology", "Nephrology"]
SUPER = ["Cardiology", "Neurology", "Gastroenterology", "Urology", "Nephrology",
         "Oncology", "General Medicine", "Orthopaedics"]

# Departments a hospital can have that no condition in the model maps to. They
# are seeded anyway, because a hospital list that omits Paediatrics would look
# wrong to anyone reading it.
EXTRA_SPECIALISATIONS = ["Paediatrics", "Oncology"]


PUNE_DISTRICT_HOSPITALS = [

    # =======================================================================
    # STATE GOVERNMENT - district level and medical colleges
    # =======================================================================
    ("District Hospital Pune (Aundh Civil Hospital)", "govt",
     "Aundh, Pune", "Aundh", "Pune", "411027", 18.5590, 73.8070,
     "020-25887000", True, True, DISTRICT, 360),

    ("Punyashlok Ahilyadevi Holkar Government Medical College & Swargiya Ajitdada Pawar General Hospital", "govt",
     "MIDC Area, Baramati", "Baramati MIDC", "Baramati", "413133", 18.1520, 74.5770,
     "02112-243000", True, True, TEACHING, 500),

    ("Regional Mental Hospital, Yerwada", "govt",
     "Yerwada, Pune", "Yerwada", "Pune", "411006", 18.5510, 73.8850,
     "020-26681530", False, False, ["Psychiatry", "General Medicine"], 2540),

    ("Aundh Chest Hospital (TB & Respiratory Diseases)", "govt",
     "Aundh, Pune", "Aundh", "Pune", "411027", 18.5620, 73.8100,
     "020-25885000", True, False, ["Pulmonology", "General Medicine"], 300),

    # =======================================================================
    # PUNE MUNICIPAL CORPORATION
    # =======================================================================
    ("PMC Dr. Naidu Infectious Diseases Hospital", "municipal",
     "Naidu Hospital Road, Yerwada", "Yerwada", "Pune", "411006", 18.5350, 73.8760,
     "020-26051006", True, True, ["General Medicine", "Pulmonology", "Paediatrics"], 250),

    ("PMC Rajiv Gandhi Hospital, Yerwada", "municipal",
     "Yerwada, Pune", "Yerwada", "Pune", "411006", 18.5490, 73.8820,
     "020-26690000", True, True, BASIC + ["Paediatrics", "Gynaecology"], 180),

    ("PMC Dr. Dalvi Hospital", "municipal",
     "Shivajinagar, Pune", "Shivajinagar", "Pune", "411005", 18.5300, 73.8480,
     "020-25534000", True, False, BASIC, 100),

    ("PMC Sonawane Hospital", "municipal",
     "Navi Peth, Pune", "Navi Peth", "Pune", "411030", 18.5090, 73.8420,
     "020-24450000", True, False, BASIC + ["Gynaecology"], 120),

    # =======================================================================
    # PIMPRI-CHINCHWAD MUNICIPAL CORPORATION
    # =======================================================================
    ("Yashwantrao Chavan Memorial (YCM) Hospital", "municipal",
     "Sant Tukaram Nagar, Pimpri", "Pimpri", "Pimpri-Chinchwad", "411018", 18.6280, 73.8000,
     "020-27423000", True, True, TEACHING, 750),

    ("PCMC Talera Hospital", "municipal",
     "Chinchwad, Pimpri-Chinchwad", "Chinchwad", "Pimpri-Chinchwad", "411033", 18.6480, 73.7990,
     "020-27355000", True, True, BASIC + ["Paediatrics"], 150),

    ("PCMC Jijamata Hospital", "municipal",
     "Pimpri, Pimpri-Chinchwad", "Pimpri", "Pimpri-Chinchwad", "411018", 18.6250, 73.8050,
     "020-27425000", True, True, RURAL, 130),

    ("PCMC New Bhosari Hospital", "municipal",
     "Bhosari, Pimpri-Chinchwad", "Bhosari", "Pimpri-Chinchwad", "411039", 18.6280, 73.8470,
     "020-27110000", True, True, BASIC, 120),

    ("PCMC Thergaon Hospital", "municipal",
     "Thergaon, Pimpri-Chinchwad", "Thergaon", "Pimpri-Chinchwad", "411033", 18.6050, 73.7660,
     "020-27275000", True, False, BASIC, 90),

    ("PCMC Akurdi Hospital", "municipal",
     "Akurdi, Pimpri-Chinchwad", "Akurdi", "Pimpri-Chinchwad", "411035", 18.6480, 73.7660,
     "020-27640000", True, False, BASIC, 80),

    # =======================================================================
    # CANTONMENT BOARDS
    # =======================================================================
    ("Sardar Vallabhbhai Patel Cantonment General Hospital", "municipal",
     "Golibar Maidan, Pune Camp", "Pune Camp", "Pune", "411001", 18.5080, 73.8790,
     "020-26363000", True, True, BASIC + ["Paediatrics", "Gynaecology"], 160),

    ("Command Hospital (Southern Command)", "govt",
     "Wanowrie, Pune", "Wanowrie", "Pune", "411040", 18.4890, 73.8930,
     "020-26026000", True, True, TEACHING, 1100),

    # =======================================================================
    # TEACHING / TRUST HOSPITALS
    # =======================================================================
    ("Dr. D. Y. Patil Medical College, Hospital & Research Centre", "trust",
     "Sant Tukaram Nagar, Pimpri", "Pimpri", "Pimpri-Chinchwad", "411018", 18.6230, 73.8010,
     "020-27805000", True, True, TEACHING, 1200),

    ("Smt. Kashibai Navale Medical College & General Hospital", "trust",
     "Narhe, Off Mumbai-Bangalore Highway", "Narhe", "Pune", "411041", 18.4560, 73.8180,
     "020-24106200", True, True, TEACHING, 900),

    ("KEM Hospital, Pune", "trust",
     "489, Rasta Peth, Sardar Moodliar Road", "Rasta Peth", "Pune", "411011", 18.5230, 73.8730,
     "020-66037300", True, True, MULTI + ["Paediatrics", "Gynaecology"], 550),

    ("Symbiosis University Hospital & Research Centre", "trust",
     "Symbiosis Knowledge Village, Lavale", "Lavale", "Mulshi", "412115", 18.5310, 73.7080,
     "020-28116000", True, True, MULTI, 300),

    ("Poona Hospital & Research Centre", "trust",
     "27, Sadashiv Peth, Nirmala Convent Road", "Sadashiv Peth", "Pune", "411030", 18.5100, 73.8480,
     "020-66096000", True, True, MULTI, 350),

    ("Inlaks & Budhrani Hospital", "trust",
     "7-9, Koregaon Park", "Koregaon Park", "Pune", "411001", 18.5370, 73.8930,
     "020-66013000", True, True, MULTI, 200),

    ("N. M. Wadia Institute of Cardiology", "trust",
     "32, Sassoon Road", "Sassoon Road", "Pune", "411001", 18.5300, 73.8750,
     "020-26058000", True, False, ["Cardiology", "General Medicine"], 120),

    ("National Institute of Ophthalmology", "trust",
     "1187/30, Off Ghole Road, Shivajinagar", "Shivajinagar", "Pune", "411005", 18.5250, 73.8420,
     "020-66033000", False, False, ["Ophthalmology"], 60),

    ("H. V. Desai Eye Hospital", "trust",
     "Mohammadwadi, Hadapsar", "Hadapsar", "Pune", "411060", 18.4700, 73.9100,
     "020-26970000", False, False, ["Ophthalmology"], 150),

    ("Cipla Palliative Care & Training Centre", "trust",
     "Warje, Pune", "Warje", "Pune", "411058", 18.4820, 73.8010,
     "020-25230000", False, False, ["Oncology", "General Medicine"], 50),

    ("Chellaram Diabetes Institute", "trust",
     "Lalani Quantum, Bavdhan", "Bavdhan", "Pune", "411021", 18.5140, 73.7770,
     "020-66839000", False, False, ["Endocrinology", "General Medicine"], 60),

    ("Sancheti Hospital", "trust",
     "16, Shivajinagar, Thube Park", "Shivajinagar", "Pune", "411005", 18.5310, 73.8470,
     "020-25533333", True, True, ["Orthopaedics", "General Medicine", "Neurology"], 300),

    ("Bharati Vidyapeeth Medical College Hospital", "trust",
     "Katraj-Dhankawadi, Pune-Satara Road", "Katraj", "Pune", "411043", 18.4570, 73.8560,
     "020-24374126", True, True, TEACHING, 800),

    ("Deenanath Mangeshkar Hospital & Research Centre", "trust",
     "Erandwane, Near Mhatre Bridge", "Erandwane", "Pune", "411004", 18.5050, 73.8230,
     "020-40151000", True, True, TEACHING, 600),

    ("Ruby Hall Clinic", "trust",
     "40, Sassoon Road", "Sassoon Road", "Pune", "411001", 18.5320, 73.8790,
     "020-66455100", True, True, SUPER + ["Endocrinology", "Pulmonology"], 550),

    ("Ruby Hall Clinic, Wanowrie", "trust",
     "Sopan Baug, Wanowrie", "Wanowrie", "Pune", "411040", 18.4960, 73.8990,
     "020-67116000", True, True, MULTI, 200),

    ("Ruby Hall Clinic, Hinjawadi", "trust",
     "Hinjawadi Phase 1", "Hinjawadi", "Pune", "411057", 18.5910, 73.7380,
     "020-67206000", True, True, MULTI, 150),

    # =======================================================================
    # MAJOR PRIVATE - Pune city
    # =======================================================================
    ("Jehangir Hospital", "private",
     "32, Sassoon Road", "Sassoon Road", "Pune", "411001", 18.5300, 73.8760,
     "020-66819999", True, True, MULTI + ["Dermatology", "ENT"], 350),

    ("Sahyadri Super Speciality Hospital, Deccan Gymkhana", "private",
     "Plot 30-C, Erandwane, Karve Road", "Deccan Gymkhana", "Pune", "411004", 18.5140, 73.8330,
     "020-67213000", True, True, SUPER, 250),

    ("Sahyadri Super Speciality Hospital, Nagar Road", "private",
     "Nagar Road, Yerwada", "Nagar Road", "Pune", "411006", 18.5540, 73.9020,
     "020-67215000", True, True, SUPER, 200),

    ("Sahyadri Super Speciality Hospital, Hadapsar", "private",
     "Bhosale Garden, Hadapsar", "Hadapsar", "Pune", "411028", 18.5090, 73.9260,
     "020-67227000", True, True, MULTI, 180),

    ("Sahyadri Hospital, Bibwewadi", "private",
     "Bibwewadi, Pune-Satara Road", "Bibwewadi", "Pune", "411037", 18.4700, 73.8620,
     "020-67210000", True, True, MULTI, 120),

    ("Noble Hospital & Research Centre", "private",
     "153, Magarpatta City Road, Hadapsar", "Hadapsar", "Pune", "411013", 18.5100, 73.9280,
     "020-66285000", True, True, MULTI, 300),

    ("Manipal Hospital, Kharadi (formerly Columbia Asia)", "private",
     "Survey 49, Near Nyati County, Kharadi", "Kharadi", "Pune", "411014", 18.5510, 73.9410,
     "020-67164000", True, True, MULTI, 220),

    ("Jupiter Hospital, Baner", "private",
     "Baner-Pashan Link Road", "Baner", "Pune", "411045", 18.5590, 73.7830,
     "020-67681000", True, True, SUPER, 350),

    ("Aditya Birla Memorial Hospital", "private",
     "Aditya Birla Marg, Thergaon, Chinchwad", "Thergaon", "Pimpri-Chinchwad", "411033", 18.6080, 73.7660,
     "020-30717000", True, True, SUPER, 500),

    ("Apollo Spectra Hospital, Pune", "private",
     "Sadashiv Peth, Near Alka Talkies", "Sadashiv Peth", "Pune", "411030", 18.5090, 73.8500,
     "020-67300000", True, True, MULTI, 80),

    ("Global Hospital & Research Institute", "private",
     "Dattawadi, Sinhagad Road", "Dattawadi", "Pune", "411030", 18.4960, 73.8360,
     "020-24350000", True, False, BASIC + ["General Medicine"], 100),

    ("Hardikar Hospital", "private",
     "1160/61, Shivajinagar, Model Colony", "Shivajinagar", "Pune", "411016", 18.5290, 73.8380,
     "020-25661000", True, False, ["Gynaecology", "Paediatrics", "General Medicine"], 90),

    ("Joshi Hospital", "private",
     "778, Shivajinagar, Deccan Gymkhana", "Shivajinagar", "Pune", "411004", 18.5180, 73.8420,
     "020-25534000", True, False, MULTI, 110),

    ("Kotbagi Hospital", "private",
     "Aundh, DP Road", "Aundh", "Pune", "411007", 18.5590, 73.8100,
     "020-25889000", True, True, MULTI, 130),

    ("Gupte Hospital", "private",
     "Baner Road", "Baner", "Pune", "411045", 18.5610, 73.7860,
     "020-27290000", True, False, ["Gynaecology", "Paediatrics"], 60),

    ("Inamdar Multispeciality Hospital", "private",
     "Fatima Nagar, Wanowrie", "Fatima Nagar", "Pune", "411040", 18.5010, 73.8990,
     "020-26870000", True, True, MULTI, 150),

    ("Medipoint Hospital", "private",
     "Aundh, DP Road", "Aundh", "Pune", "411007", 18.5580, 73.8070,
     "020-27290100", True, True, MULTI, 120),

    ("ONP Leela Hospital", "private",
     "Shivajinagar, Pune", "Shivajinagar", "Pune", "411005", 18.5270, 73.8450,
     "020-25530000", True, False, ["Gynaecology", "Paediatrics"], 70),

    ("Oyster & Pearl Hospital", "private",
     "Nagar Road, Kalyani Nagar", "Kalyani Nagar", "Pune", "411006", 18.5480, 73.9020,
     "020-67240000", True, True, ["Gynaecology", "Paediatrics", "General Medicine"], 80),

    ("Cloudnine Hospital, Kalyani Nagar", "private",
     "Kalyani Nagar, Pune", "Kalyani Nagar", "Pune", "411006", 18.5490, 73.9040,
     "020-67290000", True, False, ["Gynaecology", "Paediatrics"], 70),

    ("Motherhood Hospital, Kharadi", "private",
     "Kharadi, Pune", "Kharadi", "Pune", "411014", 18.5520, 73.9430,
     "020-67380000", True, False, ["Gynaecology", "Paediatrics"], 60),

    ("Sanjeevan Hospital", "private",
     "Erandwane, Karve Road", "Erandwane", "Pune", "411004", 18.5060, 73.8290,
     "020-25441000", True, False, MULTI, 100),

    ("Ratna Memorial Hospital", "private",
     "968, Senapati Bapat Road, Shivajinagar", "Senapati Bapat Road", "Pune", "411016", 18.5310, 73.8290,
     "020-25671000", True, False, MULTI, 90),

    ("Shashwat Hospital", "private",
     "Aundh, Pune", "Aundh", "Pune", "411007", 18.5610, 73.8080,
     "020-25880000", True, True, MULTI, 100),

    ("Star Hospital", "private",
     "Kondhwa Khurd", "Kondhwa", "Pune", "411048", 18.4650, 73.8880,
     "020-26830000", True, True, MULTI, 90),

    ("Vishwaraj Hospital", "private",
     "Loni Kalbhor, Pune-Solapur Road", "Loni Kalbhor", "Haveli", "412201", 18.4650, 74.0250,
     "020-67206200", True, True, MULTI, 200),

    ("Lifepoint Multispeciality Hospital", "private",
     "Wakad, Pune", "Wakad", "Pimpri-Chinchwad", "411057", 18.5980, 73.7620,
     "020-67308000", True, True, MULTI, 120),

    ("Apple Hospital", "private",
     "Wakad, Pune", "Wakad", "Pimpri-Chinchwad", "411057", 18.5960, 73.7650,
     "020-67390000", True, False, BASIC, 70),

    ("Lokmanya Hospital, Nigdi", "private",
     "Nigdi, Pradhikaran", "Nigdi", "Pimpri-Chinchwad", "411044", 18.6510, 73.7690,
     "020-27650000", True, True, ["Orthopaedics", "General Medicine", "Neurology"], 130),

    ("Lokmanya Hospital, Chinchwad", "private",
     "Chinchwad, Pimpri-Chinchwad", "Chinchwad", "Pimpri-Chinchwad", "411033", 18.6440, 73.7980,
     "020-27442000", True, True, ["Orthopaedics", "General Medicine"], 110),

    ("Surya Mother & Child Super Speciality Hospital", "private",
     "Wakad, Pune", "Wakad", "Pimpri-Chinchwad", "411057", 18.5990, 73.7600,
     "020-67206000", True, True, ["Gynaecology", "Paediatrics"], 100),

    ("Sterling Multispeciality Hospital", "private",
     "Nigdi, Pimpri-Chinchwad", "Nigdi", "Pimpri-Chinchwad", "411044", 18.6520, 73.7700,
     "020-27659000", True, True, MULTI, 100),

    ("Birla Hospital, Chinchwad", "private",
     "Chinchwad, Pimpri-Chinchwad", "Chinchwad", "Pimpri-Chinchwad", "411033", 18.6460, 73.8010,
     "020-27351000", True, True, MULTI, 120),

    # =======================================================================
    # HAVELI TALUKA (the rural belt wrapped around Pune city)
    # =======================================================================
    ("Rural Hospital, Wagholi", "govt",
     "Wagholi, Nagar Road", "Wagholi", "Haveli", "412207", 18.5800, 73.9800,
     "020-27050000", True, True, RURAL, 50),

    ("Rural Hospital, Loni Kalbhor", "govt",
     "Loni Kalbhor", "Loni Kalbhor", "Haveli", "412201", 18.4630, 74.0230,
     "020-26910000", True, False, RURAL, 30),

    ("Rural Hospital, Khadakwasla", "govt",
     "Khadakwasla", "Khadakwasla", "Haveli", "411024", 18.4390, 73.7690,
     "020-25440000", True, False, RURAL, 30),

    # =======================================================================
    # BARAMATI TALUKA
    # =======================================================================
    ("Sub-District Hospital, Baramati", "govt",
     "Baramati, Pune", "Baramati", "Baramati", "413102", 18.1510, 74.5800,
     "02112-224000", True, True, DISTRICT, 100),

    ("Rural Hospital, Malegaon (Baramati)", "govt",
     "Malegaon Budruk", "Malegaon", "Baramati", "413115", 18.1120, 74.4600,
     "02112-255000", True, False, RURAL, 30),

    ("Rural Hospital, Supe", "govt",
     "Supe, Baramati", "Supe", "Baramati", "412213", 18.3560, 74.4200,
     "02112-266000", True, False, RURAL, 30),

    ("Silver Jubilee Government Hospital, Baramati", "govt",
     "Baramati, Pune", "Baramati", "Baramati", "413102", 18.1490, 74.5820,
     "02112-222000", True, True, DISTRICT, 120),

    ("Giriraj Hospital, Baramati", "private",
     "Indapur Road, Baramati", "Baramati", "Baramati", "413102", 18.1530, 74.5830,
     "02112-243300", True, True, MULTI, 90),

    # =======================================================================
    # INDAPUR TALUKA
    # =======================================================================
    ("Sub-District Hospital, Indapur", "govt",
     "Indapur, Pune", "Indapur", "Indapur", "413106", 18.1180, 75.0270,
     "02111-223000", True, True, DISTRICT, 100),

    ("Rural Hospital, Bhigwan", "govt",
     "Bhigwan, Indapur", "Bhigwan", "Indapur", "413130", 18.2960, 74.7630,
     "02111-234000", True, False, RURAL, 30),

    ("Rural Hospital, Walchandnagar", "govt",
     "Walchandnagar, Indapur", "Walchandnagar", "Indapur", "413114", 18.2160, 74.7500,
     "02111-236000", True, False, RURAL, 30),

    # =======================================================================
    # DAUND TALUKA
    # =======================================================================
    ("Sub-District Hospital, Daund", "govt",
     "Daund, Pune", "Daund", "Daund", "413801", 18.4640, 74.5810,
     "02117-262000", True, True, DISTRICT, 100),

    ("Rural Hospital, Yavat", "govt",
     "Yavat, Daund", "Yavat", "Daund", "412214", 18.4460, 74.2540,
     "02117-244000", True, False, RURAL, 30),

    ("Rural Hospital, Kedgaon", "govt",
     "Kedgaon, Daund", "Kedgaon", "Daund", "412203", 18.4270, 74.3550,
     "02117-246000", True, False, RURAL, 30),

    # =======================================================================
    # PURANDAR TALUKA
    # =======================================================================
    ("Sub-District Hospital, Saswad", "govt",
     "Saswad, Purandar", "Saswad", "Purandar", "412301", 18.3450, 74.0300,
     "02115-222000", True, True, DISTRICT, 90),

    ("Rural Hospital, Jejuri", "govt",
     "Jejuri, Purandar", "Jejuri", "Purandar", "412303", 18.2770, 74.1600,
     "02115-233000", True, False, RURAL, 30),

    ("Rural Hospital, Nira", "govt",
     "Nira, Purandar", "Nira", "Purandar", "412102", 18.0300, 74.1400,
     "02115-236000", True, False, RURAL, 30),

    # =======================================================================
    # BHOR AND VELHE TALUKAS
    # =======================================================================
    ("Sub-District Hospital, Bhor", "govt",
     "Bhor, Pune", "Bhor", "Bhor", "412206", 18.1490, 73.8430,
     "02113-222000", True, True, DISTRICT, 90),

    ("Rural Hospital, Nasrapur", "govt",
     "Nasrapur, Bhor", "Nasrapur", "Bhor", "412213", 18.2350, 73.8600,
     "02113-244000", True, False, RURAL, 30),

    ("Rural Hospital, Velha", "govt",
     "Velha, Pune", "Velha", "Velha", "412212", 18.2900, 73.6300,
     "02130-234000", True, False, RURAL, 30),

    # =======================================================================
    # KHED TALUKA
    # =======================================================================
    ("Sub-District Hospital, Rajgurunagar (Khed)", "govt",
     "Rajgurunagar, Khed", "Rajgurunagar", "Khed", "410505", 18.8580, 73.8890,
     "02135-222000", True, True, DISTRICT, 100),

    ("Rural Hospital, Chakan", "govt",
     "Chakan, Khed", "Chakan", "Khed", "410501", 18.7600, 73.8640,
     "02135-249000", True, True, RURAL, 50),

    ("Apex Hospital, Rajgurunagar", "private",
     "Pabal Road, Rajgurunagar, Khed", "Rajgurunagar", "Khed", "410505", 18.8600, 73.8910,
     "02135-224000", True, True, MULTI, 70),

    # =======================================================================
    # AMBEGAON TALUKA
    # =======================================================================
    ("Sub-District Hospital, Manchar", "govt",
     "Manchar, Ambegaon", "Manchar", "Ambegaon", "410503", 19.0030, 73.9400,
     "02133-222000", True, True, DISTRICT, 90),

    ("Rural Hospital, Ghodegaon", "govt",
     "Ghodegaon, Ambegaon", "Ghodegaon", "Ambegaon", "412408", 19.0800, 73.8600,
     "02133-244000", True, False, RURAL, 30),

    # =======================================================================
    # JUNNAR TALUKA
    # =======================================================================
    ("Sub-District Hospital, Junnar", "govt",
     "Junnar, Pune", "Junnar", "Junnar", "410502", 19.2080, 73.8750,
     "02132-222000", True, True, DISTRICT, 100),

    ("Rural Hospital, Narayangaon", "govt",
     "Narayangaon, Junnar", "Narayangaon", "Junnar", "410504", 19.0700, 73.9800,
     "02132-244000", True, True, RURAL, 50),

    ("Rural Hospital, Otur", "govt",
     "Otur, Junnar", "Otur", "Junnar", "412409", 19.1800, 74.0200,
     "02132-255000", True, False, RURAL, 30),

    ("Rural Hospital, Alephata", "govt",
     "Alephata, Junnar", "Alephata", "Junnar", "412411", 19.1400, 74.1300,
     "02132-266000", True, False, RURAL, 30),

    # =======================================================================
    # SHIRUR TALUKA
    # =======================================================================
    ("Sub-District Hospital, Shirur (Ghodnadi)", "govt",
     "Shirur, Pune", "Shirur", "Shirur", "412210", 18.8270, 74.3760,
     "02138-222000", True, True, DISTRICT, 90),

    ("Rural Hospital, Ranjangaon", "govt",
     "Ranjangaon MIDC, Shirur", "Ranjangaon", "Shirur", "412220", 18.7600, 74.2400,
     "02138-233000", True, False, RURAL, 30),

    ("Rural Hospital, Shikrapur", "govt",
     "Shikrapur, Shirur", "Shikrapur", "Shirur", "412208", 18.6900, 74.1300,
     "02137-252000", True, False, RURAL, 30),

    ("Rural Hospital, Talegaon Dhamdhere", "govt",
     "Talegaon Dhamdhere, Shirur", "Talegaon Dhamdhere", "Shirur", "412208", 18.6600, 74.0700,
     "02137-256000", True, False, RURAL, 30),

    # =======================================================================
    # MAVAL TALUKA
    # =======================================================================
    ("Sub-District Hospital, Talegaon Dabhade", "govt",
     "Talegaon Dabhade, Maval", "Talegaon Dabhade", "Maval", "410507", 18.7350, 73.6770,
     "02114-222000", True, True, DISTRICT, 90),

    ("Rural Hospital, Vadgaon Maval", "govt",
     "Vadgaon, Maval", "Vadgaon Maval", "Maval", "412106", 18.7500, 73.6400,
     "02114-244000", True, False, RURAL, 30),

    ("Rural Hospital, Lonavala", "govt",
     "Lonavala, Maval", "Lonavala", "Maval", "410401", 18.7530, 73.4090,
     "02114-273000", True, True, RURAL, 50),

    ("Dr. Bhausaheb Sardesai Talegaon Rural Hospital", "trust",
     "Talegaon-Chakan Road, Talegaon Dabhade", "Talegaon Dabhade", "Maval", "410507", 18.7370, 73.6800,
     "02114-226000", True, True, MULTI, 150),

    ("Pioneer Hospital, Talegaon", "private",
     "Old Mumbai-Pune Highway, Talegaon", "Talegaon Dabhade", "Maval", "410506", 18.7300, 73.6750,
     "02114-228000", True, True, BASIC, 60),

    # =======================================================================
    # MULSHI TALUKA
    # =======================================================================
    ("Rural Hospital, Paud", "govt",
     "Paud, Mulshi", "Paud", "Mulshi", "412108", 18.5200, 73.6100,
     "02132-233000", True, False, RURAL, 30),

    ("Rural Hospital, Pirangut", "govt",
     "Pirangut, Mulshi", "Pirangut", "Mulshi", "412115", 18.5100, 73.6700,
     "020-66760000", True, False, RURAL, 30),
]


def as_seed_rows():
    """The list in the tuple shape seed_data.py expects."""
    return list(PUNE_DISTRICT_HOSPITALS)


def summary():
    """Counts by type and by taluka, for the seed command's output."""
    by_type, by_city = {}, {}
    for row in PUNE_DISTRICT_HOSPITALS:
        by_type[row[1]] = by_type.get(row[1], 0) + 1
        by_city[row[4]] = by_city.get(row[4], 0) + 1
    return {"total": len(PUNE_DISTRICT_HOSPITALS), "by_type": by_type, "by_city": by_city}
