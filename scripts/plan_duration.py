#!/usr/bin/env python3
"""
Recommend an explainer-video duration from content density.

Input can be a product brief markdown file or free-form text. The heuristic is deliberately
simple and explainable so the storyboard approval gate can show why a target length was chosen.
"""
import argparse
import json
import re
from pathlib import Path


KEYWORDS = {
    "feature": ["feature", "capability", "功能", "特点", "能力"],
    "benchmark": ["benchmark", "leaderboard", "score", "eval", "评测", "基准"],
    "demo": ["demo", "workflow", "use case", "case", "场景", "演示", "客户"],
    "pricing": ["pricing", "price", "cost", "token", "成本", "价格"],
}


def read_input(value):
    p = Path(value)
    if p.exists():
        return p.read_text()
    return value


def count_matches(text, terms):
    low = text.lower()
    return sum(low.count(t.lower()) for t in terms)


def recommend(text, audience, format_hint):
    words = re.findall(r"[\w.-]+", text)
    word_count = len(words)
    counts = {name: count_matches(text, terms) for name, terms in KEYWORDS.items()}
    density = sum(min(v, 6) for v in counts.values())

    if word_count < 250 and density <= 3:
        target = 35
        band = "25-45s"
        rationale = "single-message content with low proof density"
    elif word_count < 700 and density <= 9:
        target = 75
        band = "60-90s"
        rationale = "moderate feature/proof density"
    elif audience == "external" or format_hint == "16:9":
        target = 150
        band = "120-180s"
        rationale = "customer-facing overview with multiple proof points"
    else:
        target = 120
        band = "100-140s"
        rationale = "dense internal/product content, but still preview-friendly"

    # Benchmarks and pricing need comprehension time, not just narration time.
    if counts["benchmark"] >= 4:
        target += 20
    if counts["pricing"] >= 2:
        target += 10
    target = min(target, 210 if audience == "external" else 240)

    return {
        "target_seconds": target,
        "recommended_range": band,
        "rationale": rationale,
        "signals": {
            "word_count": word_count,
            "keyword_counts": counts,
            "audience": audience,
            "format": format_hint,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Product brief path or inline text.")
    ap.add_argument("--audience", choices=["external", "internal"], default="external")
    ap.add_argument("--format", choices=["16:9", "9:16"], default="16:9")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    args = ap.parse_args()

    result = recommend(read_input(args.input), args.audience, args.format)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("# Duration recommendation")
    print()
    print(f"- Target: **{result['target_seconds']}s**")
    print(f"- Range: **{result['recommended_range']}**")
    print(f"- Rationale: {result['rationale']}")
    print(f"- Signals: {json.dumps(result['signals'], ensure_ascii=False)}")


if __name__ == "__main__":
    main()
