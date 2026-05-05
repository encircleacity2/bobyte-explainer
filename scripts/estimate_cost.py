#!/usr/bin/env python3
"""
Estimate cost of executing a storyboard.

Reads storyboard.json and outputs a markdown cost table.

Usage:
    python3 estimate_cost.py storyboard.json
    python3 estimate_cost.py storyboard.json --plan creator
    python3 estimate_cost.py storyboard.json --plan-balance 145

Plans:
    creator-monthly: 200 credits/month at $29
    creator-annual:  200 credits/month at $24
    pro:             2000 credits/month at $99
    free:            10 credits/month
"""
import argparse
import json
import sys
from pathlib import Path

# HeyGen credit rates (per second, web plan)
RATES_PER_SEC = {
    "heygen-avatar": 6.7,         # Avatar V / Avatar IV via MCP
    "heygen-avatar-v3": 3.0,      # older Avatar III
    "heygen-photo-avatar": 6.7,   # photo avatar via MCP
    "heygen-video-agent": 2.0,    # Video Agent
    "heygen-lipsync": 2.0,
    "hyperframes": 0,
    "hybrid": None,                # cost is sum of underlying tools
}

# Tool name aliases — accept multiple ways to name the same thing
TOOL_ALIASES = {
    "video-agent": "heygen-video-agent",
    "videoagent": "heygen-video-agent",
    "avatar": "heygen-avatar",
    "avatar-v": "heygen-avatar",
    "avatar-iv": "heygen-photo-avatar",
    "photo-avatar": "heygen-photo-avatar",
}

PLANS = {
    "free": 10,
    "creator-monthly": 200,
    "creator-annual": 200,
    "creator": 200,
    "pro": 2000,
    "business": 1000,
}


def normalize_tool(name):
    n = name.lower().strip()
    return TOOL_ALIASES.get(n, n)


def credits_for_segment(seg):
    tool = normalize_tool(seg.get("tool", ""))
    duration = float(seg.get("duration", 0))
    rate = RATES_PER_SEC.get(tool)
    if rate is None:
        return None  # unknown / hybrid
    return round(rate * duration)


def perplexity_cost_estimate(num_queries=5, avg_tokens=1500, model="sonar-pro"):
    # Rough: sonar-pro ~$1/1M tokens
    rate = 1.0 if model == "sonar-pro" else 0.20
    return round(num_queries * avg_tokens / 1_000_000 * rate, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard", help="Path to storyboard.json")
    ap.add_argument("--plan", default="creator-annual",
                    help="HeyGen plan: free, creator, pro, etc.")
    ap.add_argument("--plan-balance", type=int, default=None,
                    help="Override starting credit balance (defaults to plan's monthly allowance)")
    ap.add_argument("--perplexity-already-spent", type=float, default=0.30,
                    help="USD already spent on Perplexity in Phase 2 (default 0.30)")
    ap.add_argument("--out", default="cost-estimate.md", help="Output markdown file")
    args = ap.parse_args()

    sb = json.loads(Path(args.storyboard).read_text())
    segments = sb.get("segments", [])

    total_credits = 0
    total_usd = 0
    rows = []

    for seg in segments:
        sid = seg.get("id", "?")
        seg_type = seg.get("type", "")
        tool = normalize_tool(seg.get("tool", ""))
        duration = seg.get("duration", 0)
        c = credits_for_segment(seg)
        usd = 0
        if c is None:
            cost_str = "varies"
        elif c == 0:
            cost_str = "$0"
        else:
            cost_str = f"{c} credits"
            total_credits += c
        rows.append({
            "id": sid,
            "type": seg_type,
            "tool": tool,
            "duration": duration,
            "cost": cost_str,
        })

    plan_balance = args.plan_balance if args.plan_balance is not None else PLANS.get(args.plan, 200)
    after_balance = plan_balance - total_credits

    # Build markdown report
    lines = [
        "# Cost estimate",
        "",
        f"**Storyboard:** `{args.storyboard}`",
        f"**Plan:** {args.plan}",
        "",
        "## Per-segment breakdown",
        "",
        "| # | Type | Tool | Duration | Cost |",
        "|---|------|------|----------|------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['type']} | {r['tool']} | {r['duration']}s | {r['cost']} |"
        )

    lines.extend([
        "",
        "## Totals",
        "",
        f"- **HeyGen Premium Credits**: {total_credits}",
        f"- **HyperFrames render**: $0",
        f"- **Perplexity research (already spent in Phase 2)**: ${args.perplexity_already_spent}",
        f"- **Lark upload**: $0",
        "",
        "## Plan impact",
        "",
        f"- Starting balance: {plan_balance} credits",
        f"- This run: -{total_credits}",
        f"- After this run: **{after_balance} credits remaining**",
    ])

    if after_balance < 0:
        lines.extend([
            "",
            "⚠️  **WARNING: Insufficient credits.** Either:",
            f"  - Buy a 300-credit Premium Pack ($15) — covers this and {300 - total_credits + after_balance} more",
            "  - Reduce video length / replace Video Agent segments with HyperFrames",
            "  - Upgrade to Pro plan ($99/mo, 2000 credits)",
        ])
    elif after_balance < 50:
        lines.extend([
            "",
            f"ℹ️  Note: only {after_balance} credits will remain after this run. Plan accordingly.",
        ])

    md = "\n".join(lines)
    Path(args.out).write_text(md)

    print(md)
    print(f"\n[Cost estimate saved to {args.out}]", file=sys.stderr)


if __name__ == "__main__":
    main()
