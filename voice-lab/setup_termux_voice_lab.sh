#!/data/data/com.termux/files/usr/bin/env bash
# setup_termux_voice_lab.sh
# Bootstraps a native Termux voice cloning lab (ElevenLabs IVC + optional OpenVoice).
# Idempotent: re-running only installs what is missing.

set -euo pipefail

# Resolve directories relative to this script so the user can invoke it from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_DIR="${SCRIPT_DIR}"
SAMPLES_DIR="${LAB_DIR}/samples"
PREPARED_DIR="${LAB_DIR}/prepared"
OUTPUT_DIR="${LAB_DIR}/output"
CONFIG_DIR="${LAB_DIR}/config"
VENV_DIR="${LAB_DIR}/.venv"

log()  { printf '[setup] %s\n' "$*"; }
warn() { printf '[setup][warn] %s\n' "$*" >&2; }
err()  { printf '[setup][err] %s\n' "$*" >&2; }

is_termux() {
    [ -n "${PREFIX:-}" ] && [ -d "${PREFIX}" ] && [[ "${PREFIX}" == *"com.termux"* ]]
}

if ! is_termux; then
    warn "This does not look like a Termux environment (\$PREFIX is not com.termux)."
    warn "Continuing, but pkg/termux-* commands may not be available. This toolkit is"
    warn "designed for native Termux on Android only (no proot/chroot/Docker)."
fi

have_cmd() { command -v "$1" >/dev/null 2>&1; }

ensure_pkg() {
    local pkg="$1"
    if have_cmd pkg; then
        if pkg list-installed 2>/dev/null | grep -q "^${pkg}/"; then
            log "pkg ${pkg} already installed."
        else
            log "Installing Termux pkg: ${pkg}"
            pkg install -y "${pkg}" || warn "pkg install ${pkg} failed (continuing)."
        fi
    else
        warn "'pkg' not found; cannot auto-install ${pkg}."
    fi
}

log "Creating toolkit folders under ${LAB_DIR}"
mkdir -p "${SAMPLES_DIR}" "${PREPARED_DIR}" "${OUTPUT_DIR}" "${CONFIG_DIR}"

# Core Termux packages.
for p in python git ffmpeg termux-api build-essential clang make pkg-config libffi openssl; do
    ensure_pkg "${p}"
done

# Sanity checks for required tools.
for bin in python3 git ffmpeg; do
    if have_cmd "${bin}"; then
        log "Found $(${bin} --version 2>&1 | head -n1)"
    else
        err "Required tool missing: ${bin}"
    fi
done

if ! have_cmd termux-microphone-record; then
    warn "termux-microphone-record not found. Install the Termux:API Android app"
    warn "  from F-Droid and ensure the 'termux-api' package is installed."
fi

# Python virtual environment for ElevenLabs SDK.
if [ ! -d "${VENV_DIR}" ]; then
    log "Creating Python venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
else
    log "Python venv already present at ${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

log "Upgrading pip/setuptools/wheel"
pip install --upgrade pip setuptools wheel >/dev/null

log "Installing ElevenLabs SDK and helpers"
pip install --upgrade "elevenlabs>=1.0.0" "python-dotenv>=1.0.0" "requests>=2.31.0"

deactivate

# .env.example (never write a real key here).
ENV_EXAMPLE="${LAB_DIR}/.env.example"
if [ ! -f "${ENV_EXAMPLE}" ]; then
    cat > "${ENV_EXAMPLE}" <<'EOF'
# Copy this file to `.env` and fill in your secrets. `.env` is gitignored.
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
# Optional: default model for TTS.
ELEVENLABS_MODEL=eleven_multilingual_v2
# Optional: default voice id (populated by create_ivc.py).
ELEVENLABS_VOICE_ID=
EOF
    log "Wrote ${ENV_EXAMPLE}"
else
    log ".env.example already exists, leaving untouched."
fi

# Empty voice-id config the Python scripts will populate.
VOICE_CONFIG="${CONFIG_DIR}/voice.json"
if [ ! -f "${VOICE_CONFIG}" ]; then
    printf '{}\n' > "${VOICE_CONFIG}"
    log "Wrote empty ${VOICE_CONFIG}"
fi

cat <<EOF

[setup] Done. Next steps:

  1. Grant microphone permission to Termux:API (open the Android app once).
  2. Copy .env.example to .env and add your ElevenLabs API key:
         cp "${ENV_EXAMPLE}" "${LAB_DIR}/.env"
  3. Record three ~20s samples:
         bash "${LAB_DIR}/record_sample.sh" 20 "${SAMPLES_DIR}/sample_01.m4a"
         bash "${LAB_DIR}/record_sample.sh" 20 "${SAMPLES_DIR}/sample_02.m4a"
         bash "${LAB_DIR}/record_sample.sh" 20 "${SAMPLES_DIR}/sample_03.m4a"
  4. Prepare them:
         bash "${LAB_DIR}/prepare_audio.sh" "${SAMPLES_DIR}" "${PREPARED_DIR}"
  5. Create the Instant Voice Clone (prints a voice id):
         "${VENV_DIR}/bin/python" "${LAB_DIR}/create_ivc.py" --name "MyVoice" "${PREPARED_DIR}"/*.mp3
  6. Speak:
         "${VENV_DIR}/bin/python" "${LAB_DIR}/speak_ivc.py" --text "Hello from Termux"
  7. Validate the environment any time:
         bash "${LAB_DIR}/smoke_test.sh"

EOF
