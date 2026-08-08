#!/bin/bash
# usage: init_mapping.sh <project_dir>
# Probes the project's rush with ffprobe and writes a CORRECT mapping.json skeleton:
# real fps (from r_frame_rate), width/height, durationInFrames = floor(duration × fps).
# Never hand-write those numbers — a wrong fps desyncs every image, a wrong
# durationInFrames cuts the reel short. Existing mapping.json is backed up.
set -e
PROJ="$(cd "$1" && pwd)"

RUSH=""
for f in "$PROJ"/rush.*; do [ -f "$f" ] && RUSH="$f" && break; done
[ -n "$RUSH" ] || { echo "ERROR: no rush.* found in $PROJ"; exit 1; }

[ -f "$PROJ/mapping.json" ] && cp "$PROJ/mapping.json" "$PROJ/mapping.json.bak" \
  && echo "(existing mapping.json backed up to mapping.json.bak)"

RUSH="$RUSH" PROJ="$PROJ" python3 <<'EOF'
import json, os, subprocess
rush, proj = os.environ['RUSH'], os.environ['PROJ']
p = subprocess.run(
    ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
     '-show_entries', 'stream=r_frame_rate,width,height',
     '-show_entries', 'format=duration', '-of', 'json', rush],
    capture_output=True, text=True, check=True)
d = json.loads(p.stdout)
st = d['streams'][0]
num, den = st['r_frame_rate'].split('/')
fps = round(int(num) / int(den), 3)
if fps == int(fps):
    fps = int(fps)
duration = float(d['format']['duration'])
frames = int(duration * fps)  # floor: never exceed the rush
mapping = {
    'rush': 'project/' + os.path.basename(rush),
    'fps': fps,
    'width': st['width'],
    'height': st['height'],
    'durationInFrames': frames,
    'subtitlesBurned': False,
    'imageTop': 118,
    'segments': [],
}
json.dump(mapping, open(os.path.join(proj, 'mapping.json'), 'w'), indent=1)
print(f"mapping.json: fps={fps}  {st['width']}x{st['height']}  "
      f"duration={duration:.2f}s  durationInFrames={frames}")
print("Now fill in `segments` (word-synced starts) and set subtitlesBurned if needed.")
EOF
