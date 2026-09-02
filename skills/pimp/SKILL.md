---
name: pimp
description: Pimp a talking-head video into a reel with word-synced iconic cutaway images (movies, memes, web culture). Use when the user gives a video rush and wants illustration images added, or types /pimp <path>. Runs the full pipeline — transcribe, map, source, validate, render, export.
---

# pimp — word-synced cutaway images over a talking-head rush

You turn a raw facecam video into a reel where **iconic images land exactly on the
words that call for them**. The images are the product. Everything else is plumbing.

**Three rules decide whether this works or not:**

1. **Never guess timings.** Transcribe first, always. Guessed timings put Gatsby on
   "people are kind" — the single most common failure of this pipeline.
2. **The human validates the images before you edit.** You propose, they decide.
3. **Prove the result.** Show frames of the final file before claiming it's done.

Scripts live in `scripts/`, reference docs in `references/`. Paths below are relative
to this skill directory.

---

## 0. Environment

Run `bash scripts/doctor.sh`. If anything fails, run `bash scripts/setup.sh` once
(it is idempotent and downloads the Whisper model on first use), then re-check.

If the user typed `/pimp` with no argument and has no rush ready, offer the demo:
`bash scripts/make_demo.sh` creates a 15s synthetic-voice rush at `demo/rush.mp4`;
continue the pipeline with it so they see a finished reel within minutes.

## 1. Project folder

Create `~/pimpmyreels/<name>/` and copy the rush in as `rush.mp4`. Everything for
this reel lives there: `words.json`, `candidates/`, `board.png`, `mapping.json`,
`img/`, `out/`. That way any reel can be reopened and re-exported later without
redoing the expensive steps.

**Order matters: pimp the RAW rush, add captions afterwards.** Captions apps place
their text wherever they like — often high, exactly where the cutaways go. Adding
images last means fighting for the same 400px. If the user still hands you a rush with
captions already burned in, measure the band before you place anything:

```bash
python3 scripts/detect_captions.py ~/pimpmyreels/<name> --write
```

It reports the caption band and, on collision, writes a conservative `captionsTop` into
`mapping.json` — every overlay is then automatically fitted above the text instead of
eating the first word of each line. Say plainly that a re-export with the captions in
the lower third (or a raw rush) gives a better-looking result, then carry on: a fitted
reel ships today, it does not wait for a re-export.

With `captionsTop` set, prefer `"imageFormat": "landscape"`: the fit shrinks by height,
and landscape keeps the full 41% width where a square would collapse to 23%.

## 2. Transcribe FIRST — never guess timings

```bash
bash scripts/transcribe.sh ~/pimpmyreels/<name>/rush.mp4 ~/pimpmyreels/<name>
```

Produces `segments.json` (sentences) and `words.json` (word-level). It skips itself
if already done.

- **Trust the timecodes, never the spelling.** Whisper mangles words ("persimmonité",
  "un vir"). That is fine — you only need *when*, not perfect text.
- `frame = seconds × fps` — and **fps is whatever `mapping.json` says**, never an
  assumption. Phone rushes come in 24, 25, 30, 50 and 60fps; treating a 60fps rush as
  30 puts every single image at double the intended time. `init_mapping.sh` reads the
  real value (and warns on variable frame rate, which breaks the formula entirely).
- To find a specific word's timecode, grep `words.json` for it.

## 3. Write the brief — MANDATORY (export.sh refuses without it)

```bash
python3 scripts/brief.py init ~/pimpmyreels/<name>     # one beat per sentence, fields empty
```

**Read `references/idea-bank.md` FIRST**, then `~/.pimpmyreels/taste.md` if it exists
(every swap and rejection this user ever made). Then fill, for every beat:

| field | what goes in it | what gets refused |
|---|---|---|
| `idea` | what the sentence **means** | empty |
| `scene` | **one concrete picture** a viewer recognises as that idea *without the words*: a human moment, a cultural reference, a graphic object with an obvious reading | a keyword; anything abstract (gradient, texture, pattern, shape, silhouette) |
| `register` | `film` `meme` `gif` `icon` `photo` `graphic` | culture (`film`+`meme`+`gif`+`icon`) outside **50–85 %**; `graphic` over 20 % |
| `refs` | the film / series / meme / artwork you **considered**, even when a photo wins | empty — an editor with no reference in mind ships stock |
| `query` | what the **engine** needs: title + actor + moment, or subject + action + framing | a copy of `scene` |
| `engine` | `ddg` for films/memes/gifs, `unsplash` for photos, `wikimedia` for icons | — |

**The one rule under all of it: illustrate the IDEA, never the WORD.** "Spiritual" is a
monk, not a pink rectangle. "Degree" is an amp that goes to eleven, not a thermometer.
"Yes or no, black or white" is Morpheus holding out two pills, not two squares.
"Putting yourself in a box" is a *Hello my name is* sticker, not a cardboard box. When
the idea is abstract, the picture must be MORE concrete, not less — that is exactly
where the reference reels use a cultural scene.

Still true, still enforced by the brief:

- **One image per idea, one every 2–3 s** on a dense script; an enumeration is as many
  images as it has items. `brief.py check` warns on any hole longer than 5 s.
- **Close-ups and medium shots only** — at 41 % of the frame a wide shot is a smudge.
- **Ask what the reference NARRATES.** Distracted-boyfriend is a man cheating; it does
  not illustrate "respect".
- **Make this reel unique** (no still reused across the user's reels), **stay current**
  (1–2 references from the last 2–3 years), **1–2 gifs** on reaction beats, **alternate
  punch and breath**. **Cinema is the base material, photography is the breathing space
  between punches** — the author asked for more film scenes, not fewer.

```bash
python3 scripts/brief.py check ~/pimpmyreels/<name>    # refuses a lazy brief, exit 1
```

## 4. Source — from the brief, 3 candidates per beat

```bash
python3 scripts/brief.py source ~/pimpmyreels/<name>   # candidates/<NN-slug>/ per beat, idempotent
```

To re-source one beat with a better query, call `source_images.py` directly:

```bash
python3 scripts/source_images.py --query "<title actor moment>" --concept <tag> \
  --out ~/pimpmyreels/<name>/candidates/07-<slug>/ --candidates 3 --engine ddg
```

Engines, measured: **DuckDuckGo** returns real stills for films Bing gets wrong (Rain
Man, A Beautiful Mind, Inside Out) and indexes Tenor — first choice for films, memes and
gifs. **Unsplash** for design photography (50 req/h). **Wikimedia** for historical
figures and artworks. **Bing** as fallback. `--bank-max 0` keeps every reel fresh;
`--format landscape` only for a wide meme gif whose text a square crop would amputate.

## 5. Look, name, validate — THE semantic gate (BLOCKING)

```bash
python3 scripts/build_board.py ~/pimpmyreels/<name>              # candidates, whole, outlined
```

Choose by number, copy the winners into `img/`, put each path in the beat's `image`
(`project/img/<file>.jpg`), then:

```bash
python3 scripts/validate_picks.py ~/pimpmyreels/<name> --sheet-only   # picks_sheet.png
```

**Open `picks_sheet.png` and, for every pick, write `shows`: 2+ words naming what is
LITERALLY in the frame** — the content, not the concept you searched. Then the sentence
sits above the picture and `shows` below it, and the test is one glance: if the picture
needs the folder name to make sense, it fails. A reel shipped where "name badges" were
restaurant menu clipboards and "a dismissal" was two old men playing chess, because
every pick was made off a 200 px thumbnail and assumed right by its folder name.

```bash
python3 scripts/validate_picks.py ~/pimpmyreels/<name>       # stamps .picks-ok, or refuses
```

It refuses: a missing `shows`, a `shows` that copies the query, a `shows` describing an
abstract or generic image (gradient, pattern, shape, silhouette, stranger portrait,
cardboard box, mug, fabric…), an image used twice, an undersized file, and a culture
share outside 50–85 %. Watermarks are `export.sh`'s job; run
`detect_watermark.py` on the candidates folder early to save a round-trip.

**Then show `picks_sheet.png` to the human, state the picks, and wait.** Their taste
beats yours. **Write what they swapped** into `~/.pimpmyreels/taste.md`, one line per
decision — that log is how their choices reach the NEXT reel instead of being
re-litigated. Never render before explicit human validation.

## 6. mapping.json — generated, never hand-written

```bash
bash scripts/init_mapping.sh ~/pimpmyreels/<name>     # fps / size / durationInFrames from ffprobe
python3 scripts/brief.py mapping ~/pimpmyreels/<name> # segments from the brief (+ collage)
```

- `start` comes from the sentence timecodes in the brief (3-frame lead applied).
- **Collage**: list 6 validated images in the brief's `collage` — no text on it, the user
  adds titles in Captions. **It holds through the ENTIRE hook line** (`collageMinSeconds`,
  3 s floor); the template drops any cutaway swallowed underneath and starts the next one
  exactly when the collage ends.
- `format` defaults to square; `"format": "landscape"` only for a wide composition a 1:1
  crop would destroy. `speaker` / `images` per beat are carried through for mode 2.
- Any hand edit to `mapping.json` or `brief.json` voids the stamp: re-run
  `validate_picks.py` (seconds) before `export.sh`.

## 7. Render

```bash
bash scripts/export.sh ~/pimpmyreels/<name> --draft   # fast, half resolution
bash scripts/export.sh ~/pimpmyreels/<name>           # final, CRF 15
```

**Never re-render everything for a partial change.** If the edit starts at frame N,
re-render only from there and splice onto the existing export:

```bash
bash scripts/export.sh ~/pimpmyreels/<name> --from N
```

The head of `out/reel.mp4` is kept (frame-accurate), only N→end is re-rendered.
Changing a single image is a two-number edit plus seconds of render, not a full
re-export. (`--from` needs a previous full export; the manual equivalent lives in
`references/golden-path.md`.)

## 7b. The user re-edited their rush (re-cut)

A shortened or re-ordered rush is a NEW timeline, not a tweak: every timecode is dead,
and the speech may be restructured, not just trimmed. But the images survive — they
were validated once and stay validated.

1. New project folder, copy the old project's `img/` across.
2. Re-transcribe (never reuse the old `words.json` — this is the whole point).
3. Re-map the existing images onto the new word timings. Orphaned images (their
   sentence was cut) are dropped; a surviving image may fit a DIFFERENT line better
   than the one it originally illustrated — check.
4. Skip sourcing and the board entirely unless the new cut contains new ideas.

Cost of a re-cut handled this way: one transcription plus one render. No sourcing,
no validation round-trip.

## 8. Prove it before delivering (BLOCKING GATE)

Extract 6–8 frames spread across the final mp4 and **look at them**:

```bash
for t in 1 5 12 20 30 40; do ffmpeg -y -ss $t -i out/reel.mp4 -vframes 1 chk_$t.png -loglevel error; done
```

Verify and **show** them: images land on the right words · no watermark or black bars ·
images full-bleed · hard cuts (no fades) · collage clears the face · **burned-in
captions fully readable — not one letter covered**.

**Safe zone check — mandatory, measured, not eyeballed.** Platform UI covers the top
200px, the bottom 340px and the right 140px of a 1080×1920 frame. Nothing meaningful
may enter those. Measure it:

```bash
# 1. Same frame index, twice: once with segments, once with segments emptied.
#    Different frame numbers would diff the moving video too and measure nothing.
npx remotion still ReelCutaways /tmp/withimg.png --frame=400      # normal mapping
#    then temporarily set "segments": [] in mapping.json and:
npx remotion still ReelCutaways /tmp/nude.png --frame=400
# 2. Measure the overlay's bounding box:
python3 - <<'EOF'
from PIL import Image, ImageChops
b = ImageChops.difference(Image.open('/tmp/nude.png').convert('RGB'),
                          Image.open('/tmp/withimg.png').convert('RGB')).getbbox()
print('bbox', b, '| top>200:', b[1] > 200, '| bottom<1580:', b[3] < 1580, '| right<940:', b[2] < 940)
EOF
```

**Timing integrity — same check, one command.** The export must have exactly the same
duration and frame count as the rush; any difference means drift, and every image is
off by that much:

```bash
for f in rush.mp4 out/reel.mp4; do
  ffprobe -v error -select_streams v:0 -count_frames \
    -show_entries stream=nb_read_frames,r_frame_rate \
    -show_entries format=duration -of default=noprint_wrappers=1 "$f"
done
```

**Check the file's modification time**: a failed render exits 0 and leaves the previous
export in place, where a matching frame count makes a 90-minute-old file look fresh.

Frame count and duration must match. If they don't, the mapping's `fps` or
`durationInFrames` is wrong — regenerate with `init_mapping.sh`, never patch by hand.

All three safe-zone bounds must be True **for cutaway images**. The intro collage is the single
documented exception: it sits higher (top 44) and clips into the header zone, exactly
as the reference reels do — it is a 1–2s flourish, not information. Every other frame
obeys the box. This rule existed in `insta-specs.md` from day one and was
still violated for three versions — because nothing checked it. Check it.

No delivery without shown proof — "it should be fine" is not a result.

## 9. Deliver

Hand over `out/reel.mp4` and `out/cover.jpg`. `export.sh` has already copied the reel
to `~/Downloads/<project>-reel.mp4` and revealed it in Finder — say where it landed, do not make the
user hunt for a path. Then run, without asking:

```bash
python3 scripts/contribute.py ~/pimpmyreels/<name>
```

It silently shares newly validated images with the bank and bumps usage counters on
existing ones (one line of output — never a question; images that survived the whole
pipeline are validated by revealed preference).

Close with hook advice from `references/hooks.md` — advisory only, never blocking.

---

## Mode 2 — full-frame backgrounds (cutout rush)

When the rush is the speaker CUT OUT on transparency, the format flips: the person
floats small and centred, and the images fill the whole frame behind them.
`init_mapping.sh` detects the alpha channel and sets `"mode": "background"` on its
own — you never ask.

- **Rush**: must carry real alpha — ProRes 4444 `.mov` or VP9 `.webm`. A green-screen
  or HEVC-alpha export converts first:
  `ffmpeg -i cutout.mov -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le rush.mov`
  (green screen: insert `-vf "chromakey=0x00FF00:0.12:0.05"` before `-c:v`).
- **Each segment carries an `images` ARRAY (1-4)**, not a single image. Layouts are
  fixed: 1 = fullscreen, 2 = stacked halves, 3 = top band + two quadrants, 4 = 2x2
  grid. Edge to edge, no gap, hard cuts — same rules as ever.
- **The hook is a 4-grid.** After it, no rule: 1, 2 or 4 per beat as the words demand.
  A single strong image fullscreen breathes; a 4-grid punches.
- **Backgrounds are Unsplash ONLY — never the scrape.** `--engine unsplash` no longer
  falls back: an empty result beats slop. On the first mode-2 reel, 16 of 26 backgrounds
  came from the scrape and the user rejected every one of them — "old stock, no depth,
  no sense" — and two carried a "Magnific" watermark grid that the watermark gate does
  not know and could not read. A clean source is the only reliable defence; the gate is
  a net, not a guarantee.
- **SHOW THE WORLD THE SCRIPT LIVES IN — that beats any metaphor.** Three passes were
  burned choosing images that were *about* the idea instead of showing the situation:
  a sprinter on a track for "a bolder guy than you", Superman for "you're an introvert",
  a white dress in a forest for "the pure-princess myth", a plated table for "she's
  interested". A seduction script lives in bars, clubs, parties, people approaching each
  other — so that is what the backgrounds must be. Read the script, name its WORLD, and
  source inside it. Metaphor is the exception you reach for when the world has no image
  for that beat, never the default.
- **METAPHOR MEANS A HUMAN MOMENT, NOT A TEXTURE.** The second mode-2 pass swung from
  bad stock to macro objects — red silk for "desire", coffee cups for "she talks to
  you", lace for "the pure princess myth", cubes, a suit sleeve — and the user rejected
  all of it just as hard: fabric does not say desire. What works is what has always
  worked here: **recognisable moments that tell a story** (Drake refusing, Gandalf's
  bridge, Clark Kent's shirt, an Uno reverse) and **cinematic human scenes with depth**
  (a woman meeting your eye on a neon street, a silhouette walking away in the rain, a
  suited man arms crossed, a cliff jumper). Query Unsplash in that register —
  "woman confident eye contact night city cinematic", not "red silk fabric macro".
- **An image validated at 41% is NOT automatically valid full-frame.** Two shipped that
  way and both failed: a green-screen "JUST DO IT" gif (a green square is invisible at
  41%, a green wall at 100%) and a flat cartoon Cinderella (charming small, a slab of
  cyan large). Re-judge every reused reference at full bleed.
- **Leave the MIDDLE free — that is where the user's subtitles go.** Default the
  speaker to the upper third (`speakerY` 0.26, `speakerScale` 0.36), as the reference
  reels do: person small and high, captions across the centre, background everywhere.
- **MOVE THE SPEAKER, AND CHECK IT ON THE BOARD.** Each segment takes
  `speaker: {x, y, scale}` (defaults 0.5 / 0.26 / 0.36, normalised). Judge candidates
  on a board that composites the cutout over the full-bleed crop — otherwise you ship a
  cliff jumper the speaker covers entirely, which happened. Subject centre-left → push
  the speaker to x 0.68, subject right → x 0.30.
- **A background whose subject is small is unusable**, exactly as in mode 1: full-bleed
  does not rescue a wide shot, it just enlarges the emptiness around a tiny figure. A fixed centre cutout masks the very subject being
  illustrated — a statue, a face, a rose. Read each background and push the speaker to
  the empty side: subject centre-left → x 0.65, subject low → y 0.30, and so on.
- **Source with `--format portrait --engine unsplash`** — cells are 9:16 or 9:8, and a
  wide still cover-cropped to portrait loses most of itself. Unsplash is the right
  engine for ambiance and metaphor (design photography, no watermarks, no AI slop);
  the scrape chain stays for film stills and memes. Favour METAPHOR over decoration:
  crystal dice for "dare", a sprinter in the blocks for "bolder than you", a handed
  rose for "you offer" — comprehensible in half a second, beautiful, modern. Ambiance-first reads best at full
  bleed (offices, skies, streets, close objects); precise film stills still work when
  their subject is central.
- **Speaker placement**: `speakerScale` (default 0.45), `speakerX`/`speakerY`
  (defaults 0.5/0.40) in mapping.json. One steady placement — the reference reels
  never bounce the person around.
- **Safe zones do not apply to the backgrounds** (they are full-bleed by design, like
  the reference reels); the speaker default keeps them clear of platform UI. Still
  zero text: titles and subtitles stay the user's job (Captions).
- Everything else is unchanged: transcribe first, word-synced starts, the board gate,
  the watermark gate, the proofs.

## Anti-patterns

The 15 mistakes that were actually made building this pipeline, and the rule each one
produced, are in `references/style-rules.md`. Read them before your first mapping.

## Worked example

`references/golden-path.md` contains one complete real run — transcript, mapping
table, board, resync, economical iteration, export. Imitate its rhythm.
