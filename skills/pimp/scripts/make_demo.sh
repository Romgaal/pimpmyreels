#!/bin/bash
# Builds demo/rush.mp4 (~15s, synthetic voice) so a new user can run the whole
# pipeline 3 minutes after installing — without filming anything.
# The script is written to hit concepts that exist in the shipped bank.
set -e
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DEMO="$PLUGIN_ROOT/demo"
mkdir -p "$DEMO"

TXT="Tu as oublié une chose : tu as de la valeur. Avec tes potes tu es drôle. Alors prends ton courage, va rencontrer des gens, et fais-leur passer un bon moment."

if command -v say >/dev/null; then
  say -v Thomas -o "$DEMO/voice.aiff" "$TXT"
  AUDIO="$DEMO/voice.aiff"
elif command -v espeak-ng >/dev/null || command -v espeak >/dev/null; then
  ESP=$(command -v espeak-ng || command -v espeak)
  "$ESP" -v fr -w "$DEMO/voice.wav" "$TXT"
  AUDIO="$DEMO/voice.wav"
else
  echo "ERROR: no text-to-speech available (macOS 'say' or 'espeak')."
  echo "Use your own rush instead: /pimp <video>"
  exit 1
fi

ffmpeg -y -f lavfi -i "color=c=0x1a2030:s=1080x1920" -i "$AUDIO" -shortest \
  -c:v libx264 -pix_fmt yuv420p -c:a aac "$DEMO/rush.mp4" -loglevel error
rm -f "$DEMO/voice.aiff" "$DEMO/voice.wav"

echo "demo rush: $DEMO/rush.mp4"
