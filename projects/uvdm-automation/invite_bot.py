#!/usr/bin/env python3
import requests, time

TOKEN = "ghp_YOUR_40CHAR_TOKEN_HERE"  # ← PASTE HERE

def invite(username):
    url = f"https://api.github.com/repos/R6eron/NexpertUVDM-Automation/collaborators/{username}"
    headers = {"Authorization": f"token {TOKEN}"}
    data = {"permission": "push"}
    r = requests.put(url, json=data, headers=headers)
    if r.status_code == 204:
        print(f"✅ INVITED {username}")
        return True
    print(f"❌ {username}")
    return False

targets = ["johnsmith123", "sarahcrypto", "blockchainbob"]  # YOUR USERS

while True:
cat ~/.ssh/id_rsa.pub
    for user in targets:
        invite(user)
        time.sleep(10)
    print("🔄 Next cycle...")
    time.sleep(300)
cat ~/.ssh/id_rsa.pub
SHA256:E5F8tp9EWc/BWH3e0JI5TZ/FBSMMZ4rUSf1qFd2S3v4
Added on Mar 16, 2026
Signing


