#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$HOME/NexpertUVDM-Automation"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$ROOT/backups/runtime/$STAMP"
mkdir -p "$DEST"
cp -a "$ROOT/runtime/." "$DEST/" 2>/dev/null || true
cp -a "$ROOT/execution_log.jsonl" "$DEST/" 2>/dev/null || true
echo "backup_saved=$DEST"
