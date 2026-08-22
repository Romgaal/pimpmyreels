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
  # Never splice onto a drifted base: two consecutive splices once compounded a
  # one-frame loss into two (1722 -> 1721 -> 1720), shifting every image after the
  # cut. If the existing reel does not match the mapping exactly, re-render fully.
  HAVE=$(ffprobe -v error -select_streams v:0 -count_frames \
         -show_entries stream=nb_read_frames -of default=nk=1:nw=1 "$PROJ/out/reel.mp4")
  WANT=$(python3 -c "import json;print(json.load(open('$PROJ/mapping.json'))['durationInFrames'])")
  [ "$HAVE" = "$WANT" ] || { echo "ERROR: out/reel.mp4 has $HAVE frames, mapping says $WANT — drifted base, run a FULL export first"; exit 1; }
  [ -n "$DRAFT" ] && { echo "ERROR: --from and --draft don't mix (the head keeps full quality)"; exit 1; }
  CUT=$(python3 -c "print($FROM/$FPS)")
  echo "== partial render: frames $FROM-$LAST (head kept up to ${CUT}s) =="
  (cd "$TPL" && npx remotion render ReelCutaways "$PROJ/out/span.mp4" --frames="$FROM-$LAST")
  # Head: frame-accurate trim needs a re-encode (stream-copy only cuts on keyframes).
  # Trim the VIDEO by frame count, not seconds: -t $CUT once produced a 233-frame head
  # where 234 were asked (encoder rounding), silently shifting everything after the
  # splice by one frame. -frames:v is exact; -t stays for the audio only.
  ffmpeg -y -i "$PROJ/out/reel.mp4" -frames:v "$FROM" -t "$CUT" \
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
# delivery: the user still has to go dig for it. Downloads is where rushes arrive and
# where people already look, so that is where the finished reel goes.
# Override with PIMP_DELIVER_DIR, disable with PIMP_DELIVER_DIR=off.
DEST="${PIMP_DELIVER_DIR:-$HOME/Downloads}"
if [ "$DEST" != "off" ]; then
  # The '-reel' suffix is a safety belt, not decoration. Delivering as "<project>.mp4"
  # destroyed a user's source video: the project was named 'film', the rush had come
  # from ~/Downloads/film.mp4, and the export wrote straight over it. Recoverable only
  # because the pipeline keeps its own copy of the rush.
  NAME="$(basename "$PROJ")-reel"
  mkdir -p "$DEST"
  TARGET="$DEST/$NAME.mp4"
  # Belt and braces: never write onto any file this project reads from.
  for guard in "$PROJ"/rush.*; do
    [ -e "$guard" ] || continue
    if [ "$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")" = \
         "$(cd "$(dirname "$guard")" && pwd)/$(basename "$guard")" ]; then
      echo "REFUSING to deliver: $TARGET is this project's source file"; exit 1
    fi
  done
  cp "$PROJ/out/reel.mp4" "$TARGET"
  [ -f "$PROJ/out/cover.jpg" ] && cp "$PROJ/out/cover.jpg" "$DEST/$NAME.jpg"
  echo "DELIVERED: $TARGET"
  # Reveal it, selected, in the file manager — macOS only; elsewhere the path above
  # is the answer and no window is forced open.
  [ "$(uname)" = "Darwin" ] && open -R "$TARGET" 2>/dev/null || true
fi

echo "EXPORT OK: $PROJ/out/reel.mp4 (+cover.jpg)"
