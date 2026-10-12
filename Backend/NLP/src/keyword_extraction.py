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

    # Code-mixed Roman Hindi
    "khatam ho gaya hai", "shelter taiyaar hai",
    "boats se nikala jayega", "bacchon aur bimar logon",
    "bujurgon", "khana", "paani",
    "road band", "road bandh", "bandh",
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


# ------------------------------------------
# Run keyword extraction
# ------------------------------------------

def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}\n"
            "Check the CSV filename and dataset folder."
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = {"Image_Name", "Language", "Original_Text"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {missing_columns}"
        )

    df["Preprocessed_Text"] = (
        df["Original_Text"]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df["Independent_Extracted_Keywords"] = (
        df["Preprocessed_Text"]
        .apply(extract_keywords_independent)
    )

    df["Filtered_Keywords"] = (
        df["Independent_Extracted_Keywords"]
        .apply(remove_overlapping_keywords)
    )

    output_df = df[
        [
            "Image_Name",
            "Language",
            "Original_Text",
            "Preprocessed_Text",
            "Independent_Extracted_Keywords",
            "Filtered_Keywords",
        ]
    ].copy()
    if "Expected_Keywords" in df.columns:
        evaluate_keywords(df)
    else:
        print("Expected_Keywords not found; skipping evaluation.")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("Keyword extraction completed successfully.")
    print(f"Records processed: {len(output_df)}")
    print(f"Output saved to: {OUTPUT_PATH}")

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