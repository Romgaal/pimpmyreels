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


def fetch(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def engine_bing(q, gif=False):
    f = '+filterui:photo-animatedgif' if gif else '+filterui:aspect-wide+filterui:imagesize-large'
    html = fetch('https://www.bing.com/images/search?q=' + urllib.parse.quote(q) + '&form=HDRSC2&qft=' + f)
    return re.findall(r'murl&quot;:&quot;(.*?)&quot;', html.decode('utf-8', 'ignore'))[:45]


def engine_ddg(q, gif=False):
    try:
        html = fetch('https://duckduckgo.com/html/?q=' + urllib.parse.quote(q + (' gif' if gif else ' movie scene still')))
        return [urllib.parse.unquote(u) for u in re.findall(r'imgurl=([^&"]+)', html.decode('utf-8', 'ignore'))][:30]
    except Exception:
        return []


def letterbox(im):
    """True if the image has black bars top and bottom (cropped cinemascope screenshot)."""
    g = im.convert('L')
    h = g.height
    b = max(3, int(h * 0.06))
    bm = lambda y0, y1: g.crop((0, y0, g.width, y1)).resize((1, 1)).getpixel((0, 0))
    return bm(0, b) < 20 and bm(h - b, h) < 20 and bm(int(h * 0.42), int(h * 0.58)) > bm(0, b) + 28


def from_dir(d, concept, out, n, tier):
    """Pull from a bank tier. Uses manifest.json concepts, or filename match for the user bank."""
    got = []
    man = os.path.join(d, 'manifest.json')
    if os.path.exists(man):
        for e in json.load(open(man)):
            if len(got) >= n:
                break
            if concept.lower() in [c.lower() for c in e.get('concepts', [])]:
                src = os.path.join(d, e['file'])
                if os.path.exists(src):
                    dst = os.path.join(out, f'{tier}-{len(got)+1}{os.path.splitext(src)[1]}')
                    shutil.copy(src, dst)
                    got.append({'path': dst, 'source': f'{tier}:{e["file"]}'})
    elif os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if len(got) >= n:
                break
            if concept.lower() in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                dst = os.path.join(out, f'{tier}-{len(got)+1}{os.path.splitext(f)[1]}')
                shutil.copy(os.path.join(d, f), dst)
                got.append({'path': dst, 'source': f'{tier}:{f}'})
    return got


def scrape(q, out, n, gif):
    block = blocklist()
    got = []
    cache = os.path.join(HOME, 'cache', hashlib.sha1((q + str(gif)).encode()).hexdigest()[:12])
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
            urls = eng(q, gif)
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
                    if len(data) < 30000:
                        continue
                    ext = '.gif'
                else:
                    im = Image.open(io.BytesIO(data)).convert('RGB')
                    if im.width < 720 or im.width < im.height * 1.2 or letterbox(im):
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
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--reject', help='learn a bad domain (adds it to the local blocklist)')
    a = ap.parse_args()

    if a.reject:
        learn(a.reject)
        print('learned:', a.reject)
        sys.exit(0)

    os.makedirs(a.out, exist_ok=True)
    res = from_dir(os.path.join(HOME, 'mybank'), a.concept, a.out, a.candidates, 'mybank')
    for tier in ('core', 'community'):
        if len(res) < a.candidates:
            res += from_dir(os.path.join(PLUGIN_ROOT, 'bank', tier), a.concept, a.out,
                            a.candidates - len(res), tier)
    if len(res) < a.candidates:
        res += scrape(a.query, a.out, a.candidates - len(res), a.gif)
    print(json.dumps(res, indent=1))
