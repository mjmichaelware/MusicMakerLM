# Vercel serverless entry point.
# Set env vars BEFORE any imports so music21 and SQLite use /tmp.
import os
os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("MUSIC21_COMMON_CORPUS_CACHE_DISABLED", "1")
# Point music21 scratch space to /tmp (only writable dir on Vercel)
os.environ.setdefault("HOME", "/tmp")

from app.main import app  # noqa: F401, E402
