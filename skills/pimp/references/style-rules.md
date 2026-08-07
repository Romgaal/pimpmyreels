# Style rules

The look is deliberately minimal. Every rule below exists because the opposite was
tried and rejected on real reels.

## Hard rules

| Rule | Why |
|---|---|
| **Hard cuts only.** No fades, no dissolves, no transitions of any kind. | Reference reels that perform have none. Transitions read as "edited by a beginner". |
| **No zoom, no Ken Burns, no motion on the image.** Images are static. | Movement steals attention from the speaker and the meaning. |
| **No shadow, no glow, no border chrome, no window frames.** | The image is the content. Decoration around it looks like a template. |
| **No text on or under the images.** No labels, no captions of your own. | The user adds titles and subtitles themselves (Captions app). Your label duplicates or contradicts theirs. |
| **Full-bleed images.** No logos, no watermarks, no black letterbox bars. | A watermark instantly cheapens the whole reel. |
| **No gaps.** Each image holds until the next one starts. | Empty stretches break the rhythm; the eye expects continuity. |
| **Intro collage:** 3×2 grid of 6 validated images, no text, high enough to clear the face. | Standard opener on this format — it promises the content. |
| **Square format for close-ups only.** Never square-crop a wide composition. | See the Rocky anti-example below. |
| **Left/right offsets sparingly.** Most images centered. | Occasional offset catches the eye; constant offset is noise. |
| **Duration 2–10s.** A strong image can hold 8s. | Length is not the problem — a weak image is wrong at any duration. |
| **Bank images get the same visual QA as scraped ones.** | The community tier is not curated. Look before you use. |

## Anti-examples — real mistakes, and the rule each produced

| What was done | Why it failed | Rule |
|---|---|---|
| Timings estimated from reading the script | Images landed on the wrong words — Gatsby appeared on "95% of people are kind", the intellectual on "you're funny" | **Transcribe first. Always.** This is failure #1. |
| Images wrapped in a macOS window frame (title bar, traffic-light dots) | Looked like a screen recording, not an illustration | Raw image, nothing around it |
| A descriptive label under each image ("your full potential") | Redundant with the speech, competes with the user's subtitles | No text |
| Drop shadow under the images | Reads as a slide deck | No shadow |
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

## Calibration log

Style constants live in `template/src/ReelCutaways.tsx` (image sizes, top offset) and
`template/mapping.example.json` (defaults). `/pimp-calibrate` may update them against
current trends. Log changes here.

- **0.1.0** — initial: landscape 51.9% of width, square 43.5%, top 118px, collage 3×2 at top 44px.
