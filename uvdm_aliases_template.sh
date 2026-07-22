# Colors and Formatting
C_CYN=$'\u001B[1;36m'
C_GRN=$'\u001B[1;32m'
C_YLW=$'\u001B[1;33m'
C_DIM=$'\u001B[2;37m'
C_RST=$'\u001B[0m'

# Identity & Hex definition
export UVDM_HEX="0x9f1a2b3c4d5e6f78910a11b12c13d14e15f16a17b18c19d20e21f22a23b24c25d26e27f28"
export UVDM_HEXERS="UVDM Book Reader"
MASKED_HEX="${UVDM_HEX:0:6} •••• ${UVDM_HEX: -4}"

# Core Git & System
alias gcheck='git status'
alias gpush='git push origin main'
alias deploy='uvdm_deploy_script_here'
alias status='uvdm_status_script_here'
alias summary='python ~/NexpertUVDM-Automation/uv_auto_dashboard.py'
alias good1='echo "Mark last good config"'
alias lastgood='restoreuvdm_last_good'
alias restoreuvdm='bash scripts/restore_uvdm.sh'

# UVDM Bots
alias uvmon='python uv_monitor.py'
alias uvxrp='python uv_xrp_bot.py'
alias uvxlm='python uv_xlm_bot.py'
alias uvbtc='python uv_btc_bot.py'
alias uvsgb='python uv_sgb_bot.py'
alias uvflr='python uv_flr_bot.py'
alias uvpaxg='python uv_paxg_bot.py'
alias live='python uv_live_dashboard.py'
alias mkt='python uv_market_scan.py'

# Generic UV launcher
uv() {
  local tkr="$1"
  if [ -z "$tkr" ]; then
    echo -e "${C_YLW}Usage: uv <ticker>${C_RST}"
    return 1
  fi
  python "uv_${tkr,,}_bot.py"
}

# Full glossary (invoked by 'hex')
hex() {
  echo -e "${C_CYN}FULL UVDM GLOSSARY${C_RST}"
  echo "  hex           : ${UVDM_HEX}"
  echo "  hexers        : ${UVDM_HEXERS}"
}

# The Welcome HUD (Runs on new terminals)
uv_onboarding() {
  cat <<EOF3
${C_CYN}#UVDM Wingman TM${C_RST}
Digital Immortal Number 001 | DIN 150868001
─────────────────────────────────────────────────────────────────
${C_DIM}REPO: ~/home | SYSTEM: Active${C_RST}

${C_GRN}IDENTITY${C_RST}
  Status   : BOUND
  Access   : ${UVDM_HEXERS}
  Hex ID   : ${C_CYN}${MASKED_HEX}${C_RST}

${C_GRN}DEPLOYMENT${C_RST}
  Syntax   : <usdt> <ticker> <spot|futures> <leverage> <dry|live>
  Example  : 500 xlm futures 10x live

${C_CYN}MARKET ONBOARDING${C_RST}
  mkt         → market scan / live cockpit
  status      → status
  summary     → ${C_GRN}summary${C_RST} (PnL & performance)
  gcheck      → git status
  gpush       → git push origin main
  restoreuvdm → restore runtime
  live        → live dashboard

${C_GRN}UV TICKER COMMANDS${C_RST}
  uvxrp uvxlm uvbtc uvsgb uvflr uvpaxg
  Rule: any supported ticker may use uv prefix (e.g. uv eth).

${C_YLW}DOCTRINE${C_RST}
  I do not predict; I wait for proof.
  I don't buy spot, I wait at levels.
  I do not hope; I define invalidation first.
  
  Tape truth: Obey. Do not argue.
  Process over outcome. No revenge trading.

EOF3
}
