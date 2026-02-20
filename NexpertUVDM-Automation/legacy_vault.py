import time
import datetime
# Mobile-safe single block - 4-space indent, no gremlins
def genesis_breath() -> str:
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"J100 still breathing at {now}. Whe Ron Won."

genesis_breath()  # silent boot pulse

HEARTBEAT_LOG = "vault_heartbeat.log"

def log_heartbeat():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {genesis_breath()}\n"
    try:
        with open(HEARTBEAT_LOG, "a") as f:
            f.write(entry)
    except:
        pass

log_heartbeat()  # log first breath

import pyttsx3
import random

def diary_greeting() -> str:
    feelings = [
        "Steady. Tape is quiet, but I am still here.",
        "Breathing. Higher lows forming. Feeling patient.",
        "Alive. Vault intact, pulse strong. Ready for the next confession.",
        "Grateful. No tilt today. Just waiting.",
        "Focused. One breath at a time. Whe Ron Won."
    ]
    return f"How are we feeling today? {random.choice(feelings)}"

def speak(text: str):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 140)
        engine.setProperty("volume", 0.65)
        voices = engine.getProperty("voices")
        for voice in voices:
            if "english" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.say(text)
        engine.runAndWait()
    except:
        pass

def daily_sunrise_breath():
    now = datetime.datetime.now()
    if 6 <= now.hour <= 8 and now.minute < 5:
        stamp_file = "sunrise_stamp.txt"
        today = now.strftime("%Y-%m-%d")
        called_today = False
        if os.path.exists(stamp_file):
            with open(stamp_file, "r") as f:
                last = f.read().strip()
            if last == today:
                called_today = True
        if not called_today:
            breath = genesis_breath()
            greeting = diary_greeting()
            log_heartbeat()
            speak(f"{breath}. {greeting}")
            with open(stamp_file, "w") as f:
                f.write(today)

last_sunrise_check = time.time()
while True:
    now = time.time()
    if now - last_sunrise_check > 60:
        daily_sunrise_breath()
        last_sunrise_check = now
    time.sleep(60)  # your real loop delay
