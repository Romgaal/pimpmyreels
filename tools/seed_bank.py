#!/usr/bin/env python3
"""One-shot seeding of the shared bank from the stills validated in real reels.

Run once by the maintainer. Kept in the repo for transparency about what is in
bank/core and why. CORE = images that shipped in a validated reel. COMMUNITY =
usable alternates. Rejected images are listed in EXCLUDE with the reason.
"""
import hashlib, json, os, shutil, sys, datetime
from PIL import Image

SRC = "/Users/romgal/CLAUDE/Remotion - Montage & AE/remotion/public"
DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bank')
TODAY = datetime.date.today().isoformat()

# Rejected — never ship these (reason kept for the record)
EXCLUDE = {
    'films/alt/roilion-1': 'watermark', 'films/alt/roilion-2': 'watermark',
    'films/alt/roilionclean-1': 'too dark', 'films/alt/roilionclean-2': 'too dark',
    'films/alt/roilionclean-3': 'off message', 'films/alt/simba-1': 'off message',
    'films/alt/simba-2': 'off message',
    'films/nonnon-1': 'burned-in text', 'films/nonnon-2': 'burned-in text',
    'radar/iceberg-1': 'watermark', 'radar/iceberg-2': 'watermark',
    'radar/radar-1': 'white bars', 'radar/radar-2': 'white bars',
    'films/jamaispret-2': 'burned-in text',
    'films/confiance-1': 'empty room, unreadable',
    'valeur/loner-1': 'rejected reference', 'valeur/loner-2': 'rejected reference',
    'films/courage-inter-1': 'weak (empty cockpit)', 'films/courage-inter-2': 'weak + logo',
    'valeur/timide-1': 'wrong register', 'valeur/timide-2': 'wrong register',
    'valeur/timide-3': 'wrong register',
    'films/oser-1': 'too weak, not instantly readable', 'films/oser-2': 'too weak',
    'radar/rencontre-1': 'Titanic + Alamy watermark — rejected in favour of Walter Mitty',
    'radar/rencontre-2': 'Titanic + watermark',
}

# CORE: file -> (film, [concepts], universal)
CORE = {
    'films/savoir-2': ('Good Will Hunting', ['knowledge', 'learning'], True),
    'films/potes-2': ('Friends', ['friends', 'funny'], True),
    'films/valeur-1': ('Rocky', ['value', 'victory'], True),
    'films/rencontre-1': ('Forrest Gump', ['meeting', 'strangers'], True),
    'films/bonmoment-1': ('The Great Gatsby', ['good-time', 'cheers'], True),
    'films/bienveillant-1': ('Intouchables', ['kindness', 'benevolence'], True),
    'films/peur-1': ('Home Alone', ['fear', 'panic'], True),
    'films/faux-2': ('The Matrix', ['false', 'choice'], True),
    'films/jamaispret-1': ('waiting skeleton meme', ['never-ready', 'waiting'], True),
    'films/faisle-1': ('Shia LaBeouf meme', ['just-do-it', 'action'], True),
    'films/nonnon-crop': ('The Office', ['rejection', 'panic'], True),
    'films/courage-vikings-1': ('Vikings', ['courage', 'warrior'], True),
    'films/alt/limitless-1': ('Limitless', ['potential', 'knowledge'], True),
    'films/alt/gladiator-1': ('Gladiator', ['warrior', 'arena'], True),
    'radar/perdu-1': ('Cast Away', ['lost', 'burnout'], True),
    'radar/sousmarin-1': ('submarine control room', ['control-room', 'unknown'], False),
    'radar/radar-clean': ('radar screen', ['radar', 'unknown'], False),
    'radar/mitty-jump-1': ('The Secret Life of Walter Mitty', ['leap', 'unexpected'], True),
    'radar/mitty-longboard-1': ('The Secret Life of Walter Mitty', ['adventure', 'freedom'], True),
    'radar/iceberg-clean': ('iceberg', ['hidden', 'potential'], True),
    'radar/espoir-1': ('The Shawshank Redemption', ['hope', 'freedom'], True),
    'valeur/hero-1': ('Iron Man', ['hero', 'extraordinary'], True),
    'valeur/capacites-2': ('Sherlock Holmes', ['capacities', 'smart'], True),
    'valeur/cool-2': ('James Bond', ['cool', 'class'], True),
    'valeur/charisme-1': ('Peaky Blinders', ['charisma', 'authentic'], True),
    'valeur/magnetique-1': ('The Wolf of Wall Street', ['magnetic', 'speech'], True),
    'valeur/potes-2': ('The Hangover', ['friends', 'fun'], True),
    'valeur/timide-h-1': ('Fight Club', ['shy', 'disconnected'], True),
}

# COMMUNITY: usable alternates -> (film, [concepts])
COMMUNITY = {
    'films/savoir-1': ('Good Will Hunting', ['knowledge']),
    'films/potes-1': ('Friends', ['friends']),
    'films/valeur-2': ('Rocky', ['value']),
    'films/rencontre-2': ('Forrest Gump', ['meeting']),
    'films/bonmoment-2': ('The Great Gatsby', ['good-time']),
    'films/bienveillant-2': ('Intouchables', ['kindness']),
    'films/peur-2': ('Home Alone', ['fear']),
    'films/faux-1': ('The Matrix', ['false', 'choice']),
    'films/faisle-2': ('Shia LaBeouf meme', ['just-do-it']),
    'films/courage-1': ('Braveheart', ['courage']),
    'films/courage-2': ('Braveheart', ['courage']),
    'films/courage-vikings-2': ('Vikings', ['courage']),
    'films/confiance-2': ('American Psycho', ['confidence', 'class']),
    'films/alt/limitless-2': ('Limitless', ['potential']),
    'films/alt/gladiator-2': ('Gladiator', ['warrior']),
    'films/alt/einstein-1': ('Albert Einstein', ['knowledge', 'genius']),
    'films/alt/einstein-2': ('Albert Einstein', ['knowledge', 'genius']),
    'radar/perdu-2': ('Cast Away', ['lost']),
    'radar/sousmarin-2': ('submarine control room', ['control-room']),
    'radar/mitty-jump-2': ('The Secret Life of Walter Mitty', ['leap']),
    'radar/mitty-longboard-2': ('The Secret Life of Walter Mitty', ['adventure']),
    'radar/mitty-adventure-1': ('The Secret Life of Walter Mitty', ['adventure']),
    'radar/mitty-adventure-2': ('The Secret Life of Walter Mitty', ['adventure']),
    'radar/espoir-2': ('The Shawshank Redemption', ['hope']),
    'valeur/hero-2': ('Iron Man', ['hero']),
    'valeur/capacites-1': ('Sherlock Holmes', ['capacities']),
    'valeur/cool-1': ('James Bond', ['cool']),
    'valeur/charisme-2': ('Peaky Blinders', ['charisma']),
    'valeur/magnetique-2': ('The Wolf of Wall Street', ['magnetic']),
    'valeur/gladiator-1': ('Gladiator', ['warrior']),
    'valeur/gladiator-2': ('Gladiator', ['warrior']),
    'valeur/potes-1': ('The Hangover', ['friends']),
    'valeur/timide-h-2': ('Fight Club', ['shy']),
}


def seed(spec, tier, universal_default=False):
    out = os.path.join(DST, tier)
    os.makedirs(out, exist_ok=True)
    manifest, missing = [], []
    for rel, meta in spec.items():
        src = os.path.join(SRC, rel + '.jpg')
        if not os.path.exists(src):
            missing.append(rel)
            continue
        h = hashlib.sha256(open(src, 'rb').read()).hexdigest()[:16]
        fn = f'{h}.jpg'
        shutil.copy(src, os.path.join(out, fn))
        with Image.open(src) as im:
            aspect = 'square' if 0.85 < im.width / im.height < 1.18 else 'landscape'
        manifest.append({
            'file': fn, 'hash': h, 'film': meta[0], 'concepts': meta[1],
            'universal': meta[2] if len(meta) > 2 else universal_default,
            'aspect': aspect, 'use_count': 1 if tier == 'core' else 0, 'added': TODAY,
        })
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
    return len(manifest), missing


if __name__ == '__main__':
    if not os.path.isdir(SRC):
        print('source not found:', SRC)
        sys.exit(1)
    nc, mc = seed(CORE, 'core')
    nk, mk = seed(COMMUNITY, 'community')
    print(f'core: {nc} images / community: {nk} images')
    print(f'excluded on purpose: {len(EXCLUDE)}')
    if mc or mk:
        print('MISSING (not found in source):', mc + mk)
