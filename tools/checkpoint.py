#!/usr/bin/env python3
"""
UVDM Checkpoint & Voice Assist with actual speech
"""

import sys
from datetime import datetime
from pathlib import Path
import subprocess

RUNTIME = Path.home() / ".config" / "uvdm" / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)

LOG_FILE = RUNTIME / "checkpoint.log"


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")
    print(entry)


def speak(text: str):
    """Actual Termux TTS"""
    try:
        subprocess.run(["termux-tts-speak", "-r", "1.0", text], check=True, timeout=8)
    except:
        print("(TTS not available - printing only)")


def voice_assist(status: str, message: str):
    if status.lower() == "pass":
        log(f"✅ VOICE ASSIST PASSED: {message}", "PASS")
        speak(f"Well done, Ron. {message}.")
        print(f"\nWell done, Ron. {message}.")
        print("You're obeying the tape like a true speculator. The plan is holding.")
        print("Keep the faith in the process. The market rewards patience.\n")
    elif status.lower() == "fail":
        log(f"❌ VOICE ASSIST FAILED: {message}", "FAIL")
        speak(f"Steady, Ron. {message}.")
        print(f"\nSteady, Ron. {message}.")
        print("Don't let emotion pull you off the rails. Return to the plan you wrote when calm.")
        print("Remember: The tape is the sole source of truth. We obey. We do not argue.\n")
    else:
        log(f"ℹ️ VOICE ASSIST: {message}", "INFO")
        speak(f"Note for you, Ron: {message}")
        print(f"\nNote for you, Ron: {message}\n")


def run_basic_tests():
    print("\n=== UVDM Automatic Self-Test ===")
    print("Checking the machine, Ron...\n")
    
    tests_passed = 0
    tests_failed = 0

    tp_file = RUNTIME / "tp_levels_live.json"
    if tp_file.exists():
        log("TP Levels file found", "PASS")
        tests_passed += 1
        print("✓ TP levels are ready.")
    else:
        log("TP Levels file missing", "FAIL")
        tests_failed += 1
        print("✗ TP levels file not found.")

    try:
        test_file = RUNTIME / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        log("Runtime directory writable", "PASS")
        tests_passed += 1
        print("✓ Runtime environment is healthy.")
    except Exception as e:
        log(f"Runtime directory issue: {e}", "FAIL")
        tests_failed += 1
        print("✗ Runtime directory has an issue.")

    print(f"\n=== Test Summary ===")
    print(f"Passed: {tests_passed} | Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ All systems look good, Ron. You're maintaining discipline well.")
        speak("All systems look good, Ron. You're maintaining discipline well.")
        print("Process over outcome. Keep going.\n")
    else:
        print("\n⚠️ A few things need attention. Let's stay on top of it, Ron.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 tools/checkpoint.py test")
        print("  python3 tools/checkpoint.py voice_assist pass \"message\"")
        print("  python3 tools/checkpoint.py voice_assist fail \"message\"")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        run_basic_tests()
    elif command == "voice_assist":
        if len(sys.argv) < 4:
            print("Usage: python3 tools/checkpoint.py voice_assist <pass|fail> \"message\"")
            sys.exit(1)
        status = sys.argv[2]
        message = " ".join(sys.argv[3:])
        voice_assist(status, message)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
