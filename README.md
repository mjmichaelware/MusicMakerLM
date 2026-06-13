# MusicMakerLM

Generate, analyze, and teach music — built on a symbolic core (MIDI + MusicXML), $0 during development.

Every external dependency (LLM, audio synthesis) sits behind a swap layer in `app/providers/`.
Build and test entirely free with Ollama + FluidSynth; flip to paid APIs when monetizing.

## Quick Start

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Copy environment config
cp .env.example .env

# 3. (Optional) Install FluidSynth for WAV audio
#    Ubuntu/Debian:  sudo apt-get install fluidsynth
#    macOS:          brew install fluid-synth

# 4. (Optional) Start Ollama for LLM generation
#    Install from https://ollama.com, then:
ollama serve &
./scripts/pull_llm_model.sh

# 5. Start the app
./run.sh
# → http://localhost:8000
```

The app works without Ollama (returns a deterministic stub piece) and without FluidSynth
(`wav_b64` will be `null` in API responses).

## Run Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Tests pass with no external services installed.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/api/v1/generate` | POST | Generate a piece from a text prompt |
| `/api/v1/analyze` | POST | Analyze a piece (key, chords, stats) |
| `/api/v1/teach` | POST | Analyze + LLM explanation |

Interactive docs: `http://localhost:8000/docs`

## Project Structure

```
app/
  core/          ← all music logic (generation, analysis, tutor, render)
  providers/     ← LLM and audio swap layer ($0 local ↔ paid API)
  routes/        ← FastAPI endpoints
  llm/           ← prompts
  db/            ← SQLAlchemy models + session
static/          ← single-page UI
tests/           ← pytest (no external deps needed)
scripts/         ← setup helpers
corpus/          ← downloaded scores (gitignored)
soundfonts/      ← .sf2 files (gitignored)
models/          ← Ollama model weights (gitignored)
```

See [AGENTS.md](AGENTS.md) for the full architecture guide.

## Provider Swap (Free → Paid)

Set environment variables to switch backends:

```
LLM_PROVIDER=openai     # swap Ollama → OpenAI (Issue #7)
AUDIO_PROVIDER=api      # swap FluidSynth → hosted audio (Issue #8)
```

No code changes required — only config.

## Build Order

The blueprint follows this sequence:
1. ✅ **Starting tree** — data model, providers, analysis, tutor, render, routes, basic UI
2. ⬜ Corpus download + style profiles (Issue #4)
3. ⬜ style_engine.py — "compose in the style of Mahler" (Issue #12)
4. ⬜ OSMD notation viewer (Issue #3)
5. ⬜ Auth + billing (Issues #1, #9)
6. ⬜ Paid provider flip (Issues #7, #8)
7. ⬜ Docker + CI + marketing site (Issues #2, #10, #13)
