wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "df -h /\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
verify_image = verify["image"]
