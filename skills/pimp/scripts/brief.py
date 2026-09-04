#!/usr/bin/env python3
"""usage: brief.py init|check|source|mapping <project_dir>

The brief is the contract between each sentence and its image, and it is MANDATORY:
export.sh refuses a project whose picks were not validated against one.

Why it exists — every bad image this pipeline ever shipped came from the same move:
a concept WORD typed into a search engine, which returns a picture OF THAT WORD. A
thermometer for "degree". A pink gradient for "spiritual". A cardboard box for
"putting yourself in a box". Two squares for "black or white". The brief forces the
two steps a good editor does in their head before touching a search box:

  idea   -> what the sentence MEANS, not the words it uses
  scene  -> ONE concrete picture a viewer recognises as that idea WITHOUT the words.
            A human moment, a cultural reference (film, series, meme, artwork), or a
            graphic object with an obvious reading (a battery at 1%, a red pill and a
            blue pill). NEVER abstract: no gradients, textures, patterns, shapes,
            silhouettes, portraits of strangers, generic objects.
  refs   -> the cultural references CONSIDERED for this beat, even when a photo wins.
            An editor with no references in mind ships stock.

Commands
  init     writes brief.json from segments.json: one beat per sentence, fields empty
  check    refuses an incomplete or lazy brief (exit 1) and checks the register mix
  source   downloads 3 candidates per beat into candidates/<NN-slug>/ (idempotent)
  mapping  writes mapping.json segments from the brief's chosen images (+ collage)

Registers: film | meme | gif | icon | photo | graphic.  Culture (film+meme+gif+icon)
must be 50-90% of the beats. The author asked for MORE film scenes after a 59% reel:
recognisable cinema is what gives a reel its "esprit de reference", and modern
illustration photography is the breathing space between the punches — not the base
material. Below 50% it reads as stock; above 90% it is meme spam. The ceiling moved from
85 to 90 rather than force a weak stock photo in just to satisfy a ratio: a filler
photo is worse for the reel than one more good film scene.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTERS = {'film', 'meme', 'gif', 'icon', 'photo', 'graphic'}
CULTURE = {'film', 'meme', 'gif', 'icon'}
# A scene built on these words is not a scene, it is a texture.
ABSTRACT = re.compile(r'\b(gradient|d[ée]grad[ée]|texture|pattern|motif|abstract|abstrait|'
                      r'bokeh|blur|flou|silhouette|shape|forme|colou?r field|square|carr[ée]|'
                      r'rectangle)\b', re.I)


def load(proj, name):
    p = os.path.join(proj, name)
    if not os.path.exists(p):
        sys.exit(f'ERROR: {p} not found')
    return json.load(open(p))


def save(proj, name, data):
    json.dump(data, open(os.path.join(proj, name), 'w'), indent=1, ensure_ascii=False)


def slug(s, n=3):
    words = re.findall(r'[a-zA-ZÀ-ſ]+', s.lower())
    return '-'.join(w for w in words if len(w) > 2)[:40].strip('-') or 'beat'


def cmd_init(proj):
    seg = load(proj, 'segments.json')
    beats = []
    for s in seg['transcription']:
        o = s['offsets']
        beats.append({
            'start': round(o['from'] / 1000, 2), 'end': round(o['to'] / 1000, 2),
            'sentence': s['text'].strip(),
            'idea': '', 'scene': '', 'register': '', 'refs': [],
            'query': '', 'engine': 'auto', 'format': 'square',
            'image': '', 'shows': '', 'skip': False,
        })
    out = os.path.join(proj, 'brief.json')
    if os.path.exists(out):
        sys.exit(f'brief.json already exists — edit it, or delete it to start over.')
    save(proj, 'brief.json', {'collage': [], 'beats': beats})
    print(f'brief.json: {len(beats)} beats to brief. Fill idea / scene / register / refs / query.')
    print('Read references/idea-bank.md FIRST: it holds the references a culture-literate '
          'editor reaches for.')


def active(brief):
    return [b for b in brief['beats'] if not b.get('skip')]


def mix_report(beats):
    n = len(beats)
    cult = sum(1 for b in beats if b.get('register') in CULTURE)
    graph = sum(1 for b in beats if b.get('register') == 'graphic')
    return n, cult, graph


def cmd_check(proj):
    brief = load(proj, 'brief.json')
    beats = active(brief)
    errs = []
    for i, b in enumerate(beats):
        tag = f'beat {i} @{b["start"]:.2f}s "{b["sentence"][:40]}"'
        if not b.get('idea', '').strip():
            errs.append(f'{tag}: idea is empty — what does the sentence MEAN?')
        scene = b.get('scene', '').strip()
        if len(scene.split()) < 3:
            errs.append(f'{tag}: scene "{scene}" is a keyword, not a scene (>= 3 words: '
                        f'who/what is in frame, doing what)')
        if ABSTRACT.search(scene):
            errs.append(f'{tag}: scene "{scene}" is abstract — a texture is not a picture '
                        f'of anything. Find the human moment or the cultural reference.')
        if b.get('register') not in REGISTERS:
            errs.append(f'{tag}: register must be one of {sorted(REGISTERS)}')
        if not b.get('refs'):
            errs.append(f'{tag}: refs is empty — name at least one film/series/meme/artwork '
                        f'you CONSIDERED, even if a photo wins')
        q = b.get('query', '').strip()
        reg = b.get('register')
        if not q:
            errs.append(f'{tag}: query is empty')
        elif q.lower() == scene.lower():
            errs.append(f'{tag}: query is a copy of scene — the query is what the ENGINE '
                        f'needs (film title + actor + moment; or subject + action + framing)')
        elif reg not in CULTURE and len(q.split()) < 6:
            # MEASURED, and it is the single biggest quality lever found so far.
            # "simulation" returns a Penrose triangle and two VR headsets. "face with
            # glowing code projected onto skin, dark blue light, extreme close up"
            # returns the image the author actually wanted — same engine, same second.
            # "overthinking" returns a graphic reading DON'T OVERTHINK; "man sitting on
            # floor in dark room, single lamp, head in hands, cinematic" returns the
            # picture. A stock engine matches WORDS IN CAPTIONS, so a concept noun finds
            # pictures captioned with that noun — literal, generic, lifeless. Describe
            # the PHOTOGRAPH: subject + action + light + framing, six words minimum.
            errs.append(f'{tag}: query "{q}" is a concept, not a photograph. Stock engines '
                        f'match caption words, so a bare concept returns literal stock. '
                        f'Describe the picture: subject + action + light + framing '
                        f'(>= 6 words). See references/query-guide.md.')
    n, cult, graph = mix_report(beats)
    if n:
        share = cult / n
        if share < 0.50:
            errs.append(f'mix: {cult}/{n} culture beats ({share:.0%}) — below 50%. No '
                        f'"esprit de référence": the author asked for MORE film scenes. '
                        f'Replace photo beats with recognisable cinema — read idea-bank.md.')
        if share > 0.90:
            errs.append(f'mix: {cult}/{n} culture beats ({share:.0%}) — above 90%: meme spam. '
                        f'Keep a few modern illustration photos as breathing space.')
        if graph / n > 0.20:
            errs.append(f'mix: {graph}/{n} graphic beats — above 20%.')
    # Density: a hole longer than 5 s reads as "the editor gave up".
    prev = None
    for b in beats:
        if prev is not None and b['start'] - prev > 5.5:
            print(f'  warning: {b["start"] - prev:.1f}s without a new image before '
                  f'{b["start"]:.2f}s — split the beat or accept the hole deliberately.')
        prev = b['start']
    if errs:
        print('BRIEF REFUSED:')
        for e in errs:
            print('  -', e)
        sys.exit(1)
    print(f'brief OK: {n} beats, {cult} culture ({cult / n:.0%}), {graph} graphic.')


def cmd_source(proj):
    brief = load(proj, 'brief.json')
    beats = active(brief)
    root = os.path.join(proj, 'candidates')
    os.makedirs(root, exist_ok=True)
    for i, b in enumerate(beats):
        out = os.path.join(root, f'{i:02d}-{slug(b["scene"])}')
        if os.path.isdir(out) and os.listdir(out):
            print(f'{os.path.basename(out)}: cached ({len(os.listdir(out))})')
            continue
        cmd = [sys.executable, os.path.join(HERE, 'source_images.py'),
               '--query', b['query'], '--concept', b.get('idea') or b['scene'],
               '--out', out + '/', '--candidates', '3', '--bank-max', '0',
               '--format', b.get('format', 'square'), '--engine', b.get('engine', 'auto')]
        if b.get('register') == 'gif':
            cmd.append('--gif')
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        got = len(os.listdir(out)) if os.path.isdir(out) else 0
        print(f'{os.path.basename(out)}: {got}  [{b.get("engine", "auto")}] {b["query"][:50]}')


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower().replace("'", ""))


def word_stream(proj):
    """Word-level timings from words.json: [(start_seconds, normalised_token), ...]."""
    p = os.path.join(proj, 'words.json')
    if not os.path.exists(p):
        return []
    out = []
    for x in json.load(open(p)).get('transcription', []):
        n = norm(x.get('text', ''))
        if n:
            out.append((x['offsets']['from'] / 1000.0, n))
    return out


def snap(words, sentence, declared):
    """Where does this beat's sentence actually START being spoken?

    Beat times written by hand drift by a few tenths — enough for the author to see
    every image land before the words it illustrates. The sentence text is matched
    against the word stream (whisper splits into sub-word tokens, so the comparison is
    on a concatenation, not token-by-token) and the match nearest the declared time
    wins. Falls back to the declared time when nothing matches.
    """
    key = norm(sentence)[:24]
    if not words or len(key) < 6:
        return declared
    best, bestd = None, 1e9
    for i in range(len(words)):
        acc = ''
        for j in range(i, min(i + 14, len(words))):
            acc += words[j][1]
            if len(acc) >= len(key):
                break
        if acc.startswith(key):
            d = abs(words[i][0] - declared)
            if d < bestd:
                best, bestd = words[i][0], d
    # A match more than 2.5s from the declared time is a coincidence, not this beat.
    return best if best is not None and bestd <= 2.5 else declared


def cmd_mapping(proj):
    brief = load(proj, 'brief.json')
    m = load(proj, 'mapping.json')
    fps = m['fps']
    words = word_stream(proj)
    # +2 frames, not -3. The old 3-frame LEAD was meant to make the image land on the
    # word; combined with hand-written beat times it made every cutaway arrive before
    # the words it illustrates — reported on a delivered reel. A cut that lands a hair
    # late reads as intentional; one that lands early reads as broken.
    F = lambda s: max(0, round(s * fps) + 2)
    segs = []
    if brief.get('collage'):
        segs.append({'start': 0, 'type': 'collage', 'images': brief['collage']})
    for b in active(brief):
        if not b.get('image'):
            continue
        at = snap(words, b.get('sentence', ''), b['start'])
        if abs(at - b['start']) > 0.05:
            print(f'  snap @{b["start"]:.2f} -> {at:.2f}  "{b.get("sentence","")[:34]}"')
        seg = {'start': F(at), 'image': b['image']}
        if b.get('images'):
            seg['images'] = b['images']
        if b.get('speaker'):
            seg['speaker'] = b['speaker']
        if b.get('format') == 'landscape':
            seg['format'] = 'landscape'
        segs.append(seg)
    m['segments'] = segs
    save(proj, 'mapping.json', m)
    print(f'mapping.json: {len(segs)} segments written from the brief.')


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('init', 'check', 'source', 'mapping'):
        sys.exit(__doc__)
    globals()['cmd_' + sys.argv[1]](os.path.abspath(sys.argv[2]))
