from pathlib import Path
import pandas as pd
import re
from difflib import SequenceMatcher

from ocr import adaptive_ocr


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_DIR = PROJECT_ROOT / "Backend" / "NLP" / "Dataset"
RESULTS_DIR = PROJECT_ROOT / "Backend" / "NLP" / "Results"

GROUND_TRUTH_FILE = DATASET_DIR / "FloodSense_Dataset_Ground_Truth.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(text):
    """Normalize text before comparing OCR output with ground truth."""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similarity_score(predicted_text, expected_text):
    """Calculate character-sequence similarity as a percentage."""
    predicted_text = normalize_text(predicted_text)
    expected_text = normalize_text(expected_text)

    return (
        SequenceMatcher(
            None,
            predicted_text,
            expected_text
        ).ratio() * 100
    )


def main():
    if not GROUND_TRUTH_FILE.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {GROUND_TRUTH_FILE}"
        )

    ground_truth = pd.read_csv(GROUND_TRUTH_FILE)

    required_columns = {"Image_Name", "Original_Text"}
    missing_columns = required_columns - set(ground_truth.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    results = []

    for _, row in ground_truth.iterrows():
        image_name = str(row["Image_Name"])
        image_path = DATASET_DIR / image_name
        expected_text = str(row["Original_Text"])

        if not image_path.exists():
            print(f"Skipping missing image: {image_name}")
            continue

        language_options = {
            "EN": ["eng"],
            "HI": ["hin"],
            "AS": ["asm"],
            "CM": ["eng+hin", "hin+eng"],
        }

        name_upper = image_name.upper()

        if "_AS_EN_" in name_upper:
            languages = ["eng+asm", "asm+eng"]
        elif "_CM_" in name_upper:
            languages = language_options["CM"]
        elif "_EN_" in name_upper:
            languages = language_options["EN"]
        elif "_HI_" in name_upper:
            languages = language_options["HI"]
        elif "_AS_" in name_upper:
            languages = language_options["AS"]
        else:
            languages = ["eng", "hin", "asm"]

        candidates = adaptive_ocr(str(image_path), languages)

        if not candidates:
            print(f"No OCR candidates for: {image_name}")
            continue

        # Evaluate every OCR candidate against the reference text.
        scored_candidates = []

        for candidate in candidates:
            score = similarity_score(
                candidate["Extracted_Text"],
                expected_text
            )

            scored_candidates.append((score, candidate))

        best_score, best_candidate = max(
            scored_candidates,
            key=lambda item: item[0]
        )

        results.append({
            "Image_Name": image_name,
            "Layout": best_candidate["Layout"],
            "Preprocessing": best_candidate["Preprocessing"],
            "Language": best_candidate["Language"],
            "PSM": best_candidate["PSM"],
            "Extracted_Text": best_candidate["Extracted_Text"],
            "Similarity_Percent": round(best_score, 2),
        })

        print(f"{image_name}: {best_score:.2f}%")

    if not results:
        print("No results generated. Check the image files and CSV.")
        return

    results_df = pd.DataFrame(results)

    output_file = RESULTS_DIR / "baseline_ocr_results.csv"
    results_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\nEvaluation complete.")
    print(f"Images evaluated: {len(results_df)}")
    print(
        "Mean text similarity: "
        f"{results_df['Similarity_Percent'].mean():.2f}%"
    )
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()