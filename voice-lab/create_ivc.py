#!/usr/bin/env python3
"""Create an ElevenLabs Instant Voice Clone from one or more sample files.

Usage:
    python create_ivc.py --name "MyVoice" sample1.mp3 [sample2.mp3 ...]
    python create_ivc.py --name "MyVoice" --description "calm baritone" prepared/*.mp3

Reads the API key from $ELEVENLABS_API_KEY (or a sibling .env file).
Saves the returned voice id into config/voice.json; never writes secrets to disk.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config" / "voice.json"
ENV_PATH = SCRIPT_DIR / ".env"


def load_env() -> None:
    """Minimal .env loader so we don't hard-require python-dotenv to be importable."""
    if not ENV_PATH.is_file():
        return
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create an ElevenLabs Instant Voice Clone.")
    p.add_argument("--name", required=True, help="Name for the cloned voice.")
    p.add_argument("--description", default="", help="Optional voice description.")
    p.add_argument("--labels", default="", help='Optional labels as JSON, e.g. {"accent":"us"}')
    p.add_argument(
        "--config",
        default=str(CONFIG_PATH),
        help=f"Path to voice config JSON (default: {CONFIG_PATH}).",
    )
    p.add_argument("files", nargs="+", help="Sample audio files (mp3/wav/m4a/...).")
    return p.parse_args()


def main() -> int:
    load_env()
    args = parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print(
            "[create_ivc][err] ELEVENLABS_API_KEY is not set. "
            "Copy .env.example to .env and fill it in, or `export ELEVENLABS_API_KEY=...`.",
            file=sys.stderr,
        )
        return 2

    sample_paths = [Path(f) for f in args.files]
    missing = [str(p) for p in sample_paths if not p.is_file()]
    if missing:
        print(f"[create_ivc][err] Missing sample files: {missing}", file=sys.stderr)
        return 2

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        print(
            f"[create_ivc][err] elevenlabs package not importable: {exc}. "
            "Activate the voice-lab venv or `pip install elevenlabs`.",
            file=sys.stderr,
        )
        return 1

    labels = None
    if args.labels:
        try:
            labels = json.loads(args.labels)
        except json.JSONDecodeError as exc:
            print(f"[create_ivc][err] --labels is not valid JSON: {exc}", file=sys.stderr)
            return 2

    client = ElevenLabs(api_key=api_key)

    # Open all sample files as binary handles; ElevenLabs SDK accepts a list of files.
    file_handles = [p.open("rb") for p in sample_paths]
    try:
        print(f"[create_ivc] Uploading {len(file_handles)} sample(s) as '{args.name}'...")
        voice = client.voices.ivc.create(
            name=args.name,
            description=args.description or None,
            files=file_handles,
            labels=labels,
        )
    finally:
        for fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass

    voice_id = getattr(voice, "voice_id", None) or getattr(voice, "id", None)
    if not voice_id:
        print(f"[create_ivc][err] Unexpected response, no voice_id: {voice!r}", file=sys.stderr)
        return 1

    config_path = Path(args.config)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(config_path.read_text()) if config_path.is_file() else {}
        if not isinstance(existing, dict):
            existing = {}
    except json.JSONDecodeError:
        existing = {}

    existing.setdefault("voices", {})
    existing["voices"][args.name] = {
        "voice_id": voice_id,
        "description": args.description,
        "sample_files": [str(p) for p in sample_paths],
    }
    existing["default_voice_id"] = voice_id
    existing["default_voice_name"] = args.name
    config_path.write_text(json.dumps(existing, indent=2) + "\n")

    print(f"[create_ivc] voice_id: {voice_id}")
    print(f"[create_ivc] Saved to {config_path}")
    print("[create_ivc] Next: python speak_ivc.py --text \"Hello world\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
