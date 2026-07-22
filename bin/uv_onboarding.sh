#!/usr/bin/env bash
C_CYN=$'\u001B[1;36m'
C_GRN=$'\u001B[1;32m'
C_YLW=$'\u001B[1;33m'
C_DIM=$'\u001B[2;37m'
C_MAG=$'\u001B[1;35m'
C_RST=$'\u001B[0m'

printf '%b
' "${C_CYN}#UVDM Wingman TM${C_RST}"
printf '%b
' "${C_GRN}Digital Immortal Number 001${C_RST}"
printf '%b
' "${C_GRN}DIN 150868001${C_RST}"
printf '%s
' '────────────────────────────────'
printf '
'
printf '%bHOME:%b %s
' "$C_DIM" "$C_RST" "$HOME"
printf '%bLOCATION:%b %s
' "$C_DIM" "$C_RST" "$PWD"
printf '%bREPO:%b %s
' "$C_DIM" "$C_RST" "$HOME/NexpertUVDM-Automation"
printf '
'
printf '%bDeploy syntax:%b <amount-usdt> <symbol> <spot|long|futures> <1x|3x|5x|7x|10x> <dry|live>
' "$C_MAG" "$C_RST"
printf '%s
' 'Number is always treated as USDT; long = futures; spot implies 1x.'
printf '
'
printf '%bMarket onboarding%b
' "$C_CYN" "$C_RST"
printf '%s
' '  mkt           → market scan / live cockpit'
printf '%s
' '  status        → status'
printf '%s
' '  summary       → summary'
printf '%s
' '  gcheck        → git status'
printf '%s
' '  gpush         → git push origin main'
printf '%s
' '  restoreuvdm   → restore runtime'
printf '%s
' '  live          → live dashboard'
printf '
'
printf '%bUV ticker commands%b
' "$C_CYN" "$C_RST"
printf '%s
' '  uvxrp uvxlm uvbtc uvsgb uvflr uvpaxg'
printf '%s
' '  Rule: any supported ticker may use uv prefix.'
printf '
'
printf '%bSpecific hex%b
' "$C_CYN" "$C_RST"
printf '%s
' '  hex           : 0x9f1a •••• 7f28'
printf '%s
' '  hexers        : UVDM Ultrasafe Virtual Digital Machine book readers, specifically'
printf '
'
printf '%bDoctrine%b
' "$C_CYN" "$C_RST"
printf '%s
' 'I do not predict; I wait for proof.'
printf '%s
' 'I do not chase; I manage what is live.'
printf '%s
' 'I do not hope; I define invalidation first.'
printf '
'
printf '%bTape truth:%b Obey. Do not argue.
' "$C_YLW" "$C_RST"
printf '%bProcess over outcome.%b No revenge trading.
' "$C_YLW" "$C_RST"
