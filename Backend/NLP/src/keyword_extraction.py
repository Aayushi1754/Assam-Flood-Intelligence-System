# ============================================================
# FloodSense: Static Multilingual Keyword Dictionary
# Languages: English, Hindi, Assamese, Romanized Hindi
# Categories: Food, Water, Medical, Rescue, Shelter
# ============================================================

KEYWORD_MATRIX = {
    "Food": {
        "Resource": "Food Supplies",
        "Keywords": {
            "EN": [
                "food", "need food", "no food", "food needed",
                "hungry", "starving", "ration", "food packets",
                "need groceries", "cooked food", "baby food",
                "food supplies", "no groceries", "meal needed",
                "we have nothing to eat",
                "dry ration", "food shortage", "food supply", "food kits",
"food kit", "cooked food", "no food", "food packets",
"food packet", "ration card", "flood-affected", "hungry",
"starving", "meal needed", "food needed"
            ],
            "HI": [
                "खाना", "भोजन", "खाना नहीं है", "भूख लगी है",
                "राशन चाहिए", "भोजन चाहिए", "खाने की जरूरत है",
                "खाने का सामान", "भूखे हैं", "बच्चों का खाना",
                "पका हुआ खाना", "खाने को कुछ नहीं है",
                "सूखा राशन", "खाद्य किट", "खाने के पैकेट",
"भोजन की कमी", "खाना नहीं", "अनाज",
"राहत वितरण", "राशन कार्ड", "भूखे",
"खाद्य सामग्री", "पका हुआ खाना"
            ],
            "AS": [
                "খাদ্য", "খোৱা", "খাবলৈ নাই", "ভোক লাগিছে",
                "খাদ্য লাগে", "চাউল লাগে", "খাদ্যৰ অভাৱ",
                "খাবলৈ একো নাই", "ৰেচন লাগে",
                "খাদ্য সামগ্ৰী লাগে","শুকান খাদ্য", "খাদ্য কিট", "খাদ্যৰ পেকেট",
"খাদ্যৰ অভাৱ", "খাদ্য নাই", "ৰেচন কাৰ্ড",
"খাদ্য যোগান", "ৰন্ধা খাদ্য", "ভোকত",
"ত্ৰাণ বিতৰণ"
            ],
            "Romanized_HI": [
                "khana chahiye", "khana nahi hai", "bhook lagi hai",
                "ration chahiye", "bhookhe hain", "bhojan chahiye",
                "khane ko kuch nahi hai", "khane ka saman chahiye"
            ]
        }
    },

    "Water": {
        "Resource": "Drinking Water",
        "Keywords": {
            "EN": [
                "water", "drinking water", "no drinking water",
                "need water", "need clean water", "clean water",
                "no safe water", "water shortage", "thirsty",
                "water bottles needed", "water tanker needed",
                "water contaminated", "water purification tablets",
                "safe drinking water", "no water available",
                "water level", "stable", "danger mark",
"water shortage", "chlorine tablets", "water cans",
"water tanker", "no safe drinking water",
"receding", "water under control", "tube wells",
"water supply", "water contaminated","drinking water","clean water"
            ],
            "HI": [
                "पानी", "पीने का पानी", "पीने का पानी नहीं है",
                "पानी चाहिए", "साफ पानी चाहिए", "प्यास लगी है",
                "पानी दूषित है", "पानी की बोतल चाहिए",
                "पानी का टैंकर चाहिए", "पानी की कमी है",
                "पीने के लिए पानी नहीं है", "स्वच्छ पानी चाहिए","जलस्तर", "स्थिर", "खतरे के निशान",
"पानी उतर रहा", "पानी के कैन", "हैंडपंप",
"क्लोरीन की गोलियां", "पानी का टैंकर",
"पीने का साफ पानी", "पानी की कमी"
            ],
            "AS": [
                "পানী", "খোৱা পানী নাই", "বিশুদ্ধ পানী লাগে",
                "পিয়াহ লাগিছে", "পানী দূষিত হৈছে",
                "পানীৰ বটল লাগে", "পানীৰ টেংকাৰ লাগে",
                "নিৰাপদ পানী নাই", "খোৱা পানী লাগে",
                "পানীৰ অভাৱ হৈছে","পানীৰ স্তৰ", "স্থিৰ", "বিপদসীমা",
"পানী নামি আছে", "পানীৰ কেন", "নলকূপ",
"ক্লৰিন বটিকা", "পানীৰ টেংকাৰ",
"খোৱা পানীৰ অভাৱ", "পানীৰ অভাৱ হৈছে"
            ],
            "Romanized_HI": [
                "pani chahiye", "pani nahi hai",
                "peene ka pani", "saaf pani chahiye",
                "pyaas lagi hai", "pani ki kami hai",
                "pani ganda hai", "pani ka tanker chahiye",
                "peene ke liye pani nahi hai"
            ]
        }
    },

    "Medical": {
        "Resource": "Medical supplies",
        "Keywords": {
            "EN": [
                "injured", "injury", "bleeding", "medical help",
                "need medicine", "medicine needed", "doctor needed",
                "ambulance", "sick", "seriously injured",
                "medical emergency", "first aid", "hospital",
                "pregnant woman", "snake bite", "fever",
                "cannot breathe", "medical supplies","urgent medical assistance", "breathing trouble",
"chest pain", "labour", "diarrhoea", "infection",
"medical team", "health check-up camp", "ORS",
"insulin", "medicines", "doctor", "fever",
"medical camp", "seriously injured"
            ],
            "HI": [
                "घायल", "चोट लगी है", "खून बह रहा है",
                "दवा चाहिए", "डॉक्टर चाहिए", "चिकित्सा सहायता",
                "एम्बुलेंस चाहिए", "बीमार हैं", "अस्पताल चाहिए",
                "प्राथमिक उपचार", "बुखार है", "सांस नहीं आ रही",
                "गर्भवती महिला", "सांप ने काट लिया",
                "गंभीर रूप से घायल","सीने में दर्द", "प्रसव पीड़ा", "दस्त",
"संक्रमण", "मेडिकल टीम", "स्वास्थ्य जांच शिविर",
"ओआरएस", "इंसुलिन", "दवाइयां",
"सांस लेने में तकलीफ", "उल्टी"
            ],
            "AS": [
                "আঘাত পাইছে", "আহত", "তেজ ওলাইছে",
                "ঔষধ লাগে", "ডাক্তৰ লাগে", "চিকিৎসা লাগে",
                "এম্বুলেন্স লাগে", "অসুস্থ", "হাস্পতাল লাগে",
                "জ্বৰ হৈছে", "উশাহ লোৱাত কষ্ট",
                "প্ৰাথমিক চিকিৎসা লাগে","বুকুত বিষ", "প্ৰসৱ বেদনা", "ডায়েৰিয়া",
"সংক্ৰমণ", "চিকিৎসক দল", "স্বাস্থ্য পৰীক্ষা শিবিৰ",
"ওআৰএছ", "ইনচুলিন", "ঔষধ", "জ্বৰ", "বমি"
            ],
            "Romanized_HI": [
                "chot lagi hai", "khoon beh raha hai",
                "dawai chahiye", "doctor chahiye",
                "ambulance chahiye", "bimar hain",
                "aspatal chahiye", "bukhar hai",
                "saans nahi aa rahi", "medical madad chahiye"
            ]
        }
    },

    "Rescue": {
        "Resource": "Rescue Team",
        "Keywords": {
            "EN": [
                "rescue", "need rescue", "trapped", "trapped in flood",
                "stranded", "drowning", "stuck in water",
                "rescue team", "boat needed", "people stranded",
                "stuck on roof", "cannot escape", "evacuate",
                "evacuation needed", "water rising",
                "family trapped", "rescue urgently","rescue boat", "rescue boats", "bridge", "road",
"embankment", "evacuate", "evacuation",
"higher ground", "rescued", "operations",
"rising", "monitoring", "flooded", "stuck",
"send help", "boat", "boats", "rescue team"
            ],
            "HI": [
                "बचाओ", "बचाव चाहिए", "फंसे हुए हैं",
                "बाढ़ में फंसे हैं", "पानी में फंसे हैं",
                "डूब रहे हैं", "नाव चाहिए", "बचाव दल चाहिए",
                "छत पर फंसे हैं", "निकालने में मदद करें",
                "पानी बढ़ रहा है", "परिवार फंसा हुआ है",
                "तुरंत बचाव चाहिए", "बाहर नहीं निकल पा रहे","नावें", "तटबंध", "बांध", "खाली करें",
"ऊंचे स्थान", "बचाव कार्य", "बचाव",
"पुल", "सड़क", "बढ़ रहा", "नियंत्रण",
"बाढ़ प्रभावित", "हेल्पलाइन"
            ],
            "AS": [
                "উদ্ধাৰ লাগে", "বানত আবদ্ধ", "পানীত আবদ্ধ",
                "আৱদ্ধ হৈ আছোঁ", "ডুব গৈছে",
                "নাও লাগে", "উদ্ধাৰকাৰী দল লাগে",
                "ঘৰৰ ছাদত আবদ্ধ", "পানী বাঢ়িছে",
                "বাহিৰলৈ ওলাব পৰা নাই","আটকা পৰি আছে", "আটকা পৰা", "উদ্ধাৰ কাৰ্য",
"বাঢ়ি আছে", "দলং", "ৰাস্তা", "খালী কৰক",
"ওখ ঠাই", "স্থানান্তৰ", "বান্ধ", "হেল্পলাইন",
"বিপদসীমা"
            ],
            "Romanized_HI": [
                "bachao", "madad karo", "bachav chahiye",
                "baadh mein fanse hain", "pani mein fanse hain",
                "doob rahe hain", "naav chahiye",
                "chhat par fanse hain", "nikalne mein madad karo",
                "pani badh raha hai", "rescue chahiye"
            ]
        }
    },

    "Shelter": {
        "Resource": "Shelter",
        "Keywords": {
            "EN": [
                "shelter", "need shelter", "homeless",
                "house flooded", "home destroyed", "roof collapsed",
                "temporary shelter", "place to stay",
                "need accommodation", "shelter needed",
                "camp needed", "no place to sleep",
                "house damaged", "lost my home", "evacuation center","relief camp", "blankets", "dry clothes",
"warm clothing", "tarpaulin", "temporary shelter",
"relief", "safe", "trucks", "flood-affected"
            ],
            "HI": [
                "आश्रय चाहिए", "रहने की जगह चाहिए",
                "घर में पानी भर गया", "घर टूट गया",
                "छत गिर गई", "घर नष्ट हो गया",
                "अस्थायी आश्रय चाहिए", "रहने की जगह नहीं है",
                "सोने की जगह नहीं है", "घर क्षतिग्रस्त है",
                "घर बह गया", "शरण चाहिए","राहत शिविर", "कंबल", "सूखे कपड़े",
"गर्म कपड़ों", "तिरपाल", "अस्थायी आश्रय",
"राहत", "सुरक्षित", "ट्रक"
            ],
            "AS": [
                "আশ্ৰয় লাগে", "থাকিবলৈ ঠাই লাগে",
                "ঘৰত পানী সোমাইছে", "ঘৰ ভাঙি গৈছে",
                "ঘৰৰ চাল খহি পৰিছে", "অস্থায়ী আশ্ৰয় লাগে",
                "থাকিবলৈ ঠাই নাই", "ঘৰ ক্ষতিগ্ৰস্ত হৈছে",
                "শুবলৈ ঠাই নাই", "ঘৰ উটি গৈছে","ত্ৰাণ শিবিৰ", "কম্বল", "শুকান কাপোৰ",
"গৰম কাপোৰ", "তেৰপাল", "অস্থায়ী আশ্ৰয়",
"ত্ৰাণ", "নিৰাপদ", "ট্ৰাক"
            ],
            "Romanized_HI": [
                "rehne ki jagah chahiye", "ghar mein pani bhar gaya",
                "ghar toot gaya", "chhat gir gayi",
                "aashray chahiye", "sone ki jagah nahi hai",
                "ghar beh gaya", "ghar kharab ho gaya",
                "rehne ki jagah nahi hai"
            ]
        }
    }
}
def classify_relief_need(text):
    keywords_found = extract_keywords_independent(text)

    matched_categories = []
    matched_resources = []

    # Find categories only from keywords actually detected.
    for category, category_data in KEYWORD_MATRIX.items():

        category_keywords = []

        for language, keywords in category_data["Keywords"].items():
            category_keywords.extend(keywords)

        matched = [
            keyword
            for keyword in keywords_found
            if keyword in category_keywords
        ]

        if matched:
            matched_categories.append(category)
            matched_resources.append(category_data["Resource"])

    return {
        "keywords": keywords_found,
        "categories": matched_categories,
        "resources": list(dict.fromkeys(matched_resources))
    }
def remove_overlapping_keywords(keywords):
    # Remove duplicates while preserving order.
    keywords = list(dict.fromkeys(keywords))

    filtered_keywords = []

    for keyword in keywords:
        # Skip a keyword if it is contained in a longer
        # matched keyword.
        is_overlapping = any(
            keyword.casefold() in other.casefold()
            and keyword.casefold() != other.casefold()
            for other in keywords
        )

        if not is_overlapping:
            filtered_keywords.append(keyword)

    return filtered_keywords
import re


def extract_keywords_independent(text):
    if not isinstance(text, str) or not text.strip():
        return []

    found_keywords = []
    normalized_text = text.casefold()

    for category, category_data in KEYWORD_MATRIX.items():
        for language, keywords in category_data["Keywords"].items():
            for keyword in keywords:
                keyword_normalized = keyword.casefold()

                # ASCII keywords use boundaries to avoid matching
                # substrings inside unrelated words.
                if keyword.isascii():
                    pattern = (
                        r"(?<!\w)"
                        + re.escape(keyword_normalized)
                        + r"(?!\w)"
                    )
                    matched = re.search(pattern, normalized_text)
                else:
                    matched = keyword_normalized in normalized_text

                if matched:
                    found_keywords.append(keyword)

    # Remove duplicate matches while preserving order.
    return remove_overlapping_keywords(found_keywords)
import re

def extract_people_affected(text: str) -> int:
    """
    Extract the estimated number of people affected from a flood message.
    Returns 0 when no count can be identified.
    """
    if not isinstance(text, str) or not text.strip():
        return 0

    patterns = [
        r"\b(\d[\d,]*)\s+(?:people|persons|families|residents|villagers|individuals|flood victims|victims|)\b",
        r"\b(\d[\d,]*)\s+(?:लोग|परिवार|व्यक्ति)\b",
        r"\b(\d[\d,]*)\s+(?:লোক|জন|পৰিয়াল|পৰিয়াল)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except ValueError:
                continue

    return 0