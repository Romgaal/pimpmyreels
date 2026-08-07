#!/bin/bash
# pimpmyreels — environment check. Tells you exactly what to fix.
PLUGIN_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FAIL=0

chk() {
  if eval "$2" >/dev/null 2>&1; then
    echo "OK   $1"
  else
    echo "FAIL $1 → fix: $3"
    FAIL=1
  fi
}

chk ffmpeg          "command -v ffmpeg"        "brew install ffmpeg"
chk whisper-cli     "command -v whisper-cli"   "brew install whisper-cpp"
chk node            "node --version"           "brew install node"
chk pillow          "python3 -c 'import PIL'"  "pip3 install pillow"
chk whisper-model   "test -f $HOME/.pimpmyreels/models/ggml-small.bin" "bash skills/pimp/scripts/setup.sh"
chk template-deps   "test -d $PLUGIN_ROOT/template/node_modules"       "bash skills/pimp/scripts/setup.sh"
chk template-render "cd $PLUGIN_ROOT/template && npx remotion still ReelCutaways /tmp/pimp-doctor.png --frame=0" \
                    "check template/mapping.json and template/public/project assets"

if gh auth status >/dev/null 2>&1; then
  echo "OK   gh (bank contributions enabled)"
else
  echo "WARN gh not authenticated → bank contributions disabled (optional): gh auth login"
fi

if [ $FAIL -eq 0 ]; then
  echo "== ALL CHECKS PASSED =="
else
  echo "== FIX THE FAILURES ABOVE, THEN RERUN =="
fi
exit $FAIL
