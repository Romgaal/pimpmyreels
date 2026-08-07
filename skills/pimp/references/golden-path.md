# Golden path — one complete real run

This is an actual reel that shipped ("the radar metaphor", 42s, French facecam).
Nothing here is invented. Imitate the rhythm.

## 1. Transcription (never guessed)

```bash
bash scripts/transcribe.sh ~/pimpmyreels/radar/rush.mp4 ~/pimpmyreels/radar
```

```
   0.0-   5.1  Peut-être que ça va pas du tout, que t'es à bout de souffle, que tu te sens perdu
   5.1-   9.2  Mais la vie amène toujours des circonstances que tu n'auras pas prévues.
   9.2-  14.8  C'est un petit peu comme dans les sous-marins, on voit cet écran là...
  17.7-  21.7  Mais la plupart des choses qui auront de l'impact ne seront pas sur cet écran radar.
  21.7-  28.0  Ce sera une rencontre, un événement, une circonstance qui va arriver...
  32.1-  37.8  ...ce que tu perçois sur ton écran radar, c'est que 20% de ce que la vie va t'offrir.
  37.8-  42.1  Tout le reste n'est pas encore visible... pourtant c'est là, à portée de main.
```

Word-level lookup gave `10.8s = "on voit cet écran là"` — this exact number matters,
see step 5.

## 2. Mapping thought out before sourcing

| Time | Word | Image | Why |
|---|---|---|---|
| 2.0s | perdu / à bout de souffle | Cast Away | universal image of being lost |
| 9.2s | sous-marins | submarine control room | literal, sets up the metaphor |
| 10.8s | cet écran radar | green radar sweep | the heart of the whole reel |
| 21.7s | un événement imprévu | Walter Mitty, jumping to the helicopter | the unexpected that changes everything |
| 26.0s | la variable qui change tout | Walter Mitty, longboard in Iceland | life going off-radar |
| 32.0s | 20% de ce que la vie offre | iceberg above/below water | literal, instantly understood |
| 37.8s | à portée de main | Shawshank, arms open in the rain | the payoff |

## 3. Sourcing, 3 candidates per beat

```bash
python3 scripts/source_images.py --query "cast away tom hanks stranded alone island" \
  --concept lost --out ~/pimpmyreels/radar/candidates/01-lost/
```
…one call per beat.

## 4. Board — QA then human gate

```bash
python3 scripts/build_board.py ~/pimpmyreels/radar
```

Read the single sheet. Rejected there: the radar candidate with white side bars, the
iceberg with an "Adobe Stock" watermark, a Gladiator frame with burned-in text.
Re-sourced, sheet rebuilt.

Then shown to the human with picks. **They vetoed Titanic for "an unexpected
encounter" and asked for Walter Mitty instead** — a better call than the machine's,
and exactly why this gate exists.

## 5. mapping.json — and the resync that mattered

First version placed the radar at 14.0s because the *sentence* started there. The
human noticed it landed late. The word-level file said **10.8s**. Two numbers changed:

```json
{ "start": 276, "image": "project/img/submarine.jpg", "end": 324 },
{ "start": 324, "image": "project/img/radar.jpg", "format": "square" }
```

Lesson: sentence timing is not word timing.

## 6. Economical iteration — never re-render everything

Two changes came in after the first full export. Neither triggered a full re-render.

**Color-corrected rush** (new source file, same edit): swap the file, render once.

**Point 3 reworked** (images changed after 26s only):

```bash
# render just the changed span
npx remotion render ReelCutaways out/part3.mp4 --frames=750-1619
# keep the good part, glue
ffmpeg -y -i out/reel.mp4 -t 25 -c copy out/part12.mp4
printf "file 'part12.mp4'\nfile 'part3.mp4'\n" > out/concat.txt
ffmpeg -y -f concat -safe 0 -i out/concat.txt -c copy out/reel-final.mp4
```

The seam is invisible when the cut point has identical content on both sides.

## 7. Proof before delivery

```bash
for t in 1 5.5 11.3 27 40; do ffmpeg -y -ss $t -i out/reel.mp4 -vframes 1 chk_$t.png -loglevel error; done
```

Frames were looked at and shown: collage clears the face ✓ · radar lands at 11.3s ✓ ·
no watermarks ✓ · hard cuts ✓.

## 8. Delivered

`out/reel.mp4` (1080×1920, H.264 CRF15, 42s) + `out/cover.jpg`, ready for the user to
add their own subtitles. Then `contribute.py` ran silently.

---

**This exact sequence produced a validated reel.** Keep the rhythm:
transcribe → think → source → board → **STOP** → map → draft → proof → deliver.
