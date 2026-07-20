#!/data/data/com.termux/files/usr/bin/bash
set -e
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.config/uvdm"
cat > "$HOME/.config/uvdm/bootstrap.sh" <<'BOOT'
export PATH="$HOME/.local/bin:$PATH"
[ -x "$HOME/.local/bin/deploy" ] || true
BOOT
for f in "$HOME/.bashrc" "$HOME/.profile"; do
  touch "$f"
  grep -q 'source "$HOME/.config/uvdm/bootstrap.sh"' "$f" || printf '\n[ -f "$HOME/.config/uvdm/bootstrap.sh" ] && source "$HOME/.config/uvdm/bootstrap.sh"\n' >> "$f"
done
cat > "$HOME/.local/bin/deploy" <<'WRAP'
#!/data/data/com.termux/files/usr/bin/bash
exec "$HOME/NexpertUVDM-Automation/tools/deploy" "$@"
WRAP
chmod +x "$HOME/.local/bin/deploy"
cat > "$HOME/.local/bin/mkt" <<'WRAP'
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/NexpertUVDM-Automation" || exit 1
if [ $# -eq 0 ]; then
  exec bash "$HOME/NexpertUVDM-Automation/output/xrpeasy_market_live.sh"
fi
case "${1,,}" in
  xlm) exec bash "$HOME/NexpertUVDM-Automation/output/xrpeasy_market_live.sh" ;;
  flr) exec bash "$HOME/NexpertUVDM-Automation/output/flreasy_market_live.sh" ;;
  sgb) exec bash "$HOME/NexpertUVDM-Automation/output/sgbeasy_market_live.sh" ;;
  xrp) exec bash "$HOME/NexpertUVDM-Automation/.xrpeasy_market" ;;
  *) echo "Usage: mkt [xlm|flr|sgb|xrp]"; exit 1 ;;
esac
WRAP
chmod +x "$HOME/.local/bin/mkt"
cat > "$HOME/.local/bin/gcheck" <<'WRAP'
#!/data/data/com.termux/files/usr/bin/bash
exec git status -sb
WRAP
chmod +x "$HOME/.local/bin/gcheck"
cat > "$HOME/.local/bin/gpush" <<'WRAP'
#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$HOME/NexpertUVDM-Automation" || exit 1
git status -sb
git fetch origin
git pull --rebase origin main
if git diff --quiet && git diff --cached --quiet; then
  echo "✅ No changes to commit. main already up to date."
  exit 0
fi
git diff --stat
git add .
git commit -m "${1:-update}"
git push origin main
WRAP
chmod +x "$HOME/.local/bin/gpush"
for a in deploy mkt gcheck gpush; do
  sed -i "/alias $a=/d" "$HOME/.bashrc" || true
done
printf '%s\n' '✅ UVDM hardened wrappers installed' 'Run: source ~/.bashrc' 'Then test: command -v deploy && command -v mkt && command -v gcheck && command -v gpush'
