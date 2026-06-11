# Standalone TTS reference

Use standalone TTS when narration should be independent from Seedance A-roll:

- Customer-facing 16:9 overview videos where the visual story is product/demo/benchmark first.
- Benchmark-heavy sections where timing must match charts.
- Videos where A-roll is used only as a light intro/outro, or removed entirely.
- Iterations where the voice needs to be regenerated without re-rendering paid video clips.

## Supported providers

`scripts/generate_tts.py` supports:

| Provider | Profile | Key source | Notes |
|---|---|---|---|
| BytePlus Seed TTS | `byteplus-tts` | `BYTEPLUS_TTS_API_KEY` or `config.byteplus_tts_api_key` | Good default for BytePlus demos. |
| ElevenLabs | `elevenlabs` | `ELEVENLABS_API_KEY` or `config.elevenlabs_api_key` | Use when a more expressive English VO is needed. |
| Internal proxy | `proxy` | `EXPLAINER_API_PROXY_URL` or `config.api_proxy_url` | Best for team-wide key management and provider switching. |

Example:

```bash
python3 scripts/generate_tts.py \
  --provider byteplus-tts \
  --speaker en_female_stokie_uranus_bigtts \
  --text narration/seg01.txt \
  --out assets/audio/seg01.m4a
```

## Timing rules

- Estimate narration at **2.1 to 2.4 English words per second** for calm customer-facing delivery.
- For dense benchmark pages, target **1.7 to 2.0 words per second** and leave 1.0-1.5 s of visual hold time.
- Generate TTS before final timing lock. Use `ffprobe` to read actual audio duration, then update `storyboard.json`.
- Avoid segment-level silence gaps. Either let the next scene start with a visual transition while audio finishes, or add a short intentional hold.

## Audio pipeline

1. Generate one voice file per spoken segment.
2. Normalize each file to about `-18 LUFS` with `ffmpeg loudnorm`.
3. Put voice tracks directly on the HyperFrames timeline whenever possible.
4. Add music only after the full voice/video timeline is complete.
5. Use one continuous sidechain-ducked music bed. Do not splice already-mixed audio from another final video.

This avoids the common failure mode where page 1 and page 2 have different music phase,
different loudness, or an abrupt cut at the boundary.

## Storyboard fields

For TTS-backed segments, include:

```json
{
  "id": "seg03",
  "type": "vo-broll",
  "tool": "hyperframes",
  "voice": {
    "mode": "tts",
    "provider": "byteplus-tts",
    "speaker": "en_female_stokie_uranus_bigtts",
    "script": "The key story is balanced omni-modal capability in a lightweight model.",
    "target_wpm": 130
  }
}
```

## Quality checklist

- [ ] Voice does not end mid-word at the final frame.
- [ ] Dense claims are spoken slower than feature headlines.
- [ ] Every benchmark page has enough time for the viewer to read the key comparison.
- [ ] Music is mixed after voice, not before.
- [ ] TTS outputs are cached in `assets/audio/` so visual iterations do not regenerate paid audio.
