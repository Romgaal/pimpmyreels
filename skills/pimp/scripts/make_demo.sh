#!/bin/bash
# Builds demo/rush.mp4 (~15s, synthetic voice) so a new user can run the whole
# pipeline 3 minutes after installing — without filming anything.
# The script is written to hit concepts that exist in the shipped bank.
set -e
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DEMO="$PLUGIN_ROOT/demo"
mkdir -p "$DEMO"

TXT_FR="Tu as oublié une chose : tu as de la valeur. Avec tes potes tu es drôle. Alors prends ton courage, va rencontrer des gens, et fais-leur passer un bon moment."
TXT_EN="You forgot one thing: you have value. With your friends, you are funny. So take your courage, go meet people, and give them a good time."

if command -v say >/dev/null; then
  # macOS quietly falls back to the default voice when the requested one is missing,
  # which would read French text with an English voice. Pick explicitly instead:
  # Thomas if present, else any installed fr_* voice, else default voice + English text.
  VOICE=""
  if say -v '?' | grep -q "^Thomas "; then
    VOICE="Thomas"
  else
    VOICE=$(say -v '?' | grep " fr_" | head -1 | sed 's/ *[a-z][a-z]_[A-Z][A-Z].*//')
  fi
  if [ -n "$VOICE" ]; then
    echo "voice: $VOICE (French)"
    say -v "$VOICE" -o "$DEMO/voice.aiff" "$TXT_FR"
  else
    echo "voice: system default (no French voice installed) — using English text"
    say -o "$DEMO/voice.aiff" "$TXT_EN"
  fi
  AUDIO="$DEMO/voice.aiff"
elif command -v espeak-ng >/dev/null || command -v espeak >/dev/null; then
  ESP=$(command -v espeak-ng || command -v espeak)
  "$ESP" -v fr -w "$DEMO/voice.wav" "$TXT_FR" 2>/dev/null || "$ESP" -w "$DEMO/voice.wav" "$TXT_EN"
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
