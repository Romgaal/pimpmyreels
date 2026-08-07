# Mapping guide — choosing the image

**The image choice is 80% of the value.** The code is trivial; the taste is the product.

## Principles

- **Instantly recognizable beats clever.** If the viewer needs a second to place it,
  it's the wrong image. Friends' couch works; an obscure arthouse frame doesn't.
- **Modern and fun beats old and worthy.** Vikings/Ragnar over Braveheart for
  "courage". The reference should feel alive, not like a history lesson.
- **Memes are first-class.** Shia LaBeouf "Just Do It", The Office's Michael Scott
  panicking. They are the fastest shared language available.
- **Literal beats abstract.** "You only perceive 20% of what life offers" → an iceberg
  above/below the waterline. The audience gets it before the sentence ends.
- **Don't illustrate everything.** Only concept-words. The speaker's face carries the
  rest, and constant images exhaust the viewer.
- **Match the audience's register.** Check who is actually watching before choosing.

## Validated concept → scene table

These shipped in real reels. Use `--concept <tag>` to pull them straight from the bank.

| Concept tag | Scene | Film |
|---|---|---|
| `value`, `victory` | arms raised at the top of the steps | Rocky |
| `knowledge`, `learning` | solving the blackboard problem | Good Will Hunting |
| `potential` | breakthrough, letters flying | Limitless |
| `friends`, `funny` | the six on the Central Perk couch | Friends |
| `friends`, `fun` | the three on the rooftop | The Hangover |
| `meeting`, `strangers` | talking to a stranger on the bench | Forrest Gump |
| `good-time`, `cheers` | raising the champagne glass | The Great Gatsby |
| `kindness`, `benevolence` | pushing the wheelchair, both laughing | Intouchables |
| `fear`, `panic` | hands on cheeks, screaming | Home Alone |
| `false`, `choice` | red pill / blue pill | The Matrix |
| `never-ready`, `waiting` | skeleton still waiting on the bench | meme |
| `just-do-it`, `action` | "JUST DO IT" green screen | Shia LaBeouf meme |
| `rejection`, `panic` | "no no no" face | The Office |
| `courage`, `warrior` | Ragnar before the battle | Vikings |
| `warrior`, `arena` | Maximus in the arena | Gladiator |
| `lost`, `burnout` | alone on the island | Cast Away |
| `unexpected`, `leap` | jumping to the helicopter | The Secret Life of Walter Mitty |
| `adventure`, `freedom` | longboarding down the Icelandic road | The Secret Life of Walter Mitty |
| `hidden`, `potential` | iceberg above and below the waterline | stock |
| `hope`, `freedom` | arms open in the rain | The Shawshank Redemption |
| `hero`, `extraordinary` | suiting up | Iron Man |
| `capacities`, `smart` | deduction close-up | Sherlock Holmes |
| `cool`, `class` | tuxedo, bar | James Bond |
| `charisma`, `authentic` | Tommy Shelby, cap and smoke | Peaky Blinders |
| `magnetic`, `speech` | rallying the floor | The Wolf of Wall Street |
| `shy`, `disconnected` | the narrator at his desk | Fight Club |
| `control-room`, `unknown` | submarine control room | stock |
| `radar`, `unknown` | green sonar sweep | stock |

## Alternates — never make the same reel twice

**This is the most important section for quality.** The table above is a *standard*,
not a shopping list. If every reel opens Rocky on "value", every reel looks the same
and the format dies. Rotate.

| Concept | Option A | Option B | Option C |
|---|---|---|---|
| value / self-worth | Rocky, steps | Gladiator, "my name is" | Iron Man, suiting up |
| knowledge | Good Will Hunting, blackboard | Limitless, breakthrough | Sherlock, deduction |
| friends / funny | Friends, couch | The Hangover, rooftop | Superbad / Brooklyn 99 reaction |
| courage | Vikings, Ragnar | 300, the stand | Top Gun Maverick, cockpit |
| fear | Home Alone, scream | The Office, Michael panicking | Get Out, the sunken place |
| meeting strangers | Forrest Gump, bench | Before Sunrise, the train | Hitch, the approach |
| good time | Gatsby, toast | Wolf of Wall Street, party | Ted Lasso, the pub |
| never ready | waiting skeleton | SpongeBob "3 hours later" | Kung Fu Panda, "there is no secret" |
| act anyway | Shia "Just Do It" | Nike-style athlete | Jump/leap moment from a recent film |
| hidden potential | iceberg | The Matrix, waking up | Interstellar, the black hole |

Extend this table rather than repeating a line. Two reels in a row on the same theme
must not share a single image.

The engine helps: it tracks what you already used (`~/.pimpmyreels/used.json`) and
pushes fresh candidates to the top of the board. Don't fight it by always picking
candidate 1.

## Stay current

Timeless classics are the safe backbone, **not the whole reel**. Aim for **1–2
references from the last 2–3 years** per reel whenever the topic allows: a current
series, a film that just landed, a meme people are actually sharing this month.

- Recent scenes signal "this was made now", classics signal "this could be from 2015".
- If you're unsure what's current, ask the user — they know their feed better than any
  index does.
- `/pimp-calibrate` looks at trending reels for *form*; **you** are responsible for
  keeping the *references* current.

## GIFs

Reaction beats — panic, "no no no", "just do it", disbelief — land harder animated
than frozen. Add `--gif` to the sourcing call and search the meme by its name. Use
them sparingly (one or two per reel); a reel of gifs is exhausting.

## Extending it

Check the bank first (`--concept`), then invent — with the same bar: universally
known, instantly readable, right register, no watermark. Anything you validate and
ship is contributed back automatically, so the alternates grow on their own: the more
the bank fills, the more variety it offers, not less.
