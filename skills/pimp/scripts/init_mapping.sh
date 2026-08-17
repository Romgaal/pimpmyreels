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
     '-show_entries', 'stream=r_frame_rate,avg_frame_rate,width,height,nb_frames,start_time',
     '-show_entries', 'format=duration', '-of', 'json', rush],
    capture_output=True, text=True, check=True)
d = json.loads(p.stdout)
st = d['streams'][0]
def rate(v):
    try:
        n, d = v.split('/')
        return int(n) / int(d) if int(d) else 0
    except Exception:
        return 0

r, avg = rate(st.get('r_frame_rate', '0/1')), rate(st.get('avg_frame_rate', '0/1'))
fps = round(r, 3)
if fps == int(fps):
    fps = int(fps)

# Variable frame rate: 'frame = seconds x fps' stops being true and every image drifts.
# Common on phone recordings. Refuse silently guessing — tell the user how to fix it.
if avg and r and abs(r - avg) / r > 0.01:
    print(f"WARNING: variable frame rate detected (r={r:.3f} vs avg={avg:.3f}).")
    print("  Image timing WILL drift. Convert to constant frame rate first:")
    print(f"    ffmpeg -i '{rush}' -vsync cfr -r {round(avg)} -c:v libx264 -crf 15 -c:a copy fixed.mp4")
    print("  Then re-run init_mapping.sh on fixed.mp4.")

# Stream offsets: a non-zero audio/video start shifts the whole reel.
if abs(float(st.get('start_time', 0) or 0)) > 0.02:
    print(f"WARNING: video stream starts at {st['start_time']}s, not 0 — timings may be offset.")
duration = float(d['format']['duration'])
# Ground truth first: the container's own frame count. Falling back to
# int(duration * fps) truncates on float error (40.533*30 = 1215.99 -> 1215),
# clipping the last frame of the reel.
nbf = st.get('nb_frames')
frames = int(nbf) if nbf and str(nbf).isdigit() else round(duration * fps)
mapping = {
    'rush': 'project/' + os.path.basename(rush),
    'fps': fps,
    'width': st['width'],
    'height': st['height'],
    'durationInFrames': frames,
    'subtitlesBurned': False,
    'imageTop': 235,   # below the Instagram UI header (safe zone)
    'imageShadow': False,
    'segments': [],
}
json.dump(mapping, open(os.path.join(proj, 'mapping.json'), 'w'), indent=1)
print(f"mapping.json: fps={fps}  {st['width']}x{st['height']}  "
      f"duration={duration:.2f}s  durationInFrames={frames}")
print("Now fill in `segments` (word-synced starts) and set subtitlesBurned if needed.")
EOF
