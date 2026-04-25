#!/usr/bin/env python3
"""Smoke test: synthesize a short phrase in EN/ES/FR/DE through the cloned voice.

Usage:
    python multilingual_test.py
    python multilingual_test.py --voice-id ABC123 --out-dir output/multi
    python multilingual_test.py --languages en,es

Writes one MP3 per language and prints the resulting paths.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config" / "voice.json"
OUTPUT_DIR = SCRIPT_DIR / "output" / "multilingual"
ENV_PATH = SCRIPT_DIR / ".env"

PHRASES = {
    "en": "Hello, this is a quick multilingual test of the cloned voice.",
    "es": "Hola, esta es una prueba multilingüe rápida de la voz clonada.",
    "fr": "Bonjour, ceci est un test multilingue rapide de la voix clonée.",
    "de": "Hallo, dies ist ein schneller mehrsprachiger Test der geklonten Stimme.",
}


def load_env() -> None:
    if not ENV_PATH.is_file():
        return
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def resolve_voice_id(cli: str | None) -> str | None:
    if cli:
        return cli
    env_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if env_id:
        return env_id
    if CONFIG_PATH.is_file():
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            if isinstance(cfg, dict):
                return cfg.get("default_voice_id")
        except json.JSONDecodeError:
            return None
    return None


def main() -> int:
    load_env()

    parser = argparse.ArgumentParser(description="Multilingual smoke test.")
    parser.add_argument("--voice-id", help="Override voice id.")
    parser.add_argument("--out-dir", default=str(OUTPUT_DIR), help="Output directory.")
    parser.add_argument(
        "--languages",
        default="en,es,fr,de",
        help="Comma-separated language codes (subset of en,es,fr,de).",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        help="Model id (default: eleven_multilingual_v2).",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("[multi][err] ELEVENLABS_API_KEY not set.", file=sys.stderr)
        return 2

    voice_id = resolve_voice_id(args.voice_id)
    if not voice_id:
        print(
            "[multi][err] No voice id available. Pass --voice-id or run create_ivc.py.",
            file=sys.stderr,
        )
        return 2

    langs = [code.strip().lower() for code in args.languages.split(",") if code.strip()]
    unknown = [c for c in langs if c not in PHRASES]
    if unknown:
        print(f"[multi][err] Unknown language codes: {unknown}", file=sys.stderr)
        return 2

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        print(f"[multi][err] elevenlabs not importable: {exc}", file=sys.stderr)
        return 1

    client = ElevenLabs(api_key=api_key)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[multi] voice_id={voice_id} model={args.model}")
    written: list[Path] = []
    for code in langs:
        text = PHRASES[code]
        out_path = out_dir / f"smoke_{code}.mp3"
        print(f"[multi] {code}: {text}")
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=args.model,
            text=text,
            output_format="mp3_44100_128",
        )
        with out_path.open("wb") as fh:
            for chunk in audio:
                if chunk:
                    fh.write(chunk)
        if out_path.stat().st_size == 0:
            print(f"[multi][err] empty output for {code}", file=sys.stderr)
            return 1
        written.append(out_path)

    print("[multi] Wrote:")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
