cd ~/NexpertUVDM-Automation

cat > uvdm_master.py << 'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from wyckoff_trend_wrapper_v2 import WyckoffTrendWrapper
except Exception:
    WyckoffTrendWrapper = None

RESET = "\u001B[0m"
RED = "\u001B[31m"
GREEN = "\u001B[32m"
YELLOW = "\u001B[33m"
CYAN = "\u001B[36m"
MAGENTA = "\u001B[35m"
WHITE = "\u001B[97m"
BOLD = "\u001B[1m"
GOLD = "\u001B[93m"

APP_NAME = "UVDM MASTER"
APP_VERSION = "6.1-riskflow"
ROOT = Path(os.getenv("UVDM_ROOT", str(Path.home() / "NexpertUVDM-Automation")))
CONFIG_DIR = ROOT / "config"
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "output"
STATE_PATH = Path(os.getenv("UVDM_STATE_FILE", str(Path.home() / ".xrpeasy_onboarding_state.json")))
LEGACY_IDENTITY_FILE = ROOT / "uvdm_identity.json"
EXECUTION_LOG = LOG_DIR / "execution_log.jsonl"
RECEIPT_DIR = LOG_DIR / "receipts"

for d in (CONFIG_DIR, LOG_DIR, OUTPUT_DIR, RECEIPT_DIR):
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class UserProfile:
    key: str
    name: str
    confirms: int
    cooldown: int
    max_pct: float
    live_enabled: bool


@dataclass
class OrderIntent:
    intent_id: str
    ts: str
    user_key: str
    user_name: str
    identity_name: str
    identity_number: str
    venue: str
    mode: str
    market: str
    symbol: str
    side: str
    portfolio_usd: float
    usdt_amount: float
    notional_usd: float
    asset_amount: float
    leverage: float
    max_pct: float
    limit_value_usd: float
    entry_style: str = "ladder"
    stop_loss_pct: Optional[float] = None
    tp_ladder: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    idempotency_key: str = ""


FOUNDER = UserProfile("founder", "XRPeasy Digital Solutions Founder", 2, 5, 0.05, True)
HEIR = UserProfile("heir", "XRPeasy Digital Solutions Heir", 7, 30, 0.01, False)
NEW_USER = UserProfile("new_user", "New User", 2, 3, 0.02, False)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def parse_money(text: str) -> float:
    s = text.strip().lower().replace(",", "").replace("$", "").replace("usdt", "").strip()
    mult = 1.0
    if s.endswith("k"):
        mult = 1000.0
        s = s[:-1]
    elif s.endswith("m"):
        mult = 1000000.0
        s = s[:-1]
    return float(s) * mult


def smart_round(value: float) -> float:
    if value >= 1000:
        return round(value / 50.0) * 50.0
    if value >= 100:
        return round(value / 10.0) * 10.0
    if value >= 10:
        return round(value / 2.0) * 2.0
    return round(value, 4)


def leverage_colour(leverage: float) -> str:
    if leverage >= 10:
        return RED
    if leverage >= 7:
        return YELLOW
    return GREEN


def format_compact(value: float, decimals: int = 2) -> str:
    if value >= 1000000:
        return f"{value / 1000000:.2f}m"
    if value >= 1000:
        return f"{value / 1000:.2f}k"
    return f"{value:.{decimals}f}"


class TTS:
    @staticmethod
    def speak(text: str) -> None:
        try:
            if shutil.which("termux-tts-speak"):
                subprocess.run(
                    ["termux-tts-speak", "-r", "1.0", "-p", "1.0", text],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass


def prompt_nonempty(label: str) -> str:
    while True:
        v = input(label).strip()
        if v:
            return v
        print("This value cannot be empty, sir.")
        TTS.speak("This value cannot be empty, sir.")


def prompt_money(label: str) -> float:
    while True:
        raw = input(label).strip()
        try:
            v = parse_money(raw)
            if v <= 0:
                print("Value must be greater than zero, sir.")
                continue
            return v
        except ValueError:
            print("Invalid amount, sir. Try 500, 5000, 50k, or 1.2m.")


def prompt_leverage(label: str) -> float:
    while True:
        raw = input(label).strip().lower().replace("x", "")
        try:
            lev = float(raw)
            if lev <= 0:
                print("Leverage must be greater than zero, sir.")
                continue
            if lev > 10:
                print("Max leverage is 10x, sir. Recommendation remains 5x.")
                continue
            return lev
        except ValueError:
            print("Invalid leverage, sir. Try 3, 5, 7, or 10.")


def prompt_yes_no(question: str) -> bool:
    while True:
        ans = input(f"{question} [yes/no]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer yes or no, sir.")


def get_symbol() -> str:
    while True:
        symbol = input("Symbol (e.g. XLM/USDT): ").strip().upper()
        if not symbol:
            print("Symbol cannot be empty, sir.")
            continue
        if "/" not in symbol and len(symbol) >= 6 and symbol.endswith("USDT"):
            base = symbol[:-4]
            quote = symbol[-4:]
            symbol = f"{base}/{quote}"
            print(f"Normalising symbol to {symbol}, sir.")
        return symbol


def extract_base_symbol(symbol: str) -> str:
    return symbol.split("/")[0].upper()


class IdentityManager:
    def __init__(self, state_path: Path = STATE_PATH, legacy_path: Path = LEGACY_IDENTITY_FILE):
        self.state_path = state_path
        self.legacy_path = legacy_path

    def load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default
        return default

    def save_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_identity(self) -> Dict[str, Any]:
        state = self.load_json(self.state_path, {})
        if state.get("identity_bound"):
            return {
                "source": "state",
                "digital_immortal_name": state.get("display_identity", "UVDM Bound Identity"),
                "digital_immortal_number": state.get("immortal_id", "uvdm-unset"),
                "first_user_hex": state.get("first_user_hex"),
                "device_label": state.get("device_label"),
                "state": state,
            }

        legacy = self.load_json(self.legacy_path, {})
        first_user = legacy.get("first_user")
        if first_user:
            return {
                "source": "legacy",
                "digital_immortal_name": first_user.get("digital_immortal_name", "UVDM Legacy User"),
                "digital_immortal_number": first_user.get("digital_immortal_number", "legacy-unset"),
                "first_user_hex": first_user.get("first_user_hex"),
                "device_label": None,
                "state": legacy,
            }

        return {"source": "unbound", "digital_immortal_name": "UNBOUND", "digital_immortal_number": "UNBOUND"}

    def require_onboarding_binding(self) -> Dict[str, Any]:
        print(f"{CYAN}First-use onboarding and binding required, sir.{RESET}")
        print("Open onboarding flow and bind from book with the first-user hex.")
        first_user_hex = prompt_nonempty("First-user hex from book: ")
        identity_name = prompt_nonempty("Digital Immortal Name: ")
        identity_number = prompt_nonempty("Digital Immortal Number: ")
        state = {
            "identity_bound": True,
            "display_identity": identity_name,
            "immortal_id": identity_number,
            "first_user_hex": first_user_hex,
            "bound_at": utc_now(),
        }
        self.save_json(self.state_path, state)
        self.save_json(
            self.legacy_path,
            {
                "first_user": {
                    "digital_immortal_name": identity_name,
                    "digital_immortal_number": identity_number,
                    "first_user_hex": first_user_hex,
                    "bound_at": state["bound_at"],
                }
            },
        )
        return {
            "source": "state",
            "digital_immortal_name": identity_name,
            "digital_immortal_number": identity_number,
            "first_user_hex": first_user_hex,
            "device_label": None,
            "state": state,
        }


class Journal:
    def __init__(self, log_path: Path = EXECUTION_LOG, receipt_dir: Path = RECEIPT_DIR):
        self.log_path = log_path
        self.receipt_dir = receipt_dir

    def append(self, event: Dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "
")

    def write_receipt(self, intent: OrderIntent, payload: Dict[str, Any]) -> Path:
        self.receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = self.receipt_dir / f"{intent.intent_id}.json"
        receipt_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return receipt_path


class RiskEngine:
    def validate(self, user: UserProfile, intent: OrderIntent) -> None:
        if intent.usdt_amount <= 0:
            raise ValueError("Actual USDT amount must be greater than zero")
        if intent.notional_usd <= 0:
            raise ValueError("Notional must be greater than zero")
        if intent.portfolio_usd <= 0:
            raise ValueError("Portfolio value must be greater than zero")
        if intent.usdt_amount > intent.limit_value_usd:
            raise ValueError(
                f"Requested actual USDT ${intent.usdt_amount:,.2f} exceeds allowed max ${intent.limit_value_usd:,.2f}"
            )
        if intent.mode == "live" and not user.live_enabled:
            raise ValueError(f"Live mode not permitted for profile {user.name}")
        if intent.market == "spot" and intent.leverage != 1.0:
            raise ValueError("Spot market must use 1x leverage")
        if intent.leverage <= 0 or intent.leverage > 10:
            raise ValueError("Leverage must be between 1x and 10x")
        if intent.venue not in {"paper_router", "spot_router", "xrpl_amm", "live_router"}:
            raise ValueError(f"Unsupported venue: {intent.venue}")


class ExecutionAdapter:
    name = "base"

    def preview_order(self, intent: OrderIntent) -> Dict[str, Any]:
        raise NotImplementedError

    def validate_order(self, intent: OrderIntent) -> None:
        raise NotImplementedError

    def place_order(self, intent: OrderIntent) -> Dict[str, Any]:
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "order_id": order_id}

    def sync_positions(self) -> Dict[str, Any]:
        return {"status": "not_implemented", "positions": []}


class DryRunAdapter(ExecutionAdapter):
    name = "dry_run"

    def preview_order(self, intent: OrderIntent) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": intent.mode,
            "status": "preview",
            "intent": asdict(intent),
            "message": "Dry-run preview generated. No live order sent.",
        }

    def validate_order(self, intent: OrderIntent) -> None:
        return None

    def place_order(self, intent: OrderIntent) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "status": "simulated",
            "intent_id": intent.intent_id,
            "simulated_order_id": f"dry-{intent.intent_id[:8]}",
            "message": "Dry-run only. Execution intentionally simulated.",
        }


class LiveGateAdapter(ExecutionAdapter):
    name = "live_gate"

    def preview_order(self, intent: OrderIntent) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": intent.mode,
            "status": "preview",
            "intent": asdict(intent),
            "message": "Live-gated adapter prepared. Broker-specific placement is not wired in this framework.",
        }

    def validate_order(self, intent: OrderIntent) -> None:
        required = [intent.symbol, intent.side, intent.market, intent.venue]
        if any(not x for x in required):
            raise ValueError("Missing required live execution fields")
        if intent.mode != "live":
            raise ValueError("Live adapter requires intent.mode == 'live'")

    def place_order(self, intent: OrderIntent) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "status": "gated",
            "intent_id": intent.intent_id,
            "message": "Live gate passed, but broker-specific order placement is intentionally not implemented.",
        }


class Router:
    def __init__(self):
        self.dry_run = DryRunAdapter()
        self.live_gate = LiveGateAdapter()

    def get_adapter(self, mode: str) -> ExecutionAdapter:
        return self.live_gate if mode == "live" else self.dry_run


class WyckoffDashboard:
    def __init__(self, journal: Journal):
        self.journal = journal

    def run_auto_dashboard(self) -> None:
        print("=" * 50)
        print(" UVDM AUTO DASHBOARD ".center(50))
        print("=" * 50)

        if WyckoffTrendWrapper is None:
            print(f"{YELLOW}wyckoff_trend_wrapper_v2.py not available. Dashboard disabled.{RESET}")
            self.journal.append(
                {
                    "ts": utc_now(),
                    "type": "dashboard_unavailable",
                    "reason": "wyckoff_trend_wrapper_v2 import failed",
                }
            )
            return

        wrapper = WyckoffTrendWrapper()
        tape_states = [
            ("FLR", "Phase B accumulation", "ST", "ST", "Testing supply. Waiting for Spring or SOS."),
            ("SGB", "Phase D accumulation", "SOS -> LPS", "LPS", "Demand holding support."),
            ("PAXG", "Phase A stopping action", "SC -> AR", "SC", "Violent selloff mapped. Wait."),
            ("XLM", "Phase D accumulation", "SOS -> BUEC -> LPS", "LPS", "Narrowing spreads on back-up."),
        ]

        results = []
        for state in tape_states:
            try:
                res = wrapper.process_tape_event(*state)
                results.append(res)
            except Exception as e:
                print(f"{RED}[ERROR]{RESET} {state[0]} -> {e}")
                self.journal.append(
                    {"ts": utc_now(), "type": "dashboard_error", "asset": state[0], "reason": str(e)}
                )

        print("")
        print("[ AUTO SUMMARY VIEW ]")
        for r in results:
            print(r.get("cockpit_summary", "<missing summary>"))

        print("")
        print("[ DETAILED ASSET STRUCTURE ]")
        for r in results:
            print(r.get("cockpit_detail", "<missing detail>"))
            print("-" * 40)

        print("")
        print("[ EXECUTION ROUTING TO UVDM_LIVE.PY ]")
        for r in results:
            asset = r.get("asset", "UNKNOWN")
            action_tag = r.get("action_tag", "none")
            print(f"Routing {asset.ljust(5)} -> action_tag: {action_tag}")

        self.journal.append(
            {
                "ts": utc_now(),
                "type": "dashboard_run",
                "assets": [r.get("asset") for r in results],
                "count": len(results),
            }
        )


class MasterConsole:
    def __init__(self, identity_manager: IdentityManager, journal: Journal, risk: RiskEngine, router: Router):
        self.identity_manager = identity_manager
        self.identity = identity_manager.get_identity()
        self.journal = journal
        self.risk = risk
        self.router = router
        self.dashboard = WyckoffDashboard(journal)

    def ensure_bound_identity(self) -> None:
        if self.identity.get("source") == "unbound":
            self.identity = self.identity_manager.require_onboarding_binding()

    def show_banner(self) -> None:
        print(f"{BOLD}{CYAN}UVDM Wingman TM 2025{RESET}")
        print(f"{WHITE}{self.identity['digital_immortal_name']}{RESET}")
        print(f"{GOLD}{self.identity['digital_immortal_number']}{RESET}")
        print(f"{GOLD}Process over outcome..{RESET}")
        print(f"{GOLD}No fear or Greed if you hope to succeed..{RESET}")
        print(f"{GREEN}Tape is the only source of Truth{RESET}")
        print(f"{MAGENTA}{APP_NAME} v{APP_VERSION}{RESET}")
        TTS.speak("U V D M Wingman online, sir.")

    def select_main_action(self) -> str:
        print("Select action:")
        print("1) Execution framework")
        print("2) Wyckoff auto dashboard")
        return "dashboard" if input("> ").strip() == "2" else "execution"

    def select_profile(self) -> UserProfile:
        print("Select profile:")
        print("1) Founder")
        print("2) XRPeasy Digital Solutions Heir")
        print("3) New User")
        choice = input("> ").strip()
        if choice == "2":
            return HEIR
        if choice == "3":
            self.ensure_bound_identity()
            return NEW_USER
        return FOUNDER

    def select_mode(self) -> str:
        print("Select mode:")
        print("1) Dry-run")
        print("2) Live-gated")
        return "live" if input("> ").strip() == "2" else "dry"

    def select_market(self) -> tuple[str, str]:
        print("Select market:")
        print("1) Futures / Long")
        print("2) Spot")
        print("3) Futures / Short")
        choice = input("> ").strip()
        if choice == "3":
            return "futures", "sell"
        if choice == "2":
            return "spot", "buy"
        return "futures", "buy"

    def select_venue(self, mode: str, market: str) -> str:
        if mode == "live":
            return "live_router"
        if market == "spot":
            return "spot_router"
        return "paper_router"

    def select_entry_style(self) -> str:
        print("Select entry style:")
        print("1) Adaptive Limit Ladder")
        print("2) Single Shot")
        return "single" if input("> ").strip() == "2" else "ladder"

    def prompt_reference_price(self, symbol: str) -> float:
        base = extract_base_symbol(symbol)
        return prompt_money(f"Reference price for {base} in USDT: ")

    def build_tp_ladder(self, entry_style: str) -> List[Dict[str, Any]]:
        if entry_style == "single":
            return [{"take_profit_pct": 2.0, "size": 1.0}]
        return [
            {"take_profit_pct": 1.0, "size": 0.25},
            {"take_profit_pct": 2.0, "size": 0.25},
            {"take_profit_pct": 3.0, "size": 0.50},
        ]

    def render_risk_block(self, intent: OrderIntent) -> None:
        colour = leverage_colour(intent.leverage)
        base = extract_base_symbol(intent.symbol)
        print("")
        print(f"{colour}{BOLD}[ RISK SNAPSHOT ]{RESET}")
        print(
            f"{colour}{intent.market.upper():<8}{RESET} | {base:<6} | side={intent.side:<4} | lev={intent.leverage:.0f}x | "
            f"actual={format_compact(intent.usdt_amount)} USDT | notional={format_compact(intent.notional_usd)} USDT | "
            f"size={format_compact(intent.asset_amount, 4)} {base}{RESET}"
        )
        if intent.entry_style == "ladder":
            print(f"{CYAN}Adaptive Limit Ladder{RESET} -> compact notional and asset sizing shown, sir.")
        else:
            print(f"{WHITE}Single Shot{RESET} -> one compact entry block, sir.")
        print(f"{GREEN}5x green{RESET} | {YELLOW}7x yellow{RESET} | {RED}10x red{RESET}")

    def build_intent(self, user: UserProfile, mode: str, market: str, side: str, venue: str) -> Optional[OrderIntent]:
        portfolio = prompt_money("Current total portfolio value in USD: ")
        symbol = get_symbol()
        reference_price = self.prompt_reference_price(symbol)
        leverage = 1.0 if market == "spot" else prompt_leverage("Leverage (recommend 5x, max 10x): ")
        entry_style = self.select_entry_style()

        while True:
            raw = input("Actual amount of USDT to deploy (or 'quit'): ").strip().lower()
            if raw in {"quit", "q", "exit"}:
                return None
            try:
                usdt_amount = parse_money(raw)
                if usdt_amount <= 0:
                    print("Actual USDT amount must be greater than zero, sir.")
                    continue
                break
            except ValueError:
                print("Invalid amount, sir. Try 500, 1000, 2.5k, or 10k.")

        limit_value = portfolio * user.max_pct
        notional = smart_round(usdt_amount * leverage)
        asset_amount = smart_round(notional / reference_price)
        intent = OrderIntent(
            intent_id=str(uuid.uuid4()),
            ts=utc_now(),
            user_key=user.key,
            user_name=user.name,
            identity_name=self.identity["digital_immortal_name"],
            identity_number=self.identity["digital_immortal_number"],
            venue=venue,
            mode=mode,
            market=market,
            symbol=symbol,
            side=side,
            portfolio_usd=portfolio,
            usdt_amount=usdt_amount,
            notional_usd=notional,
            asset_amount=asset_amount,
            leverage=leverage,
            max_pct=user.max_pct,
            limit_value_usd=limit_value,
            entry_style=entry_style,
            stop_loss_pct=1.0 if market == "spot" else 0.8,
            tp_ladder=self.build_tp_ladder(entry_style),
            notes=f"Clean rewritten Wingman master console intent ({entry_style})",
            idempotency_key=f"{user.key}-{extract_base_symbol(symbol)}-{side}-{int(time.time())}",
        )
        self.risk.validate(user, intent)
        self.render_risk_block(intent)
        return intent

    def confirm_intent(self, user: UserProfile, intent: OrderIntent) -> bool:
        print("")
        print(f"{user.name}, bound to {intent.identity_name} #{intent.identity_number}.")
        print(
            f"Portfolio: ${intent.portfolio_usd:,.2f} | Policy: {intent.max_pct * 100:.2f}% actual USDT per instruction "
            f"(max ${intent.limit_value_usd:,.2f})."
        )
        print(
            f"About to {intent.side} {intent.symbol} using actual ${intent.usdt_amount:,.2f} USDT, "
            f"notional ${intent.notional_usd:,.2f}, size {intent.asset_amount:,.4f}."
        )
        TTS.speak(
            f"Confirmation required. {intent.side} {extract_base_symbol(intent.symbol)} with {intent.usdt_amount:,.2f} dollars actual and {intent.notional_usd:,.2f} dollars notional."
        )
        for i in range(1, user.confirms + 1):
            if i < user.confirms:
                q = f"Confirmation {i} of {user.confirms}: execute, sir?"
            else:
                q = f"Confirmation {i} of {user.confirms}: final answer - execute now, sir?"
            if not prompt_yes_no(q):
                return False
            if i < user.confirms and user.cooldown > 0:
                time.sleep(user.cooldown)
        return True

    def execute(self, user: UserProfile, intent: OrderIntent) -> None:
        adapter = self.router.get_adapter(intent.mode)
        preview = adapter.preview_order(intent)
        self.journal.append(
            {"ts": utc_now(), "type": "preview", "intent_id": intent.intent_id, "payload": preview}
        )
        receipt_payload = {"intent": asdict(intent), "preview": preview}
        receipt_path = self.journal.write_receipt(intent, receipt_payload)
        print(f"{CYAN}Execution preview{RESET}")
        print(json.dumps(preview, indent=2))
        print(f"Receipt: {receipt_path}")

        if not self.confirm_intent(user, intent):
            self.journal.append(
                {
                    "ts": utc_now(),
                    "type": "cancelled",
                    "intent_id": intent.intent_id,
                    "reason": "User declined confirmation",
                }
            )
            print(f"{RED}Instruction cancelled by operator.{RESET}")
            return

        adapter.validate_order(intent)
        result = adapter.place_order(intent)
        self.journal.append(
            {"ts": utc_now(), "type": "execution_result", "intent_id": intent.intent_id, "payload": result}
        )
        final_receipt = {"intent": asdict(intent), "preview": preview, "result": result}
        self.journal.write_receipt(intent, final_receipt)
        print(f"{GREEN}Execution result{RESET}")
        print(json.dumps(result, indent=2))


def main() -> int:
    identity_manager = IdentityManager()
    journal = Journal()
    risk = RiskEngine()
    router = Router()
    console = MasterConsole(identity_manager, journal, risk, router)

    console.show_banner()
    action = console.select_main_action()
    if action == "dashboard":
        console.dashboard.run_auto_dashboard()
        return 0

    user = console.select_profile()
    mode = console.select_mode()
    market, side = console.select_market()
    venue = console.select_venue(mode, market)
    try:
        intent = console.build_intent(user, mode, market, side, venue)
        if intent is None:
            print(f"{YELLOW}No instruction created.{RESET}")
            return 0
        console.execute(user, intent)
        return 0
    except ValueError as e:
        print(f"{RED}Validation failed: {e}{RESET}")
        journal.append({"ts": utc_now(), "type": "validation_failed", "reason": str(e)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
EOF

python -m py_compile uvdm_master.py && echo "✅ Complete working code restored."