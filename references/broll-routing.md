# B-roll routing — Video Agent vs Seedance vs HyperFrames vs Hybrid

This is the most consequential design decision in the storyboard. Picking the wrong tool wastes credits OR produces a bad-looking segment. The decision rules below are based on what each tool does well.

## What each tool is actually good at

### HeyGen Video Agent (cinematic AI generation)

**Strengths:**
- Generates plausible-feeling lifestyle/scene footage from a prompt
- Camera moves, lighting, atmospheric vibe
- Abstract concepts visualized (data flowing, networks connecting, agents collaborating)
- Things that need to feel "real" but you don't have actual footage of

**Weaknesses:**
- Cannot reproduce specific UI screenshots accurately — text and logos render as gibberish
- Cannot show specific numbers or data — generated text is unreliable
- Costs credits per second
- Non-deterministic — may need 2-3 tries to get something usable
- Generation takes 30-90 seconds per clip

**Cost:** ~5-10 credits per 2-3 second clip on Creator plan rate.

**Use it for:** mood/atmosphere, abstract conceptual scenes, cinematic transitions, lifestyle shots, anything where exact accuracy doesn't matter but feeling does.

### Seedance 2.0 (BytePlus ModelArk — cinematic AI generation)

**Strengths:**
- Comparable or better motion quality vs HeyGen Video Agent for cinematic scenes
- Also supports **talking-head A-roll** with a pre-approved portrait asset
- Same use cases as Video Agent for B-roll
- Independent of HeyGen plan — useful when Video Agent plan is unavailable or quota is low

**Weaknesses:**
- Same fundamental limitations as Video Agent: no specific UI/text accuracy, non-deterministic
- Generation takes 60-180 seconds per clip (slower than Video Agent)
- For A-roll: portrait upload + review adds 30-120s one-time setup; voice accuracy lower than HeyGen cloned voice
- Requires `BYTEPLUS_ARK_API_KEY` env var (separate from HeyGen)

**Cost:** BytePlus token-based pricing (see https://docs.byteplus.com/en/docs/ModelArk/1544106).

**Use it for:** any cinematic B-roll where HeyGen Video Agent would apply; A-roll when cinematic portrait realism matters more than voice accuracy. Default choice when HeyGen Video Agent is not available on the user's plan.

**API reference:** `references/seedance-api.md`

### HyperFrames (programmatic HTML/CSS/GSAP animation)

**Strengths:**
- Pixel-perfect control over text, numbers, layout
- Free (renders locally)
- Deterministic — same code = same output every time
- Fast iteration: edit HTML, re-render in 2 minutes
- Can incorporate user-provided screenshots as IMG elements (not regenerated)
- Great for: counters, comparisons, charts, quotes, feature montages, CTAs

**Weaknesses:**
- Can't generate "real-looking" footage
- Cinematic camera moves require lots of hand-coded GSAP
- Looks "designed" rather than "shot" — can feel less authentic for some products

**Cost:** $0. Local Chromium render.

**Use it for:** anything with specific text/numbers/data, before-after comparisons, quotes, CTAs, programmatic transitions, feature lists, anything where you want exact visual control.

### Hybrid (HyperFrames frame + cinematic fill)

Sometimes you want a HyperFrames-style structure (a card layout, a labeled comparison) but with cinematic content INSIDE the cards. The cinematic fill can come from Video Agent or Seedance.

**Use it for:** structured content where one zone benefits from cinematic generation but the framing/labels/transitions need to be exact.

---

## Decision matrix

For each B-roll segment in the storyboard, route it using this table:

| If the segment shows... | Use | Why |
|---|---|---|
| The actual product UI being used | **HyperFrames + screenshots** | Generated UI looks fake; real screenshots feel real |
| Numbers (counts, %, $, ratios) | **HyperFrames** | Precise typography, animatable counters |
| Trends, time-series, growth curves | **HyperFrames** | SVG/CSS animation, exact control |
| Abstract concepts (AI agents, data flow) | **Video Agent** or **Seedance** | Cinematic feel impossible to fake with HTML |
| Feature comparison side-by-side | **HyperFrames** | Layout precision matters |
| Quote or testimonial overlay | **HyperFrames** | Typography control |
| Mood/establishing scene (city, office) | **Video Agent** or **Seedance** | Generative atmosphere |
| Quick-cut feature montage (3-5 features) | **HyperFrames + screenshots** | Reuses existing assets, cheap |
| Single feature spotlight with motion | **Hybrid** (HF frame + VA/Seedance inside) | Real product + designed framing |
| Founder voiceover B-roll (no specific content) | **Video Agent** or **Seedance** | Atmosphere over specifics |
| CTA / link / "go try it now" | **HyperFrames** | Must be readable, branded |
| Logo + tagline ending | **HyperFrames** | Brand consistency |
| User reaction / human moment | **Video Agent** or **Seedance** | Real people > generated UIs |
| Product packaging / physical thing | **Video Agent** / **Seedance** / screenshots | Generative if no photos exist |

**Choosing between Video Agent and Seedance for cinematic segments:**
- HeyGen Video Agent available on plan → use Video Agent (faster, already authenticated)
- HeyGen Video Agent not available / quota low → use Seedance
- User explicitly requests Seedance → use Seedance regardless

---

## Anti-patterns (don't do these)

### ❌ Video Agent or Seedance for screenshots / UI demos
Generated UI text looks garbled. Always use real screenshots in HyperFrames for product UI segments.

### ❌ HyperFrames for atmospheric scenes
A static designed graphic of "AI agents collaborating" looks corporate-cringe. Use Video Agent or Seedance with a cinematic prompt instead.

### ❌ Video Agent or Seedance for any specific number
If the segment needs to display "61.5k stars" precisely, never trust generative models to render that text — use HyperFrames with a counter animation.

### ❌ Excessive hybrid segments
Hybrid is more complex to author. Use it only when there's a clear creative reason. If you can do it with one tool cleanly, prefer that.

### ❌ Mixing A-roll tools within the same video
Pick either HeyGen Avatar V or Seedance talking head for ALL A-roll segments. Don't mix — the avatar style will be visually inconsistent.

---

## Cost-aware routing

If the user's storyboard exceeds their available credits, the first thing to do is **shift Video Agent segments to either Seedance or HyperFrames**:
- Shift to **Seedance**: if cinematic quality must be preserved — Seedance is priced differently (tokens, not HeyGen credits)
- Shift to **HyperFrames**: if the segment can be expressed with text/data/animation — $0 cost

Each Video Agent segment saved = 5-10 HeyGen credits. Often a "demo of feature X" can be replaced with "screenshot of feature X with HyperFrames zoom-in" at zero cost and similar visual quality.

---

## Routing checklist for storyboard.md

For every B-roll segment, the storyboard must explicitly answer:

1. **Tool**: `video-agent` | `seedance` | `hyperframes` | `hybrid`
2. **Why this tool** (1 sentence): tie back to the rules above
3. **Spec**: the actual prompt (Video Agent / Seedance) or layout description (HyperFrames)
4. **Duration**: in seconds, integer or 0.5 increment
5. **Cost**: credits (if Video Agent), tokens (if Seedance), or $0 (if HyperFrames)

If any segment is ambiguous, default to HyperFrames — it's cheaper and more reliable.
