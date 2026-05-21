"""
Pipeline texte : lire PDFs texte avec PyMuPDF et chunker
"""
import fitz  # PyMuPDF
import os
from typing import List
from chunking import chunk_text


def extract_text_from_pdf(path: str) -> List[dict]:
	"""Retourne une liste de dicts pour chaque page: {'page': i, 'text': ...}"""
	docs = []
	try:
		doc = fitz.open(path)
	except Exception as e:
		print(f"Erreur ouverture PDF {path}: {e}")
		return docs
	for i, page in enumerate(doc):
		try:
			text = page.get_text()
		except Exception:
			text = ""
		docs.append({"page": i + 1, "text": text or ""})
	return docs


def index_text_dir(directory: str, max_chars: int = 1000) -> List[dict]:
	"""Parcours le dossier, lit les PDF texte et renvoie un index list.

	Chaque entrée: {'text': chunk, 'source': filename, 'page': page, 'type': 'text'}
	"""
	index = []
	for root, _, files in os.walk(directory):
		for f in files:
			fp = os.path.join(root, f)
			if not f.lower().endswith('.pdf'):
				continue
			pages = extract_text_from_pdf(fp)
			for p in pages:
				chunks = chunk_text(p.get('text', ''), max_chars=max_chars)
				for c in chunks:
					index.append({
						'text': c,
						'source': fp,
						'page': p.get('page'),
						'type': 'text'
					})
	return index


if __name__ == '__main__':
	import sys
	d = sys.argv[1] if len(sys.argv) > 1 else '.'
	idx = index_text_dir(d)
	print(f'Indexed {len(idx)} chunks from text PDFs in {d}')


