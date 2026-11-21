wins = windows()
matches = [w for w in wins if w["title"] == terminal_title]
assert_state(len(matches) == 1, "expected exactly one terminal window titled " + terminal_title)
term = matches.pop()
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "rm -rf /tmp/hoc-ky-2 && mkdir -p /tmp/hoc-ky-2/dsa /tmp/hoc-ky-2/ktvm /tmp/hoc-ky-2/oop && find /tmp/hoc-ky-2 -type d\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
assert_file_exists("/tmp/hoc-ky-2/dsa")
assert_file_exists("/tmp/hoc-ky-2/ktvm")
assert_file_exists("/tmp/hoc-ky-2/oop")
verify_image = verify["image"]
