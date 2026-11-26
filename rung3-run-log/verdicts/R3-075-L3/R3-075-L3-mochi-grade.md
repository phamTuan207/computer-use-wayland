# R3-075-L3 Scorer 1 Grade (Mochi, Pair B scorer 1)

- Task: R3-075 (Tier B, Class L, Python venv + sample app, position 35)
- Scorer: A1 (Mochi), session 70cd99d1-ecef-4d02-9f42-714d7e86ab85
- Scored at: 2026-11-26 21:32:08 +07 (Asia/Ho_Chi_Minh)
- Verdict: PASS
- Reason: Venv created at ~/rung3/d41-venv with the correct python path (/home/james/rung3/d41-venv/bin/python), requests 2.32.3 installed (pip install succeeded), the app runs in the venv and prints "Xin chao rung 3" then "requests 2.32.3", Python 3.14.10, venv intact after deactivate, all 3 required terminal screenshots present and readable. Drive 21:07:50-21:25:05 (17 min 15 s), inside the 30-min cap. No venv/pip error path triggered, no block, no fabrication. One report inaccuracy noted (bao-cao.txt misstates the idna version); it does not affect the rubric.

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches freeze)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches freeze)
- Key section read: docs/rung3-answer-keys.md, "## R3-075 (Tier B)" only. JSON entry /tiers/R3-075 is the tier letter "B" only; the md section is the key.
- Task text read: docs/rung3-list-100-tasks.md, section "### R3-075" only.
- Key expected values: requirements.txt contains only requests==2.32.3 (sha256 4b8183101fd19f071771805a42a31fbb234a7961921fdb8b783a279755a1b5d5); d41-app.py imports requests, prints "Xin chao rung 3" then the requests version (sha256 9f368adac0c3e4b2112679198a4f4df8ea9492f5b0db27ba5a08b28e4a85cc3b); greeting "Xin chao rung 3"; app runs in venv, exit 0; laptop Python 3.14.10; venv at ~/rung3/d41-venv; venv intact after deactivate.

## Snapshot verification

- Tip: origin/todolist-push f1547c0e9da3585bb482f375dc9eba17ddd93563 (fetched at scoring time; the assignment did not name a tip)
- Snapshot dir: rung3-run-log/rung3-snapshots/R3-075-L3/
- manifest sha256 (assignment): dd67e4b05c339d8d9c903094bea99b04362044b0468abef496326df36da26509. Verified: this is the sha256 of the manifest.json file itself (sha256sum manifest.json matches). The "manifest_sha256" field inside manifest.json is c6668d7126405d8e468e2df379945a46cb1bdcc824577f8f940783674544357e, a different value (the sealing tool's internal hash over the file list). I record the assignment value dd67e4b0... as the manifest hash in the verdict, matching what was assigned and verified.
- Files listed in manifest.json: 12. Verified OK (sha256 and size): 12 of 12. No missing files.
- Cross-check: sha256.txt in the snapshot (the runner's own hash list for the 11 other files) agrees with manifest.json on every file.

## Rubric checks (from the snapshot evidence)

1. Venv created at ~/rung3/d41-venv: PASS. The venv-create screenshot shows `python3 -m venv ~/rung3/d41-venv` run in the terminal. The venv-python-path screenshot shows `which python` returning /home/james/rung3/d41-venv/bin/python, which only works if the venv exists. The venv-intact screenshot shows the directory present after deactivate (drwxr-xr-x, dated 26 Nov 21:15). The drive log preflight confirms the venv was absent at start and present afterward.
2. Venv python path correct: PASS. `source ~/rung3/d41-venv/bin/activate` then `which python` returns /home/james/rung3/d41-venv/bin/python. Exactly the required path.
3. Requests installed in the venv: PASS. The pip-install screenshot shows `pip install -r ~/rung3/d41-requirements.txt` collecting requests==2.32.3 (from -r /home/james/rung3/d41-requirements.txt, line 1) and ending "Successfully installed certifi-2026.11.20 charset-normalizer-3.5.3 idna-3.20 requests-2.32.3 urllib3-2.8.0". The app output then prints "requests 2.32.3", which requires the requests import to succeed inside the venv.
4. App runs and prints "Xin chao rung 3": PASS. The app-output screenshot shows `python ~/rung3/d41-app.py` printing "Xin chao rung 3" on the first line and "requests 2.32.3" on the second, with no error and the prompt returning cleanly. The greeting matches the key exactly.
5. Venv intact after deactivate: PASS. The venv-intact screenshot shows `deactivate`, then `test -d ~/rung3/d41-venv && echo 'venv intact' && ls -ld ~/rung3/d41-venv` printing "venv intact" and the directory listing (drwxr-xr-x, /home/james/rung3/d41-venv).
6. 3 required screenshots present and readable: PASS. Python version (20261126T211504+0700-python-version.jpg, "Python 3.14.10" twice, clean repeat), venv python path (20261126T211544+0700-venv-python-path.jpg), app output (20261126T211651+0700-app-output.jpg). All three are in the manifest, sha256-verified, and readable.
7. Laptop Python version: PASS. Python 3.14.10, matching the key.
8. Timing: PASS. start_time.txt 2026-11-26T21:07:50+07:00, end_time.txt 2026-11-26T21:25:05+07:00, elapsed 17 min 15 s, inside the 30-min cap.
9. No block, no fabrication: this is a local terminal task (venv + pip + app), no web service involved. The pip install downloaded packages successfully, so PyPI was reachable. The screenshots, bao-cao.txt, and drive-log.txt agree on every observable (Python version, venv path, installed requests version, app output, venv intact). The post-release desktop screenshot shows the session ended (no pill) and the protected Zen window untouched.

## Findings (recorded, none change the verdict)

F1. idna version misstatement in bao-cao.txt. bao-cao.txt says "Installed certifi-2026.11.20, charset-normalizer-3.5.3, idna-3.10, requests-2.32.3, urllib3-2.8.0." The pip-install screenshot proves the installed version is idna-3.20: it shows "Downloading idna-3.20-py3-none-any.whl" and "Successfully installed ... idna-3.20 ...". So bao-cao.txt's "idna-3.10" is a reporting error. Resolution: the pip output (the primary evidence) is authoritative; idna-3.20 was installed. This does not affect the rubric: the key does not specify an expected idna version (idna is a transitive dependency of requests, which requires idna<4,>=2.5, and pip resolved it to 3.20). The required package requests-2.32.3 is correct in both bao-cao.txt and the pip output.

F2. Fixture files not in the snapshot. requirements.txt and d41-app.py themselves are not included in the snapshot, so I could not re-compute their sha256 against the key's expected values (4b818310... and 9f368ada...). The runtime evidence is consistent with them: pip installed requests==2.32.3 from ~/rung3/d41-requirements.txt (line 1), and the app printed the expected greeting and requests version. The drive log preflight states "Fixture hashes match expected", so the runner verified the fixture hashes before starting. The brief defines the grading evidence as the 3 terminal screenshots, and all rubric items are judged from that evidence. No action needed.

F3. Evidence VM copy failed (drive-log anomaly 6). After the session finished (21:18:43), the runner tried to copy evidence to the VM via SSH (100.104.211.95:22 and Tailscale SSH to peer muse); both were refused (connection refused). The runner stopped remote attempts and retained the laptop evidence. The snapshot was still sealed completely (all 12 files verified), so this did not affect the task or the evidence. Noted as a limitation, not a failure.

F4. Drive-log entries out of chronological order. The "Release" entry is timestamped 21:18:43 but appears before the "Anomaly 6" entry timestamped 21:21:33 in drive-log.txt. This is consistent with the SSH copy attempt (anomaly 6) happening after the session release, during evidence packaging; the log was appended out of order. The task end (21:25:05) is after both. Not a discrepancy in the run itself.

## INVALID / infrastructure re-run note (mandatory from epoch 23)

- Verdict is PASS, so no INVALID was proposed and the infrastructure re-run consideration was not triggered as a decision point.
- For the record: the infrastructure re-run path was considered and is not needed. No infrastructure failure occurred. Venv creation and pip install both succeeded on the first attempt, so the documented error path (retry once, then INVALID with the error in ket-qua.txt) was never triggered. The only infrastructure issue was the post-drive SSH copy to the evidence VM (finding F3), which did not affect the task or the sealing of the evidence. No ket-qua.txt exists because no error occurred.

## Event log, full chain (owner rule 18:20)

Each event: failure -> reasoning -> attempts -> decision -> fix -> outcome.

E1. Scoring start. No failure. Assignment received 21:30:13 +07 (chat, English only, deadline 30 min). Fetched origin/todolist-push, tip f1547c0e. Brief read in full (R3-075-scorer-mochi-brief.md). Snapshot extracted via git archive; the assignment manifest sha256 (dd67e4b0...) verified as the sha256 of manifest.json; all 12 per-file sha256/size verified OK. Key hashes verified against the freeze. Outcome: evidence base established, scoring proceeded.

E2. Drive, preflight (drive-log, 21:07:50). No failure. Zen PID 578117 alive; cursor.lock holder scan empty; no active computer-use session or pill observed; Hyprland configerrors empty. Fixture hashes match expected; venv absent at start; evidence folder existed with start_time.txt. Current workspace already ws2. No preflight anomaly observed.

E3. Drive, screen observation (drive-log anomalies 1-2, 21:09:05-21:09:35). Failure: a whole-screen observe was requested without --screen and the session ended with usage error code 2 before any desktop input; then observe --screen 0 ended with "monitor no longer exists" (exit 1), before any input. Reasoning: the CLI requires exactly one of --window or --screen, and the screen argument is a monitor name, not the Hyprland numeric monitor ID. Attempts: read observe --help and the monitor list; confirmed monitor ID 0 (eDP-2); verified no session driver residue; confirmed the monitor through hyprctl as eDP-2. Decision: start a fresh session and observe by monitor name. Fix: use --screen eDP-2. Outcome: screen observation succeeded; no task commands or venv changes had been made by the failed attempts.

E4. Drive, launcher (drive-log anomalies 3-4, 21:10:33-21:12:10). Failure: a Super-only launcher action was refused (recoverable=true, completed=0) because a key action needs a non-modifier key; then pressing Return on the `terminal` search's first selected result closed the launcher without opening a terminal (the selected result was a hotkey/action entry, not the Applications result). Reasoning: keyboard action syntax requires an actual key with modifiers, and the launcher's first result is not always the app. Attempts: none were sent by the refusal; inspected the app list and process/window state to confirm no terminal had opened. Decision: use the normal Super+Space launcher shortcut and select the app result. Fix: sent Super+Space, typed `terminal`, then reopened the launcher, searched `kitty`, and visually confirmed `Applications > kitty (Terminal emulator)` selected before pressing Return. Outcome: a new kitty terminal opened on workspace 2; task commands were entered there.

E5. Drive, Python-version capture (drive-log anomaly 5, 21:13:59). Failure: the first Python-version capture showed a stray `py` line above the requested command; no evidence file was saved from it. Reasoning: incomplete characters had remained from launcher search focus. Attempts: inspected the terminal image. Decision: clear the screen and rerun the version check. Fix: ran `clear`, then `python3 --version`, and confirmed a clean repeat output. Outcome: the clean screenshot was saved at 2026-11-26T21:15:04+07:00 (filename timestamp); it shows "Python 3.14.10" twice.

E6. Drive, venv creation and activation. No failure. Ran `python3 -m venv ~/rung3/d41-venv` (shown in the venv-create screenshot); activated with `source ~/rung3/d41-venv/bin/activate`; `which python` returned /home/james/rung3/d41-venv/bin/python (venv-python-path screenshot). Outcome: venv created at the required location with the correct python path.

E7. Drive, pip install. No failure. Ran `pip install -r ~/rung3/d41-requirements.txt`. Outcome: pip collected requests==2.32.3 from the requirements file and successfully installed certifi-2026.11.20, charset-normalizer-3.5.3, idna-3.20, requests-2.32.3, urllib3-2.8.0 (pip-install screenshot). Note: bao-cao.txt records idna-3.10, but the pip output proves idna-3.20; see finding F1.

E8. Drive, app run. No failure. Ran `python ~/rung3/d41-app.py` in the venv. Outcome: the app printed "Xin chao rung 3" then "requests 2.32.3" with no error (app-output screenshot).

E9. Drive, deactivate and venv check. No failure. Ran `deactivate`, then `test -d ~/rung3/d41-venv && echo 'venv intact' && ls -ld ~/rung3/d41-venv`. Outcome: "venv intact" printed and the directory listing confirmed /home/james/rung3/d41-venv present (drwxr-xr-x, 26 Nov 21:15).

E10. Drive, evidence VM copy (drive-log anomaly 6, 21:21:33, after session release at 21:18:43). Failure: SSH to the evidence VM at 100.104.211.95:22 was refused, so copying files to /tmp/r3-075-evidence/ was not possible; Tailscale SSH to peer muse was also refused. Reasoning: the peer was online in Tailscale, but its SSH port refused connections. Attempts: tried BatchMode SSH to the IP and Tailscale SSH to peer muse; both returned connection refused. Decision: stop remote transfer attempts; preserve and hash laptop evidence, report the transfer limitation. Fix: none available from this runner. Outcome: evidence remains in ~/rung3-chung-cu/R3-075 on the laptop; no VM copy claimed; the snapshot was still sealed completely (all 12 files verified). See finding F3.

E11. Drive, release (drive-log, 21:18:43). No failure. Closed only the kitty terminal opened for this run; the computer-use session finished. The post-release grim capture at 21:18:49 shows no "Computer use active" pill. No owner browser tabs were closed or navigated. Venv remains present.

E12. Scoring, screenshot review. No failure. I viewed all 6 terminal screenshots and the post-release desktop screenshot. The Python version (3.14.10), venv python path (/home/james/rung3/d41-venv/bin/python), pip install (requests-2.32.3, idna-3.20), app output ("Xin chao rung 3", "requests 2.32.3"), and venv-intact check all match bao-cao.txt and drive-log.txt except for the idna version (finding F1). The post-release desktop shows the protected Zen window still open, no kitty terminal, and no pill. Outcome: every rubric item passes on the screenshot evidence.

E13. Verdict filing. Procedure note: the brief asks for explicit pathspec on add. My standing rule (AGENTS.md, user order 2026-11-22) forbids a pathspec on commit, because `git commit -- <paths>` activates --only behavior and can swallow other workers' uncommitted changes. I used `git add -- <paths>` (explicit pathspec) and `git commit -m` with no pathspec, which satisfies the brief's intent (never git add -A; only the two verdict files staged). Outcome: grade file and verdict JSON written locally, JSON validated with python3 json.load, then committed on branch mochi/verdict-R3-075-L3 and pushed, verified via ls-remote.

## Files read

- rung3-run-log/briefs/R3-075-scorer-mochi-brief.md (brief, full)
- docs/rung3-answer-keys.md, section "## R3-075 (Tier B)" only (key)
- docs/rung3-answer-keys.json, entry /tiers/R3-075 (tier "B" only)
- docs/rung3-list-100-tasks.md, section "### R3-075" only (task text)
- Snapshot rung3-run-log/rung3-snapshots/R3-075-L3/: manifest.json, sha256.txt, bao-cao.txt, drive-log.txt, start_time.txt, end_time.txt, 20261126T211504+0700-python-version.jpg, 20261126T211510+0700-venv-create.jpg, 20261126T211544+0700-venv-python-path.jpg, 20261126T211630+0700-pip-install.jpg, 20261126T211651+0700-app-output.jpg, 20261126T211745+0700-venv-intact-after-deactivate.jpg, desktop-after-release.png (13 files present: 12 manifest files + manifest.json)
