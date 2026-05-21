Comparaison de deux pipelines de recherche de documents (SANS IA)

Structure:
- main.py: CLI principal
- text_pipeline.py: extraction texte via PyMuPDF
- image_pipeline.py: conversion PDF->images + OCR (Tesseract via pytesseract)
- ocr_module.py: wrapper Tesseract
- chunking.py: découpage en chunks
- scoring.py: scoring simple (overlap, tf-cosine)
- benchmark.py: évalue top-1/top-3 accuracy

Installation (macOS):

1) Installer Tesseract et poppler (pour pdf2image):
   brew install tesseract poppler

2) Créer un venv et installer dépendances:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

Utilisation rapide:

- Indexer un dossier (texte + OCR):
  python main.py index /chemin/vers/fichiers --which both

- Rechercher une requête:
  python main.py search --query "Quel est le prix?"

- Lancer un benchmark avec un fichier tests.json:
  python main.py benchmark tests/queries.json --out results/bench.json

Format des tests (tests/queries.json):
[
  {
    "query": "Quel est le prix du produit X?",
    "relevant": ["/chemin/vers/mon/fichier.pdf"]
  }
]

Remarques:
- Pas d'embeddings ni LLM utilisés — uniquement matching string + TF
- Tesseract OCR supporte plusieurs langues (fra, eng, etc.) via le paramètre --lang

