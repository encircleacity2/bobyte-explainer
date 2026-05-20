# bobyte-explainer

A [Claude Code](https://claude.ai/code) skill that turns product information — Lark/Feishu
docs, GitHub repos, screenshots, PDFs, or a plain description — into a polished **9:16
vertical explainer video**.

Every video combines:
- **A-roll** — an AI digital-human talking-head, generated entirely with the **Seedance 2.0**
  API (BytePlus ModelArk).
- **B-roll** — animated typographic / data scenes rendered locally with **HyperFrames**.
- **Music** — AI background music from the **Volcengine** music API.

## Pipeline overview

```
  Onboarding (first run only)
        │
        ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Phase 1  │ → │ Phase 2  │ → │ Phase 3  │ → │ Phase 4  │ → │ Phase 5  │
│ Intake   │   │ Restyle  │   │Storyboard│   │Production│   │ Deliver  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
   parse        Seedream 4.5    approval        Seedance +     save to
   inputs       portrait        gate            HyperFrames    output
                (optional)                      + music        folder
```

**No paid generation runs until Phase 3's storyboard is explicitly approved.**

## Onboarding (first run)

The first time the skill runs it walks the user through a one-time English-language setup
and writes `~/.bobyte-explainer/config.json`:

1. A short explanation of what the skill does.
2. The **BytePlus ModelArk API key** (Seedance video + Seedream images).
3. The **BytePlus IAM AK / SK** (asset library + TOS object storage).
4. A **personal photo** and a **portrait video with audio** — the appearance and the
   voice/facial-motion references for the digital human.
5. The preferred **output folder** (default `~/Downloads`).

## Per-task workflow

- **Phase 1 — Intake.** Parse inputs (Lark docs via `lark-cli`, GitHub repos, screenshots,
  PDFs, descriptions) into a `product-brief.md`.
- **Phase 2 — Optional portrait restyle.** Ask whether to restyle the portrait (outfit /
  environment / lighting) with **Seedream 4.5**. If yes: generate **4 variations** from a
  user prompt, let the user review and pick / revise / skip.
- **Phase 3 — Storyboard (approval gate).** Recommend a video length, design a
  segment-by-segment storyboard with A-roll / B-roll routing and a cost estimate. Present
  and **wait for explicit approval**.
- **Phase 4 — Production.** Generate the Seedance 2.0 A-roll, render the HyperFrames
  B-roll, generate Volcengine music, assemble (slice + concat + sidechain-ducked mix).
- **Phase 5 — Deliver.** Save the MP4 to the configured output folder; optionally upload
  to Lark with confirmation.

## A-roll — Seedance 2.0

A-roll is generated entirely with Seedance 2.0. Two modes:

- **image + text** — portrait + a scripted line → native 9:16 talking-head with a
  generated voice.
- **r2v (reference-to-video)** — portrait (appearance) + a 9:16 reference video (voice
  character + facial motion) → talking-head in the user's own voice.

Real-person assets must be uploaded to the ModelArk **asset library** and referenced with
the `asset://<AssetId>` scheme — see `references/seedance-api.md`.

## Requirements

- A BytePlus ModelArk API key and BytePlus IAM AK/SK.
- Node 18+ and npm (HyperFrames renderer).
- Python 3.11+ with `requests`, `Pillow`, `volcengine` (`pip install --break-system-packages ...`).
- ffmpeg.
- `lark-cli` — only if ingesting Lark/Feishu docs or uploading to Lark.
- The `tos-upload` skill for staging files on TOS object storage.

## Reference docs

- `SKILL.md` — orchestration: onboarding + the 5-phase workflow.
- `references/seedance-api.md` — Seedance 2.0 video API: endpoints, asset library, `asset://`, r2v + image+text.
- `references/seedream-api.md` — Seedream 4.5 image API: the Phase 2 portrait restyle.
- `references/volcengine-music-api.md` — Volcengine BGM API: GenBGM/QuerySong, similarity-retry, mixing.
- `references/storyboard-format.md` — storyboard spec.
- `references/production-techniques.md` — HyperFrames composition, slicing, concat, sidechain ducking, kinetic typography.
- `references/hook-patterns.md` — hook templates.
- `references/broll-routing.md` — B-roll scene-type guide.
- `references/cost-rates.md` — Seedance / Volcengine rates.
- `references/lark-upload-guide.md` — `lark-cli` upload commands.
- `references/reference-video-analysis.md` — extracting style from a reference clip.

## Scripts

`scripts/` — helpers: `preflight.py`, `parse_inputs.py`, `estimate_cost.py`,
`compose_and_render.py`, `analyze_reference_video.py`, `upload_to_lark.py`.

## Installing as a Claude Code skill

Place this directory at `~/.claude/skills/bobyte-explainer/`. Claude Code auto-discovers it
on next launch. Trigger phrases:

> "Make an explainer video about <product>"
> "Produce a Shorts video for this GitHub repo"
> "Turn this skill pack into a launch video"

On first use the skill runs the one-time onboarding automatically.

## License

MIT
