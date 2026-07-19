from pathlib import Path

content = r'''#!/usr/bin/env bash
set -euo pipefail

BASE="${HOME}/NexpertUVDM-Automation"
RUNTIME="${BASE}/runtime"
ALERTS="${RUNTIME}/alerts.json"
WATCHER="${BASE}/tools/uvdm_voice_watch.py"
BACKUP="${BASE}/tools/uvdm_backup_runtime.sh"

mkdir -p "$RUNTIME"

lower() { printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]'; }
upper() { printf '%s' "${1:-}" | tr '[:lower:]' '[:upper:]'; }

amount=""
asset=""
mode=""
lev=""
voice_cmd=""
operator_action="SCALE_IN_SMALL"
backup_saved=""

if [ "$#" -eq 0 ]; then
  echo "deploy: interactive menu not yet wired."
  echo "Use: deploy 58 xlm futures 10x"
  exit 0
fi

voice_cmd="deploy $*"

for tok in "$@"; do
  ltok="$(lower "$tok")"
  if [[ "$ltok" =~ ^([0-9]+(.[0-9]+)?)x$ ]]; then
    lev="$ltok"
    continue
  fi
  case "$ltok" in
    f|futures|future|ft)
      mode="futures"
      continue
      ;;
    spot)
      mode="spot"
      continue
      ;;
  esac
  case "$ltok" in
    xlm|xrp|btc|eth)
      asset="$ltok"
      continue
      ;;
  esac
  if [[ "$ltok" =~ ^[0-9]+(.[0-9]+)?$ ]]; then
    amount="$ltok"
    continue
  fi
done

if [ -z "$amount" ]; then
  echo "Amount not understood. Example: deploy 58 xlm futures 10x"
  exit 1
fi
if [ -z "$asset" ]; then
  echo "Asset not understood. Example: deploy 58 xlm futures 10x"
  exit 1
fi
if [ -z "$mode" ]; then
  echo "Mode not understood. Use: f, futures, or spot."
  exit 1
fi
if [ -z "$lev" ]; then
  echo "Leverage not understood. Use e.g. 10x, 7x, 5x, 1x."
  exit 1
fi

if awk "BEGIN {exit !($amount >= 1000)}"; then
  operator_action="SCALE_IN_MEDIUM"
fi

echo "deploy_args=$amount $asset $mode $lev"

asset_up="$(upper "$asset")"
request_id="$(date -u +'%Y%m%dT%H%M%SZ')"

if [ -x "$BACKUP" ]; then
  backup_saved="$("$BACKUP" | tail -n 1)"
  echo "$backup_saved"
else
  echo "backup_skipped=no_backup_script"
fi

cat > "$ALERTS" <<JSON
{
  "status": "execute_ready",
  "message": "",
  "asset": "$asset_up",
  "setup": "MANUAL_DEPLOY",
  "level": "$amount",
  "regime": "manual",
  "voice_cmd": "$voice_cmd",
  "operator_action": "$operator_action",
  "request_id": "$request_id",
  "mode": "$mode",
  "leverage": "$lev"
}
JSON

printf '
Wrote runtime/alerts.json:
'
cat "$ALERTS"
printf '
Running duplicate watcher path with voice on...

'

python3 "$WATCHER" \
  --debug \
  --dry-run \
  --auto-on-execute-ready \
  --trigger-on-start \
  --oneshot || true
'''
Path("tools/deploy").write_text(content, encoding="utf-8")
print("WROTE tools/deploy")
