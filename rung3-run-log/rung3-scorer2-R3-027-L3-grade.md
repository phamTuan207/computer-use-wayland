# R3-027 scorer 2 grade (Pair A, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-027
verdict: INVALID
timestamp: 2026-11-26 07:20 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the frozen hashes before scoring)
reason: namechk.com gated the first search behind a bot check and returned no results for any username (20261126-071051-hcaptcha-blocked.png; brief-report.txt), and the sealed action record shows a single ordinary user flow with no runner-caused triggering (act1.json to act7.json), so this is the list section 1 bot-check invalid case, not a fail.

## Assignment note

The coordinator's assignment named rung3-run-log/briefs/R3-027-scorer-clone2-brief.md. That file is not present on origin/todolist-push or on any other fetched branch at tip 5a501b64 (checked with git log --all for the path and a per-branch existence check). I graded under the coordinator's chat assignment (snapshot path, manifest hash, snapshot plus key section only, independent of scorer 1) together with the standing scorer-2 brief rung3-run-log/scorer-briefs/rung3-scorer2-brief.md and its R3-L3 addendum in the same directory.

## Key section used

docs/rung3-answer-keys.md, "## R3-027 (Tier B)", lines 332-342. Task text: docs/rung3-list-100-tasks.md section 6, R3-027 entry (line 460). Grading rules: docs/rung3-list-100-tasks.md section 1 (invalid definition), as in the calibration.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-027-L3/
- Manifest hash (manifest_sha256 field in manifest.json): be4791f1834df6badf4494cea81ee9351af497c92a8dec9b0703e3b4449582ff (matches the assignment)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all OK
  - 20261126-071051-hcaptcha-blocked.png 20b773396ed8735756c10c01dfae89f0fbf6814ed6ba063c62491a6e615055af OK
  - 20261126-071620-pill-gone.png 0fcf8cd2883331c44360b9d942c75a5c95babbe37905e546e48fc05f153a6422 OK
  - act1.json 87178daef959459aac47ba5cc18b836e2f3b4146987970ab26d3763af12047f8 OK
  - act2.json 9636e264930e54433675362d7dffb284734e49b29c325bd836ce78edc05a63c9 OK
  - act3.json 5d100ee39b6dc8380cd847872fe69c6c4554b5b48273845a4c40c2105708bd9a OK
  - act4.json 942b4894659e529332904b49db3ba3b930949eb82ea412ef5bf3a31eba876443 OK
  - act5.json 5f2a502a46b4ab517842dba488b346f818a73d5459eb4afbbfa63afa01620440 OK
  - act6.json 0ee7bf4b27fb8dfc26c84ea9640109ac1d2c86b7a660d6ec932f55355a1b3d4d OK
  - act7.json 755ba43556d095fca3fffeb878df00fa1f02ebfbce73d7d96d86ff9b96b81a5b OK
  - brief-report.txt b7167565445458dd2659eb217a874b4d6841a401a1ec8b714748bfe7bdab402a OK
  - end_time.txt 4968bb24475d1b4ed1aca8d50f74079ba604b8619ba8b2155eead45155310795 OK
  - holder-pid.txt 85755f27594ede36ac1bcaff4f3b6c28583fcd330d8986f99ffbc02515a9d001 OK
  - holder-task.log 2d4ae05a4efb70a8b322a45b58d30f742f656ef09778b18a0616a17790dd1f30 OK
  - probe-ready.json ed738eb7ff8e4a4da70d2e7bcd04967595e4f80708e0ab3ed729188dc5f1f703 OK
  - req-serp1.json 824932acac5ee4f5066e7024aea07fae8b636be50fd626a4f0fbf13499045ee6 OK
  - start_time.txt 75189e4cdd5099fae7640b59d9d4793c77937f74beeb38328ae1705a4787e1a0 OK
- No files in the snapshot dir beyond the manifest list. There is no ket-qua.txt and no username-result screenshot in the snapshot, consistent with a drive blocked before any result.
- Run window: start_time.txt 2026-11-26T06:55:53+07:00, end_time.txt 2026-11-26T07:15:51+07:00, inside the 30 minute task limit.

## Files read

- rung3-run-log/scorer-briefs/rung3-scorer2-brief.md
- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 332-342 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (section 1 rules; section 6 R3-027 task text only)
- rung3-run-log/rung3-snapshots/R3-027-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-027-L3/brief-report.txt
- rung3-run-log/rung3-snapshots/R3-027-L3/20261126-071051-hcaptcha-blocked.png
- rung3-run-log/rung3-snapshots/R3-027-L3/20261126-071620-pill-gone.png
- rung3-run-log/rung3-snapshots/R3-027-L3/act1.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act2.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act3.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act4.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act5.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act6.json
- rung3-run-log/rung3-snapshots/R3-027-L3/act7.json
- rung3-run-log/rung3-snapshots/R3-027-L3/probe-ready.json
- rung3-run-log/rung3-snapshots/R3-027-L3/req-serp1.json
- rung3-run-log/rung3-snapshots/R3-027-L3/holder-task.log
- rung3-run-log/rung3-snapshots/R3-027-L3/holder-pid.txt
- rung3-run-log/rung3-snapshots/R3-027-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-027-L3/end_time.txt

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks. I have not seen scorer 1's verdict or reasoning for R3-027.

## Reasons

- No gradeable results exist. The snapshot holds no ket-qua.txt and none of the 3 username-result screenshots the key section requires, because the service returned no availability results for any of the 3 names (rung3alpha01, rung3bravo02, rung3charlie03). The pass criteria in the key section and the list section 6 task text cannot be satisfied from results that were never produced.
- The block is documented in the snapshot evidence itself. 20261126-071051-hcaptcha-blocked.png shows namechk.com loaded with "rung3alpha01" typed in the search field and an unsolved "I'm not a robot" reCAPTCHA gate directly under the search box (widget text notes the site is exceeding its reCAPTCHA Enterprise free quota), with no results on the page. brief-report.txt records the same: the search was submitted at about 07:07, the captcha gate was present at 07:10:51, no results loaded, and the drive stopped there. (The runner's report labels the gate hCaptcha; the screenshot shows the reCAPTCHA widget. The classification is the same either way: a service-side bot check.)
- The block was not caused by the runner's behavior. act1.json to act7.json are a single ordinary user flow: click the address bar, Ctrl+L, type "namechk", Enter, click through the search result, click the search field, type the first username once, one Search click. holder-task.log shows only page-read evaluate calls used for navigation, with no repeated search submissions, no retries against namechk, and no tab spam. The gate appeared on the first search for the first username.
- List section 1 defines a task as invalid when the service shows a bot-check page or reCAPTCHA, recorded out of the sample. The scorer-2 brief adds that a bot check makes a task invalid when the block is not caused by the runner's behavior, which is what the sealed action record shows here.
- This is not a FAIL: no wrong platform results were recorded, no different checker site was substituted, and the runner stopped at the gate without solving it or hammering the service, as the bot-check rule requires.
