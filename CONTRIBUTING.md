# Contributing

## The bank (automatic)

You don't have to do anything. When you finish a reel, `contribute.py` opens a pull
request with the images that survived the whole pipeline, and bumps usage counters on
images that were already known.

The reasoning: an image that passed the automatic filters, the agent's visual QA, your
validation board **and** made it into the final render is validated by what you did.
Asking "was this good?" would only collect polite yeses.

Disable with `{"contribution": "off"}` in `~/.pimpmyreels/config.json`.

## Tiers

| Tier | Who writes | When it's used |
|---|---|---|
| `~/.pimpmyreels/mybank/` | you, locally | first — never leaves your machine |
| `bank/core/` | maintainers only | second — curated, shipped in validated reels |
| `bank/community/` | anyone, via automatic PRs | third — uncurated |

The core tier is protected on purpose: even if the community tier fills with mediocre
images, quality never degrades. Community images are still visually QA'd by the agent
and validated by the human before they can land in a reel.

## Curation (maintainers)

Promotion is driven by data, not opinion. Open `bank/community/manifest.json` and sort
by `use_count`:

- **Used by several people** → move the file to `bank/core/`, move its manifest entry,
  fill in `film` and `concepts` properly, set `universal` honestly.
- **Zero use after a couple of months** → delete it.

Ten minutes a week. You're reading facts of usage, not promises.

## Manual additions

PRs adding images by hand are welcome, with:

- The image itself in `bank/community/`, named `<sha256[:16]>.jpg`
- Its manifest entry (`file`, `hash`, `film`, `concepts`, `universal`, `aspect`,
  `use_count: 0`, `added`)
- **A screenshot of the board** it appeared in, or of the image in context
- No watermark, no black bars, no burned-in text, landscape unless it's a close-up

## Rules and method

Changes to `skills/pimp/references/style-rules.md` need a reason grounded in a real
reel — ideally an anti-example ("this was tried, here's why it failed"). That file is
the actual product; keep its signal high.

Style constants (sizes, offsets) are updated through `/pimp-calibrate` against
trending references, and logged in the Calibration log.
