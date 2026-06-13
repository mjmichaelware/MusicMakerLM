#!/usr/bin/env bash
set -euo pipefail
MODEL="${OLLAMA_MODEL:-llama3}"
echo "Pulling Ollama model: $MODEL"
ollama pull "$MODEL"
echo "Model $MODEL ready."
