---
name: pimp-calibrate
description: Calibrate pimpmyreels' visual style against currently trending reels. Use when the user provides reference reel URLs (Instagram/TikTok/YouTube) and wants the output style matched to what works now — /pimp-calibrate <urls>.
---

# pimp-calibrate — tune the style to what works right now

Trends move. Rather than rewriting rules from memory, look at reels that are working
today and adjust the measurable parameters to match.

## 1. Get the references

Needs `yt-dlp` (`brew install yt-dlp` if missing).

```bash
mkdir -p ~/pimpmyreels/_calibration && cd ~/pimpmyreels/_calibration
yt-dlp -o "ref-%(id)s.%(ext)s" <url1> <url2> <url3>
```

## 2. Look at them

Extract 8 evenly spread frames per reel and assemble one contact sheet per reel
(2 rows × 4), then **read the sheets**:

```bash
for f in ref-*.mp4; do
  DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  for i in $(seq 0 7); do
    T=$(python3 -c "print(round($DUR*($i+0.5)/8,2))")
    ffmpeg -y -ss $T -i "$f" -vframes 1 "${f%.mp4}_$i.png" -loglevel error
  done
done
```

## 3. Measure, don't guess

For each reel, note:

- **Image width** as a fraction of frame width (measure on a frame)
- **Top offset** in pixels — how high the image sits
- **Format mix** — landscape vs square vs full-bleed
- **Intro collage?** — present or not, grid size
- **Density** — images per minute
- **Chained or gaps** — are there stretches with no image
- **Corner radius**, and whether any decoration is used at all

## 4. Compare and propose

Current defaults live in:

- `template/src/ReelCutaways.tsx` — `0.519` (landscape width), `0.435` (square),
  `top` offset, collage height `0.107`, `borderRadius: 10`
- `template/mapping.example.json` — `imageTop`
- `skills/pimp/references/style-rules.md` — the rules and the calibration log

Show the human a diff table (parameter · current · observed in refs · proposed) and
**wait for approval**.

## 5. Apply

On approval, update the constants and append an entry to the **Calibration log**
section of `style-rules.md` (date, what changed, which references drove it).

**Never change the hard rules** — no transitions, no zoom, no shadow, no text — unless
the human explicitly asks. Those are identity, not fashion. If the references show
transitions everywhere, report it as an observation and let the human decide.
