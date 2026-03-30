#!/data/data/com.termux/files/usr/bin/bash

DATE="$(date +%Y%m%d_%H%M)"
mkdir -p "$HOME/projects/uvdm-automation/logs"
LOG="$HOME/projects/uvdm-automation/logs/pull_${DATE}.log"

echo "$DATE: UVDM Voice → BREATH Flywheel" >> "$LOG"

mkdir -p "$HOME/projects/uvdm-automation/vault/voice_breaths_2026"

# SINGLE LINE: find + exec (no line breaks)

cd "$HOME/projects/uvdm-automation/vault/voice_breaths_2026" || exit 0
NEW="$(find . -name "*.m4a" -mtime -1 | wc -l)"
TOTAL="$(ls *.m4a 2>/dev/null | wc -l)"
echo "$DATE: $NEW new → $TOTAL total breaths vaulted" >> "$LOG"
# Voice puller (
for f in "$HOME/storage/shared/Download"/*.m4a; do 
  [ -f "$f" ] && cp "$f" "$HOME/projects/uvdm-automation/vault/voice_breaths_2026/" && echo "Copied: $(basename "$f")" >> "$LOG"
done
for f in "$HOME/storage/shared/Download"/*.m4a; do [ -f "$f" ] && cp "$f" vault/voice_breaths_2026/ && echo "Copied $(basename "$f")"; done
