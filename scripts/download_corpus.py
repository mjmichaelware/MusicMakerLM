"""Prepare built-in music21 corpus examples into the corpus/ directory.

These are public-domain scores included with the music21 package itself —
no external download required. Real IMSLP/KernScores corpus ingestion is
deferred to Issue #4.
"""
import os
import sys

from music21 import corpus

DEST = os.path.join(os.path.dirname(__file__), "..", "corpus")
os.makedirs(DEST, exist_ok=True)

PIECES = [
    ("bach/bwv66.6", "bach_bwv66_6"),
    ("bach/bwv7.7", "bach_bwv7_7"),
    ("beethoven/opus18no1/movement1", "beethoven_op18no1_mvt1"),
    ("mozart/k80/movement1", "mozart_k80_mvt1"),
]

saved = 0
for corpus_path, stem in PIECES:
    out = os.path.join(DEST, f"{stem}.xml")
    try:
        p = corpus.parse(corpus_path)
        p.write("musicxml", fp=out)
        print(f"Saved {out}")
        saved += 1
    except Exception as e:
        print(f"Skipped {corpus_path}: {e}", file=sys.stderr)

print(f"\nDone. {saved}/{len(PIECES)} pieces saved to corpus/")
