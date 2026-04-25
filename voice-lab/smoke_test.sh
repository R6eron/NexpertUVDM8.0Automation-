#!/data/data/com.termux/files/usr/bin/env bash
# smoke_test.sh
# Verifies the voice-lab toolkit is wired up correctly. Does NOT call paid APIs
# unless --api is passed (then a single cheap user-info request is made).
#
# Usage:
#   smoke_test.sh           # local checks only (no network)
#   smoke_test.sh --api     # also check ElevenLabs API key works
#   smoke_test.sh -h | --help

set -euo pipefail

usage() { sed -n '2,9p' "$0"; }

API_CHECK=0
case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    --api) API_CHECK=1 ;;
    "") ;;
    *) echo "[smoke][err] unknown arg: $1" >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
ENV_FILE="${SCRIPT_DIR}/.env"

PASS=0; FAIL=0
ok()  { echo "[smoke][ok]  $*"; PASS=$((PASS+1)); }
bad() { echo "[smoke][!!]  $*" >&2; FAIL=$((FAIL+1)); }

# Required CLI tools.
for bin in python3 git ffmpeg bash; do
    if command -v "${bin}" >/dev/null 2>&1; then
        ok "$(${bin} --version 2>&1 | head -n1)"
    else
        bad "missing: ${bin}"
    fi
done

# Termux-specific tools (warn-only when missing, since they need real Termux).
for bin in termux-microphone-record termux-tts-speak; do
    if command -v "${bin}" >/dev/null 2>&1; then
        ok "termux tool present: ${bin}"
    else
        echo "[smoke][warn] termux tool missing: ${bin} (only meaningful on a real device)"
    fi
done

# Audio player (mpv preferred, ffplay fallback).
if command -v mpv >/dev/null 2>&1; then
    ok "audio player: mpv"
elif command -v ffplay >/dev/null 2>&1; then
    ok "audio player: ffplay (mpv preferred)"
else
    bad "no audio player found (install mpv or rely on ffplay)"
fi

# Toolkit files.
EXPECTED=(
    setup_termux_voice_lab.sh
    record_sample.sh
    prepare_audio.sh
    create_ivc.py
    speak_ivc.py
    play_output.sh
    multilingual_test.py
    openvoice_native_check.sh
    smoke_test.sh
    README.md
    .env.example
)
for f in "${EXPECTED[@]}"; do
    if [ -f "${SCRIPT_DIR}/${f}" ]; then
        ok "file present: ${f}"
    else
        bad "missing toolkit file: ${f}"
    fi
done

# Shell syntax checks.
for sh in "${SCRIPT_DIR}"/*.sh; do
    if bash -n "${sh}"; then
        ok "shell syntax ok: $(basename "${sh}")"
    else
        bad "shell syntax error: $(basename "${sh}")"
    fi
done

# Python syntax checks.
for py in "${SCRIPT_DIR}"/*.py; do
    if python3 -m py_compile "${py}"; then
        ok "python syntax ok: $(basename "${py}")"
    else
        bad "python syntax error: $(basename "${py}")"
    fi
done

# Venv + ElevenLabs SDK (optional but expected after setup).
if [ -x "${VENV_DIR}/bin/python" ]; then
    ok "venv present: ${VENV_DIR}"
    if "${VENV_DIR}/bin/python" -c "import elevenlabs" 2>/dev/null; then
        ok "elevenlabs SDK importable in venv"
    else
        bad "elevenlabs SDK not importable in venv (run setup_termux_voice_lab.sh)"
    fi
else
    echo "[smoke][warn] venv not yet created at ${VENV_DIR} (run setup_termux_voice_lab.sh)"
fi

# .env / API key visibility (don't print the key itself).
if [ -f "${ENV_FILE}" ]; then
    if grep -q '^ELEVENLABS_API_KEY=.\+' "${ENV_FILE}" \
       && ! grep -q '^ELEVENLABS_API_KEY=your-elevenlabs-api-key-here' "${ENV_FILE}"; then
        ok ".env defines ELEVENLABS_API_KEY"
    else
        bad ".env exists but ELEVENLABS_API_KEY is missing or still the placeholder"
    fi
else
    echo "[smoke][warn] .env not found (copy .env.example to .env and edit)"
fi

# Optional live API check.
if [ "${API_CHECK}" -eq 1 ]; then
    if [ ! -x "${VENV_DIR}/bin/python" ]; then
        bad "--api requested but venv missing"
    elif [ ! -f "${ENV_FILE}" ]; then
        bad "--api requested but .env missing"
    else
        echo "[smoke] Calling ElevenLabs /v1/user (counts against your quota lightly)..."
        if "${VENV_DIR}/bin/python" - <<'PY'
import os, sys
from pathlib import Path

env = Path(__file__).resolve().parent / ".env" if "__file__" in dir() else None
# stdin-mode: re-read .env ourselves.
env_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] or ".")), ".env")
if os.path.isfile(env_path):
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
if not key:
    print("[smoke][!!] ELEVENLABS_API_KEY missing"); sys.exit(1)

try:
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=key)
    user = client.user.get()
    print(f"[smoke][ok]  api ok (subscription tier: {getattr(user, 'subscription', None) and getattr(user.subscription, 'tier', '?')})")
except Exception as exc:
    print(f"[smoke][!!] api call failed: {exc.__class__.__name__}: {exc}")
    sys.exit(1)
PY
        then
            PASS=$((PASS+1))
        else
            FAIL=$((FAIL+1))
        fi
    fi
fi

echo
echo "[smoke] Summary: ${PASS} ok, ${FAIL} issue(s)."
[ "${FAIL}" -eq 0 ]
