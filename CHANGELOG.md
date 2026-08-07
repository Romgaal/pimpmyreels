# Changelog

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
