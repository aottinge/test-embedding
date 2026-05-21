"""
Scoring utilities:
- tokenisation simple
- word overlap score
- TF (term-frequency) cosine similarity (optionnel)

Retourne un score flottant; plus grand = meilleur.
"""
import re
from collections import Counter
from typing import List
import math
import numpy as np


TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> List[str]:
	return [t.lower() for t in TOKEN_RE.findall(text)]


def overlap_score(query: str, doc: str) -> float:
	q_tokens = set(tokenize(query))
	if not q_tokens:
		return 0.0
	d_tokens = set(tokenize(doc))
	inter = q_tokens.intersection(d_tokens)
	return len(inter) / len(q_tokens)


def tf_counter(text: str) -> Counter:
	return Counter(tokenize(text))


def tf_cosine_score(query: str, doc: str) -> float:
	q_cnt = tf_counter(query)
	d_cnt = tf_counter(doc)
	if not q_cnt or not d_cnt:
		return 0.0
	# build union of tokens
	tokens = list(set(list(q_cnt.keys()) + list(d_cnt.keys())))
	qv = np.array([q_cnt.get(t, 0) for t in tokens], dtype=float)
	dv = np.array([d_cnt.get(t, 0) for t in tokens], dtype=float)
	num = np.dot(qv, dv)
	denom = np.linalg.norm(qv) * np.linalg.norm(dv)
	if denom == 0:
		return 0.0
	return float(num / denom)


def rank_documents(query: str, docs: List[dict], top_k: int = 3, method: str = "overlap") -> List[dict]:
	"""Rank docs (list of dicts containing at least 'text') and return top_k docs with scores added.
	"""
	scorer = overlap_score if method == "overlap" else tf_cosine_score
	scored = []
	for d in docs:
		s = scorer(query, d.get("text", ""))
		entry = dict(d)
		entry["score"] = s
		scored.append(entry)
	scored.sort(key=lambda x: x["score"], reverse=True)
	return scored[:top_k]


if __name__ == "__main__":
	q = "Quel est le prix?"
	docs = [{"text": "Le prix est 10 euros.", "source": "a.pdf"}, {"text": "Ceci est un test.", "source": "b.pdf"}]
	print(rank_documents(q, docs, top_k=2, method="overlap"))


