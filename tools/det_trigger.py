import time, subprocess, requests
def speak(t):
    print(f"[VOICE] {t}")
    subprocess.run(["termux-tts-speak", t], stderr=subprocess.DEVNULL)
def get_p():
    try: return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=XLMUSDT").json()["price"])
    except: return None
mode, slp = "SLOW", 60
h = get_p()
l = h
last = h
speak("DET wired to dry run ladder for XLM")
while True:
    try:
        time.sleep(slp)
        c = get_p()
        if not c: continue
        print(f"[{mode}] XLM Price: {c} | Low: {l}")
        if c > h: h = c
        if c < l:
            l = c
            if mode=="HUNTING": print(f"Trailing low: {l}")
        if mode=="SLOW" and (h-c)/h >= 0.002:
            mode, slp = "FAST", 15
            speak("Fast mode engaged")
        elif mode=="FAST":
            if c < last:
                mode, slp = "HUNTING", 10
                speak("Hunting mode engaged")
            elif (c-l)/l >= 0.001:
                mode, slp, h = "SLOW", 60, c
        elif mode=="HUNTING" and (c-l)/l >= 0.001:
            speak("Bounce confirmed. Deploying ladder.")
            print(f"TRIGGER! Bounce {l} to {c}")
            print("[*] EXECUTING DRY-RUN LADDER...")
            try:
                subprocess.run(["python", "/data/data/com.termux/files/home/NexpertUVDM-Automation/tools/opt2_adaptive_ladder.py", "--dry-run"], check=False)
            except Exception as e:
                print(f"Failed to call ladder: {e}")
            mode, slp, h, l = "SLOW", 60, c, c
        last = c
    except KeyboardInterrupt:
        print("Stopped.")
        break
