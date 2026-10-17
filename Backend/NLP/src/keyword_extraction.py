import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT / "dataset" / "FloodSense_Dataset_Ground_Truth.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "results" / "FloodSense_Keyword_Extraction_Results.csv"
)


# ------------------------------------------
# Multilingual keyword dictionary
# ------------------------------------------

KEYWORD_PHRASES = [
    # English: water, food and supplies
    "no food or drinking water", "drinking water",
    "food packets", "food packet", "blankets",
    "warm clothes", "baby clothing", "wet clothes",
    "water tankers", "water tank", "shortage",

    # English: rescue and evacuation
    "road to the clinic is under water",
    "rescue boat", "boat ambulance", "boat assistance",
    "two boats", "three boats", "boats", "boat",
    "ambulance", "rescue team", "rescue",
    "evacuate", "evacuation", "stranded", "trapped",
    "stuck at home", "rooftop", "relief camp",
    "temporary shelter", "shelter", "tarpaulin",

    # English: people and medical needs
    "elderly and disabled", "pregnant woman",
    "women and children", "two small children",
    "medical assistance", "medical team", "medical camp",
    "in labour", "high fever", "doctors", "doctor",
    "medicines", "medicine", "injured", "elderly",
    "children", "baby", "people", "buses", "trucks",
    "food", "help", "urgent", "emergency",

    # English: flood conditions and infrastructure
    "water is still rising", "under waist-deep water",
    "two bridges are flooded", "road is flooded",
    "road is under water", "rising water",
    "low-lying lanes", "danger mark", "water level",
    "high water", "flooded", "flood", "river",
    "collapsed",

    # Hindi
    "गर्भवती महिला", "प्रसव पीड़ा",
    "पीने का पानी", "खाने के पैकेट", "भोजन के पैकेट",
    "राहत सामग्री", "राहत शिविर", "अस्थायी आश्रय",
    "बचाव दल", "नावों से निकाला जाएगा",
    "नावों", "नाव", "फँसे हुए", "फँसे",
    "मदद कीजिए", "बुज़ुर्गों", "बुज़ुर्ग",
    "बहुत तेज़ बुखार", "तेज़ बुखार",
    "सड़क पर पानी भरा है", "मुख्य पुल पानी में डूबा है",
    "पानी लगातार बढ़ रहा है", "पानी के टैंकर",
    "खत्म हो गया है", "निकासी", "सुरक्षित स्थान",
    "बेघर", "तिरपाल", "कंबल", "कपड़े",
    "जो लोग चल नहीं सकते", "डॉक्टर", "दवाइयाँ",
    "बच्चों", "बच्चे", "भोजन", "बाढ़", "पानी", "बचाव",
    "फँस गए", "फँस गए हैं",
    "फंस गए", "फंस गए हैं",
    "रेस्क्यू", "रेस्क्यू बोट",
    "रेस्क्यू बोट की जरूरत",
    "बचाने के लिए", "बचाने की जरूरत",
    "जरूरत है", "की जरूरत है",
    "लोग फँस गए", "लोग फंस गए",
    # Assamese
    "খোৱাপানী", "খাদ্যৰ পেকেট", "খাদ্য",
    "উদ্ধাৰ দল", "নাৱেৰে উদ্ধাৰ", "নাৱেৰে",
    "নিৰাপদ স্থান", "ত্ৰাণ শিবিৰ", "কম্বল",
    "গৰম কাপোৰ", "শিশুৰ কাপোৰ", "যোগাযোগ বন্ধ",
    "ৰাস্তা পানীত ডুবি", "পানী দ্ৰুতগতিত বাঢ়িছে",
    "বানৰ পানী ঘৰলৈ সোমাইছে", "শেষ হৈছে",
    "আহত", "চিকিৎসা", "চিকিৎসক", "এম্বুলেন্স",
    "বৃদ্ধ", "শিশু", "ভোকত", "বিতৰণ",
    "জৰুৰী", "নিৰুদ্দেশ", "পানী", "বানপানী",
    "আবদ্ধ", "আৱদ্ধ", "উদ্ধাৰ", "নাৱ", "নাও",
    "লোক আবদ্ধ হৈ আছে",
    "লোক আৱদ্ধ হৈ আছে",
    "উদ্ধাৰ কৰিবলৈ",
    "উদ্ধাৰ কৰিবলৈ নাওৰ প্ৰয়োজন",
    "নাওৰ প্ৰয়োজন",
    "নাওৰ প্ৰয়োজন",
    "উদ্ধাৰৰ প্ৰয়োজন",
    "উদ্ধাৰৰ প্ৰয়োজন",

    # Code-mixed Roman Hindi
    "khatam ho gaya hai", "shelter taiyaar hai",
    "boats se nikala jayega", "bacchon aur bimar logon",
    "bujurgon", "khana", "paani",
    "road band", "road bandh", "bandh",
    "log fase gaye hain",
    "log phanse hue hain",
    "rescue boat chahiye",
    "rescue boat ki zarurat hai",
    "bachane ke liye",
    "naav ki zarurat hai",
    "madad ki zarurat hai",
]

KEYWORD_PHRASES = list(dict.fromkeys(KEYWORD_PHRASES))


# ------------------------------------------
# Keyword extraction
# ------------------------------------------

def extract_keywords_independent(text):
    """Extract dictionary-based flood-related keyword phrases."""

    if not isinstance(text, str) or not text.strip():
        return []

    normalized_text = text.casefold()
    matches = []

    for phrase in KEYWORD_PHRASES:
        normalized_phrase = phrase.casefold()

        if phrase.isascii():
            pattern = (
                r"(?<!\w)"
                + re.escape(normalized_phrase)
                + r"(?!\w)"
            )
        else:
            pattern = re.escape(normalized_phrase)

        if re.search(pattern, normalized_text):
            matches.append(phrase)

    return matches


# ------------------------------------------
# Remove overlapping keyword matches
# ------------------------------------------

def remove_overlapping_keywords(keywords):
    """Keep longer phrases when they contain shorter matches."""

    sorted_keywords = sorted(
        set(keywords),
        key=len,
        reverse=True
    )

    filtered_keywords = []

    for keyword in sorted_keywords:
        keyword_lower = keyword.casefold()

        is_redundant = any(
            keyword_lower in existing.casefold()
            and keyword_lower != existing.casefold()
            for existing in filtered_keywords
        )

        if not is_redundant:
            filtered_keywords.append(keyword)

    return filtered_keywords

def classify_relief_need(text):
    """Classify the primary assistance need, avoiding informational false positives."""

    if not isinstance(text, str) or not text.strip():
        return "Flood assistance"

    text = text.casefold()

    # Detect messages that only provide routine information.
    informational_phrases = [
        "no immediate evacuation",
        "no evacuation is needed",
        "no rescue is needed",
        "routine flood information update",
        "river level is being monitored",
        "water levels are stable",
        "নদীৰ পানীৰ স্তৰ বৃদ্ধি পাইছে",
        "জলস্তৰ বৃদ্ধি পাইছে",
        "জলস্তৰ বাঢ়ি",
    ]

    if any(phrase in text for phrase in informational_phrases):
        return "Flood assistance"

    categories = {
        "Rescue": [
            "rescue", "trapped", "stranded", "evacuate",
            "evacuation", "boat", "boats",
            "बचाव", "फँसे", "फंसे", "फँस", "फंसा",
            "रेस्क्यू", "नाव", "नौका",
            "उद्धार", "আবদ্ধ", "আৱদ্ধ", "উদ্ধাৰ",
            "নাও", "ৰেচকিউ",
            "boats se nikala jayega",
        ],

        "Medical": [
            "medical", "medicine", "medicines", "doctor",
            "ambulance", "injured", "fever",
            "चिकित्सा", "डॉक्टर", "दवाइयाँ",
            "চিকিৎসা", "চিকিৎসক", "আহত",
        ],

        "Food": [
            "food", "hungry", "meal", "food packet",
            "food packets", "खाना", "भोजन",
            "খাদ্য", "ভোকত", "khana",
        ],

        "Shelter": [
            "shelter", "blanket", "blankets", "tarpaulin",
            "relief camp", "কंबल", "कंबल",
            "राहत शिविर", "আশ্ৰয়", "আশ্রয়",
            "কম্বল", "ত্ৰাণ শিবিৰ", "গৃহহীন",
        ],
            "Water": [
    # English
    "drinking water",
    "clean water",
    "water supply",
    "water shortage",
    "water tanker",
    "water tank",

    # Hindi
    "पीने का पानी",
    "पीने का साफ पानी",
    "साफ पानी",
    "स्वच्छ पानी",
    "पानी नहीं मिल रहा",
    "पानी की कमी",
    "जल की कमी",

    # Assamese
    "খোৱাপানী",
    "খোৱা পানী",
    "খোৱা পানীৰ",
    "খোৱাৰ পানী",
    "খোৱাপানীৰ প্ৰয়োজন",
    "খোৱাপানীৰ প্ৰয়োজন",

    # Roman Hindi
    "paani",
    "saaf pani",
    "peene ka paani",
    "peene ka saaf paani",
    "paani nahi mil raha",
    "paani ki kami",
],
    }

    priority_order = [
        "Rescue",
        "Medical",
        "Food",
        "Shelter",
        "Water",
    ]

    for category in priority_order:
        if any(keyword in text for keyword in categories[category]):
            return category

    return "Flood assistance"
def extract_people_affected(text):
    """Extract affected-person or family counts from English, Hindi,
    Assamese, and Roman Hindi."""

    if not isinstance(text, str) or not text.strip():
        return 0

    # Convert Hindi and Assamese digits to ASCII digits.
    digit_map = str.maketrans(
        "०१२३४५६७८९০১২৩৪৫৬৭৮৯",
        "01234567890123456789"
    )
    text = text.translate(digit_map)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    # Numeric counts, including language-specific suffixes and word order.
    patterns = [
        # English: 30 people, 12 families, 8 injured flood victims
        r"\b(\d+)\s+(?:people|persons|families|victims)\b",
        r"\b(\d+)\s+injured\s+(?:flood\s+)?victims\b",
        r"\b(\d+)\s+(?:injured|affected)\s+people\b",

        # Hindi: 15 लोगों, 20 परिवार, 9 लोग घायल
        r"(\d+)\s*(?:लोगों|लोग|व्यक्ति|व्यक्तियों|परिवारों|परिवार|पीड़ितों|पीड़ित)\b",

        # Assamese: 10 জন, 18 জন লোক, 20টা পৰিয়াল, 20 পৰিয়াল
        r"(\d+)\s*(?:টা\s*)?(?:জন|লোক|পৰিয়াল|পৰিয়াল|ভুক্তভোগী)\b",

        # Roman Hindi: 20 log, 15 logon, 10 parivar
        r"\b(\d+)\s*(?:logon|log|logo|vyakti|parivar|parivaar)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))

    # English number words: twenty-five people, thirty families.
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
        "ninety": 90,
    }

    word_pattern = (
        r"\b(" + "|".join(number_words) +
        r")(?:[- ](" + "|".join(number_words) +
        r"))?\s+(?:people|persons|families|victims)\b"
    )

    match = re.search(word_pattern, text, flags=re.IGNORECASE)

    if match:
        first = number_words[match.group(1).lower()]
        second = match.group(2)

        if second:
            second_value = number_words[second.lower()]
            if first >= 20 and first % 10 == 0 and second_value < 10:
                return first + second_value

        return first

    return 0

def evaluate_keywords(df):
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for _, row in df.iterrows():
        expected = {
            k.strip().casefold()
            for k in str(row["Expected_Keywords"]).split(";")
            if k.strip() and k.strip().casefold() != "nan"
        }

        predicted = {
            str(k).strip().casefold()
            for k in row["Filtered_Keywords"]
            if str(k).strip()
        }

        total_tp += len(expected & predicted)
        total_fp += len(predicted - expected)
        total_fn += len(expected - predicted)

    precision = (
        total_tp / (total_tp + total_fp)
        if total_tp + total_fp else 0
    )

    recall = (
        total_tp / (total_tp + total_fn)
        if total_tp + total_fn else 0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    print("\nKeyword Extraction Evaluation")
    print("-----------------------------")
    print(f"True Positives:  {total_tp}")
    print(f"False Positives: {total_fp}")
    print(f"False Negatives: {total_fn}")
    print(f"Precision:       {precision:.2%}")
    print(f"Recall:          {recall:.2%}")
    print(f"F1-score:        {f1_score:.2%}")
if __name__ == "__main__":
    main()