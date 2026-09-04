# Query guide

## The one rule that changed the most: describe the PHOTOGRAPH, not the concept

A stock engine matches words in captions. Give it a concept noun and it returns pictures
whose captions contain that noun — which is literal, generic and lifeless. Give it a
description of a photograph and it returns that photograph. Measured side by side, same
engine, same minute:

| Query | What comes back |
|---|---|
| `simulation` | a Penrose triangle, two VR headsets |
| `face with glowing code projected onto skin, dark blue light, extreme close up` | a face constellated with light in darkness — the actual image |
| `overthinking` | a graphic that reads DON'T OVERTHINK |
| `man sitting on floor in dark room, single lamp, head in hands, cinematic` | a man alone under a single light, cinematic |

This is why Pinterest feels like a goldmine: its search understands a *vibe*. That
search is unreachable (see the Pinterest section below), but the images are not — the
same engines return them once the query describes the picture.

**The shape**: subject + action + light + framing. Six words minimum for any non-culture
beat; `brief.py check` refuses fewer.

- subject: *who or what is in frame* — "a man", "two hands", "a red umbrella"
- action: *what is happening* — "sitting on the floor", "holding out two pills"
- light: *the mood, in light terms* — "single lamp", "dark blue light", "warm backlight",
  "night, neon reflections"
- framing: "extreme close up", "medium shot", "from above", "cinematic"

**For a film**, the shape is different and shorter: title + actor + moment
(`Morpheus red pill blue pill hands`). Never the title alone — that returns the poster
with its title card burned in, measured three times out of three on Lucy.

## Pinterest

Pinterest's own search cannot be automated. Measured, with a real API token:

- `/v5/user_account`, `/v5/boards`, `/v5/pins` -> 401 *"Your application consumer type
  is not supported"* — the app needs Pinterest's approval.
- `/v5/search/partner/pins` -> 401 *"does not have access to this restricted feature:
  **pin_search**"* — global pin search is gated behind commercial partner approval, so
  even an approved app does not get it.
- The internal `/resource/` API returns 403 without session cookies, `/search/pins/`
  renders in JavaScript, and an automated browser is served a blank page.

What IS open: the RSS feed of a public board (`pinterest.com/<user>/<board>.rss`), which
`scripts/pinboard.py` syncs. Use it for boards a person genuinely curates — but do not
treat it as the answer to sourcing, because the automatable answer is the query rule
above.

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
