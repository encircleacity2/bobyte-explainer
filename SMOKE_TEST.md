# Smoke test guide — explainer-video skill (post 12-PR refactor)

Quick tests to verify each wave works before deciding which PRs to push to GitHub.

## Setup

For Codex installs, use:

```bash
export SKILL_DIR="${HOME}/.codex/skills/explainer-video"
git -C "$SKILL_DIR" pull --ff-only
```

For Claude Code installs, replace the first line with:

```bash
export SKILL_DIR="${HOME}/.claude/skills/explainer-video"
```

```bash
# Confirm files exist
ls "$SKILL_DIR/scripts/audit_storyboard.py"
ls "$SKILL_DIR/scripts/fetch_registry.py"
ls "$SKILL_DIR/scripts/validate_overflow.py"
ls "$SKILL_DIR/scripts/synthesize_screen_ui.py"
ls "$SKILL_DIR/scripts/beat_align.py"
ls "$SKILL_DIR/templates/agent-chip-row.html"
ls "$SKILL_DIR/templates/openai-product-demo.json"
ls "$SKILL_DIR/assets/style-presets/openai-clean/design.md"
ls "$SKILL_DIR/assets/macos-window-chrome.html"
```

All 9 should exist after the refactor.

## Codex regression tests

### BytePlus TTS streaming JSON decodes to audio

```bash
cd "$SKILL_DIR"
python3 - <<'EOF'
import base64
from scripts.generate_tts import decode_byteplus_tts_payload

payload = (
    b'{"code":0,"message":"","data":"'
    + base64.b64encode(b"ID3demo-audio")
    + b'"}\n{"code":20000000,"message":"OK","data":null}\n'
)
assert decode_byteplus_tts_payload(payload) == b"ID3demo-audio"
print("ok")
EOF
```

Expected: `ok`. If this fails, Codex may write JSON bytes as `.mp3` and later
ship a silent or broken video.

### Renderer refuses placeholder B-roll scenes

```bash
cd "$SKILL_DIR"
cat > /tmp/stub-scene-storyboard.json <<'EOF'
{
  "mode": "pure-broll-product-demo",
  "aspect_ratio": "16:9",
  "total_duration": 3,
  "segments": [
    {
      "id": "s1",
      "start": 0,
      "duration": 3,
      "type": "title-card",
      "tool": "hyperframes",
      "intent": "This should not render as a placeholder"
    }
  ]
}
EOF
python3 scripts/compose_and_render.py /tmp/stub-scene-storyboard.json \
  --project-root /tmp --skip-validate --skip-render
```

Expected: exits non-zero with `Missing scene_html/html`. This is intentional:
agents must author real scene HTML/GSAP or use a custom `index.html`.

## Wave 1 tests (PRs 2, 9, 7, 11)

### PR #2 — render at 60fps

```bash
python3 ~/.claude/skills/explainer-video/scripts/compose_and_render.py --help | grep -A1 fps
```

Expected: `--fps` defaults to 60.

### PR #7 + #11 — storyboard auditor

Make a tiny storyboard that's intentionally bad and run the auditor:

```bash
cat > /tmp/bad-storyboard.json << 'EOF'
{
  "mode": "pure-broll-product-demo",
  "style_preset": "openai-clean",
  "channel": "x",
  "aspect_ratio": "1:1",
  "content_profile": "single-message",
  "total_duration": 60,
  "segments": [
    {"id": "open", "type": "title-card", "tool": "hyperframes", "start": 0, "duration": 4, "intent": "Hello"},
    {"id": "long-dead", "type": "device-mockup", "tool": "hyperframes", "start": 4, "duration": 50, "intent": "lots of empty time", "beats": [{"at": 5, "name": "one"}]},
    {"id": "aroll-violation", "type": "a-roll", "tool": "seedance", "start": 54, "duration": 6, "intent": "shouldn't be here in pure-broll mode"}
  ]
}
EOF

python3 ~/.claude/skills/explainer-video/scripts/audit_storyboard.py /tmp/bad-storyboard.json
```

Expected: warnings about (a) total 60s over single-message target by >30%, (b) dead air in long-dead segment, (c) A-roll in pure-broll mode.

### PR #9 — agent-list reference

```bash
cat ~/.claude/skills/explainer-video/references/agent-list.md | grep -c "^|"
```

Expected: ~12+ rows in the agent table.

## Wave 2 tests (PRs 4, 1, 12)

### PR #4 — registry fetch + cache

```bash
python3 ~/.claude/skills/explainer-video/scripts/fetch_registry.py --type block | head -30
```

Expected: prints registry items grouped by type; cache lands at `~/.explainer-video/registry-cache.json`.

```bash
python3 ~/.claude/skills/explainer-video/scripts/fetch_registry.py --name caption
```

Expected: just caption-* items.

### PR #1 + #12 — preflight in actual skill invocation

This is the integration test. Trigger the skill via Claude Code:

> "Make me a 30-second 1:1 video for X about <some product>, openai-clean style."

Expected behavior in Claude's response:
- Phase 1 asks the 3 preflight questions (or absorbs the answers from the prompt)
- Storyboard.json contains `mode`, `style_preset`, `channel`, `aspect_ratio` top-level fields
- Phase 3 shows the design context line ("This storyboard targets X at 1:1 using openai-clean...")
- The Phase 3 cost estimate omits Seedance line items (pure-broll mode)

### PR #12 — style presets exist

```bash
for p in openai-clean anthropic-warm linear-minimal apple-keynote brand-bold; do
  echo "--- $p ---"
  grep -E "^bg_primary|^accent" ~/.claude/skills/explainer-video/assets/style-presets/$p/design.md
done
```

Expected: each preset's design.md has bg_primary + accent declared.

## Wave 3 tests (PRs 3, 6, 5)

### PR #3 — caption components doc

```bash
grep -c "caption-" ~/.claude/skills/explainer-video/references/caption-components.md
```

Expected: 15+ caption-* references (4 starter set + 12 others).

### PR #6 — overflow validator

Use an existing rendered MP4 (e.g. the v4 demo):

```bash
python3 ~/.claude/skills/explainer-video/scripts/validate_overflow.py \
  /Users/bojsun/Downloads/bobyte-explainer-demo-v4.mp4 \
  --at 5,10,15,20,25,30
```

Expected: outputs OK or FAIL with timestamped edge intrusions. (The v4 demo will FAIL with 8px margin warnings — that's known and documented.)

### PR #5 — recipe template + screen synth script exists

```bash
cat ~/.claude/skills/explainer-video/templates/openai-product-demo.json | python3 -m json.tool > /dev/null && echo "valid JSON"
python3 ~/.claude/skills/explainer-video/scripts/synthesize_screen_ui.py --help | head -10
```

Expected: JSON valid; help text shows --mode llm / raw-screenshots.

## Wave 4 tests (PRs 8, 10)

### PR #8 — meta-output beat doc

```bash
grep -E "^## " ~/.claude/skills/explainer-video/references/meta-output-beat.md
```

Expected: sections on multi-shot, two strategies, QT chrome, per-preset, when-not-to-use.

### PR #10 — beat-sync dry-run

```bash
# librosa is heavy; install only if you want to actually test
# pip install --user librosa numpy soundfile

python3 ~/.claude/skills/explainer-video/scripts/beat_align.py --help | head -10
```

Expected: help text. If you have a storyboard.json + music_bed.m4a from a previous render:

```bash
python3 ~/.claude/skills/explainer-video/scripts/beat_align.py \
  storyboard.json assets/music_bed.m4a --dry-run
```

Expected: lists snapped timings (or "librosa not installed; skipping" — graceful).

## Wave 5 tests (validation suite + auto-fix loop)

### Individual validators on a cleaned recipe

```bash
cd ~/.claude/skills/explainer-video
python3 - << 'EOF'
import json
sb = json.load(open('templates/openai-product-demo.json'))
repls = {
    "REPLACE: who is the viewer / what role-and-situation": "Erica, an engineering lead preparing a launch",
    "REPLACE: specific friction this product solves": "Launch updates are scattered across docs, commits, and screenshots",
    "REPLACE: the one beat that produces 'oh, that's clever'": "The agent turns a repo plus screenshots into a polished launch video",
    "REPLACE: single sentence to remember 30s later": "Ship the story, not just the screen.",
    "REPLACE: where they go after (url, app store, etc)": "github.com/example/product",
    "REPLACE: a real name (e.g., 'Erica')": "Erica",
    "REPLACE: their role": "Engineering lead",
    "REPLACE: their company / context": "Orbit Labs",
    "REPLACE: 1-line why they care": "Needs a launch asset by end of day",
    "REPLACE: the main artifact (e.g., 'Vertex Labs sync' meeting)": "Orbit launch repo",
    "REPLACE: who the protagonist interacts with": "Maya, product marketing lead",
    "REPLACE: an exact quoted sentence that recurs": "Can we make this feel like a real launch?",
    "REPLACE: a specific document / file / artifact": "launch-notes.md",
    "REPLACE: e.g., 'italic serif quote, same typography'": "lavender highlighted quote, same type treatment",
    "REPLACE: your opening line — sets the situation, not the product": "A launch needs more than a screenshot.",
    "REPLACE: opening line": "A launch needs more than a screenshot",
    "REPLACE: the line that introduces the product as the answer": "Drop in the repo, and the story starts to assemble.",
    "REPLACE: the line that names what just got accomplished": "Now the proof is on screen, timed and ready to share.",
    "REPLACE: the memorable line. Reuse narrative.memorable_line.": "Ship the story, not just the screen.",
    "REPLACE: closing line": "Ship the story, not just the screen",
    "REPLACE: product name": "Orbit",
    "REPLACE: tagline or url": "github.com/example/product",
    "REPLACE": "Maya"
}
def walk(x):
    if isinstance(x, str):
        return repls.get(x, x)
    if isinstance(x, list):
        return [walk(v) for v in x]
    if isinstance(x, dict):
        return {k: walk(v) for k, v in x.items()}
    return x
json.dump(walk(sb), open('/tmp/clean-sb.json', 'w'), indent=2)
EOF
python3 scripts/audit_storyboard.py /tmp/clean-sb.json   # 0 warnings
python3 scripts/check_overlap.py /tmp/clean-sb.json       # 0 findings
python3 scripts/check_assets.py --project-root templates                  # skipped (no index.html)
```

### verify.py orchestrator — clean storyboard

```bash
python3 scripts/verify.py /tmp/clean-sb.json --mode pre
```

Expected: `severe: 0  warnings: 0  auto-fixable: 0`

### Auto-fix loop — deliberately broken storyboard

Make a broken storyboard with overflow + track collision:

```bash
cp /tmp/clean-sb.json /tmp/broken-sb.json
python3 - << 'EOF'
import json
sb = json.load(open('/tmp/broken-sb.json'))
sb['segments'][1]['camera_path'][-1]['scale'] = 1.45            # overflow
sb['segments'][1]['track_index'] = 2; sb['segments'][1]['duration'] = 20  # collision
sb['segments'][2]['track_index'] = 2
json.dump(sb, open('/tmp/broken-sb.json', 'w'), indent=2)
EOF

# Without auto-fix — should find severe overflow/overlap issues
python3 scripts/verify.py /tmp/broken-sb.json --mode pre

# With auto-fix — should converge to 0 severe unless the remaining issue is semantic
python3 scripts/verify.py /tmp/broken-sb.json --mode pre --auto-fix
```

Expected with `--auto-fix`:
```
iteration 1:
  applies cap_camera_scale + move_to_unique_track
iteration 2:
  severe: 0
```

### Post-render validators on an existing MP4

Use any rendered MP4 from earlier iterations:

```bash
python3 scripts/check_render_spec.py \
  templates/openai-product-demo.json \
  /Users/bojsun/Downloads/bobyte-explainer-demo-v4.mp4

python3 scripts/check_audio_levels.py \
  templates/openai-product-demo.json \
  /Users/bojsun/Downloads/bobyte-explainer-demo-v4.mp4
```

Expected: 0 findings (v4 matches the recipe's 1440×1440/60fps/32s spec, audio in -22 to -16 dB target range).

### Integrated pipeline test

When you next run the full skill, `compose_and_render.py` will:
1. Generate composition
2. Run `verify.py --mode pre --auto-fix` → potentially modify storyboard and regenerate composition
3. Render
4. Run `verify.py --mode post --auto-fix` → potentially re-mux audio gain in place
5. Report final status

If you want to opt out: pass `--no-auto-fix` to verify only without repairing, or `--force` to render even when severe issues are present.

## Storyline patterns test (8 patterns from STORYLINE.md)

The auditor enforces 8 narrative patterns. To verify they all trip correctly:

```bash
# Bare storyboard (no narrative metadata) → should fail with 5+ severe findings
cat > /tmp/bare.json <<'EOF'
{ "mode": "pure-broll-product-demo", "aspect_ratio": "1:1",
  "total_duration": 30, "segments": [
    {"id": "s1", "start": 0, "duration": 30, "type": "device-mockup", "tool": "hyperframes"}
  ]}
EOF
python3 ~/.claude/skills/explainer-video/scripts/audit_storyboard.py /tmp/bare.json
```

Expected: warnings/severe findings about missing visual quality bar, motion, layout guardrails, narrative / canon / cast / echo / narration / frame_name. Several are severe and block render.

```bash
# Recipe template with REPLACE: placeholders still in → should fail
python3 ~/.claude/skills/explainer-video/scripts/audit_storyboard.py \
  ~/.claude/skills/explainer-video/templates/openai-product-demo.json
```

Expected: severe findings for unresolved `REPLACE:` placeholders. The recipe is a scaffold; customize it into `/tmp/clean-sb.json` for the clean pass above.

## End-to-end (the full test)

The most useful test: actually trigger the skill on a real input and verify the new flow.

```text
You: "Make a 30s 1:1 X video about <some product>"

Expected Claude response:
  Phase 1 Intake:
    - reads input
    - shows product-brief
    Preflight:
      Q1 mode → auto-suggests pure-broll
      Q2 style → asks (or auto-suggests openai-clean based on context)
      Q3 channel → infers x / 1:1 / 1440×1440 from the input prompt
  Phase 2: skipped (pure-broll mode)
  Phase 3:
    - shows design context line first
    - shows storyboard
    - runs audit_storyboard.py — should be 0 warnings on a clean draft
    - shows cost (just music if enabled, no Seedance)
    - WAITS FOR APPROVAL
  Phase 4 (after approval):
    - installs registry blocks per storyboard
    - generates index.html at 1440×1440 with openai-clean tokens
    - renders at 60fps
    - generates music (if enabled)
    - assembles
  Phase 5: delivers MP4
```

If any of those steps don't happen as expected, that's a bug to investigate. The most likely failure: Claude doesn't read motion-house-style.md / style-presets.md before authoring the composition, producing motion that violates the rules. If that happens, the fix is to make SKILL.md Phase 4 reference those files more aggressively (already does, but may need stronger wording).

## Rollback

Pre-refactor backup:

```bash
rm -rf ~/.claude/skills/explainer-video
cp -r ~/Desktop/Dev/explainer/explainer-video.pre-refactor.bak ~/.claude/skills/explainer-video
```

## Reporting back

After running the tests, if you want to push specific PRs to the GitHub repo:

1. Identify which PRs work cleanly end-to-end
2. Extract their diffs from the changes documented in `CHANGELOG.md`
3. Open a PR per-PR (or grouped per-wave) against `github.com/encircleacity2/bobyte-explainer`

The 4 lowest-risk PRs to ship first (Wave 1) require zero coordination — pick any 1 and push as a standalone PR to validate the workflow.
