# Redteam: Worker Y4d diagnose-first implementation (attack before live rerun)

- Date: 2026-11-21, ~18:30 +07
- Target: uncommitted diff in `tests/realistic/run_live.py` and
  `tests/realistic/run_agyq2.py` on branch `todolist-push`, plus the full
  new code in both files, against the design in
  `improvements/worker-y4b-hidden-body-root-cause.md`.
- Method: read every changed line, traced each claim to a concrete
  execution path. No live run, no browser driving, no ydotool.
- Scope note: the Y4d code was reviewed as found in the working tree.
  Line numbers below are from that working tree.

## Verdict: BLOCK

Do not run the live agy-q2 rerun on this code. One hole (H1) makes the
rerun unable to start at all under its own documented launch, so the
handover window would be burned on a preflight failure. Two more holes
(H2, H3) break the safety and legitimacy conditions the design itself
imposes. The remaining holes are real but fixable in the same pass.
Fix H1-H3, re-verify with the checks listed under each hole, then rerun.

## H1 (BLOCKER): preflight lock check can never pass, rerun cannot start

File: `tests/realistic/run_agyq2.py`, `preflight()`, line 1189.

```python
if len(parts) < 6 or parts[1] != "POSIX" or parts[3] != "WRITE":
    continue
```

The real `/proc/locks` format, verified live on this VM, is:

```
7: FLOCK  ADVISORY  READ 742 00:42:3369848 0 EOF
```

Fields after split: `[0]` id (`7:`), `[1]` lock type (`FLOCK`,
`POSIX`, or `OFDLCK`), `[2]` mode (`ADVISORY`), `[3]` access
(`READ`/`WRITE`), `[4]` pid, `[5]` `dev:ino`, `[6]` start, `[7]` end.
The code requires `parts[1] == "POSIX"`. The lock in question is held
by `fcntl.flock` (`scripts/zen_dom.py` line 85,
`fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)`) and by
the documented launch command (`flock -w 1800
~/.cache/agent-computer-use/zen_dom.lock -c ...`,
`improvements/worker-y4-run-log.md` lines 48-49). Both produce a
`FLOCK` entry, never a `POSIX` entry. POSIX locks come from
`fcntl.lockf`, which nothing in this path uses.

Exploit trace: launch exactly as documented, under `flock -w`, with
`LIVE_OWNER_AWAY=1`. Preflight reads `/proc/locks`, finds the `FLOCK
WRITE` entry for the lock inode, skips it because `parts[1]` is
`FLOCK`, ends with `holders == []`, and raises at line 1206
(`PREFLIGHT: no flock holder on zen_dom.lock; run must be launched
under flock`). `main()` returns 2. No tab opens, no test runs. The
fail-closed direction is right, but the predicate is wrong, so it
fails closed on every correct launch. The likely operator response,
deleting or bypassing the lock check to get the run going, destroys
the single-session safety the check exists for.

Note the other indices are correct: `parts[3]` is the access
(`WRITE`), `parts[4]` is the pid, `parts[5].rsplit(":", 1)[1]` is the
inode. Only `parts[1]` is wrong.

Fix: `parts[1] != "FLOCK"`. Then verify live before the rerun: hold
the lock with `flock` in one shell and run `preflight()` in another;
it must print `PREFLIGHT OK`. Also verify the negative: run without
`flock` and confirm it still refuses.

Related, same function, lower severity: the ancestor walk at lines
1203-1211 builds `ancestors` from ppids only and never includes
`os.getpid()` itself. If the lock were ever held by the Python
process itself via `fcntl.flock` (the `zen_dom.py` style) instead of
by the `flock` CLI wrapper, the holder would be the process itself
and the check would falsely refuse. The documented launch uses the
CLI wrapper, so this is latent, not live. Fix by adding
`os.getpid()` to `ancestors`.

Also in the same sweep (lines 1145-1176): `/proc/<pid>/stat`
`.split()[3]` is the ppid only when the comm field contains no
spaces. `geckodriver` has no spaces, so the sweep itself is safe,
but the same index is reused for the ancestor walk, where a comm
with spaces would silently shift every field. Parse stat by finding
the last `)` instead of splitting blindly. And the kill sequence
(SIGTERM, sleep 1, `kill(pid, 0)`, SIGKILL) never reaps or
re-verifies: if the pid is recycled inside that 1 s window, SIGKILL
lands on an unrelated process. Narrow, but the fix is cheap: re-read
`/proc/<pid>/cmdline` and confirm it still names geckodriver before
SIGKILL.

## H2 (BLOCKER): owner-away check is one env var, no independent check

File: `tests/realistic/run_agyq2.py`, `preflight()`, lines 1109-1111.

```python
if os.environ.get("LIVE_OWNER_AWAY") != "1":
    raise RuntimeError("PREFLIGHT: LIVE_OWNER_AWAY is not 1; ...")
```

That is the entire safety case. There is no idle-time check, no
input-activity check, no re-check per test, no expiry, and no log
line recording that idle time was not independently verified.

Three concrete failures:

1. The council fix paper (`improvements/worker-y4b-council-fix.md`
   line 73) required a two-part check: explicit authorisation PLUS a
   recent-input check if a reliable idle source is available, and if
   none is available, a log line recording that idle time was not
   independently verified. The implementation silently drops part 2
   entirely. It does not even do the fallback logging.
2. Nothing in the repo shows who sets the variable for this rerun.
   The launch command recorded in `improvements/worker-y4-run-log.md`
   lines 48-49 does NOT set `LIVE_OWNER_AWAY` at all, so that exact
   command now fails preflight. The rerun launcher must add it, and
   the only thing stopping a tired operator from adding it while the
   owner is at the keyboard is the operator's own judgment. Y4b says
   never infer away-from-silence; the env var is itself an assertion,
   not a measurement, and it is checked once, before the suite, while
   the suite runs for minutes during which the owner could return.
   The 17:59 input freeze (owner keyboard and mouse dead for about
   1 minute during probe tab navigation) is exactly the harm this
   gate exists to prevent.
3. The variable is inherited. A stale `export LIVE_OWNER_AWAY=1` in a
   reused shell, a cron environment, or a copied launch line passes
   preflight with no fresh human decision behind it.

Reconciliation: the env var does satisfy the design's "explicit
authorisation, never inferred from silence" half. It satisfies none
of the measurement half. There is also a standing handover order in
memory (2026-11-21 18:24, the owner handed the machine over, out of the
house), but the code neither cites it nor checks it; an env var set
for that window stays valid after the window ends.

Fix: add an independent idle check (Hyprland idle time, or
`/dev/input` activity, whichever is readable on the laptop; if none
is readable, print and log `idle-time NOT independently verified`
and require a second explicit confirmation token, e.g. a
timestamped handover file, not a bare env var). Re-check idle before
each test, not just once in preflight. Record who set the flag and
when in the run log.

## H3 (BLOCKER): tz-hidden removal has disclosure in the JSON but no tracked item, and the headline still reads green

Design requirement (`worker-y4b-hidden-body-root-cause.md`, fix
design): removing the class masks a real user-facing defect, so the
intervention must be disclosed in the test report AND tracked as a
separate item to fix or disable the extension. The design states the
fix is legitimate only paired with that tracked item.

What the code actually does:

- Disclosure is half present. `_log_diag` (`run_agyq2.py` lines
  148-179) writes a JSONL record and prints a `HIDDEN-BODY` line.
  `ensure_visible` (lines 253-258) sets `r.details["tz_hidden_removed"]`
  and prints an `INTERVENTION removed tz-hidden` line. The suite
  summary (lines 1288-1297) prints `passed`, `clean`, `flagged`, and
  `hidden_body_encounters` in one JSON object.
- But the headline still reads green. `main()` line 1312 returns
  `0 if passed == len(results) else 1`, and `passed` counts flagged
  passes. A 10/10 run with 3 flagged passes exits 0, prints
  `passed: 10`, and any consumer reading `pass` per test
  (`Runner.summary`, `run_live.py` lines 483-487, `pass` is
  `len(self.failures) == 0`) sees 10 passes. `clean` and `flagged`
  sit in the same JSON line, but nothing forces a reader, a script,
  or an exit-code check to notice them. Nobody reading the headline
  knows the browser is sick.
- The tracked item does not exist. I searched the repo for any
  tracked item, TODO, issue, or follow-up file for the Transparent
  Zen defect: there is no `worker-y4d*` file, no entry in any
  todolist or board file, and no reference outside the Y4b papers
  and the code comments. The pairing is asserted in the docstring
  ("counted separately, never folded silently into the headline
  number", lines 226-231) and not implemented anywhere else.

Fix: create the tracked item first (file or issue, with owner and
deadline: fix or disable Transparent Zen 0.9.4, or blacklist
`127.0.0.1` in its settings), cite its path in the run report, and
make the suite exit non-zero (or print a distinct `SUITE FLAGGED`
headline) whenever `flagged > 0`, so a flagged green can never be
mistaken for a clean green. Until the item exists, the removal step
must be treated as unapproved masking, not as a legitimate recovery.

## H4 (HIGH): diagnose-first is false for run_live.py, and refresh() never diagnoses anywhere

The choke-point claim holds only on the agy-q2 path, not on the
shared driver both runners use.

1. `WD.goto` (`run_live.py` lines 325-349) diagnoses and stores the
   result in `self.last_diagnosis`, but no caller in `run_live.py`
   ever reads it. `run_one` (lines 1284-1300) runs the test function
   and prints the summary; the comment at lines 335-339 claims
   "other runners print the warning below", but the only warning is
   the `[diag]` print at lines 346-348, after which the test proceeds
   to click and type anyway. A hidden body in t01-t10 or f01-f10
   therefore fails at the first `type_text` with Marionette's
   "element not interactable" error, misreported as a fixture
   failure, not as `INFRA: hidden-body`.
2. `run_t05` and `run_t06` (`run_live.py`) open NEW tabs by clicking
   a link/popup button and then type into them after only
   `wait_ready()` plus a sleep. Those are fresh tabs, the exact
   incident-2 pattern (6 of 6 new tabs hidden), with zero diagnosis
   on the new tab. `switch()` (0.5 s settle, no diagnose) is the only
   guard.
3. `WD.refresh()` (`run_live.py` lines 351-358) never diagnoses and
   leaves `last_diagnosis` stale from before the reload. In
   `open_fixture` (`run_agyq2.py` lines 277-313) the order is:
   `goto` (diagnoses load 1), `eval` clearStorage (executes JS on
   load 1), `refresh()` (reloads to load 2, runs `wait_ready()` evals
   and a 1.0 s sleep on load 2 with no diagnosis), and only then
   `ensure_visible` diagnoses load 2. So JS executes on the fresh
   load before any diagnosis of that load. The evals are reads and a
   storage clear, not clicks, so the practical harm is small, but
   the claim "diagnose before ANY interaction" is false as written.
   The true invariant is "diagnose before click/type", and it holds
   only where `ensure_visible` is called.
4. `diagnose_body` (`run_live.py` lines 154-175) does not wrap the
   first snapshot eval (line 165, `snap1 = d.eval(_DIAG_JS)`). If a
   tab has an open alert, that eval raises, and the exception
   propagates out of `ensure_visible`, `rebootstrap_tab`, and
   `bootstrap_tab` as a raw error, not as `INFRA: hidden-body`, so
   the infra counter never increments and the abort logic never
   sees it. `WD.goto` wraps the same call; the other three callers
   do not.

Fix: make `goto` raise, or make every test entry call
`ensure_visible` (including t05/t06 after switching to a new tab),
add a diagnose at the end of `refresh()` and refresh
`last_diagnosis`, and wrap `snap1` eval in `diagnose_body` so a
failed eval returns `FIXTURE_FAILURE` instead of raising.

## H5 (HIGH): mid-suite stall is not recovered, the ladder just fails twice and aborts

The suite shares ONE tab (`bootstrap_tab`, `run_agyq2.py` lines
1039-1095). If the extension chain stalls DURING the suite, every
later test inherits the same hidden tab, and the ladder does not
recover that case when the stall is `OTHER_HIDDEN` or when new tabs
also hide.

Exact trace for q03-q10, assuming the stall starts at q03 and new
tabs hide 6 of 6 (incident 2 rate):

- q03 `open_fixture`: `goto` on the shared tab diagnoses hidden.
  `ensure_visible` polls 2.0 s (no self-clear), classification is
  `OTHER_HIDDEN` (no `tz-hidden` class), so the removal step is
  skipped by design. `rebootstrap_tab` scans handles (no visible
  fixture tab), creates 3 new tabs, each diagnoses hidden, each is
  closed. Raises `RuntimeError`. `ensure_visible` returns
  `(False, False)`. `open_fixture` raises `INFRA: hidden-body`.
  `infra_blocked` becomes 1. q03 fails.
- q04: `r.tab` is still the same hidden shared tab (main loop only
  updates `tab` when `r.tab` changes, lines 1280-1282). Identical
  path, identical outcome. `infra_blocked` becomes 2, `abort_infra`
  fires, the suite breaks. q05-q10 never run. Results are truncated
  to 4 tests, exit code 1.
- If the stall is V1 instead, the removal step can rescue each test
  individually as a FLAGGED pass, but the class is re-added at
  `document_start` on every next `goto`, so each subsequent test pays
  the poll plus removal again, and the flagged count grows while the
  underlying defect persists. There is no persistent fix and no
  re-check of the old tab.

Two more defects in the same path:

- `open_fixture` allows one rebootstrap per test, but the rebootstrap
  tab is verified VISIBLE only on `about:blank`. The fixture load on
  it is a fresh navigation, which can hide again (the content script
  runs at `document_start` on every navigation, including in a reused
  tab; the design doc itself records that the old "reused tab avoids
  the loading screen" story is false). If the second
  `ensure_visible` swaps again (`swapped2`), `open_fixture` raises
  `INFRA` without trying a third tab, even though a visible tab
  existed seconds earlier.
- The old hidden tab is never re-checked. It lingers for the rest of
  the suite and is only navigated to `about:blank` at cleanup. No
  evidence is ever collected about whether it cleared, which is the
  same evidence gap the Y4b synthesis flags in both incidents.

Fix: on a mid-suite stall, after the first INFRA, re-diagnose the
old shared tab before abandoning it (it may have cleared), and do
not count a stall that hides the rebootstrap fixture load as a final
INFRA until at least one more fresh tab has been tried. Record the
old tab's later state in the log either way.

## H6 (MEDIUM): the rAF counter is not null-broken, but it is near-useless as evidence

The task brief asserted the second sample reads `rafTicks=null` on a
fresh load because `refresh()` wipes the counter. That is incorrect
as written, and I am recording the correction, not the claim:
`diagnose_body` (`run_live.py` lines 154-175) evals
`_RAF_INSTALL_JS` before `snap1` in the same call, so after a
refresh the counter is reinstalled, `snap1` reads about 0 (the first
callback has not fired yet), and `snap2` 300 ms later reads an int
(about 18 at 60 fps if ticks flow, 0 if they do not). `rafDelta` is
therefore normally a number, not null, in exactly the hidden cases.

The metric is still not worth citing, for three reasons:

1. It measures only 300 ms on a counter installed by the measurement
   itself. It cannot answer the question the design needs: whether
   ticks flowed during the minutes the tab was hidden before
   diagnosis. It cannot produce the 5 s gap history the design doc
   demands for the decisive experiment.
2. A 300 ms window cannot distinguish frozen rAF from background
   throttling (about 1 Hz in a background tab) or a busy main thread.
   A delta of 0 in that window will be misread as "ticks frozen",
   which would resurrect the dead V2 mechanism by accident.
3. The install eval is swallowed (`try: d.eval(_RAF_INSTALL_JS)
   except Exception: pass`, lines 158-160). If it fails, `rafTicks`
   is null and `_log_diag` (`run_agyq2.py` lines 158-168) records
   `rafDelta300ms: None` silently, with no warning that the metric
   is absent. Null is logged as if it were data.

Fix: either extend the sample to a 5 s window with largest-gap
history (as the design doc specifies) and warn loudly when the
counter is absent, or delete the metric and stop printing `rafDelta`
in run reports. Do not cite the 300 ms delta as evidence for or
against any mechanism.

## H7 (MEDIUM): "two consecutive INFRA" aborts on non-consecutive INFRA

`main()` (`run_agyq2.py` lines 1268-1272) increments `infra_blocked`
on an INFRA exception and resets it to 0 only in the `else` branch,
i.e. only when a NON-INFRA runner exception occurs. A passing test
does not reset it. Trace: q03 INFRA (`infra_blocked` 1), q04 passes
(still 1), q05 INFRA (2, abort). The abort message says "two
consecutive INFRA-blocked tests", but q03 and q05 were not
consecutive; a pass intervened. A recoverable suite aborts early on
a miscount.

Fix: reset `infra_blocked = 0` on the success path, after
`TESTS[tid](r, d)` returns without raising.

## H8 (MEDIUM): the 8 s ladder budget is false, worst case is about 15 s per hidden test

The docstring (`run_agyq2.py` lines 222-231) and the design doc both
say 8 s total budget per tab opening. Count the actual worst path
for one hidden test: poll loop 2.0 s (each iteration also sleeps
0.3 s inside `diagnose_body` when hidden, so about 2.2 s), removal
plus 0.5 s plus re-diagnose 0.3 s, `rebootstrap_tab` up to 3 new tabs
at about 2 s each (`switch` 0.5 s + `goto` settle 1.0 s + diagnose
0.3 s) for about 6 s, then the second fixture load (`goto` about
1.3 s + `refresh` about 1.3 s + second `ensure_visible` up to
2.5 s). Total is about 14-16 s, double the claimed budget. The
budget is not enforced anywhere; there is no deadline check around
the ladder.

Fix: either enforce a real deadline (pass a deadline into
`ensure_visible` and `rebootstrap_tab` and stop creating tabs when
it expires) or correct the docstring and design to the measured
worst case. The handover window planning uses this number, so a
wrong budget is a planning bug, not a cosmetic one.

## H9 (LOW-MEDIUM): FIXTURE_FAILURE is routed to rebootstrap and reported as INFRA hidden-body

`_classify_snapshot` (`run_live.py` lines 130-151) returns
`FIXTURE_FAILURE` when there is no body. `ensure_visible`
(`run_agyq2.py` lines 222-275) treats every non-VISIBLE, non-V1
classification the same: skip removal, go to `rebootstrap_tab`.
A 404 fixture, a dead fixture server, or a page that genuinely has
no body therefore burns 3 new tabs and is finally raised as
`INFRA: hidden-body`, which mislabels a fixture or server failure
and sends the next investigator after the extension instead of the
server. Also, if the `snap2` eval fails inside `diagnose_body`,
the classification becomes `FIXTURE_FAILURE` even when `snap1`
showed `TZ_STUCK_V1`, so a transient eval error silently skips the
removal step that would have fixed the tab.

Fix: branch on `FIXTURE_FAILURE` before the ladder: raise
`INFRA: fixture-unavailable` (or a fixture failure, not a
hidden-body INFRA) without creating tabs, and prefer `snap1`'s
classification when `snap2` fails.

## H10 (LOW): scan touches user tabs, and two small hygiene bugs

1. `rebootstrap_tab` (lines 183-201) and `bootstrap_tab` (lines
   1058-1075) loop over ALL handles and eval `document.URL` on each,
   including user tabs and the alert tab. That is a read-only touch,
   but the design's never-do list says never touch a user tab, and
   the scan also leaves the current window sitting on a user tab
   mid-scan. Restrict the scan to handles already known to be test
   tabs where possible, and switch back to a known test tab if the
   scan finds nothing.
2. `WD.__enter__` (`run_live.py` line 196) opens the geckodriver log
   file before `Popen`. If `Popen` raises (missing `/tmp/geckodriver`),
   the handle leaks and no cleanup runs. Move the open after a
   successful `Popen`, or wrap it in try/except with cleanup.
   Related: the pid/log paths are keyed only by `WD_PORT`, so two
   concurrent `WD` sessions on the same port overwrite each other's
   pid file, and the first session's `_cleanup` unlinks the second
   session's pid file. Single-session operation makes this latent,
   but the pid file is exactly what preflight trusts to kill
   orphans, so a collision there is a safety-relevant race.
3. Preflight's Marionette check (lines 1117-1122) only proves
   something accepts a TCP connection on 2828, not that it speaks
   Marionette. A stale listener would pass. Send a real Marionette
   handshake or accept the weakness in a comment.

## What is actually sound (so the fix pass does not regress it)

- The V2 removal is correct: class-absent plus computed-hidden is
  `OTHER_HIDDEN`, and the repaint step is rightly gone.
- The switch-away step is rightly gone; nothing in the new code
  switches to a user tab as a recovery.
- The removal eval itself is scoped correctly: test tab only, test
  origin only, single class, logged as an intervention.
- The orphan fix in `WD.__enter__` (cleanup on session-create
  failure) and the abort-heuristic fix (only session-creation
  failures count toward `wd_failures`) are correct and should be
  kept.
- `_classify_snapshot` correctly treats visible-plus-opacity-0 as
  `OTHER_HIDDEN`, not `VISIBLE`.

## Fix checklist (in order, re-verify each)

1. H1: `parts[1] == "FLOCK"`. Live check: hold lock, preflight
   must pass; release lock, preflight must refuse.
2. H3: create the Transparent Zen tracked item with owner and
   deadline; cite it in the report; make `flagged > 0` exit
   non-zero or print a distinct flagged headline.
3. H2: add an independent idle check plus per-test re-check, or a
   timestamped handover token; log when idle was not verified.
4. H4: `refresh()` diagnoses; `run_live.py` callers consult
   `last_diagnosis`; t05/t06 diagnose new tabs; wrap `snap1` eval.
5. H7: reset `infra_blocked` on success.
6. H5: re-diagnose the old shared tab after a stall; do not finalise
   INFRA on a hidden rebootstrap fixture load without one more tab.
7. H9: branch `FIXTURE_FAILURE` out of the hidden-body ladder.
8. H6: extend rAF sampling to 5 s with gap history, or delete it.
9. H8: enforce a real ladder deadline or correct the budget.
10. H10: narrow the handle scan, fix the log-handle leak, handshake
    Marionette in preflight.

## Files changed by this review

- `improvements/worker-y4d-redteam.md` (this file) only. No code
  touched, no A1 pilot files touched.
