#!/bin/bash
# pimpmyreels — one-shot, idempotent setup. Safe to run many times.
set -e
echo "== pimpmyreels setup =="

if [[ "$(uname)" == "Darwin" ]]; then
  command -v brew >/dev/null || { echo "ERROR: Homebrew required → https://brew.sh"; exit 1; }
  command -v ffmpeg      >/dev/null || brew install ffmpeg
  command -v whisper-cli >/dev/null || brew install whisper-cpp
  command -v gh          >/dev/null || brew install gh
  command -v node        >/dev/null || brew install node
else
  echo "Linux detected: make sure ffmpeg, whisper.cpp (whisper-cli), gh and node are installed (see README)."
fi

MODEL="$HOME/.pimpmyreels/models/ggml-small.bin"
if [ ! -f "$MODEL" ]; then
  mkdir -p "$(dirname "$MODEL")"
  echo "Downloading Whisper model (465MB, one-time)..."
  curl -L --progress-bar -o "$MODEL" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
fi

mkdir -p "$HOME/.pimpmyreels/cache" "$HOME/.pimpmyreels/mybank" "$HOME/pimpmyreels"
[ -f "$HOME/.pimpmyreels/config.json" ] || echo '{"contribution":"auto","language":"auto"}' > "$HOME/.pimpmyreels/config.json"

PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
if [ ! -d "$PLUGIN_ROOT/template/node_modules" ]; then
  cd "$PLUGIN_ROOT/template"
  cp -n mapping.example.json mapping.json 2>/dev/null || true
  npm install --no-fund --no-audit
fi

python3 -c "import PIL" 2>/dev/null \
  || pip3 install --quiet --break-system-packages pillow 2>/dev/null \
  || pip3 install --quiet pillow

echo "== setup OK =="
