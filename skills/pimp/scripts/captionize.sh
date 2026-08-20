#!/bin/bash
# usage: captionize.sh <project_dir> [--template ctpl_xxx] [--list] [--probe ctpl_a,ctpl_b]
#
# Burns styled subtitles onto a finished reel using the Captions API, so the phone
# round-trip (AirDrop -> Captions app -> export -> upload) disappears.
#
# Order matters and is not negotiable: images first, captions LAST. The API returns a
# rendered mp4 only — no SRT, no timings — so nothing can be layered on top afterwards.
#
#   --list             print available caption templates (also proves the key works)
#   --probe a,b,c      caption a 5s sample with each template and MEASURE where the text
#                      lands. A template that writes at y~488 collides with the cutaway
#                      band (235-678) and eats the first word of every line. Pick a low one.
#   --template ctpl_x  caption the real reel and deliver it
#
# Needs CAPTIONS_API_KEY in the environment (dashboard -> API key).
set -e
API="${CAPTIONS_API_BASE:-https://api.mirage.app}"
[ -n "$CAPTIONS_API_KEY" ] || { echo "ERROR: export CAPTIONS_API_KEY=... first"; exit 1; }
H=(-H "x-api-key: $CAPTIONS_API_KEY")

if [ "$1" = "--list" ]; then
  curl -s "${H[@]}" "$API/v1/caption-templates" | python3 -m json.tool
  exit 0
fi

PROJ="$(cd "$1" && pwd)"; shift
TPL=""; PROBE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --template) TPL="$2"; shift ;;
    --probe) PROBE="$2"; shift ;;
    *) echo "unknown flag: $1"; exit 1 ;;
  esac; shift
done
SRC="$PROJ/out/reel.mp4"
[ -f "$SRC" ] || { echo "ERROR: no $SRC — render the reel first"; exit 1; }

# The API caps input at 50MB. CRF 20 is visually near-lossless and lands a 40s
# 1080x1920 reel around 23MB (measured), so this never degrades what you send.
shrink() {
  ffmpeg -y -i "$1" ${3:+-t "$3"} -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p \
    -c:a aac -b:a 192k "$2" -loglevel error
  local mb=$(( $(stat -f%z "$2" 2>/dev/null || stat -c%s "$2") / 1048576 ))
  [ "$mb" -lt 50 ] || { echo "ERROR: $mb MB after compression, API limit is 50 MB"; exit 1; }
  echo "  prepared: ${mb} MB"
}

submit() {   # $1 = file, $2 = template -> prints the finished mp4 path in $3
  local id
  id=$(curl -s "${H[@]}" -F "file=@$1" -F "templateId=$2" "$API/v1/videos/captions" \
       | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")
  [ -n "$id" ] || { echo "ERROR: submit failed (check key / template id)"; exit 1; }
  local st=""
  for _ in $(seq 1 120); do
    sleep 5
    st=$(curl -s "${H[@]}" "$API/v1/videos/$id" \
         | python3 -c "import json,sys; print(json.load(sys.stdin).get('status',''))")
    [ "$st" = "COMPLETE" ] && break
    [ "$st" = "FAILED" ] || [ "$st" = "CANCELLED" ] && { echo "ERROR: job $st"; exit 1; }
  done
  [ "$st" = "COMPLETE" ] || { echo "ERROR: timed out after 10 min"; exit 1; }
  curl -s "${H[@]}" "$API/v1/videos/$id/content" -o "$3"
}

if [ -n "$PROBE" ]; then
  # 5 seconds is enough to see where a template writes, and keeps the bill in cents.
  echo "== probing templates on a 5s sample =="
  shrink "$SRC" /tmp/pmr_sample.mp4 5
  for t in ${PROBE//,/ }; do
    echo "-- $t"
    submit /tmp/pmr_sample.mp4 "$t" "/tmp/pmr_$t.mp4"
    mkdir -p "/tmp/pmr_probe_$t" && cp "/tmp/pmr_$t.mp4" "/tmp/pmr_probe_$t/rush.mp4"
    python3 "$(dirname "$0")/detect_captions.py" "/tmp/pmr_probe_$t" | sed 's/^/     /'
  done
  echo "Pick the template whose band starts BELOW 678 — anything higher covers your images."
  exit 0
fi

[ -n "$TPL" ] || { echo "ERROR: --template required (see --list, then --probe)"; exit 1; }
echo "== captioning $(basename "$PROJ") =="
shrink "$SRC" /tmp/pmr_send.mp4
submit /tmp/pmr_send.mp4 "$TPL" "$PROJ/out/reel-captioned.mp4"

DEST="${PIMP_DELIVER_DIR:-$HOME/Downloads}"
if [ "$DEST" != "off" ]; then
  NAME="$(basename "$PROJ")"
  mkdir -p "$DEST"; cp "$PROJ/out/reel-captioned.mp4" "$DEST/$NAME-sous-titres.mp4"
  echo "DELIVERED: $DEST/$NAME-sous-titres.mp4"
  [ "$(uname)" = "Darwin" ] && open -R "$DEST/$NAME-sous-titres.mp4" 2>/dev/null || true
fi
