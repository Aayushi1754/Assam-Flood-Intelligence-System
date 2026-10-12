"""
FloodSense: Multilingual Urgency Scoring
Languages: English, Hindi, Assamese, and Roman Hindi.

Uses predefined category weights and critical-emergency overrides.
"""

import re


# ==================================================
# 1. PREDEFINED URGENCY CATEGORIES
# ==================================================

URGENCY_CATEGORIES = {
    "rescue_emergency": {
        "weight": 5,
        "keywords": [
            # English
            "trapped", "stranded", "stuck at home",
            "immediate rescue", "people trapped",

            # Hindi
            "फँसे हुए", "फँसे", "फंसे हुए", "फंसे",
            "बचाव दल", "मदद कीजिए",

            # Assamese
            "আবদ্ধ", "আৱদ্ধ", "উদ্ধাৰ দল",
            "নাৱেৰে উদ্ধাৰ",

            # Roman Hindi
            "madad chahiye", "log fase hue",
            "bachao", "rescue chahiye",
        ],
    },

    "medical_emergency": {
        "weight": 5,
        "keywords": [
            # English
            "pregnant woman", "in labour", "in labor",
            "medical emergency", "urgent medical assistance",
            "high fever", "injured", "ambulance needed",

            # Hindi
            "गर्भवती महिला", "प्रसव पीड़ा",
            "तेज़ बुखार", "बहुत तेज़ बुखार",
            "घायल", "डॉक्टर चाहिए", "चिकित्सा सहायता",

            # Assamese
            "আহত", "চিকিৎসা", "চিকিৎসক",
            "এম্বুলেন্স", "জৰুৰী চিকিৎসা",

            # Roman Hindi
            "garbhvati mahila", "tez bukhar",
            "doctor chahiye", "dawai chahiye",
        ],
    },

    "evacuation": {
        "weight": 4,
        "keywords": [
            # English
            "evacuation", "evacuate", "rescue boat",
            "boat ambulance", "water is still rising",
            "rising water", "road is flooded",
            "two bridges are flooded",

            # Hindi
            "निकासी", "सुरक्षित स्थान",
            "नाव", "नावों", "पानी लगातार बढ़ रहा है",
            "सड़क पर पानी भरा है",

            # Assamese
            "নাৱেৰে উদ্ধাৰ", "নাৱেৰে",
            "পানী দ্ৰুতগতিত বাঢ়িছে",
            "ৰাস্তা পানীত ডুবি",

            # Roman Hindi
            "nikasi", "surakshit jagah",
            "paani badh raha hai", "road band",
            "boat se nikala jayega",
        ],
    },

    "essential_supplies": {
        "weight": 3,
        "keywords": [
            # English
            "drinking water", "food packets",
            "food packet", "no food or drinking water",
            "medicines", "medicine", "water tankers",
            "shortage",

            # Hindi
            "पीने का पानी", "खाने के पैकेट",
            "भोजन के पैकेट", "पानी के टैंकर",
            "दवाइयाँ", "भोजन", "खाना",

            # Assamese
            "খোৱাপানী", "খাদ্যৰ পেকেট",
            "খাদ্য", "পানী", "শেষ হৈছে",

            # Roman Hindi
            "paani", "khana", "food packets",
            "khana khatam ho gaya hai",
        ],
    },

    "shelter_relief": {
        "weight": 2,
        "keywords": [
            # English
            "relief camp", "temporary shelter",
            "shelter", "blankets", "warm clothes",
            "tarpaulin",

            # Hindi
            "राहत शिविर", "अस्थायी आश्रय",
            "कंबल", "तिरपाल", "कपड़े",

            # Assamese
            "ত্ৰাণ শিবিৰ", "নিৰাপদ স্থান",
            "কম্বল", "গৰম কাপোৰ", "শিশুৰ কাপোৰ",

            # Roman Hindi
            "rahat shivir", "kambal",
            "kapde chahiye", "shelter taiyaar hai",
        ],
    },

    "general_information": {
        "weight": 1,
        "keywords": [
            # English
            "flood update", "water level",
            "flood situation", "river level",

            # Hindi
            "बाढ़ की जानकारी", "जलस्तर",
            "बाढ़ की स्थिति",

            # Assamese
            "বানপানীৰ খবৰ", "পানীৰ স্তৰ",
            "বানপানীৰ পৰিস্থিতি",

            # Roman Hindi
            "baadh ki jankari", "paani ka star",
        ],
    },
}


# ==================================================
# 2. CRITICAL EMERGENCY OVERRIDES
# ==================================================

CRITICAL_RESCUE_KEYWORDS = [
    "trapped", "stranded", "stuck at home",
    "immediate rescue", "फँसे हुए", "फँसे",
    "फंसे हुए", "फंसे", "আবদ্ধ", "আৱদ্ধ",
    "log fase hue", "bachao",
]

CRITICAL_MEDICAL_KEYWORDS = [
    "in labour", "in labor", "medical emergency",
    "urgent medical assistance", "गर्भवती महिला",
    "प्रसव पीड़ा", "बहुत तेज़ बुखार",
    "আহত", "জৰুৰী চিকিৎসা",
    "garbhvati mahila",
]


# ==================================================
# 3. TEXT MATCHING
# ==================================================

def contains_phrase(text, phrase):
    """Match a phrase without case sensitivity."""
    text = text.casefold().strip()
    phrase = phrase.casefold().strip()

    if not text or not phrase:
        return False

    if phrase.isascii():
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        return re.search(pattern, text) is not None

    return phrase in text


# ==================================================
# 4. CATEGORY DETECTION
# ==================================================

def detect_urgency_categories(text):
    """Identify urgency categories present in a message."""
    if not isinstance(text, str) or not text.strip():
        return []

    matched = []

    for category, details in URGENCY_CATEGORIES.items():
        if any(
            contains_phrase(text, keyword)
            for keyword in details["keywords"]
        ):
            matched.append(category)

    return matched


# ==================================================
# 5. URGENCY SCORING
# ==================================================

def calculate_urgency(text):
    """
    Calculate a score from 1 to 5.

    Critical rescue or medical keywords trigger score 5.
    Otherwise, calculate the average weight of matched categories.
    """

    if not isinstance(text, str) or not text.strip():
        return {
            "urgency_score": 1.0,
            "urgency_level": "Informational",
            "matched_categories": [],
        }

    matched_categories = detect_urgency_categories(text)

    critical_keywords = (
        CRITICAL_RESCUE_KEYWORDS
        + CRITICAL_MEDICAL_KEYWORDS
    )

    critical_match = any(
        contains_phrase(text, keyword)
        for keyword in critical_keywords
    )

    if critical_match:
        score = 5.0

    elif matched_categories:
        weights = [
            URGENCY_CATEGORIES[category]["weight"]
            for category in matched_categories
        ]

        score = sum(weights) / len(weights)

    else:
        score = 1.0

    if score >= 4.5:
        level = "Critical"
    elif score >= 3.5:
        level = "High"
    elif score >= 2.5:
        level = "Medium"
    elif score >= 1.5:
        level = "Low"
    else:
        level = "Informational"

    return {
        "urgency_score": round(score, 2),
        "urgency_level": level,
        "matched_categories": matched_categories,
    }


# ==================================================
# 6. BASIC MULTILINGUAL TESTS
# ==================================================

if __name__ == "__main__":

    test_messages = [
        "People are trapped on rooftops and need immediate rescue.",
        "गर्भवती महिला को प्रसव पीड़ा हो रही है।",
        "আহত লোকক চিকিৎসাৰ প্ৰয়োজন।",
        "We urgently need drinking water and food packets.",
        "कृपया राहत शिविर में कंबल भेजें।",
        "বানপানীৰ খবৰ আৰু পানীৰ স্তৰ পৰীক্ষা কৰা হৈছে।",
        "Paani aur khana chahiye.",
        "The river level is being monitored.",
    ]

    print("\nFloodSense Multilingual Urgency Tests")
    print("=" * 55)

    for message in test_messages:
        result = calculate_urgency(message)

        print(f"\nMessage: {message}")
        print(f"Score: {result['urgency_score']}")
        print(f"Level: {result['urgency_level']}")
        print(f"Categories: {result['matched_categories']}")