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
