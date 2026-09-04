#!/usr/bin/env python3
"""usage: pinboard.py sync | list | search <words...>

Turns the user's own Pinterest boards into a local, searchable image source.

Why a board and not a search: Pinterest's own search is what makes it a goldmine, and
it is exactly what cannot be reached — the internal /resource/ API returns 403 without
session cookies, /search/pins/ renders in JavaScript, and an automated browser is served
a blank page. Going through Bing's index of Pinterest instead reaches the CDN but not
the taste: measured, "overthinking mind" came back as beach photos and city skylines.

What IS open, with no authentication at all, is the RSS feed of a public board:

    https://www.pinterest.com/<user>/<board>.rss     ->  24 items, 21 images

So the flow inverts. The person browses Pinterest — which they enjoy and are good at —
and pins what they like to a board. This syncs the board down, and those pins become
candidates for future reels, searchable by the words in their titles.

The feed carries /236x/ thumbnails, and every sized variant returns 403 to a plain
client while /originals/ returns 200. Rewriting the size segment is therefore required,
not merely nicer: one measured pin went from 236x158 to 6016x4016.

Boards live in ~/.pimpmyreels/boards.txt, one per line:

    https://www.pinterest.com/romgal/cinema-moody/     | cinema
    https://www.pinterest.com/romgal/abstract-ideas/   | abstrait
    # a leading # comments a line out

The optional tag after | groups pins; without it the board slug is used. Sync is
incremental — a pin already downloaded is skipped — so running it often is cheap.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

HOME = os.path.expanduser('~/.pimpmyreels')
BOARDS = os.path.join(HOME, 'boards.txt')
PINS = os.path.join(HOME, 'pins')
INDEX = os.path.join(PINS, 'index.json')
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/124 Safari/537.36'}


def get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def variants(url):
    """Every form of a pin URL worth trying, biggest first.

    /originals/ is the full-resolution pin — one measured feed thumbnail went from
    236x158 to 6016x4016 through this rewrite. But not every pin HAS an original
    (about half, measured on a 24-pin feed), so fall back through the large sized
    variants before giving up. Sizes fabricated with the wrong extension 403; these are
    built from the feed's own URL, so the extension is right."""
    out = [re.sub(r'i\.pinimg\.com/\d+x\d*/', 'i.pinimg.com/originals/', url)]
    for size in ('1200x', '736x', '564x'):
        v = re.sub(r'i\.pinimg\.com/\d+x\d*/', f'i.pinimg.com/{size}/', url)
        if v not in out:
            out.append(v)
    if url not in out:
        out.append(url)
    return out


def load_index():
    if os.path.exists(INDEX):
        return json.load(open(INDEX))
    return {}


def read_boards():
    if not os.path.exists(BOARDS):
        os.makedirs(HOME, exist_ok=True)
        open(BOARDS, 'w').write(
            '# One Pinterest board per line. Optional "| tag" groups the pins.\n'
            '# The board must be PUBLIC — that is all it takes, no login anywhere.\n'
            '# https://www.pinterest.com/<user>/<board>/   | tag\n')
        sys.exit(f'created {BOARDS} — add your boards to it, then run sync again.')
    out = []
    for line in open(BOARDS):
        line = line.split('#')[0].strip()
        if not line:
            continue
        url, _, tag = line.partition('|')
        url = url.strip().rstrip('/')
        slug = url.rsplit('/', 1)[-1]
        out.append((url, (tag.strip() or slug)))
    return out


def cmd_sync():
    boards = read_boards()
    if not boards:
        sys.exit(f'{BOARDS} has no boards in it.')
    idx = load_index()
    os.makedirs(PINS, exist_ok=True)
    added = skipped = failed = 0
    for url, tag in boards:
        try:
            raw = get(url + '.rss')
        except Exception as e:
            print(f'{tag}: FEED UNREACHABLE ({type(e).__name__}) — is the board public?')
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            print(f'{tag}: the feed is not XML — check the board URL')
            continue
        items = root.findall('.//item')
        print(f'{tag}: {len(items)} pins in the feed')
        for it in items:
            title = (it.findtext('title') or '').strip()
            desc = (it.findtext('description') or '')
            link = (it.findtext('link') or '').strip()
            m = re.search(r'https://i\.pinimg\.com/[^"\'<>\s]+\.(?:jpg|jpeg|png)', desc)
            if not m:
                continue
            cands = variants(m.group(0))
            key = hashlib.sha1(cands[0].encode()).hexdigest()[:16]
            if key in idx and os.path.exists(os.path.join(PINS, idx[key]['file'])):
                skipped += 1
                continue
            data = src = None
            for c in cands:
                try:
                    data = get(c)
                    src = c
                    break
                except Exception:
                    continue
            if data is None:
                failed += 1
                continue
            d = os.path.join(PINS, tag)
            os.makedirs(d, exist_ok=True)
            rel = os.path.join(tag, key + os.path.splitext(src)[1].split('?')[0])
            open(os.path.join(PINS, rel), 'wb').write(data)
            # The title is the only text a pin reliably carries, and it is what makes
            # the pin findable later. Strip the HTML the feed wraps it in.
            clean = re.sub(r'<[^>]+>', ' ', desc)
            idx[key] = {'file': rel, 'tag': tag, 'title': title,
                        'text': ' '.join((title + ' ' + clean).split())[:300],
                        'link': link, 'src': src}
            added += 1
    json.dump(idx, open(INDEX, 'w'), indent=1, ensure_ascii=False)
    print(f'\n{added} new, {skipped} already had, {failed} failed. {len(idx)} pins total in {PINS}')


def cmd_list():
    idx = load_index()
    if not idx:
        sys.exit('no pins yet — run: pinboard.py sync')
    tags = {}
    for v in idx.values():
        tags.setdefault(v['tag'], []).append(v)
    for t, v in sorted(tags.items()):
        print(f'{t:<20} {len(v):>4} pins')
    print(f'{"TOTAL":<20} {len(idx):>4}')


def score(entry, words):
    """Word overlap with the pin's own text. Deliberately simple: a board is curated,
    so the useful signal is 'does this pin mention what the beat is about', not a
    ranking model."""
    text = entry['text'].lower()
    return sum(1 for w in words if w in text)


def search(query, n=3):
    idx = load_index()
    words = [w for w in re.findall(r'[a-zà-ÿ]{3,}', query.lower())]
    scored = [(score(v, words), v) for v in idx.values()]
    scored = [(s, v) for s, v in scored if s > 0]
    scored.sort(key=lambda x: -x[0])
    return [os.path.join(PINS, v['file']) for _, v in scored[:n]]


def cmd_search(args):
    hits = search(' '.join(args), 8)
    if not hits:
        print('no pin matches — sync more boards, or the wording does not appear in any '
              'pin title. pinboard.py list shows what you have.')
        return
    for h in hits:
        print(h)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('sync', 'list', 'search'):
        sys.exit(__doc__)
    if sys.argv[1] == 'search':
        cmd_search(sys.argv[2:])
    else:
        globals()['cmd_' + sys.argv[1]]()
