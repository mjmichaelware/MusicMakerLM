#!/usr/bin/env bash
set -euo pipefail

echo "=== MusicMakerLM environment setup ==="

# FluidSynth
if command -v fluidsynth &>/dev/null; then
  echo "FluidSynth already installed: $(fluidsynth --version 2>&1 | head -1)"
elif command -v apt-get &>/dev/null; then
  echo "Installing FluidSynth via apt..."
  sudo apt-get install -y fluidsynth
elif command -v brew &>/dev/null; then
  echo "Installing FluidSynth via brew..."
  brew install fluid-synth
else
  echo "WARNING: Cannot install FluidSynth automatically. Install it manually."
  echo "  Ubuntu/Debian: apt-get install fluidsynth"
  echo "  macOS:         brew install fluid-synth"
fi

# Copy .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

# Python deps
pip install -r requirements-dev.txt

# Smoke test music21
python -c "import music21; print('music21:', music21.__version__)"

echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Run: bash scripts/pull_llm_model.sh   (needs Ollama installed)"
echo "  2. Download a SoundFont to soundfonts/GeneralUser.sf2"
echo "  3. Run: ./run.sh"
