# Storyboard format specification

The storyboard is the artifact that gets approved before any paid generation runs. It must be complete, unambiguous, and reviewable by a non-technical user.

## File location

Working directory: `storyboard.md` and `storyboard.json`

The `.md` is human-readable for the user. The `.json` is machine-readable for `compose_and_render.py`. Keep them in sync.

---

## storyboard.md format

```markdown
# Storyboard — <product name>

## Hook strategy
**Pattern:** <Pain question | Bold claim | Visual surprise | Curiosity gap>
**Rationale:** <1-2 sentences tying to Phase 2 research>

## Total duration: 15s (or 30s)

## Timeline

| # | Time | Type | Tool | Content | Voice-over | Cost |
|---|------|------|------|---------|------------|------|
| 1 | 0.0–2.5s | A-roll | HeyGen Avatar V | "Building AI agents from scratch is brutal." | *(avatar lip-sync)* | 17 credits |
| 2 | 2.5–4.0s | B-roll | HyperFrames | 4 pain words slam in: Memory · Sandbox · Tools · Sub-agents | "All of this — just to get started." | $0 |
| 3 | 4.0–6.5s | A-roll | HeyGen Avatar V | "DeerFlow fixes that — open source, from ByteDance." | *(avatar lip-sync)* | 17 credits |
| 4 | 6.5–9.0s | B-roll | Video Agent | Cinematic agents collaborating, blue-green palette | "Sub-agents that actually plan." | 5 credits |
| 5 | 9.0–11.0s | B-roll | HyperFrames | Counter 0→61.5k stars + #1 Trending badge | "61,500 stars and climbing." | $0 |
| 6 | 11.0–13.0s | A-roll | HeyGen Avatar V | "One harness. Many hands." | *(avatar lip-sync)* | 13 credits |
| 7 | 13.0–15.0s | B-roll | HyperFrames | CTA: github.com/bytedance/deer-flow → | "Link in bio." | $0 |

## Segment details

### Segment 1 (A-roll, 0.0–2.5s)
- **Script:** "Building AI agents from scratch is brutal."
- **Tone:** Direct, slightly frustrated, eye contact
- **Background:** #FAFAF7 (off-white)
- **Caption overlay:** "DeerFlow: open-source AI agent harness" (appears at 0.5s)

### Segment 2 (B-roll HyperFrames, 2.5–4.0s)
- **Tool:** HyperFrames
- **Why this tool:** Specific text labels + slam-in animation requires precise typography and timing — HF is the right fit.
- **Voice-over script:** "All of this — just to get started."
- **Voice-over style:** Slightly exasperated, fast delivery to match the visual slam-in energy
- **Spec:**
  - Background: #0a0a0a
  - "all of this" text in red, rotated -6deg, slamming in at 2.5s
  - 4 pain word boxes (Memory, Sandbox, Tools, Sub-agents) staggered 0.15s apart with back-out scale
- **Animation:** GSAP back-out(1.7) for each word

### Segment 3 (A-roll, 4.0–6.5s)
- ...

### Segment 4 (B-roll Video Agent, 6.5–9.0s)
- **Tool:** Video Agent
- **Why this tool:** Atmospheric, cinematic feel that HyperFrames can't reproduce. No specific text needed.
- **Voice-over script:** "Sub-agents that actually plan."
- **Voice-over style:** Confident, low energy, let the visuals carry it
- **Prompt:** "Cinematic abstract visualization of multiple AI agents collaborating: glowing nodes connected by streams of light data, dark futuristic background, slow camera dolly-in, blue-to-green color palette. No people, no text, no logos. 2.5 seconds, 9:16 vertical."
- **Caption overlay:** "Sub-agents that actually plan" (appears 6.8s, fades out 9.0s)
- **Fallback:** if generation produces unusable result, fallback to HyperFrames with abstract animated network diagram

### Segment 5 (B-roll HyperFrames, 9.0–11.0s)
- ...

### Segment 6 (A-roll, 11.0–13.0s)
- ...

### Segment 7 (B-roll HyperFrames, 13.0–15.0s)
- ...

## Cost estimate

| Item | Quantity | Cost |
|------|----------|------|
| HeyGen A-roll segments | 3 (7s total) | 47 credits |
| HeyGen Video Agent segments | 1 (2.5s) | 5 credits |
| HeyGen TTS voice-over (B-roll) | 4 segments | ~0 credits (TTS is free on Creator+) |
| HyperFrames segments | 3 (5.5s) | $0 |
| **Subtotal HeyGen** |  | **52 credits** |
| Perplexity research (Phase 2) | 5 queries | $0.30 |
| Lark upload | 1 file | $0 |
| **Total** |  | **52 credits + $0.30** |

Plan balance after this run:
- Creator plan (200/mo): 148 credits remaining

## Approval

**Status:** ⏸ Awaiting user approval

User: please respond with one of:
- `approve` — proceed to Phase 4 production
- `change <segment>` — describe what to change
- `restart` — go back to Phase 3 with a different angle
```

---

## storyboard.json format

```json
{
  "product_name": "DeerFlow",
  "total_duration": 15.0,
  "hook_pattern": "pain_question",
  "hook_rationale": "Phase 2 research showed 'building agents from scratch' as the #1 pain in r/LocalLLaMA threads.",
  "segments": [
    {
      "id": "seg-1",
      "type": "a-roll",
      "tool": "heygen-avatar",
      "start": 0.0,
      "duration": 2.5,
      "script": "Building AI agents from scratch is brutal.",
      "tone": "direct, slightly frustrated",
      "background": "#FAFAF7",
      "caption": "DeerFlow: open-source AI agent harness",
      "caption_start": 0.5,
      "caption_duration": 2.0,
      "estimated_credits": 17
    },
    {
      "id": "seg-2",
      "type": "b-roll",
      "tool": "hyperframes",
      "start": 2.5,
      "duration": 1.5,
      "intent": "make the user feel the pain — show all the things AI agents need",
      "voiceover_script": "All of this — just to get started.",
      "voiceover_style": "slightly exasperated, fast delivery to match visual slam-in energy",
      "spec": {
        "background": "#0a0a0a",
        "elements": [
          {
            "type": "text",
            "content": "all of this",
            "style": {"color": "#ef4444", "rotation": -6, "fontSize": 56},
            "animation": {"type": "slam-in", "easing": "back.out(2)", "duration": 0.3}
          },
          {
            "type": "grid",
            "items": ["Memory", "Sandbox", "Tools", "Sub-agents"],
            "style": {"borderColor": "#ef4444", "background": "rgba(239,68,68,0.1)"},
            "animation": {"type": "stagger-in", "stagger": 0.15, "easing": "back.out(1.7)"}
          }
        ]
      },
      "estimated_credits": 0
    },
    // ... more segments
  ],
  "cost_breakdown": {
    "heygen_credits": 52,
    "perplexity_usd": 0.30,
    "hyperframes_usd": 0,
    "lark_usd": 0,
    "total_credits": 52,
    "total_usd": 0.30
  },
  "approval_status": "pending"
}
```

### Voice-over field rules

| Segment type | `voiceover_script` | `voiceover_style` |
|---|---|---|
| A-roll | **omit** — the avatar lip-syncs the `script` field directly | **omit** |
| B-roll (any tool) | **required** — always provide a script, even if brief ("Link in bio.") | **required** — tone guidance for TTS generation |
| B-roll (intentionally silent) | Set to `null` with a `voiceover_rationale` field explaining why silence is a deliberate creative choice | **omit** |

**Never leave `voiceover_script` absent on a B-roll segment** without a `voiceover_rationale`. A missing voice-over is an unpleasant viewer experience, not a valid default.

---

## Validation checklist

Before presenting to user, verify:

- [ ] Total of all segment durations equals stated total duration (15.0s or 30.0s)
- [ ] No gaps in timeline (segment N's end == segment N+1's start)
- [ ] Hook segment ends ≤ 3.0s
- [ ] No A-roll segment > 3.0s (viewer fatigue)
- [ ] A-roll script word count: ≤ 12 words for 2.5s, ≤ 15 words for 3s
- [ ] Every B-roll segment has explicit `tool` and `why this tool` reasoning
- [ ] Every B-roll segment has `voiceover_script` OR `voiceover_rationale` (null + reason)
- [ ] B-roll voice-over word count fits duration: ≤ 8 words for 2s, ≤ 12 words for 3s, ≤ 18 words for 5s
- [ ] B-roll voice-over does NOT repeat verbatim what the visual already shows — it should complement, not caption
- [ ] All Video Agent segments have a fallback HyperFrames spec
- [ ] Cost estimate matches segment count × per-segment rate
- [ ] CTA is the last segment (not buried mid-video)

If any check fails, fix before presenting to user.
