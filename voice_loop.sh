#!/data/data/com.termux/files/usr/bin/bash

jesse_say() {
  termux-tts-speak "Jesse says: $1"
}

ron_say() {
  termux-tts-speak "Ron says: $1"
}

while true; do
  CMD="$(termux-speech-to-text 2>/dev/null | tr '[:upper:]' '[:lower:]')"

  case "$CMD$" in
    ""|"error: error_no_match"|"error: error_network")
      sleep 1
      continue
      ;;
  esac

  echo "HEARD: $CMD"

  case "$CMD" in
    *price*xlm*|*xlm*price*|*ixlm*|*xlm*phil*price*|*lm*fill*price*)
      ron_say "X L M price request logged. Pulling your X L M report now."
      xlm
      ;;

    *btc*|*bitcoin*)
      ron_say "B T C is the macro driver. Any new deployment gets checked against its structure first."
      btc
      ;;

    *wake*up*jesse*|*jesse*|*jessie*)
      jesse_say "Jesse online. Stay sharp and wait for confirmation."
      ;;

    *ron*wake*up*|*wake*up*ron*|*ron*)
      ron_say "Ron online. Systems are up."
      ;;

    *)
      jesse_say "Command not wired yet. Log it and add a case when you are ready."
      ;;
  esac
done
