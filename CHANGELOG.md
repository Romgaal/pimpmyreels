# Changelog

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
