# Platform specs — Reels / TikTok / Shorts

## Export

| Setting | Value |
|---|---|
| Resolution | 1080×1920 (9:16), native — **never upscale** |
| Frame rate | match the rush (usually 30fps) |
| Codec | H.264, CRF 15, `yuv420p` |
| Audio | AAC 256k |
| Container | .mp4 |

Instagram re-compresses on upload, so hand it the highest quality you have. Rendering
a ProRes intermediate is pointless here (a 42s reel weighs ~3GB) — `export.sh` goes
straight to H.264.

`export.sh` also writes `out/cover.jpg` from the middle of the intro collage: the
ready-made thumbnail.

## Safe zones (1080×1920)

Keep meaningful content out of these:

| Zone | Reels | TikTok |
|---|---|---|
| Top (UI header, "trial" badge) | ~200px | ~160px |
| Right rail (like/comment/share) | ~140px | ~160px |
| Bottom (caption, handle, audio) | ~340px | ~420px |

Images sit at `imageTop: 235` by default — **below** the header, clear of the right
rail and of the caption zone. On a 1080×1920 frame the usable box is therefore:

```
top    > 200      bottom < 1580      right < 940
```

**Check it, don't trust it.** Diff a frame that has a cutaway against one that doesn't,
take the bounding box, and assert the three bounds (the command is in SKILL.md step 8).
This rule was documented from version 0.1 and violated until 0.4 — because nothing
measured it.

## Burned-in subtitles

Two workflows, both supported:

- **Raw rush** — the user adds subtitles later (Captions app). Default `imageTop: 235`.
- **Rush already exported from Captions** — subtitles are burned in, usually around
  chest height. Images stay at the top; check on a frame that the collage and the
  subtitles never overlap, and raise `imageTop` slightly if they do.

Either way: **never add your own text**. The user owns the typography.
