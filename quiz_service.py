"""
QUIZ SERVICE: High-Yield Current Affairs & UPSC MCQ Engine
Generates balanced, 4-option multiple-choice questions with educational explanations.
"""
import random
import json
from config import Config
import news_service

# CURATED HIGH-YIELD QUESTION POOL ACCROSS 6 DOMAINS
QUESTION_BANK = {
    "polity": [
        {
            "question": "Which Constitutional Amendment Act introduced the Goods and Services Tax (GST) in India?",
            "options": ["99th Amendment Act", "101st Amendment Act", "103rd Amendment Act", "105th Amendment Act"],
            "correct_index": 1,
            "explanation": "The 101st Constitutional Amendment Act, 2016 introduced the nationwide Goods and Services Tax (GST), establishing Article 246A and the GST Council under Article 279A."
        },
        {
            "question": "Under which Article of the Indian Constitution does the Supreme Court have the power to review its own judgments?",
            "options": ["Article 132", "Article 137", "Article 142", "Article 144"],
            "correct_index": 1,
            "explanation": "Article 137 of the Constitution empowers the Supreme Court to review any judgment pronounced or order made by it."
        },
        {
            "question": "The Law Commission of India submitted its comprehensive report on 'Simultaneous Elections'. Which Article deals with the duration of the Houses of Parliament?",
            "options": ["Article 79", "Article 83", "Article 85", "Article 87"],
            "correct_index": 1,
            "explanation": "Article 83 of the Constitution provides for the duration of both Houses of Parliament (Lok Sabha and Rajya Sabha)."
        },
        {
            "question": "What is the primary role of the Delimitation Commission in India?",
            "options": [
                "Auditing political party funding",
                "Redrawing boundaries of Lok Sabha and Assembly constituencies based on census data",
                "Registering new national political parties",
                "Appointing Election Commissioners"
            ],
            "correct_index": 1,
            "explanation": "The Delimitation Commission is mandated to redraw the boundaries of parliamentary and assembly constituencies based on recent census demographic data."
        },
        {
            "question": "Which writ is issued by the higher courts to command an inferior court or authority to perform a mandatory statutory duty?",
            "options": ["Habeas Corpus", "Mandamus", "Certiorari", "Quo Warranto"],
            "correct_index": 1,
            "explanation": "'Mandamus' literally means 'we command'. It is issued to a public official or body requiring them to perform their statutory duty."
        },
        {
            "question": "In which landmark verdict did the Supreme Court recognize the Right to Privacy as a Fundamental Right under Article 21?",
            "options": [
                "Kesavananda Bharati v. State of Kerala (1973)",
                "Justice K.S. Puttaswamy (Retd.) v. Union of India (2017)",
                "Navtej Singh Johar v. Union of India (2018)",
                "Minerva Mills v. Union of India (1980)"
            ],
            "correct_index": 1,
            "explanation": "A 9-judge bench in K.S. Puttaswamy (2017) unanimously ruled that the right to privacy is an intrinsic part of the right to life and personal liberty under Article 21."
        }
    ],
    "world": [
        {
            "question": "Which nation recently became the newest full member of the BRICS grouping at the beginning of 2024?",
            "options": ["Indonesia", "United Arab Emirates (UAE)", "Argentina", "Nigeria"],
            "correct_index": 1,
            "explanation": "The UAE, Egypt, Ethiopia, and Iran officially joined BRICS on January 1, 2024, expanding the multilateral economic bloc."
        },
        {
            "question": "The strategic 'Chabahar Port', which India is developing to access Central Asia bypassing Pakistan, is located in which water body?",
            "options": ["Red Sea", "Gulf of Oman", "Persian Gulf", "Strait of Malacca"],
            "correct_index": 1,
            "explanation": "Chabahar Port is situated in southeastern Iran on the Gulf of Oman, offering India a direct sea-land transit route to Afghanistan and Central Asia."
        },
        {
            "question": "The 'Abraham Accords' facilitated bilateral diplomatic normalization between Israel and which Arab nations?",
            "options": [
                "Saudi Arabia and Qatar",
                "UAE, Bahrain, Sudan, and Morocco",
                "Jordan and Egypt",
                "Oman and Kuwait"
            ],
            "correct_index": 1,
            "explanation": "Brokered in 2020, the Abraham Accords normalized diplomatic relations between Israel and the UAE, Bahrain, Sudan, and Morocco."
        },
        {
            "question": "What is the primary objective of the India-Middle East-Europe Economic Corridor (IMEC) announced at the G20 New Delhi Summit?",
            "options": [
                "Military defense alliance against piracy",
                "Ship-to-rail transit network fostering economic integration across Asia, the Arabian Gulf, and Europe",
                "Space exploration consortium",
                "Standardization of global semiconductor tariffs"
            ],
            "correct_index": 1,
            "explanation": "IMEC aims to stimulate economic development through connectivity, clean hydrogen transit, and digital trade networks connecting India to Europe through the Gulf."
        },
        {
            "question": "The headquarters of the International Court of Justice (ICJ) is situated in which city?",
            "options": ["Geneva, Switzerland", "The Hague, Netherlands", "Vienna, Austria", "New York, USA"],
            "correct_index": 1,
            "explanation": "The International Court of Justice (ICJ), the principal judicial organ of the UN, is headquartered at the Peace Palace in The Hague, Netherlands."
        }
    ],
    "tech": [
        {
            "question": "India's 'IndiaAI Mission' approved by the Union Cabinet primarily focuses on which key pillar?",
            "options": [
                "Banning open-source foundation models",
                "Democratizing compute infrastructure by procuring over 10,000 GPUs for startups and researchers",
                "Replacing civil servants with automated bots",
                "Creating a sovereign cryptocurrency"
            ],
            "correct_index": 1,
            "explanation": "The IndiaAI Mission was allocated over Rs 10,300 crore to build a national sovereign compute infrastructure with 10,000+ GPUs to nurture indigenous AI innovation."
        },
        {
            "question": "Which Indian spacecraft successfully performed a soft landing near the lunar south polar region in August 2023?",
            "options": ["Mangalyaan-2", "Chandrayaan-3", "Aditya-L1", "Gaganyaan-1"],
            "correct_index": 1,
            "explanation": "ISRO's Chandrayaan-3 made India the first country in history to land a probe near the Moon's rugged south polar region."
        },
        {
            "question": "What does 'Zero-Day Vulnerability' refer to in cybersecurity parlance?",
            "options": [
                "A bug that takes zero days to fix",
                "A software flaw unknown to the vendor, for which no security patch exists yet",
                "A cyberattack launched exactly at midnight",
                "A denial-of-service attack on cloud servers"
            ],
            "correct_index": 1,
            "explanation": "A Zero-Day vulnerability is an unpatched flaw in software or hardware that developers have had 'zero days' to remediate, making it vulnerable to exploitation."
        },
        {
            "question": "Under the Digital Personal Data Protection (DPDP) Act 2023, what is the entity that determines the purpose and means of data processing termed as?",
            "options": ["Data Principal", "Data Fiduciary", "Data Auditor", "Data Courier"],
            "correct_index": 1,
            "explanation": "Under the DPDP Act, a 'Data Fiduciary' is the entity that decides why and how personal data is processed, whereas the individual is the 'Data Principal'."
        },
        {
            "question": "Which orbits do India's NavIC (Navigation with Indian Constellation) satellites utilize?",
            "options": [
                "Low Earth Orbit (LEO) only",
                "Geostationary (GEO) and Geosynchronous (GSO) orbits",
                "Polar Sun-Synchronous Orbits (SSO)",
                "Lunar Trajectory Orbits"
            ],
            "correct_index": 1,
            "explanation": "NavIC employs a regional constellation consisting of satellites placed in both Geostationary (GEO) and inclined Geosynchronous (GSO) orbits."
        }
    ],
    "economy": [
        {
            "question": "What is the primary statutory objective of the Reserve Bank of India's Monetary Policy Committee (MPC)?",
            "options": [
                "Maximizing commercial bank stock values",
                "Maintaining price stability with an inflation target of 4% (+/- 2%) while supporting growth",
                "Managing national fiscal deficit and tax collection",
                "Directing international foreign exchange reserves to trade"
            ],
            "correct_index": 1,
            "explanation": "Under the RBI Act, the MPC is mandated to maintain consumer price index (CPI) inflation within a 4% target band (+/- 2% tolerance) while keeping growth in mind."
        },
        {
            "question": "Which index is considered the headline measure for retail inflation in India?",
            "options": [
                "Wholesale Price Index (WPI)",
                "Consumer Price Index Combined (CPI-C)",
                "Index of Industrial Production (IIP)",
                "Gross Domestic Product Deflator"
            ],
            "correct_index": 1,
            "explanation": "The Reserve Bank of India adopted the Consumer Price Index Combined (CPI-C) as its headline measure of retail inflation in 2014 following Urjit Patel Committee recommendations."
        },
        {
            "question": "What does the term 'Fiscal Deficit' represent in the Union Budget?",
            "options": [
                "Excess of total imports over total exports",
                "Total expenditure minus total receipts (excluding borrowings)",
                "Total revenue expenditure minus revenue receipts",
                "The outstanding external debt owed to IMF and World Bank"
            ],
            "correct_index": 1,
            "explanation": "Fiscal Deficit is the excess of the government's total expenditure over its total non-debt receipts, representing the total borrowing requirements for the fiscal year."
        },
        {
            "question": "India's Sovereign Green Bonds (SGrBs) are issued primarily to finance which category of government expenditures?",
            "options": [
                "Defense procurement and border fencing",
                "Public sector projects that reduce carbon intensity and promote renewable energy",
                "Subsidizing fossil fuel consumption in rural belts",
                "Financing commercial airlines"
            ],
            "correct_index": 1,
            "explanation": "Sovereign Green Bond proceeds are ring-fenced for capital projects that accelerate decarbonization, clean transportation, and renewable energy adoption."
        },
        {
            "question": "Which organization is responsible for compiling and releasing the Index of Industrial Production (IIP) data in India?",
            "options": [
                "NITI Aayog",
                "National Statistical Office (NSO), MoSPI",
                "Reserve Bank of India",
                "Department for Promotion of Industry and Internal Trade (DPIIT)"
            ],
            "correct_index": 1,
            "explanation": "The National Statistical Office (NSO) under the Ministry of Statistics and Programme Implementation (MoSPI) compiles and releases the monthly IIP numbers."
        }
    ],
    "sports": [
        {
            "question": "Which city will host the upcoming 2028 Summer Olympic Games?",
            "options": ["Brisbane, Australia", "Los Angeles, United States", "Madrid, Spain", "Doha, Qatar"],
            "correct_index": 1,
            "explanation": "The 2028 Summer Olympics (Games of the XXXIV Olympiad) are scheduled to be held in Los Angeles, California, USA."
        },
        {
            "question": "Which sport was officially approved by the International Olympic Committee (IOC) for inclusion in the 2028 Los Angeles Olympics?",
            "options": ["Polo", "Cricket (T20 Format)", "Kabaddi", "Kho-Kho"],
            "correct_index": 1,
            "explanation": "Cricket will return to the Olympic Games at Los Angeles 2028 in the Men's and Women's T20 format for the first time since 1900."
        },
        {
            "question": "What is the primary role of the National Anti-Doping Agency (NADA) in India?",
            "options": [
                "Funding athlete travel subsidies",
                "Promoting clean sports and enforcing anti-doping rules in compliance with WADA code",
                "Selecting players for the Olympic contingent",
                "Managing national stadium construction"
            ],
            "correct_index": 1,
            "explanation": "NADA is the national organization responsible for promoting, coordinating, and monitoring the doping control program in sports in India according to World Anti-Doping Agency rules."
        },
        {
            "question": "The 'Khelo India Youth Games' were instituted primarily with what strategic goal?",
            "options": [
                "Privatizing national sports federations",
                "Grassroots talent identification and structured financial support for young athletes",
                "Commercializing university tournaments",
                "Promoting international cricket leagues"
            ],
            "correct_index": 1,
            "explanation": "The Khelo India initiative aims to revive the sports culture in India at the grassroots level and scout budding talents for long-term scholarship support."
        }
    ],
    "general": [
        {
            "question": "World Environment Day is observed globally each year on which date?",
            "options": ["April 22", "June 5", "March 21", "September 16"],
            "correct_index": 1,
            "explanation": "World Environment Day is celebrated annually on June 5, established by the United Nations at the 1972 Stockholm Conference on the Human Environment."
        },
        {
            "question": "Which Indian state became the first in the country to implement a Uniform Civil Code (UCC) post-independence in 2024?",
            "options": ["Gujarat", "Uttarakhand", "Assam", "Madhya Pradesh"],
            "correct_index": 1,
            "explanation": "Uttarakhand became the first state in independent India to pass and implement a Uniform Civil Code Bill governing marriage, divorce, and inheritance across communities."
        },
        {
            "question": "The Nobel Peace Prize 2024 was awarded to which organization for its efforts to achieve a world free of nuclear weapons?",
            "options": [
                "International Campaign to Abolish Nuclear Weapons (ICAN)",
                "Nihon Hidankyo (Japanese atomic bomb survivors movement)",
                "Doctors Without Borders",
                "Amnesty International"
            ],
            "correct_index": 1,
            "explanation": "The Norwegian Nobel Committee awarded the 2024 Nobel Peace Prize to Nihon Hidankyo, a grassroots movement of atomic bomb survivors from Hiroshima and Nagasaki (Hibakusha)."
        },
        {
            "question": "What is the primary objective of the Ramsar Convention signed in 1971?",
            "options": [
                "Protection of the Ozone Layer",
                "Conservation and sustainable utilization of Wetlands",
                "Regulating transboundary movement of hazardous waste",
                "Mitigating space debris in low Earth orbit"
            ],
            "correct_index": 1,
            "explanation": "The Ramsar Convention is an intergovernmental treaty that provides the framework for the conservation and wise use of wetlands and their resources."
        }
    ]
}

def generate_quiz_for_category(category="polity", count=5):
    """
    Returns 5 balanced multiple-choice questions for the specified category.
    """
    category = (category or "general").lower().strip()
    
    # If category not directly in bank or general mix requested
    if category == "general" or category not in QUESTION_BANK:
        pool = []
        for cat_questions in QUESTION_BANK.values():
            pool.extend(cat_questions)
    else:
        pool = list(QUESTION_BANK[category])
        # If pool has fewer than requested count, backfill from other categories
        if len(pool) < count:
            other_questions = []
            for k, v in QUESTION_BANK.items():
                if k != category:
                    other_questions.extend(v)
            random.shuffle(other_questions)
            pool.extend(other_questions[:count - len(pool)])

    # Select random sample
    selected = random.sample(pool, min(count, len(pool)))
    
    # Format for client delivery (ensure IDs and structured format)
    formatted_questions = []
    for idx, item in enumerate(selected, 1):
        formatted_questions.append({
            "id": idx,
            "category": category,
            "question": item["question"],
            "options": item["options"],
            "correct_index": item["correct_index"],
            "explanation": item["explanation"]
        })
        
    return formatted_questions

def grade_quiz_submission(submitted_answers, original_questions):
    """
    Validates answers submitted by the candidate.
    submitted_answers: dict of {question_id: selected_option_index}
    Returns score, percentage, and detailed question breakdown.
    """
    total = len(original_questions)
    correct_count = 0
    results = []

    for q in original_questions:
        q_id = str(q["id"])
        user_choice = submitted_answers.get(q_id)
        is_correct = (user_choice == q["correct_index"])
        
        if is_correct:
            correct_count += 1
            
        results.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "user_choice": user_choice,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    percentage = round((correct_count / max(1, total)) * 100, 1)
    
    # Performance assessment tier
    if percentage >= 80:
        tier = "UPSC Prelims Ready 🌟"
        tier_class = "success"
    elif percentage >= 60:
        tier = "Commended Current Affairs Grasp 🎯"
        tier_class = "info"
    elif percentage >= 40:
        tier = "Good Foundation (Revision Recommended) 📈"
        tier_class = "warning"
    else:
        tier = "Daily Reading Required 📚"
        tier_class = "danger"

    return {
        "score": correct_count,
        "total_questions": total,
        "percentage": percentage,
        "tier": tier,
        "tier_class": tier_class,
        "breakdown": results
    }
