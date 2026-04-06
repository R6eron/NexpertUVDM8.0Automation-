#!/usr/bin/env python3
import requests, time, os
from datetime import datetime

GITHUB_TOKEN = "ghp_YourActualToken123"  # Replace with your token
REPO = "R6eron/NexpertUVDM-Automation"

def invite_user(username):
    url = f"https://api.github.com/repos/{REPO}/collaborators/{username}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"permission": "push"}
    try:
        r = requests.put(url, json=data, headers=headers)
        if r.status_code == 204:
            print(f"✅ [{datetime.now()}] INVITED {username}")
            os.system('cat notes/standard_enquiries.md | say')  # Voice output
            return True
        else:
            print(f"❌ [{r.status_code}] {username}")
    except:
        pass
    return False

# Your DM targets (add real usernames:hex here)
targets = [
    "user1",  # Replace with real LinkedIn usernames
    "user2",
    "user3"
]

print("🚀 XRPEASY AUTO-INVITER STARTED")
while True:
    for user in targets:
        invite_user(user)
        time.sleep(5)  # Rate limit safety
    print("🔄 Cycle complete. Waiting 5min...")
    time.sleep(300)

