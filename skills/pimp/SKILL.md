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

## 3. Think the mapping BEFORE sourcing anything

Read `references/mapping-guide.md` (concept → validated iconic scenes) and
`references/style-rules.md` (the hard rules and the anti-examples).

- **Show every word that can be shown.** One image per *idea*, and an enumeration is
  as many ideas as it has items: "posture, diction, vocabulary, hygiene, intelligence,
  general knowledge" is six images, not one. Two images across nine seconds of dense
  speech is padding, and it reads as padding.
- **Aim for one image every 2–3s** on a dense script. The old guidance here said one per
  4–6s and produced exactly the sparse result users reject. Slow down only where the
  speaker's face genuinely carries the line — a direct address, a pause, the CTA.
- **CLOSE-UPS AND MEDIUM SHOTS ONLY.** A cutaway is 41% of the frame width; on a phone
  that is about the size of a matchbox. A wide shot — a figure in a room, a crowd, a
  full-body walk — turns into an unreadable smudge, and no crop can save it, because the
  subject is small in the source. Judge every candidate at its final size on the board,
  not full-screen. This is the single most common reason a technically-fine image fails.
- Only **instantly recognizable** subjects: if it takes more than half a second to read,
  it's the wrong image.
- **And ask what the reference NARRATES.** Recognisable is not enough: a famous meme
  carries its own story, and that story must agree with the sentence. Real miss —
  distracted-boyfriend (a man cheating) placed in a reel about respect.
- **It does not have to be a film.** A meme, a gif, a plain photograph of the object or
  gesture being named — anything that makes the word visible. Films are a reliable source
  of iconic, recognisable frames, not a requirement.
- 1.5–8s per image. A great image can hold 6s; a weak one is wrong at any length.
- **Make this reel unique.** The bank is a quality standard, not a shopping list. If
  the user already has reels, do not reuse the same still for the same idea — the
  alternates table in `mapping-guide.md` exists for that, and the engine surfaces
  fresh candidates first. Two reels that look alike is a failure, even if each one is
  individually fine.
- **Stay current.** Include **1–2 references from the last 2–3 years** when the topic
  allows (recent series, films, memes actually circulating), on top of the timeless
  classics. Ask the user what they're watching if you're unsure.
- **Use 1–2 gifs per reel, not zero.** The pipeline is fully wired for them
  (`--gif` sourcing with header+PIL validation, `<Gif>` rendering) and they have been
  used exactly once across six real reels — a wired feature nobody uses is a missing
  feature. Reaction beats are the spot: panic, "no no no", "just do it", an eye-roll.
  Never more than two: motion is salt, not the dish.
- **Mix punch and breath, roughly 50/50.** A wall of movie stills reads as noisy
  meme-spam. The reels that look premium alternate a *punch* (meme / iconic scene)
  with a *breath* (an atmospheric, cinematic, slightly surreal image). Plan both when
  you write the mapping — see the "Punch and breath" section of `mapping-guide.md`.

**Read `~/.pimpmyreels/taste.md` first if it exists** — it is the record of every
swap and rejection this user has made on past boards. A mapping that repeats a logged
rejection is a wasted round-trip you chose to have.

Write the plan as a table (timecode · word · film · why) before touching the network.

## 4. Source 3 candidates per beat

```bash
python3 scripts/source_images.py --query "<film actor precise scene> scene" \
  --concept <tag> --out ~/pimpmyreels/<name>/candidates/01-<beat>/ --candidates 3
```

By default **only 1 of the 3 candidates comes from the banks** (freshest first, across
all tiers — an unused community still outranks a core one you already used); the other
2 are sourced fresh from the web. That is deliberate: it keeps every reel visually
different while the bank keeps the quality bar. `--bank-max 3` forces bank-only
(useful offline), `--bank-max 0` forces all-fresh.

Images are **square by default** (`--format square`), which is also what the aspect
filter enforces — atmospheric images are often 1:1 and would be rejected by the
landscape filter. Pass `--format landscape` only for wide compositions you intend to
display as landscape.

Wide meme gifs (the classic 498x280 format) get `"format": "landscape"` in their
segment — a square cover-crop amputates the meme's own text.

Craft web queries per `references/query-guide.md` (it has a dedicated section for
atmospheric images — they are searched by mood, not by film). Add `--gif` for
animated memes.

## 5. QA + validation — ONE board, two uses (BLOCKING GATE)

```bash
python3 scripts/build_board.py ~/pimpmyreels/<name>
```

This builds a single numbered sheet: row = beat, columns = candidates, labelled
`beat.candidate` (`2.3` = beat 2, candidate 3).

**Read that one sheet.** Never open candidate files one by one — it costs ~20× more
for the same information.

**Use `build_board.py` — do not hand-roll a contact sheet that centre-crops.** The board
shows each candidate WHOLE with the displayed square outlined, on purpose: a cropped
thumbnail hides what the file is. A stacked three-panel montage shipped to a user
because an ad-hoc square-cropped sheet showed only its middle panel, which looked fine.
Structure and framing must be judged in the same glance.

Run `python3 scripts/detect_watermark.py <project>/candidates/<beat>` on anything you
are about to keep — a tiled stamp is invisible at board size and `export.sh` will
refuse the render anyway. Reject, by number: watermarks and source logos, black bars, posters instead of scene
stills, AI-looking renders, and anything that isn't the scene you asked for. Re-source
the rejected beats with a better query; if a domain keeps polluting results,
`python3 scripts/source_images.py --reject <domain>` teaches the blocklist. Rebuild
the sheet, then re-read it.

**Then show the sheet to the human**, state your picks (`1.2, 2.1, 3.3`) and the film
behind each, and **wait**. They swap what they want. Their taste beats yours — this
gate exists because it repeatedly caught choices that were technically fine and
editorially wrong.

**Never render before explicit human validation.**

**Then write down what they swapped.** Append one line per decision to
`~/.pimpmyreels/taste.md` — `rejected Indiana Jones for "courage": too old, wants
modern` / `swapped in Vikings: watches it`. That file is the user's taste, learned
the only way taste can be learned. It is not optional bookkeeping: the board gate
exists because their choices beat yours, and the log is how their choices reach the
NEXT reel's mapping instead of being re-litigated every time.

## 6. Write mapping.json

**Generate the skeleton first — never hand-write fps or durationInFrames:**

```bash
bash scripts/init_mapping.sh ~/pimpmyreels/<name>
```

It probes the rush with ffprobe and writes the correct `fps`, `width`, `height` and
`durationInFrames` (a wrong fps desyncs every image; a wrong duration cuts the reel
short). You only fill in `segments`. Do **not** copy `mapping.example.json` — it
points at the doctor's test fixture, not at your project.

Schema reference: `../../template/mapping.example.json`.

- `start` comes from the word timecodes. This is the whole point.
- Copy the chosen images into `~/pimpmyreels/<name>/img/` and reference them as
  `project/img/<file>.jpg`.
- **No gaps**: omit `end` and each image holds until the next one starts.
- Open with a **collage** of 6 validated images — **no text on it**. The user adds
  titles and subtitles themselves (Captions app). Place it high enough to clear the
  speaker's face.
- **The collage holds through the ENTIRE hook line — 3s is the floor, not the target.**
  Find where the hook sentence ends in `words.json` and start the first cutaway there;
  an image that fires mid-hook burns itself on words that belong to the collage. The template enforces this
  (`collageMinSeconds`), drops any cutaway swallowed underneath, and starts the next
  one exactly when the collage ends. So write your first cutaway's timecode from the
  words as usual and let the template resolve the opening; do not hand-shift it.
- **`format` defaults to square** — leave it out. Only set `"format": "landscape"`
  for a wide composition that a 1:1 crop would destroy; that is the exception.
- `align: "left"/"right"` occasionally, to vary the eye. Not every image.

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
