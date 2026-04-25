#!/usr/bin/env python3
"""Generate speech with a previously-created ElevenLabs Instant Voice Clone.

Usage:
    python speak_ivc.py --text "Hello from Termux"
    python speak_ivc.py --text "Hola" --voice-id ABC123 --out output/hola.mp3
    python speak_ivc.py --text-file speech.txt --model eleven_multilingual_v2
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config" / "voice.json"
OUTPUT_DIR = SCRIPT_DIR / "output"
ENV_PATH = SCRIPT_DIR / ".env"


def load_env() -> None:
    if not ENV_PATH.is_file():
        return
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Speak text with an ElevenLabs IVC voice.")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to speak.")
    group.add_argument("--text-file", help="Path to a UTF-8 text file.")
    p.add_argument("--voice-id", help="Override voice id (defaults to config/voice.json).")
    p.add_argument(
        "--model",
        default=os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        help="ElevenLabs model id (default: eleven_multilingual_v2).",
    )
    p.add_argument("--out", help="Output MP3 path (default: output/<timestamp>.mp3).")
    p.add_argument(
        "--output-format",
        default="mp3_44100_128",
        help="ElevenLabs output_format (default: mp3_44100_128).",
    )
    return p.parse_args()


def resolve_voice_id(cli_voice_id: str | None) -> str | None:
    if cli_voice_id:
        return cli_voice_id
    env_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if env_id:
        return env_id
    if CONFIG_PATH.is_file():
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            if isinstance(cfg, dict):
                vid = cfg.get("default_voice_id")
                if vid:
                    return vid
        except json.JSONDecodeError:
            pass
    return None


def main() -> int:
    load_env()
    args = parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("[speak][err] ELEVENLABS_API_KEY is not set.", file=sys.stderr)
        return 2

    voice_id = resolve_voice_id(args.voice_id)
    if not voice_id:
        print(
            "[speak][err] No voice id available. Pass --voice-id, set ELEVENLABS_VOICE_ID, "
            "or run create_ivc.py first.",
            file=sys.stderr,
        )
        return 2

    if args.text is not None:
        text = args.text
    else:
        text = Path(args.text_file).read_text(encoding="utf-8")
    if not text.strip():
        print("[speak][err] Empty text.", file=sys.stderr)
        return 2

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        print(f"[speak][err] elevenlabs package not importable: {exc}", file=sys.stderr)
        return 1

    client = ElevenLabs(api_key=api_key)

    if args.out:
        out_path = Path(args.out)
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUT_DIR / f"speak_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[speak] voice_id={voice_id} model={args.model}")
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=args.model,
        text=text,
        output_format=args.output_format,
    )

    with out_path.open("wb") as fh:
        for chunk in audio_iter:
            if chunk:
                fh.write(chunk)

    size = out_path.stat().st_size
    if size == 0:
        print(f"[speak][err] Wrote empty file: {out_path}", file=sys.stderr)
        return 1
    print(f"[speak] Wrote {out_path} ({size} bytes)")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
