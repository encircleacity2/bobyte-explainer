#!/usr/bin/env python3
"""
Generate standalone narration audio for explainer-video projects.

Supported providers:
  - byteplus-tts: BytePlus Seed TTS v2 unidirectional endpoint
  - elevenlabs: ElevenLabs text-to-speech endpoint
  - proxy: a compatible internal proxy endpoint

Secrets are read from environment variables or ~/.explainer-video/config.json. The script
never prints full keys. Output is normalized with ffmpeg when available.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests


CONFIG_PATH = Path.home() / ".explainer-video" / "config.json"


def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def read_text_arg(value):
    p = Path(value)
    if p.exists():
        return p.read_text().strip()
    return value.strip()


def key_from_env_or_config(env_name, cfg_name, cfg):
    return os.environ.get(env_name) or cfg.get(cfg_name) or ""


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def normalize_audio(src, dst):
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-af", "loudnorm=I=-18:TP=-2:LRA=9",
        "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
        str(dst),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"warning: audio normalization skipped: {exc}", file=sys.stderr)
        return False


def byteplus_tts(text, speaker, api_key):
    if not api_key:
        raise SystemExit("Missing BytePlus TTS key. Set BYTEPLUS_TTS_API_KEY or config.byteplus_tts_api_key.")
    url = "https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/unidirectional"
    payload = {
        "req_params": {
            "text": text,
            "speaker": speaker,
            "additions": json.dumps({
                "disable_markdown_filter": True,
                "enable_language_detector": True,
                "enable_latex_tn": True,
                "disable_default_bit_rate": True,
                "max_length_to_filter_parenthesis": 0,
                "cache_config": {"text_type": 1, "use_cache": True},
            }, separators=(",", ":")),
            "audio_params": {"format": "mp3", "sample_rate": 24000},
        }
    }
    headers = {
        "x-api-key": api_key,
        "X-Api-Resource-Id": "seed-tts-2.0",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.content, ".mp3"


def elevenlabs_tts(text, voice_id, api_key):
    if not api_key:
        raise SystemExit("Missing ElevenLabs key. Set ELEVENLABS_API_KEY or config.elevenlabs_api_key.")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.48, "similarity_boost": 0.72, "style": 0.18},
    }
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.content, ".mp3"


def proxy_tts(text, speaker, profile, cfg):
    proxy_url = os.environ.get("EXPLAINER_API_PROXY_URL") or cfg.get("api_proxy_url")
    if not proxy_url:
        raise SystemExit("Missing proxy URL. Set EXPLAINER_API_PROXY_URL or config.api_proxy_url.")
    payload = {
        "task": "tts",
        "profile": profile,
        "speaker": speaker,
        "text": text,
        "audio": {"format": "mp3", "sample_rate": 24000},
    }
    r = requests.post(proxy_url.rstrip("/") + "/tts", json=payload, timeout=120)
    r.raise_for_status()
    return r.content, ".mp3"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="Text or path to a text file.")
    ap.add_argument("--out", required=True, help="Output audio path.")
    ap.add_argument("--provider", default="", help="byteplus-tts, elevenlabs, or proxy.")
    ap.add_argument("--speaker", default="", help="Speaker / voice id.")
    ap.add_argument("--profile", default="", help="Proxy/provider profile name.")
    ap.add_argument("--raw", action="store_true", help="Skip ffmpeg loudness normalization.")
    args = ap.parse_args()

    cfg = load_config()
    provider = args.provider or cfg.get("tts_profile") or "byteplus-tts"
    speaker = args.speaker or cfg.get("tts_speaker") or "en_female_stokie_uranus_bigtts"
    profile = args.profile or cfg.get("tts_profile") or provider
    text = read_text_arg(args.text)

    if not text:
        raise SystemExit("TTS text is empty.")

    if provider == "byteplus-tts":
        data, suffix = byteplus_tts(
            text, speaker,
            key_from_env_or_config("BYTEPLUS_TTS_API_KEY", "byteplus_tts_api_key", cfg),
        )
    elif provider == "elevenlabs":
        data, suffix = elevenlabs_tts(
            text, speaker,
            key_from_env_or_config("ELEVENLABS_API_KEY", "elevenlabs_api_key", cfg),
        )
    elif provider == "proxy":
        data, suffix = proxy_tts(text, speaker, profile, cfg)
    else:
        raise SystemExit(f"Unsupported TTS provider: {provider}")

    out = Path(args.out)
    raw_out = out if args.raw else out.with_suffix(".raw" + suffix)
    write_bytes(raw_out, data)
    if args.raw:
        print(str(raw_out))
        return

    if normalize_audio(raw_out, out):
        try:
            raw_out.unlink()
        except OSError:
            pass
        print(str(out))
    else:
        print(str(raw_out))


if __name__ == "__main__":
    main()
