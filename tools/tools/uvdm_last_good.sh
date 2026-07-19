#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/NexpertUVDM-Automation"
STAMP="$(date +%Y%m%d-%H%M%S)"
NOTE="${1:-manual}"
SAFE_NOTE="$(printf '%s' "$NOTE" | tr ' /:' '___')"
DEST="$ROOT/backups/last_good/${STAMP}_${SAFE_NOTE}"

mkdir -p "$DEST"

FILES=(
  "uvdm_live.py"
  "uvdm_master.py"
  "wingman_cli.py"
  "livermore_pivot_guard_auto.py"
  "wyckoff_trend_wrapper_v2.py"
  "config"
  "tools"
)

for item in "${FILES[@]}"; do
  if [ -e "$ROOT/$item" ]; then
    cp -a "$ROOT/$item" "$DEST/"
  fi
done

if [ -d "$ROOT/.git" ]; then
  git -C "$ROOT" rev-parse --short HEAD > "$DEST/git_head.txt" 2>/dev/null || true
  git -C "$ROOT" status --short > "$DEST/git_status.txt" 2>/dev/null || true
fi

echo "$DEST" > "$ROOT/backups/last_good/LATEST"
echo "last_good_saved: $DEST"
