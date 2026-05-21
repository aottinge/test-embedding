"""
CLI principal pour:
- indexer dir with text pipeline (PyMuPDF)
- indexer dir with image pipeline (OCR)
- recherche interactive
- benchmark

Usage examples in README.
"""
import argparse
import json
import os
from text_pipeline import index_text_dir
from image_pipeline import index_image_dir
from scoring import rank_documents
from benchmark import run_benchmark, export_results


def save_index(index, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def load_index(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def cmd_index(args):
    if args.which in ('text', 'both'):
        print('Indexation pipeline A (text)...')
        idx = index_text_dir(args.input, max_chars=args.max_chars)
        save_index(idx, args.text_index)
        print(f'Saved text index to {args.text_index} ({len(idx)} chunks)')
    if args.which in ('image', 'both'):
        print('Indexation pipeline B (image/OCR)...')
        idx = index_image_dir(args.input, max_chars=args.max_chars, poppler_path=args.poppler_path, lang=args.lang)
        save_index(idx, args.ocr_index)
        print(f'Saved OCR index to {args.ocr_index} ({len(idx)} chunks)')


def cmd_search(args):
    # load both indexes
    a = load_index(args.text_index)
    b = load_index(args.ocr_index)
    q = args.query
    print('--- Pipeline A (text) ---')
    ra = rank_documents(q, a, top_k=3, method=args.method)
    for i, r in enumerate(ra, 1):
        print(f'{i}. score={r["score"]:.4f} source={r["source"]} page={r.get("page")}')
        print(f'   snippet: {r["text"][:200]!s}\n')
    print('--- Pipeline B (OCR) ---')
    rb = rank_documents(q, b, top_k=3, method=args.method)
    for i, r in enumerate(rb, 1):
        print(f'{i}. score={r["score"]:.4f} source={r["source"]} page={r.get("page")}')
        print(f'   snippet: {r["text"][:200]!s}\n')


def cmd_benchmark(args):
    a = load_index(args.text_index)
    b = load_index(args.ocr_index)
    res = run_benchmark(args.tests, a, b, method=args.method)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if args.out:
        export_results(res, args.out)
        print(f'Exported results to {args.out}')


def make_parser():
    p = argparse.ArgumentParser(description='Comparer pipeline texte vs OCR (sans IA)')
    sub = p.add_subparsers(dest='cmd')

    idx = sub.add_parser('index')
    idx.add_argument('input')
    idx.add_argument('--which', choices=['text', 'image', 'both'], default='both')
    idx.add_argument('--text-index', default='indexes/text_index.json')
    idx.add_argument('--ocr-index', default='indexes/ocr_index.json')
    idx.add_argument('--max-chars', type=int, default=1000)
    idx.add_argument('--poppler-path', default=None)
    idx.add_argument('--lang', default='fr')
    idx.set_defaults(func=cmd_index)

    s = sub.add_parser('search')
    s.add_argument('--text-index', default='indexes/text_index.json')
    s.add_argument('--ocr-index', default='indexes/ocr_index.json')
    s.add_argument('--query', required=True)
    s.add_argument('--method', choices=['overlap', 'tf'], default='overlap')
    s.set_defaults(func=cmd_search)

    b = sub.add_parser('benchmark')
    b.add_argument('tests')
    b.add_argument('--text-index', default='indexes/text_index.json')
    b.add_argument('--ocr-index', default='indexes/ocr_index.json')
    b.add_argument('--out', default='results/benchmark.json')
    b.add_argument('--method', choices=['overlap', 'tf'], default='overlap')
    b.set_defaults(func=cmd_benchmark)

    return p


def main():
    p = make_parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
        return
    args.func(args)


if __name__ == '__main__':
    main()

