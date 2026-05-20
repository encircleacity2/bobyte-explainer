---
name: bobyte-explainer
description: Turns product information — Lark/Feishu docs, GitHub repos, screenshots, PDFs, free-form text — into a polished 9:16 vertical explainer video that combines a Seedance 2.0 AI digital-human A-roll with animated HyperFrames B-roll and AI background music. Use whenever the user wants to make a short-form vertical explainer / announcement / launch video about a product, feature, repo, or skill. Trigger phrases: "make an explainer video about X", "produce a Shorts/TikTok video for this", "turn this repo into a video", "create a product launch reel", or any request to generate a vertical product video.
---

# bobyte-explainer — Product explainer video pipeline

Turns product inputs into a polished **9:16 vertical explainer video**:
- **A-roll** — an AI digital-human talking-head, generated entirely with the **Seedance 2.0** API (BytePlus ModelArk).
- **B-roll** — animated typographic / data scenes rendered locally with **HyperFrames**.
- **Music** — AI background music from the **Volcengine** music API.

The pipeline is gated: the user must approve the storyboard before any paid generation runs.

---

## STEP 0 — Onboarding check (run this FIRST, on every invocation)

Before doing anything else, check whether the user has onboarded:

```bash
cat ~/.bobyte-explainer/config.json 2>/dev/null
```

- **File missing or empty** → run the **§ Onboarding** flow below, then continue to the per-task workflow.
- **File present** → load it and go straight to **§ Per-task workflow**.

`config.json` schema:
```json
{
  "modelark_api_key": "<ModelArk API key>",
  "iam_ak": "<BytePlus IAM access key>",
  "iam_sk": "<BytePlus IAM secret key>",
  "portrait_image": "/abs/path/to/personal-photo.jpg",
  "reference_video": "/abs/path/to/portrait-video-with-audio.mov",
  "output_folder": "/abs/path/to/save/folder",
  "onboarded_at": "YYYY-MM-DD"
}
```

---

## Onboarding (first run only — all in English)

When `config.json` is missing, walk the user through this once. Keep it friendly and concise.

**1. Explain what the skill does** — show the user:

> "This skill turns product information into a polished 9:16 vertical explainer video.
> Feed it Lark/Feishu docs (requires the Lark CLI to be installed and authorized),
> GitHub repos, screenshots, PDFs, or a plain description — and it generates, in one
> flow, a complete video: an AI digital-human **A-roll** (you, on camera) plus animated
> **B-roll** scenes, with background music. Let's get you set up — it takes a minute."

**2. Collect the ModelArk API key.**
Ask: *"Paste your BytePlus ModelArk API key (used to generate Seedance 2.0 video and Seedream images)."*

**3. Collect the BytePlus IAM AK / SK.**
Ask: *"Paste your BytePlus IAM access key (AK) and secret key (SK). These are used to operate the ModelArk asset library and TOS object storage."*

**4. Collect the personal portrait assets.**
Ask: *"Provide two files for the digital-human A-roll:
  (a) a clear front-facing personal photo, and
  (b) a short portrait video of yourself talking, WITH audio.
The photo drives the avatar's appearance; the video drives the voice and facial motion."*
Record the absolute paths.

**5. Ask for the preferred output folder.**
Ask: *"Where should finished videos be saved? (press Enter for the default `~/Downloads`)"*

**6. Write the config** to `~/.bobyte-explainer/config.json` (create the dir, `chmod 600` the file). Confirm: *"Setup complete — you're ready to make videos."*

> Per-task steps (portrait restyle, storyboard review) are NOT part of onboarding — they run on every task. See § Per-task workflow.

---

## Per-task workflow

Run these phases in order for every video. Never skip the Phase 3 approval gate.

### Phase 1 — Intake

1. List the user's inputs and categorize: `text_docs`, `github_url`, `lark_doc`, `screenshots`, `pdfs`, `chat_description`.
2. Extract content:
   - **Lark/Feishu docs** — fetch with `lark-cli docs +fetch --api-version v2 --doc <token> --as user`. (Requires lark-cli installed + authorized.)
   - **GitHub URL** — `web_fetch` the repo for README, stars, recent commits.
   - **Screenshots / PDFs** — read with vision / the pdf skill.
   - **Chat description** — treat as the user's stated intent.
3. Produce `product-brief.md` (what it is, core differentiators, audience, visual assets, stated angle). Show it and confirm before Phase 2.

### Phase 2 — Optional portrait restyle with Seedream 4.5

At the start of **every new task**, ask:

> *"Want to restyle your portrait for this video — a new outfit, environment, or lighting — with Seedream 4.5? (yes / no)"*

If **yes**:
1. Ask the user for a styling prompt (outfit, setting, mood).
2. Generate **4 variations** with Seedream 4.5 (see `references/seedream-api.md`).
3. Show all 4 and let the user **review**: pick one, regenerate with a revised prompt, or skip.
4. The chosen image becomes the portrait for this task's A-roll. If the user skips, use `config.portrait_image`.

If **no** → use `config.portrait_image` directly.

### Phase 3 — Storyboard + shot design (APPROVAL GATE)

Before any paid generation, design and present:

1. **Recommended length** — pick from the content profile and state the reasoning:

   | Content profile | Recommended length |
   |---|---|
   | Single clear message, broad audience | 20–30s |
   | 2–4 features, moderate explanation | 45–60s |
   | Many distinct workflows / skills to cover | 75–110s |

2. **Storyboard** — a segment-by-segment beat sheet. For each segment specify: time range, type (`A-roll` / `B-roll`), on-screen content, and for A-roll the spoken script.

3. **A-roll / B-roll routing:**
   - **A-roll (Seedance 2.0)** — talking-head segments. Typically a hook/intro and a closing CTA. Keep each 5–10s.
   - **B-roll (HyperFrames)** — everything else: typographic scenes, skill/feature demos, data callouts, kinetic-typography hooks, brand reveal. Rendered locally, no per-clip cost.

4. **Cost estimate** — Seedance tokens (A-roll), Volcengine music, HyperFrames $0. Show it.

5. **PRESENT EVERYTHING. STOP. WAIT FOR EXPLICIT APPROVAL** ("approved" / "yes" / "proceed"). "Looks good" is not approval — confirm. On change requests, revise and re-present.

### Phase 4 — Production

Runs only after Phase 3 approval.

1. **Workspace** — `mkdir -p` a project dir; `cp -r <skill>/assets/* .`; `npm install` (downloads HyperFrames).
2. **A-roll** — generate every talking-head segment with Seedance 2.0. See § A-roll generation.
3. **B-roll** — build the HyperFrames composition (`index.html`); `npm run render`. See `references/production-techniques.md`.
4. **Music** — generate BGM with the Volcengine API. See `references/volcengine-music-api.md`.
5. **Assemble** — slice the HyperFrames render, concat with the A-roll segments, mix the music bed (sidechain-duck the music under any A-roll voice). See `references/production-techniques.md`.

### Phase 5 — Deliver

Save the final MP4 to `config.output_folder` (default `~/Downloads`). Report duration, size, and path. Offer to upload to Lark (see `references/lark-upload-guide.md`) — never upload without explicit confirmation.

---

## A-roll generation — Seedance 2.0 only

A-roll is generated entirely with the Seedance 2.0 API. Full API details, endpoints, the asset-library workflow, and Python helpers are in **`references/seedance-api.md`** — read it before generating. Two modes:

### Mode A — image + text (native 9:16, generated voice)
Portrait image + a text prompt containing the spoken line → a talking-head that speaks the line with Seedance's own generated voice. Honors `aspect_ratio: "9:16"` natively. Best when you want exact scripted wording and don't have a reference video.

### Mode B — r2v (reference-to-video)
Portrait image (appearance) + a reference video (voice character + facial-muscle motion) → a talking-head. **The output follows the reference video's aspect ratio**, so the reference video must itself be 9:16 to get a 9:16 result. Best when you want the user's real voice and natural facial performance.

**Critical r2v constraints (learned the hard way — do not skip):**
- The reference video must be **9:16** for 9:16 output. Centre-crop a landscape source.
- Reference video duration must be **≤ 15.2 s**.
- Asset-library video assets must be **409,600–2,086,876 pixels** (e.g. 720×1280 or 1080×1920).
- Real-person photos/videos passed as raw URLs are **blocked by content moderation**. You MUST upload them to the ModelArk **asset library**, wait for `Status: Active`, then reference them with the **`asset://<AssetId>`** scheme — approved assets bypass re-moderation. This is the only working path for real-person A-roll.

When the storyboard's A-roll segments need specific spoken lines, **put the script in the text prompt** even in r2v mode.

---

## References (load on demand)

| File | Content |
|---|---|
| `references/seedance-api.md` | Seedance 2.0 video API — endpoints, asset library (SigV4), `asset://`, r2v + image+text modes |
| `references/seedream-api.md` | Seedream 4.5 image API — the Phase 2 portrait restyle (4-variation generate) |
| `references/volcengine-music-api.md` | Volcengine BGM API — GenBGM/QuerySong, similarity-retry, mixing |
| `references/storyboard-format.md` | Storyboard JSON/markdown spec |
| `references/production-techniques.md` | HyperFrames composition, slicing, concat, sidechain ducking, kinetic typography |
| `references/hook-patterns.md` | Hook templates for short-form video |
| `references/broll-routing.md` | B-roll scene-type decision guide |
| `references/cost-rates.md` | Current Seedance / Volcengine rates |
| `references/lark-upload-guide.md` | lark-cli upload commands |
| `references/reference-video-analysis.md` | Extracting style from a reference clip |

## Scripts

`scripts/` holds helpers (`preflight.py`, `parse_inputs.py`, `estimate_cost.py`, `compose_and_render.py`, etc.). They use stdin/stdout/JSON and never write outside the working directory.

---

## Security and safety

- All credentials (ModelArk key, IAM AK/SK) come from `~/.bobyte-explainer/config.json` (mode 600) — never hardcode, never print in full.
- All paid operations require the Phase 3 approval gate. If asked to skip it, push back.
- Never upload or share a finished video without explicit user confirmation.
- Respect content moderation — never attempt to bypass real-person or copyright checks.
