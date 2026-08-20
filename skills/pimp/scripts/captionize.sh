#!/bin/bash
# usage: captionize.sh <project_dir> --template ctpl_xxx
#        captionize.sh --list
#        captionize.sh <project_dir> --probe ctpl_a,ctpl_b,...
#
# Burns styled subtitles onto a finished reel with the Captions API, replacing the
# phone round-trip (AirDrop -> Captions app -> export -> upload).
#
# Order is fixed: images first, captions LAST. The API returns a rendered mp4 only —
# no SRT, no word timings — so nothing can be layered on afterwards.
#
# Every endpoint and field name below was verified against the live API; the published
# docs disagree on three of them (see comments). Needs CAPTIONS_API_KEY.
set -e
A="${CAPTIONS_API_BASE:-https://api.mirage.app}"
[ -n "$CAPTIONS_API_KEY" ] && : || { \
  [ -f "$HOME/.config/pimpmyreels/env" ] && . "$HOME/.config/pimpmyreels/env"; }
[ -n "$CAPTIONS_API_KEY" ] || { echo "ERROR: set CAPTIONS_API_KEY (or put it in ~/.config/pimpmyreels/env)"; exit 1; }
K=(-H "x-api-key: $CAPTIONS_API_KEY")

# Templates live under /v1/videos/captions/templates — NOT /v1/caption-templates.
if [ "$1" = "--list" ]; then
  curl -s "${K[@]}" "$A/v1/videos/captions/templates" | python3 -c "
import json,sys
for r in json.load(sys.stdin)['data']: print(f\"  {r['name']:<22} {r['id']}\")"
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

# The API caps input at 50MB. CRF 20 is visually near-lossless and takes a 37s
# 1080x1920 reel from 62MB to 23MB (measured), so this never costs visible quality.
prep() { # src, dst, [seconds]
  ffmpeg -y ${3:+-ss 20 -t "$3"} -i "$1" -c:v libx264 -crf 20 -preset ${3:+fast}${3:-slow} \
    -pix_fmt yuv420p -c:a aac -b:a 192k "$2" -loglevel error
  local mb=$(( $(stat -f%z "$2" 2>/dev/null || stat -c%s "$2") / 1048576 ))
  [ "$mb" -lt 50 ] || { echo "ERROR: ${mb}MB after compression, API limit is 50MB"; exit 1; }
}

run() { # file, template, out  — POST field names are 'video' and 'caption_template_id'
  local id st
  id=$(curl -s "${K[@]}" -F "video=@$1" -F "caption_template_id=$2" \
       "$A/v1/videos/captions" | python3 -c "
import json,sys
d=json.load(sys.stdin)
# 'error' is present and null on success — truthiness, not membership.
if d.get('error'): sys.exit('API: '+d['error']['message'])
print(d['id'])")
  for _ in $(seq 1 60); do
    sleep 6
    st=$(curl -s "${K[@]}" "$A/v1/videos/$id" | python3 -c "import json,sys;print(json.load(sys.stdin)['status'])")
    case "$st" in COMPLETE) break ;; FAILED|CANCELLED) echo "ERROR: job $st"; exit 1 ;; esac
  done
  [ "$st" = "COMPLETE" ] || { echo "ERROR: timed out"; exit 1; }
  curl -s -L "${K[@]}" "$A/v1/videos/$id/content" -o "$3"
}

if [ -n "$PROBE" ]; then
  # Probe on the RAW RUSH, never on the finished reel. detect_captions.py finds text by
  # differencing frame pairs, and a cutaway CHANGING between them has the same signature
  # as a word changing — on a reel with images it reports the cutaway band as captions.
  # Measured the wrong way: "collision at y529". Measured on the rush: y1277. Same file.
  echo "== probing on the raw rush, 5s =="
  prep "$PROJ/rush.mp4" /tmp/pmr_raw.mp4 5
  for t in ${PROBE//,/ }; do
    rm -rf "/tmp/pmr_pb_$t"; mkdir -p "/tmp/pmr_pb_$t"
    run /tmp/pmr_raw.mp4 "$t" "/tmp/pmr_pb_$t/rush.mp4"
    echo "-- $t"
    python3 "$(dirname "$0")/detect_captions.py" "/tmp/pmr_pb_$t" | sed -n '2,3p' | sed 's/^/   /'
  done
  echo "Keep a template whose band starts BELOW 678 — higher would sit on your cutaways."
  exit 0
fi

[ -n "$TPL" ] || { echo "ERROR: --template required (see --list, then --probe)"; exit 1; }
[ -f "$PROJ/out/reel.mp4" ] || { echo "ERROR: render the reel first"; exit 1; }
echo "== captioning $(basename "$PROJ") =="
prep "$PROJ/out/reel.mp4" /tmp/pmr_send.mp4
run /tmp/pmr_send.mp4 "$TPL" "$PROJ/out/reel-captioned.mp4"

DEST="${PIMP_DELIVER_DIR:-$HOME/Downloads}"
if [ "$DEST" != "off" ]; then
  N="$(basename "$PROJ")"; mkdir -p "$DEST"
  cp "$PROJ/out/reel-captioned.mp4" "$DEST/$N-sous-titres.mp4"
  echo "DELIVERED: $DEST/$N-sous-titres.mp4"
  [ "$(uname)" = "Darwin" ] && open -R "$DEST/$N-sous-titres.mp4" 2>/dev/null || true
fi
