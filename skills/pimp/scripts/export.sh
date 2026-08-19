#!/bin/bash
# usage: export.sh <project_dir> [--draft] [--from N]
#   (no flag)  full render, straight to H.264 CRF15 (no ProRes intermediate) + cover.jpg
#   --draft    half resolution, fast review iterations
#   --from N   economical iteration: re-render ONLY frames N→end and splice onto the
#              existing out/reel.mp4 (its head is kept, re-encoded once, frame-accurate).
#              This is how a one-image swap costs seconds, not a full re-render.
set -e
PROJ="$(cd "$1" && pwd)"; shift
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TPL="$PLUGIN_ROOT/template"

DRAFT=""; FROM=""
while [ $# -gt 0 ]; do
  case "$1" in
    --draft) DRAFT="--scale=0.5 --crf=22" ;;
    --from) FROM="$2"; shift ;;
    *) echo "unknown flag: $1"; exit 1 ;;
  esac
  shift
done

# Stage the project into the template (mapping + assets)
rm -rf "$TPL/public/project"
mkdir -p "$TPL/public/project"
cp "$PROJ/mapping.json" "$TPL/mapping.json"
cp "$PROJ"/rush.* "$TPL/public/project/" 2>/dev/null || true
[ -d "$PROJ/img" ] && cp -R "$PROJ/img" "$TPL/public/project/img"
mkdir -p "$PROJ/out"

FPS=$(python3 -c "import json;print(json.load(open('$PROJ/mapping.json'))['fps'])")
LAST=$(python3 -c "import json;print(json.load(open('$PROJ/mapping.json'))['durationInFrames']-1)")

if [ -n "$FROM" ]; then
  [ -f "$PROJ/out/reel.mp4" ] || { echo "ERROR: --from needs an existing out/reel.mp4 (run a full export first)"; exit 1; }
  [ -n "$DRAFT" ] && { echo "ERROR: --from and --draft don't mix (the head keeps full quality)"; exit 1; }
  CUT=$(python3 -c "print($FROM/$FPS)")
  echo "== partial render: frames $FROM-$LAST (head kept up to ${CUT}s) =="
  (cd "$TPL" && npx remotion render ReelCutaways "$PROJ/out/span.mp4" --frames="$FROM-$LAST")
  # Head: frame-accurate trim needs a re-encode (stream-copy only cuts on keyframes).
  ffmpeg -y -i "$PROJ/out/reel.mp4" -t "$CUT" \
    -c:v libx264 -crf 15 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 256k \
    -video_track_timescale 90000 "$PROJ/out/head.mp4" -loglevel error
  mv "$PROJ/out/reel.mp4" "$PROJ/out/reel.prev.mp4"
  printf "file 'head.mp4'\nfile 'span.mp4'\n" > "$PROJ/out/concat.txt"
  if ! ffmpeg -y -f concat -safe 0 -i "$PROJ/out/concat.txt" -c copy \
       "$PROJ/out/reel.mp4" -loglevel error; then
    # Copy-concat can fail on param mismatch: re-encode the join as a fallback.
    ffmpeg -y -f concat -safe 0 -i "$PROJ/out/concat.txt" \
      -c:v libx264 -crf 15 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 256k \
      "$PROJ/out/reel.mp4" -loglevel error
  fi
  rm -f "$PROJ/out/span.mp4" "$PROJ/out/head.mp4" "$PROJ/out/concat.txt"
else
  (cd "$TPL" && npx remotion render ReelCutaways "$PROJ/out/reel.mp4" $DRAFT)
fi

# Cover: middle of the first segment (usually the intro collage)
MID=$(python3 -c "
import json
m = json.load(open('$PROJ/mapping.json'))
s = m['segments'][0] if m['segments'] else {'start': 0}
e = s.get('end', m['segments'][1]['start'] if len(m['segments']) > 1 else m['durationInFrames'])
print(round((s['start'] + e) / 2 / m['fps'], 2))")
ffmpeg -y -ss "$MID" -i "$PROJ/out/reel.mp4" -vframes 1 "$PROJ/out/cover.jpg" -loglevel error

# Hand the file over somewhere findable. A path printed in a terminal is not a
# delivery: the user still has to go dig for it. Default lands next to the other
# finished reels; override with PIMP_DELIVER_DIR, disable with PIMP_DELIVER_DIR=off.
DEST="${PIMP_DELIVER_DIR:-$HOME/Desktop/Reels}"
if [ "$DEST" != "off" ]; then
  NAME="$(basename "$PROJ")"
  mkdir -p "$DEST"
  cp "$PROJ/out/reel.mp4" "$DEST/$NAME.mp4"
  [ -f "$PROJ/out/cover.jpg" ] && cp "$PROJ/out/cover.jpg" "$DEST/$NAME.jpg"
  echo "DELIVERED: $DEST/$NAME.mp4"
  # Reveal it, selected, in the file manager — macOS only; elsewhere the path above
  # is the answer and no window is forced open.
  [ "$(uname)" = "Darwin" ] && open -R "$DEST/$NAME.mp4" 2>/dev/null || true
fi

echo "EXPORT OK: $PROJ/out/reel.mp4 (+cover.jpg)"
