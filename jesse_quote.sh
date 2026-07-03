#!/data/data/com.termux/files/usr/bin/bash
set -e

VOICE_FILE="./voice/jesse_catchphrases.txt"
FALLBACK="$HOME/jesse_vocab.txt"

if [ -r "$VOICE_FILE" ]; then
    QUOTE="$(grep -v '^[[:space:]]*$' "$VOICE_FILE" | shuf -n 1)"
elif [ -r "$FALLBACK" ]; then
    QUOTE="$(grep -v '^[[:space:]]*$' "$FALLBACK" | shuf -n 1)"
else
    QUOTE="Wing-man Jesse quote library not found."
fi

cd "$HOME/NexpertUVDM-Automation"
python wingman_cli.py voice --test "$QUOTE"
