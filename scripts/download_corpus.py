"""
Prepare starter corpus examples from music21's built-in corpus.
This does NOT download from external URLs — it uses the package-bundled files.
Real public-domain corpus ingestion (IMSLP etc.) is tracked in GitHub Issue #4.
"""
import os
from music21 import corpus

DEST = "corpus"
os.makedirs(DEST, exist_ok=True)

PIECES = [
    ("bach/bwv66.6",         "bach_bwv66_6"),
    ("beethoven/opus18no1",  "beethoven_opus18no1"),
    ("mozart/k80",           "mozart_k80"),
]

for corpus_path, out_stem in PIECES:
    try:
        p = corpus.parse(corpus_path)
        out = os.path.join(DEST, out_stem + ".musicxml")
        p.write("musicxml", fp=out)
        print(f"Saved {out}")
    except Exception as e:
        print(f"Skipped {corpus_path}: {e}")

print(f"Corpus prepared in {DEST}/")
