#!/data/data/com.termux/files/usr/bin/env bash
# record_sample.sh
# Records a microphone sample using termux-microphone-record (Termux:API).
#
# Usage:
#   record_sample.sh [DURATION_SECONDS] [OUTPUT_PATH]
#   record_sample.sh -h | --help
#
# Defaults:
#   DURATION_SECONDS = 20
#   OUTPUT_PATH      = ./samples/sample_<timestamp>.m4a (next to this script)

set -euo pipefail

usage() {
    sed -n '2,12p' "$0"
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

DURATION="${1:-20}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_OUT="${SCRIPT_DIR}/samples/sample_$(date +%Y%m%d_%H%M%S).m4a"
OUT_PATH="${2:-${DEFAULT_OUT}}"

if ! [[ "${DURATION}" =~ ^[0-9]+$ ]]; then
    echo "[record][err] DURATION_SECONDS must be a positive integer, got: ${DURATION}" >&2
    exit 2
fi

if ! command -v termux-microphone-record >/dev/null 2>&1; then
    cat >&2 <<'EOF'
[record][err] termux-microphone-record not found.
Install the Termux:API Android app from F-Droid AND run:
    pkg install termux-api
Then grant microphone permission to the Termux:API app.
EOF
    exit 127
fi

mkdir -p "$(dirname "${OUT_PATH}")"

# Stop any currently-running recording session before starting a new one.
termux-microphone-record -q >/dev/null 2>&1 || true

echo "[record] Recording ${DURATION}s to ${OUT_PATH}"
echo "[record] Speak naturally; vary intonation. Press Ctrl-C to abort."

# -d duration in seconds, -f output file. termux-microphone-record returns immediately
# and records in the background; we sleep + stop to make this script blocking.
termux-microphone-record -d "${DURATION}" -f "${OUT_PATH}"

# Poll for completion. Slightly over-sleep to ensure the file is flushed.
sleep "$((DURATION + 2))"
termux-microphone-record -q >/dev/null 2>&1 || true

if [ ! -s "${OUT_PATH}" ]; then
    echo "[record][err] Output file is missing or empty: ${OUT_PATH}" >&2
    echo "[record][err] Check that microphone permission is granted to Termux:API." >&2
    exit 1
fi

SIZE_BYTES=$(stat -c '%s' "${OUT_PATH}" 2>/dev/null || wc -c < "${OUT_PATH}")
echo "[record] Saved ${OUT_PATH} (${SIZE_BYTES} bytes)"
