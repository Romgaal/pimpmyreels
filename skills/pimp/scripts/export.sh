#!/bin/bash
# usage: export.sh <project_dir> [--draft]
# Renders the reel straight to H.264 (no ProRes intermediate) and grabs a cover.
# --draft = half resolution, for fast review iterations.
set -e
PROJ="$(cd "$1" && pwd)"
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TPL="$PLUGIN_ROOT/template"
DRAFT=""
[ "$2" = "--draft" ] && DRAFT="--scale=0.5 --crf=22"

rm -rf "$TPL/public/project"
mkdir -p "$TPL/public/project"
cp "$PROJ/mapping.json" "$TPL/mapping.json"
cp "$PROJ"/rush.* "$TPL/public/project/" 2>/dev/null || true
[ -d "$PROJ/img" ] && cp -R "$PROJ/img" "$TPL/public/project/img"

mkdir -p "$PROJ/out"
(cd "$TPL" && npx remotion render ReelCutaways "$PROJ/out/reel.mp4" $DRAFT)

MID=$(python3 -c "
import json
m = json.load(open('$PROJ/mapping.json'))
s = m['segments'][0]
e = s.get('end', m['segments'][1]['start'] if len(m['segments']) > 1 else m['durationInFrames'])
print(round((s['start'] + e) / 2 / m['fps'], 2))")
ffmpeg -y -ss "$MID" -i "$PROJ/out/reel.mp4" -vframes 1 "$PROJ/out/cover.jpg" -loglevel error

echo "EXPORT OK: $PROJ/out/reel.mp4 (+cover.jpg)"
