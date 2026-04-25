#!/data/data/com.termux/files/usr/bin/env bash
# openvoice_native_check.sh
# Probes whether OpenVoice / MeloTTS dependencies can be installed and imported
# *natively* in Termux. Does NOT use proot/chroot/Docker. Prints actionable
# guidance and a summary; never silently switches strategies.
#
# Usage:
#   openvoice_native_check.sh [--install]
#   openvoice_native_check.sh -h | --help
#
# Without --install: only checks/reports.
# With    --install: attempts a best-effort native install in voice-lab/.venv-openvoice
#                    and reports what worked and what didn't.

set -euo pipefail

usage() { sed -n '2,14p' "$0"; }

INSTALL=0
case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    --install) INSTALL=1 ;;
    "") ;;
    *) echo "[ov-check][err] unknown arg: $1" >&2; usage; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv-openvoice"

PASS=0; FAIL=0
ok()   { echo "[ov-check][ok]  $*"; PASS=$((PASS+1)); }
bad()  { echo "[ov-check][!!]  $*" >&2; FAIL=$((FAIL+1)); }
note() { echo "[ov-check][..]  $*"; }

check_cmd() {
    local cmd="$1"
    if command -v "${cmd}" >/dev/null 2>&1; then
        ok "${cmd} present: $(${cmd} --version 2>&1 | head -n1)"
    else
        bad "${cmd} not found"
    fi
}

check_pkg() {
    local pkg="$1"
    if command -v pkg >/dev/null 2>&1 && pkg list-installed 2>/dev/null | grep -q "^${pkg}/"; then
        ok "termux pkg installed: ${pkg}"
    else
        bad "termux pkg missing: ${pkg}  (try: pkg install ${pkg})"
    fi
}

note "Native Termux only — no proot/chroot/Docker."
note "Checking base toolchain..."
check_cmd python3
check_cmd pip
check_cmd ffmpeg
check_cmd git
check_cmd clang

note "Checking Termux build packages..."
check_pkg python
check_pkg ffmpeg
check_pkg git
check_pkg clang
check_pkg make
check_pkg pkg-config
check_pkg libffi
check_pkg openssl

# Things OpenVoice/MeloTTS commonly need at build time.
for p in libjpeg-turbo libpng rust binutils; do
    check_pkg "${p}" || true
done

# Probe Python import surface in the existing venv if one exists.
PROBE_PY="${SCRIPT_DIR}/.venv/bin/python"
if [ ! -x "${PROBE_PY}" ]; then
    PROBE_PY="$(command -v python3 || true)"
fi

if [ -n "${PROBE_PY}" ] && [ -x "${PROBE_PY}" ]; then
    note "Probing Python imports with ${PROBE_PY}"
    "${PROBE_PY}" - <<'PY' || true
import importlib, sys
mods = ["torch", "torchaudio", "numpy", "scipy", "librosa", "soundfile",
        "MeloTTS", "openvoice"]
for m in mods:
    try:
        importlib.import_module(m)
        print(f"[ov-check][ok]  python import: {m}")
    except Exception as exc:
        print(f"[ov-check][!!]  python import failed: {m}: {exc.__class__.__name__}: {exc}")
PY
fi

if [ "${INSTALL}" -eq 1 ]; then
    note "Attempting best-effort native install into ${VENV_DIR}"
    note "This is expected to fail on many Termux setups (PyTorch wheels are not"
    note "officially published for Android/aarch64). Read the messages carefully."
    if [ ! -d "${VENV_DIR}" ]; then
        python3 -m venv "${VENV_DIR}"
    fi
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    pip install --upgrade pip setuptools wheel || true

    # NumPy/SciPy/librosa: usually buildable on Termux given the build packages above.
    pip install --upgrade numpy || bad "numpy install failed"
    pip install --upgrade scipy || bad "scipy install failed (needs gfortran/openblas; may not be available natively)"
    pip install --upgrade soundfile librosa || bad "librosa/soundfile install failed"

    # PyTorch: there is no official aarch64-Android wheel. Try, but expect failure.
    if pip install --upgrade torch torchaudio; then
        ok "torch + torchaudio installed natively"
    else
        bad "torch install failed natively. This is the common blocker."
        note "Guidance:"
        note "  - There is no upstream PyTorch wheel for Termux/Android aarch64."
        note "  - Building from source on-device is extremely heavy and often fails on RAM."
        note "  - Check community wheels (e.g. termux-pytorch projects on GitHub) and"
        note "    install one manually with 'pip install <wheel-url>' if you trust it."
        note "  - DO NOT switch to proot/chroot/Docker per project policy."
        note "  - As a fallback, stay on the ElevenLabs IVC path (already wired up)."
    fi

    # MeloTTS depends on torch, so this only succeeds if torch did.
    if pip install --upgrade git+https://github.com/myshell-ai/MeloTTS.git; then
        ok "MeloTTS installed"
    else
        bad "MeloTTS install failed (most likely because torch is missing)."
    fi

    if pip install --upgrade git+https://github.com/myshell-ai/OpenVoice.git; then
        ok "OpenVoice installed"
    else
        bad "OpenVoice install failed."
    fi

    deactivate
fi

echo
echo "[ov-check] Summary: ${PASS} ok, ${FAIL} issue(s)."
if [ "${FAIL}" -gt 0 ]; then
    echo "[ov-check] OpenVoice native install on Termux is best-effort."
    echo "[ov-check] If torch will not install, the supported path here is ElevenLabs IVC."
fi
