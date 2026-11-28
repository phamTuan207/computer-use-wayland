# Pick 1 program template

This is the durable template for the Phase B Pick 1 programs. Copy P1, P2, P3 and P4 from this file.

## Shape rule

Use this order for every task with a terminal action:

`windows() -> observe() -> act() -> observe() -> assert`

The observe after `act()` is both the settle interval and the verify image. Put file assertions after that fresh observe, then assign `verify_image = verify["image"]`. Never call an assert directly after `act()`. Never use a wait act with an observation made before the previous act. A fresh observe is the settle step and gives the verification image.

For P1 and P2, keep the unchanged shape: `windows()`, `observe()`, `act()`, verify `observe()`, then `verify_image = verify["image"]`. They have no file asserts. The P1 and P2 programs below are the exact programs measured in the A1 live run, with the terminal title kept as speed-pick1-term to match P3 and P4 (the A1 live run copied them with the title changed to speed-a1-term).

## P1 program

```python
wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "df -h /\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
verify_image = verify["image"]
```

## P2 program

```python
wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "python3 -c \"print(144/150*100)\"\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
verify_image = verify["image"]
```

## P3 program

```python
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
```

The three P3 targets are directories. assert_file_exists checks path existence, including directories.

## P4 program

```python
wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "printf 'Ý tưởng 1: app nhắc uống nước.\\nÝ tưởng 2: bot tóm tắt bài giảng.\\nÝ tưởng 3: web bán đồ secondhand.\\n' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\n"}], obs)
verify = observe(window=term["address"])
assert_state(result["ok"], "act failed")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 1: app nhắc uống nước.")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 2: bot tóm tắt bài giảng.")
assert_file_contains("/tmp/y-tuong.txt", "Ý tưởng 3: web bán đồ secondhand.")
verify_image = verify["image"]
```

The three lines above were copied from task P4 A-01 in `/tmp/speed-profile-20261118/pick1-run1/measure-brief.md` and checked byte-for-byte. The runtime type text must have literal backslash plus `n` between the lines, inside one single-quoted `printf` argument, and exactly one real newline at the end to run the shell command. Therefore the Python program file has `\\n` (two backslashes then `n`) between the lines and `\n` (one backslash then `n`) only at the end. Python's actual `repr` uses double quotes around the value because its shell command contains single quotes:

```text
"printf 'Ý tưởng 1: app nhắc uống nước.\\nÝ tưởng 2: bot tóm tắt bài giảng.\\nÝ tưởng 3: web bán đồ secondhand.\\n' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\n"
```
## Root causes and evidence

- P3 was a template ordering race. The request at `records.jsonl` label `pick1-p3-code` returned `assert failed: file does not exist: /tmp/hoc-ky-2/dsa` after only windows, observe, and act. The shell may still be executing the typed command when `act()` returns. The retry label `pick1-p3-code-retry` then returned `assert failed: wait failed`: it sent a wait act with the pre-act observation. `scripts/code_exec.py` binds observations to ids, and `scripts/cu.py` screen-change preflight at lines 1476-1479 refuses an act when the screen changed. The post-act observe in this template gives the shell time to finish and binds a fresh image before assertions.
- P4 was malformed shell text, not byte mangling in `act()`. `scripts/cu.py` `CodeExecBackend.act` at lines 1995-2002 passes the actions list directly to `desktop_act`. The original `prog-pick1-p4.py` matches the base request JSON stdin byte-for-byte; the retry envelope at `records.jsonl` label `pick1-p4-code-retry` echoes the expected accented text intact. `native/vendor/wtype/main.c` lines 161-187 maps real newline to Return and maps other characters through `xkb_utf32_to_keysym`. In the old program, Python interpreted each `\n` in the type string as a real newline, so wtype pressed Return inside the shell command. The argument also lacked single quotes. The diagnostic image `~/.cache/agent-computer-use/d5e0d6a1bee7.png` shows `bash: command not found: Ý` and the redirect on a separate prompt. The baseline action in `actions-base-p4.json` used a single-quoted argument with literal backslash-n and one final newline; the verify image `~/.cache/agent-computer-use/cf009120181b.png` shows `cat` printing all three lines with diacritics. The echo looked mangled during rapid typing in both images, while the baseline file output was correct.

## Phase B handoff

Phase B must copy the P3 and P4 programs from this document, not from the old measure brief. The coordinator must amend the Phase B brief to point here before the rerun.
