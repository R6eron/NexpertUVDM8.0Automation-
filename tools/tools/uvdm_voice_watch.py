#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any, Dict, Optional

BASE = Path.home() / "NexpertUVDM-Automation"
RUNTIME = BASE / "runtime"
STATE_FILE = RUNTIME / "voice_watch_state.json"
WATCH_FILE = RUNTIME / "alerts.json"
LOG_FILE = RUNTIME / "voice_watch.log"
LAST_SPOKEN_FILE = RUNTIME / "voice_watch_last_spoken.txt"

DEFAULT_POLL_SECONDS = int(os.getenv("UVDM_WATCH_POLL", "15"))
DEFAULT_TRIGGER_ON_START = os.getenv("UVDM_WATCH_TRIGGER_ON_START", "0") == "1"
DEFAULT_AUTO_ON_EXECUTE_READY = os.getenv("UVDM_WATCH_AUTO_ON_EXECUTE_READY", "0") == "1"
DEFAULT_ONESHOT = os.getenv("UVDM_WATCH_ONESHOT", "0") == "1"
DEFAULT_DEBUG = os.getenv("UVDM_WATCH_DEBUG", "0") == "1"
DEFAULT_DRY_RUN = os.getenv("UVDM_WATCH_DRY_RUN", "0") == "1"
DEFAULT_SPEAK_OFF = os.getenv("UVDM_WATCH_SPEAK_OFF", "0") == "1"
DEFAULT_DEBOUNCE_SECONDS = int(os.getenv("UVDM_WATCH_DEBOUNCE", "45"))
DEFAULT_REPEAT_EXECUTE_SECONDS = int(os.getenv("UVDM_WATCH_EXECUTE_DEBOUNCE", "180"))
DEFAULT_NOTIFY = os.getenv("UVDM_WATCH_NOTIFY", "1") == "1"

UPPER_KEYS = {"asset", "symbol", "ticker", "tag"}
LOWER_KEYS = {"regime", "setup", "status", "state", "mode", "venue", "action", "operator_action"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def now_epoch() -> int:
    return int(time.time())

def ensure_runtime() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)

def append_text(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)

class WatchRuntime:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.debug_enabled = bool(args.debug)
        self.speak_enabled = not bool(args.speak_off)
        self.notify_enabled = bool(args.notify)
        self.voice_name = "TermuxVoice"
        self.voice_rate = 0.9
        self.voice_pitch = 0.85

    def log(self, msg: str, level: str = "INFO") -> None:
        line = f"[{utc_now()}] [{level}] {msg}\
"
        append_text(self.args.log_file, line)
        if self.debug_enabled or level in {"ERROR", "WARN"}:
            print(line, end="")

    def debug(self, msg: str) -> None:
        if self.debug_enabled:
            self.log(msg, level="DEBUG")

    def speak(self, msg: str) -> None:
        msg = compact_message(msg)
        if not msg:
            return
        append_text(self.args.last_spoken_file, msg + "\
")
        if not self.speak_enabled:
            self.debug(f"speak_off: {msg}")
            return
        try:
            if which("termux-tts-speak"):
                subprocess.run(["termux-tts-speak", msg], check=False)
            if self.notify_enabled and which("termux-notification"):
                subprocess.run([
                    "termux-notification",
                    "--title", "UVDM Wingman",
                    "--content", msg,
                ], check=False)
        except Exception as exc:
            self.log(f"speak failed: {type(exc).__name__}: {exc}", level="WARN")

def compact_message(msg: str) -> str:
    return " ".join(str(msg or "").split()).strip()

def load_json(path: Path, default: Any, rt: Optional[WatchRuntime] = None) -> Any:
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        if rt:
            rt.log(f"json load failed for {path}: {type(exc).__name__}: {exc}", level="WARN")
    return default

def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\
")
    os.replace(tmp, path)

def file_hash(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_value(key: str, value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, list):
        return [normalize_value(key, x) for x in value]
    if isinstance(value, dict):
        return normalize_alerts(value)
    text = compact_message(str(value))
    if key in UPPER_KEYS:
        return text.upper()
    if key in LOWER_KEYS:
        return text.lower()
    return text

def normalize_alerts(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        out: Dict[str, Any] = {}
        for key in sorted(data.keys()):
            out[str(key)] = normalize_value(str(key), data[key])
        return out
    if isinstance(data, list):
        return {"items": [normalize_value("items", x) for x in data]}
    if data is None:
        return {}
    return {"message": compact_message(str(data))}

def semantic_fingerprint(data: Dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def build_message(cur: Dict[str, Any], prev: Optional[Dict[str, Any]]) -> str:
    explicit = compact_message(cur.get("message", ""))
    if explicit:
        return explicit
    bits = []
    status = str(cur.get("status", "")).strip()
    regime = str(cur.get("regime", "")).strip()
    asset = str(cur.get("asset", "")).strip().upper()
    level = str(cur.get("level", "")).strip()
    if status:
        bits.append(f"status {status}")
    if regime:
        bits.append(f"regime {regime}")
    action = str(cur.get("operator_action", "")).strip().upper().replace(" ", "_")
    if action:
        bits.append(f"ACTION {action}")
    if asset:
        bits.append(asset)
    if level:
        bits.append(f"level {level}")
    if not bits and prev != cur:
        return "RISK: UVDM state changed. ACTION: Review only."
    return " | ".join(bits)

def whisper_wrap(message: str, cur: Dict[str, Any]) -> str:
    msg = compact_message(message)
    if not msg:
        return ""
    status = str(cur.get("status", "")).strip().lower()
    regime = str(cur.get("regime", "")).strip().lower()
    action = str(cur.get("operator_action", cur.get("action", ""))).strip().upper().replace(" ", "_")
    parts = []
    if status:
        parts.append(f"RISK: {status}")
    if regime:
        parts.append(f"PROCESS: regime {regime}")
    if action:
        parts.append(f"ACTION: {action}")
    parts.append("EMOTION: calm, detached, process over outcome")
    parts.append(msg)
    return " | ".join(parts)

def should_debounce(msg_fp: str, prev_state: Dict[str, Any], debounce_seconds: int) -> bool:
    last_fp = prev_state.get("last_message_fp")
    last_ts = int(prev_state.get("last_message_ts") or 0)
    return bool(last_fp and last_fp == msg_fp and (now_epoch() - last_ts) < debounce_seconds)

def should_debounce_execute(exec_fp: str, prev_state: Dict[str, Any], debounce_seconds: int) -> bool:
    last_fp = prev_state.get("last_execute_fp")
    last_ts = int(prev_state.get("last_execute_ts") or 0)
    return bool(last_fp and last_fp == exec_fp and (now_epoch() - last_ts) < debounce_seconds)

def maybe_auto_execute(cur: Dict[str, Any], prev_state: Dict[str, Any], rt: WatchRuntime):
    if not rt.args.auto_on_execute_ready:
        return False, ""
    status = str(cur.get("status", "")).strip().lower()
    voice_cmd = compact_message(cur.get("voice_cmd", ""))
    if status != "execute_ready" or not voice_cmd:
        rt.debug("auto_execute skipped: status/voice_cmd not ready")
        return False, ""
    exec_fp = semantic_fingerprint({
        "status": status,
        "voice_cmd": voice_cmd,
        "request_id": str(cur.get("request_id", "")),
    })
    if should_debounce_execute(exec_fp, prev_state, rt.args.repeat_execute_seconds):
        rt.debug(f"execute debounced: {voice_cmd}")
        return False, exec_fp
    rt.log(f"dry_run execute: {voice_cmd}" if rt.args.dry_run else f"execute: {voice_cmd}")
    return True, exec_fp

def step(prev_state: Dict[str, Any], start: bool, rt: WatchRuntime) -> Dict[str, Any]:
    cur_hash = file_hash(rt.args.watch_file)
    cur_alerts = normalize_alerts(load_json(rt.args.watch_file, {}, rt)) if rt.args.watch_file.exists() else {}
    cur_fp = semantic_fingerprint(cur_alerts)
    changed = (cur_hash != prev_state.get("watch_hash")) or (cur_fp != prev_state.get("alerts_fp"))
    rt.debug(f"step changed={changed} start={start} hash={cur_hash} fp={cur_fp}")

    new_state = dict(prev_state)
    new_state.update({
        "watch_hash": cur_hash,
        "alerts": cur_alerts,
        "alerts_fp": cur_fp,
        "last_seen_ts": utc_now(),
    })

    if changed and (rt.args.trigger_on_start or not start):
        msg = build_message(cur_alerts, prev_state.get("alerts"))
        status = str(cur_alerts.get("status", "")).strip().lower()
        setup = str(cur_alerts.get("setup", "")).strip().upper()
        regime = str(cur_alerts.get("regime", "")).strip().lower()
        if status == "execute_ready" and setup == "MANUAL_DEPLOY" and regime == "manual":
            level = str(cur_alerts.get("level", "")).strip()
            asset = str(cur_alerts.get("asset", "")).strip().upper()
            mode = str(cur_alerts.get("mode", "")).strip().lower()
            lev = str(cur_alerts.get("leverage", "")).strip()
            bits = []
            if level:
                bits.append(level)
            if asset:
                bits.append(asset)
            if mode:
                bits.append(mode)
            if lev:
                bits.append(lev)
            spec = " ".join(bits) or "this deploy"
            msg = f"set limit ladder or single shot for {spec}"
        wrapped = whisper_wrap(msg, cur_alerts)
        msg_fp = semantic_fingerprint({"message": wrapped}) if wrapped else ""
        if wrapped and not should_debounce(msg_fp, prev_state, rt.args.debounce_seconds):
            rt.log(f"trigger: {wrapped}")
            rt.speak(wrapped)
            new_state["last_message"] = wrapped
            new_state["last_message_fp"] = msg_fp
            new_state["last_message_ts"] = now_epoch()
        elif wrapped:
            rt.debug(f"message debounced: {wrapped}")
        executed, exec_fp = maybe_auto_execute(cur_alerts, prev_state, rt)
        if exec_fp:
            new_state["last_execute_fp"] = exec_fp
            new_state["last_execute_ts"] = now_epoch()
            new_state["last_execute_ok"] = bool(executed)

    save_json(rt.args.state_file, new_state)
    return new_state

def main() -> int:
    ensure_runtime()
    p = argparse.ArgumentParser()
    p.add_argument("--watch-file", type=Path, default=WATCH_FILE)
    p.add_argument("--state-file", type=Path, default=STATE_FILE)
    p.add_argument("--log-file", type=Path, default=LOG_FILE)
    p.add_argument("--last-spoken-file", type=Path, default=LAST_SPOKEN_FILE)
    p.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    p.add_argument("--trigger-on-start", action="store_true", default=DEFAULT_TRIGGER_ON_START)
    p.add_argument("--auto-on-execute-ready", action="store_true", default=DEFAULT_AUTO_ON_EXECUTE_READY)
    p.add_argument("--oneshot", action="store_true", default=DEFAULT_ONESHOT)
    p.add_argument("--debug", action="store_true", default=DEFAULT_DEBUG)
    p.add_argument("--dry-run", action="store_true", default=DEFAULT_DRY_RUN)
    p.add_argument("--speak-off", action="store_true", default=DEFAULT_SPEAK_OFF)
    p.add_argument("--notify", action="store_true", default=DEFAULT_NOTIFY)
    p.add_argument("--debounce-seconds", type=int, default=DEFAULT_DEBOUNCE_SECONDS)
    p.add_argument("--repeat-execute-seconds", type=int, default=DEFAULT_REPEAT_EXECUTE_SECONDS)
    args = p.parse_args()

    rt = WatchRuntime(args)
    rt.log(f"boot watcher voice={rt.voice_name} rate={rt.voice_rate} pitch={rt.voice_pitch}")
    rt.log(f"watch_file={args.watch_file}")
    rt.log(f"state_file={args.state_file}")
    rt.log(f"dry_run={args.dry_run} debug={args.debug} auto_execute={args.auto_on_execute_ready}")

    prev_state = load_json(args.state_file, {}, rt)
    start = True
    while True:
        prev_state = step(prev_state, start, rt)
        if args.oneshot:
            break
        start = False
        time.sleep(max(1, args.poll_seconds))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
