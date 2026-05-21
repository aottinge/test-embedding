"""
Benchmark pour comparer deux indexes (texte vs OCR) sur un jeu de requêtes.

Le fichier de test attendu: JSON array d'objets {"query": "...", "relevant": ["path/to/file.pdf", ...]}

Calcul des metrics: top-1 et top-3 accuracy.
"""
import json
from typing import List, Dict
from scoring import rank_documents
import os


def load_tests(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_hit(relevant_files: List[str], results: List[Dict]) -> (bool, bool):
    """Return (top1_hit, top3_hit) depending on whether any of relevant_files appear in results' sources."""
    top1 = False
    top3 = False
    if not results:
        return False, False
    top_k_sources = [r.get('source') for r in results]
    if top_k_sources:
        top1 = any(r == top_k_sources[0] for r in relevant_files)
    top3 = any(r in top_k_sources[:3] for r in relevant_files)
    return top1, top3


def run_benchmark(tests_path: str, index_a: List[dict], index_b: List[dict], method: str = 'overlap') -> Dict:
    tests = load_tests(tests_path)
    results = {'pipeline_a': {'top1': 0, 'top3': 0}, 'pipeline_b': {'top1': 0, 'top3': 0}, 'n': len(tests), 'details': []}
    for t in tests:
        query = t.get('query', '')
        relevant = t.get('relevant', [])
        ranked_a = rank_documents(query, index_a, top_k=3, method=method)
        ranked_b = rank_documents(query, index_b, top_k=3, method=method)
        a_top1, a_top3 = check_hit(relevant, ranked_a)
        b_top1, b_top3 = check_hit(relevant, ranked_b)
        results['pipeline_a']['top1'] += int(a_top1)
        results['pipeline_a']['top3'] += int(a_top3)
        results['pipeline_b']['top1'] += int(b_top1)
        results['pipeline_b']['top3'] += int(b_top3)
        results['details'].append({
            'query': query,
            'relevant': relevant,
            'a': ranked_a,
            'b': ranked_b
        })
    # normalize
    if results['n'] > 0:
        results['pipeline_a']['top1_acc'] = results['pipeline_a']['top1'] / results['n']
        results['pipeline_a']['top3_acc'] = results['pipeline_a']['top3'] / results['n']
        results['pipeline_b']['top1_acc'] = results['pipeline_b']['top1'] / results['n']
        results['pipeline_b']['top3_acc'] = results['pipeline_b']['top3'] / results['n']
    return results


def export_results(results: Dict, out_path: str):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print('Usage: benchmark.py tests.json text_index.json ocr_index.json')
        sys.exit(1)
    tests_path = sys.argv[1]
    text_index_path = sys.argv[2]
    ocr_index_path = sys.argv[3]
    with open(text_index_path, 'r', encoding='utf-8') as f:
        idx_a = json.load(f)
    with open(ocr_index_path, 'r', encoding='utf-8') as f:
        idx_b = json.load(f)
    res = run_benchmark(tests_path, idx_a, idx_b)
    print(json.dumps(res, ensure_ascii=False, indent=2))

