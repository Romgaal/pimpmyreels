#!/usr/bin/env python3
"""usage: ruler.py <project_dir> [seconds]

Draws a graduated grid over one frame of the rush and saves it as ruler.png, so the
speaker's hair line, eye line and shoulder line can be READ instead of estimated.

Use it whenever detect_speaker.py reports a handheld rush, or whenever a placement
looks wrong. Reference lines drawn: the Reels header (310, measured — at 235 images
still fell under the word), the bio band (from H-470: username, caption, audio ticker)
and the right icon rail (140px).
"""
import os
import subprocess
import sys
from PIL import Image, ImageDraw

HEADER, FOOTER, RAIL = 310, 470, 140


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    t = sys.argv[2] if len(sys.argv) > 2 else None
    rush = next((os.path.join(proj, f) for f in sorted(os.listdir(proj))
                 if f.startswith('rush.')), None)
    if not rush:
        sys.exit(f'ERROR: no rush.* in {proj}')
    if t is None:
        dur = float(subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', rush],
            capture_output=True, text=True, check=True).stdout)
        t = f'{dur / 3:.2f}'
    subprocess.run(['ffmpeg', '-y', '-ss', str(t), '-i', rush, '-vframes', '1',
                    '/tmp/_ruler.png', '-loglevel', 'error'], check=True)
    im = Image.open('/tmp/_ruler.png').convert('RGB')
    W, H = im.size
    d = ImageDraw.Draw(im)
    for y in range(0, H, 100):
        d.line([0, y, W, y], fill=(255, 255, 0) if y % 500 else (255, 120, 0),
               width=2 if y % 500 else 4)
        d.rectangle([0, y, 120, y + 34], fill=(0, 0, 0))
        d.text((8, y + 8), str(y), fill=(255, 255, 0))
    d.line([0, HEADER, W, HEADER], fill=(255, 0, 0), width=6)
    d.line([0, H - FOOTER, W, H - FOOTER], fill=(255, 0, 0), width=6)
    d.line([W - RAIL, 0, W - RAIL, H], fill=(0, 200, 255), width=5)
    out = os.path.join(proj, 'ruler.png')
    im.save(out)
    print(f'{out}  ({W}x{H} at t={t}s)')
    print(f'  red   {HEADER}      Reels header ends here — nothing above it')
    print(f'  red   {H - FOOTER}  bio band starts here — nothing below it')
    print(f'  cyan  x={W - RAIL}  icon rail — nothing to its right')
    print('  Read off the hair line, the eye line and the shoulder line, then set')
    print('  imageTop so the cutaway ends ABOVE the eyes.')


if __name__ == '__main__':
    main()
