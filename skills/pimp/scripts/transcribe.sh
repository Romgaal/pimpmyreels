#!/bin/bash
# usage: transcribe.sh <rush> <outdir>
# Produces <outdir>/segments.json (sentences) and <outdir>/words.json (word-level timings).
# Skips automatically if already transcribed. Prints the segment timeline.
set -e
RUSH="$1"
OUT="$2"
MODEL="$HOME/.pimpmyreels/models/ggml-small.bin"
LANG=$(python3 -c "import json;print(json.load(open('$HOME/.pimpmyreels/config.json')).get('language','auto'))" 2>/dev/null || echo auto)

mkdir -p "$OUT"
if [ -f "$OUT/words.json" ] && [ -f "$OUT/segments.json" ]; then
  echo "(transcription already present — skipping)"
else
  ffmpeg -y -i "$RUSH" -vn -ac 1 -ar 16000 "$OUT/audio.wav" -loglevel error
  whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l "$LANG" -oj -of "$OUT/segments" >/dev/null 2>&1
  whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l "$LANG" -ml 1 -oj -of "$OUT/words" >/dev/null 2>&1
fi

python3 - "$OUT" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1] + '/segments.json'))
for s in d.get('transcription', []):
    o = s['offsets']
    print(f"{o['from']/1000:6.1f}-{o['to']/1000:6.1f}  {s['text'].strip()}")
EOF
