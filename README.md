# pimpmyreels

**Turn a talking-head rush into a reel with iconic movie stills and memes landing exactly on the words that call for them.**

You film yourself talking. `/pimp` transcribes what you said, decides which cultural
reference illustrates each idea, finds the images, shows you a board to validate, and
renders the finished reel. You add your own subtitles and post.

Built as a Claude Code plugin. Ships with a curated bank of validated stills that
grows every time someone makes a reel.

---

## Install it in one sentence

Paste this to Claude Code:

> installe https://github.com/Romgaal/pimpmyreels

It reads `CLAUDE.md` in this repo and does the rest: registers the plugin, installs
ffmpeg / whisper.cpp / the model / Node / Remotion, and creates the folders. You then
restart the conversation and type `/pimp`.

Manual equivalent:

```
/plugin marketplace add Romgaal/pimpmyreels
/plugin install pimpmyreels@pimpmyreels
```

Restart the conversation, then:

```
/pimp ~/Movies/my-rush.mp4
```

No rush handy? Just type `/pimp` — it builds a 15-second demo so you can see a
finished reel in about three minutes.

## 🇫🇷 Démarrage rapide

1. Installe **Claude Code** (abonnement Claude requis — c'est lui qui choisit les images).
2. Dans Claude Code : `/plugin marketplace add Romgaal/pimpmyreels`
3. Puis : `/plugin install pimpmyreels@pimpmyreels`
4. Redémarre la conversation.
5. `/pimp ~/Downloads/ma-video.mp4` — laisse-toi guider, valide la planche d'images quand elle s'affiche.

## Requirements

| | |
|---|---|
| **Claude Code** | required — plus an active Claude subscription |
| **macOS** | first-class. Homebrew installs everything automatically |
| **Linux** | best-effort: install `ffmpeg`, `whisper.cpp` (`whisper-cli`), `node`, `gh` yourself; `espeak` replaces `say` for the demo |
| **Windows** | via WSL |
| **API keys** | none. Transcription runs locally |

First run downloads a 465MB Whisper model, once.

## How it works

```
rush.mp4
   ↓  whisper.cpp, word-level          transcribe.sh
timecodes for every word
   ↓  agent picks a scene per concept  mapping-guide.md
mapping plan
   ↓  bank first, then web             source_images.py
3 candidates per beat
   ↓  one numbered contact sheet       build_board.py
board.png  →  you validate  ←  BLOCKING GATE
   ↓  data-driven composition          mapping.json
Remotion render, straight to H.264     export.sh
   ↓
reel.mp4 + cover.jpg
```

Everything for a reel lives in `~/pimpmyreels/<name>/`, so you can reopen it later,
tweak a duration in `mapping.json`, and re-export in seconds.

## The style

Deliberately minimal, because that is what performs: **hard cuts, no transitions, no
zoom, no shadows, no text of ours.** Raw images at the top of the frame, chained with
no gaps. You own the typography — add titles and subtitles with whatever you use
(Captions app, CapCut, Premiere).

Every rule and, more usefully, every **rejected** approach is documented in
`skills/pimp/references/style-rules.md`.

## The bank

Images live in three tiers, searched in this order:

1. `~/.pimpmyreels/mybank/` — your own images (drop files in, name them by concept)
2. `bank/core/` — curated, shipped in validated reels
3. `bank/community/` — contributed automatically, uncurated

When you finish a reel, the images that survived the whole pipeline are pushed as a
pull request, silently. No question is asked: an image that passed the filters, the
visual QA, your board, and the final render is validated by what you did, not by what
you'd answer. Known images get a usage counter bump instead — that counter is what
promotes an image from `community` to `core`.

Turn it off with `{"contribution": "off"}` in `~/.pimpmyreels/config.json`.

## Cost

Local transcription is free. The agent spends tokens on choosing scenes, QA-ing the
board and writing the mapping — roughly a few tens of cents of usage per reel,
depending on your plan. The single contact sheet exists precisely to keep that low.

## Licenses

- **pimpmyreels**: MIT.
- **Remotion** (the renderer): free for individuals and companies of 3 people or
  fewer; larger companies need a paid license — see [remotion.pro](https://remotion.pro).
- **Images**: sourced from the open web. Editorial/commentary use, under your own
  responsibility. Nothing is redistributed beyond this repository's bank.

## Contributing

See `CONTRIBUTING.md`. Bank contributions happen on their own; curation is manual and
driven by usage counts.
