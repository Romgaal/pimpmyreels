#!/bin/bash
# pimpmyreels — one-shot, idempotent setup. Safe to run many times.
set -e
echo "== pimpmyreels setup =="

# Anything already on the machine is reused as-is — nothing is reinstalled or upgraded.
need() { command -v "$1" >/dev/null; }
report() { if need "$1"; then echo "  $2: already installed, reusing"; else echo "  $2: installing..."; fi; }

if [[ "$(uname)" == "Darwin" ]]; then
  command -v brew >/dev/null || { echo "ERROR: Homebrew required → https://brew.sh"; exit 1; }
  for pair in "ffmpeg:ffmpeg" "whisper-cli:whisper-cpp" "gh:gh" "node:node"; do
    bin="${pair%%:*}"; pkg="${pair##*:}"
    report "$bin" "$pkg"
    need "$bin" || brew install "$pkg"
  done
else
  echo "  Linux: ensure ffmpeg, whisper.cpp (whisper-cli), gh and node are installed (see README)."
fi

MODEL="$HOME/.pimpmyreels/models/ggml-small.bin"
if [ -f "$MODEL" ]; then
  echo "  whisper model: already downloaded, reusing"
else
  mkdir -p "$(dirname "$MODEL")"
  echo "  whisper model: downloading (465MB, one-time)..."
  curl -L --progress-bar -o "$MODEL" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
fi

mkdir -p "$HOME/.pimpmyreels/cache" "$HOME/.pimpmyreels/mybank" "$HOME/pimpmyreels"
[ -f "$HOME/.pimpmyreels/config.json" ] || echo '{"contribution":"auto","language":"auto"}' > "$HOME/.pimpmyreels/config.json"

# The Remotion template is deliberately self-contained, even if you already have
# Remotion projects: yours may force a different codec (ProRes = 3GB reels), register
# other compositions, or simply be work in progress. pimpmyreels never touches them.
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
if [ -d "$PLUGIN_ROOT/template/node_modules" ]; then
  echo "  remotion template: already set up, reusing"
else
  echo "  remotion template: installing its own isolated copy (your own Remotion projects are left untouched)..."
  cd "$PLUGIN_ROOT/template"
  cp -n mapping.example.json mapping.json 2>/dev/null || true
  npm install --no-fund --no-audit
fi

if python3 -c "import PIL" 2>/dev/null; then
  echo "  pillow: already installed, reusing"
else
  echo "  pillow: installing..."
  pip3 install --quiet --break-system-packages pillow 2>/dev/null || pip3 install --quiet pillow
fi

echo "== setup OK =="
