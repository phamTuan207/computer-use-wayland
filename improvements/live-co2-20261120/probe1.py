wins = windows()
terms = [w for w in wins if w["title"] == "co2-term"]
assert_state(len(terms) == 1, "expected exactly one co2-term window")
term = terms[0]
obs = observe_change_only(window=term["address"])
probe_first_mode = obs["mode"]
probe_first_fraction = obs["changed_fraction"]
probe_first_summary = obs["summary"]
result = act([{"type": "type", "text": "x"}], obs["observation"])
assert_state(result["ok"], "act failed")
verify = observe_change_only(previous_observation=obs["observation"])
probe_mode = verify["mode"]
probe_fraction = verify["changed_fraction"]
probe_bbox = verify["bbox"]
probe_summary = verify["summary"]
probe_image_present = verify["image"] is not None
probe_thumb_present = verify["thumbnail"] is not None
probe_keys = sorted(list(verify.keys()))
probe_obs_image = verify["observation"]["image"]
probe_obs_keys = sorted(list(verify["observation"].keys()))
print(probe_summary)
result2 = act([{"type": "type", "text": "\n"}], verify["observation"])
assert_state(result2["ok"], "second act failed")
verify2 = observe_change_only(previous_observation=verify["observation"])
probe2_mode = verify2["mode"]
probe2_fraction = verify2["changed_fraction"]
probe2_bbox = verify2["bbox"]
probe2_summary = verify2["summary"]
probe2_image_present = verify2["image"] is not None
probe2_thumb_present = verify2["thumbnail"] is not None
probe2_keys = sorted(list(verify2.keys()))
print(probe2_summary)
verify3 = observe_change_only(previous_observation=verify2["observation"])
probe3_mode = verify3["mode"]
probe3_fraction = verify3["changed_fraction"]
probe3_summary = verify3["summary"]
print(probe3_summary)
verify_image = verify2["observation"]["image"]
