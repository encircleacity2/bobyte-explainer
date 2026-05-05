#!/usr/bin/env python3
"""
Orchestrator for Phase 4 — production execution.

This is mostly a guide / scaffold. The actual MCP calls happen through Claude Code,
not from this script (Python can't directly invoke Claude Code MCP tools).

What this script DOES do:
  - Validates that all assets/*.mp4 files exist
  - Generates a HyperFrames composition (index.html) from storyboard.json
  - Runs npm run check + npm run render
  - Produces dist/main.mp4

The MCP calls (create_video_from_avatar, create_video_agent) are handled by Claude
Code following SKILL.md Phase 4 instructions, NOT this script.

Usage:
    # After all HeyGen-generated MP4s are in place:
    python3 compose_and_render.py storyboard.json
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def validate_assets(storyboard, project_root):
    """Check all required MP4 files exist and are non-empty."""
    missing = []
    empty = []
    assets_dir = project_root / "assets"

    for seg in storyboard["segments"]:
        if seg.get("tool") in ("hyperframes",):
            continue  # programmatic, no MP4 needed
        sid = seg["id"]
        mp4 = assets_dir / f"{sid}.mp4"
        if not mp4.exists():
            missing.append(str(mp4))
        elif mp4.stat().st_size < 1024:
            empty.append(str(mp4))

    return missing, empty


def generate_composition(storyboard, project_root, template_path):
    """
    Generate index.html from storyboard.json + template.

    The template has placeholder markers we replace with real segments.
    For complex animations the user / Claude Code may need to hand-edit afterwards.
    """
    template = template_path.read_text()
    total_duration = storyboard.get("total_duration", 15.0)

    elements = []
    timeline = []

    for seg in storyboard["segments"]:
        sid = seg["id"]
        start = seg["start"]
        duration = seg["duration"]
        tool = seg.get("tool", "")
        seg_type = seg.get("type", "")

        if seg_type == "a-roll" or tool == "heygen-avatar":
            # Insert <video> + <audio> for an A-roll segment
            mp4 = f"assets/{sid}.mp4"
            elements.append(f"""
      <video id="{sid}" class="clip" data-start="{start}" data-duration="{duration}"
             data-track-index="1" src="{mp4}" muted></video>
      <audio id="{sid}-audio" class="clip" data-start="{start}" data-duration="{duration}"
             data-track-index="3" src="{mp4}"></audio>""")
            cap = seg.get("caption")
            if cap:
                cap_start = seg.get("caption_start", start + 0.3)
                cap_dur = seg.get("caption_duration", duration - 0.5)
                elements.append(f"""
      <div id="{sid}-caption" class="clip caption" data-start="{cap_start}"
           data-duration="{cap_dur}" data-track-index="2">
        <span class="caption-bg">{cap}</span>
      </div>""")
                timeline.append(
                    f'      tl.from("#{sid}-caption", {{opacity: 0, y: 30, duration: 0.4}}, {cap_start});\n'
                    f'      tl.to("#{sid}-caption", {{opacity: 0, duration: 0.2}}, {cap_start + cap_dur - 0.2});\n'
                    f'      tl.set("#{sid}-caption", {{opacity: 0}}, {cap_start + cap_dur});'
                )

        elif tool == "heygen-video-agent" or seg_type == "b-roll-video-agent":
            mp4 = f"assets/{sid}.mp4"
            elements.append(f"""
      <video id="{sid}" class="clip" data-start="{start}" data-duration="{duration}"
             data-track-index="1" src="{mp4}" muted></video>""")
            cap = seg.get("caption")
            if cap:
                cap_start = seg.get("caption_start", start + 0.3)
                cap_dur = seg.get("caption_duration", duration - 0.5)
                elements.append(f"""
      <div id="{sid}-caption" class="clip caption" data-start="{cap_start}"
           data-duration="{cap_dur}" data-track-index="2">
        <span class="caption-bg">{cap}</span>
      </div>""")
                timeline.append(
                    f'      tl.from("#{sid}-caption", {{opacity: 0, y: 30, duration: 0.4}}, {cap_start});\n'
                    f'      tl.to("#{sid}-caption", {{opacity: 0, duration: 0.2}}, {cap_start + cap_dur - 0.2});\n'
                    f'      tl.set("#{sid}-caption", {{opacity: 0}}, {cap_start + cap_dur});'
                )

        elif tool == "hyperframes":
            # This is where we'd render programmatic scene from spec.
            # For complex specs, leave a stub the user/Claude Code edits manually.
            elements.append(f"""
      <!-- HYPERFRAMES_SCENE id={sid} duration={duration} -->
      <div id="{sid}" class="clip hyperframes-scene"
           data-start="{start}" data-duration="{duration}" data-track-index="1"
           style="background:#0a0a0a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:32px;">
        <!-- TODO: implement scene per storyboard spec -->
        Scene {sid}: {seg.get('intent', '')[:50]}
      </div>""")

    # Inject into template
    template = template.replace("<!-- ELEMENTS_PLACEHOLDER -->", "\n".join(elements))
    template = template.replace("// TIMELINE_PLACEHOLDER", "\n".join(timeline))
    template = template.replace("DURATION_PLACEHOLDER", str(total_duration))

    out_path = project_root / "index.html"
    out_path.write_text(template)
    print(f"✓ Generated {out_path}")


def run_lint(project_root):
    print("Running lint...")
    r = subprocess.run(["npm", "run", "check"], cwd=project_root,
                       capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return False
    return True


def run_render(project_root):
    print("Running render (this may take 2-4 min)...")
    r = subprocess.run(["npm", "run", "render"], cwd=project_root)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard", help="Path to storyboard.json")
    ap.add_argument("--project-root", default=".", help="HyperFrames project root")
    ap.add_argument("--template",
                    help="Path to hyperframes-template.html (defaults to ./assets/hyperframes-template.html)")
    ap.add_argument("--skip-validate", action="store_true",
                    help="Skip MP4 file existence check")
    ap.add_argument("--skip-render", action="store_true",
                    help="Generate composition only, don't render")
    args = ap.parse_args()

    storyboard = json.loads(Path(args.storyboard).read_text())
    project_root = Path(args.project_root).resolve()

    template_path = (Path(args.template) if args.template
                     else project_root / "assets" / "hyperframes-template.html")
    if not template_path.exists():
        # try repo path as fallback
        template_path = Path(__file__).parent.parent / "assets" / "hyperframes-template.html"
    if not template_path.exists():
        print(f"ERROR: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    if not args.skip_validate:
        missing, empty = validate_assets(storyboard, project_root)
        if missing:
            print(f"ERROR: missing MP4 files (Phase 4 step 3-4 incomplete):", file=sys.stderr)
            for m in missing:
                print(f"  - {m}", file=sys.stderr)
            sys.exit(1)
        if empty:
            print(f"ERROR: empty MP4 files:", file=sys.stderr)
            for m in empty:
                print(f"  - {m}", file=sys.stderr)
            sys.exit(1)

    generate_composition(storyboard, project_root, template_path)

    if args.skip_render:
        print("Composition generated. Run `npm run check && npm run render` manually.")
        return

    if not run_lint(project_root):
        print("Lint failed. Fix errors above.", file=sys.stderr)
        sys.exit(1)

    if not run_render(project_root):
        print("Render failed.", file=sys.stderr)
        sys.exit(1)

    print("\n✓ Production complete. Output: dist/main.mp4")


if __name__ == "__main__":
    main()
