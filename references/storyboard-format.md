# Storyboard format specification

The storyboard is the artifact approved before any paid generation runs (Phase 3 gate).
It must be complete, unambiguous, and reviewable by a non-technical user.

## File location

Working directory: `storyboard.md` (human-readable) and optionally `storyboard.json`
(machine-readable for `compose_and_render.py`). Keep them in sync.

---

## storyboard.md format

```markdown
# Storyboard — <product name>

## Recommended length: 90s
**Rationale:** <why — content profile, number of features/skills to cover>

## Timeline

| # | Time | Type | Tool | Content | Spoken / VO |
|---|------|------|------|---------|-------------|
| 1 | 0–5s   | B-roll | HyperFrames | Kinetic-typography hook | — |
| 2 | 5–12s  | A-roll | Seedance 2.0 | Intro to camera | "Every SA juggles Lark, meetings, dashboards…" |
| 3 | 12–16s | B-roll | HyperFrames | Install scene | — |
| 4 | 16–86s | B-roll | HyperFrames | 7 skill demos, 10s each | — |
| 5 | 86–91s | A-roll | Seedance 2.0 | Closing CTA to camera | "Seven skills, one install. Get it on GitHub." |
| 6 | 91–96s | B-roll | HyperFrames | Brand reveal | — |

## Segment details

### Segment 1 (B-roll HyperFrames, 0–5s) — kinetic-typography hook
- **Why this tool:** rhythmic word animation needs precise type control — HyperFrames.
- **Spec:** chaos words punch-flash in sequence, then resolve to the POLYM wordmark + tagline.

### Segment 2 (A-roll Seedance 2.0, 5–12s)
- **Mode:** r2v (reference video → voice + facial motion) or image+text — see SKILL.md.
- **Script:** "Every SA juggles Lark, meetings, dashboards and wikis. Polym does the heavy lifting."
- **Tone:** warm, confident, direct to camera.
- **Note:** even in r2v mode, put the script in the text prompt so the spoken words are controlled.

### Segment 4 (B-roll HyperFrames, 16–86s) — skill demos
- **Why this tool:** typed-prompt + result + deliverable cards need exact UI mockups — HyperFrames.
- **Spec:** per skill (~10s): title → typed prompt → agent runs → result → deliverable doc card.

### Segment 5 (A-roll Seedance 2.0, 86–91s) — closing CTA
- **Script:** "Seven skills. One install. Polym — your SA team's polymath. Get it on GitHub."

## Cost estimate

| Item | Quantity | Cost |
|------|----------|------|
| Seedance A-roll | 2 clips (~12s) | <tokens> |
| HyperFrames B-roll | N segments | $0 |
| Volcengine music | 1 track | <small> |
| **Total** |  | **<tokens> + small** |

## Approval

**Status:** ⏸ Awaiting user approval — respond `approve` / `change <segment>` / `restart`.
```

---

## Segment field rules

| Segment type | Tool | Notes |
|---|---|---|
| A-roll | `seedance-2.0` | Talking-head. Always carries a spoken `script`. Keep each clip 5–10s. Typically only 2 per video (hook + CTA). |
| B-roll | `hyperframes` | Typographic / data / demo scenes. Free, local render. The default for B-roll. |
| B-roll | `seedance-2.0` | Only for non-person cinematic / atmospheric shots. |

There is **one** A-roll tool: Seedance 2.0. Do not mix A-roll tools.

---

## Validation checklist

Before presenting to the user, verify:

- [ ] Segment durations sum to the stated total; no timeline gaps.
- [ ] A-roll segments are 5–10s each; the spoken script fits the duration (~2 words/sec).
- [ ] Every A-roll segment has an explicit `script`.
- [ ] Every B-roll segment has an explicit `tool` and a one-line "why this tool".
- [ ] Cost estimate is shown.
- [ ] The CTA is the last spoken beat (not buried mid-video).
- [ ] A recommended length is stated with rationale.

If any check fails, fix before presenting.
