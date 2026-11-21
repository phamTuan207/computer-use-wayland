wins = windows()
matches = [w for w in wins if w["title"] == terminal_title]
assert_state(len(matches) == 1, "expected exactly one terminal window titled " + terminal_title)
term = matches.pop()
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "rm -f /tmp/y-tuong.txt && printf 'Ý tưởng 1: app nhắc uống nước.\\nÝ tưởng 2: bot tóm tắt bài giảng.\\nÝ tưởng 3: web bán đồ secondhand.\\n' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 1: app nhắc uống nước.")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 2: bot tóm tắt bài giảng.")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 3: web bán đồ secondhand.")
verify_image = verify["image"]
