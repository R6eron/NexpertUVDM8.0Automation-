#!/data/data/com.termux/files/usr/bin/bash
set -e

VOICE_FILE="./voice/jesse_catchphrases.txt"
FALLBACK="./jesse_vocab.txt"

if [ -r "$VOICE_FILE" ]; then
    QUOTE="$(shuf -n 1 "$VOICE_FILE")"
elif [ -r "$FALLBACK" ]; then
    QUOTE="$(shuf -n 1 "$FALLBACK")"
else
    QUOTE="Wing-man Jesse quote library not found."
fi

# Use tuned Wing-man Google TTS profile via the CLI
cd "$HOME/NexpertUVDM-Automation"
python wingman_cli.py voice --test "$QUOTE"
