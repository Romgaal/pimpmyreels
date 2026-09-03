#!/usr/bin/env python3
"""usage: validate_picks.py <project_dir> [--sheet-only]

THE semantic gate. export.sh refuses to render until this has passed on the CURRENT
brief.json + mapping.json (a stamp carries their hash; touch either and it is void).

What it enforces — each rule is a shipped failure:

  shows      For every picked image, the brief must carry `shows`: 2+ words naming
             what is LITERALLY in the frame, written AFTER looking at the image at
             380px or more. Not the concept searched — the content. A reel shipped
             where "name badges" were restaurant menu clipboards and "a dismissal" was
             two men playing chess: every pick was made off a 200px thumbnail and
             assumed right because it sat in a folder named after the concept.
  ban        `shows` may not describe an abstract or generic image (gradient, texture,
             pattern, shape, silhouette, stranger portrait, generic object). A pink
             gradient for "spiritual" and a cardboard box for "putting yourself in a
             box" both passed every mechanical check and were both rightly called
             garbage by the person who has to publish them.
  mix        culture (film/meme/gif/icon) must be 50-90% of picked beats.
  unique     no image on two beats.
  size       short side >= 400px in mode 1 (a 443px cell), >= 1000px in mode 2 (full frame).

--sheet-only  builds picks_sheet.png (sentence + shows under each image at 380px) and
              skips the stamp — use it to LOOK before writing `shows`.
"""
import hashlib
import json
import os
import re
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Anchored on BOTH sides, and NAMED objects escape: an early version lacked the closing
# \b and refused "Jim Carrey" (carr[ée]) and "Rubik's cube" (cube); a later one refused
# "boîte de chocolats" (Forrest Gump's own prop) on the bare-box rule. The net exists to
# catch a LAZY abstraction — "a cardboard box" standing in for "putting yourself in a
# box" — not a named object that IS the reference. So "box"/"boîte" only fire when
# nothing follows them: "boîte de chocolats" and "box of chocolates" pass, "une boîte"
# does not.
BAN = re.compile(r"\b(gradient|d[ée]grad[ée]|texture|pattern|motif|abstract|abstrait|blur|"
                 r"flou|bokeh|silhouette|shape|forme|rectangle|square|carr[ée]s?|stranger|"
                 r"inconnu|random|generic|g[ée]n[ée]rique|stock|cardboard|carton|"
                 r"box(?! of \w)|bo[iî]tes?(?! (de|à) \w)|"
                 r"mug|cup|tasse|fabric|tissu|(?<![Rr]ubik.s )cubes?|colou?r field|aplat|wall|"
                 r"mur|portrait of a (man|woman)|portrait d.un)\b", re.I)
CULTURE = {'film', 'meme', 'gif', 'icon'}
CELL = 380


def font(size):
    for p in ('/System/Library/Fonts/Helvetica.ttc', '/Library/Fonts/Arial.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def stamp_value(proj):
    h = hashlib.sha256()
    for n in ('mapping.json', 'brief.json'):
        h.update(open(os.path.join(proj, n), 'rb').read())
    return h.hexdigest()


def resolve(proj, rel):
    # mapping paths are 'project/<x>' relative to the template's public dir
    return os.path.join(proj, rel[len('project/'):] if rel.startswith('project/') else rel)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    sheet_only = '--sheet-only' in sys.argv
    brief = json.load(open(os.path.join(proj, 'brief.json')))
    mapping = json.load(open(os.path.join(proj, 'mapping.json')))
    # A mode-1 cutaway is drawn 41% of the frame wide (443px on 1080): a 400px short
    # side is a 1.1x upscale nobody can see on a phone. A mode-2 background fills the
    # frame and needs the real thing.
    min_side = 1000 if mapping.get('mode') == 'background' else 400
    beats = [b for b in brief['beats'] if not b.get('skip') and b.get('image')]
    errs = []
    seen = {}
    cells = []
    for i, b in enumerate(beats):
        tag = f'@{b["start"]:.2f}s "{b["sentence"][:38]}"'
        path = resolve(proj, b['image'])
        if not os.path.exists(path):
            errs.append(f'{tag}: {b["image"]} does not exist')
            continue
        im = Image.open(path)
        if min(im.size) < min_side:
            errs.append(f'{tag}: {os.path.basename(path)} is {im.size[0]}x{im.size[1]} — short '
                        f'side under {min_side}px for this mode')
        if b['image'] in seen:
            errs.append(f'{tag}: same image as beat @{seen[b["image"]]:.2f}s')
        seen[b['image']] = b['start']
        shows = (b.get('shows') or '').strip()
        if not sheet_only:
            if len(shows.split()) < 2:
                errs.append(f'{tag}: `shows` missing — look at the image at 380px and write '
                            f'what is literally in it')
            elif shows.lower() in (b.get('query', '').lower(), b.get('scene', '').lower()):
                errs.append(f'{tag}: `shows` is a copy of query/scene — that is not looking')
            elif BAN.search(shows):
                errs.append(f'{tag}: `shows` = "{shows}" describes an abstract or generic '
                            f'image. Reject it and find the human moment or the reference.')
        cells.append((b, im.convert('RGB'), shows))
    if beats and not sheet_only:
        cult = sum(1 for b in beats if b.get('register') in CULTURE)
        share = cult / len(beats)
        if not 0.50 <= share <= 0.90:
            errs.append(f'mix: {cult}/{len(beats)} culture beats ({share:.0%}) — must be 50-90%. '
                        f'Cinema is the base material, photography is the breathing space.')

    # The sheet: sentence ABOVE, shows BELOW. Reading the two lines against the picture
    # is the whole test — if the picture needs the folder name to make sense, it fails.
    cols = 4
    rows = (len(cells) + cols - 1) // cols
    head, foot = 46, 40
    W, H = CELL * cols, (CELL + head + foot) * max(rows, 1)
    sheet = Image.new('RGB', (W, H), (14, 14, 16))
    d = ImageDraw.Draw(sheet)
    f_s, f_b = font(15), font(14)
    for k, (b, im, shows) in enumerate(cells):
        r, c = divmod(k, cols)
        x, y = c * CELL, r * (CELL + head + foot)
        lines = textwrap.wrap(f'{b["start"]:.1f}s  {b["sentence"]}', 46)[:2]
        for j, ln in enumerate(lines):
            d.text((x + 6, y + 4 + j * 19), ln, fill=(240, 240, 240), font=f_s)
        w, h = im.size
        k2 = min(w, h)
        sq = im.crop(((w - k2) // 2, (h - k2) // 2, (w + k2) // 2, (h + k2) // 2)).resize((CELL, CELL))
        sheet.paste(sq, (x, y + head))
        tag = f'[{b.get("register", "?")}] {shows or "— shows: not written —"}'
        d.text((x + 6, y + head + CELL + 4), textwrap.shorten(tag, 52), fill=(255, 205, 80), font=f_b)
    out = os.path.join(proj, 'picks_sheet.png')
    sheet.save(out)
    print(f'sheet: {out}  ({len(cells)} picks at {CELL}px)')

    if errs:
        print('PICKS REFUSED:')
        for e in errs:
            print('  -', e)
        try:
            os.remove(os.path.join(proj, '.picks-ok'))
        except FileNotFoundError:
            pass
        sys.exit(1)
    if sheet_only:
        print('sheet only — now write `shows` for every pick, then run without --sheet-only.')
        return
    open(os.path.join(proj, '.picks-ok'), 'w').write(stamp_value(proj))
    cult = sum(1 for b in beats if b.get('register') in CULTURE)
    print(f'PICKS OK: {len(beats)} beats, {cult} culture ({cult / len(beats):.0%}). '
          f'Stamp written — export.sh will accept this exact brief + mapping.')


if __name__ == '__main__':
    main()
