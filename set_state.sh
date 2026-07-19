#!/usr/bin/env bash
set -euo pipefail

key="${1:-}"
value="${2:-}"
db="${UVDM_STATE_DB:-$HOME/.config/uvdm/state.db}"
db_dir="$(dirname "$db")"

usage() {
  echo "Usage: set_state_complete.sh KEY VALUE"
  echo "Allowed keys: XLM_SPOT XLM_FUT XLM_TARGET FLR_TOTAL SGB_TOTAL XRPN_TOTAL"
}

if [[ -z "$key" || -z "$value" ]]; then
  usage
  exit 1
fi

case "$key" in
  XLM_SPOT|XLM_FUT|XLM_TARGET|FLR_TOTAL|SGB_TOTAL|XRPN_TOTAL)
    ;;
  *)
    echo "Invalid key: $key" >&2
    usage
    exit 1
    ;;
esac

case "$value" in
  ''|*[!0-9]*)
    echo "Invalid value: must be digits only" >&2
    exit 1
    ;;
esac

mkdir -p "$db_dir"
[[ -f "$db" ]] || touch "$db"

tmp="$(mktemp "$db_dir/.state.db.tmp.XXXXXX")"

cleanup() {
  [[ -f "$tmp" ]] && rm -f "$tmp"
}
trap cleanup EXIT INT TERM

if grep -q "^${key}=" "$db"; then
  sed "s/^${key}=.*/${key}=${value}/" "$db" > "$tmp"
else
  cat "$db" > "$tmp"
  printf '%s=%s
' "$key" "$value" >> "$tmp"
fi

chmod --reference="$db" "$tmp" 2>/dev/null || chmod 600 "$tmp"
mv -f "$tmp" "$db"
trap - EXIT INT TERM

echo "Updated: ${key}=${value}"
echo "DB: $db"