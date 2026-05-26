#!/usr/bin/env bash
set -e

key="$1"
value="$2"
db="$HOME/.config/uvdm/state.db"

if [ -z "$key" ] || [ -z "$value" ]; then
  echo "Usage: set_state.sh KEY VALUE"
  exit 1
fi

case "$key" in
  XLM_SPOT|XLM_FUT|XLM_TARGET|FLR_TOTAL|SGB_TOTAL|XRPN_TOTAL)
    ;;
  *)
    echo "Invalid key: $key"
    exit 1
    ;;
esac

case "$value" in
  ''|*[!0-9]*)
    echo "Invalid value: must be digits only"
    exit 1
    ;;
esac

mkdir -p "$HOME/.config/uvdm"
touch "$db"

tmp="$(mktemp)"

if grep -q "^${key}=" "$db"; then
  sed "s/^${key}=.*/${key}=${value}/" "$db" > "$tmp"
else
  cat "$db" > "$tmp"
  echo "${key}=${value}" >> "$tmp"
fi

mv "$tmp" "$db"
echo "Updated: ${key}=${value}"
