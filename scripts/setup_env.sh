#!/usr/bin/env bash
set -euo pipefail

echo "=== MusicMakerLM environment setup ==="

# FluidSynth (optional — WAV synthesis)
if command -v apt-get &>/dev/null; then
    echo "Installing FluidSynth via apt..."
    sudo apt-get install -y fluidsynth || echo "WARNING: Could not install FluidSynth automatically."
elif command -v brew &>/dev/null; then
    echo "Installing FluidSynth via brew..."
    brew install fluid-synth || echo "WARNING: Could not install FluidSynth automatically."
else
    echo "WARNING: Cannot detect package manager. Install FluidSynth manually."
fi

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — review and update as needed."
fi

# Python dependencies
pip install -r requirements-dev.txt

# Smoke test imports
python -c "import music21; import mido; import fastapi; print('Core imports OK')"

echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Run Ollama:  ollama serve  (in a separate terminal)"
echo "  2. Pull model:  ./scripts/pull_llm_model.sh"
echo "  3. Start app:   ./run.sh"
