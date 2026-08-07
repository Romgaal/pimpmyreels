# Agent instructions — installing pimpmyreels

**If a user pointed you at this repository and asked you to install it, do exactly this.**

## 1. Register and install the plugin

```
/plugin marketplace add Romgaal/pimpmyreels
/plugin install pimpmyreels@pimpmyreels
```

Then tell the user: **"Restart this conversation, then type `/pimp`."** The plugin's
skills are only loaded at conversation start — this step is not optional.

## 2. If slash commands are unavailable in this environment

Install everything manually, then hand over:

```bash
git clone https://github.com/Romgaal/pimpmyreels.git ~/.pimpmyreels/repo
bash ~/.pimpmyreels/repo/skills/pimp/scripts/setup.sh
```

`setup.sh` is idempotent and installs the whole toolchain: ffmpeg, whisper.cpp plus
its model (465MB, once), Node, the Remotion template and its dependencies, Pillow,
and the working folders. Then follow `~/.pimpmyreels/repo/skills/pimp/SKILL.md`
manually for the pipeline.


## What setup reuses vs installs

`setup.sh` never reinstalls or upgrades what the machine already has. It prints, line
by line, what it reuses and what it fetches. Typical run on a developer machine:
everything reused except the template's dependencies.

**One deliberate exception**: the Remotion template gets its own isolated dependency
copy, even if the user already has Remotion projects. Theirs may force a different
codec (a ProRes config would turn a 42s reel into a 3GB file), register other
compositions, or be work in progress. pimpmyreels never touches an existing project.
Cost: about 15 seconds and 200MB, once.

## 3. Nothing else is required from the user

No API keys. No accounts. Transcription runs locally. The first `/pimp` runs
`doctor.sh`, and `setup.sh` if anything is missing — so the user genuinely only has
to install the plugin and type `/pimp`.

**Do not** ask the user to install ffmpeg, Remotion, Whisper or anything else by
hand: `setup.sh` does it. Just run it.

## What this plugin does

Turns a talking-head video into a reel with iconic movie stills and memes synced to
the exact words. See `README.md` for the product, and `skills/pimp/SKILL.md` for the
method (that file is the source of truth once installed).
