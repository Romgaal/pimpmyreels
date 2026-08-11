# Style rules

The look is deliberately minimal. Every rule below exists because the opposite was
tried and rejected on real reels.

## Hard rules

| Rule | Why |
|---|---|
| **Hard cuts only.** No fades, no dissolves, no transitions of any kind. | Reference reels that perform have none. Transitions read as "edited by a beginner". |
| **No zoom, no Ken Burns, no motion on the image.** Images are static. | Movement steals attention from the speaker and the meaning. |
| **No glow, no border chrome, no window frames.** Shadow: **off by default** — a subtle, realistic one is available via `imageShadow: true` and nothing else. | The image is the content; decoration looks like a template. The reference reels do carry a faint shadow that lifts the image off the wall, so it is offered — but it must stay physical, never decorative. |
| **No text on or under the images.** No labels, no captions of your own. | The user adds titles and subtitles themselves (Captions app). Your label duplicates or contradicts theirs. |
| **Full-bleed images.** No logos, no watermarks, no black letterbox bars. | A watermark instantly cheapens the whole reel. |
| **No gaps.** Each image holds until the next one starts. | Empty stretches break the rhythm; the eye expects continuity. |
| **Intro collage:** 3×2 grid of 6 validated images, no text, high enough to clear the face. | Standard opener on this format — it promises the content. |
| **Square is the default format.** Landscape is the justified exception (a wide composition a 1:1 crop would destroy). | The reference reels are square throughout — one constant shape is what makes the series feel designed rather than assembled. |
| **Left/right offsets sparingly.** Most images centered. | Occasional offset catches the eye; constant offset is noise. |
| **Duration 2–10s.** A strong image can hold 8s. | Length is not the problem — a weak image is wrong at any duration. |
| **Bank images get the same visual QA as scraped ones.** | The community tier is not curated. Look before you use. |
| **Never make the same reel twice.** Rotate references across reels; don't reuse a still for the same idea. | The bank makes reels consistent — and, unchecked, identical. Variety is the whole point of a *personal* visual identity. |
| **1–2 current references per reel** (last 2–3 years) alongside the classics. | Only-classics reads as dated; only-current reads as disposable. |
| **Roughly 50/50 punch (memes/films) and breath (atmospheric images).** | All-punch is meme-spam; the alternation is what reads as premium. |
| **Nothing enters the platform safe zones** — top 200px, bottom 340px, right 140px. **Measured, not eyeballed.** One documented exception: the intro collage sits higher (top 44) and clips the header zone, as the reference reels do — it is a brief flourish, not information. | See the anti-example below: a documented rule that nothing checked was violated for three versions. An exception that is written down is a decision; one that is silent is a bug. |

## Anti-examples — real mistakes, and the rule each produced

| What was done | Why it failed | Rule |
|---|---|---|
| Timings estimated from reading the script | Images landed on the wrong words — Gatsby appeared on "95% of people are kind", the intellectual on "you're funny" | **Transcribe first. Always.** This is failure #1. |
| Images wrapped in a macOS window frame (title bar, traffic-light dots) | Looked like a screen recording, not an illustration | Raw image, nothing around it |
| A descriptive label under each image ("your full potential") | Redundant with the speech, competes with the user's subtitles | No text |
| A heavy, glowing drop shadow under the images | Read as a slide deck | Off by default; only the subtle physical `imageShadow` is allowed, and only if it earns its place on screen |
| Ken Burns slow zoom on stills | Nothing in the reference reels moves | Static images |
| Images spaced out with empty gaps between them | Rhythm collapsed | Chain them |
| Rocky's wide vista square-cropped | The composition was destroyed — the subject was lost | Never square-crop a wide shot |
| Indiana Jones leap-of-faith for "act despite fear" | Too slow to read, not iconic enough at thumbnail size | Instantly recognizable only |
| Amélie Poulain for "shy" | Wrong register for the audience | Match the audience's world |
| Movie **posters** instead of scene stills | Posters read as marketing, not as reference | Scene stills, never posters |
| Alamy / "F HD" / Movieclips watermarks | Cheapens everything | Blocklist + visual QA |
| Emoji cards as placeholders "for now" | Placeholders were shown as if they were the product | Real stills or nothing |
| Intro collage placed too low | It covered the speaker's face | Collage high, face clear |
| The radar image appeared 3s after the word "radar" | The metaphor landed after the sentence had moved on | Sync to the exact word |
| Full re-render for a single image swap | Minutes wasted, gigabytes written | Re-render the span, concat |
| Images placed at `imageTop: 118` while `insta-specs.md` documented a 200px UI header | The top of every cutaway sat under the Instagram interface — for three versions. The rule was written; nothing enforced it | A documented rule without an automated check is a wish. Measure it in the proof step |
| Landscape images at 52% of frame width | Overwhelms the speaker's face, reads as a patch stuck on top | Square at 41% — the image should feel like an object in the room |

## Calibration log

Style constants live in `template/src/ReelCutaways.tsx` (image sizes, top offset) and
`template/mapping.example.json` (defaults). `/pimp-calibrate` may update them against
current trends. Log changes here.

- **0.1.0** — initial: landscape 51.9% of width, square 43.5%, top 118px, collage 3×2 at top 44px.
- **0.4.0** — calibrated against reference reels (2026-08): **square by default at 41%**
  of width, `imageTop` **235** (clears the 200px UI header), corner radius **4**,
  collage **68%** wide and centered with a 4px gap and square cells, optional subtle
  shadow (`imageShadow`, off by default).
