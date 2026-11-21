# Y13f fix log: fix the Y13r re-review BLOCK on the codex-y5 live runner

- Fixer: Worker Y13f (Muse test fixer), 2026-11-21 20:47- +07
- Commit under fix: cb26d1d (Y13), re-reviewed by Y13r (commit f48b54c,
  log improvements/worker-y13r-rereview-log.md + 4 papers). Verdict BLOCK.
- Task: fix every finding exactly as specified in that log, re-verify
  mechanically, regenerate the manifest LAST, commit on todolist-push.
- No live driving (Y11b holds the live slot now; Y6c nested is running).
- No ydotool, no em/en dash, no personal info. All checks timed/logged.

## Start state (20:47 +07)

- Repo tests/realistic/__pycache__/ held 11 .pyc files (incl.
  run_live + run_codex_y5), gitignored build artifact. DELETED before
  any edit: the H1 pre-import scan refuses any .pyc under the ship dir,
  and the repo dir is the scan root when the module is imported from
  the working tree, so a stale __pycache__ would fail every probe
  import. The staged ship /tmp/worker-y13-server/__pycache__/ also
  holds run_live.cpython-312.pyc (the exact H1 attack surface); it is
  re-staged clean by the regen script, never hand-edited.
- MEMORY.md (parent, 20:39): Y11b metrics proof PASS (8e4331c); Y6c
  nested now running; Y13 next after Y6c. H2 noted as a shared
  runner-pattern bug; Y14 must apply the same fix when it re-stages.

## Fix plan (Y13r log order)

- H1 (HIGH): forged __pycache__ bypasses the M1 allowlist. Fix in
  three layers: (1) sys.dont_write_bytecode before the run_live
  import + PYTHONDONTWRITEBYTECODE=1 in the launcher env, so this
  ship never writes .pyc; (2) a pre-import scan at the top of
  run_codex_y5.py (before ANY ship import) that refuses any .pyc
  file or any symlink under the ship dir with exit 2 -- the manifest
  check in main() runs AFTER run_live is imported, so it alone
  cannot stop a forged .pyc from executing (the marker prints
  first); the scan is what makes "exit 2 with no marker printed"
  achievable; (3) _verify_manifest refuses any .pyc / __pycache__
  dir (the line-406 skip becomes a refusal) as defense in depth.
  Ship-time deletion lives in the regen script --stage (it assembles
  the curated ship and deletes __pycache__ there). The launcher does
  NOT delete __pycache__ at launch: silent deletion would hide a
  tampered ship; the runner scan refuses instead.
- H2 (HIGH): process regex misses bare-relative launches (/proc
  cmdlines are NUL-separated). Fix: tokenize argv in BOTH copies
  (launcher + preflight) and require a python interpreter token
  before the script token (or the script as argv[0], or first word
  of a -c string, or bash/sh for non-.py run-nested scripts). This
  also kills the path-mention false positive (md5sum /abs/run_x.py
  no longer trips). The exact tokenizer code is recorded in this log
  AND in the plan, so Y14 applies the SAME fix to run_batch3.py when
  it re-stages (Y14 files NOT edited here). Cycle guard added to
  both preflight ancestry walks.
- H3 (HIGH): Y6c queue gate blind twice. Fix: (a) Y6c process names
  (run-nested-pill.py, run-nested-wayland[.sh]) in the patterns
  (via the shared tokenizer); (b) marker matched against SUBJECTS
  only (git log --format=%H%x09%ct%x09%s, regex applied in Python);
  (c) wording tightened (require a run token or a verdict token,
  reject any subject containing "harness"); (d) freshness/ordering
  rule (completion must be newer than the last abort; an abort newer
  than the newest completion refuses); (e) --repo REQUIRED (no more
  operator-assertion fallback) and in the SHIPPED.md launch line.
- M1 (MEDIUM, wall cap): tag the trip as WallCapExceeded, handle it
  in main() BEFORE the diagnose block (live failure directly, never
  diagnose-reclassify, never re-run); fix the docstring. Cumulative
  attempt-2 trip kept by design (it trips, but does not spend a
  re-run slot).
- M2 + L2 (MEDIUM/LOW): _proven_no_body returns False when
  diag.get("eval_error") is present (redteam wins the adjudication:
  the fail-safe direction is INFRA over fixture-unavailable); use
  s.get("hasBody") is False. Docstring rewritten to the actual rule.
- AMEND: F1 (regen script incl. the 1e3901c run_live.py pin, command
  recorded in SHIPPED.md + plan); F8 (msg = f"{type(exc).__name__}:
  {exc}"); H4 after-rebootstrap site split (lines 987-993) +
  docstring/plan wording (plan lines 81-82, 378-380, written to the
  ACTUAL rule as implemented under the redteam M2 win: eval_error
  present is INFRA, period; Council 2 fix 5 wording assumed Side B,
  which lost the adjudication, so it is NOT used); F9 nits (wrap the
  marker typeof eval; None typeof is inconclusive); M1 allowlist
  symlink-dir bypass (os.walk, refuse any symlink, refuse any dir
  that is not a prefix of a manifest path; launcher compares ship
  manifest md5 vs the committed manifest from git when --repo is
  given -- this also closes the pin-decline substitute gap); L1
  (marker exception classes InfraError / FixtureUnavailableError,
  isinstance in step(); launcher check_token isinstance dict +
  float wrap); L3 (skip suite-end tab cleanup when aborted_handover);
  L4 (cumulative_elapsed_ms on session-creation-failure summaries);
  L6 (park warning recorded structurally in the suite JSON);
  L7 (Y4d ports 8768/4448 + 8770/4450 in both port lists);
  codex processes (refuse when the cmdline mentions hand_drive_e1,
  geckodriver, a browser profile path, or Marionette; warn otherwise;
  implemented in launcher AND preflight).

## Timed work log

- 20:47 +07: start. Read the Y13r log + all 4 papers, the runner
  (4222 lines), the launcher (305 lines), the manifest, SHIPPED.md,
  the plan lines 81-82 / 378-380, Y14's port gate (run_batch3.py
  line 1949: ports 8767-8770/4448-4451, flat range, no labels).
  Deleted the stale repo __pycache__ (11 .pyc). This log created.
- 20:55 +07: MEMORY.md update (parent): Y6c ended NO VERDICT
  (commit 5a2b69d, BLOCKED at launch: F0 --socket, F1 hyprglass ABI,
  U5b wrong log). That commit matches NEITHER the H3 completion NOR
  the abort pattern, so the H3 gate as specified will refuse until
  Y6d's rebuild run produces a fresh marker (or Muse directs
  otherwise). Verified via git log: the only Y6c commit on
  todolist-push is 5a2b69d. NOT worked around; recorded in the plan.
- 20:47-21:05 +07: all code edits done (runner + launcher + regen
  script + plan). Details: H1 pre-import scan + dont_write_bytecode
  + verify refuses any .pyc/symlink/non-prefix dir; entry-point
  .pyc exemption found necessary by live test (CPython writes the
  self .pyc during get_code, before the module code sets the flag;
  a plain import recreated exactly the self .pyc and refused --
  proven 21/11, then fixed by exempting the two __main__ entry
  .pyc files only); H2 tokenizer in both copies + cycle guards +
  codex refuse rule; H3 subject-only marker + harness reject +
  freshness/ordering + --repo required + launcher manifest-md5
  comparison; M1 WallCapExceeded + main() pre-diagnose branch;
  M2/L2 _proven_no_body eval_error + hasBody is False; H4
  after-rebootstrap split; F8 type-name msg; F9 marker eval wrap
  + None inconclusive; L1 marker classes + isinstance in step() +
  launcher check_token; L3 cleanup skip on abort; L4 cumulative key
  on session failure; L6 park warnings in suite JSON; L7 ports
  8768/4448 + 8770/4450 in both lists. 10 INFRA + 3 FIXTURE raises
  converted to marker classes by script, 0 remaining RuntimeError
  forms (grep verified). py_compile NOT used after the scan landed
  (it writes .pyc into the repo dir); syntax checked via the
  import itself + compile() where needed.

## Verification (all probes in /tmp/y13f/, own implementations)

- Forge + negative manifest (probe_forge.py): 14/14 PASS. Clean
  ship exit 0; forged run_live .pyc refused exit 2 with NO marker
  printed; tamper, extra top-level .py, extra suite-dir file,
  planted file, symlink file, symlink dir, non-dict manifest,
  dropped file, B1 exact (duplicate + dropped spec), escape entry,
  non-JSON manifest all refuse exit 2. NOTE: Y13r's forge script
  file itself was NOT run (a system execution-risk flag on its
  tool-result delivery); the forge here is a fresh implementation
  from the task description (header mtime/size from source stat,
  attacker bytecode printing a marker). The re-review should
  treat the H1 gate as proven by this equivalent probe.
- Tokenizer unit table (probe_tokenizer.py): 34/34 PASS, identical
  verdicts in both copies (bare-relative, absolute, flock -c,
  shell -c, python -u, run-nested hyphen, bash run-nested .sh,
  hand_drive_e1, md5sum/grep path mentions pass, codex plain
  passes, direct exec matches).
- Live process probe (probe_process_live.py): 14/14 PASS on the
  second run (twice, the second time under Y14b-style background
  load). Real dummies refused: bare-relative, absolute, flock -c,
  shell -c, Y6c bare + absolute, codex+geckodriver, live
  geckodriver + live parent. Plain codex (warn only), md5sum
  mention, dead pid file, orphan geckodriver pass. FIRST RUN:
  cases 8/9 failed (rc=2) with the refusal detail truncated by
  the probe, offender unidentified; the probe was fixed to print
  full output + kill process groups (flock/sh children survived a
  plain kill and left 3 sleepers, killed by hand), and the re-runs
  pass with every refusal naming exactly the intended dummy. The
  transient offender was most likely a concurrent fleet process
  (Y14b was verifying run_batch3.py at that minute); Y14b's
  reconstructed cmdlines were tested offline and do NOT match the
  tokenizer, so the offender remains unidentified, not a known
  false positive.
- Marker + manifest-md5 (probe_marker.py): 13/13 PASS on a
  synthetic bare remote + clone. Harness subject, body-DONE under
  "Fix flake", no Y6c commits, completion touching only README,
  abort newer than completion all refuse; completion newer than
  abort, verdict REPRODUCED, run DONE all pass; no --repo and
  non-git --repo refuse. Ship md5 == committed passes; the REAL
  cb26d1d manifest as a stale ship refuses; missing ship manifest
  refuses. PROBE BUG found and fixed mid-run: the first
  reset_branch reset to a stale origin/todolist-push, leaking the
  case-5 abort into cases 6-8; fixed by resetting to the recorded
  base commit.
- _proven_no_body + park (probe_body.py): 13/13 PASS. All 11 table
  cases incl. the redteam proof (eval_error + good snap1 -> False)
  and hasBody None -> False. L6: keeper tab in opened_tabs records
  one structured warning and is removed.
- Wall cap / step / reload / H4 (probe_wallcap.py): 14/14 PASS
  with the REAL diagnose_body + a scripted fake driver. W1 trip
  raises WallCapExceeded; W2 under cap passes; S1 nested trip
  unwrapped; S2 InfraError/FixtureUnavailableError unwrapped; S3
  plain RuntimeError mentioning INFRA stays wrapped; R1 reload ok;
  R2 click-raised tolerance; R3 marker survived fails; R4 marker
  eval raise fails "marker check failed"; R5 marker None fails
  "inconclusive"; H4a after-rebootstrap proven no-body raises
  FixtureUnavailableError; H4b transport error raises InfraError.
- main() stub harness (probe_main.py): 6/6 PASS. M1 wall-cap trip
  + TZ diagnose -> failed, 1 attempt, no re-run. M2 plain failure
  + TZ -> infra-blocked + re-run, pass on attempt 2. M3 bare
  TimeoutError + VISIBLE -> infra-blocked + re-run (F8 works).
  M4 "fixture timeout waiting for" + VISIBLE -> failed, no re-run
  (wording guard works). M5 handover abort -> rc 2, Y13WD entered
  exactly once (smoke only), zero cleanup drives (L3 works). M6
  session failure -> summary carries cumulative_elapsed_ms (L4).
- Transcription (probe_transcription.py): 30/30 identical under
  node (10 ids x empty/WRONG/exact). Parsed _VERIFY_JS value:
  14 single-\n, 0 double-\n. Exact maps are per-test (83 entries:
  77 equal + 6 extra); #delete-status differs between test-03
  ('Entry restored') and test-05 ('Deleted 2026-12-21'), so a
  single global map would have given test-03 the wrong value --
  the first run used a global map and the probe was fixed to
  per-test maps before the 30/30 pass.
- AST + audit (probe_ast_audit.py): 13/13 PASS. AST recount
  matches STEP_COUNTS exactly per test, total 626. First run was
  +7 on EVERY test (total 696): the recount had followed the call
  graph into open_fixture, which holds exactly 7 r.step/r.check
  calls but runs with audit DISABLED, so they are not in the
  table; excluding open_fixture makes it exact. Audit sim 10/10
  (jsonl == STEP_COUNTS); a 1-record shortfall on test-05 is
  caught (58 vs 59).
- Launcher dry runs (probe_launcher.py): 8/8 PASS. D1 no Y13_GO,
  D2 no --repo, D3 no marker, D5 stale ship (real cb26d1d bytes),
  D6 non-dict token, D7 non-numeric asserted_at_unix all refuse
  exit 2. D4 all clear passes every launcher check ("launch
  checks passed; taking flock", MANIFEST OK, SERVED FILES OK)
  and the runner fails preflight on BiDi 9222 as expected on the
  VM (rc 2). D8 own port 8771 answering refuses ("own port 8771
  answers"). Two probe-assertion errors were fixed mid-run: D4
  first required rc != 2 (the runner legitimately returns 2 for
  preflight failure), and D8 first expected the wrong message
  ("predecessor port 8771" / "SERVER FAILED" -- 8771 is an OWN
  port, refused by check_ports). D8 failed twice more with rc=2
  before passing; the standalone re-run shows the expected
  refusal, so the flakes were transient concurrent fleet load,
  not a launcher defect.
- Dash check: 0 em/en dashes in the runner, launcher, regen
  script, SHIPPED.md, plan, and this log.
- __pycache__ pollution, twice: the pre-import scan refused
  imports because tests/realistic/__pycache__ held run_agyq2 /
  run_batch3 / run_live .pyc files -- once from Y14b's
  `python3 -m py_compile tests/realistic/run_batch3.py`, once
  from my own background `python3 -c "import run_batch3"` (its
  .pyc writes landed AFTER my rm -rf). Both times the scan did
  exactly what it should (fail closed); the regen script deletes
  the cache before regenerating. Y14b should use compile(), not
  py_compile, on ship files. Every probe run deletes the cache
  first and imports with PYTHONDONTWRITEBYTECODE=1.

## Final ship (21/11 ~21:29 +07)

- Manifest regenerated LAST: 27 files, md5
  f27c03020c9866cfa0dcd637df6f8647. Runner
  3cc5fa11a4be533c1bb49941008bfa75, launcher
  2b02c5ec85ef474bfcddf4b59dcacc0f, run_live 84fa106c (1e3901c
  pin holds). SHIPPED.md updated (new md5s, launch line with
  --repo, regen command, Y6c NO VERDICT + Y6d 72eb8ad + Y6e
  risk-check queue note) and verified byte-identical to the
  manifest (27/27, md5 match).
- Staged ship /tmp/worker-y13-server re-staged from the final
  bytes: --verify-manifest exit 0, manifest_ok true, 27 files.
- Y6d DONE (per MEMORY.md 21:29 update): launcher v3 + C2 ALL
  PASS VM 42 + laptop, commit 72eb8ad; Y6e is risk-checking it.
  The H3 gate still matches ^Y6c subjects only, so no Y6d/Y6e
  commit satisfies it as written; the gate refuses until a fresh
  Y6c-pattern marker lands or Muse directs otherwise. NOT
  weakened here.
- Total wall time: start 20:47, ship staged 21:29 +07 (~42 min).
- Commits (todolist-push): 118c67f (code fixes + regen script +
  plan), <commit-2-TBD> (manifest + SHIPPED.md + this log).
