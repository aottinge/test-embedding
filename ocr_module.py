"""
Wrapper simple pour OCR Tesseract (pytesseract).

Retourne le texte extrait d'une image (PIL or path).
"""
import pytesseract
from typing import List
from PIL import Image
import os


class OCRWrapper:
    def __init__(self, lang: str = 'fra'):
        # lang: 'fra' for French, 'eng' for English
        # Tesseract uses ISO 639-3 language codes
        self.lang = lang

    def image_to_text(self, img) -> str:
        """Extract text from PIL Image or file path."""
        if isinstance(img, str):
            if not os.path.exists(img):
                return ""
            img = Image.open(img)
        try:
            # Convert PIL Image to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Extract text using Tesseract
            text = pytesseract.image_to_string(img, lang=self.lang)
            return text.strip()
        except Exception as e:
            print(f"Erreur OCR: {e}")
            return ""


if __name__ == '__main__':
    print('OCR wrapper ready (requires tesseract system package and pytesseract Python package).')

