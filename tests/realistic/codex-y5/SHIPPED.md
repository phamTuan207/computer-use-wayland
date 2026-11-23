# Y13 codex-y5 live ship (frozen)

Runner: tests/realistic/run_codex_y5.py (Worker Y13, 21/11/2026).
Base: run_live.py from commit 1e3901c ONLY, md5 84fa106c253d5e7f16daccf2ce3f14a5
(Y4d live-proven base; ONE 10/10 live run on these bytes, run 2; run 1 was 8/10).
NOT HEAD: HEAD's run_live.py changed in 91d3cd2 (Y11 live-metrics, +415/-66),
unit-verified only. live_metrics.py must be ABSENT from the ship dir.

Launcher: tests/realistic/launch_y13.py (council A F4 + redteam H5,
Y13f H3 re-review fix, Y13g B1-B4 + 5 amends, Y13g round 2, Y13g
round 3). It performs the launch-time checks (go order asserted,
Y6c marker check with --repo REQUIRED, ship manifest md5 vs the
committed manifest, entry-.pyc out-of-process check,
full-allowlist ship scan, handover token written fresh after the
ship passes its integrity checks then checked, runner-quiet
process check, predecessor + own ports free, no live geckodriver
with a live parent) and then execs the runner under flock -w 60
with `python3 -P -E` (PYTHONSAFEPATH=1, all PYTHON* env vars
ignored at interpreter startup). LIVE RUNS go ONLY via the
launcher; the direct form (`python3 -P -E run_codex_y5.py
--verify-manifest`, `python3 -P -E run_codex_y5.py <tests>`) is
supported WITH -P -E for verify / staging / probes, never for a
live run. --ship-dir DIR (or Y13_SHIP_DIR) points the launcher
at a different ship dir (value space-separated only, must be an
existing directory); a repo-tree path refuses when the launcher
derives the ship dir from the file's own dir (the file-dir
branch), not when an explicit --ship-dir/Y13_SHIP_DIR is given.
The marker check matches subjects only (never --grep), rejects
"harness" subjects, requires the newest completion to be newer
than the newest abort BY GIT LOG --first-parent ORDER
(first-parent branch position, --first-parent --topo-order, not
committer date); a side-branch marker never counts, so markers
must land as first-parent commits. It refuses unless the git
remote, normalized (SSH form incl. ssh://, trailing slashes,
optional .git incl. .GIT, host case), is the known repo remote.
The marker is a COORDINATION SIGNAL among pushers, not
authentication. Script form only: `python3 -P -E launch_y13.py`
and `python3 -P -E run_codex_y5.py`; -m and bare imports are
UNSUPPORTED (both entry points refuse them at the module top,
exit 2) and a forged entry .pyc invoked via -m/import executes,
so no legitimate flow ever invokes -m/import on an unverified
ship. A bare invocation (no -P) refuses at the module top
(sys.flags.safe_path). A non-empty PYTHONPATH also refuses at
the module top (-P does not clear PYTHONPATH, and a planted
stdlib .py in a PYTHONPATH dir would execute at import); -E is
what closes the startup channel: without it the interpreter
itself imports warnings/re/functools/collections at startup, so
a PYTHONPATH plant of one of those names executes before any
module-top code runs (live-proved 2026-11-22). The ship is re-staged from the
committed bytes with (from the repo root):
  python3 tests/realistic/regen_codex_y5_manifest.py --stage /tmp/worker-y13-server
(Regenerate the manifest LAST, after every runner edit; the
launcher refuses a ship whose manifest md5 differs from the
committed manifest. If the manifest md5 mismatches, commit + push
the manifest first, then re-stage.)

How to verify (C3-3): importing either entry point exits 2 (the
script-form-only guard), so the tokenizer and the checks are
verified by AST-extraction (parse the file, take the named
FunctionDef nodes, exec in a fresh namespace with os/sys/json/
hashlib/re/shlex/subprocess/time/marshal and _SHIP_DIR set to
the staged ship), never by importing the module. The tokenizer
is 14 functions, identical in both files (AST-verified):
_script_basename_is_runner, _is_python_token, _shlex_tokens,
_runner_md5s, _path_is_runner_copy, _token_is_runner_script,
_c_code_executes_runner, _m_module_is_runner,
_python_executes_runner, _is_timeout_dur,
_command_executes_runner, _argv_tokens, _is_runner_cmdline,
_is_codex_process, plus the 4 constants _RUNNER_MODULE_NAMES,
_RUNNER_MANIFEST_PATHS, _RUNNER_MD5S, _PY_NO_VALUE. A cmdline
is a NUL-joined argv list, exactly as read from
/proc/<pid>/cmdline. Copy-pasteable check (from the repo root,
against a staged ship at /tmp/ship):
  python3 -c "
  import sys; sys.path.insert(0, 'improvements/y13g-verify')
  import extract_lib
  ns = extract_lib.extract_tokenizer(
      'tests/realistic/launch_y13.py', '/tmp/ship')
  print(ns['_is_runner_cmdline'](
      'python3\\x00-c\\x00exec(open(\\'run_codex_y5.py\\').read())\\x00',
      '/tmp/ship'))"
To extract _check_entry_pyc as well, also take the FunctionDef
_check_entry_pyc plus _fail and the SHIP_DIR constant (the
tokenizer-only extraction above does not cover it). The md5 leg
disables itself silently when the manifest is unreadable or the
extracted copy runs outside a ship dir (the name leg still
catches every named form).

Ship dir (laptop): /tmp/worker-y13-server
Ports: server 8771, WD 4452, Marionette 2828 (shared, connect-existing).
Handover token: /tmp/worker-y13-handover.json (written by the launcher after the ship passes its integrity checks).
JSONL: /tmp/worker-y13-live.jsonl. Shots: /tmp/worker-y13-shots/.
Gecko log: /tmp/geckodriver-4452.log (copied per test).

Launch (on the laptop, from /tmp/worker-y13-server, ONLY after the
Y6c completion marker + Muse's go order + the launch-time checks pass):
  cd /tmp/worker-y13-server && Y13_GO=1 python3 -P -E launch_y13.py \
    --repo ~/workspace/computer-use-wayland all \
  > /tmp/worker-y13-stdout.log 2>&1

Manifest: codex-y5-manifest.json, md5 d2a2bf08ae1c942f9bd888793ef7eb2e, 27 files.
Files (path, md5):

- run_codex_y5.py 510336331de0e93c06c3195d52fac51f
- launch_y13.py 3ac1b74524b5f3a6518787f808d5a2f2
- run_live.py 84fa106c253d5e7f16daccf2ce3f14a5
- codex-y5/test-01-git-workflow.md 0f347247c21b2f1375596c1ee51449b4
- codex-y5/test-02-music-player.md 15925f6709c62908dfd5cd88f1fc8c91
- codex-y5/test-03-password-vault.md e931e09bee8d28ca64768f5bc2053f40
- codex-y5/test-04-maps-directions.md 0d59678a646493d17fc8b2efdf518cc3
- codex-y5/test-05-calendar-recurring.md 71cbaa55642161c97d7fc98e9221e72b
- codex-y5/test-06-video-editor.md 842783b7278cf8bb5bc7b1b40d1516cb
- codex-y5/test-07-chat-search.md 3b0c37be71f023d8be148a1c99805971
- codex-y5/test-08-spreadsheet-pivot.md d50ffaee6f2261108551279416c5cd1b
- codex-y5/test-09-file-search-tag.md cae2f8e3afb0c476590e7d6ba5ecfe68
- codex-y5/test-10-extension-settings.md ed5f2b35862784b6b02eafbb185691c7
- codex-y5/simulate.mjs b6c7c9c9c09a0da452c1996a8c43504d
- codex-y5/check.mjs 56312f93fcf8f13eae9b4fabe85d172d
- codex-y5/README.md 217c3edceb42a040f2f601fdddbcdf6a
- codex-y5/check-dashes.py d4e7659f4e6b77dc351c6e7319ed4e61
- codex-y5/fixtures/test-01-git-workflow.html ac0f3f5f6510bbd9c5ccf32e2b2f8301
- codex-y5/fixtures/test-02-music-player.html 0b988fde53e221f6522b6d8965f92113
- codex-y5/fixtures/test-03-password-vault.html 21ecdc2bb9b2ae34fdd1b7ca48e60a80
- codex-y5/fixtures/test-04-maps-directions.html ea6f1365c4d57f030d58e6913f39ac28
- codex-y5/fixtures/test-05-calendar-recurring.html caf9d8acd2440028b135d005ed42a4f2
- codex-y5/fixtures/test-06-video-editor.html 6cd220edc51a1c69c97ae6fcb87d5bb4
- codex-y5/fixtures/test-07-chat-search.html 45a8077d703ee5481092ec316ce26d83
- codex-y5/fixtures/test-08-spreadsheet-pivot.html af10ca0627a72dc8eb8890c0ea3d635d
- codex-y5/fixtures/test-09-file-search-tag.html 16507889dd0cb236339cc11fe6b80f7e
- codex-y5/fixtures/test-10-extension-settings.html 21b2aacee36e9bc3dd7a61dbaba25123

Queue: Y13 runs AFTER Y6c (Wayland-nested) reports completion AND Muse says go.
Y6c ended NO VERDICT (commit 5a2b69d, BLOCKED at launch); Y6d rebuilt the
plugin + launcher (commit 72eb8ad) and Y6e is risk-checking it. The H3 gate
as written matches ^Y6c subjects only, so a Y6d/Y6e commit does NOT satisfy
it; the gate refuses until a fresh Y6c-pattern marker lands or Muse directs
otherwise. Do NOT weaken the gate. Y14 (batch-3 live) queues AFTER Y13.
Y13 completion marker for Y14:
a todolist-push commit matching ^Y13 codex-y5: .*live complete, plus the
log line 'Y13 codex-y5 live complete: <clean>/<flagged>/<total>'.
