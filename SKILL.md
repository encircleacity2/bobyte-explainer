---
name: bobyte-explainer
description: Research-driven, agentic pipeline that produces a polished 15–30 second TikTok-style 9:16 vertical product video from any product input (markdown docs, GitHub URLs, screenshots, PDFs, reference videos). Use this skill whenever the user wants to make a short-form vertical video about a product, feature, launch, GitHub repo, or open-source project — even if they don't say "skill". Trigger phrases include "make a TikTok video about X", "produce a Shorts video for this product", "create an announcement video", "build a product launch reel", "turn this repo into a video", "do a quick-cut intro for this", or any mention of combining HeyGen + HyperFrames for a product story. The skill uses Perplexity for social-listening research, designs a custom storyboard with hook strategy and B-roll routing (Video Agent vs HyperFrames), presents it for user approval with cost estimate, then produces and uploads the final MP4 to Lark.
---

# Product video pipeline (agentic)

A 5-phase research-and-design workflow that turns product information into a polished 9:16 vertical video, optimized for TikTok / YouTube Shorts / Instagram Reels.

**This is NOT a fixed-template skill.** Each video is custom-designed based on:
- The product's actual differentiators (read from user inputs)
- What the audience already cares about (researched via Perplexity)
- Which B-roll segments need real cinematic generation (Video Agent) vs programmatic data animation (HyperFrames)

The user MUST approve the storyboard plan before any paid generation runs.

---

## How to invoke this skill

The user will provide some combination of:
- Markdown documents about the product
- GitHub repo URL
- Screenshots (PNG/JPG)
- PDFs
- Reference videos (style examples)
- Free-form description in chat

A typical first message looks like:

> "Make a 15-second TikTok video about DeerFlow. Here's the GitHub link, the README, and 3 screenshots. Also here's a reference video in the style I want."

Your job is to walk through the 5 phases in order. **Never skip a phase.** Do NOT generate any HeyGen videos until Phase 3's storyboard has been explicitly approved by the user.

---

## Phase 1 — Intake and parsing

**Goal:** Build a clean, structured understanding of the product before doing any research or design.

### Steps

1. List all inputs the user provided. Categorize by type: `text_docs`, `github_url`, `screenshots`, `pdfs`, `reference_videos`, `chat_description`.

2. For each input type, extract content:
   - **Markdown / text docs:** read directly with `view` or `Read` tool
   - **GitHub URL:** use `web_fetch` on the repo page to get the README, star count, license, recent commits
   - **Screenshots:** use the vision capability — describe what's shown, identify UI elements, infer the product workflow
   - **PDFs:** use `view` or `pdf-reading` skill if available; extract text + key visuals
   - **Reference videos:** run `scripts/analyze_reference_video.py <video_path>` — extracts duration, frame rate, key frames, and pacing analysis
   - **Chat description:** treat as user's stated intent; preserve verbatim

3. Produce `product-brief.md` in the working directory with these sections:
   ```
   # Product Brief — <product name>
   
   ## What it is (1-2 sentences)
   ## Core differentiators (3-5 bullet points)
   ## Target audience signals (from inputs)
   ## Visual assets available (list of screenshots, demos)
   ## Reference style notes (if user provided reference video)
   ## User's stated angle (if any)
   ```

4. Show this brief to the user inline and ask: "Did I capture the product correctly? Anything to add before I research the angle?"

Wait for confirmation or correction before Phase 2.

### Skipping inputs

If the user provides ONLY chat description (no docs/URLs), still produce the brief — just note explicitly which sections are inferred vs stated. Do not invent facts.

---

## Phase 2 — Social listening research

**Goal:** Discover what the audience already cares about, so the video's hook and angle resonate instead of feeling generic.

### Steps

1. Verify Perplexity API access:
   ```bash
   echo "$PERPLEXITY_API_KEY" | head -c 10
   ```
   If not set, ask the user to `export PERPLEXITY_API_KEY='pplx-...'` before continuing.

2. Run `scripts/perplexity_research.py` with the product name and 3-5 research queries derived from the brief. The script handles parallel queries and returns a structured `research.md`.

   The research queries should target:
   - **Pain points:** "What are people frustrated about with [product category]?"
   - **Viral angles:** "What posts about [product] or similar have gone viral on TikTok / Twitter / HN recently?"
   - **Competitive landscape:** "Who are [product]'s main competitors and what do users say about them?"
   - **Latest discussions:** "What did people say about [product] in the last 30 days?"
   - **Audience demographics:** "Who is [product]'s typical user? Engineer? Marketer? PM?"

3. Read `research.md` carefully. Extract:
   - Top 3 hooks the audience would respond to (e.g., "Building agents from scratch is brutal" because that's the #1 pain in r/LocalLLaMA threads)
   - 1-2 visual metaphors that work well for this audience
   - 1-2 "do NOT do this" anti-patterns from comments on competitor videos

4. Show the research summary to the user (3-5 bullets, not the full doc) and confirm: "These are the angles I found. Anything you'd skip or add?"

Wait for confirmation before Phase 3.

### Cost note for Perplexity

`sonar-pro` is the recommended model for this research — costs roughly $0.06 per query. 5 queries ≈ $0.30 total. This is charged to the Perplexity account, separate from HeyGen credits.

See `references/perplexity-usage.md` for query patterns and cost optimization.

---

## Phase 3 — Storyboard design with media routing

**Goal:** Produce a complete, segment-by-segment plan that the user must explicitly approve before any paid generation.

### Steps

1. Decide overall video length based on:
   - User's stated preference (if given)
   - Reference video duration (if provided)
   - Number of distinct beats needed to deliver the message
   - Complexity of the product: how many differentiators, how technical the audience

   Range: 15–60 seconds. Use this judgement guide:

   | Content profile | Recommended length |
   |---|---|
   | Single clear differentiator, broad audience | 15s |
   | 2-3 features, moderate explanation needed | 20–30s |
   | Technical product, multiple distinct workflows | 30–45s |
   | Complex product needing demo + context + CTA | 45–60s |

   Make a specific recommendation (e.g. "I recommend 25s because...") and explain the reasoning. The user can override.

2. Design the **hook (first 3 seconds)** using one of these patterns from `references/hook-patterns.md`:
   - **Pain question** ("Building AI agents from scratch is brutal.")
   - **Bold claim** ("This is the only AI agent harness you'll ever need.")
   - **Visual surprise** (jarring data viz, before/after split)
   - **Curiosity gap** ("Why is this open-source project at #1 trending on GitHub?")
   
   The hook should be derived from Phase 2 research, not generic.

3. Design **A-roll segments** (talking-head, on-camera narration):

   Two tool options — pick one per project (don't mix within the same video):

   | Tool | When to use |
   |---|---|
   | **HeyGen Avatar V** | Default. Cloned voice, reliable lip sync, fast turnaround. Best when audio accuracy matters (technical terms, exact wording). |
   | **Seedance 2.0 (talking head)** | When cinematic visual realism is priority. Requires a pre-approved portrait asset (see Phase 4 Step 2B for setup). Portrait review takes 30-120s first time; reused freely after. Voice is driven by a HeyGen TTS audio reference — so voice accuracy is preserved even in Seedance. |

   **If HeyGen Avatar V is chosen:** before writing storyboard segments, call `list_avatar_groups` (type=private) then `list_avatar_looks` for each group via the HeyGen MCP tool. Present the look IDs and thumbnail names to the user and ask them to pick one. Do the same for voices via `list_voices` (type=private). Lock in `avatar_look_id` and `voice_id` before designing segments — storyboard entries should reference the chosen IDs.

   Layout rules (apply to both tools):
   - Each A-roll segment is 2–3 seconds, max 12-15 words
   - Total A-roll across the video: 6-10 seconds (avoid more — Shorts viewers tune out talking heads)
   - 3 segments for 15s video, 4-5 for 30s
   - Each segment delivers ONE clear point

   In the storyboard, record the chosen A-roll tool as `"tool": "heygen-avatar"` or `"tool": "seedance-talking-head"` in every A-roll segment.

4. Design **B-roll segments** by routing each one to the right tool — **Seedance 2.0** or **HyperFrames** only:

   | B-roll content | Tool | Why |
   |--|--|--|
   | Abstract conceptual scene (AI agents, data flow, atmosphere) | **Seedance 2.0** | Cinematic generative quality; no specific text/numbers needed |
   | Mood-setting establishing shot | **Seedance 2.0** | Atmosphere over precision |
   | User reaction / human moment | **Seedance 2.0** | Generative realism |
   | Product demo / UI walkthrough | **HyperFrames + screenshots** | Real screenshots look real; generated UI text is garbled |
   | Number / counter / trend animation | **HyperFrames** | Precise typography, animatable counters |
   | Feature comparison / before-after | **HyperFrames** | Layout control |
   | Quote / testimonial / stat callout | **HyperFrames** | Typography control |
   | Quick-cut feature montage | **HyperFrames + screenshots** | Composable from existing assets, free |
   | CTA / link / "try it now" | **HyperFrames** | Must be readable and branded |

   For each B-roll segment, write down:
   - `tool`: `seedance` | `hyperframes` | `hybrid`
   - `duration`: in seconds
   - `intent`: what the viewer should feel/understand
   - `prompt_or_spec`: the cinematic prompt (Seedance) or animation spec (HyperFrames)
   - `voiceover_script`: **required** — a short narration line spoken over this clip
   - `voiceover_style`: tone/delivery guidance for TTS (e.g. "confident, slow", "punchy, fast")

   **Voice-over rules for B-roll:**
   - Every B-roll segment MUST have a voice-over script unless silence is a deliberate creative choice. If intentionally silent, set `voiceover_script: null` and add `voiceover_rationale` explaining why.
   - Word count must fit the duration: ≤ 8 words for 2s, ≤ 12 words for 3s, ≤ 18 words for 5s.
   - The voice-over must **complement** the visual — it adds context or emotion, it does NOT read out text that's already on screen.
   - After designing all segments, read the full audio track aloud (A-roll scripts + B-roll voice-overs in order) and confirm it sounds like one coherent monologue, not disconnected fragments.

5. Estimate cost using `scripts/estimate_cost.py` with the storyboard JSON. Output should look like:

   ```
   Cost breakdown:
   
   HeyGen Premium Credits:
     A-roll seg 1 (2.5s): 17 credits
     A-roll seg 2 (2.5s): 17 credits
     A-roll seg 3 (2.0s): 13 credits
     ────────────────────────────────────────
     Subtotal: 47 credits (Creator plan: 200/mo, after this: 153 left)
   
   Seedance 2.0 B-roll (BytePlus token pricing):
     B-roll cinematic scene 1 (5s, lite model): ~X tokens
     B-roll cinematic scene 2 (5s, lite model): ~X tokens
   
   HyperFrames programmatic scenes: $0 (local render)
   
   Perplexity API (already spent in Phase 2): ~$0.30
   
   Lark upload: free
   
   ─────────────────────
   TOTAL: 47 HeyGen credits + Seedance tokens + $0.30 already spent
   ```

6. Write the full storyboard to `storyboard.md` in the working directory. Format follows `references/storyboard-format.md`.

7. **PRESENT THE STORYBOARD AND COST ESTIMATE TO THE USER. STOP HERE. WAIT FOR EXPLICIT APPROVAL.**

   Show the user:
   - The hook line
   - A timeline table with all segments (time, type, content, tool)
   - The cost breakdown
   - "Do you want me to: (a) proceed with production, (b) revise specific segments, or (c) start over with a different angle?"

   **Do NOT proceed to Phase 4 unless the user explicitly says yes / approve / 继续 / 可以 / proceed.** "Sounds good" or "interesting" is NOT approval — ask again to confirm.

### Iteration

If the user says "change segment 3" or "make the hook more aggressive", revise `storyboard.md` and re-run cost estimate. Show the diff. Get approval again.

---

## Phase 4 — Production execution

**Goal:** Generate all video segments and compose them into the final MP4.

This phase only runs AFTER Phase 3 approval.

### Steps

1. Set up project workspace:
   ```bash
   mkdir -p ~/projects/<product-slug>-video
   cd ~/projects/<product-slug>-video
   cp -r <SKILL_PATH>/assets/* .
   npm install   # downloads HyperFrames + Chromium ~2 min
   ```

2. **A-roll tool setup** — based on which A-roll tool was chosen in the storyboard:

   **Option A — HeyGen Avatar V** (default):
   ```
   1. list_avatar_groups (type=private)
      → for each group: list_avatar_looks (group_id=<id>)
      → present numbered list of look IDs + names to user
      → user picks → save as avatar_look_id

   2. list_voices (type=private)
      → present numbered list of voice names/IDs to user
      → user picks → save as voice_id
   ```
   Present both lists clearly before proceeding. If the user already specified both in Phase 3 (locked into storyboard), skip the prompt and confirm the selections.

   **Option B — Seedance 2.0 talking head**:

   **2B-1. Verify env vars:**
   - `BYTEPLUS_ARK_API_KEY` must be set. If missing, ask the user to export it.
   - TOS credentials are read from `/Users/bytedance/.claude/skills/tos-upload/tos_credentials.json` — no env vars needed if that file is filled.

   **2B-2. List existing portrait assets:**
   - Call `GetAsset` for any known `AssetId`s the user has, OR ask: "Do you have a previously approved portrait AssetId for Seedance?"
   - If the user provides an existing approved `AssetId`, use `ark://asset/<AssetId>` directly and skip to step 2B-5.
   - If none: proceed to 2B-3.

   **2B-3. Portrait image upload via TOS (NOT Files API, NOT lark-cli):**
   - Ask the user: "Please provide the path to a portrait photo (JPEG, PNG, WEBP). Requirements: front-facing, single person, clear face, ≥300×300px."
   - If the file is WEBP or HEIC, convert to JPEG first:
     ```bash
     sips -s format jpeg <input_path> --out /tmp/portrait.jpg
     ```
   - Upload to TOS using the tos-upload skill:
     ```bash
     python3 /Users/bytedance/.claude/skills/tos-upload/scripts/upload.py \
         /tmp/portrait.jpg \
         --key "seedance-portraits/<project-slug>/portrait.jpg" \
         --expires 86400
     ```
   - Capture the `url` field from the JSON output → save as `TOS_PORTRAIT_URL`.

   **2B-4. Create ModelArk portrait asset:**
   ```python
   # Using Python helpers from references/seedance-api.md:
   group_id = create_asset_group("portrait-group-<project-slug>")
   asset_id = create_asset(group_id, "portrait-<project-slug>", TOS_PORTRAIT_URL, "image/jpeg")
   asset_uri = poll_asset_approval(asset_id)   # polls every 10s until "approved"
   # asset_uri = "ark://asset/<asset_id>"
   ```
   Portrait review typically takes 30-120 seconds. Poll and report progress to user.
   If `Status == "rejected"`: ask user for a better photo and restart from 2B-3.

   **2B-5. Also list HeyGen voices for audio reference:**
   - Call `list_voices` (type=private) via HeyGen MCP tool.
   - Present numbered list to user and ask them to pick one → save as `heygen_voice_id`.
   - This voice will be used to generate the audio reference in step 3.

   Save `asset_uri` and `heygen_voice_id` for all A-roll generation in this project.
   Full API details and Python helpers in `references/seedance-api.md`.

3. **Generate A-roll segments** (parallel where possible):

   **HeyGen path:**
   ```
   For each A-roll segment in storyboard:
     submit create_video_from_avatar with:
       avatar_id: <chosen>
       voice_id: <chosen>
       script: <segment script>
       dimension: 720x1280
       background: solid color from storyboard or default
     poll get_video every 15s until completed
     download to ./assets/aroll-N.mp4
   ```

   **Seedance talking-head path:**

   For each A-roll segment, first generate the voice audio via HeyGen TTS, then submit to Seedance with that audio as reference:

   ```
   Step 3a — Generate voice audio for this segment:
     Call HeyGen TTS API (POST /v2/text_to_speech):
       voice_id: <heygen_voice_id from step 2B-5>
       text: <segment script>
       speed: 1.0
     Download audio to /tmp/aroll-N-voice.mp3

   Step 3b — Upload voice audio to TOS:
     python3 /Users/bytedance/.claude/skills/tos-upload/scripts/upload.py \
         /tmp/aroll-N-voice.mp3 \
         --key "seedance-audio/<project-slug>/aroll-N.mp3" \
         --expires 86400
     Capture url → TOS_AUDIO_URL

   Step 3c — Submit Seedance talking-head task:
     CreateContentsGenerationsTasks:
       model: "dreamina-seedance-2-0-260128"
       content: [
         {"type": "text", "text": "Person speaking directly to camera, <tone from storyboard>: '<script>'"},
         {"type": "asset_uri", "asset_uri": "<asset_uri from step 2B>"},
         {"type": "audio_url", "audio_url": "<TOS_AUDIO_URL>"}
       ]
       parameters: {aspect_ratio: "9:16", duration: <segment duration>, resolution: "720p"}
     poll task status every 15s until "succeeded"
     download output.url to ./assets/aroll-N.mp4
   ```
   The audio reference drives the lip sync and voice character of the generated avatar — the output video will have the HeyGen cloned voice baked in.

4. **Generate cinematic B-roll segments** (Seedance 2.0 only, parallel where possible):

   ```
   For each seedance B-roll segment in storyboard:
     submit CreateContentsGenerationsTasks with:
       model: "dreamina-seedance-2-0-260128"
       content: [{"type": "text", "text": "<cinematic prompt from storyboard>"}]
       parameters: {aspect_ratio: "9:16", duration: <segment duration>, resolution: "720p"}
     poll task status every 15s until "succeeded"
     download output.url to ./assets/broll-<scene-name>-silent.mp4
   ```
   Full API details and Python helpers in `references/seedance-api.md`.

5. Generate voice-over audio for each B-roll segment that has a `voiceover_script`:
   ```
   For each B-roll segment where voiceover_script is not null:
     Call HeyGen TTS API (POST /v2/text_to_speech):
       voice_id: <same voice_id used for A-roll>
       text: <voiceover_script>
       speed: 1.0  (adjust if needed to fit segment duration)
     Download audio to ./assets/vo-<segment-id>.mp3
   ```

   Then merge voice-over audio into each B-roll video:
   ```bash
   # For each B-roll segment with voice-over:
   ffmpeg -y \
     -i ./assets/broll-<name>-silent.mp4 \
     -i ./assets/vo-<id>.mp3 \
     -c:v copy -c:a aac -b:a 192k \
     -shortest \
     ./assets/broll-<name>.mp4

   # For B-roll segments with voiceover_script: null, add silent audio track:
   ffmpeg -y \
     -i ./assets/broll-<name>-silent.mp4 \
     -f lavfi -i anullsrc=r=48000:cl=stereo \
     -c:v copy -c:a aac -b:a 192k \
     -shortest \
     ./assets/broll-<name>.mp4
   ```

   **Important:** Every B-roll segment output file MUST have an audio track (either voice-over or silence). A video with no audio stream causes ffmpeg concat to misalign audio from subsequent A-roll segments, breaking lip sync.

6. Build HyperFrames composition:
   - Start from `assets/index.html` template
   - For each programmatic B-roll segment: add a `<div class="clip" data-start data-duration data-track-index>` block
   - Wire GSAP timeline animations matching the segment's `prompt_or_spec`
   - HyperFrames renders visuals only (no audio) — the voice-over MP3 is merged in the ffmpeg step above before concatenation

7. Render HyperFrames B-roll to silent MP4, then apply step 5 voice-over merge:
   ```bash
   npm run render  # → dist/main.mp4 (visuals only for HF segments)
   # Then extract each HF segment and merge voice-over (see step 5 pattern)
   ```

### Production sub-techniques (apply when storyboard requires)

For the techniques below, see `references/production-techniques.md` for full code patterns.

- **B-roll annotations** — when the segment needs callout text (e.g., pointing out flaws in a failure-demo Seedance clip), pre-render cumulative RGBA PNGs with PIL and overlay via ffmpeg (default ffmpeg builds lack `drawtext`). Skip border boxes; use a colored bullet + text with a 3px black stroke for legibility.
- **Split-screen B-roll (cinematic + data)** — when a narrative beat needs both atmosphere and structured data (benchmark, comparison), `hstack` a 360×1280 letterboxed Seedance clip on the left with a 360×1280 HyperFrames data panel on the right. **Always letterbox the cinematic side, never crop** — crop loses content the user wanted to see.
- **Wordmark / brand reveal** — pre-render a PNG sequence with PIL (scale-in + glow + fade-out animation), composite via ffmpeg `-itsoffset` + image2 demuxer. Sync the reveal to a meaningful audio cue (avatar word, beat drop, segment transition).
- **Seedance frame-rate alignment** — Seedance always outputs 24fps; A-roll is 25fps. Re-encode each Seedance clip to 25fps before concat.
- **TTS-first segment timing** — submit HeyGen TTS first, read the actual `duration`, size segments to `tts_duration + 0.4s`. Update `storyboard.json` to match.
- **Seedance content-policy avoidance** — humanoid robots/mech/anime triggers `OutputVideoSensitiveContentDetected`. Default to industrial machinery, abstract geometric, generic engineering. Add "no logos, no IP, original generic design" disclaimers to prompts.
- **Concat strategy** — always use the **concat filter** (re-encode at CRF 18), never `-c copy`. AAC frame-boundary clicks at seams perceptibly clip the first phoneme of speech in subsequent segments.

---

8. **Generate background music with Volcengine BGM API** (can run in parallel with other generation):
   - Verify `VOLC_MUSIC_AK` and `VOLC_MUSIC_SK` env vars are set.
   - Submit `GenBGM` with a prompt tuned to the video's tone (tech / lifestyle / serious / energy / contemplative). See prompt patterns table in `references/volcengine-music-api.md`.
   - **Minimum duration is 30s** (v5.0 model floor). For shorter videos, generate ≥30s and trim with ffmpeg `-t <video_duration>` plus a 3s fade-out.
   - Poll `QuerySong` every 10s until `Status: 2` (success). Generation typically 30-90s.
   - Download the WAV from `SongDetail.AudioUrl`, trim and convert to AAC m4a (see helpers in `references/volcengine-music-api.md`).
   - Output: `./assets/music_bed.m4a` matching the final video duration.

9. Validate and assemble final video:
   ```bash
   # Verify every segment has an audio track (non-empty audio stream)
   for f in assets/*.mp4; do
     codec=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of default=nw=1:nk=1 "$f")
     [ -z "$codec" ] && echo "MISSING AUDIO: $f"
   done

   # Verify all segments share resolution + framerate (e.g. 720x1280 @ 25fps)
   # Re-encode any outliers to match before concat

   # Concatenate using the concat FILTER (re-encodes; eliminates AAC frame boundary
   # clicks/cut-offs that -c copy sometimes produces when stitching different sources)
   ffmpeg -y \
     -i aroll-1.mp4 -i broll-seg2.mp4 -i aroll-3.mp4 \
     -i broll-seg4.mp4 -i aroll-5.mp4 -i broll-seg6.mp4 \
     -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a][5:v][5:a]concat=n=6:v=1:a=1[v][a]" \
     -map "[v]" -map "[a]" \
     -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 \
     -c:a aac -b:a 192k -ar 48000 \
     /tmp/concat_clean.mp4

   # Mix music bed under voice using SIDECHAIN DUCKING — music auto-drops when avatar
   # speaks and rises during musical-only moments, so voice always stays dominant.
   ffmpeg -y -i /tmp/concat_clean.mp4 -i assets/music_bed.m4a \
     -filter_complex "\
       [0:a]asplit=2[voice_trigger][voice_out]; \
       [1:a]volume=0.5[music_in]; \
       [music_in][voice_trigger]sidechaincompress=threshold=0.03:ratio=10:attack=10:release=300:makeup=1[music_ducked]; \
       [voice_out][music_ducked]amix=inputs=2:duration=first:normalize=0[a]" \
     -map 0:v -map "[a]" \
     -c:v copy -c:a aac -b:a 192k -ar 48000 \
     dist/main.mp4
   ```

   **Why sidechain ducking instead of static music volume:**
   - Static-volume mix (e.g. `[music]volume=0.35,amix=...`) compromises in both directions: too loud during voice, too quiet during gaps.
   - Sidechain ducking compresses the music *only when voice is present*. Settings: threshold 0.03 (voice above ~3% of full scale triggers ducking), ratio 10 (heavy duck), attack 10ms (fast onset so first phonemes aren't competing), release 300ms (smooth recovery between phrases).
   - Result: voice consistently sits ~10-15 dB above music during speech; music breathes back in during transitions. Verify with `ffmpeg -af volumedetect`: voice moments should land near -18 dB, music-only gaps between -22 and -28 dB.

   **Important:** Use the concat FILTER (not the concat demuxer with `-c copy`) when stitching segments from different sources. `-c copy` preserves source codecs but leaves AAC priming-delay artifacts at boundaries — these manifest as clicks, dropped first phonemes, or apparent "cut-offs" at segment seams. The filter re-encodes once and produces clean transitions.

### Failure handling

- If a HeyGen A-roll segment fails: re-submit it ONLY (don't redo the whole batch)
- If TOS upload fails: check `/Users/bytedance/.claude/skills/tos-upload/tos_credentials.json` — endpoint must be `tos-ap-southeast-1.bytepluses.com` (not `volces.com`), bucket must match the region
- If Seedance `CreateAsset` fails with URL error: TOS URL may have expired — re-run the tos-upload script with `--expires 86400` and retry CreateAsset with the new URL
- If HeyGen TTS audio download fails: retry once; if still failing, fall back to submitting Seedance without an `audio_url` and note that voice quality may differ
- If a Seedance task fails (`"status": "failed"`): check `error.message`; common causes: portrait aspect ratio out of range (fix image), prompt too long (shorten), or model quota exceeded
- If Seedance portrait asset is rejected: the image doesn't meet requirements — ask user for a better photo (front-facing, no occlusion, ≥300×300px)
- If a HeyGen TTS voice-over call fails: retry once; if still failing, generate a silent audio track for that B-roll as a fallback and note it in the Phase 5 summary
- If credits insufficient: stop, tell user how many credits short, suggest options
- If HyperFrames lint errors: read the specific error, fix the HTML, re-run
- If final video has lip sync issues: verify every segment has an audio track (`ffprobe` check in step 8); a missing audio stream on any B-roll causes timestamp drift in subsequent A-roll

---

## Phase 5 — Lark upload and delivery

**Goal:** Get the final MP4 into the user's Lark space and return a shareable URL.

### Steps

1. Verify lark-cli is set up:
   ```bash
   lark-cli --version
   lark-cli auth status
   ```
   If not authenticated: `lark-cli auth login --recommend` (this opens a browser for OAuth).

2. Upload to Lark Drive:
   ```bash
   lark-cli drive +upload --file dist/main.mp4 --folder-token <user's preferred folder> --output json
   ```
   
   If user hasn't specified a folder, ask: "Which Lark folder should I upload to?" — they can paste a folder URL and you parse the token from it.

3. Parse the JSON output to get:
   - `file_token` — the file ID in Lark
   - `url` or constructed URL: `https://<domain>/file/<file_token>`

4. Optionally send the URL to a Lark chat via `lark-cli im +messages-send`. Ask the user if they want this.

5. Return a final summary:
   ```
   ✓ Video produced: dist/main.mp4 (12.3 MB, 15.0s)
   ✓ Uploaded to Lark: https://...
   
   Total cost:
     - HeyGen credits: 53 (147 remaining this month)
     - Perplexity API: $0.30
     - Lark / HyperFrames: free
   
   Local file: ~/projects/<product-slug>-video/dist/main.mp4
   ```

See `references/lark-upload-guide.md` for detailed lark-cli commands and troubleshooting.

---

## Reference docs (load on demand)

- `references/hook-patterns.md` — viral hook templates from TikTok/Shorts research
- `references/broll-routing.md` — full decision matrix for video-agent vs hyperframes vs seedance
- `references/storyboard-format.md` — exact JSON/markdown spec for storyboard.md
- `references/cost-rates.md` — current HeyGen credit rates and Perplexity pricing
- `references/seedance-api.md` — Seedance 2.0 API: endpoints, portrait upload workflow, Python helpers
- `references/volcengine-music-api.md` — Volcengine BGM API: GenBGM/QuerySong, prompt patterns, mix volumes
- `references/production-techniques.md` — Phase 4 patterns: PIL annotation overlays, split-screen layouts, wordmark reveals, frame-rate alignment, concat strategy, iterative refinement loop
- `references/perplexity-usage.md` — query patterns, model selection, cost tips
- `references/lark-upload-guide.md` — lark-cli commands, auth, folder management
- `references/reference-video-analysis.md` — how to extract style from user's reference clip

Load these only when you need their specific guidance — do not pre-read them.

---

## Scripts

- `scripts/preflight.py` — environment check (node, ffmpeg, lark-cli, env vars)
- `scripts/parse_inputs.py` — categorize and extract from user's input files
- `scripts/analyze_reference_video.py` — ffprobe + key frame analysis
- `scripts/perplexity_research.py` — parallel social-listening queries
- `scripts/estimate_cost.py` — storyboard → credit + USD cost breakdown
- `scripts/compose_and_render.py` — orchestrates HeyGen + HyperFrames + ffmpeg
- `scripts/upload_to_lark.py` — wraps lark-cli for the upload step

All scripts use stdin/stdout/JSON. They never write to anywhere outside the working directory.

---

## Security and safety

- API keys (HeyGen, Perplexity, BytePlus Ark, Volcengine Music) MUST come from environment variables, never written to disk
- Never log or print full API keys — show only first 8 chars + `...`
- All paid operations require user approval (Phase 3 gate)
- Never auto-share videos to chats without explicit user confirmation
- Lark upload requires the user to be already authenticated (don't prompt for credentials)

If at any point the user asks to skip Phase 3 approval, push back: "Phase 3 approval prevents wasting credits. Are you sure?"
