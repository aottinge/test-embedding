"""
Fonctions de chunking simples :
- découpe en paragraphes
- limite de taille en caractères

Chaque chunk retourné est une string nettoyée.
"""
import re
from typing import List


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_paragraphs(text: str) -> List[str]:
    # Split on two or more newlines
    parts = re.split(r"\n\s*\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """Chunk text by paragraphs, split long paragraphs further by sentence boundaries.

    Args:
        text: input text
        max_chars: maximum characters per chunk

    Returns:
        list of chunk strings
    """
    text = normalize_whitespace(text)
    paras = split_paragraphs(text)
    chunks = []
    for p in paras:
        if len(p) <= max_chars:
            chunks.append(p)
        else:
            # try split by sentences (approx)
            sentences = re.split(r'(?<=[.!?])\s+', p)
            cur = []
            cur_len = 0
            for s in sentences:
                if not s:
                    continue
                if cur_len + len(s) + 1 <= max_chars:
                    cur.append(s)
                    cur_len += len(s) + 1
                else:
                    if cur:
                        chunks.append(normalize_whitespace(" ".join(cur)))
                    # if single sentence is longer than max_chars, hard split
                    if len(s) > max_chars:
                        for i in range(0, len(s), max_chars):
                            chunks.append(s[i : i + max_chars])
                        cur = []
                        cur_len = 0
                    else:
                        cur = [s]
                        cur_len = len(s)
            if cur:
                chunks.append(normalize_whitespace(" ".join(cur)))
    return chunks


if __name__ == "__main__":
    sample = """
    Ceci est un paragraphe.

    Ceci est un autre paragraphe très long. """ * 20
    print(len(chunk_text(sample, max_chars=200)))

