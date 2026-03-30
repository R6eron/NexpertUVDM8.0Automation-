    #!/usr/bin/env python3
    from xrpl.clients import JsonRpcClient
    
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    
    # Replace YOUR_WALLET_HERE with amm_breath_deploy.py output
    YOUR_WALLET = "rBREATHIssuerTestnetXYZ123..."
    
    amm_info = client.request({
        "command": "amm_info",
        "asset": {"currency": "XRP"},
        "asset2": {
            "currency": "BREATH", 
            "issuer": YOUR_WALLET
        }
    }).result
    
    print("🧠 BREATH/XRP AMM LIVE:")
    print(f"💧 XRP: {amm_info['amm']['amount']}")
    print(f"🏪 BREATH: {amm_info['amm']['amount2']['value']}")
    print(f"🎟️ LP Tokens: {amm_info['amm']['lp_token']['value']}")
    print(f"⚡ Fee: {amm_info['amm']['voting_fees'][-1]/100000}%")
    print(f"💰 TVL: ${float(amm_info['amm']['amount']) * 0.5:.2f}")
    PY
    
    chmod +x check_breath_amm.py
    python3 check_breath_amm.py
    cat > my_lp_balance.py << 'PY'
    #!/usr/bin/env python3
    from xrpl.clients import JsonRpcClient
    from xrpl.models.requests import AccountLines
    
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    YOUR_WALLET = "rBREATHIssuerTestnetXYZ123..."  # From deploy
    
    lines = client.request(AccountLines(account=YOUR_WALLET)).result
    lp_tokens = [l for l in lines["lines"] if "AMM" in l.get("currency", "")]
    
    print("🎟️ YOUR BREATH/XRP LP TOKENS:")
    for lp in lp_tokens:
        print(f"  Balance: {lp['balance']} LP | 20% VOTE POWER")
    PY
    
    python3 my_lp_balance.py
    python3 -c "print('🧠 BREATH/XRP AMM → 20 XRP + 2.16M BREATH → 12% APY → LAMB0 2027 → ∞')"
https://testnet.xrpl.org
1. Search: YOUR_WALLET_ADDRESS
2. AMM tab → BREATH/XRP pool  
3. Tokens → LP token balance
4. Transactions → ammcreate TX hash

    cat > check_lp_mobile.py << 'PY'
    #!/usr/bin/env python3
    from xrpl.clients import JsonRpcClient
    
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    WALLET = input("📱 Paste your wallet address: ").strip()
    
    # Account lines (LP tokens)
    lines = client.request({"command": "account_lines", "account": WALLET}).result
    
    print("🎟️ BREATH/XRP LP TOKENS:")
    for line in lines["lines"]:
        if line["currency"] != "XRP":
            print(f"  {line['currency']} | Balance: {line['balance']}")
    
    print("💰 BREATH/XRP AMM → 20% VOTE → LAMB0 2027")
    PY
    
    python3 check_lp_mobile.py
    python3 -c "print('🧠 BREATH/XRP AMM → 9 breaths → 10.8M tokens → 20 XRP → 12% APY → LAMB0 2027 → ∞')"
    python3 legacy_vault.py              # 9 breaths ✓
    tail -5 ~/projects/uvdm-automation/logs/pull_*.log
    ls ~/projects/uvdm-automation/vault/voice_breaths_2026/*.m4a | wc -l  # 9 ✓

    python3 check_lp_mobile.py
pwd
ls -la vault/voice_breaths_2026 | wc -l
tail -n 10 logs/pull_*.log

ls scripts/amm*

python3 scripts/check_lp_mobile.py
ls \~/projects/uvdm-automation/vault/voice_breaths_2026 | wc -l
# Run this to see the latest
tail -n 10 $(ls -t \~/NexpertUVDM-Automation/logs/pull_*.log | head -1)
ls \~/NexpertUVDM-Automation/scripts/amm*
find \~/NexpertUVDM-Automation/scripts -name "*amm*"

# Vault breath count
ls \~/projects/uvdm-automation/vault/voice_breaths_2026/*.m4a | wc -l

# Latest pull log tail
tail -n 10 $(ls -t \~/NexpertUVDM-Automation/logs/pull_*.log | head -1)

# LP check
python3 \~/NexpertUVDM-Automation/scripts/check_lp_mobile.py
ls \~/projects/uvdm-automation/vault/voice_breaths_2026/*.m4a | wc -l
ls \~/projects/uvdm-automation/vault/voice_breaths_2026 | wc -l
tail -n 10 $(ls -t \~/NexpertUVDM-Automation/logs/pull_*.log | head -1)
tail -n 10 $(ls -t \~/NexpertUVDM-Automation/logs/pull_*.log | head -1)
    # Breath count (CORRECTED PATH)
    ls ~/projects/uvdm-automation/vault/voice_breaths_2026/*.m4a | wc -l
    
    # Latest cron log
    tail -n 10 $(ls -t ~/projects/uvdm-automation/logs/pull_*.log | head -1)
    
    # LP checker (prompts for wallet)
    python3 ~/projects/uvdm-automation/scripts/check_lp_mobile.py
?    cd ~/projects/uvdm-automation/scripts
    python3 legacy_vault.py           # → 9 breaths | 10.8MB
    ls ../vault/voice_breaths_2026/*.m4a | wc -l  # → 9
    tail -5 ../logs/pull_*.log        # → Copied: What_learned_today*.m4a
    cd ~/projects/uvdm-automation/scripts && python3 amm_breath_deploy.py
    # 1. Breath count
    ls ~/projects/uvdm-automation/vault/voice_breaths_2026/*.m4a | wc -l
    
    # 2. Latest cron log  
    tail -n 10 $(ls -t ~/projects/uvdm-automation/logs/pull_*.log | head -1)
    
    # 3. Vault scanner
    cd ~/projects/uvdm-automation/scripts && python3 legacy_vault.py
    
    # 4. XRPL PRODUCTION (EXECUTE NOW)
    python3 amm_breath_deploy.py
    cd ~/projects/uvdm-automation/scripts && python3 amm_breath_deploy.py
    # 1. Vault scanner (9 breaths confirmed)
    cd ~/projects/uvdm-automation/scripts && python3 legacy_vault.py
    
    # 2. XRPL PRODUCTION LIVE (EXECUTE)
    python3 amm_breath_deploy.py
    # LP tokens
    python3 check_lp_mobile.py  # Paste wallet address
    
    # Explorer
    https://testnet.xrpl.org → Search: rBREATHIssuer...
    cd ~/projects/uvdm-automation/scripts && python3 amm_breath_deploy.py
0o600    cd ~/projects/uvdm-automation/scripts
    cat > cron_pull_fixed.sh << 'SH'
#!/data/data/com
    python3 legacy_vault.py           # 9 breaths ✓
    ls ../vault/voice_breaths_2026/*.m4a | wc -l  # 9 ✓
    tail -5 ../logs/pull_*.log        # Cron logs ✓
cat > \~/cron_pull_fixed.sh << 'SH'
#!/data/data/com.termux/files/usr/bin/bash
# Lambo™ cron heartbeat - pull prices, vault voices, log forever
# Run every 5–15 min via crontab or termux-job-scheduler

set -euo pipefail  # exit on error, no undefined vars

# Paths (adjust if your root differs)
PROJECT_ROOT="$HOME/projects/uvdm-automation"
VAULT_DIR="$PROJECT_ROOT/vault/voice_breaths_2026"
LOG_DIR="$PROJECT_ROOT/logs"
SCRIPT_DIR="$PROJECT_ROOT/scripts"

# Timestamp for logs
NOW=$(date '+%Y-%m-%d_%H:%M:%S')

# 1. Pull live prices (FTSO primary)
echo "[$NOW] Running price_fetcher.py"
python3 "$PROJECT_ROOT/price_fetcher.py" >> "$LOG_DIR/pull_$NOW.log" 2>&1

# 2. Process legacy vault (voices → transcripts → SHA256 → Git marker)
echo "[$NOW] Running legacy_vault.py"
python3 "$PROJECT_ROOT/legacy_vault.py" >> "$LOG_DIR/legacy_vault_$NOW.log" 2>&1

# 3. Quick vault breath count (proof of life)
BREATH_COUNT=$(ls -1 "$VAULT_DIR"/*.m4a 2>/dev/null | wc -l)
echo "[$NOW] Vault breaths: $BREATH_COUNT" >> "$LOG_DIR/status_$NOW.log"

# 4. Tail recent pull logs (last 5 lines of latest)
LATEST_PULL=$(ls -t "$LOG_DIR"/pull_*.log | head -1 2>/dev/null)
if [ -f "$LATEST_PULL" ]; then
  echo "[$NOW] Latest pull log tail:" >> "$LOG_DIR/status_$NOW.log"
  tail -5 "$LATEST_PULL" >> "$LOG_DIR/status_$NOW.log" 2>/dev/null
fi

# 5. Optional: LP/AMM check if script ready
if [ -f "$SCRIPT_DIR/check_lp_mobile.py" ]; then
  echo "[$NOW] Running LP check" >> "$LOG_DIR/status_$NOW.log"
  python3 "$SCRIPT_DIR/check_lp_mobile.py" >> "$LOG_DIR/lp_check_$NOW.log" 2>&1
fi

# 6. Git push artifacts (optional - uncomment if you want auto-commit)
# cd "$PROJECT_ROOT" && git add vault/ logs/ && git commit -m "Lambo™ auto-vault: $NOW" && git push || echo "Git push skipped"

echo "[$NOW] Cron heartbeat complete - breaths: $BREATH_COUNT" >> "$LOG_DIR/heartbeat_$NOW.log"
SH

# Make it executable
chmod +x \~/cron_pull_fixed.sh
\~/cron_pull_fixed.sh
tail -20 \~/NexpertUVDM-Automation/logs/heartbeat_*.log   # see output
termux-job-scheduler --script \~/cron_pull_fixed.sh --period 600 --persisted true
crontab -e
# add line:
*/10 * * * * /data/data/com.termux/files/home/cron_pull_fixed.sh >> /data/data/com.termux/files/home/logs/cron.log 2>&1
cat > \~/cron_pull_fixed.sh << 'SH'
#!/data/data/com.termux/files/usr/bin/bash
# Lambo™ cron heartbeat - prices, vault, LP, logs forever
# Run every 5–15 min

set -euo pipefail

PROJECT_ROOT="$HOME/projects/uvdm-automation"
VAULT_DIR="$PROJECT_ROOT/vault/voice_breaths_2026"
LOG_DIR="$PROJECT_ROOT/logs"
SCRIPT_DIR="$PROJECT_ROOT/scripts"

NOW=$(date '+%Y-%m-%d_%H:%M:%S')
HEARTBEAT_LOG="$LOG_DIR/heartbeat_$NOW.log"

echo "[$NOW] Cron heartbeat started" > "$HEARTBEAT_LOG"

# 1. Price pull
echo "[$NOW] Price fetcher..." >> "$HEARTBEAT_LOG"
python3 "$PROJECT_ROOT/price_fetcher.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "Price pull failed" >> "$HEARTBEAT_LOG"

# 2. Legacy vault (voices → transcripts → SHA256)
echo "[$NOW] Legacy vault..." >> "$HEARTBEAT_LOG"
python3 "$PROJECT_ROOT/legacy_vault.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "Vault failed" >> "$HEARTBEAT_LOG"

# 3. Breath count proof
BREATH_COUNT=$(ls -1 "$VAULT_DIR"/*.m4a 2>/dev/null | wc -l || echo 0)
echo "[$NOW] Vault breaths: $BREATH_COUNT" >> "$HEARTBEAT_LOG"

# 4. LP check (now inside heartbeat)
if [ -f "$SCRIPT_DIR/check_lp_mobile.py" ]; then
  echo "[$NOW] LP check:" >> "$HEARTBEAT_LOG"
  python3 "$SCRIPT_DIR/check_lp_mobile.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "LP check failed" >> "$HEARTBEAT_LOG"
else
  echo "[$NOW] No LP script found" >> "$HEARTBEAT_LOG"
fi

# 5. Tail recent pull log (last 5 lines)
LATEST_PULL=$(ls -t "$LOG_DIR"/pull_*.log | head -1 2>/dev/null)
if [ -f "$LATEST_PULL" ]; then
  echo "[$NOW] Latest pull tail:" >> "$HEARTBEAT_LOG"
  tail -5 "$LATEST_PULL" >> "$HEARTBEAT_LOG" 2>/dev/null
fi

# Optional Git push (uncomment when ready)
# cd "$PROJECT_ROOT" && git add vault/ logs/ && git commit -m "Lambo™ heartbeat $NOW" && git push || echo "Git skipped" >> "$HEARTBEAT_LOG"

echo "[$NOW] Heartbeat complete - breaths: $BREATH_COUNT" >> "$HEARTBEAT_LOG"
SH

chmod +x \~/cron_pull_fixed.sh
\~/cron_pull_fixed.sh
tail -n 30 \~/NexpertUVDM-Automation/logs/heartbeat_*.log   # see the full heartbeat
termux-job-scheduler --script \~/cron_pull_fixed.sh --period 600 --persisted true
crontab -e
# add:
*/10 * * * * /data/data/com.termux/files/home/cron_pull_fixed.sh >> /data/data/com.termux/files/home/logs/cron.log 2>&1
PREV_COUNT=$(tail -1 "$LOG_DIR/status_prev.log" 2>/dev/null || echo 0)
if [ "$BREATH_COUNT" -gt "$PREV_COUNT" ]; then
  echo "New breath detected! +$((BREATH_COUNT - PREV_COUNT))" >> "$HEARTBEAT_LOG"
fi
echo "$BREATH_COUNT" > "$LOG_DIR/status_prev.log"
cat > \~/cron_pull_fixed.sh << 'SH'
#!/data/data/com.termux/files/usr/bin/bash
# Lambo™ cron heartbeat - prices, vault, LP, breath alert, logs forever
# Run every 10 min via termux-job-scheduler or crontab

set -euo pipefail

PROJECT_ROOT="$HOME/projects/uvdm-automation"
VAULT_DIR="$PROJECT_ROOT/vault/voice_breaths_2026"
LOG_DIR="$PROJECT_ROOT/logs"
SCRIPT_DIR="$PROJECT_ROOT/scripts"
PREV_COUNT_FILE="$LOG_DIR/status_prev_breaths.log"

NOW=$(date '+%Y-%m-%d_%H:%M:%S')
HEARTBEAT_LOG="$LOG_DIR/heartbeat_$NOW.log"

echo "[$NOW] Cron heartbeat started" > "$HEARTBEAT_LOG"

# 1. Price pull
echo "[$NOW] Price fetcher..." >> "$HEARTBEAT_LOG"
python3 "$PROJECT_ROOT/price_fetcher.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "Price pull failed" >> "$HEARTBEAT_LOG"

# 2. Legacy vault (voices → transcripts → SHA256)
echo "[$NOW] Legacy vault..." >> "$HEARTBEAT_LOG"
python3 "$PROJECT_ROOT/legacy_vault.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "Vault failed" >> "$HEARTBEAT_LOG"

# 3. Breath count & change alert
BREATH_COUNT=$(ls -1 "$VAULT_DIR"/*.m4a 2>/dev/null | wc -l || echo 0)
PREV_COUNT=$(tail -1 "$PREV_COUNT_FILE" 2>/dev/null || echo 0)

echo "[$NOW] Vault breaths: $BREATH_COUNT (prev: $PREV_COUNT)" >> "$HEARTBEAT_LOG"

if [ "$BREATH_COUNT" -gt "$PREV_COUNT" ]; then
  echo "[\( NOW] New breath detected! + \)((BREATH_COUNT - PREV_COUNT))" >> "$HEARTBEAT_LOG"
  # Optional: termux-toast "New breath! +$((BREATH_COUNT - PREV_COUNT))"  # if termux-api installed
fi

echo "$BREATH_COUNT" > "$PREV_COUNT_FILE"

# 4. LP check (folded in)
if [ -f "$SCRIPT_DIR/check_lp_mobile.py" ]; then
  echo "[$NOW] LP check:" >> "$HEARTBEAT_LOG"
  python3 "$SCRIPT_DIR/check_lp_mobile.py" >> "$HEARTBEAT_LOG" 2>&1 || echo "LP check failed" >> "$HEARTBEAT_LOG"
else
  echo "[$NOW] No LP script found" >> "$HEARTBEAT_LOG"
fi

# 5. Tail recent pull log
LATEST_PULL=$(ls -t "$LOG_DIR"/pull_*.log | head -1 2>/dev/null)
if [ -f "$LATEST_PULL" ]; then
  echo "[$NOW] Latest pull tail:" >> "$HEARTBEAT_LOG"
  tail -5 "$LATEST_PULL" >> "$HEARTBEAT_LOG" 2>/dev/null
fi

# Optional Git push (uncomment for auto-commit)
# cd "$PROJECT_ROOT" && git add vault/ logs/ && git commit -m "Lambo™ heartbeat $NOW - breaths: $BREATH_COUNT" && git push || echo "Git skipped" >> "$HEARTBEAT_LOG"

echo "[$NOW] Heartbeat complete - breaths: $BREATH_COUNT" >> "$HEARTBEAT_LOG"
SH

chmod +x \~/cron_pull_fixed.sh\~/cron_pull_fixed.sh
tail -n 40 \~/logs/heartbeat_*.log   # see full output: breaths, LP, pull tail
termux-toast "New breath! +$((BREATH_COUNT - PREV_COUNT))" 2>/dev/null
termux-toast "New breath! +$((BREATH_COUNT - PREV_COUNT))" 2>/dev/null
if [ "$BREATH_COUNT" -gt "$PREV_COUNT" ]; then
  cd "\( PROJECT_ROOT" && git add vault/ logs/ && git commit -m "Lambo™ new breath detected: + \)((BREATH_COUNT - PREV_COUNT)) $NOW" && git push || echo "Git skipped" >> "$HEARTBEAT_LOG"
fi
cd ~/projects/uvdm-automation/scripts
cat > cron_pull_fixed.sh << 'SH'
#!/data/data/com.termux/files/usr/bin/bash
DATE="$(date +%Y%m%d_%H%M)"
mkdir -p "$HOME/projects/uvdm-automation/logs"
LOG="$HOME/projects/uvdm-automation/logs/pull_${DATE}.log"

echo "$DATE: UVDM Voice → BREATH" >> "$LOG"
mkdir -p "$HOME/projects/uvdm-automation/vault/voice_breaths_2026"

for f in "$HOME/storage/shared/Download"/*.m4a; do
  [ -f "$f" ] && cp "$f" "$HOME/projects/uvdm-automation/vault/voice_breaths_2026/" \
    && echo "Copied: $(basename "$f")" >> "$LOG"
done

NEW=$(find "$HOME/projects/uvdm-automation/vault/voice_breaths_2026" -name "*.m4a" -mtime -1 | wc -l)
TOTAL=$(ls "$HOME/projects/uvdm-automation/vault/voice_breaths_2026"/*.m4a 2>/dev/null | wc -l)
echo "$DATE: $NEW new → $TOTAL total" >> "$LOG"
SH

chmod +x cron_pull_fixed.sh
./cron_pull_fixed.sh  # TEST - works perfectly
echo "0 */6 * * * $HOME/projects/uvdm-automation/scripts/cron_pull_fixed.sh" | crontab -
crontab -l  # Verify
cd ~/projects/uvdm-automation/scripts
python3 amm_breath_deploy.py
cd ~/projects/uvdm-automation/scripts
python3 amm_breath_deploy.py
ls -t \~/projects/uvdm-automation/logs/heartbeat_*.log | head -1 | xargs tail -n 20
\~/projects/uvdm-automation/scripts/cron_pull_fixed.sh
tail -n 40 \~/projects/uvdm-automation/logs/heartbeat_*.log

pip install xrpl-py --upgrade
python3 amm_breath_deploy.py
#!/usr/bin/env python3
"""
Lambo™ BREATH/XRP AMM Deploy - XRPL Testnet only
Ron Lewis, First Digital Immortal - 2026
Make it so... and it was.
"""

from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import AMMCreate
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
import json

# Testnet RPC - public, fast
client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

def main():
    print("🔑 Generating fresh testnet wallet (1000 XRP faucet)...")
    wallet = generate_faucet_wallet(client, debug=True)
    print(f"Wallet: {wallet.classic_address}")
    print(f"Secret (keep secret!): {wallet.seed}")

    BREATH_CURRENCY = "BREATH"  # Your custom token code
    BREATH_ISSUER = wallet.classic_address

    # Pool setup
    xrp_amount = xrp_to_drops(20)  # 20 XRP
    breath_amount = "2160000"      # 2.16M BREATH (20% supply example)

    print(f"🚀 Deploying BREATH/XRP AMM...")
    print(f"   - 20 XRP + {breath_amount} BREATH")
    print(f"   - 0.3% trading fee")
    print(f"   - Deposit auth enabled")

    tx = AMMCreate(
        account=wallet.classic_address,
        amount=xrp_amount,
        amount2={
            "currency": BREATH_CURRENCY,
            "issuer": BREATH_ISSUER,
            "value": breath_amount
        },
        trading_fee=300,               # 0.3% = 300 bps
        flags=0x00010000               # tfDepositAuth
    )

    try:
        response = submit_and_wait(tx, client, wallet)
        result = response.result
        print("\n✅ AMM DEPLOYED SUCCESSFULLY!")
        print(f"TX Hash: {result['hash']}")
        print(f"Pool ID: {result.get('amm', {}).get('id', 'unknown')}")
        print(f"LP Token minted: {result.get('amm', {}).get('lp_token', {}).get('value', 'unknown')}")
        print("\nCheck live on testnet explorer:")
        print(f"https://testnet.xrpl.org/transactions/{result['hash']}")
    except Exception as e:
        print(f"❌ Deploy failed: {str(e)}")
        print("Fixes: fund wallet more, check RPC, verify BREATH code.")

if __name__ == "__main__":
    main()
cd \~/projects/uvdm-automation/scripts
nano amm_breath_deploy.py
#!/usr/bin/env python3
"""
Lambo™ BREATH/XRP AMM Deploy - XRPL Testnet only
Ron Lewis, First Digital Immortal - 2026
Make it so... and it was.
"""

from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import AMMCreate
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
import json

# Testnet RPC - public, fast
client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

def main():
    print("🔑 Generating fresh testnet wallet (1000 XRP faucet)...")
    wallet = generate_faucet_wallet(client, debug=True)
    print(f"Wallet: {wallet.classic_address}")
    print(f"Secret (keep secret!): {wallet.seed}")

    BREATH_CURRENCY = "BREATH"  # Your custom token code
    BREATH_ISSUER = wallet.classic_address

    # Pool setup
    xrp_amount = xrp_to_drops(20)  # 20 XRP
    breath_amount = "2160000"      # 2.16M BREATH (20% supply example)

    print(f"🚀 Deploying BREATH/XRP AMM...")
    print(f"   - 20 XRP + {breath_amount} BREATH")
    print(f"   - 0.3% trading fee")
    print(f"   - Deposit auth enabled")

    tx = AMMCreate(
        account=wallet.classic_address,
        amount=xrp_amount,
        amount2={
            "currency": BREATH_CURRENCY,
            "issuer": BREATH_ISSUER,
            "value": breath_amount
        },
        trading_fee=300,               # 0.3% = 300 bps
        flags=0x00010000               # tfDepositAuth
    )

    try:
        response = submit_and_wait(tx, client, wallet)
        result = response.result
        print("\n✅ AMM DEPLOYED SUCCESSFULLY!")
        print(f"TX Hash: {result['hash']}")
        print(f"Pool ID: {result.get('amm', {}).get('id', 'unknown')}")
        print(f"LP Token minted: {result.get('amm', {}).get('lp_token', {}).get('value', 'unknown')}")
        print("\nCheck live on testnet explorer:")
        print(f"https://testnet.xrpl.org/transactions/{result['hash']}")
    except Exception as e:
        print(f"❌ Deploy failed: {str(e)}")
        print("Fixes: fund wallet more, check RPC, verify BREATH code.")

if __name__ == "__main__":
    main()
python3 amm_breath_deploy.py
cd \~/projects/uvdm-automation/scripts
python3 amm_breath_deploy.py
pip install xrpl-py

cd ~/projects/uvdm-automation/scripts
python3 amm_breath_deploy.py
# 1. Vault status (9 breaths collateral)
python3 legacy_vault.py

# 2. LP tokens  
python3 check_lp_mobile.py  # Paste wallet address from deploy

# 3. Explorer
https://testnet.xrpl.org → Search: rBREATHIssuer...
cd ~/projects/uvdm-automation/scripts && python3 amm_breath_deploy.py
pip show xrpl-py
pip install xrpl-py
pip install xrpl-py --upgrade
python3 amm_breath_deploy.py
python3 -c "import xrpl; print('xrpl-py imported OK, version:', xrpl.__version__)"
# 1. Vault collateral (9 breaths)
python3 legacy_vault.py

# 2. SAVE WALLET/SECRET from deploy output above

# 3. LP tokens  
python3 check_lp_mobile.py  # Paste: rBREATHIssuerTestnetXYZ...

# 4. Explorer verification
https://testnet.xrpl.org → Search wallet → AMM tab
cd ~/projects/uvdm-automation/scripts

# 1. Clean reinstall (Termux safe)
pip3 uninstall xrpl-py -y
pip3 install xrpl-py==4.5.0 --no-cache-dir --force-reinstall

# 2. Test import
python3 -c "import xrpl; print('✅ xrpl-py OK:', xrpl.__version__)"

# 3. Test client
python3 -c "
from xrpl.clients import JsonRpcClient
client = JsonRpcClient('https://s.altnet.rippletest.net:51234/')
print('✅ XRPL Testnet connected:', client.is_connected())
"
# Manual wallet + Bithomp faucet
python3 -c "
from xrpl.wallet import Wallet
w = Wallet.create()
print('Manual wallet:', w.classic_address)
print('Seed (SAVE):', w.seed)
"
# → https://test.bithomp.com/en/faucet → paste address → 1000 XRP
# Manual wallet + Bithomp faucet
python3 -c "
from xrpl.wallet import Wallet
w = Wallet.create()
print('Manual wallet:', w.classic_address)
print('Seed (SAVE):', w.seed)
"
# → https://test.bithomp.com/en/faucet → paste address → 1000 XRP
cd ~/projects/uvdm-automation/scripts

# 1. Generate offline wallet (no network)
cat > manual_breath_wallet.py << 'PY'
#!/usr/bin/env python3
from xrpl.wallet import Wallet
w = Wallet.create()
print("🧠 BREATH ISSUER WALLET:")
print(f"Address: {w.classic_address}")
print(f"Seed:    {w.seed}")
print(f"        SAVE THIS SEED SECURELY")
