# Changelog

## 0.4.10 — a famous meme can tell the wrong story

- **Check what a reference NARRATES, not just whether it is recognised.** The
  distracted-boyfriend meme is universally known and depicts a man cheating on his
  girlfriend; dropped on "if you don't dare, you give up your spot" in a reel preaching
  respect, it contradicts the speaker. Caught by the user, not the pipeline. New rule
  in style-rules: before every pick, ask what story this frame tells someone who knows
  it — that story has to be the sentence's.
- **The splice now verifies itself.** Even trimming the head by frame count, the
  assembled file came out one frame short intermittently. `--from` now compares the
  result against the mapping and, on mismatch, re-renders in full and says so. An
  optimisation that silently shifts every image after the cut is worse than none.

## 0.4.9 — the collage owns the hook, and splices cannot drift

- **The collage holds through the WHOLE hook line** — 3s is the floor, not the target.
  A cutaway that fires mid-hook burns an image on words that belong to the collage
  (a real reel had Rocky appear at 3.0s inside a 5.2s hook; the user caught it).
- **Gifs render in their native aspect.** A 498x280 meme gif cover-cropped into a
  square loses its text; set `"format": "landscape"` on wide gifs — the landscape
  box (560x322, ratio .575) matches the classic meme ratio almost exactly.
- **`--from` splices are now frame-exact, twice over.** The head was trimmed with
  `-t` (seconds) and encoder rounding once produced a 233-frame head for 234 asked;
  worse, re-splicing onto the drifted result compounded the loss (1722 -> 1721 ->
  1720). The head is now cut with `-frames:v`, and --from refuses outright to splice
  onto a base whose frame count no longer matches the mapping. Proven: full render
  1722 -> splice -> still 1722.
- taste.md grew a context rule: an image that worked for one line can be "nul" for
  another — context outranks the image's own track record.

## 0.4.8 — taste is data, re-cuts are cheap, gifs are used

- **`~/.pimpmyreels/taste.md`** — every board swap and rejection gets one logged line,
  and the mapping step of the NEXT reel reads the file first. Six reels of decisions
  were living only in conversation history; a mapping that repeats a logged rejection
  is a wasted round-trip. Ships with nothing; grows with use.
- **Re-cut workflow (7b).** A shortened rush is a new timeline: re-transcribe, re-map
  the already-validated images, drop orphans, re-check fits. No sourcing, no board.
  A real re-cut cost one transcription and one render.
- **Show the action, not a mood** (mapping-guide): the frame performs the VERB of the
  sentence — someone mid-approach beats a confident face. Portraits are the weakest
  cutaways. Plus the caption test: no words around it, half a second, or reject.
- **Enumerations are a burst**: one image per listed item at the word's own pace.
- **Gifs: 1–2 per reel is now the target, not a suggestion** — the pipeline was fully
  wired and used once across six reels.

## 0.4.7 — show every word, and only in close-up

- **Density was wrong by a factor of three.** The method asked for one image per 4-6s
  and produced reels a user called padding: two images across nine seconds of dense
  speech. It now asks for **one image every 2-3s**, and treats an enumeration as as many
  images as it has items — "posture, diction, vocabulary, hygiene, intelligence, general
  knowledge" is six images in three seconds, not one. On a real 86s reel this took the
  count from 16 to 39.
- **Close-ups and medium shots only.** A cutaway renders at 41% of frame width — a
  matchbox on a phone. A wide shot's subject is a smudge there and no crop repairs it,
  because the subject is already small in the source. A full-body James Bond shipped
  this way and was unreadable. Every query now carries "close up" or "medium shot", and
  candidates are judged at final size on the board.
- **Films are a source, not a requirement** — but the split matters: an *object* (an ear,
  a dictionary, a library, chess pieces) photographs fine as a plain image, while a
  *human idea* searched as a generic photo comes back as AI portraits, white-background
  cutouts and flat illustrations. Half of one batch had to be rebuilt for exactly that.
  Human ideas need a recognisable anchor: a film, a series, or a meme.

## 0.4.6 — the images sit lower, where the phone actually shows them

- **`imageTop` 235 -> 310, collage 44 -> 150.** Reported from a published reel, not
  theorised: on a real iPhone the Instagram Reels header ("Reels", camera icon) is drawn
  over the top band, and the collage landed under the word. The old values came from
  reference reels seen as files; these come from one seen on a phone.

## 0.4.5 — the export stops overwriting your source video

- **Data-loss fix.** Delivery wrote `~/Downloads/<project>.mp4`. On a project named
  `film`, whose rush had come from `~/Downloads/film.mp4`, the export overwrote the
  user's original video. Recoverable only because the pipeline keeps its own copy of
  the rush inside the project. Deliveries are now `<project>-reel.mp4`, and `export.sh`
  additionally refuses to write onto any path the project reads from.

## 0.4.4 — the collage is the hook, and it gets three seconds

- **The intro collage now holds for at least 3s** (`collageMinSeconds`, default 3).
  It was ending after a beat or two — sometimes 0.9s — which throws away the visual
  that stops the scroll during the exact window the hook needs. Enforced in the
  template, not left to whoever writes the timings.
- **Cutaways under the collage are handled, not clipped blind.** One swallowed
  entirely is dropped; one left under a second by the clip is dropped too (a
  fraction-of-a-second image reads as a glitch) and the next cutaway takes over the
  instant the collage ends, so no gap opens. The first version of this fix did leave
  a 0.7s hole — the timeline is now resolved once, before rendering, instead of
  being decided inside the render loop.
- **Delivery goes to `~/Downloads`** instead of the Desktop: that is where rushes
  arrive and where people already look. `PIMP_DELIVER_DIR` still overrides it.

## 0.4.3 — the file lands somewhere you can find it

- **`export.sh` now delivers.** A path printed in a terminal is not a delivery: the
  reel sat in `~/pimpmyreels/<name>/out/` and finding it meant navigating there by
  hand, every time. Each export now also lands in `~/Desktop/Reels/<project>.mp4`
  (+ cover) and, on macOS, opens Finder with the file selected. `PIMP_DELIVER_DIR`
  overrides the folder; `PIMP_DELIVER_DIR=off` disables it.
- **query-guide: name the moment, not the film.** Generic `"<film> scene film still"`
  queries match fan-made grid compilations best — 8 of 36 candidates on one reel.
  Three pixel heuristics to filter grids were written and all three dropped (2/9,
  3/11 with a false positive, 5/11); the board gate catches them anyway. The query
  is the fix, with a before/after table.

## 0.4.2 — burned captions no longer get eaten

- **`detect_captions.py` (new).** A rush that already went through Captions/CapCut often
  carries its text HIGH — at y488 on a real one, right inside the 235-678 cutaway band.
  The images then cover the first word of every line ("d'aborder." shipped as "order.").
  Detection diffs frame pairs: swapping text saturates pixels, a moving face doesn't, so
  a threshold of 180 isolates the caption band (60 catches the whole body). Verified on
  three rushes: one true positive, two true negatives.
- **`captionsTop` in mapping.json**: overlays (cutaways *and* the intro collage) are
  fitted above the band, keeping their aspect ratio, instead of covering it. The value is
  reported conservatively — 10 sampled frames cannot see the tallest caption line of 1200,
  measured 517 by sampling vs 488 by hand — so it means "nothing goes below this".
- **`imageFormat`** at mapping level. Under a caption fit, landscape keeps the full 41%
  width where a square would collapse to 23% for the same available height.
- **The method now states the order**: pimp the raw rush, add captions last.
- **Fix: the last frame was dropped.** `int(duration * fps)` truncates on float error
  (40.533 x 30 = 1215.99 -> 1215). `init_mapping.sh` now takes the container's own
  `nb_frames` as ground truth (verified: 1216).

## 0.4.1 — timing integrity

- **Fix: right-aligned images entered the icon rail.** `paddingRight` was 64px while
  the platform rail eats ~140px — a right-aligned cutaway reached x=1016 (limit 940).
  Now 150px. Caught by the v0.4 safe-zone check on a real reel, one render before
  shipping it. Margins are asymmetric on purpose: 64 left (no UI there), 150 right.
- **Never assume the frame rate.** The method said "rushes are usually 30fps" — an
  invitation to guess. A 60fps rush treated as 30 puts every image at double its
  intended time. fps now always comes from `mapping.json`, which `init_mapping.sh`
  reads from the file itself (verified: a 60fps rush is detected as 60).
- **Variable frame rate is detected and refused.** Phone recordings are often VFR, and
  `frame = seconds × fps` silently stops being true — every image drifts. `init_mapping.sh`
  compares r_frame_rate against avg_frame_rate and prints the exact ffmpeg command to
  convert to CFR (verified on a real VFR file: 60 announced vs 18.4 actual, caught).
  Non-zero stream start times are flagged too.
- **Drift check added to the proof step**: the export must have the same frame count and
  duration as the rush. Any difference means every image is off by that much.

## 0.4.0 — the polished look

Calibrated against reference reels, every change measured on a real reel:

- **Safe zone fixed.** `imageTop` 118 → **235**. The code had been violating its own
  `insta-specs.md` (documented 200px UI header) since 0.1 — the top of every cutaway
  sat under the Instagram interface. Proven: bbox top 118 (violation) → 235 (compliant).
- **Square by default**, 41% of frame width (was landscape at 52%, which overwhelmed
  the speaker). Landscape is now the justified exception.
- **Sourcing follows the format**: new `--format square|landscape` drives the aspect
  filter. The old landscape-only gate rejected square/atmospheric images outright —
  it would have made the point below impossible.
- **Punch and breath, ~50/50.** The method now asks for half memes/film stills and half
  atmospheric, cinematic images sharing one tonal universe. A wall of stills reads as
  meme-spam; the alternation is what looks premium. New sections in mapping-guide and
  query-guide (atmospheric images are searched by mood and composition, never by film).
- Collage centered at 68% wide, 4px gap, square cells; corner radius 10 → 4; optional
  subtle `imageShadow` (off by default).
- **Safe-zone check is now part of the proof step** — measured with a bounding box on
  the same frame with and without the overlay. A documented rule that nothing enforces
  is a wish. The intro collage is the one written-down exception.

## 0.3.0 — crash-test fixes

Full audit (8 findings), everything proven by command:

- **init_mapping.sh** (new): probes the rush with ffprobe and generates a correct
  mapping skeleton — real fps, width/height, durationInFrames. Kills the wrong-fps /
  cut-short class of bugs. (The audit itself caught a live one: the demo rush is
  25fps, not the assumed 30.)
- **export.sh --from N**: economical iteration is now one command — re-renders only
  frames N→end and splices onto the existing reel, frame-accurate (proven: identical
  frame count after splice).
- **contribute.py re-run safe**: a per-project `.contributed.json` marker makes
  re-runs contribute only the delta — honest use_count, no duplicate PRs.
- **make_demo.sh**: picks Thomas, else any installed French voice, else the default
  voice with an English script — no more silent French-text-English-voice demo.
- **valid_gif()**: scraped GIFs are verified (header + PIL parse) before being kept.
- Docs: honest disk figure (~470MB), bank coverage note (seed leans
  personal-development; other niches grow via mybank + contributions).

## 0.2.1 — fresh-install fix

- **Fix**: `doctor.sh` failed `template-render` on every fresh install. It rendered the
  current `mapping.json`, which points at project assets that do not exist yet (they
  are gitignored). Found by an end-to-end install test — a locally-dirty dev machine
  could never reproduce it.
- A tiny fixture (36KB: 2s clip + 6 thumbnails) is now committed, `mapping.example.json`
  points at it, and doctor renders **that**, restoring any in-progress project mapping
  afterwards. The check is deterministic and actually exercises the Remotion chain.

## 0.2.0 — variety

- **Anti-sameness**: only 1 of 3 candidates now comes from the banks (`--bank-max`,
  default 1); the other 2 are sourced fresh. Every reel looks different.
- **Usage memory** (`~/.pimpmyreels/used.json`): stills used in past reels are pushed
  down the candidate list, globally across tiers — an unused community image outranks
  a core one you already used. Recorded even when contribution is off.
- **Alternates table**: 3 options per concept in the mapping guide, so rotating is the
  default, not an effort.
- **Stay current**: the method now asks for 1–2 references from the last 2–3 years per
  reel, and promotes gifs for reaction beats.
- Agent-readable install (`CLAUDE.md` / `AGENTS.md`): "installe <repo url>" now works.
- Fix: `gh pr create` needed explicit `--head/--base`.
- Fix: removed mislabeled watermarked stills (Titanic) from `bank/core`.

## 0.1.0 — initial release

- `/pimp` — full pipeline: Whisper word-level transcription, concept mapping, image
  sourcing (bank first, then web), numbered validation board, Remotion render, H.264
  export with auto cover.
- `/pimp-calibrate` — tune style constants against trending reference reels.
- Image bank seeded with 29 curated stills (core) + 33 alternates (community), tagged
  by concept.
- Method encoded in `skills/pimp/references/`: style rules with 15 real anti-examples,
  mapping guide, query guide, complete worked example, hook advice, platform specs.
- One-shot `setup.sh`, `doctor.sh` diagnostics, synthetic-voice demo.
