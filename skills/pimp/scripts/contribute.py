#!/usr/bin/env python3
"""Silently contribute newly validated images back to the shared bank.

usage: contribute.py <project_dir>

Runs in a SEPARATE clone (~/.pimpmyreels/contrib) so it can never conflict with
`/plugin update` on the installed plugin. Images that survived the full pipeline
(filters -> agent QA -> human board -> final render) are, by revealed preference,
worth sharing: no question is asked. Known images get a use_count bump instead,
which is what drives curation (community -> core).

Disable with: {"contribution": "off"} in ~/.pimpmyreels/config.json
"""
import datetime, hashlib, json, os, shutil, subprocess, sys

HOME = os.path.expanduser('~/.pimpmyreels')
CLONE = os.path.join(HOME, 'contrib')
REPO = 'https://github.com/Romgaal/pimpmyreels.git'

try:
    cfg = json.load(open(os.path.join(HOME, 'config.json')))
except Exception:
    cfg = {}
if cfg.get('contribution', 'auto') != 'auto':
    print('contribution off')
    sys.exit(0)
if subprocess.run(['gh', 'auth', 'status'], capture_output=True).returncode != 0:
    print('contribution skipped (gh not authenticated)')
    sys.exit(0)


def run(*cmd, cwd=CLONE, ok=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode and ok:
        raise RuntimeError(' '.join(cmd) + ' -> ' + r.stderr[:300])
    return r


if not os.path.isdir(os.path.join(CLONE, '.git')):
    os.makedirs(os.path.dirname(CLONE), exist_ok=True)
    subprocess.run(['git', 'clone', '--depth', '20', REPO, CLONE], capture_output=True)
    if not os.path.isdir(os.path.join(CLONE, '.git')):
        print('contribution skipped (could not clone repo)')
        sys.exit(0)
run('git', 'checkout', 'main', ok=False)
run('git', 'pull', '--ff-only', ok=False)

proj = sys.argv[1]
mapping = json.load(open(os.path.join(proj, 'mapping.json')))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

known = {}
for tier in ('core', 'community'):
    mp = os.path.join(CLONE, 'bank', tier, 'manifest.json')
    if os.path.exists(mp):
        for e in json.load(open(mp)):
            known[e['hash']] = (tier, e)

comm_dir = os.path.join(CLONE, 'bank', 'community')
os.makedirs(comm_dir, exist_ok=True)
comm_mp = os.path.join(comm_dir, 'manifest.json')
comm = json.load(open(comm_mp)) if os.path.exists(comm_mp) else []

new, bumped = [], 0
for seg in mapping['segments']:
    for img in ([seg['image']] if seg.get('image') else seg.get('images', [])):
        p = os.path.join(proj, img.replace('project/', ''))
        if not os.path.exists(p) or p.lower().endswith('.gif'):
            continue
        h = sha(p)
        if h in known:
            known[h][1]['use_count'] = known[h][1].get('use_count', 0) + 1
            bumped += 1
        else:
            fn = f'{h}.jpg'
            shutil.copy(p, os.path.join(comm_dir, fn))
            e = {
                'file': fn, 'hash': h,
                'concepts': [os.path.basename(os.path.dirname(img)) or 'misc'],
                'film': 'unknown', 'universal': False, 'use_count': 1,
                'added': datetime.date.today().isoformat(),
            }
            comm.append(e)
            known[h] = ('community', e)
            new.append(fn)

json.dump(comm, open(comm_mp, 'w'), indent=1, ensure_ascii=False)
core_mp = os.path.join(CLONE, 'bank', 'core', 'manifest.json')
if os.path.exists(core_mp):
    json.dump([e for t, e in known.values() if t == 'core'], open(core_mp, 'w'), indent=1, ensure_ascii=False)

if not new and not bumped:
    print('nothing to contribute')
    sys.exit(0)

br = f"contrib/{os.environ.get('USER', 'user')}-{datetime.date.today().isoformat()}-{os.getpid()}"
run('git', 'checkout', '-B', br)
run('git', 'add', 'bank')
run('git', 'commit', '-m', f'bank: +{len(new)} images, {bumped} use_count bumps')
if run('git', 'push', '-u', 'origin', br, ok=False).returncode:
    run('gh', 'repo', 'fork', '--remote', '--remote-name', 'fork', ok=False)
    run('git', 'push', '-u', 'fork', br, ok=False)
# --head is required: gh does not reliably detect the freshly pushed branch.
pr = run('gh', 'pr', 'create', '--fill', '--head', br, '--base', 'main', ok=False)
run('git', 'checkout', 'main', ok=False)
opened = 'PR opened' if pr.returncode == 0 else 'branch pushed (open the PR manually)'
print(f'contributed: {len(new)} new image(s), {bumped} bump(s) — {opened}')
