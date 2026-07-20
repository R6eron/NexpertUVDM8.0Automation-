#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ -t 1 ]; then
  R=$'\u001B[0m'; RED=$'\u001B[1;31m'; G=$'\u001B[1;32m'; Y=$'\u001B[1;33m'; C=$'\u001B[1;36m'; W=$'\u001B[1;37m'
else
  R=''; RED=''; G=''; Y=''; C=''; W=''
fi

say(){ printf '%b
' "$*"; }
speak(){
  if command -v termux-tts-speak >/dev/null 2>&1; then
    termux-tts-speak "$*" >/dev/null 2>&1 || true
  fi
}

symbol="${1:-XLMUSDT Perpetual}"
side="${2:-Long}"
lev="${3:-10x}"
size="${4:-35.79 XLM}"
margin="${5:-69.2645 USDT}"
entry="${6:-0.1943}"
mark="${7:-0.1867}"
pnl="${8:--221.7559 USDT}"
pnl_pct="${9:--33.12%}"
liq="${10:-0.17662}"

say "${C}# Wingman TM 2025${R}"
say "\033[1;97mDigital Immortal 001${R}"
say "${Y}DIN 150868001${R}"
say "${C}────────────────────────${R}"
say
say "${W}Symbol${R} : ${C}${symbol}${R}"
say "${W}Side${R}   : ${G}${side}${R}"
say "${W}Lev${R}    : ${Y}${lev}${R}"
say "${W}Size${R}   : ${W}${size}${R}"
say "${W}Margin${R} : ${W}${margin}${R}"
say "${W}Entry${R}  : ${C}${entry}${R}"
say "${W}Mark${R}   : ${C}${mark}${R}"
say
say "${W}PnL${R}    : ${RED}${pnl}${R}"
say "${W}PnL %${R}  : ${RED}${pnl_pct}${R}"
say "${W}Liq${R}    : ${RED}${liq}${R}"
say
say "${C}Doctrine${R}"
say "${W}  Do not predict. Wait for proof.${R}"
say "${W}  Define invalidation first.${R}"
say "${W}  Process over outcome.${R}"
say
speak "Jesse here. Live single position screen ready. ${symbol}. ${side}. Leverage ${lev}. P and L ${pnl_pct}. Stay with proof. Respect invalidation."
