#!/data/data/com.termux/files/usr/bin/bash
set -e

VOICE_FILE="./voice/jesse_catchphrases_premium.txt"

if [ -r "$VOICE_FILE" ]; then
    QUOTE="$(grep -v '^[[:space:]]*$' "$VOICE_FILE" | shuf -n 1)"
else
    QUOTE="Premium Jesse library not found. Protect capital anyway."
fi

cd "$HOME/NexpertUVDM-Automation"
python wingman_cli.py voice --test "$QUOTE"
