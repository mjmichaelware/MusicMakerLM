# AGENTS.md — MusicMakerLM Codebase Guide

This file is for AI agents (and humans) who need to understand and modify this codebase quickly.

---

## Core Architecture

```
User prompt / score upload
        ↓
app/routes/          ← FastAPI endpoints (thin — delegate to core/)
        ↓
app/core/            ← all logic (no framework code)
  generation.py      ← LLM → JSON → Piece (with deterministic fallback)
  analysis.py        ← Piece → analysis dict (deterministic, music21)
  tutor.py           ← analysis dict → explanation (LLM narrates, never invents facts)
  render_notation.py ← Piece → MusicXML / SVG fallback
  render_audio.py    ← Piece → MIDI bytes / WAV bytes (WAV optional)
        ↓
app/core/data_model.py    ← Piece is the ONLY source of truth
        ↓
app/providers/       ← swap layer between free-local and paid-API backends
  base.py            ← abstract LLMProvider, AudioProvider + factories
  llm_local.py       ← Ollama (free, local)
  llm_api.py         ← OpenAI stub (paid — Issue #7)
  audio_local.py     ← FluidSynth subprocess (free, optional)
  audio_api.py       ← hosted audio stub (paid — Issue #8)
```

---

## Invariants — Never Violate These

1. **Symbolic JSON is the source of truth.** The `Piece` Pydantic model is the only form
   stored in the database (`PieceRecord.symbolic_json`). MIDI and WAV are derived artifacts
   generated on request; never store them in the DB.

2. **LLM never produces facts.** `analysis.py` runs deterministically (music21). The LLM in
   `tutor.py` only narrates what analysis already computed. Never call `analyze_piece()` from
   inside `generation.py`.

3. **ProviderUnavailableError surfaces at call time only.** Provider constructors and factory
   functions never raise. Errors appear only on `complete()`, `stream()`, or `synthesize()`.
   `render_to_wav()` catches `ProviderUnavailableError` and returns `None` — callers must handle.

4. **Never import concrete providers directly in routes.** Always go through
   `get_llm_provider(settings)` and `get_audio_provider(settings)` from `app/providers/base.py`.

5. **`analysis.py` never raises.** It always returns a dict with all 11 required keys.
   Partial failures go into `warnings`.

---

## Provider Swap Pattern

Switch providers via environment variables — no code changes needed:

| Env var | `"local"` (default, $0) | `"openai"` / `"api"` (paid) |
|---|---|---|
| `LLM_PROVIDER` | Ollama (`llm_local.py`) | OpenAI stub → Issue #7 |
| `AUDIO_PROVIDER` | FluidSynth (`audio_local.py`) | API stub → Issue #8 |

To add a new LLM backend:
1. Create `app/providers/llm_myname.py` implementing `LLMProvider`.
2. Add `if settings.llm_provider == "myname": return MyNameProvider(settings)` in `get_llm_provider()`.
3. Add the provider name to `.env.example`.

---

## Symbolic Data Flow

```
POST /api/v1/generate
  → generate_piece(prompt, llm_provider)
      → LLM.complete(full_prompt)  [or fallback stub]
      → json.loads → Piece.model_validate(data)
  → render_to_midi(piece)           → bytes (mido, absolute-tick queue)
  → render_to_wav(piece, audio)     → bytes | None (FluidSynth subprocess)
  → render_to_musicxml(piece)       → str (music21 Score → temp .musicxml)
  → response: {piece_json, musicxml, midi_b64, wav_b64}

POST /api/v1/analyze
  → Piece.model_validate(piece_json)
  → analyze_piece(piece)            → dict (music21 key/chord, always safe)

POST /api/v1/teach
  → analyze_piece(piece)            → analysis dict
  → explain_analysis(dict, llm)     → str (LLM narrates; fallback if unavailable)
```

---

## Which File to Edit for Each Concern

| Concern | File |
|---|---|
| Generation prompt wording | `app/llm/prompts.py` |
| Add new analysis metric | `app/core/analysis.py` only |
| Change tutor explanation style | `app/llm/prompts.py::EXPLAIN_ANALYSIS_TEMPLATE` |
| Add a new API endpoint | `app/routes/` + register in `app/main.py::create_app()` |
| Change the data model | `app/core/data_model.py` → update `to_midi()` and `to_musicxml()` → re-run tests |
| Add a new instrument | Change `Part.instrument_midi` (GM patch 0-127) |
| Add LLM provider | `app/providers/llm_*.py` + factory in `app/providers/base.py` |
| Add audio provider | `app/providers/audio_*.py` + factory in `app/providers/base.py` |
| Change DB schema | `app/db/models.py` + add Alembic migration (Issue #9) |

---

## Test Philosophy

Tests must pass with no external services installed (no Ollama, no FluidSynth, no Verovio):
- Use `_fallback_piece()` as a fixture.
- Mock providers with inline classes implementing the abstract interface.
- `render_to_wav()` returning `None` is correct behavior when the provider raises.

---

## Deferred Work (GitHub Issues)

| Issue | Title |
|---|---|
| #1 | Auth & multi-user (JWT, UserRecord) |
| #2 | Docker & docker-compose |
| #3 | Frontend OSMD (replace `<pre>` with OpenSheetMusicDisplay) |
| #4 | Real corpus download & style profiles |
| #5 | RAG / vector index for style-aware generation |
| #6 | Deep music21 analysis (voice leading, form detection) |
| #7 | OpenAI / Anthropic LLM provider |
| #8 | Paid audio synthesis API |
| #9 | Alembic migrations |
| #10 | Marketing site & Cloudflare Pages |
| #11 | audio_transcribe.py (recording → notation) |
| #12 | Advanced generation modules (harmony, voice_leading, orchestration) |
| #13 | Makefile + CI/CD (GitHub Actions) |
