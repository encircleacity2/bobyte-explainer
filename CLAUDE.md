# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`bobyte-explainer` is a **Claude Code skill** (not a standalone application). It is installed under `~/.claude/skills/bobyte-explainer/` and Claude Code auto-discovers it. The skill turns product inputs (markdown, GitHub URLs, screenshots, PDFs, reference videos) into a 15–60s 9:16 vertical product video by orchestrating four external services: HeyGen (A-roll), Seedance 2.0 / BytePlus ModelArk (cinematic B-roll), HyperFrames (programmatic B-roll), and Volcengine BGM (music). Perplexity is used in Phase 2 for social-listening research.

When working in this repo, you are almost always either editing `SKILL.md` (the orchestration spec), tweaking helper scripts in `scripts/`, or updating reference docs in `references/`. There is no application server, test suite, or compile step at the repo root.

## Key files

- `SKILL.md` — the canonical orchestration spec. Phase 1–5 workflow, every approval gate, every API call pattern. The README is a summary of this file; treat `SKILL.md` as the source of truth and keep it synchronized when behavior changes.
- `assets/` — workspace template copied into each per-project directory. `assets/package.json` contains the HyperFrames npm scripts; `hyperframes-template.html` and `hyperframes.json` are the renderer inputs.
- `references/*.md` — load-on-demand deep dives (B-roll routing matrix, hook patterns, Seedance API helpers, ffmpeg techniques, etc.). `SKILL.md` deliberately does not duplicate these; link to them rather than inlining.
- `scripts/` — small, JSON-in/JSON-out Python helpers. They never write outside the working directory.

## Commands

Repo-level (run from the repo root):

```bash
python3 scripts/preflight.py        # check Node 22+, ffmpeg, lark-cli, claude CLI, MCP servers, PERPLEXITY_API_KEY
python3 scripts/parse_inputs.py <files-or-dir>   # Phase 1 input categorization
python3 scripts/perplexity_research.py "<product>" [--brief product-brief.md]   # Phase 2
python3 scripts/estimate_cost.py storyboard.json [--plan creator] [--plan-balance N]   # Phase 3
```

Per-project (run from the user's `~/projects/<slug>-video/` workspace, after copying `assets/*` into it):

```bash
npm install        # downloads HyperFrames + Chromium (~2 min, first time only)
npm run dev        # HyperFrames preview server
npm run check      # hyperframes lint + validate + inspect
npm run render     # render HyperFrames composition → dist/main.mp4 (visuals only; voice/music merged via ffmpeg afterward)
```

There are no unit tests in this repo. "Testing" a change usually means dry-running the pipeline end-to-end against a small product brief.

## Architecture: the 5-phase gate

The defining property of this skill is that **Phase 3 is a hard approval gate**. No paid generation runs until the user explicitly approves the storyboard. When editing `SKILL.md` or any phase logic, preserve this invariant:

1. **Intake** (`scripts/parse_inputs.py`) → produces `product-brief.md`, waits for user confirmation.
2. **Research** (`scripts/perplexity_research.py`, ~$0.30) → produces `research.md`, waits for user confirmation.
3. **Storyboard** (`scripts/estimate_cost.py`) → produces `storyboard.md` + cost table. **Stop and wait for explicit approval.** "Sounds good" is not approval.
4. **Production** — HeyGen A-roll, Seedance B-roll, HyperFrames composition, Volcengine BGM, ffmpeg assembly.
5. **Delivery** — `lark-cli drive +upload` → shareable URL.

If you add a new step that costs money, route it behind Phase 3 approval.

## Architecture: B-roll routing

Every B-roll segment must be routed to exactly one of three tools. The routing rule is the cornerstone of the skill's quality:

- **HyperFrames** (free, deterministic, local Chromium render) — anything with specific text, numbers, UI screenshots, or branded layout. Generated UI text from video models is garbled; always use real screenshots inside HyperFrames for product demos.
- **Seedance 2.0** (paid tokens, cinematic) — abstract / atmospheric / mood scenes. Avoid humanoid robots, mech, or anime — those trigger `OutputVideoSensitiveContentDetected`. Default to industrial / abstract / generic engineering subjects.
- **Hybrid `hstack`** — split-screen 360×1280 letterboxed Seedance + 360×1280 HyperFrames panel. **Always letterbox the cinematic side, never crop.**

A-roll is either HeyGen Avatar V (default) or Seedance 2.0 talking head (cinematic, requires a TOS-uploaded portrait asset that goes through a 30–120s approval). Don't mix A-roll tools within one video.

## Architecture: audio invariants

These come up repeatedly and break things subtly when violated:

- **Every output segment MUST have an audio track**, even silent B-roll. Use `anullsrc` to add silence. A missing audio stream causes ffmpeg's concat to drift timestamps and break lip sync on subsequent A-roll.
- **Concat with the filter, not `-c copy`.** `-c copy` leaves AAC priming-delay artifacts at boundaries — they manifest as clicks or dropped first phonemes. Always re-encode at CRF 18 during concat.
- **Seedance outputs 24fps, HeyGen outputs 25fps.** Re-encode Seedance to 25fps before concat.
- **Voice-over scripts on B-roll must complement, not narrate, on-screen text.** Word budget: ≤8 words for 2s, ≤12 words for 3s, ≤18 words for 5s. After designing all segments, read A-roll + B-roll voice-overs end-to-end as one monologue.
- **Music mix uses sidechain ducking**, not static volume. Threshold 0.03, ratio 10, attack 10ms, release 300ms. Static volume always compromises (too loud during voice or too quiet during gaps).

## External service conventions

- **TOS uploads** (for Seedance portrait assets and audio references) go through the separate `tos-upload` skill at `~/.claude/skills/tos-upload/`. Endpoint must be `tos-ap-southeast-1.bytepluses.com` (not `volces.com`).
- **HeyGen** is invoked via the HeyGen MCP server (registered with `claude mcp add`), not direct REST calls. HeyGen TTS is the exception — used directly to generate audio references for Seedance talking-head A-roll.
- **Volcengine BGM** has a 30s minimum duration floor on the v5.0 model. For shorter videos, generate ≥30s and trim with ffmpeg + 3s fade-out.
- API keys (`PERPLEXITY_API_KEY`, `BYTEPLUS_ARK_API_KEY`, `VOLC_MUSIC_AK`, `VOLC_MUSIC_SK`) come from environment variables only. `VOLC_MUSIC_SK` is base64-encoded — pass it raw to the SDK without decoding.

## Editing conventions

- When you change behavior, update `SKILL.md` first (it is the spec the agent follows at runtime). The README mirrors `SKILL.md` at a higher level — sync it when phase shape or major commands change, but don't duplicate the deep details.
- Keep `references/*.md` independently loadable; `SKILL.md` instructs the agent not to pre-read them. If a reference doc grows a new section, link to it from `SKILL.md` rather than inlining.
- Scripts must remain stdin/stdout/JSON and must not write outside the caller's working directory. Generated artifacts (`dist/`, `projects/`) are gitignored.
