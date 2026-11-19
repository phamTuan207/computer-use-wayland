wins = windows()
terms = [w for w in wins if w["title"] == "co2r-method-term"]
assert_state(len(terms) == 1, "expected exactly one co2r-method-term window")
term = terms[0]
obs = observe_change_only(window=term["address"])
obs_mode = obs["mode"]
obs_summary = obs["summary"]
obs_bbox = obs["bbox"]
obs_changed_tile_count = obs["changed_tile_count"]
obs_changed_fraction = obs["changed_fraction"]
obs_image = obs["image"]
obs_thumbnail = obs["thumbnail"]
result = act([{"type": "type", "text": "mkdir -p /tmp/hoc-ky-2/dsa /tmp/hoc-ky-2/ktvm /tmp/hoc-ky-2/oop && find /tmp/hoc-ky-2 -type d\n"}], obs["observation"])
verify = observe_change_only(previous_observation=obs["observation"])
verify_mode = verify["mode"]
verify_summary = verify["summary"]
verify_bbox = verify["bbox"]
verify_changed_tile_count = verify["changed_tile_count"]
verify_changed_fraction = verify["changed_fraction"]
verify_crop = verify["image"]
verify_thumb = verify["thumbnail"]
assert_state(result["ok"], "act failed")
assert_file_exists("/tmp/hoc-ky-2/dsa")
assert_file_exists("/tmp/hoc-ky-2/ktvm")
assert_file_exists("/tmp/hoc-ky-2/oop")
verify_image = verify["observation"]["image"]
