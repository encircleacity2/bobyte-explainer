#!/usr/bin/env python3
"""
Pre-flight check for the bobyte-explainer skill.

Verifies all environment dependencies for the 5-phase workflow.
"""
import os
import shutil
import subprocess
import sys


def check(label, ok, hint=""):
    mark = "✓" if ok else "✗"
    line = f"  {mark} {label}"
    if hint and not ok:
        line += f"\n      → {hint}"
    print(line)
    return ok


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "", ""


print("=" * 60)
print("Product-video skill — preflight check")
print("=" * 60)

print("\n[1/4] Local tools")

ok_node, node_v, _ = run(["node", "--version"])
node_major = int(node_v.lstrip("v").split(".")[0]) if ok_node and node_v else 0
check("Node.js v22+", ok_node and node_major >= 22,
      "install Node 22+ from https://nodejs.org")

ok_python = shutil.which("python3") is not None
check("Python 3", ok_python, "install Python 3.8+")

ok_ff, ff_out, _ = run(["ffmpeg", "-version"])
check("ffmpeg", ok_ff, "brew install ffmpeg / apt install ffmpeg")

ok_ffprobe = shutil.which("ffprobe") is not None
check("ffprobe", ok_ffprobe, "comes with ffmpeg")

print("\n[2/4] CLIs")

ok_claude = shutil.which("claude") is not None
check("Claude Code CLI", ok_claude, "install from https://docs.claude.com/en/docs/claude-code/overview")

ok_lark = shutil.which("lark-cli") is not None
check("lark-cli", ok_lark, "npm install -g @larksuite/cli")

print("\n[3/4] MCP servers (via Claude Code)")

if ok_claude:
    ok_mcp, mcp_out, _ = run(["claude", "mcp", "list"], timeout=15)
    has_heygen = "heygen" in mcp_out.lower() if ok_mcp else False
    check("HeyGen MCP server registered", has_heygen,
          "claude mcp add --transport http -s user heygen https://mcp.heygen.com/mcp/v1/")
else:
    print("  (skipped — claude CLI not available)")

print("\n[4/4] Environment variables")

key = os.environ.get("PERPLEXITY_API_KEY", "")
ok_pplx = key.startswith("pplx-") if key else False
check("PERPLEXITY_API_KEY set", ok_pplx,
      "export PERPLEXITY_API_KEY='pplx-...' from https://perplexity.ai/settings/api")
if ok_pplx:
    print(f"      key prefix: {key[:8]}...")

print()
print("=" * 60)

if all([ok_node and node_major >= 22, ok_python, ok_ff, ok_lark, ok_pplx]):
    print("All systems ready. Proceed with Phase 1 (intake).")
else:
    print("Some prerequisites are missing. Fix the items marked ✗ above before continuing.")
    sys.exit(1)
