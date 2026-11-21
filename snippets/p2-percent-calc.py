wins = windows()
matches = [w for w in wins if w["title"] == terminal_title]
assert_state(len(matches) == 1, "expected exactly one terminal window titled " + terminal_title)
term = matches.pop()
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "python3 -c \"print(144/150*100)\"\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
verify_image = verify["image"]
