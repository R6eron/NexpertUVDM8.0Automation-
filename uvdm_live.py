import sys
import os
import json
import shutil
import subprocess
from pathlib import Path

try:
    import requests
except Exception:
    requests = None

C_RESET = "\u001B[0m"
C_CYAN = "\u001B[1;36m"
C_WHITE = "\u001B[1;37m"
C_GREEN = "\u001B[1;32m"
C_YELLOW = "\u001B[1;33m"
C_RED = "\u001B[1;31m"
C_MAGENTA = "\u001B[1;35m"

ROOT = Path("/data/data/com.termux/files/home/NexpertUVDM-Automation")
CFG_VENUE = ROOT / "config" / "execution_venue.json"
CFG_LEVELS = ROOT / "config" / "asset_levels.json"
VOICE_DIR = ROOT / "voice"

class UVDMLiveExecution:
    def __init__(self):
        self.max_exposure_usdt = 2000.0
        self.sharpe_gate = 3.1
        self.venue_cfg = self.load_json(CFG_VENUE, {
            "global_default": "bitrue",
            "owner_override": {"enabled": True, "owner_name": "Ron Lewis", "venue": "bitrue"},
            "allowed_venues": ["bitrue", "binance", "mexc", "bybit"]
        })
        self.asset_cfg = self.load_json(CFG_LEVELS, {})
        self.term_width = self.get_term_width()
        self.mobile_lock = os.environ.get("UVDM_MOBILE", "1") == "1"
        self.two_col = (self.term_width >= 96) and (not self.mobile_lock)

    def load_json(self, path, fallback):
        if path.exists():
            return json.loads(path.read_text())
        return fallback

    def get_term_width(self):
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            if size.columns and size.columns > 0:
                return size.columns
        except Exception:
            pass
        return 80

    def resolve_venue(self, onboarding_venue=None):
        owner = self.venue_cfg.get("owner_override", {})
        if owner.get("enabled", False):
            return owner.get("venue", "bitrue")
        if onboarding_venue:
            return onboarding_venue.lower()
        return self.venue_cfg.get("global_default", "bitrue")

    def raw_len(self, s):
        out = ""
        in_esc = False
        for ch in s:
            if ch == "\u001B":
                in_esc = True
                continue
            if in_esc:
                if ch == "m":
                    in_esc = False
                continue
            out += ch
        return len(out)

    def fmt(self, k, v, color=C_WHITE):
        return f"{C_WHITE}{k}{C_RESET}: {color}{v}{C_RESET}"

    def print_row(self, left, right=None):
        if not right or not self.two_col:
            print(left)
            if right:
                print(right)
            return
        gap = 3
        if self.raw_len(left) + gap + self.raw_len(right) <= self.term_width:
            print(left + (" " * gap) + right)
        else:
            print(left)
            print(right)

    def fetch_live_price(self, asset):
        symbol = f"{asset.upper()}USDT"
        if requests:
            for url in (
                f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
                f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}",
            ):
                try:
                    r = requests.get(url, timeout=4)
                    data = r.json()
                    if "price" in data:
                        return float(data["price"])
                except Exception:
                    pass
        return None

    def level_context(self, asset, price):
        cfg = self.asset_cfg.get(asset.upper(), {})
        if asset.upper() == "XLM":
            defended = cfg.get("defended_levels", [0.20, 0.21])
            flush = cfg.get("flush_level", 0.1790)
            break_level = cfg.get("break_level", 0.2000)
            active_demand = cfg.get("active_demand", 0.2000)
        else:
            defended = cfg.get("defended_levels", [])
            flush = cfg.get("flush_level")
            break_level = cfg.get("break_level")
            active_demand = cfg.get("active_demand", min(defended) if defended else None)

        nearest_defended = None
        if defended:
            nearest_defended = min(defended, key=lambda x: abs(x - price))

        regime = "neutral"
        if defended and price >= min(defended):
            regime = "constructive"
        if flush and price <= flush:
            regime = "flush-risk"

        invalidation = flush if flush is not None else break_level

        return {
            "nearest_defended": nearest_defended,
            "flush_level": flush,
            "break_level": break_level,
            "active_demand": active_demand,
            "invalidation": invalidation,
            "regime": regime
        }

    def estimate_volatility(self, price, ctx):
        if ctx["flush_level"]:
            downside = max(price - ctx["flush_level"], 0.0001)
            return downside / price
        return 0.03

    def estimate_volume_score(self, price, ctx):
        if ctx["nearest_defended"] is None:
            return 0.5
        dist = abs(price - ctx["nearest_defended"]) / price
        score = max(0.2, min(1.0, 1.0 - dist * 12))
        return score

    def build_adaptive_ladder(self, asset, input_usdt, price, mode, leverage):
        ctx = self.level_context(asset, price)
        vol = self.estimate_volatility(price, ctx)
        vol_score = max(0.2, min(1.0, vol / 0.05))
        volume_score = self.estimate_volume_score(price, ctx)

        if asset.upper() == "XLM":
            ladder_prices = [
                round(price, 5),
                round(price * 0.996, 5),
                round(price * 0.9915, 5),
                round(price * 0.985, 5),
                0.18189,
                0.17920
            ]
            ladder_prices = sorted(set(ladder_prices), reverse=True)
            rung_count = len(ladder_prices)
            depth_pct = ((price - min(ladder_prices)) / price) if ladder_prices else 0.0
            weights = [0.95, 1.00, 1.10, 1.20, 1.45, 1.70][:rung_count]
        else:
            rung_count = 8 if vol_score < 0.4 else 10 if vol_score < 0.7 else 12
            if ctx["regime"] == "constructive":
                rung_count = max(6, rung_count - 2)

            depth_pct = 0.018 + (vol_score * 0.03)
            if ctx["regime"] == "constructive":
                depth_pct *= 0.75

            lower = price * (1 - depth_pct)
            spacing = (price - lower) / max(rung_count - 1, 1)
            ladder_prices = [round(price - (i * spacing), 5) for i in range(rung_count)]
            weights = []
            for i in range(rung_count):
                base = 1.0 + (i * 0.10)
                if ctx["flush_level"] and ladder_prices[i] <= max(ctx["flush_level"], lower):
                    base *= 1.25
                if volume_score > 0.7:
                    base *= 0.95
                weights.append(base)

        total_alloc = input_usdt
        weight_sum = sum(weights)
        ladder = []
        for i, rung_price in enumerate(ladder_prices):
            alloc = total_alloc * (weights[i] / weight_sum)
            qty = alloc / rung_price
            ladder.append({
                "rung": i + 1,
                "price": round(rung_price, 5),
                "alloc_usdt": round(alloc, 2),
                "qty_xlm": round(qty, 4)
            })

        voice = self.build_voice_summary(asset, mode, input_usdt, leverage, price, ctx, rung_count, depth_pct, volume_score)
        return {
            "ctx": ctx,
            "vol_score": round(vol_score, 3),
            "volume_score": round(volume_score, 3),
            "rung_count": rung_count,
            "depth_pct": round(depth_pct * 100, 2),
            "ladder": ladder,
            "voice": voice
        }

    def build_voice_summary(self, asset, mode, input_usdt, leverage, price, ctx, rung_count, depth_pct, volume_score):
        parts = []
        parts.append(f"Ron, {asset} {mode} is {ctx['regime']} at {price:.4f}.")
        if ctx["nearest_defended"] is not None:
            parts.append(f"Nearest defended level is {ctx['nearest_defended']:.3f}.")
        if ctx["flush_level"] is not None:
            parts.append(f"Flush risk sits near {ctx['flush_level']:.3f}.")
        parts.append(f"Option two is an adaptive ladder using {rung_count} rungs.")
        parts.append(f"Deploy amount is {input_usdt:.2f} U S D T at {leverage} x.")
        parts.append(f"Ladder depth is {depth_pct * 100:.2f} percent.")
        if volume_score > 0.7:
            parts.append("Volume support is constructive, so the ladder is compressed.")
        else:
            parts.append("Volume support is average, so bids are distributed more evenly.")
        return " ".join(parts)

    def short_voice_summary(self, asset, mode, price, ctx, rung_count, total_usdt=None, total_qty=None):
        voice_mode = "long" if mode == "futures" else mode
        base = f"Ron, {asset} {voice_mode} {ctx['regime']} at {price:.4f}. Opt 2 favored. {rung_count} rungs ready."
        if total_usdt is not None and total_qty is not None:
            return base + f" Total deploy is {total_usdt:.2f} U S D T, ladder size is {total_qty:.2f} {asset}."
        return base

    def speak_text(self, text):
        spoken = (
            text.replace("XLM", "X L M")
                .replace(" live ", " l-eye-v ")
                .replace("Live ", "L-eye-v ")
        )
        try:
            if shutil.which("termux-tts-speak"):
                subprocess.run(
                    ["termux-tts-speak", spoken],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return "termux-tts-speak"
        except Exception:
            pass
        return "silent"

    def save_voice(self, text):
        VOICE_DIR.mkdir(parents=True, exist_ok=True)
        wav = VOICE_DIR / "uvdm_voice_summary.wav"
        txt = VOICE_DIR / "uvdm_voice_summary.txt"
        txt.write_text(text)
        try:
            if shutil.which("espeak"):
                subprocess.run(["espeak", "-w", str(wav), text], check=False,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return wav, txt

    def render_single_shot(self, asset, action_tag, input_usdt, current_price, mode="spot", leverage=1, env_mode="live", onboarding_venue=None):
        self.two_col = False
        venue = self.resolve_venue(onboarding_venue)
        derived_xlm = input_usdt / current_price
        order_qty = int(derived_xlm)
        effective_notional = input_usdt * leverage

        print(f"{C_CYAN}=== UVDM LIVE EXECUTION ==={C_RESET}")
        self.print_row(self.fmt("Symbol", asset), self.fmt("Venue", venue, C_GREEN if venue == "bitrue" else C_YELLOW))
        self.print_row(self.fmt("Mode", mode.capitalize(), C_GREEN if mode == "spot" else C_YELLOW),
                       self.fmt("Bias", action_tag, C_GREEN))
        self.print_row(self.fmt("Price", f"{current_price:.4f}", C_CYAN))
        self.print_row(self.fmt("Input USDT", f"{input_usdt:.2f}"),
                       self.fmt("Derived XLM", f"{derived_xlm:.4f}", C_GREEN))
        self.print_row(self.fmt("Order Qty", f"{order_qty} {asset}", C_GREEN),
                       self.fmt("Lev", f"{leverage}x", C_YELLOW))
        if mode == "futures":
            self.print_row(self.fmt("Eff Notl", f"{effective_notional:.2f} USDT", C_MAGENTA))
        print("")
        print(f"{C_CYAN}ORDER{C_RESET}")
        self.print_row(self.fmt("Cmd", f"deploy {input_usdt:.0f} {asset.lower()} {mode} {leverage}x {env_mode}"))
        self.print_row(self.fmt("Route", "single shot", C_YELLOW),
                       self.fmt("Action", f"Buy {order_qty} {asset} @ {current_price:.4f}", C_MAGENTA))
        self.print_row(self.fmt("Status", "prepared for routing", C_GREEN))
        print("")

    def render_adaptive_ladder(self, asset, input_usdt, current_price, mode="spot", leverage=1, env_mode="live", onboarding_venue=None):
        self.two_col = False
        venue = self.resolve_venue(onboarding_venue)
        out = self.build_adaptive_ladder(asset, input_usdt, current_price, mode, leverage)
        ctx = out["ctx"]
        ladder = out["ladder"]
        full_voice = out["voice"]
        total_usdt = float(input_usdt)
        total_qty = round(sum(row["qty_xlm"] for row in ladder), 2)
        short_voice = self.short_voice_summary(asset, mode, current_price, ctx, out["rung_count"], total_usdt, total_qty)
        wav, txt = self.save_voice(full_voice)
        speaker = self.speak_text(short_voice)

        print(f"{C_CYAN}=== UVDM ADAPTIVE LADDER ==={C_RESET}")
        self.print_row(self.fmt("Symbol", asset), self.fmt("Venue", venue, C_GREEN if venue == "bitrue" else C_YELLOW))
        mode_label = "Long" if mode == "futures" else mode.capitalize()
        self.print_row(self.fmt("Mode", mode_label, C_GREEN if mode == "spot" else C_YELLOW),
                       self.fmt("Regime", ctx["regime"], C_GREEN if ctx["regime"] == "constructive" else C_YELLOW))
        self.print_row(self.fmt("Suggested", "2 adaptive ladder", C_MAGENTA),
                       self.fmt("Price", f"{current_price:.4f}", C_CYAN))
        self.print_row(self.fmt("Input", f"{input_usdt:.2f} USDT", C_WHITE),
                       self.fmt("Rungs", str(out["rung_count"]), C_YELLOW))
        self.print_row(self.fmt("Depth", f"{out['depth_pct']:.2f}%", C_MAGENTA),
                       self.fmt("VolScore", out["vol_score"], C_YELLOW))
        self.print_row(self.fmt("VolmScore", out["volume_score"], C_GREEN))
        if ctx["nearest_defended"] is not None:
            self.print_row(self.fmt("Defended", f"{ctx['nearest_defended']:.4f}", C_GREEN))
        if ctx["active_demand"] is not None:
            self.print_row(self.fmt("Active demand", f"{ctx['active_demand']:.4f}", C_GREEN))
        if ctx["break_level"] is not None:
            self.print_row(self.fmt("Break", f"{ctx['break_level']:.4f}", C_YELLOW))
        if ctx["flush_level"] is not None:
            self.print_row(self.fmt("Flush", f"{ctx['flush_level']:.4f}", C_RED))
        if ctx["invalidation"] is not None:
            self.print_row(self.fmt("Invalidation", f"{ctx['invalidation']:.4f}", C_RED))
        print("")
        print(f"{C_CYAN}LADDER{C_RESET}")
        for row in ladder:
            if row["rung"] == 1:
                color = C_GREEN
            elif row["rung"] == 2:
                color = C_YELLOW
            elif row["rung"] == 3:
                color = C_MAGENTA
            else:
                color = C_WHITE
            print(f"{color}R{row['rung']:<2}{C_RESET}  {row['price']:.5f}  ${row['alloc_usdt']:.2f}  {row['qty_xlm']:.4f}")
            if row["rung"] == 3:
                print("")
        print("")
        total_usdt = float(input_usdt)
        total_qty = round(sum(row["qty_xlm"] for row in ladder), 2)
        if mode == "futures":
            eff_notional = round(float(input_usdt) * leverage, 2)
            print(f"{C_WHITE}TOTALS{C_RESET}  {C_YELLOW}${total_usdt:.2f}{C_RESET}  {C_GREEN}{total_qty:.2f} {asset}{C_RESET}  {C_MAGENTA}Eff ${eff_notional:.2f}{C_RESET}")
        else:
            print(f"{C_WHITE}TOTALS{C_RESET}  {C_YELLOW}${total_usdt:.2f}{C_RESET}  {C_GREEN}{total_qty:.2f} {asset}{C_RESET}")
        print("")
        print(f"{C_CYAN}VOICE{C_RESET}")
        self.print_row(self.fmt("Now", short_voice, C_WHITE))
        self.print_row(self.fmt("Speak", speaker, C_GREEN if speaker != "silent" else C_RED))
        print("")

def main():
    live = UVDMLiveExecution()

    if len(sys.argv) < 6:
        print("Usage:")
        print("  python3 uvdm_live.py <USDT> <ASSET> <spot|futures|f> <LEVx> <live> [PRICE] [ROUTE] [VENUE]")
        print("  ROUTE: 1=single shot, 2=adaptive ladder")
        return

    input_usdt = float(sys.argv[1])
    asset = sys.argv[2].upper()
    mode = sys.argv[3].lower()
    lev_text = sys.argv[4].lower()
    env_mode = sys.argv[5].lower()

    if mode in ("f", "long"):
        mode = "futures"

    leverage = int(lev_text.replace("x", ""))

    manual_price = None
    route = "1"
    venue = None

    arg7 = sys.argv[6] if len(sys.argv) >= 7 else None
    arg8 = sys.argv[7] if len(sys.argv) >= 8 else None
    arg9 = sys.argv[8] if len(sys.argv) >= 9 else None

    if arg7:
        if arg7 in ("1", "2"):
            route = arg7
        else:
            try:
                manual_price = float(arg7)
            except ValueError:
                route = arg7

    if arg8:
        if arg8 in ("1", "2"):
            route = arg8
        else:
            venue = arg8

    if arg9:
        venue = arg9

    price = manual_price if manual_price is not None else live.fetch_live_price(asset)
    if price is None:
        price = 0.1850

    if route == "2":
        live.render_adaptive_ladder(asset, input_usdt, price, mode, leverage, env_mode, venue)
    else:
        live.render_single_shot(asset, "LPS_DEPLOY_ZONE", input_usdt, price, mode, leverage, env_mode, venue)

if __name__ == "__main__":
    main()
