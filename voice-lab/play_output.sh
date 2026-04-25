#!/data/data/com.termux/files/usr/bin/env bash
# play_output.sh
# Plays generated audio. Prefers mpv, falls back to ffplay. Optionally speaks a
# cue via termux-tts-speak so the Android status is audible before playback.
#
# Usage:
#   play_output.sh PATH_TO_AUDIO [--cue "Playing now"] [--no-cue]
#   play_output.sh -h | --help

set -euo pipefail

usage() { sed -n '2,9p' "$0"; }

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ -z "${1:-}" ]; then
    usage
    exit 0
fi

AUDIO="$1"
shift || true

CUE="Playing sample"
NO_CUE=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --cue) CUE="${2:-}"; shift 2 ;;
        --no-cue) NO_CUE=1; shift ;;
        *) echo "[play][warn] ignoring unknown arg: $1" >&2; shift ;;
    esac
done

if [ ! -f "${AUDIO}" ]; then
    echo "[play][err] File not found: ${AUDIO}" >&2
    exit 2
fi

if [ "${NO_CUE}" -eq 0 ] && command -v termux-tts-speak >/dev/null 2>&1; then
    termux-tts-speak "${CUE}" >/dev/null 2>&1 || true
fi

if command -v mpv >/dev/null 2>&1; then
    echo "[play] mpv ${AUDIO}"
    exec mpv --really-quiet --no-video "${AUDIO}"
elif command -v ffplay >/dev/null 2>&1; then
    echo "[play] ffplay ${AUDIO}"
    exec ffplay -nodisp -autoexit -loglevel error "${AUDIO}"
elif command -v play >/dev/null 2>&1; then
    echo "[play] play ${AUDIO}"
    exec play -q "${AUDIO}"
else
    cat >&2 <<'EOF'
[play][err] No audio player found. Install one:
    pkg install mpv        # recommended
    pkg install ffmpeg     # provides ffplay
EOF
    exit 127
fi
