#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAVOURITES_FILE="${SCRIPT_DIR}/favourites.txt"

if [ ! -f "$FAVOURITES_FILE" ]; then
  echo "No favourites.txt found in $SCRIPT_DIR" >&2
  exit 1
fi

while read -r token; do
  [ -z "$token" ] && continue
  clear
  "${SCRIPT_DIR}/uvdm_fingertips.sh" "$token"
  echo
  read -rp "Press Enter for next token (or Ctrl+C to exit)..." _
done < "$FAVOURITES_FILE"
