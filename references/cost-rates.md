# Cost rates reference

Current pricing (as of May 2026). Verify before each project — these change.

---

## HeyGen Premium Credits (web plan)

When using MCP path (OAuth), all HeyGen operations consume Premium Credits from the user's web plan.

### Plan tiers

| Plan | Monthly cost | Credits/month | $/credit equivalent |
|------|------------|--------------|--------------------|
| Free | $0 | 10 | n/a (testing only) |
| Creator (annual) | $24 | 200 | $0.12 |
| Creator (monthly) | $29 | 200 | $0.145 |
| Pro | $99 | 2000 | $0.0495 |
| Business | varies | 1000+ shared | varies |

Premium Credit Pack add-on: $15/month for 300 extra credits (or $150/year). Stack multiple if needed.

### Credits per operation

| Operation | Credits per second | Credits per 2.5s segment | Credits per 30s |
|-----------|-------------------|------------------------|----------------|
| Avatar V (Digital Twin from web) | ~6.7 | 17 | 200 |
| Avatar IV (Photo Avatar) | ~6.7 | 17 | 200 |
| Video Agent | ~2 | 5 | 60 |
| Avatar III (older, cheaper) | ~3 | 8 | 100 |
| Lipsync | ~2 | 5 | 60 |
| Video Translation | ~3 per source second | varies | 90 |

### Quick math examples

- 15-second video, 3× A-roll (7s total) + 1× Video Agent (2.5s) = 47 + 5 = **52 credits**
- 30-second video, 4× A-roll (10s total) + 2× Video Agent (5s) = 67 + 10 = **77 credits**

### Buying more credits without upgrading plan

If user is on Creator and runs low: buy 300-credit pack at $15/month. Cancel anytime.

---

## HeyGen Direct API (x-api-key path)

Used only if user can't or doesn't want MCP. Independent billing pool.

| Operation | Cost per second |
|-----------|----------------|
| Photo Avatar (Avatar IV) | $0.05 |
| Digital Twin via API (Enterprise only) | $0.0667 |
| Video Agent | $0.0333 |
| Voices - Starfish TTS | $0.000667 |
| Lipsync - Speed | $0.0333 |
| Video Translation - Speed | $0.0333 |

Minimum top-up: $5. Pay-as-you-go.

15-second video via Photo Avatar API path: ~$0.55.

---

## Perplexity Sonar API

Used in Phase 2 for social listening research.

### Models

| Model | Best for | Cost per request (typical) |
|-------|---------|---------------------------|
| sonar | Quick fact lookup | $0.005-0.01 |
| sonar-pro | Research with citations (recommended) | $0.05-0.08 |
| sonar-reasoning | Complex multi-step | $0.10-0.20 |
| sonar-deep-research | Comprehensive reports | $0.30-1.00 |

### Pricing model

Token-based:
- Small models: ~$0.20 / 1M tokens
- Medium / sonar-pro: ~$0.60-1.00 / 1M tokens

A typical Phase 2 research with 5 sonar-pro queries:
- 5 queries × ~$0.06 average = **~$0.30 total**

If user is on Perplexity Pro subscription: $5/month included credits cover this entirely.

### Endpoint

```
POST https://api.perplexity.ai/chat/completions
Headers:
  Authorization: Bearer pplx-...
  Content-Type: application/json
Body:
  {
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "<query>"}]
  }
```

OpenAI-SDK compatible.

---

## HyperFrames

**$0.** Local headless Chromium render.

The only "cost" is local CPU + ~140 MB Chromium download (one-time).

---

## Lark CLI / Drive

**$0** for file uploads and downloads via the user's already-paid Lark plan.

Free Lark workspace tiers cap at 10GB storage. Each 9:16 720p 15s MP4 is roughly 8-15 MB.

---

## Cost decision rules for storyboard

When designing the storyboard in Phase 3:

1. **If user has plenty of credits** (>100): Use Video Agent freely for atmospheric segments.
2. **If user has tight credits** (~50-100): Limit Video Agent to 1 segment max. Replace others with HyperFrames.
3. **If user is on Free plan or out of credits**: Skip Video Agent entirely. All B-roll = HyperFrames + screenshots.

Always show credit balance BEFORE the cost breakdown so user knows what they have to work with.

---

## Cost reduction tactics

If the proposed storyboard exceeds budget:

1. **Convert Video Agent → HyperFrames** for any segment where exact accuracy matters more than vibe (saves 5-10 credits per segment).
2. **Shorten A-roll segments** by 0.5s each (saves ~3 credits per segment).
3. **Use Avatar III instead of Avatar V** if quality drop is acceptable (saves ~1.5 credits per second).
4. **Reduce video length** from 30s to 15s (cuts cost roughly in half).
5. **Use stock screenshots over generated B-roll** wherever the product UI is the focus.

Always show the user the cost-reduced alternative alongside the original — let them choose.
