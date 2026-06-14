# AGENTS.md — MusicMakerLM Codebase Guide for AI Agents

## Architecture Overview

```
User prompt / score file
        ↓
app/routes/         ← FastAPI endpoints (thin: validate, delegate, respond)
        ↓
app/core/           ← All business logic (no HTTP knowledge)
  data_model.py     ← Piece / Part / Measure / Note / Chord — the symbolic source of truth
  generation.py     ← LLM → JSON → Piece
  analysis.py       ← Piece → dict (deterministic, music21 only, no LLM)
  tutor.py          ← dict → prose explanation (LLM, with deterministic fallback)
  render_notation.py← Piece → MusicXML / SVG
  render_audio.py   ← Piece → MIDI bytes / WAV bytes (optional)
        ↓
app/providers/      ← Swap layer — local during build, paid on flip
  base.py           ← LLMProvider + AudioProvider abstract interfaces + factories
  llm_local.py      ← Ollama
  llm_api.py        ← OpenAI stub (Issue #7)
  audio_local.py    ← FluidSynth
  audio_api.py      ← Paid audio stub (Issue #8)
        ↓
app/db/             ← SQLAlchemy async models (symbolic JSON only — no audio blobs)
app/llm/prompts.py  ← All prompt templates
app/config.py       ← pydantic-settings; single source for all env vars
```

## Provider Swap Pattern

`LLM_PROVIDER` and `AUDIO_PROVIDER` in `.env` control which concrete class
`get_llm_provider()` / `get_audio_provider()` return. To add a new backend:

1. Create `app/providers/my_provider.py` implementing `LLMProvider` or `AudioProvider`
2. Add a branch to the factory in `app/providers/base.py`
3. Add the new provider name to `config.py` docs / `.env.example`

**Never** import concrete providers directly in routes — always go through the factory.

## Data Invariants

- **Symbolic JSON is the source of truth.** `Piece.model_dump_json()` is what gets stored in the DB.
- **Never store WAV or MIDI in the database.** Audio/MIDI are derived artifacts rendered on demand.
- **LLM never produces facts.** `analysis.py` is deterministic (music21). The LLM in `tutor.py` only narrates the `analysis_dict` it receives.
- **Never call `analyze_piece()` from `generation.py`.** Analysis is a separate post-generation step.

## MIDI Event Queue

`Piece.to_midi()` uses an absolute-tick queue:
1. Collect all `(abs_tick, msg_type, pitch, vel)` tuples
2. Sort by tick (note_off before note_on at the same tick)
3. Convert to delta ticks before writing `mido.Message`

This ensures chords and simultaneous events produce correct MIDI.

## Pydantic Discriminated Union

`Measure.events` is `list[Annotated[Note | Chord, Field(discriminator="kind")]]`.
`Note.kind = Literal["note"]`, `Chord.kind = Literal["chord"]`.
Always set `kind` explicitly when constructing Note/Chord objects.

## Where to Edit for Each Concern

| What to change | File(s) |
|---|---|
| LLM model / temperature | `config.py`, `providers/llm_local.py` |
| Generation prompt | `llm/prompts.py::GENERATE_PIECE_TEMPLATE` |
| Tutor narration style | `llm/prompts.py::EXPLAIN_ANALYSIS_TEMPLATE` |
| Add an analysis feature | `core/analysis.py` only |
| Add a new API route | `routes/` + `app/main.py::create_app()` |
| Change data model | `core/data_model.py` → update `to_midi()` + `to_musicxml()` → re-run tests |
| Add a new instrument | Set `Part.instrument_midi` to the GM patch number |
| Swap LLM backend | `LLM_PROVIDER=openai` in `.env` + complete `providers/llm_api.py` |
| Swap audio backend | `AUDIO_PROVIDER=api` in `.env` + complete `providers/audio_api.py` |

## Health Check

`GET /health` is mounted **outside** `/api/v1` — directly on the root app.
All other endpoints are under `/api/v1/`.
Static files are mounted last (`app.mount("/", ...)`) so they never shadow API routes.

## Testing Without Dependencies

All tests in `tests/` must pass without Ollama or FluidSynth installed.
- LLM calls are mocked with `MockLLM` / `FailLLM` classes in test files.
- Audio tests use `FakeAudio` mock or assert `render_to_wav()` returns `None`.
- `_fallback_piece()` is the deterministic test fixture — use it everywhere.

## Deferred Work (GitHub Issues)

See Issues #1–#13 for the deployed-tree roadmap:
auth, Docker, OSMD frontend, corpus, RAG, deep analysis, OpenAI provider,
paid audio, Alembic, marketing, transcription, advanced generation, CI/CD.
