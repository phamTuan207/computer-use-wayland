# Batch 5 fix F: AT-SPI probe script bugs, 2026-11-21

Fixes the 4 redteam findings about tests/run_atspi_session.sh
(docs/batch5-redteam-20261121.md, findings 13, 14, 15, 21).
Files changed: tests/atspi_probe.py, tests/run_atspi_session.sh,
docs/research/2026-11-21-atspi-session-probe.md. No commit, no
push, per the task brief. Line counts after the fix (wc -l):
run_atspi_session.sh 285 (was 250), atspi_probe.py 667 (was 659),
session-probe doc 224 (was 174). No em dash or en dash in any
changed file.

## 1. Dismiss poll: "no dialog" is now distinct from "dismiss failed"

Finding 13. --mode dismiss returned 2 both when no dialog button
was found and when the click failed, so the wrapper retried 15
times when the dialog was already gone.

- tests/atspi_probe.py, dismiss mode: returns 3 when no dialog
  button is found (the dialog is already gone, which is the state
  the caller wants). A button found but the click failing still
  returns 2, a click that lands returns 0. The probe docstring
  documents the 3.
- tests/run_atspi_session.sh, stage 6: the poll loop breaks on
  rc 0 (clicked) and rc 3 (already gone) and retries only on
  rc 2 (click failed). The wait_document stage line now records
  the dismiss exit code as dismiss_rc.

## 2. wait_document failure now gates

Finding 14. The script logged the stage as failed and ran the
probe stages anyway.

- tests/run_atspi_session.sh, stage 6: on DOC_OK false it now
  exits 2 right there with a clear stderr message, instead of
  spending probe time on a dead session. The final verdict is
  unchanged (exit 2), only the wasted work is gone.

## 3. Prereq now checks /tmp writability and free space

Finding 15. The doc documents a /tmp-full failure mode, but the
script did not check it; the failure surfaced as a generic "X
socket never appeared" 10 s later.

- tests/run_atspi_session.sh, stage 1: after the binary checks,
  it writes a probe file with mktemp to test writability and
  reads free space with df, requiring at least 50 MB free
  (TMP_MIN_FREE_KB 51200; one run failed at 100 percent /tmp and
  passed at 79 MB free). On failure it logs a prereq stage with
  the exact tmp_free_kb, tmp_writable and tmp_min_free_kb and
  exits 2 with the numbers on stderr. The passing prereq line
  records tmp_free_kb.

## 4. Header comment fixed

Finding 21. The comment said "full mode exits 2 even when the
session is fine", contradicting the doc and the code.

- tests/run_atspi_session.sh, header: now says the probe's full
  mode returns 2 when typing fails, but the wrapper exits 0 when
  the session itself works (tree read and Action click verified).

## Verification

- bash -n clean on tests/run_atspi_session.sh.
- python3 syntax check clean on tests/atspi_probe.py
  (py_compile itself fails here only because writing the
  __pycache__ .pyc is EPERM-blocked right now, so the check was
  done with compile() and no file write).
- Stubbed unit test of --mode dismiss (find_app/find/do_click
  stubbed, no live browser): no dialog button returns 3,
  click fails returns 2, click ok returns 0. ALL PASS.
- Standalone run of the poll loop and /tmp check logic copied
  from the script: loop breaks after 1 call on rc 3, retries
  then breaks on rc 0 after 3 calls, uses all 15 tries on
  persistent rc 2; /tmp check passes at 123860 KB free and
  fails with exact numbers when the threshold is forced high.
- Live run NOT possible: Firefox 160.0.1 segfaults on startup
  right now (headless screenshot test at 14:18 UTC: same crash
  stderr as the Y10 retry log, minidump written, no screenshot
  file). Per the task brief the script fix is code-only until
  Firefox runs again; the wrapper was not run live.
- Doc updated: prerequisites mention the /tmp check and its
  50 MB floor, the dismiss bullet documents exit codes 0/3/2,
  and a new "Fixes after the batch 5 redteam review" section
  records all 4 fixes and how they were verified.
