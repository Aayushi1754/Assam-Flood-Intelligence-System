from importlib import import_module
import cv2
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")

LANGUAGE_MAP={
    "EN":["eng"],
    "HI":["hin"],
    "AS":["asm"],
    "CM":["eng+hind","hin+eng"],
    "AS_EN":["eng+asm","asm+eng"],
}
def get_image_language(image_name):
    name = image_name.upper()

    if "_AS_EN_" in name:
        return LANGUAGE_MAP["AS_EN"]
    elif "_CM_" in name:
        return LANGUAGE_MAP["CM"]
    elif "_EN_" in name:
        return LANGUAGE_MAP["EN"]
    elif "_HI_" in name:
        return LANGUAGE_MAP["HI"]
    elif "_AS_" in name:
        return LANGUAGE_MAP["AS"]

    return ["eng", "hin", "asm"]
def preprocess_image(gray, method):
    if method == "original":
        return gray

    if method == "otsu":
        _, result = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return result

    if method == "adaptive":
        block_size = 31

        if min(gray.shape) < block_size:
            block_size = max(
                3,
                min(gray.shape) // 2 * 2 - 1
            )

        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            11
        )

    raise ValueError(f"Unknown preprocessing method: {method}")
def run_tesseract(image, language, psm):
    config = f"--oem 3 --psm {psm}"

    return pytesseract.image_to_string(
        image,
        lang=language,
        config=config
    ).strip()
def adaptive_ocr(image_path, language_options):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    image = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    candidates = []

    # Full-image OCR
    for method in ["original", "otsu", "adaptive"]:
        processed = preprocess_image(gray, method)

        for language in language_options:
            for psm in [3, 6, 11]:
                try:
                    text = run_tesseract(
                        processed,
                        language,
                        psm
                    )

                    candidates.append({
                        "Layout": "full_image",
                        "Preprocessing": method,
                        "Language": language,
                        "PSM": psm,
                        "Extracted_Text": text
                    })

                except pytesseract.TesseractError as error:
                    print(
                        f"Skipped {method}/{language}/PSM{psm}: {error}"
                    )

    # Two-column OCR
    height, width = gray.shape
    midpoint = width // 2
    gap = max(1, int(width * 0.015))

    left = gray[:, :max(1, midpoint - gap)]
    right = gray[:, min(width, midpoint + gap):]

    if right.size > 0:
        for method in ["original", "otsu"]:
            left_processed = preprocess_image(left, method)
            right_processed = preprocess_image(right, method)

            for language in language_options:
                try:
                    left_text = run_tesseract(
                        left_processed,
                        language,
                        6
                    )

                    right_text = run_tesseract(
                        right_processed,
                        language,
                        6
                    )

                    candidates.append({
                        "Layout": "two_columns",
                        "Preprocessing": method,
                        "Language": language,
                        "PSM": 6,
                        "Extracted_Text": (
                            left_text + "\n" + right_text
                        ).strip()
                    })

                except pytesseract.TesseractError as error:
                    print(
                        f"Skipped column OCR {method}/{language}: {error}"
                    )

    return candidates
