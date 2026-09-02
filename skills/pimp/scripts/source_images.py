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


def unsplash_key():
    k = os.environ.get('UNSPLASH_ACCESS_KEY', '')
    if not k:
        cfg = os.path.expanduser('~/.config/pimpmyreels/env')
        if os.path.exists(cfg):
            for line in open(cfg):
                if 'UNSPLASH_ACCESS_KEY=' in line:
                    k = line.split('=', 1)[1].strip()
    return k


def engine_unsplash(q, gif=False, fmt='square'):
    """Unsplash search API. The right source for AMBIANCE and metaphor images:
    original photography, design-grade, and no watermarks by construction — the
    Bing/DDG scrape returns AI slop and stamped stock for exactly those queries.
    Useless for film stills (Unsplash has none), so it is opt-in via --engine."""
    key = unsplash_key()
    if not key or gif:
        return []
    orient = {'portrait': 'portrait', 'landscape': 'landscape'}.get(fmt, 'squarish')
    url = ('https://api.unsplash.com/search/photos?query=' + urllib.parse.quote(q)
           + f'&per_page=12&orientation={orient}&client_id=' + key)
    js = json.loads(fetch(url, 20))
    return [r['urls']['full'] + '&w=1600' for r in js.get('results', [])]


def engine_bing(q, gif=False, fmt='square'):
    if gif:
        f = '+filterui:photo-animatedgif'
    else:
        aspect = 'aspect-wide' if fmt == 'landscape' else 'aspect-square'
        f = f'+filterui:{aspect}+filterui:imagesize-large'
    html = fetch('https://www.bing.com/images/search?q=' + urllib.parse.quote(q) + '&form=HDRSC2&qft=' + f)
    return re.findall(r'murl&quot;:&quot;(.*?)&quot;', html.decode('utf-8', 'ignore'))[:45]


def engine_ddg(q, gif=False, fmt='square'):
    """DuckDuckGo IMAGE search — two steps, because one does not work.

    The previous implementation scraped the /html/ WEB results page for `imgurl=`,
    which that page has not contained for a long time: it returned zero results on
    every query, silently, so the pipeline had been running on Bing alone without
    anyone noticing. The real flow asks the search page for a `vqd` token, then calls
    the JSON endpoint with it. Verified: 47 results where the old code returned 0 —
    and DDG indexes Tenor and GifDB, which makes it the best of the engines for gifs.
    """
    try:
        page = fetch('https://duckduckgo.com/?q=' + urllib.parse.quote(q) + '&iax=images&ia=images', 20)
        m = re.search(r'vqd=["\']?([\d-]+)["\']?', page.decode('utf-8', 'ignore'))
        if not m:
            return []
        js = json.loads(fetch('https://duckduckgo.com/i.js?l=us-en&o=json&q='
                              + urllib.parse.quote(q) + '&vqd=' + m.group(1) + '&f=,,,&p=1', 20))
        urls = [r['image'] for r in js.get('results', []) if r.get('image')]
        if gif:
            urls = [u for u in urls if u.lower().split('?')[0].endswith('.gif')] or urls
        return urls[:40]
    except Exception:
        return []


def engine_openverse(q, gif=False, fmt='square'):
    """Openverse — the Creative Commons aggregator (Flickr, Wikimedia, museums...).
    No key, generous quota, and a register the stock engines do not cover:
    documentary photography, archives, museum pieces."""
    try:
        orient = {'portrait': 'tall', 'landscape': 'wide'}.get(fmt, 'square')
        js = json.loads(fetch('https://api.openverse.org/v1/images/?q=' + urllib.parse.quote(q)
                              + f'&page_size=20&aspect_ratio={orient}&license_type=all', 25))
        return [r['url'] for r in js.get('results', []) if r.get('url')]
    except Exception:
        return []


def engine_wikimedia(q, gif=False, fmt='square'):
    """Wikimedia Commons — free, no key. The right source for anything historical,
    scientific or notable: archive photographs, diagrams, public figures."""
    try:
        api = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
               '&gsrnamespace=6&gsrsearch=' + urllib.parse.quote(q) +
               '&gsrlimit=20&prop=imageinfo&iiprop=url&iiurlwidth=1600&format=json')
        js = json.loads(fetch(api, 25))
        pages = (js.get('query') or {}).get('pages', {})
        out = []
        for pg in pages.values():
            for ii in pg.get('imageinfo', []):
                u = ii.get('thumburl') or ii.get('url')
                if u and u.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png')):
                    out.append(u)
        return out
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
    landscape: >=1.2 — wide compositions only.
    portrait: <=1.1 — mode-2 backgrounds fill 9:16 cells; a wide still cover-cropped
              to portrait loses most of itself, so only tall/square sources qualify."""
    r = im.width / im.height
    if fmt == 'landscape':
        return r >= 1.2
    if fmt == 'portrait':
        return r <= 1.1
    return 0.8 <= r <= 2.0


def scrape(q, out, n, gif, fmt='square', engine='auto'):
    block = blocklist()
    got = []
    cache = os.path.join(HOME, 'cache', hashlib.sha1((q + str(gif) + fmt + engine).encode()).hexdigest()[:12])
    if os.path.isdir(cache) and os.listdir(cache):
        for i, f in enumerate(sorted(os.listdir(cache))[:n]):
            dst = os.path.join(out, f'web-{i+1}{os.path.splitext(f)[1]}')
            shutil.copy(os.path.join(cache, f), dst)
            got.append({'path': dst, 'source': 'cache'})
        return got
    os.makedirs(cache, exist_ok=True)
    # 'unsplash' means ONLY unsplash. Falling back to the scrape is how 16 of 26
    # backgrounds on a real reel came from the open web — watermarked AI stock the
    # user rejected on sight. A clean source silently topped up from a dirty one is
    # a dirty source. Empty result > slop.
    engines = {
        'unsplash': (engine_unsplash,),
        'ddg': (engine_ddg,),
        'openverse': (engine_openverse,),
        'wikimedia': (engine_wikimedia,),
    }.get(engine, (engine_bing, engine_ddg, engine_openverse))
    for eng in engines:
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
    ap.add_argument('--format', dest='fmt', choices=['square', 'landscape', 'portrait'], default='square',
                    help='intended display format: square, landscape or portrait '
                         '(mode-2 backgrounds) — drives the aspect filter (default square)')
    ap.add_argument('--engine',
                    choices=['auto', 'unsplash', 'ddg', 'openverse', 'wikimedia'], default='auto',
                    help='auto: bing + duckduckgo + openverse (film stills, memes, documentary); '
                         'unsplash: design photography (needs UNSPLASH_ACCESS_KEY); '
                         'ddg: best for gifs (indexes Tenor/GifDB); '
                         'openverse: Creative Commons archives; wikimedia: historical/notable')
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
        res += scrape(a.query, a.out, a.candidates - len(res), a.gif, a.fmt, a.engine)
    # Last resort: web gave nothing (offline, blocked) — fill up from the bank.
    if len(res) < a.candidates:
        have = {r.get('hash') for r in res}
        for extra in from_bank(a.concept, a.out, a.candidates, used):
            if len(res) >= a.candidates:
                break
            if extra.get('hash') not in have:
                res.append(extra)
    print(json.dumps(res, indent=1))
