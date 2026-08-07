#!/usr/bin/env python3
"""Build ONE numbered contact sheet of every candidate.

usage: build_board.py <project_dir>

Row = beat, columns = candidates, each labelled "beat.candidate" (e.g. 3.2).
The agent reads this single image for QA (never 24 files one by one), and the
same sheet is shown to the human to validate or swap picks by number.
Output: <project_dir>/board.png
"""
import os, sys
from PIL import Image, ImageDraw

proj = sys.argv[1]
cdir = os.path.join(proj, 'candidates')
beats = sorted(d for d in os.listdir(cdir) if os.path.isdir(os.path.join(cdir, d)))

CW, CH, PAD = 400, 226, 30
sheet = Image.new('RGB', (CW * 3 + 32, (CH + PAD) * max(1, len(beats))), (16, 16, 18))
d = ImageDraw.Draw(sheet)

for r, b in enumerate(beats):
    y = r * (CH + PAD)
    d.text((8, y + 9), f'{r+1}. {b}', fill=(255, 210, 90))
    files = sorted(
        f for f in os.listdir(os.path.join(cdir, b))
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    )[:3]
    for c, f in enumerate(files):
        x = c * (CW + 16)
        try:
            im = Image.open(os.path.join(cdir, b, f)).convert('RGB')
            w, h = im.size
            nw = int(w * CH / h)
            im = im.resize((nw, CH))
            if nw >= CW:
                im = im.crop(((nw - CW) // 2, 0, (nw - CW) // 2 + CW, CH))
            sheet.paste(im, (x, y + PAD))
        except Exception:
            pass
        d.rectangle([x, y + PAD, x + 30, y + PAD + 20], fill=(0, 0, 0))
        d.text((x + 6, y + PAD + 5), f'{r+1}.{c+1}', fill=(255, 255, 255))

sheet.save(os.path.join(proj, 'board.png'))
print('board:', os.path.join(proj, 'board.png'), '|', len(beats), 'beats')
