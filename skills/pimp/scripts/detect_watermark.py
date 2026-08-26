#!/usr/bin/env python3
"""usage: detect_watermark.py <image_or_dir> [...]

Flags images carrying a stock/reseller watermark, by READING the text in them.

Why this exists: an image tiled with "ultimateapparels.com" shipped in a user's reel,
twice. It was judged on a contact sheet at ~250px, where a faint repeated overlay is
invisible. Two pixel heuristics were tried first — plain autocorrelation, then with
JPEG-block harmonics excluded — and both were dropped: on real samples they returned
1 true positive for 7 false, then 2 for 7. Guessing at periodicity does not work.
Reading the text does.

Needs tesseract (`brew install tesseract`). Without it the script says so and exits 0
rather than pretending the images are clean.

KNOWN LIMIT, learned the hard way: this is a brand/domain matcher, and a stamp whose
word is not on the list passes. A "Magnific" grid (an AI upscaler) shipped in a reel
while this reported 0/33 — the OCR could not even resolve the glyphs at thumbnail
scale. Token-repetition was tried as a brand-independent second signal and measured
useless on the same image (top token count: 1). Treat this as a net, never as a
guarantee. The real defence is the SOURCE: use `--engine unsplash` for ambiance and
background work, where watermarks do not exist by construction.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageFilter, ImageOps

# Domains and words that only ever appear as an overlay, never as filmed content.
# OCR of a faint stamp is garbled, so match what survives: domain tails (with the
# classic m->n misread), and known stock brands.
MARKS = re.compile(
    r'(\.co[mn]\b|\.ne[tf]\b|www\.|shutterstock|alamy|getty|istock|dreamstime'
    r'|depositphotos|123rf|adobestock|stablediffusion|rarefilm|apparel|fineart|pixels\.com|magnific|upscayl|topaz)',
    re.I)


def read_text(path):
    """OCR a HIGH-PASSED copy: that is what makes a faint stamp legible.

    Autocontrast was tried first and read nothing on a genuinely watermarked image —
    a 15%-opacity overlay is not a contrast problem, it is a frequency one. Subtracting
    a blur strips the photograph and leaves the stamp's thin strokes; tesseract then
    returns garbled but recognisable fragments ("drels.cOn", "ppar", "com").
    """
    out = []
    with Image.open(path) as im:
        im = im.convert('L')
        im.thumbnail((1400, 1400))
        blur = im.filter(ImageFilter.GaussianBlur(6))
        highpass = Image.eval(Image.blend(im, blur, -1.0), lambda p: min(255, max(0, p + 128)))
        unsharp = im.filter(ImageFilter.UnsharpMask(radius=8, percent=350, threshold=2))
        for variant in (highpass, unsharp):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tf:
                variant.save(tf.name)
                try:
                    for psm in ('11', '6'):
                        r = subprocess.run(['tesseract', tf.name, 'stdout', '--psm', psm],
                                           capture_output=True, text=True, timeout=60)
                        out.append(r.stdout)
                finally:
                    os.unlink(tf.name)
    return '\n'.join(out)


def main():
    if not shutil.which('tesseract'):
        print('tesseract introuvable — `brew install tesseract`. Aucune image analysée.')
        return 0
    targets = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            targets += [os.path.join(arg, f) for f in sorted(os.listdir(arg))
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        else:
            targets.append(arg)
    if not targets:
        sys.exit(__doc__)

    bad = []
    for t in targets:
        try:
            txt = read_text(t)
        except Exception as e:
            print(f'  {os.path.basename(t):<26} ERREUR {e}')
            continue
        hits = sorted({m.group(0).lower() for m in MARKS.finditer(txt)})
        # A "repeated token" signal was tried as a second cue and dropped: it fired on
        # a still of a LIFE magazine cover, whose repeated printed word is content, not
        # a stamp. The domain/brand match alone is precise.
        strong = hits
        if strong:
            bad.append(os.path.basename(t))
            print(f'  {os.path.basename(t):<26} FILIGRANE: {", ".join(strong)}')
        else:
            print(f'  {os.path.basename(t):<26} propre')
    print(f'\n{len(bad)}/{len(targets)} filigrané(s)' + (f': {bad}' if bad else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
