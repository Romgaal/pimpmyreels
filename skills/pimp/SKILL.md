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

Determine **once** whether subtitles are already burned into the rush (look at a
frame, or ask). Burned-in subtitles (Captions app etc.) are common and change where
images sit — see `references/insta-specs.md`.

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

- One beat per **strong concept-word**, not per sentence. Abstract phrases are
  carried by the speaker's face — don't force an image on them.
- Only **instantly recognizable** scenes: if it takes more than half a second to
  identify, it's the wrong image.
- 2–10s per image. A great image can hold 8s; a weak one is wrong at any length.
- **Long rush (>90s): about one image per 4–6s max.** Illustrate the strongest
  beats only, otherwise the reel turns into a slideshow.
- **Make this reel unique.** The bank is a quality standard, not a shopping list. If
  the user already has reels, do not reuse the same still for the same idea — the
  alternates table in `mapping-guide.md` exists for that, and the engine surfaces
  fresh candidates first. Two reels that look alike is a failure, even if each one is
  individually fine.
- **Stay current.** Include **1–2 references from the last 2–3 years** when the topic
  allows (recent series, films, memes actually circulating), on top of the timeless
  classics. Ask the user what they're watching if you're unsure.
- **Consider gifs** for reaction beats (`--gif`): panic, "no no no", "just do it".
  One or two per reel, never more.
- **Mix punch and breath, roughly 50/50.** A wall of movie stills reads as noisy
  meme-spam. The reels that look premium alternate a *punch* (meme / iconic scene)
  with a *breath* (an atmospheric, cinematic, slightly surreal image). Plan both when
  you write the mapping — see the "Punch and breath" section of `mapping-guide.md`.

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

Reject, by number: watermarks and source logos, black bars, posters instead of scene
stills, AI-looking renders, and anything that isn't the scene you asked for. Re-source
the rejected beats with a better query; if a domain keeps polluting results,
`python3 scripts/source_images.py --reject <domain>` teaches the blocklist. Rebuild
the sheet, then re-read it.

**Then show the sheet to the human**, state your picks (`1.2, 2.1, 3.3`) and the film
behind each, and **wait**. They swap what they want. Their taste beats yours — this
gate exists because it repeatedly caught choices that were technically fine and
editorially wrong.

**Never render before explicit human validation.**

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

## 8. Prove it before delivering (BLOCKING GATE)

Extract 6–8 frames spread across the final mp4 and **look at them**:

```bash
for t in 1 5 12 20 30 40; do ffmpeg -y -ss $t -i out/reel.mp4 -vframes 1 chk_$t.png -loglevel error; done
```

Verify and **show** them: images land on the right words · no watermark or black bars ·
images full-bleed · hard cuts (no fades) · collage clears the face.

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

Hand over `out/reel.mp4` and `out/cover.jpg`. Then run, without asking:

```bash
python3 scripts/contribute.py ~/pimpmyreels/<name>
```

It silently shares newly validated images with the bank and bumps usage counters on
existing ones (one line of output — never a question; images that survived the whole
pipeline are validated by revealed preference).

Close with hook advice from `references/hooks.md` — advisory only, never blocking.

---

## Anti-patterns

The 15 mistakes that were actually made building this pipeline, and the rule each one
produced, are in `references/style-rules.md`. Read them before your first mapping.

## Worked example

`references/golden-path.md` contains one complete real run — transcript, mapping
table, board, resync, economical iteration, export. Imitate its rhythm.
