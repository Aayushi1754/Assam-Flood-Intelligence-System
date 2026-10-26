# Install the Assamese Tesseract language data separately if needed:
# apt-get install -y -qq tesseract-ocr-asm
# pip install langdetect
import re
import os
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
import pandas as pd
from difflib import SequenceMatcher
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity_score(expected, extracted):
    expected = normalize_text(expected)
    extracted = normalize_text(extracted)

    if not expected:
        return 100.0 if not extracted else 0.0

    return round(
        SequenceMatcher(
            None,
            expected,
            extracted
        ).ratio() * 100,
        2
    )
LANGUAGE_MAP = {
    "EN": ["eng"],
    "HI": ["hin"],
    "AS": ["asm"]
}


def detect_language(text):
  text=str(text).strip()
  if len(text) <10:
    return "unknown"
  try:
    detected_code=detect(text)
    return detected_code
  except LangDetectException:
    return "unknown"


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
LANGUAGE_CODE_MAP = {
    "en": "eng",
    "hi": "hin",
    "as": "asm",
    "unknown": "unknown"
}

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

                    detected_language = detect_language(text)

                    candidates.append({
                        "Layout": "full_image",
                        "Preprocessing": method,
                        "Language": language,
                        "Detected_Language": detected_language,
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

                    text = (
                        left_text + "\n" + right_text
                    ).strip()

                    detected_language = detect_language(text)

                    candidates.append({
                        "Layout": "two_columns",
                        "Preprocessing": method,
                        "Language": language,
                        "Detected_Language": detected_language,
                        "PSM": 6,
                        "Extracted_Text": text
                    })

                except pytesseract.TesseractError as error:
                    print(
                        f"Skipped column OCR {method}/{language}: {error}"
                    )

    return candidates

def extract_text_from_image(image_path, languages=None):
    if languages is None:
        languages = ["eng", "hin", "asm"]

    candidates = adaptive_ocr(image_path, languages)

    if not candidates:
        return {
        "success": False,
        "text": "",
        "language": "unknown",
        "message": "No text could be extracted from the image."
    }

# Without ground-truth text, choose the candidate with
# the most non-whitespace characters as a simple heuristic.
    best = max(
    candidates,
    key=lambda item: len(item["Extracted_Text"].strip())
)

    extracted_text = best["Extracted_Text"].strip()

    if not extracted_text:
        return {
        "success": False,
        "text": "",
        "language": "unknown",
        "message": "No readable text was found in the image."
    }

    return {
    "success": True,
    "text": extracted_text,
    "language": best["Detected_Language"],
    "ocr_language": best["Language"],
    "preprocessing": best["Preprocessing"],
    "layout": best["Layout"],
    "psm": best["PSM"],
    "message": "Text extracted successfully."
}