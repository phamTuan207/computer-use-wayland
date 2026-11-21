wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "mkdir -p /tmp/hoc-ky-2/dsa /tmp/hoc-ky-2/ktvm /tmp/hoc-ky-2/oop && find /tmp/hoc-ky-2 -type d\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
assert_file_exists("/tmp/hoc-ky-2/dsa")
assert_file_exists("/tmp/hoc-ky-2/ktvm")
assert_file_exists("/tmp/hoc-ky-2/oop")
verify_image = verify["image"]
