# Query guide — how to search for a scene still

The formula, always in **English** (the indexes are English, even for French films):

```
"<film title> <actor> <precise scene description> scene"
```

Precision is everything. The query describes **the moment**, not the film.

## Good vs bad

| ✗ Bad | ✓ Good |
|---|---|
| `rocky` | `rocky balboa arms raised philadelphia steps` |
| `gatsby` | `great gatsby leonardo dicaprio cheers champagne toast` |
| `matrix pills` | `matrix morpheus red pill blue pill hands scene` |
| `the office no` | `the office michael scott no god please no` |
| `friends` | `friends tv show central perk couch six cast` |
| `intouchables` | `intouchables film driss philippe laughing scene` |

## Rules

- **Never** include `poster`, `cover`, `dvd`, `fan art` — you want a frame from the
  film, not marketing material.
- Name the **actor** when you know them: it disambiguates remakes and lookalikes.
- Describe the **physical action** ("arms raised", "hands on cheeks", "pushing
  wheelchair"), not the emotion ("victory", "fear") — search engines index what is
  visible.
- The script already applies wide-aspect and large-size filters, and rejects
  letterboxed images. You don't need to add those terms.
- **Animated memes**: add `--gif` and search the meme by its name
  (`shia labeouf just do it meme`), not by description.

## Atmospheric images — a different search entirely

Roughly half a good reel is *breath* images (see `mapping-guide.md`). They are **not**
searched like film stills: there is no title, no actor. You search a **mood and a
composition**.

Formula: `"<subject> <composition/action> <atmosphere> cinematic|surreal|aesthetic"`

| ✗ Bad (searching a concept) | ✓ Good (searching an image) |
|---|---|
| `comfort zone` | `lone figure walking into burning flower field surreal cinematic` |
| `disconnection` | `boy sitting on plank above the clouds surreal dreamlike` |
| `being alone in public` | `vintage smoky parisian cafe crowd 1970s film photo` |
| `self observation` | `face seen through camera viewfinder grain cinematic` |

Rules:

- Describe **what is in the frame**, never the abstract idea.
- Add one atmosphere word: `cinematic`, `surreal`, `dreamlike`, `film photo`, `aesthetic`.
- Keep the **same tonal family** across a single reel's breath images (all warm and
  filmic, or all cold and stark — not both).
- Use the default `--format square`: these images are often 1:1 or portrait, and the
  landscape filter would throw them away.
- No `--reject` needed usually; these results are rarely watermarked stock.

## When results are bad

- **Two different queries beat ten candidates from one query.** If the first three
  are wrong, rewrite the query — don't ask for more of the same.
- A domain that keeps polluting results: teach the blocklist permanently.
  ```bash
  python3 scripts/source_images.py --reject <domain>
  ```
- Recurring watermark sources already blocked: Alamy, Shutterstock, Getty, iStock,
  Movieclips, Fandango, and friends (`data/blocklist.txt`).
- Nothing usable at all? Pick a **different scene** for the same concept. There is
  always another iconic moment — see `mapping-guide.md`.

## Montage compilations — the query is the fix, not a filter

A generic `"<film> scene film still"` query is what fan-made **grid compilations**
match best: six thumbnails in one image, sometimes captioned. On one reel, 8 of 36
candidates came back as montages — all from the beats whose query was generic.

Three pixel heuristics were tried and all three were dropped (uniform-line detection
caught 2/9, content-jump 3/11 with a false positive, pure white/black gutters 5/11).
Detecting a grid reliably is harder than it looks and a filter that silently drops
good stills is worse than none. **The board gate catches them all anyway — read it.**

What actually works is naming the *moment*, not the film:

| Returns montages | Returns single frames |
|---|---|
| `Up Pixar Carl and Ellie montage film still` | `Up Pixar Carl sitting alone in his chair` |
| `Avengers Infinity War dust scene film still` | `Peter Parker I don't feel so good Tony Stark arms` |
| `Lord of the Rings Gollum scene film still` | `Gollum close up face reflection in water Two Towers` |

The word "montage" in a query is a trap: it asks for exactly the thing to avoid.


## Frame size beats everything

Add **"close up"** or **"medium shot"** to nearly every query. A cutaway renders at 41%
of frame width; a wide shot's subject ends up a few millimetres tall on a phone and the
image communicates nothing. `Casino Royale poker table` returns a wide table with four
small figures; `Daniel Craig close up at the poker table` returns a face.

## Non-film images without the AI slop

When the word is a thing rather than a story — posture, a dictionary, a library, a pair
of polished shoes — search for the **object, photographically**, and stay away from mood
words. `cinematic aesthetic golden hour silhouette` is what summons AI renders.

| Summons AI art | Returns a photograph |
|---|---|
| `elegance and refinement aesthetic` | `close up polished black oxford dress shoes` |
| `knowledge and wisdom concept` | `open vintage dictionary page close up` |
| `confidence energy portrait` | `man adjusting his tie in a mirror close up` |
