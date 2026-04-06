#!/usr/bin/env python3
import subprocess, time

def invite(username):
    cmd = f'curl -H "Authorization: token YOUR_TOKEN" -X PUT -d permission=push https://api.github.com/repos/R6eron/NexpertUVDM-Automation/collaborators/{username}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ INVITED {username}")
    else:
        print(f"❌ {username}")

targets = ["johnsmith123", "user2", "user3"]  # YOUR USERS

while True:
    for user in targets:
        invite(user)
        time.sleep(10)
    print("🔄 Cycle...")
    time.sleep(300)

