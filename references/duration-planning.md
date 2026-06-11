# Duration planning

Do not pick duration by habit. Pick it from audience, content density, and proof burden.

Use `scripts/plan_duration.py` as a quick first pass:

```bash
python3 scripts/plan_duration.py product-brief.md --audience external --format 16:9
```

## Heuristics

| Content profile | Suggested duration |
|---|---|
| One message, one CTA, low proof burden | 25-45s |
| 2-4 features, light demo/proof | 60-90s |
| Customer overview with demos + benchmarks + pricing | 120-180s |
| Internal enablement with many details | 180-240s |

## Add time for comprehension

Add time when the viewer needs to read or compare:

- Benchmark chart: +6-10s per major chart.
- Dense pricing comparison: +8-12s.
- Multi-video demo grid: +8-15s.
- Customer logo/use-case page: +6-8s.

## Narration pacing

| Use | Pace |
|---|---|
| Title / positioning | 120-135 wpm |
| Feature walkthrough | 130-145 wpm |
| Benchmark interpretation | 105-125 wpm |
| Summary / CTA | 115-130 wpm |

If TTS audio is generated, actual audio duration wins over the estimate. Update the scene
duration rather than time-stretching the voice, unless the change is under about 3%.

## Intelligent duration workflow

1. Count distinct proof objects: demos, benchmark charts, pricing tables, customer cases.
2. Pick target audience and format.
3. Run `scripts/plan_duration.py`.
4. Draft storyboard against the target range.
5. Generate TTS and measure actual durations.
6. Rebalance scene holds so the final video lands inside the range.

## Approval language

When presenting the storyboard, say:

> Recommended length: 150s, with a safe range of 120-180s. This is longer than a short
> launch reel because the video needs time for demo footage, benchmark interpretation,
> and pricing comparison without forcing the voice-over to rush.
