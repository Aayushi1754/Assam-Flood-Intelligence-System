from pathlib import Path
import csv

from ocr import adaptive_ocr

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGE_PATH = PROJECT_ROOT / "Backend" / "NLP" / "Dataset" / "FS_EN_001.png"
RESULTS_DIR = PROJECT_ROOT / "Backend" / "NLP" / "Results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("Testing FloodSense OCR...")
print(f"Image: {IMAGE_PATH.name}")

candidates = adaptive_ocr(str(IMAGE_PATH), ["eng"])

if not candidates:
    print("No OCR candidates were generated.")
    raise SystemExit(1)

# Select a candidate for this basic pipeline test.
best_result = max(
    candidates,
    key=lambda item: len(item["Extracted_Text"])
)

print("\nExtracted text:")
print(best_result["Extracted_Text"])

output_file = RESULTS_DIR / "FS_EN_001_test_result.csv"

with output_file.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Image_Name",
            "Layout",
            "Preprocessing",
            "Language",
            "PSM",
            "Extracted_Text",
        ],
    )

    writer.writeheader()
    writer.writerow({
        "Image_Name": IMAGE_PATH.name,
        **best_result,
    })

print(f"\nResult saved to: {output_file}")