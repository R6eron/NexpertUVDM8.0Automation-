#!/usr/bin/env bash

RESET='\u001B[0m'
RED='\u001B[0;31m'
GREEN='\u001B[0;32m'
YELLOW='\u001B[0;33m'
CYAN='\u001B[0;36m'
MAGENTA='\u001B[0;35m'
BOLD='\u001B[1m'

TOKEN="$(printf '%s' "${1:-XLM}" | tr '[:upper:]' '[:lower:]')"
MODE="${2:-spot}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESET_FILE="${SCRIPT_DIR}/presets/${TOKEN}.conf"
FAVOURITES_FILE="${SCRIPT_DIR}/favourites.txt"
IS_FAVOURITE="no"

if [ -f "$FAVOURITES_FILE" ] && grep -qx "$TOKEN" "$FAVOURITES_FILE"; then
  IS_FAVOURITE="yes"
fi

PAIR="${PAIR:-${TOKEN^^}/USDT}"
SUPPORT_LOW="${SUPPORT_LOW:-TBD}"
SUPPORT_HIGH="${SUPPORT_HIGH:-TBD}"
ALERT_LEVEL="${ALERT_LEVEL:-TBD}"
CUT_LEVEL="${CUT_LEVEL:-TBD}"
PULLBACK_1="${PULLBACK_1:-Light bid}"
PULLBACK_2="${PULLBACK_2:-Main bid}"
PULLBACK_3="${PULLBACK_3:-Max pain bid}"
CAMPAIGN_SIZE="${CAMPAIGN_SIZE:-Starter size only}"
PLAN_TEXT="${PLAN_TEXT:-Wait for proof, then position at levels without chasing.}"
RISK_TEXT="${RISK_TEXT:-Define invalidation first. No hope trades.}"
TAPE_TRUTH="${TAPE_TRUTH:-Obey the tape. Do not argue with price.}"

if [ -f "$PRESET_FILE" ]; then
  # shellcheck disable=SC1090
  source "$PRESET_FILE"
fi

PAIR="${PAIR_OVERRIDE:-$PAIR}"
SUPPORT_LOW="${SUPPORT_LOW_OVERRIDE:-$SUPPORT_LOW}"
SUPPORT_HIGH="${SUPPORT_HIGH_OVERRIDE:-$SUPPORT_HIGH}"
ALERT_LEVEL="${ALERT_LEVEL_OVERRIDE:-$ALERT_LEVEL}"
CUT_LEVEL="${CUT_LEVEL_OVERRIDE:-$CUT_LEVEL}"
PULLBACK_1="${PULLBACK_1_OVERRIDE:-$PULLBACK_1}"
PULLBACK_2="${PULLBACK_2_OVERRIDE:-$PULLBACK_2}"
PULLBACK_3="${PULLBACK_3_OVERRIDE:-$PULLBACK_3}"
CAMPAIGN_SIZE="${CAMPAIGN_SIZE_OVERRIDE:-$CAMPAIGN_SIZE}"
PLAN_TEXT="${PLAN_TEXT_OVERRIDE:-$PLAN_TEXT}"
RISK_TEXT="${RISK_TEXT_OVERRIDE:-$RISK_TEXT}"
TAPE_TRUTH="${TAPE_TRUTH_OVERRIDE:-$TAPE_TRUTH}"

MEXC_SYMBOL="$(printf '%s' "$PAIR" | tr -d '/')"
REFERENCE_PRICE="unavailable"
PRICE_STATE="neutral"

fetch_price() {
  curl -s "https://api.mexc.com/api/v3/ticker/price?symbol=${MEXC_SYMBOL}" \
    | python3 -c 'import json,sys
try:
    data=json.load(sys.stdin)
    print(data.get("price","unavailable"))
except Exception:
    print("unavailable")'
}

REFERENCE_PRICE="$(fetch_price)"

if [ "$REFERENCE_PRICE" != "unavailable" ] && [ "$SUPPORT_LOW" != "TBD" ] && [ "$SUPPORT_HIGH" != "TBD" ] && [ "$ALERT_LEVEL" != "TBD" ] && [ "$CUT_LEVEL" != "TBD" ]; then
  PRICE_STATE="$(python3 - "$REFERENCE_PRICE" "$SUPPORT_LOW" "$SUPPORT_HIGH" "$ALERT_LEVEL" "$CUT_LEVEL" <<'PY'
import sys
price=float(sys.argv[1])
support_low=float(sys.argv[2])
support_high=float(sys.argv[3])
alert=float(sys.argv[4])
cut=float(sys.argv[5])

if price <= cut:
    print("below_cut")
elif price < support_low:
    print("below_support")
elif support_low <= price <= support_high:
    print("in_support")
elif support_high < price < alert:
    print("between_support_and_alert")
else:
    print("above_alert")
PY
)"
fi

clear

printf "${BOLD}${CYAN}UVDM Fingertips${RESET}
"
printf "${MAGENTA}XRPeasy Digital Solutions | Preset-loaded multi-token shell${RESET}
"
printf "${YELLOW}Mode:${RESET} %s
" "$MODE"
printf "${YELLOW}Token:${RESET} %s
" "${TOKEN^^}"
printf "${YELLOW}Favourite:${RESET} %s
" "$IS_FAVOURITE"
printf "${YELLOW}Pair:${RESET} %s
" "$PAIR"
printf "
"

printf "${BOLD}${CYAN}Reference price (MEXC only)${RESET}
"
printf "${YELLOW}Source:${RESET} MEXC price feed only
"
printf "${YELLOW}Use:${RESET} Reference, not execution trigger
"
case "$PRICE_STATE" in
  below_cut)
    printf "${RED}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${RED}Context:${RESET} Below defined cut; no add unless reclaimed
"
    ;;
  below_support)
    printf "${YELLOW}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${YELLOW}Context:${RESET} Below support; reclaim needed before trust returns
"
    ;;
  in_support)
    printf "${GREEN}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${GREEN}Context:${RESET} Near planned support area
"
    ;;
  between_support_and_alert)
    printf "${CYAN}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${CYAN}Context:${RESET} Between support and alert; no need to chase
"
    ;;
  above_alert)
    printf "${MAGENTA}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${MAGENTA}Context:${RESET} Extended versus support; avoid emotional chase
"
    ;;
  *)
    printf "${YELLOW}Price:${RESET} %s
" "$REFERENCE_PRICE"
    printf "${YELLOW}Context:${RESET} No live classification available
"
    ;;
esac
printf "
"

printf "${BOLD}${CYAN}Market structure${RESET}
"
printf "${YELLOW}Support zone:${RESET} %s - %s
" "$SUPPORT_LOW" "$SUPPORT_HIGH"
printf "${YELLOW}Alert level:${RESET} %s
" "$ALERT_LEVEL"
printf "${RED}Cut level:${RESET} %s
" "$CUT_LEVEL"
printf "
"

printf "${BOLD}${CYAN}Pullback ladder${RESET}
"
printf "${GREEN}1)${RESET} %s
" "$PULLBACK_1"
printf "${GREEN}2)${RESET} %s
" "$PULLBACK_2"
printf "${GREEN}3)${RESET} %s
" "$PULLBACK_3"
printf "
"

printf "${BOLD}${CYAN}Execution doctrine${RESET}
"
printf "${YELLOW}Plan:${RESET} %s
" "$PLAN_TEXT"
printf "${YELLOW}Campaign size:${RESET} %s
" "$CAMPAIGN_SIZE"
printf "${RED}Risk:${RESET} %s
" "$RISK_TEXT"
printf "${YELLOW}Tape truth:${RESET} %s
" "$TAPE_TRUTH"
printf "
"

printf "${BOLD}${CYAN}Execute only if all are true${RESET}
"
printf "[ ] Price is near level, not extended
"
printf "[ ] Structure still valid
"
printf "[ ] Size matches campaign plan
"
printf "[ ] Invalidation is defined first
"
printf "[ ] No emotional chase
"
printf "
"

printf "${BOLD}${CYAN}Livermore gate${RESET}
"
printf "[ ] Is the market confirming the idea?
"
printf "[ ] Is price acting better than my average?
"
printf "[ ] Am I adding only on proof?
"
printf "
"

printf "${BOLD}${CYAN}Operator note${RESET}
"
printf "${MAGENTA}Standardise the shell, change only token preset files.${RESET}
"
printf "
"
