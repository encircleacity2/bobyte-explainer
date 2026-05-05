# Perplexity Sonar API — usage patterns

How to use Perplexity in Phase 2 of the bobyte-explainer skill.

## Setup

```bash
export PERPLEXITY_API_KEY='pplx-...'
```

NEVER write the key to disk. NEVER log the full key value.

## Endpoint

```
POST https://api.perplexity.ai/chat/completions
Authorization: Bearer ${PERPLEXITY_API_KEY}
Content-Type: application/json
```

## Recommended model for this skill

**`sonar-pro`** — best balance of speed, cost, and citation quality for research queries. Each query costs ~$0.06.

Use `sonar-deep-research` only if user explicitly asks for in-depth research (queries cost $0.30-1.00 each).

Avoid `sonar` (the basic model) for this skill — citation quality is lower.

## Request format

```python
import os, json, urllib.request

payload = {
    "model": "sonar-pro",
    "messages": [
        {"role": "system", "content": "You are a market research analyst. Be specific and cite sources."},
        {"role": "user", "content": query}
    ],
    "max_tokens": 2000,
    "temperature": 0.2,  # low temp for factual research
}

req = urllib.request.Request(
    "https://api.perplexity.ai/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['PERPLEXITY_API_KEY']}",
        "Content-Type": "application/json",
    },
    method="POST",
)
resp = urllib.request.urlopen(req, timeout=60)
data = json.loads(resp.read().decode())
content = data["choices"][0]["message"]["content"]
citations = data.get("citations", [])  # list of source URLs
```

## Response structure

```json
{
  "id": "...",
  "model": "sonar-pro",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "<the research text with [1][2] citation markers>"
      }
    }
  ],
  "citations": [
    "https://reddit.com/r/...",
    "https://github.com/...",
    "https://news.ycombinator.com/..."
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 800,
    "total_tokens": 900
  }
}
```

## Recommended query patterns for product video research

Run these 5 queries in parallel for a typical product:

### 1. Pain points discovery
```
What are the most common frustrations or pain points that engineers/builders 
voice about [product category, e.g. "AI agent frameworks"]? Look at recent 
reddit threads, hacker news comments, and twitter posts. List the top 3-5 
pain points with specific quotes if possible.
```

### 2. Viral angle research
```
What product launch videos in the [category] space have gone viral on TikTok, 
YouTube Shorts, or Twitter in the last 6 months? What was their hook strategy?
What made viewers engage (reshares, comments, click-through)?
```

### 3. Competitive context
```
Who are [product name]'s main competitors and what do users say about them in 
recent comparisons? What does [product] do differently that users mention?
```

### 4. Recent discussions
```
What did people say about [product name] in the last 30 days? Reddit, twitter, 
hacker news. Highlight any specific features, complaints, or surprising uses 
that came up multiple times.
```

### 5. Audience profile
```
Based on online discussions, who is the typical user of [product name]? 
Engineer? PM? Marketer? What are they currently using and why might they 
switch? What language do they use to describe their problems?
```

## Cost optimization

- **Run queries in parallel** — Perplexity rate limit on Tier 1 is 50 requests/min, plenty for 5 parallel
- **Cache results in `research-cache.json`** keyed by query hash — if user re-runs Phase 2 for the same product, reuse cached results
- **Don't ask for raw web pages** — Perplexity already does the synthesis; asking it to "list 100 reddit posts" wastes tokens
- **Use `max_tokens: 2000`** — usually enough for synthesis, prevents runaway responses

## Output: research.md format

After all queries complete, synthesize into a single markdown doc:

```markdown
# Phase 2 research — <product name>

## Top pain points (from query 1)
1. <pain> — sourced from <url>
2. ...

## Viral hook patterns (from query 2)
- Pattern: <name>. Used by: <example>. Why it worked: <reason>.
- ...

## Competitive context (from query 3)
- Main competitors: <list>
- What [product] does differently: <list>
- Typical user complaint about competitors: <list>

## Recent discussions (from query 4)
- <date>: <key thread or post>
- ...

## Audience profile (from query 5)
- Primary persona: <description>
- Their language: <key phrases they use>
- What they're switching from: <list>

## Recommended hooks (synthesis)
Based on all of the above, the top 3 hook options are:
1. ...
2. ...
3. ...

## Sources
<all citation URLs from all queries, deduplicated>
```

This research.md is what feeds into the Phase 3 storyboard design.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad API key | Check `$PERPLEXITY_API_KEY` |
| 429 Rate limited | Too many requests | Add 2-3 second delay between queries |
| 400 model not found | Old model name | Use `sonar-pro` not `sonar-medium-online` |
| Empty citations | Query was too factual / not research-shaped | Reframe as "what do people say about..." |
