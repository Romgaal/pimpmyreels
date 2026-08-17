#!/usr/bin/env python3
"""usage: detect_captions.py <project_dir> [--write]

Finds where burned-in subtitles (Captions app, CapCut, Opus...) sit in the rush.

Why this exists: a rush that already has captions burned in HIGH puts text exactly
where the cutaways go (235-678). The images then eat the first word of every line —
shipped once, caught only by reading the frames. Measure, never eyeball.

How: burned captions change word-by-word while the filmed background moves smoothly.
Differencing consecutive frames makes the caption band spike as a narrow, high-contrast
horizontal cluster. No numpy needed.

--write stores `captionsTop` in mapping.json; the template then fits every overlay
above the band instead of covering it.
"""
import json
import os
import subprocess
import sys
from PIL import Image, ImageChops

STEP = 0.35          # seconds between the two frames of a pair (a word changes in ~0.3s)
MIN_ROW_HITS = 20    # pixels changed on a row before it counts as text
NOISE = 180          # HIGH on purpose: a moving face changes pixels gradually, swapping
                     # text changes them from sky-white to near-black. Calibrated on a real
                     # Captions rush: 60 catches the whole body, 180 isolates the text band.
MAX_BAND = 0.30      # a "band" taller than 30% of the frame is a moving subject, not text


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

    samples = [dur * i / 11 for i in range(1, 11)]
    tops, bottoms, votes = [], [], 0
    W = H = 0
    for t in samples:
        a = frame(rush, t, '/tmp/_pmr_a.png')
        b = frame(rush, t + STEP, '/tmp/_pmr_b.png')
        if a.size != b.size:
            continue
        W, H = a.size
        d = ImageChops.difference(a, b).point(lambda p: 255 if p > NOISE else 0)
        px = d.load()
        # Ignore the extreme edges: platform UI and frame borders are not captions.
        rows = []
        for y in range(int(H * 0.08), int(H * 0.92), 2):
            hits = sum(1 for x in range(int(W * 0.08), int(W * 0.92), 2) if px[x, y])
            if hits >= MIN_ROW_HITS:
                rows.append(y)
        if len(rows) < 8:
            continue
        # Densest contiguous cluster = the caption block (a moving head is broader/sparser).
        best, cur = [], [rows[0]]
        for y in rows[1:]:
            if y - cur[-1] <= 24:
                cur.append(y)
                continue
            if len(cur) > len(best):
                best = cur
            cur = [y]
        if len(cur) > len(best):
            best = cur
        if len(best) >= 8 and (best[-1] - best[0]) < H * MAX_BAND:
            tops.append(best[0])
            bottoms.append(best[-1])
            votes += 1

    if votes < 3:
        print('No burned-in caption band detected (or captions sit low enough).')
        print('  -> leave captionsTop out of mapping.json; standard geometry applies.')
        return

    # Sampling sees 10 frames, not 1200: the tallest caption line of the whole video is
    # almost certainly higher than anything sampled (measured: detection 517 vs 488 by
    # hand, same rush). captionsTop therefore means "nothing may go below this", not
    # "the exact top of the band" — the template can then use a purely visual margin.
    SLACK = 30
    top, bottom = min(tops) - SLACK, max(bottoms)
    print(f'Burned captions detected on {votes}/{len(samples)} samples')
    print(f'  band: y {min(tops)} -> {bottom}  (frame {W}x{H})  '
          f'-> captionsTop {top} with {SLACK}px sampling slack')
    cut_top, cut_bot = 235, 235 + round(W * 0.41)
    if top < cut_bot:
        print(f'  COLLISION: the standard cutaway band is {cut_top}-{cut_bot} '
              f'-> {cut_bot - top}px of your captions would be covered.')
        print(f'  -> set "captionsTop": {top} in mapping.json (or run with --write):')
        print('     overlays are then fitted above the band, nothing is hidden.')
        print('  -> BEST result: re-export the rush with captions placed LOW '
              '(lower third), or run /pimp BEFORE adding captions.')
    else:
        print('  No collision with the cutaway band. Nothing to do.')

    if write:
        mp = os.path.join(proj, 'mapping.json')
        m = json.load(open(mp))
        m['captionsTop'] = top
        json.dump(m, open(mp, 'w'), indent=1)
        print(f'  written: captionsTop={top} in mapping.json')


if __name__ == '__main__':
    main()
