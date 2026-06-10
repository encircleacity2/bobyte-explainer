# Cost rates reference

Current pricing (as of May 2026). Verify before each project — these change.

The skill uses paid/free services: **Seedance 2.0** (A-roll + optional cinematic B-roll),
**Seedream 4.5** (optional portrait restyle), **standalone TTS** (optional voice-over),
**Volcengine music** (optional BGM — only when AI music is enabled in onboarding).
HyperFrames B-roll is free.

---

## Seedance 2.0 (BytePlus ModelArk) — A-roll + cinematic B-roll

Token-based pricing on the BytePlus ModelArk account. A 5–10 s 720p 9:16 clip is
inexpensive; cost scales with duration and resolution. See the ModelArk console for the
current token rate and the account balance.

- A-roll: typically 0-2 clips per video, 5-10 s each.
- Cinematic B-roll: only when a non-person atmospheric shot is needed — most B-roll is
  free HyperFrames instead.

Rough planning figure: a ~90 s explainer with 2 short A-roll clips is a small token spend
(single-digit USD-equivalent). Confirm against the live ModelArk rate.

---

## Seedream 4.5 (BytePlus ModelArk) — portrait restyle

Per-image generation cost on the same ModelArk account. The Phase 2 restyle generates
**4 images** for review; budget for 4 image generations per restyle round (plus more if
the user asks for another round). Small relative to video cost.

---

## Volcengine music API — BGM

Optional — incurred only when `config.music_enabled` is `true`. Per-generation cost for one
music track. The similarity-detection check occasionally rejects a generation; a retry then
costs one more generation. Budget for 1–3 generations per video. Small. If AI music is
disabled, this cost is $0.

---

## Standalone TTS

Optional — incurred only when `config.tts_enabled` is `true` and the storyboard uses
`VO+B-roll` segments. Cost is provider-specific:

- BytePlus Seed TTS: provider/account billed by request/characters or the configured resource.
- ElevenLabs: billed by characters/plan quota.
- Internal proxy: proxy owner should expose usage/cost reporting.

Track total narrated characters and audio minutes in the cost estimate. TTS is usually far
cheaper than regenerating video clips and is the preferred iteration path for narration edits.

---

## HyperFrames — B-roll

**$0.** Local headless Chromium render. The only "cost" is local CPU + a one-time
~140 MB Chromium download.

---

## Lark CLI / Drive

**$0** for uploads/downloads via the user's existing Lark plan. A 9:16 1080p ~90 s MP4 is
roughly 8–12 MB.

---

## Cost decision rules for the Phase 3 storyboard

1. **Most B-roll → HyperFrames** ($0). Reserve Seedance B-roll for genuine cinematic /
   atmospheric shots only.
2. **TTS voice-over** — default for B-roll-led customer overview, benchmark, pricing, and demo sections.
3. **A-roll** — keep to ~0-2 clips, 5-10 s each. Extra A-roll clips add token cost.
4. Always show the cost estimate in the Phase 3 storyboard so the user approves with eyes open.

## Cost reduction tactics

If the storyboard cost is too high:
1. Convert any Seedance B-roll segment to HyperFrames (saves the whole clip's tokens).
2. Shorten or drop one A-roll clip.
3. Move narration edits to TTS instead of regenerating paid A-roll.
4. Reduce overall video length.

Always show the user the cost-reduced alternative alongside the original.
