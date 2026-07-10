#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <commit-id> [--no-run]"
  echo "Example: $0 efd9171"
  exit 1
fi

COMMIT="$1"
NO_RUN="${2:-}"

FILES=(
  "voice/jesse_catchphrases.txt"
  "jesse_quote.sh"
  "wingman_cli.py"
  "wingman_prefs.json"
)

echo "[wingman_restore] Repo: $PWD"
echo "[wingman_restore] Target commit: $COMMIT"
echo "[wingman_restore] Files:"
printf '  - %s
' "${FILES[@]}"

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKDIR="backups/wingman-restore-$STAMP"
mkdir -p "$BACKDIR"

echo "[wingman_restore] Backing up current files to $BACKDIR"
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    cp -f "$f" "$BACKDIR"/
  fi
done

echo "[wingman_restore] Diff vs current working tree:"
git diff --stat -- "${FILES[@]}" || true

echo "[wingman_restore] Restoring files from $COMMIT"
git checkout "$COMMIT" -- "${FILES[@]}"

echo "[wingman_restore] Compiling wingman_cli.py"
python -m py_compile wingman_cli.py

if [ "$NO_RUN" != "--no-run" ]; then
  echo "[wingman_restore] Running JesseQuote"
  if command -v JesseQuote >/dev/null 2>&1; then
    JesseQuote
  else
    ./jesse_quote.sh
  fi
else
  echo "[wingman_restore] Skipping JesseQuote run (--no-run set)"
fi

echo "[wingman_restore] Done."
