# Scorer 1 grade, R3-L3, R3-004

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-004 (Tier B hybrid, position 4, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 20:56:58 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-004-L3/ at todolist-push commit 25ce78bb, manifest_sha256 47f9d4f5fd4f6d53eb783b1c583b9e2e87e6bfe8f3a78901b8f6858aa9eb1f09, all 4 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-004-L3/manifest.json (snapshot R3-004-L3, commit 25ce78bb)
- rung3-run-log/rung3-snapshots/R3-004-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-004-L3/20261125-204802-doc-reopened.png
- rung3-run-log/rung3-snapshots/R3-004-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-004-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-004 section only (lines 146-158)
- docs/rung3-answer-keys.json, R3-004 entry only (hybrid_keys entry)
- docs/rung3-list-100-tasks.md, section 6, R3-004 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, did not open the Google Doc link or re-browse the Go documentation, and did not read any runner log, ledger, or trial report.

## Key (R3-004, Tier B hybrid)

Document: "Download and install" of Go, official page https://go.dev/doc/install, Linux tab. Verified 2026-11-23. 5 installation steps in order (numbered steps 1-5 in the document; the document's numbered step 6, "Confirm that the command prints the installed version of Go", is NOT among these 5):
1. Remove old Go installation by deleting /usr/local/go (if exists), then extract the downloaded archive into /usr/local: rm -rf /usr/local/go && tar -C /usr/local -xzf go1.14.3.linux-amd64.tar.gz
2. Add /usr/local/go/bin to PATH: export PATH=$PATH:/usr/local/go/bin (in $HOME/.profile or /etc/profile)
3. Add $HOME/go/bin to PATH to use tools installed via go install: export PATH="$PATH:$(go env GOPATH)/bin" (in $HOME/.profile or $HOME/.bashrc)
4. Restart any open terminal sessions for the changes to take effect
5. Verify by opening a command prompt and typing: go version
Document link at the end of the runner's document: https://go.dev/doc/install. Key-scored part: all 5 steps in order, each step matches 1 numbered step in the document, no merging 2 steps, no vague writing, link with correct go.dev domain. Human-scored part: each step records a specific command or action, actionable. Evidence: saved online document (5 steps + link), reopen to check.

## Evidence

- ket-qua.txt (1513B) gives Google Doc link https://docs.google.com/document/d/1ZpfV1VzTlxer5HqLbRpMI8a_XTgzv7RecksuaL8_Y44/edit and 5 numbered steps, then the link https://go.dev/doc/install at the end.
- The screenshot 20261125-204802-doc-reopened.png (725489B) shows the Google Doc ("Go download and install steps R3-004") open with all 5 steps and the link VISIBLE in the document body, matching ket-qua.txt exactly. The tab list shows the "Download and install" Go doc page open. The doc was saved and reopened for checking, as the task requires.
- Step-by-step comparison:
  - Step 1: remove old Go by deleting /usr/local/go, then extract the archive into /usr/local with rm -rf /usr/local/go && tar -C /usr/local -xzf go1.27.4.linux-amd64.tar.gz. Action and command structure match the key's step 1. See the version note below.
  - Step 2: add /usr/local/go/bin to PATH with export PATH=$PATH:/usr/local/go/bin (in $HOME/.profile or /etc/profile). Matches the key's step 2.
  - Step 3: add $HOME/go/bin to PATH with export PATH="$PATH:$(go env GOPATH)/bin" (in $HOME/.profile or $HOME/.bashrc). Matches the key's step 3.
  - Step 4: restart any open terminal sessions. Matches the key's step 4.
  - Step 5: verify by opening a command prompt and typing go version. Matches the key's step 5.
- All 5 steps in order, no step merges 2 document steps, no vague step, each step has a specific command or action. The document's numbered step 6 is correctly NOT included as a step. The link is https://go.dev/doc/install (correct go.dev domain).
- Timing: start 2026-11-25T20:31:17+07:00, end 2026-11-25T20:51:04.594988+07:00 (19 min 47 s), plausible. No timing red flag.

## Version-number note (read this)

The runner's step 1 uses go1.27.4.linux-amd64.tar.gz; the frozen key records go1.14.3.linux-amd64.tar.gz. I accept step 1 as matching on substance. The version number in the tarball filename is a live value from the official page that changes with each Go release, and the task requires extracting the steps from the LIVE official document. The runner correctly took the current version from the live page. go1.14.3 is a 2020 release and appears stale in the key (the key was verified 2026-11-23, when Go was already at 1.27.x). Failing the runner for using the current version from the live page would punish correct task execution. The action and command structure of step 1 are identical to the key. I flag this for the coordinator audit: the key's frozen version number is stale, and a note that the version is a live value would prevent this mismatch in future runs. This is a key staleness note, not a reason to invalidate the task: the 5 steps' actions are clear and the task is scorable.

## Reason

All 5 installation steps are present in order, each matches the corresponding numbered step in the official Go document with a specific command or action, the document's step 6 is correctly excluded, and the link is the correct go.dev URL. The saved document is evidenced by the reopened screenshot with all content visible.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
