# Worker C4-BENCH-MANIFEST log: fixture 2-vision bench re-run plus CB-9 manifest lock

Owner: Pham Tuan. Worker: C4-BENCH-MANIFEST, for COORD-CLICK-4.
Branch: todolist-push. Repo HEAD at start: d7d569b
(d7d569be5c9f88986abdd8416143c64981667986).
Start: 2026-11-22 09:00 +07 (Asia/Ho_Chi_Minh). All times below are
wall-clock +07 unless noted. Standing rules: no em dash (U+2014) or
en dash (U+2013) anywhere in this file, no personal info, never
ydotool, full access, explicit pathspec commits only, every push
verified with git ls-remote.

Basis read first: improvements/worker-click3-final-direction-log.md,
section 1.4 CB-9 row, section 2 item (i), section 3 step 3, section 4
precondition and rung 1; improvements/worker-click4-step1-closeout-log.md
(commit 4ac9320), section 5; scripts/sync-installed.py, the 18f2304
CB-9 mechanism (_write_deploy_manifest, _verify_deploy_manifest).

Headline: bench PASS at d7d569b, wall 12.6852s, visions_used 2,
run_id bench-20261122T020225Z-3d9270, both sends V12 gated.
Manifest LOCKED in deploy-manifest.json for the exact build under
test (source commit d7d569b, source content digest
92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607,
artifact hashes, log of the same build). Rung 1 is now QUOTABLE
as a gate, for THIS run at THIS build. The old a1a672d pass still
has no manifest of its own and stays unquotable; this new run is
the quotable one.

## 1. Why the main checkout was not used for the bench

The main checkout at 09:00 +07 was dirty with other workers'
in-progress work (modified scripts/dom_act.py and scripts/zen_dom.py,
plus untracked files including worker logs and step-5 scripts), so
it could not pin a build. The bench ran in a clean worktree instead
and the main checkout was untouched by the bench run.

Worktree: /tmp/click4-bench-manifest, `git worktree add
/tmp/click4-bench-manifest d7d569b` (detached HEAD, verified
d7d569be5c9f88986abdd8416143c64981667986, `git status --short`
empty before and after the run).

## 2. Bench runtime setup

The probe-s2 venv was gone: /tmp/probe-s2-venv was wiped by the VM
restart about 07:51 +07, same restart that wiped the S0 soak. System
python3 has no selenium and system pip is PEP 668 blocked, same as
at probe-s2 time. Recreated identically (09:02 +07):

```
python3 -m venv /tmp/probe-s2-venv
/tmp/probe-s2-venv/bin/pip install -q "selenium==4.53.0"
/tmp/probe-s2-venv/bin/python -c "import selenium; print('selenium', selenium.__version__)"
```

Output: `selenium 4.53.0`. Python 3.12.3. Firefox 160.0.1,
geckodriver 0.36.0 (a3d508507022 2025-02-24 15:57 +0000). Ports
2828 and 9223 free before the run, no stale Firefox.

Note: the bench file tests/two_vision_bench.py hardcodes the
fixture path to the MAIN checkout
(file:///home/hatch/workspace/computer-use-wayland/tests/two_vision_fixture.html),
not the worktree. The executed script was the worktree copy; the
fixture read was the main-checkout file. That file is byte-identical
to the worktree copy and clean in git (sha256 147494cd... for both,
git diff clean), so the bench still ran against HEAD content. The
manifest records both paths with the same hash and refuses to lock
if they ever differ. See section 4.

## 3. Bench re-run at d7d569b: PASS 12.6852s

Command (from the worktree, fresh workdir so the ledger is clean):

```
/tmp/probe-s2-venv/bin/python tests/two_vision_bench.py --fixture \
  --workdir /tmp/click4-bench-workdir \
  --out /tmp/click4-bench-workdir/results.json
```

Run: 2026-11-22 09:02:25-09:02:38 +07 (02:02:25-02:02:38 UTC).
Exit 0. Output (verbatim, from /tmp/click4-bench-run.log):

```
{"step": "browser_launch_manual", "wall": "2026-11-22T02:02:30.936589+00:00", "elapsed_s": 5.2743, "pid": 42975}
{"step": "marionette_attach_session", "wall": "2026-11-22T02:02:35.900818+00:00", "elapsed_s": 4.8227}
{"step": "window_opened", "wall": "2026-11-22T02:02:36.227712+00:00", "elapsed_s": 10.5691, "window": "clone1", "url": "file:///home/hatch/workspace/computer-use-wayland/tests/two_vision_fixture.html?clone=1"}
{"step": "window_opened", "wall": "2026-11-22T02:02:36.986805+00:00", "elapsed_s": 11.3282, "window": "clone2", "url": "file:///home/hatch/workspace/computer-use-wayland/tests/two_vision_fixture.html?clone=2"}
{"step": "vision1_harvest_one_shot", "wall": "2026-11-22T02:02:37.221668+00:00", "elapsed_s": 0.1581, "window": "clone1", "elements": 4}
{"step": "vision1_harvest_one_shot", "wall": "2026-11-22T02:02:37.309495+00:00", "elapsed_s": 0.0424, "window": "clone2", "elements": 4}
{"step": "vision1_inventory_written", "wall": "2026-11-22T02:02:37.312068+00:00", "elapsed_s": 11.6535, "path": "/tmp/click4-bench-workdir/inventory.json"}
{"step": "send_ok_v12", "wall": "2026-11-22T02:02:37.941579+00:00", "elapsed_s": 0.6088, "window": "clone1", "intent_id": "bench-20261122T020225Z-3d9270:clone1"}
{"step": "send_ok_v12", "wall": "2026-11-22T02:02:38.343691+00:00", "elapsed_s": 0.3867, "window": "clone2", "intent_id": "bench-20261122T020225Z-3d9270:clone2"}
{"step": "benchmark_finished", "wall": "2026-11-22T02:02:38.343962+00:00", "elapsed_s": 12.6854, "outcome": "PASS", "wall_s": 12.6852, "out": "/tmp/click4-bench-workdir/results.json"}
```

Results (/tmp/click4-bench-workdir/results.json, sha256
84f43d67f2ddfde3162e1187418539da6e24ba86d7c6febcd6de7a70a9e44ad9):

- run_id: bench-20261122T020225Z-3d9270
- mode: run, live: false, instances: one
- outcome: PASS
- wall_s: 12.6852
- visions_used: 2
- step 1 clone1: sent, 0.6088s, v1_value_ok true, v11_input_events 47, v12_gate_ok true
- step 2 clone2: sent, 0.3867s, v1_value_ok true, v11_input_events 47, v12_gate_ok true

Comparison with the a1a672d pass (10.8596s, clone1 0.6904s,
clone2 0.6807s): same outcome, same gates, same bench code and
fixture blobs (see section 4). Wall time is 1.83s slower, all of it
in browser launch plus attach (5.27s plus 4.82s here); the sends
themselves are as fast or faster. That is launch variance, not a
code change: the bench code and fixture are byte-identical to the
a1a672d build.

## 4. The CB-9 manifest: what the 18f2304 mechanism did not cover

The 18f2304 mechanism (_write_deploy_manifest in
scripts/sync-installed.py) writes deploy-manifest.json into a
SYNCED installed tree, keyed to a release ledger under releases/.
It does not cover this bench shape: the fixture bench runs from a
repo CHECKOUT, not from an installed tree, so there is no installed
tree, no ledger, and no releases/ dir to key a manifest to. A
sync-first workaround would have been dishonest: syncing the tree
to the laptop would produce a manifest for a laptop install the
bench never executed.

Extension (minimal, new file scripts/bench_manifest.py, 4 tests in
tests/test_bench_manifest.py, all passing, see section 5): a
checkout-run bench manifest writer that reuses the sync mechanism's
own digest functions (_source_bundle, _digest_entries, _sha256 from
sync-installed.py, loaded as a module), so source_content_sha256
means exactly what it means in a sync manifest, and writes the same
top level keys (installer, format, source_commit,
source_content_sha256, installed_root) plus a bench section.

Definition of "installed" for a checkout-run bench, recorded in
the manifest itself: the checkout under test IS the installed tree.
The bench executes exactly these artifacts, and only these, so the
manifest hashes exactly these:

- tests/two_vision_bench.py: sha256 c993b0ae199129c3e88860c03d17b6db42752a4758dc28bc5075a4510f9c13cc, git blob 80b00469c4676d7a9a8934626b6bf66ed2a5aeee, 38378 bytes. Same blob as the step-1 closeout recorded for the a1a672d build.
- tests/two_vision_fixture.html: sha256 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf, git blob bac2702efa375ad330cce8130df40d8025d86261, 2014 bytes. Same blob as the a1a672d build. The hardcoded main-checkout path is recorded with the same sha256; the writer refuses to lock if the two copies ever differ.
- Firefox launcher /home/hatch/workspace/tools/firefox/firefox: sha256 852ba4c20cbd62e17fa5da95cf9ddfebcab9fceb344c56f89ee803f45f41a50a, version Mozilla Firefox 160.0.1.
- firefox-bin: sha256 181df71ae9179a3953ee6abb1fb94ba2bc4b2557c741c4a53b9ba20a28e5f5f0.
- geckodriver: sha256 ad7cef75f87a17491abb212ae84923dd29f6782b8347959d21bd138efc2b5f99, version geckodriver 0.36.0 (a3d508507022 2025-02-24 15:57 +0000).
- Python 3.12.3, selenium 4.53.0 (the probe venv python, passed in explicitly; system python3 has no selenium).

What the bench does NOT execute: no repo script at all. It imports
no cu.py, no first_action.py, no session driver, no sync code. So
no repo script belongs in the artifact list. The whole-tree
source_content_sha256 (92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607)
still pins the full checkout, so a bench quote cannot silently
drift to a different tree.

The log of the same build is recorded by PATH
(improvements/worker-click4-bench-manifest-log.md, this file), not
by hash: the log is written after the manifest because it quotes
the manifest, so hashing it here would be circular. Verification
requires the log file to exist and to name the same run_id and
source commit.

Manifest file: deploy-manifest.json at the repo root (the path the
task specifies; the 18f2304 mechanism specifies <installed>/
deploy-manifest.json and for this bench shape the installed root
is the worktree, while the lock copy lives in the repo so it can
be committed). Its installed_root field names the worktree under
test (/tmp/click4-bench-manifest), not the main checkout.

Command:

```
python3 scripts/bench_manifest.py write --repo /tmp/click4-bench-manifest \
  --results /tmp/click4-bench-workdir/results.json \
  --log improvements/worker-click4-bench-manifest-log.md \
  --out ~/workspace/computer-use-wayland/deploy-manifest.json \
  --python-version 3.12.3 --selenium-version 4.53.0
```

Output: `manifest written: /home/hatch/workspace/computer-use-wayland/deploy-manifest.json`,
`source_commit: d7d569be5c9f88986abdd8416143c64981667986`,
`run_id: bench-20261122T020225Z-3d9270 outcome=PASS wall_s=12.6852`.

## 5. Tests for the new mechanism: 4/4 PASS

```
python3 -m unittest tests.test_bench_manifest -v
```

Run: 2026-11-22 about 09:06 +07. Output tail:

```
test_write_pins_commit_and_artifacts ... ok
test_write_refuses_dirty_checkout ... ok
test_write_refuses_non_pass ... ok
test_verify_passes_with_log_then_fails_on_tamper ... ok
Ran 4 tests in 0.490s
OK
```

The tests use a temp git repo with a stub sync module, so they do
not depend on the real checkout or a live browser. Two real
behaviors were caught while writing them and fixed in the script:
the writer refused a dirty tree because importing the sync module
leaves __pycache__ behind (now filtered, same as the source bundle
excludes it), and verify failed on the log file itself sitting
untracked next to the manifest (the log path is now excluded from
the status check as a record file, not source).

## 6. Manifest verification: PASS

The manifest pins the worktree at d7d569b, while the log and the
manifest itself are committed from the main checkout, whose HEAD
moves when this lands. Verification therefore targets the worktree
under test, with the log read from the main checkout:

```
python3 scripts/bench_manifest.py verify \
  --manifest deploy-manifest.json --repo /tmp/click4-bench-manifest \
  --results /tmp/click4-bench-workdir/results.json \
  --log-root ~/workspace/computer-use-wayland
```

Run: 2026-11-22 about 09:08 +07. Output (verbatim):

```
ok source_commit: manifest=d7d569be5c9f88986abdd8416143c64981667986 repo=d7d569be5c9f88986abdd8416143c64981667986
ok source_content_sha256: manifest=92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607 repo=92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607
ok git_status_clean: status=''
ok artifact:bench_script: sha256=c993b0ae199129c3e88860c03d17b6db42752a4758dc28bc5075a4510f9c13cc blob=80b00469c4676d7a9a8934626b6bf66ed2a5aeee
ok artifact:fixture: sha256=147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf blob=bac2702efa375ad330cce8130df40d8025d86261
ok fixture:hardcoded_path: path=/home/hatch/workspace/computer-use-wayland/tests/two_vision_fixture.html sha256=147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf
ok artifact:firefox: path=/home/hatch/workspace/tools/firefox/firefox sha256=852ba4c20cbd62e17fa5da95cf9ddfebcab9fceb344c56f89ee803f45f41a50a
ok artifact:firefox_bin: path=/home/hatch/workspace/tools/firefox/firefox-bin sha256=181df71ae9179a3953ee6abb1fb94ba2bc4b2557c741c4a53b9ba20a28e5f5f0
ok artifact:geckodriver: path=/home/hatch/workspace/tools/geckodriver sha256=ad7cef75f87a17491abb212ae84923dd29f6782b8347959d21bd138efc2b5f99
ok log:exists_and_names_run: log=/home/hatch/workspace/computer-use-wayland/improvements/worker-click4-bench-manifest-log.md run_id=bench-20261122T020225Z-3d9270
ok results:run_id_outcome: run_id=bench-20261122T020225Z-3d9270 outcome=PASS
verify OK: manifest matches the checkout under test
```

Exit 0. Every check passes: commit, content digest, clean tree,
both repo artifacts by hash and blob, the hardcoded fixture path,
all three runtime binaries, the log naming this run, and the
results file agreeing on run_id and outcome.

## 7. Verdict: rung 1 is now quotable, for this run at this build

Section 4 precondition check (FINAL direction): source commit
recorded (d7d569b), installed artifact hashes recorded (bench
script, fixture, Firefox, firefox-bin, geckodriver, plus the
whole-tree content digest), log of the same build recorded (this
file, naming run_id bench-20261122T020225Z-3d9270 and commit
d7d569b). All three limbs are met and machine-verified in
section 6.

Rung 1 QUOTABLE: YES, as "fixture 2-vision bench PASS at d7d569b,
wall 12.6852s, visions_used 2, run_id
bench-20261122T020225Z-3d9270, both sends V12 gated, manifest
deploy-manifest.json verified". The rung-1 pass bar is the
script's own gates (V12 sent-bubble gate after each message,
scoring by OUTCOME in the thread DOM), and both gates passed.

Scope limits, stated plainly:

- The quotable run is THIS re-run at d7d569b, not the a1a672d run.
  The a1a672d pass (10.8596s, run_id bench-20261121T234030Z-86e8d8)
  still has no manifest of its own: the build predates the
  mechanism and the installed tree at bench time is gone, as the
  step-1 closeout already recorded. A retroactive manifest for it
  cannot be manufactured. Its numbers are corroborated by this
  re-run on byte-identical bench code and fixture, but the gate
  quote must cite the new run_id, not the old one.
- The landing commit for this manifest and log will have a
  different tree (it adds deploy-manifest.json, this log,
  scripts/bench_manifest.py, tests/test_bench_manifest.py), so
  the manifest's source_content_sha256 does NOT describe the
  landing commit. It describes the bench build d7d569b. Anyone
  re-verifying must run verify against the worktree at d7d569b
  (still present at /tmp/click4-bench-manifest), not against the
  landing HEAD. The manifest is a lock for the build under test,
  not for the commit that carries it.
- A rung-1 fixture pass proves the fixture only. It does not prove
  the live chat class (rung 2) or the general 90 percent claim
  (rung 3), per section 4 of the FINAL direction.

## 8. Commit record

- Log file: improvements/worker-click4-bench-manifest-log.md
  (this file).
- Manifest file: deploy-manifest.json (repo root).
- Mechanism: scripts/bench_manifest.py plus
  tests/test_bench_manifest.py.
- Commit: (filled at commit time)
- Push verification: (filled at commit time)

Elapsed: task received 09:00 +07; worktree ready about 09:00 +07;
venv recreated 09:02 +07; bench ran 09:02:25-09:02:38 +07; manifest
written about 09:07 +07; mechanism tests green about 09:06 +07;
verification about 09:08 +07; log written about 09:08 +07.
Total about 9 min of wall time plus the 13s bench run.
