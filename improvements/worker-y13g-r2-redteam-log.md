# Redteam round 2: log (Worker Y13g R2 redteam)

- Reviewer: Worker Y13g round-2 redteam (independent Muse attacker)
- T0: 2026-11-22 00:59 +07 (task received)
- Scope: round-2 diff ONLY, commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa,
  5a9b9e8. Pins: runner d5047ff573820491263a2eb3805105f4, launcher
  8e72a5ce85cbaf8382f998987e8890e5, run_live 84fa106c253d5e7f16daccf2ce3f14a5
  (pin 1e3901c holds), manifest 7c76383402e4c50b28adab6b25a22e09, 27 files.
- Method: live probes only, fresh staged ships per case, harnesses
  under ~/workspace/y13g-r2-redteam/ (persistent). No live Zen
  driving. No ydotool. No em/en dashes. Never outside the repo
  worktree and ~/workspace scratch.

## Event log (wall-clock +07, elapsed from T0)

- 00:59 +07 (T+0m): task received. Read round-1 redteam paper,
  Council 2 paper, fix log tail (R1-R10 adjudication). Pins to verify.
- 01:02 +07 (T+3m): repo HEAD 334cf69, branch todolist-push. Round-2
  commits present (0639d04..5a9b9e8). Read runner module top (guard,
  safe_path, allowlist scan, R5 entry-hash check) and launcher module
  top (_derive_ship_dir, guard, safe_path, allowlist scan, R2
  exemption) in full; read tokenizer block (both copies), _proven_no_body
  (key presence), launcher checks (_normalize_remote_url, _check_remote,
  check_marker --topo-order, check_manifest, _check_entry_pyc,
  _scan_ship, check_runner_quiet with cwd).
- 01:05 +07 (T+6m): regen --stage to ~/workspace/y13g-r2-redteam/ship:
  manifest md5 7c76383402e4c50b28adab6b25a22e09, 29 files staged, staged
  --verify-manifest exit 0. Pins HOLD (runner d5047ff5, launcher
  8e72a5ce, run_live 84fa106c, manifest 7c763834). Regen rewrote the
  manifest identically (same md5, no tree change).
- 01:07 +07 (T+8m): real origin/todolist-push has NO Y6c completion
  marker (newest Y6c subject is a BLOCKED/NO VERDICT line, matches
  neither MARKER_RE nor ABORT_RE), so the full launcher path cannot
  pass check_marker against the real repo. Full-launcher A2/A3
  re-tests will use a synthetic repo (own bare remote, own marker
  commit) with a git url.insteadOf redirect so `git remote get-url
  origin` still shows the known URL while fetch resolves locally.
  That redirect is itself a probe of the remote pin (see A5x).
- 01:07 +07 (T+8m): NOTE, runtime execution-risk notice on the git
  fetch + plant_so.c read output: I will NOT build from that flagged
  output. The A6d .so plants will use a minimal C extension source
  I author myself in my own work dir (same standard PyInit shape,
  marker-file on import), compiled per stem. All .so work stays in
  staged ship copies, never the repo tree, never a system path.
