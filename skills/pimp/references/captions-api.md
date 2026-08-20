# Captions API — verified notes

Everything here was exercised against the live API, not read off the docs. Three of
the published details are wrong; they cost a 404 and two 400s to find.

## The calls

| What | Call |
|---|---|
| List templates | `GET /v1/videos/captions/templates` — **not** `/v1/caption-templates` (404) |
| Submit | `POST /v1/videos/captions`, multipart: `video=@file` + `caption_template_id=ctpl_…` |
| Poll | `GET /v1/videos/{id}` → `status` of `PROCESSING` / `COMPLETE` / `FAILED` |
| Download | `GET /v1/videos/{id}/content` |

Auth: `x-api-key` header. A missing key gives 400 (`missing_required_field`), not 401.

Gotchas that bit:
- The submit field is `video`, not `file`; and `caption_template_id`, not `templateId`.
- The response carries `"error": null` on success — test truthiness, not membership,
  or every successful call reads as an error.
- Input caps: 9:16, 5 minutes, **50MB**. CRF 20 takes a 37s 1080x1920 reel from 62MB
  to 23MB with no visible loss, so the cap never costs quality.
- Output is a rendered mp4 only. No SRT, no word timings, nothing to layer on top —
  which is why captions must be the **last** step, after the images.

## Only 4 of 20 templates survive French

Measured on a real French reel: 16 templates clip words at the frame edge, because
they size text for English and French words are longer. On one of them, **4 of 8
sampled frames had a cut word** ("meilleu[re]", "parce[que]", "différemm[ent]").
There is no API parameter for font size, width, or placement — the template is the
only lever.

Safe on French (measured x-extent inside 40..1040):

| Template | id | Look |
|---|---|---|
| Medusa | `ctpl_yNnJyDLSH5oIouKdjQx2` | green, heavy black outline — reads on any background |
| Altair | `ctpl_pwQ0QiBOYuuRvDuEYzmr` | green, drop shadow |
| Aries | `ctpl_pUtOSPltDzsoYJgLBYmo` | cream, smaller |
| Buzz | `ctpl_yvE0ZnYzEj6ClCD2ee1f` | lavender |

They fit because they show one word (or a short pair) at a time. Every "phrase"
template overflowed. Re-measure before trusting this list in another language.

## Measuring a template correctly

Two mistakes, both made here:

1. **Probe on the raw rush, never on the finished reel.** `detect_captions.py` finds
   text by differencing frame pairs — and a cutaway *changing* between them has the
   same signature as a word changing. On a reel with images it reported the cutaway
   band as captions: "collision at y529" where the truth, measured on the rush, was
   y1277. Same file, same tool, opposite conclusion.
2. **Frame-pair differencing only sees text that CHANGES.** Counting edge overflow
   that way gave 5%; looking at eight full-resolution frames gave 50%. To judge
   overflow, crop the text band and look, or diff against the uncaptioned render.
