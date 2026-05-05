# Production techniques — Phase 4 patterns

Battle-tested patterns for the production phase. Use these when the storyboard calls for them.

---

## 1. Animated text overlays without `drawtext`

Many ffmpeg builds (esp. Homebrew on macOS) ship without libfreetype, so `drawtext` is unavailable. The reliable cross-platform fallback is **PIL → PNG → ffmpeg overlay**.

**Pattern:** render N cumulative RGBA PNG frames at the video resolution, overlay them with time-gated `enable=` expressions.

```python
from PIL import Image, ImageDraw, ImageFont

annotations = ["Low polygon count", "Stretched textures", "Jagged silhouette"]
fnt = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 40)

# Three cumulative overlays — N=1 shows label 1, N=2 shows 1+2, N=3 shows all
for n in (1, 2, 3):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(n):
        x, y = 32, 110 + i * 78
        # Red dot
        d.ellipse([(x, y + 20), (x + 16, y + 36)], fill=(255, 90, 90, 255))
        # Text with stroke for legibility against any background
        d.text((x + 30, y), annotations[i], font=fnt,
               fill=(255, 235, 235, 255),
               stroke_width=3, stroke_fill=(0, 0, 0, 230))
    img.save(f"anno_{n}.png")
```

Then overlay via ffmpeg with stagger timing:

```bash
ffmpeg -y -i base.mp4 -i anno_1.png -i anno_2.png -i anno_3.png \
  -filter_complex "
    [0:v][1:v]overlay=0:0:enable='between(t,0.4,1.4)'[v1];
    [v1][2:v]overlay=0:0:enable='between(t,1.4,2.2)'[v2];
    [v2][3:v]overlay=0:0:enable='between(t,2.2,3.5)'[v]
  " -map "[v]" -map 0:a ...
```

### Annotation styling

- **Skip border boxes.** They're hard to size correctly (text overflows) and look heavy on cinematic content.
- Default style: a colored bullet/dot + text with a 3px black stroke outline. Reads cleanly over any video.
- Bullet color signals tone: red for problems / criticisms, green for wins, blue/cyan for neutral facts.

---

## 2. Split-screen B-roll: cinematic + data

When a narrative beat calls for both a cinematic moment AND structured data (benchmark numbers, comparison stats, feature list), compose a horizontal split: cinematic on the left, data panel on the right.

**Layout (9:16 portrait 720×1280):**

```
┌─────────────┬─────────────┐
│ 360×1280    │ 360×1280    │
│ cinematic   │ HF data     │
│ (Seedance)  │ (PIL+ffmpeg)│
└─────────────┴─────────────┘
```

**ffmpeg pattern:**

```bash
ffmpeg -y -i seedance_clip.mp4 -i hf_data_panel.mp4 -i vo.wav \
  -filter_complex "
    [0:v]scale=360:640,pad=360:1280:0:320:color=0x0F0F12,setsar=1,fps=25[left];
    [1:v]scale=360:1280,setsar=1,fps=25[right];
    [left][right]hstack=inputs=2[v];
    [2:a]apad=whole_dur=5.04[a]
  " -map "[v]" -map "[a]" ...
```

### Letterbox vs crop on the cinematic side

If the cinematic source is 720×1280 portrait but needs to fit a 360-wide panel, you have two options:

- **Crop center column** (`crop=360:1280:180:0`) — fills the full panel height, but cuts off horizontal detail. Use only when the subject is centered AND vertically dominant.
- **Scale + letterbox** (`scale=360:640,pad=360:1280:0:320`) — preserves the entire frame but the subject is half-height. Use whenever the subject extends horizontally or has any cropping risk.

**Default to letterbox.** Crop almost always loses something the user wanted to see.

---

## 3. Wordmark / brand reveal animation

For a moment that needs an emphasis text reveal (brand name, key claim, product name) over an existing video segment, pre-render a PIL animation as a PNG sequence and composite via ffmpeg `-itsoffset` + image2 demuxer.

```python
# render_wordmark.py — generates 62 RGBA PNGs (2.5s @ 25fps)
# Animation: scale-in 0.5→1.05 with back-out (0–0.4s), hold (0.4–1.5s),
#            fade-out + slight zoom-out (1.5–2.5s)
# Glow halo from multiple Gaussian-blurred copies of the text
```

```bash
ffmpeg -y -i video.mp4 \
  -framerate 25 -itsoffset 8.0 -i 'wordmark_frames/frame_%04d.png' \
  -filter_complex "[0:v][1:v]overlay=x=0:y=0:eof_action=pass[v]" \
  -map "[v]" -map 0:a ...
```

`-itsoffset 8.0` shifts the PNG sequence by 8 seconds, so the wordmark first appears at t=8 in the output. `eof_action=pass` keeps the base video showing after the wordmark frames run out.

Sync the wordmark to a meaningful audio cue: a key word in the avatar's line, a beat drop in the music, or a transition between two B-roll clips.

---

## 4. Seedance frame-rate alignment

Seedance always returns video at **24 fps**. HeyGen avatar videos are at **25 fps**. ffmpeg `concat` filter handles mismatched framerates (re-encodes to a common rate), but `concat -c copy` does not.

**Always re-encode each Seedance clip to 25 fps before concat:**

```bash
ffmpeg -y -i seedance_input.mp4 -i tts_audio.wav \
  -c:v libx264 -pix_fmt yuv420p -r 25 -preset fast -crf 20 \
  -c:a aac -b:a 192k -ar 48000 \
  -filter_complex "[1:a]apad=whole_dur=5.04[a]" -map 0:v -map "[a]" -t 5.04 \
  seedance_25fps.mp4
```

---

## 5. TTS-first segment timing

The original storyboard durations are estimates; the actual HeyGen TTS output may run longer or shorter. Always:

1. Submit HeyGen TTS first.
2. Read `duration` from the response (e.g., 2.93s for "Looks great. Until you subdivide.").
3. Size the visual segment to `tts_duration + 0.4s` breathing room.
4. Update `storyboard.json` with the actual duration so cost/length stays accurate.

For A-roll videos, the avatar render duration is determined by HeyGen's TTS internally — read it back from `get_video.duration` and update the timeline accordingly.

---

## 6. Seedance content-policy avoidance

Seedance frequently returns `OutputVideoSensitiveContentDetected.PolicyViolation` for prompts that look like character IP. Failure-prone subjects:

- ❌ Humanoid robots, mech-style figures, anime characters
- ❌ Vehicles or props that look like specific brands
- ❌ Fictional characters or stylized creatures

Reliable subjects:

- ✅ Industrial machinery (six-axis robotic arms, gears, mechanical joints)
- ✅ Abstract geometric sculptures with clear "original" framing
- ✅ Generic mechanical/architectural details (panels, bolts, brushed metal)

**If a Seedance task fails with the policy code:** simplify the subject toward generic engineering. Add explicit disclaimers in the prompt: "no logos, no text overlays, original generic design, no IP, no brand markings."

---

## 7. Cinematic + benchmark visualization combos

When the storyboard calls for "show numbers AND deliver a cinematic moment", combine a Seedance clip with a HyperFrames data panel using the split-screen pattern above. Examples:

- **Win-rate benchmark**: cinematic product shot left, animated bar chart right
- **Before/after**: low-quality Seedance left (with annotations), beauty render right
- **Feature lineup**: feature spotlight Seedance left, feature list HF panel right

For benchmark bars specifically, use a **two-color segmented bar** (green = your product wins, red = competitor wins) with model labels positioned semantically — your label on the left over green, competitor name on the right over red. Show absolute percentages inside each segment.

---

## 8. Audio mix: sidechain ducking by default

See `references/volcengine-music-api.md` for the full pattern. Key points:

- Always sidechain-duck the music against the voice track. Static-volume mixing always compromises one direction.
- Settings that work across most TikTok/Shorts content: `threshold=0.03 ratio=10 attack=10 release=300`.
- Verify: voice should land near -18 dB RMS, music-only gaps near -22 to -28 dB.

---

## 9. Concat strategy: filter, not demuxer

Always use the **concat filter** (re-encodes) for the final assembly when stitching segments from different sources (HeyGen + Seedance + HyperFrames + TTS).

**Why not `-c copy`:**
- AAC frame-boundary clicks → perceived as cut-offs at segment seams
- Mismatched framerates can cause freezing
- Different encoder configs lead to subtle audio glitches

```bash
ffmpeg -y -i s1.mp4 -i s2.mp4 -i s3.mp4 ... \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]...concat=n=N:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 \
  -c:a aac -b:a 192k -ar 48000 \
  /tmp/concat_clean.mp4
```

CRF 18 is visually lossless on the source quality these segments come from.

Then mix music as a final pass with `-c:v copy` (no further video re-encode):

```bash
ffmpeg -y -i /tmp/concat_clean.mp4 -i music_bed.m4a \
  -filter_complex "[0:a]asplit=2[trig][out];[1:a]volume=0.5[m];
    [m][trig]sidechaincompress=threshold=0.03:ratio=10:attack=10:release=300:makeup=1[ducked];
    [out][ducked]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 \
  dist/main.mp4
```

---

## 10. Iterative refinement loop

Phase 4 production is rarely one-shot. Plan for 2–3 iterations:

1. **First pass**: storyboard timings often turn out wrong because TTS durations differ from estimates. Adjust segment lengths to match actual TTS.
2. **Sync pass**: voice not lining up with footage → check that A-roll videos aren't being re-encoded unnecessarily; check AAC boundary handling on concat.
3. **Visual polish**: text overflowing boxes, animation timing, music too loud/soft, content not matching narration.
4. **Content quality**: pain-point demos may need to be more concrete; cinematic shots may need to be more closely tied to the talking head.

Save every paid asset in `assets/` so iterations don't re-spend credits. Save the storyboard.json after each change so cost tracking stays accurate.

---

## File naming conventions

```
~/projects/<slug>-video/
  product-brief.md
  research.md
  storyboard.md
  storyboard.json
  scripts/
    render_broll.py            # static HF B-roll
    render_benchmark_panel.py  # data viz for split-screen
    render_wordmark.py         # brand reveal frames
  assets/
    aroll-N.mp4                # HeyGen avatar segments
    broll-segN-silent.mp4      # Seedance / HF intermediate
    broll-segN.mp4             # post-VO-merge B-roll
    vo-segN.wav                # HeyGen TTS audio
    benchmark_panel.mp4        # HF panel videos
    music_volc_raw.wav         # raw Volcengine output
    music_volc.m4a             # trimmed + faded music bed
    anno_N.png                 # annotation overlays
    wordmark_frames/           # brand reveal PNG sequence
  dist/
    main.mp4                   # final output
```
