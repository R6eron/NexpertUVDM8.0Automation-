#!/usr/bin/env python3
import subprocess, os, sys, time

def listen():
    try:
        return subprocess.getoutput("termux-speech-to-text").lower().strip()
    except:
        return ""

def speak(text):
    subprocess.run(["termux-tts-speak", text])

def main():
    speak("UVDM Sharpe voice ready")
    print("🎤 Say: 'status', 'profits', 'stop', 'start'")
    
    while True:
        print("🔊 Listening...")
        voice = listen()
        
        if voice:
            print(f"Voice: '{voice}'")
            
            if "status" in voice or "sharpe" in voice:
                speak("Checking empire")
                os.system("echo 'PIDs:' && ps aux | grep python | grep -v grep | wc -l")
                os.system("echo 'Latest:' && tail -3 empire.log")
                
            elif "profits" in voice or "nexo" in voice or "bitrue" in voice:
                speak("High value trades")
                os.system("tail -10 empire.log | grep -E 'Nexo|Bitrue|100K'")
                
            elif "stop" in voice or "kill" in voice:
                speak("Stopping empire")
                os.system("killall python3 2>/dev/null")
                speak("Empire stopped")
                break
                
            elif "start" in voice or "empire" in voice:
                speak("Starting flywheel")
                os.system("nohup python3 udvm_fixed.py > empire.log 2>&1 &")
                speak("Empire live")
                
        time.sleep(2)

if __name__ == "__main__":
    main()
