from __future__ import annotations

from pathlib import Path
import shutil
import time

import pyautogui
import pytesseract


SCREEN_DIR = Path(__file__).resolve().parents[2] / "screenshots"
SCREEN_DIR.mkdir(exist_ok=True)


def _tesseract_path():
    found = shutil.which("tesseract")
    if found:
        return found

    common = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in common:
        if Path(path).exists():
            return path

    return None


def observe_screen():
    """
    Capture the current desktop and extract visible text.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    image_path = SCREEN_DIR / f"screen_{timestamp}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(image_path)

    tess = _tesseract_path()

    if not tess:
        return {
            "success": True,
            "image": str(image_path),
            "ocr_available": False,
            "text": "",
            "message": "Screenshot captured, but Tesseract OCR is not installed."
        }

    pytesseract.pytesseract.tesseract_cmd = tess

    text = pytesseract.image_to_string(screenshot)

    return {
        "success": True,
        "image": str(image_path),
        "ocr_available": True,
        "text": text.strip(),
        "message": "Screen captured and analyzed successfully."
    }


if __name__ == "__main__":
    result = observe_screen()

    print("\n=== ASTRA SCREEN OBSERVATION ===")
    print("Success:", result["success"])
    print("Image:", result["image"])
    print("OCR:", result["ocr_available"])
    print("\n--- VISIBLE TEXT ---")
    print(result["text"] or "[No readable text detected]")
    print("\n=== DONE ===")
