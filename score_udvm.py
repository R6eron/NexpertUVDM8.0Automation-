import os
env_path = os.path.expanduser("~/.udvm_score.env")
expert_score = 0
print("EXPERT_SCORE=%d" % expert_score)
with open(env_path, "w", encoding="utf-8") as f:
    f.write("EXPERT_SCORE=%d" % expert_score + chr(10))
print("Wrote %s" % env_path)
