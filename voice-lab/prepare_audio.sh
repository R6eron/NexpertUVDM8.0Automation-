#!/data/data/com.termux/files/usr/bin/env bash
# prepare_audio.sh
# Converts/normalizes recorded audio into formats friendly for ElevenLabs IVC
# and OpenVoice (mono, 16-bit PCM at 22.05 kHz / 16 kHz, loudness-normalized).
#
# Usage:
#   prepare_audio.sh INPUT_DIR [OUTPUT_DIR]
#   prepare_audio.sh -h | --help
#
# For each INPUT_DIR/*.{m4a,wav,mp3,ogg,flac,aac,webm} we write:
#   OUTPUT_DIR/<name>.mp3   - 44.1kHz stereo MP3 (ElevenLabs-friendly)
#   OUTPUT_DIR/<name>.wav   - 22.05kHz mono 16-bit PCM (OpenVoice-friendly)

set -euo pipefail

usage() { sed -n '2,12p' "$0"; }

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ -z "${1:-}" ]; then
    usage
    exit 0
fi

INPUT_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${2:-${SCRIPT_DIR}/prepared}"

if [ ! -d "${INPUT_DIR}" ]; then
    echo "[prep][err] Input directory not found: ${INPUT_DIR}" >&2
    exit 2
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[prep][err] ffmpeg not found. Run: pkg install ffmpeg" >&2
    exit 127
fi

mkdir -p "${OUTPUT_DIR}"

shopt -s nullglob nocaseglob
FILES=("${INPUT_DIR}"/*.{m4a,wav,mp3,ogg,flac,aac,webm})
shopt -u nullglob nocaseglob

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "[prep][err] No audio files found in ${INPUT_DIR}" >&2
    exit 1
fi

for src in "${FILES[@]}"; do
    base="$(basename "${src}")"
    name="${base%.*}"
    mp3_out="${OUTPUT_DIR}/${name}.mp3"
    wav_out="${OUTPUT_DIR}/${name}.wav"

    echo "[prep] ${src}"
    # EBU R128 two-pass loudness normalization would be ideal, but is slow on-device.
    # Use dynaudnorm for a fast, stable normalization. Trim leading/trailing silence.
    COMMON_FILTERS='silenceremove=start_periods=1:start_duration=0.2:start_threshold=-40dB:detection=peak,aresample=async=1,dynaudnorm=f=250:g=15'

    # ElevenLabs-friendly: 44.1kHz stereo MP3 @ 192k.
    ffmpeg -hide_banner -loglevel error -y -i "${src}" \
        -af "${COMMON_FILTERS}" \
        -ar 44100 -ac 2 -c:a libmp3lame -b:a 192k \
        "${mp3_out}"
    echo "[prep]   wrote ${mp3_out}"

    # OpenVoice-friendly: 22.05kHz mono 16-bit PCM WAV.
    ffmpeg -hide_banner -loglevel error -y -i "${src}" \
        -af "${COMMON_FILTERS}" \
        -ar 22050 -ac 1 -c:a pcm_s16le \
        "${wav_out}"
    echo "[prep]   wrote ${wav_out}"
done

echo "[prep] Done. Outputs in ${OUTPUT_DIR}"
