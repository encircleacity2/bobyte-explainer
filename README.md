# bobyte-explainer

A research-driven, agentic [Claude Code](https://claude.ai/code) skill that turns any product input — markdown docs, GitHub URLs, screenshots, PDFs, reference videos — into a polished 15–60 second 9:16 vertical product video, optimized for TikTok / YouTube Shorts / Instagram Reels.

The skill orchestrates four AI services to produce a cohesive narrative: **HeyGen** for talking-head A-roll, **Seedance 2.0** (BytePlus ModelArk) for cinematic B-roll, **HyperFrames** for programmatic data/text animations, and **Volcengine BGM** for AI-generated copyright-free background music. Research is grounded by **Perplexity** social-listening queries so the hook resonates with the actual audience.

## Pipeline overview

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Phase 1  │ →  │ Phase 2  │ →  │ Phase 3  │ →  │ Phase 4  │ →  │ Phase 5  │
│ Intake   │    │ Research │    │Storyboard│    │Production│    │ Delivery │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
   parse           Perplexity        approval        generate        Lark
   inputs          social             gate           segments         upload
                   listening
```

Each phase has an explicit user-approval or confirmation gate. **No paid generation runs until Phase 3's storyboard is explicitly approved.**

## Phase 1 — Intake and parsing

Build a clean, structured understanding of the product before any research or design.

1. List every input the user provided (markdown, GitHub URL, screenshots, PDFs, reference videos, chat description).
2. Extract content per type — read text directly, fetch GitHub READMEs, vision-describe screenshots, transcribe PDFs, ffprobe reference videos for pacing analysis.
3. Produce `product-brief.md` with sections: what it is, core differentiators, target audience signals, visual assets available, reference style notes, user's stated angle.
4. Show the brief to the user inline. Wait for confirmation/correction before Phase 2.

## Phase 2 — Social listening research

Discover what the audience actually cares about so the hook resonates instead of feeling generic.

1. Verify Perplexity API access (`PERPLEXITY_API_KEY`).
2. Run 3–5 parallel queries via `scripts/perplexity_research.py`:
   - **Pain points** — what's frustrating about this product category
   - **Viral angles** — what posts about similar products went viral recently
   - **Competitive landscape** — competitors and their user sentiment
   - **Latest discussions** — last 30 days of mentions
   - **Audience demographics** — who actually uses this product
3. Extract from `research.md`: top 3 hooks, 1–2 visual metaphors that work, 1–2 anti-patterns from competitor video comments.
4. Show 3–5 bullet research summary to user. Wait for confirmation before Phase 3.

Cost: ~$0.30 (Perplexity sonar-pro at ~$0.06/query).

## Phase 3 — Storyboard design with media routing

Produce a complete, segment-by-segment plan that the user explicitly approves before any paid generation.

1. **Pick total length** (15–60s) using the complexity guide:
   - 15s — single clear differentiator, broad audience
   - 20–30s — 2–3 features, moderate explanation
   - 30–45s — technical product, multiple workflows
   - 45–60s — complex product needing demo + context + CTA
2. **Design the hook** (first 3 seconds) using one of: pain question, bold claim, visual surprise, curiosity gap. Ground it in Phase 2 research, not generic.
3. **Choose A-roll tool** — HeyGen Avatar V (default; cloned voice, fast) or Seedance 2.0 talking head (cinematic; needs portrait asset). Lock in `avatar_look_id` + `voice_id` (HeyGen) or `asset_uri` + `heygen_voice_id` (Seedance) before designing segments.
4. **Route every B-roll segment**:
   - Specific UI / numbers / text → **HyperFrames** (free, pixel-perfect, deterministic)
   - Cinematic / atmospheric / abstract → **Seedance 2.0** (BytePlus ModelArk)
   - Hybrid layouts (data + cinema) → split-screen `hstack(Seedance, HyperFrames)`
5. **Voice-over rules for B-roll** — every segment must have a `voiceover_script` (or explicit `voiceover_rationale: null` for deliberate silence). Word count fits duration. Voice complements visual, doesn't read it aloud. Validate by reading the full audio track end-to-end as one coherent monologue.
6. **Cost estimate** via `scripts/estimate_cost.py` — HeyGen credits + Seedance tokens + Perplexity already spent.
7. **Present and stop**. Show timeline table + hook + cost. Wait for explicit approval. "Sounds good" is not approval.

## Phase 4 — Production execution

Only runs after Phase 3 approval. Each step matches a numbered sub-section in `SKILL.md`.

1. **Workspace setup** — create project directory, copy HyperFrames template, `npm install`.
2. **A-roll tool setup**:
   - HeyGen path — list avatar groups + looks + voices, present to user, lock in selections.
   - Seedance path — verify portrait asset exists or upload via TOS → CreateAssetGroup → CreateAsset → poll for approval (30–120s).
3. **Generate A-roll segments** in parallel — HeyGen `create_video_from_avatar` or Seedance `CreateContentsGenerationsTasks` with HeyGen TTS audio reference.
4. **Generate cinematic B-roll** with Seedance 2.0 (parallel where possible).
5. **HeyGen TTS for B-roll voice-overs** + ffmpeg merge with each silent B-roll.
6. **HyperFrames composition** — programmatic segments rendered locally via Chromium.
7. **HyperFrames render to silent MP4** + voice-over merge.
8. **Volcengine BGM music generation** — `GenBGM` with a prompt tuned to video tone, poll `QuerySong`, download WAV, trim to video length with 3s fade-out.
9. **Final assembly** — concat filter (re-encodes for clean AAC boundaries) + sidechain-ducked music mix.

### Production sub-techniques

See `references/production-techniques.md` for the full pattern library:

- **B-roll annotations** — PIL → PNG → ffmpeg overlay (most ffmpeg builds lack `drawtext`)
- **Split-screen layouts** — `hstack(letterboxed Seedance 360×1280, HyperFrames panel 360×1280)`
- **Wordmark / brand reveals** — PNG sequence + ffmpeg `-itsoffset` overlay, synced to audio cues
- **Seedance frame-rate alignment** — always re-encode 24fps → 25fps before concat
- **TTS-first segment timing** — submit TTS first, size segments to actual duration
- **Seedance content-policy avoidance** — prefer industrial / abstract subjects, never humanoid / anime
- **Concat strategy** — concat filter at CRF 18, never `-c copy` (boundary clicks)
- **Sidechain-ducked music mix** — voice always dominant, music breathes back during gaps

## Phase 5 — Lark upload and delivery

1. Verify `lark-cli` is set up and authenticated.
2. Upload `dist/main.mp4` to user's Lark Drive folder via `lark-cli drive +upload`.
3. Parse `file_token` from JSON output, construct shareable URL.
4. Optionally send the URL to a Lark chat (with explicit user confirmation).
5. Return final summary: video duration, file size, Lark URL, remaining HeyGen credits.

## Setup

### Required env vars

```bash
# HeyGen — A-roll avatar generation + B-roll TTS
# Authenticated via the heygen MCP server's OAuth flow on first use

# Perplexity — social listening research
export PERPLEXITY_API_KEY="pplx-..."

# BytePlus ModelArk — Seedance 2.0 video generation
export BYTEPLUS_ARK_API_KEY="..."

# Volcengine BGM — AI music generation
export VOLC_MUSIC_AK="..."
export VOLC_MUSIC_SK="..."  # base64-encoded; pass raw to the SDK without decoding

# TOS — required for Seedance portrait asset upload (talking-head A-roll only).
# Configured via the tos-upload skill at ~/.claude/skills/tos-upload/tos_credentials.json
# (https://github.com/encircleacity2/tos-upload)
```

### Required tooling

- Node 18+ and npm (HyperFrames renderer)
- Python 3.11+ with `requests`, `Pillow`, `volcengine`
- ffmpeg (Homebrew build is fine; the skill uses PIL→PNG overlay since `drawtext` may be unavailable)
- `lark-cli` (Lark/Feishu CLI for Phase 5 upload)

## Reference docs

- `SKILL.md` — orchestration and the 5-phase workflow
- `references/hook-patterns.md` — viral hook templates from TikTok/Shorts research
- `references/broll-routing.md` — Seedance vs HyperFrames vs Hybrid decision matrix
- `references/storyboard-format.md` — exact JSON/markdown spec for `storyboard.md`
- `references/cost-rates.md` — current credit rates and pricing
- `references/seedance-api.md` — Seedance 2.0 API: portrait upload, generation, polling
- `references/volcengine-music-api.md` — GenBGM/QuerySong, prompt patterns, sidechain mix
- `references/production-techniques.md` — Phase 4 patterns and gotchas
- `references/perplexity-usage.md` — query patterns, model selection, cost tips
- `references/lark-upload-guide.md` — `lark-cli` commands and folder management
- `references/reference-video-analysis.md` — extracting style from a user-provided reference clip

## Scripts

- `scripts/preflight.py` — environment check (node, ffmpeg, lark-cli, env vars)
- `scripts/parse_inputs.py` — categorize and extract from user input files
- `scripts/analyze_reference_video.py` — ffprobe + key frame analysis
- `scripts/perplexity_research.py` — parallel social-listening queries
- `scripts/estimate_cost.py` — storyboard → credit + USD cost breakdown
- `scripts/compose_and_render.py` — orchestrates HeyGen + HyperFrames + ffmpeg
- `scripts/upload_to_lark.py` — wraps `lark-cli` for the upload step

## Installing as a Claude Code skill

Place this directory under `~/.claude/skills/bobyte-explainer/` and Claude Code auto-discovers it on next launch. Trigger phrases:

> "Make a 15-second TikTok video about <product>"
> "Produce a Shorts video for this GitHub repo"
> "Create an announcement video for the launch"
> "Turn this README into a product reel"

## License

MIT
