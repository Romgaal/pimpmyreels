#!/usr/bin/env python3
"""usage: detect_speaker.py <project_dir> [--write]

Finds WHERE THE SPEAKER IS in the frame, then says where a cutaway can go.

Why this exists: cutaway placement was a constant, `imageTop` 310 tuned by hand on one
rush and then applied to every other one. It only ever worked because those rushes were
framed alike. The moment a rush is a close selfie instead of a seated mid-shot, 310
lands on the face and "put them at the bottom instead" lands on the mouth. The frame
has to be measured, not assumed.

How: the speaker is the thing that MOVES — a talking face changes pixels every tenth of
a second while a street, a wall or a bedroom does not. Differencing frame pairs and
summing the change per row gives a profile whose peak is the face. The rows around the
peak that stay above a fraction of it are the speaker's band; what is left above and
below are the free bands.

Instagram furniture is then subtracted from those free bands:
  top    the Reels header ("Reels", camera) is drawn over the first ~200px
  bottom the username, caption and audio ticker occupy the last ~470px
  right  the icon rail (like/comment/share/...) eats ~140px on the right
The result is the largest usable band and the `imageTop` that centres a cutaway in it.

--write stores `imageTop` (and `imageAnchor`) in mapping.json.
"""
import json
import os
import subprocess
import sys
from PIL import Image, ImageChops

STEP = 0.30          # seconds between the two frames of a pair
NOISE = 34           # a talking face moves gradually; this keeps real motion, drops grain
PEAK_FRAC = 0.35     # rows keeping >=35% of the peak change belong to the speaker
HEADER = 310         # Reels header, MEASURED on an iPhone: at 235 the images still fell
                     # under the word "Reels"; 310 is the first row that clears it
FOOTER = 470         # username + caption + audio ticker — the "bio" band
RAIL = 140           # right-hand icon rail
CUT_W = 0.41         # a cutaway is 41% of the width, square
MARGIN = 24          # visual breathing room between the cutaway and the speaker


def frame(video, t, path):
    subprocess.run(['ffmpeg', '-y', '-ss', str(t), '-i', video, '-vframes', '1',
                    path, '-loglevel', 'error'], check=True)
    return Image.open(path).convert('L')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    write = '--write' in sys.argv
    rush = next((os.path.join(proj, f) for f in sorted(os.listdir(proj))
                 if f.startswith('rush.')), None)
    if not rush:
        sys.exit(f'ERROR: no rush.* in {proj}')
    dur = float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', rush],
        capture_output=True, text=True, check=True).stdout)

    rows = None
    W = H = 0
    for i in range(1, 13):
        t = dur * i / 13
        a, b = frame(rush, t, '/tmp/_sp_a.png'), frame(rush, t + STEP, '/tmp/_sp_b.png')
        if a.size != b.size:
            continue
        W, H = a.size
        d = ImageChops.difference(a, b).point(lambda p: 1 if p > NOISE else 0)
        px = d.load()
        if rows is None:
            rows = [0] * H
        for y in range(0, H, 4):
            rows[y] += sum(px[x, y] for x in range(0, W, 6))
    if not rows or max(rows) == 0:
        sys.exit('ERROR: no motion detected — is the rush a still image?')

    peak = max(rows)
    hot = [y for y in range(0, H, 4) if rows[y] >= peak * PEAK_FRAC]
    top, bot = min(hot), max(hot)
    if (bot - top) > H * 0.8:
        # Handheld: the camera shakes, so EVERY row changes and the speaker cannot be
        # separated from the street behind them. Say so — a number invented here would
        # put a cutaway on the person's mouth. Measure the frame by eye instead:
        # scripts/ruler.py draws a graduated grid on a real frame.
        print(f'frame {W}x{H}   motion fills rows {top}-{bot}: THIS RUSH IS HANDHELD.')
        print('  Frame-differencing cannot isolate the speaker when the whole image moves.')
        print('  -> run: python3 scripts/ruler.py <project>   then read off the hair line,')
        print('     the eye line and the shoulder line, and place the cutaway by hand.')
        sys.exit(2)
    cut = round(W * CUT_W)

    free_top = top - MARGIN - HEADER            # usable height above the speaker
    free_bot = (H - FOOTER) - (bot + MARGIN)    # usable height below, above the bio band
    print(f'frame {W}x{H}   speaker rows {top} -> {bot}')
    print(f'  free above: {free_top}px (between the Reels header at {HEADER} and the speaker)')
    print(f'  free below: {free_bot}px (between the speaker and the bio band at {H - FOOTER})')
    print(f'  a square cutaway needs {cut}px')

    choice, image_top = None, None
    if free_top >= cut:
        choice, image_top = 'top', HEADER + (free_top - cut) // 2
    elif free_bot >= cut:
        choice, image_top = 'bottom', bot + MARGIN + (free_bot - cut) // 2
    else:
        # Neither band fits a full square. Take the roomier one and let the template
        # shrink the image into it rather than silently covering the face.
        if free_top >= free_bot:
            choice, image_top = 'top', HEADER
            print(f'  NEITHER band fits: top is roomier ({free_top}px). Shrink to '
                  f'{max(free_top, 0)}px tall, or move the camera back next time.')
        else:
            choice, image_top = 'bottom', bot + MARGIN
            print(f'  NEITHER band fits: bottom is roomier ({free_bot}px). Shrink to '
                  f'{max(free_bot, 0)}px tall.')
    print(f'  -> place {choice.upper()}: imageTop {image_top} '
          f'(cutaway {image_top}-{image_top + cut}, rail-safe width {W - RAIL})')

    if write:
        mp = os.path.join(proj, 'mapping.json')
        m = json.load(open(mp))
        m['imageTop'] = int(image_top)
        m['imageMaxHeight'] = int(max(cut, 0) if (free_top if choice == 'top' else free_bot) >= cut
                                  else max(free_top if choice == 'top' else free_bot, 0))
        json.dump(m, open(mp, 'w'), indent=1)
        print(f'  written: imageTop={image_top}, imageMaxHeight={m["imageMaxHeight"]}')


if __name__ == '__main__':
    main()
