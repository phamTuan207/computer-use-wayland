wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "python3 -c \"print(144/150*100)\"\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
verify_image = verify["image"]
