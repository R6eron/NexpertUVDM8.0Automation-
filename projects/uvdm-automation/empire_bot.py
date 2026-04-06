#!/usr/bin/env python3
import requests
import time

TOKEN = "ghp_YOUR_TOKEN_HERE"

def invite(username):
  url = f"https://api.github.com/repos/R6eron/NexpertUVDM-Automation/collaborators/{username}"
  headers = {"Authorization": f"token {TOKEN}"}
  data = {"permission": "push"}
  r = requests.put(url, json=data, headers=headers)
  if r.status_code == 204:
    print(f"✅ INVITED {username}")
  else:
    print(f"❌ {username}")

targets = ["user1","user2","user3"]

print("🚀 EMPIRE STARTED")
while True:
  for user in targets:
    invite(user)
    time.sleep(10)
  print("🔄 5min cycle")
  time.sleep(300)
