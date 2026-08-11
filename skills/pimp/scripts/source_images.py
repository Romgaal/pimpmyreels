#!/usr/bin/env python3
"""Source candidate images for one beat.

usage: source_images.py --query "Q" --concept NAME --out DIR [--candidates 3] [--gif] [--reject DOMAIN]

Lookup order: user bank (~/.pimpmyreels/mybank) -> bank/core -> bank/community -> cache -> web.
Web results are filtered: blocklist domains, min resolution, landscape preference, letterbox rejection.
"""
import argparse, hashlib, io, json, os, re, shutil, sys, urllib.request, urllib.parse
from PIL import Image

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
HOME = os.path.expanduser('~/.pimpmyreels')
UA = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36',
    'Referer': 'https://www.bing.com/',
}


def blocklist():
    doms = set()
    for p in (os.path.join(PLUGIN_ROOT, 'skills/pimp/data/blocklist.txt'),
              os.path.join(HOME, 'blocklist-learned.txt')):
        if os.path.exists(p):
            doms |= {l.strip().lower() for l in open(p) if l.strip() and not l.startswith('#')}
    return doms


def learn(domain):
    os.makedirs(HOME, exist_ok=True)
    with open(os.path.join(HOME, 'blocklist-learned.txt'), 'a') as f:
        f.write(domain.strip().lower() + '\n')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def used_hashes():
    """Images already used in previous reels: {hash: {count, last}}. Drives variety."""
    p = os.path.join(HOME, 'used.json')
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            return {}
    return {}


def fetch(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def engine_bing(q, gif=False, fmt='square'):
    if gif:
        f = '+filterui:photo-animatedgif'
    else:
        aspect = 'aspect-wide' if fmt == 'landscape' else 'aspect-square'
        f = f'+filterui:{aspect}+filterui:imagesize-large'
    html = fetch('https://www.bing.com/images/search?q=' + urllib.parse.quote(q) + '&form=HDRSC2&qft=' + f)
    return re.findall(r'murl&quot;:&quot;(.*?)&quot;', html.decode('utf-8', 'ignore'))[:45]


def engine_ddg(q, gif=False, fmt='square'):
    try:
        html = fetch('https://duckduckgo.com/html/?q=' + urllib.parse.quote(q + (' gif' if gif else ' movie scene still')))
        return [urllib.parse.unquote(u) for u in re.findall(r'imgurl=([^&"]+)', html.decode('utf-8', 'ignore'))][:30]
    except Exception:
        return []


def valid_gif(data):
    """Scraped JPEGs are re-encoded by PIL (sanitized); GIFs are written verbatim,
    so verify they really are GIFs (header + PIL parse) before keeping them."""
    if data[:6] not in (b'GIF87a', b'GIF89a'):
        return False
    try:
        im = Image.open(io.BytesIO(data))
        return im.format == 'GIF'
    except Exception:
        return False


def letterbox(im):
    """True if the image has black bars top and bottom (cropped cinemascope screenshot)."""
    g = im.convert('L')
    h = g.height
    b = max(3, int(h * 0.06))
    bm = lambda y0, y1: g.crop((0, y0, g.width, y1)).resize((1, 1)).getpixel((0, 0))
    return bm(0, b) < 20 and bm(h - b, h) < 20 and bm(int(h * 0.42), int(h * 0.58)) > bm(0, b) + 28


def collect(d, concept, tier):
    """List matching candidates in one bank tier as (src, hash, tier). No copying."""
    out = []
    man = os.path.join(d, 'manifest.json')
    if os.path.exists(man):
        for e in json.load(open(man)):
            if concept.lower() in [c.lower() for c in e.get('concepts', [])]:
                src = os.path.join(d, e['file'])
                if os.path.exists(src):
                    out.append((src, e.get('hash') or sha(src), tier))
    elif os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if concept.lower() in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                src = os.path.join(d, f)
                out.append((src, sha(src), tier))
    return out


TIER_RANK = {'mybank': 0, 'core': 1, 'community': 2}


def from_bank(concept, out, n, used):
    """Pick from ALL bank tiers at once, freshest first.

    Ordering is global on purpose: an unused community still beats a core still that
    was already used in a previous reel. Variety across reels is the goal; tier only
    breaks ties.
    """
    cands = collect(os.path.join(HOME, 'mybank'), concept, 'mybank')
    for tier in ('core', 'community'):
        cands += collect(os.path.join(PLUGIN_ROOT, 'bank', tier), concept, tier)

    cands.sort(key=lambda c: (
        used.get(c[1], {}).get('count', 0),
        TIER_RANK.get(c[2], 9),
        used.get(c[1], {}).get('last', ''),
    ))

    got = []
    for src, h, tier in cands[:n]:
        dst = os.path.join(out, f'{tier}-{len(got)+1}{os.path.splitext(src)[1]}')
        shutil.copy(src, dst)
        got.append({
            'path': dst, 'source': f'{tier}:{os.path.basename(src)}',
            'hash': h, 'used_before': used.get(h, {}).get('count', 0),
        })
    return got


def fits(im, fmt):
    """Aspect gate driven by how the image will be DISPLAYED.
    square  : 0.8-2.0 — a square or mildly wide shot crops cleanly to 1:1. Mood and
              artistic images are often square/portrait and must not be rejected.
    landscape: >=1.2 — wide compositions only."""
    r = im.width / im.height
    return r >= 1.2 if fmt == 'landscape' else 0.8 <= r <= 2.0


def scrape(q, out, n, gif, fmt='square'):
    block = blocklist()
    got = []
    cache = os.path.join(HOME, 'cache', hashlib.sha1((q + str(gif) + fmt).encode()).hexdigest()[:12])
    if os.path.isdir(cache) and os.listdir(cache):
        for i, f in enumerate(sorted(os.listdir(cache))[:n]):
            dst = os.path.join(out, f'web-{i+1}{os.path.splitext(f)[1]}')
            shutil.copy(os.path.join(cache, f), dst)
            got.append({'path': dst, 'source': 'cache'})
        return got
    os.makedirs(cache, exist_ok=True)
    for eng in (engine_bing, engine_ddg):
        if len(got) >= n:
            break
        try:
            urls = eng(q, gif, fmt)
        except Exception:
            continue
        for u in urls:
            if len(got) >= n:
                break
            if any(b in u.lower() for b in block):
                continue
            try:
                data = fetch(u, 15)
                if gif and u.lower().endswith('.gif'):
                    if len(data) < 30000 or not valid_gif(data):
                        continue
                    ext = '.gif'
                else:
                    im = Image.open(io.BytesIO(data)).convert('RGB')
                    if im.width < 720 or not fits(im, fmt) or letterbox(im):
                        continue
                    buf = io.BytesIO()
                    im.save(buf, 'JPEG', quality=90)
                    data = buf.getvalue()
                    ext = '.jpg'
                name = f'web-{len(got)+1}{ext}'
                open(os.path.join(out, name), 'wb').write(data)
                open(os.path.join(cache, name), 'wb').write(data)
                got.append({'path': os.path.join(out, name), 'source': u})
            except Exception:
                continue
    return got


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--query', required=True)
    ap.add_argument('--concept', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--candidates', type=int, default=3)
    ap.add_argument('--bank-max', type=int, default=1,
                    help='max candidates taken from the banks (default 1). The rest come '
                         'from the web, so every board offers fresh options. Use '
                         '--bank-max 3 to work offline from the bank only.')
    ap.add_argument('--format', dest='fmt', choices=['square', 'landscape'], default='square',
                    help='intended display format — drives the aspect filter (default square)')
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--reject', help='learn a bad domain (adds it to the local blocklist)')
    a = ap.parse_args()

    if a.reject:
        learn(a.reject)
        print('learned:', a.reject)
        sys.exit(0)

    os.makedirs(a.out, exist_ok=True)
    used = used_hashes()
    bank_budget = min(a.bank_max, a.candidates)

    res = from_bank(a.concept, a.out, bank_budget, used)
    if len(res) < a.candidates:
        res += scrape(a.query, a.out, a.candidates - len(res), a.gif, a.fmt)
    # Last resort: web gave nothing (offline, blocked) — fill up from the bank.
    if len(res) < a.candidates:
        have = {r.get('hash') for r in res}
        for extra in from_bank(a.concept, a.out, a.candidates, used):
            if len(res) >= a.candidates:
                break
            if extra.get('hash') not in have:
                res.append(extra)
    print(json.dumps(res, indent=1))
