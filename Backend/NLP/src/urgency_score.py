import re
from .keyword_extraction import extract_keywords_independent
URGENCY_CATEGORIES = {
    "rescue_emergency": {
        "weight": 4,
        "keywords": [
            # English
            "trapped", "stranded", "stuck at home",
            "immediate rescue", "people trapped","urgent_rescue","need urgent rescue","severe flooding","water has entered house","people need rescue",

            # Hindi
            "फँसे हुए", "फँसे", "फंसे हुए", "फंसे",
            "बचाव दल","फँस गए", "फंस गए",
            "बचाने के लिए", "रेस्क्यू बोट",
            "तुरंत बचाव", "बचाव की जरूरत",

            # Assamese
            "আবদ্ধ", "আৱদ্ধ", "উদ্ধাৰ দল",
            "নাৱেৰে উদ্ধাৰ",

            # Roman Hindi
            "madad chahiye", "log fase hue",
            "bachao", "rescue chahiye",
        ],
    },

    "medical_emergency": {
        "weight": 4,
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
            "আহত","এম্বুলেন্স", "জৰুৰী চিকিৎসা",

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
            "shortage","no safe drinking water","no drinking water","need clean water immediately",

            # Hindi
            "पीने का पानी", "खाने के पैकेट",
            "भोजन के पैकेट", "पानी के टैंकर",
            "दवाइयाँ", "भोजन", "खाना","साफ पानी नहीं मिल रहा",
"पीने का साफ पानी नहीं मिल रहा",

            # Assamese
            "খোৱাপানী", "খাদ্যৰ পেকেট",
            "খাদ্য", "শেষ হৈছে",
            "খোৱা পানীৰ প্ৰয়োজন",
"খোৱাপানীৰ প্ৰয়োজন",
"খোৱা পানীৰ প্ৰয়োজন",
"খোৱাপানীৰ প্ৰয়োজন",

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
CRITICAL_RESCUE_KEYWORDS = [
    "trapped", "stranded", "stuck at home",
    "immediate rescue", "फँसे हुए", "फँसे",
    "फंसे हुए", "फंसे", "আবদ্ধ", "আৱদ্ধ",
    "log fase hue", "bachao","फँस गए", "फंस गए",
    "रेस्क्यू बोट",
    "तुरंत बचाव", 
]

CRITICAL_MEDICAL_KEYWORDS = [
    "in labour", "in labor", "medical emergency",
    "urgent medical assistance", "गर्भवती महिला",
    "प्रसव पीड़ा", "बहुत तेज़ बुखार",
    "আহত", "জৰুৰী চিকিৎসা",
    "garbhvati mahila",
]

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

def is_non_emergency_update(text):
    """Identify messages that explicitly describe a non-emergency."""

    text = text.casefold()

    non_emergency_phrases = [
        # English
        "no evacuations are needed",
        "no evacuation is needed",
        "no evacuation is required",
        "no immediate evacuation",
        "evacuation is not needed",
        "evacuation is not required",
        "no rescue is needed",
        "no immediate danger",
        "water levels are stable",
        "water level is stable",
        "river level is stable",
        "routine flood update",
        "routine flood information update",
        "no rescue needed",
        "everyone is safe",

        # Hindi
        "निकासी की आवश्यकता नहीं है",
        "निकासी की जरूरत नहीं है",
        "तत्काल निकासी की जरूरत नहीं है",
        "जलस्तर स्थिर है",
        "पानी का स्तर स्थिर है",
        "कोई तत्काल खतरा नहीं है",

        # Assamese
        "উদ্ধাৰৰ প্ৰয়োজন নাই",
        "উদ্ধাৰৰ প্ৰয়োজন নাই",
        "পানীৰ স্তৰ স্থিৰ",
        "জলস্তৰ স্থিৰ",
        "কোনো তাৎক্ষণিক বিপদ নাই",
    ]

    return any(
        contains_phrase(text, phrase)
        for phrase in non_emergency_phrases
    )
def calculate_urgency(text):
    """Calculate urgency from 1 to 5 using categories and message context."""

    if not isinstance(text, str) or not text.strip():
        return {
            "urgency_score": 1.0,
            "urgency_level": "Informational",
            "matched_categories": [],
        }

    matched_categories = detect_urgency_categories(text)
    normalized_text = text.casefold()

    # Detect a genuine emergency before applying a non-emergency rule.
    genuine_emergency_phrases = [
        # English
        "people are trapped",
        "people remain trapped",
        "trapped on rooftops",
        "stranded people",
        "immediate rescue",
        "urgent rescue",
        "rescue boat needed",
        "ambulance needed",
        "medical emergency",
        "evacuate immediately",
        "mandatory evacuation",

        # Hindi
        "लोग फँसे हुए हैं",
        "लोग फंसे हुए हैं",
        "तुरंत बचाव",
        "रेस्क्यू बोट चाहिए",
        "तत्काल चिकित्सा सहायता",

        # Assamese
        "লোক আবদ্ধ হৈ আছে",
        "লোক আৱদ্ধ হৈ আছে",
        "উদ্ধাৰ দল",
        "জৰুৰী চিকিৎসা",
    ]

    has_genuine_emergency = any(
        contains_phrase(normalized_text, phrase)
        for phrase in genuine_emergency_phrases
    )

    if (
        is_non_emergency_update(normalized_text)
        and not has_genuine_emergency
    ):
        return {
            "urgency_score": 1.0,
            "urgency_level": "Informational",
            "matched_categories": matched_categories,
        }
    normalized_text = text.casefold()

    # Start with the average weight of matched categories.
    if matched_categories:
        normalized_text = text.casefold()

    planned_phrases = [
        # English
        "will be distributed",
        "distribution on saturday",
        "scheduled relief distribution",
        "relief distribution",
        "relief camp will be held",
        "medical camp",

        # Hindi
        "बाँटे जाएँगे",
        "बांटे जाएंगे",
        "राहत शिविर सूचना",
        "शनिवार सुबह",

        # Assamese
        "বিতৰণ কৰা হ'ব",
        "ত্ৰাণ বিতৰণৰ বিজ্ঞপ্তি",
    ]

    is_planned = any(
        phrase in normalized_text
        for phrase in planned_phrases
    )

    if matched_categories:
        weights = [
            URGENCY_CATEGORIES[category]["weight"]
            for category in matched_categories
        ]

        priority_categories = {
            "rescue_emergency",
            "medical_emergency",
            "evacuation",
        }

        has_priority_category = any(
            category in priority_categories
            for category in matched_categories
        )

        if is_planned:
            score=2.0
        elif has_priority_category:
            score = max(weights)
        else:
            score = sum(weights) / len(weights)
    else:
        score = 1.0

    # Context indicating that the situation is currently safe.
    safe_phrases = [
        "everyone is safe",
        "everyone safe",
        "no ambulance is needed",
        "no ambulance needed",
        "no one is injured",
        "no injuries",
        "sab safe hain",
        "koi injured nahi",
        "koi ghayal nahi",
    ]

    # Context indicating a planned activity rather than an active emergency.
    planned_phrases = [
        "scheduled relief distribution",
        "relief distribution on saturday",
        "planned relief distribution",
        "scheduled medical camp",
        "free medical camp",
        "distribution will take place",
        "relief camp will be held",
    ]

    # Context indicating an immediate emergency.
    immediate_phrases = [
        "trapped",
        "stranded",
        "needs immediate rescue",
        "urgent rescue",
        "ambulance needed",
        "medical emergency",
        "evacuate immediately",
        "mandatory evacuation",
        "evacuate before",
        "rescue by",
        "boat needed immediately",
        "must evacuate",
        "must leave",
        "danger mark",
        "water level above danger",
        "urgent_rescue",
        "need urgent rescue",
        "severe flooding",
        "water has entered house",
        "people need rescue",
        # Hindi
        "निकासी सूचना",
        "खतरे के निशान से ऊपर",
        "स्थानांतरित होना होगा",
        "सुरक्षित स्थान पर पहुँचें",
        "नावों से निकाला जाएगा",

        # Assamese
        "বিপদসীমাৰ ওপৰত",
        "স্থানান্তৰৰ নিৰ্দেশ",
        "নিৰাপদ স্থানলৈ স্থানান্তৰ",
        "নাৱেৰে উদ্ধাৰ কৰা হ'ব",

        # Roman Hindi
        "turant evacuation",
        "danger mark se upar",
        "sabhi log",
        "pehle boats se nikala jayega",
        "boat bhejiye",
    ]

    is_safe = any(
        phrase in normalized_text for phrase in safe_phrases
    )

    is_planned = any(
        phrase in normalized_text for phrase in planned_phrases
    )

    is_immediate = any(
        phrase in normalized_text for phrase in immediate_phrases
    )

    # Planned activities should not be classified as emergencies
    # merely because they mention relief, food, or medical services.
    if is_planned and not is_immediate:
        score = min(score, 2.0)

    # When everyone is safe and no immediate emergency is reported,
    # reduce urgency slightly rather than treating supply requests
    # as active rescue emergencies.
    elif is_safe and not is_immediate:
        score = min(score, 3.0)

    # Convert the numerical score to an urgency level.
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

def analyze_flood_message(text):
    if not isinstance(text, str) or not text.strip():
        return{
            "extracted_keywords":[],
            "urgency_score": 1.0,
            "urgency_level": "Informational",
            "matched_categories": [],
        }
    extracted_keywords=extract_keywords_independent(text)
    urgency_result=calculate_urgency(text)

    return {
        "extracted_keywords": extracted_keywords,
        "urgency_score": urgency_result["urgency_score"],
        "urgency_level": urgency_result["urgency_level"],
        "matched_categories": urgency_result["matched_categories"],
    }

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
        "Flood update: water levels are stable today, and no evacuations are needed.",

"Twenty people are trapped on rooftops and urgently need rescue boats.",

"Water levels are stable, but 10 people remain trapped on a rooftop.",

"The river level is being monitored, and officials have issued a routine flood information update.",
    ]

    print("\nFloodSense Integrated Analysis")
    print("=" * 55)

    for message in test_messages:
        result = analyze_flood_message(message)

        print(f"\nMessage: {message}")
        print(f"Extracted Keywords: {result['extracted_keywords']}")
        print(f"Urgency Score: {result['urgency_score']}")
        print(f"Urgency Level: {result['urgency_level']}")
        print(f"Matched Categories: {result['matched_categories']}")