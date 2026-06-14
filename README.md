# MusicMakerLM

Generate, analyze, and teach music — symbolic core, local-first AI.

## Quick Start

```bash
# 1. Install Python deps
pip install -r requirements-dev.txt

# 2. Copy env config
cp .env.example .env

# 3. (Optional) Install FluidSynth for WAV playback
#    Ubuntu/Debian: sudo apt-get install fluidsynth
#    macOS:         brew install fluid-synth

# 4. (Optional) Pull an Ollama model for AI generation
#    Install Ollama from https://ollama.com, then:
bash scripts/pull_llm_model.sh

# 5. Start the server
./run.sh
# → Open http://localhost:8000
```

## Architecture

Music lives as **symbolic data** (Piece/Part/Measure/Note/Chord Pydantic models), never raw audio.

```
prompt → LLM → Piece (JSON) → MIDI → WAV (FluidSynth)
                            → MusicXML → SVG (Verovio)
                            → Analysis (music21, deterministic)
                              → Explanation (LLM narrates facts)
```

Every external dependency sits behind a provider abstraction in `app/providers/`.
- Development: Ollama (local LLM) + FluidSynth ($0)
- Production flip: set `LLM_PROVIDER=openai` + `AUDIO_PROVIDER=api`

## Run Tests

```bash
pytest tests/ -v
```

Tests pass without Ollama or FluidSynth installed.

## API

Interactive docs at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/generate` | Generate a piece from a text prompt |
| POST | `/api/v1/analyze` | Analyze a piece (key, chords, range…) |
| POST | `/api/v1/teach` | Analyze + LLM explanation |

## Roadmap

See GitHub Issues #1–#13 for the full deployed-tree roadmap.
