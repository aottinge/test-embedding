"""
Pipeline image: convertir PDF pages en images (pdf2image) et appliquer OCR (PaddleOCR)
"""
import os
from typing import List
from pdf2image import convert_from_path
from PIL import Image
from ocr_module import OCRWrapper
from chunking import chunk_text


IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}


def images_from_pdf(path: str, dpi: int = 200, poppler_path: str = None) -> List[Image.Image]:
    try:
        if poppler_path:
            return convert_from_path(path, dpi=dpi, poppler_path=poppler_path)
        else:
            return convert_from_path(path, dpi=dpi)
    except Exception as e:
        print(f"Erreur conversion PDF->images {path}: {e}")
        return []


def index_image_dir(directory: str, max_chars: int = 1000, poppler_path: str = None, lang: str = 'fr') -> List[dict]:
    index = []
    ocr = OCRWrapper(lang=lang)
    for root, _, files in os.walk(directory):
        for f in files:
            fp = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if ext == '.pdf':
                images = images_from_pdf(fp, poppler_path=poppler_path)
                for i, img in enumerate(images):
                    text = ocr.image_to_text(img)
                    chunks = chunk_text(text or '', max_chars=max_chars)
                    for c in chunks:
                        index.append({
                            'text': c,
                            'source': fp,
                            'page': i + 1,
                            'type': 'ocr'
                        })
            elif ext in IMAGE_EXT:
                try:
                    img = Image.open(fp)
                    text = ocr.image_to_text(img)
                    chunks = chunk_text(text or '', max_chars=max_chars)
                    for c in chunks:
                        index.append({
                            'text': c,
                            'source': fp,
                            'page': 1,
                            'type': 'image'
                        })
                except Exception as e:
                    print(f"Erreur lecture image {fp}: {e}")
            else:
                # skip other files
                continue
    return index


if __name__ == '__main__':
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    idx = index_image_dir(d)
    print(f'Indexed {len(idx)} chunks from images/OCR in {d}')

