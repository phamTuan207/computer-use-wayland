# R3-075 scorer 2 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-075
verdict: PASS
timestamp: 2026-11-26 21:31 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: all 3 required terminal screenshots are present and readable and show exactly what the key requires: Python 3.14.10, the activated venv python at /home/james/rung3/d41-venv/bin/python, and the app printing "Xin chao rung 3" then "requests 2.32.3" with a clean return to the prompt; the supporting screenshots show the venv created at ~/rung3/d41-venv, pip successfully installing requests-2.32.3 from d41-requirements.txt into the venv session, and the venv directory intact after deactivate.

## Key section used

docs/rung3-answer-keys.md, "## R3-075 (Tier B)", lines 492-499: requirements.txt contains only requests==2.32.3 (sha256 4b8183101fd19f071771805a42a31fbb234a7961921fdb8b783a279755a1b5d5); d41-app.py imports requests, prints "Xin chao rung 3" then the requests version (sha256 9f368adac0c3e4b2112679198a4f4df8ea9492f5b0db27ba5a08b28e4a85cc3b); the app runs in the venv, prints the greeting, exit 0; laptop Python 3.14.10; venv at ~/rung3/d41-venv; after deactivate the venv dir remains intact. Grading evidence: 3 terminal screenshots (Python version, venv python path, app output); the scorer checks the venv exists and the package is installed from the snapshot evidence. Error path: venv creation or pip install failure after 1 retry makes the task INVALID, with the error written into ket-qua.txt. The requirements.txt and d41-app.py files themselves are not part of the snapshot, so their key hashes could not be checked directly; the graded screenshot evidence covers their observable effects (the pip line 1 pin and the app output).

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-075-L3/
- Manifest: the manifest.json file's own sha256 is dd67e4b05c339d8d9c903094bea99b04362044b0468abef496326df36da26509, matching the dispatch notice. The manifest_sha256 field inside the file reads c6668d7126405d8e468e2df379945a46cb1bdcc824577f8f940783674544357e (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 12 evidence files OK
  - 20261126T211504+0700-python-version.jpg c877b9e835b06f04a0bfba20088b3a9c6f712288066411c6ef6728c3b6072a84 OK
  - 20261126T211510+0700-venv-create.jpg 24c0691d469921513538dca3722e2a97e512b855874a59e8913daa866b504037 OK
  - 20261126T211544+0700-venv-python-path.jpg c476b8533d79545d9d8ab66bfe82665e7fa11e66bf2973a34f15814656c45de5 OK
  - 20261126T211630+0700-pip-install.jpg f8f097c7c8fe06355c5447fddf442d0952babdedff662b9081d4424a889470cd OK
  - 20261126T211651+0700-app-output.jpg 0910114bdf96b2e6f2071a7982186bd45d63f8574e7f8262ec58613fea7352ac OK
  - 20261126T211745+0700-venv-intact-after-deactivate.jpg 52497825b9e9c5ec98a50e5c1018094f7f6233c7b8e3eab40577998d2c1a0b58 OK
  - bao-cao.txt acd0bbe4f85767b5d9cebf3bcefaed0356aba3e07bdc9c143adbde9ce7bddd52 OK
  - desktop-after-release.png 59669d925a0f81625804d0520cd66de1dd09a03bb2fc03723de1c6badfe03f59 OK
  - drive-log.txt 61dab8d428e2ca0958592c5bdaaf78127359a3d17e56cad77befd14099d0334a OK
  - end_time.txt 3506edd13603b9c3e55ce8619de210d98cd4cee48430f82c262a1a72b16bdf06 OK
  - sha256.txt 1a9a574a27b28967ebab42cddc95892174de7b916d37881fa9075a2f20380a59 OK
  - start_time.txt 9188e43db5c42d038de472c8edba7f6f58d34fafc79d61afcdc099a83614ad3a OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T21:07:50+07:00, end_time.txt 2026-11-26T21:25:05+07:00, inside the 30 minute task limit. All 6 screenshot timestamps (21:15:04 to 21:17:45) fall inside the window.

## Files read

- rung3-run-log/briefs/R3-075-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 492-499 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-075-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-075-L3/sha256.txt
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211504+0700-python-version.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211510+0700-venv-create.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211544+0700-venv-python-path.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211630+0700-pip-install.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211651+0700-app-output.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/20261126T211745+0700-venv-intact-after-deactivate.jpg
- rung3-run-log/rung3-snapshots/R3-075-L3/bao-cao.txt (line 11 only, to check the idna version note firsthand; the runner report is not grading evidence and no part of the verdict rests on it)
- rung3-run-log/rung3-snapshots/R3-075-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-075-L3/end_time.txt

The remaining snapshot files (drive-log.txt, desktop-after-release.png) were hash-verified against the manifest but not read for grading.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, all 6 terminal screenshots present and readable), and no infrastructure failure appears anywhere in it; in particular the documented INVALID error path (venv creation or pip install failure after 1 retry, error written into ket-qua.txt) is not triggered: there is no ket-qua.txt in the snapshot and the screenshots show the venv creation flow and a successful pip install.

## Reasons

- Python version (20261126T211504+0700-python-version.jpg): python3 --version prints "Python 3.14.10", exactly the key's laptop Python. Screenshot present and readable.
- Venv creation (20261126T211510+0700-venv-create.jpg): the terminal shows python3 -m venv ~/rung3/d41-venv being run, and the later screenshots prove it took effect: the activate script exists and works, pip installs into the session, and the final listing shows the directory.
- Venv python path (20261126T211544+0700-venv-python-path.jpg): after source ~/rung3/d41-venv/bin/activate, which python prints /home/james/rung3/d41-venv/bin/python, the correct python inside the venv at ~/rung3/d41-venv. Screenshot present and readable.
- Package installed (20261126T211630+0700-pip-install.jpg): pip install -r ~/rung3/d41-requirements.txt collects requests==2.32.3 from line 1 of /home/james/rung3/d41-requirements.txt, downloads requests-2.32.3 and its dependencies, and ends "Successfully installed certifi-2026.11.20 charset-normalizer-3.5.3 idna-3.20 requests-2.32.3 urllib3-2.8.0". The graded package, requests 2.32.3, is installed, in the terminal session where the venv was activated.
- App output (20261126T211651+0700-app-output.jpg): python ~/rung3/d41-app.py prints "Xin chao rung 3" then "requests 2.32.3" and returns to a clean prompt with no error or traceback, matching the key's expected greeting and version print. Screenshot present and readable.
- Venv intact after deactivate (20261126T211745+0700-venv-intact-after-deactivate.jpg): after deactivate, test -d ~/rung3/d41-venv succeeds, echoes "venv intact", and ls -ld shows drwxr-xr-x /home/james/rung3/d41-venv dated 26 Nov 21:15. The venv was not deleted.
- Observation, no verdict impact: bao-cao.txt line 11 lists "idna-3.10" among the installed packages, while the pip-install screenshot shows idna-3.20 in both the download line and the "Successfully installed" line. The screenshot is the ground truth evidence; bao-cao.txt is the runner's self-report and is not grading evidence. idna is a transitive dependency of requests and its version is not a key value; the graded package requests-2.32.3 agrees in both. The discrepancy is a typo in the report and changes nothing in the rubric.
- Rubric check: venv created at ~/rung3/d41-venv, venv python path correct, requests installed in the venv, app runs and prints "Xin chao rung 3", venv intact after deactivate, 3 required screenshots present and readable. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
