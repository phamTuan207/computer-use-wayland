#!/usr/bin/env python3
"""Fix-pass-6 probe for run_batch3.py (Y14b).

Covers the consolidated fix-pass-6 scope from the fix-pass-5
reviews (redteam 92fbefd + addendum 5f842a2, Council 1 cebd868,
Council 2 cebd868, Council 3 6ba5e09), all AMEND, none BLOCK.

R5-1/C5-1/C2-3: quote-state-aware separator bound.
C5-2/R5-2: _owning_command flag-value skip.
C2-4/R5-3: basename truncate at first separator char.
R5-4: _in_shell_c_string skips a non-shell -c across a sep
  (FIXED in fix pass 6, was "fix or record").
B12: direct python -c argv-boundary (_c_arg_flat_end).
R5-8/C2-5: recorded false positives (expect True).
C5-5: "A1-A14" label corrected to "A1-A9 plus 7 further wrapper
cases" (doc only, not probed here).
C5-6: URL case strengthened to a real URL (Council 1 B15).
C2-9/C2-10/R5-7: "cannot occur in /proc" claim corrected (doc
only, not probed here).

Run: python3 y14b-fix6-probe.py (from tests/realistic).
Exit 0 = all PASS. Counts are by PASS lines, not the summary.

NOTE (Council 2 C6-5, fix pass 6): the author probe files in
/tmp were deleted (all 17 y14b-*.py author probes gone; the
reviewers' own probes remain). This file is the reconstructed
fix6 probe, saved under tests/realistic/ so it persists in the
repo. The -c code is a SINGLE argv element in the direct cases
(a real /proc cmdline carries -c code as one element);
_c_arg_flat_end relies on that boundary.
"""
import sys
sys.path.insert(0, ".")
import run_batch3

FAILURES = []


def check(name, got, want):
    ok = got == want
    print(("PASS" if ok else "FAIL"), name,
          "got", got, "want", want)
    if not ok:
        FAILURES.append(name)


def unit(name, cmdline, want, codex=False):
    if codex:
        got = run_batch3._is_codex_executor(cmdline)
    else:
        got = run_batch3._is_runner_cmdline(cmdline)
    check("unit " + name, got, want)


def live(name, argv, want, codex=False):
    """Live check: spawn the argv (stub sleeps), read its real
    /proc cmdline, run the predicate on it, kill it."""
    import subprocess, time, os
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    time.sleep(0.3)
    try:
        raw = open(f"/proc/{p.pid}/cmdline", "rb").read()
        cmdline = raw.decode("utf-8", "replace")
    except Exception:
        cmdline = ""
    p.kill()
    p.wait()
    if codex:
        got = run_batch3._is_codex_executor(cmdline)
    else:
        got = run_batch3._is_runner_cmdline(cmdline)
    check("live " + name, got, want)


# --- R5-1: quote-state bound, import branch (direct python -c) ---
# NOTE: a real /proc cmdline carries the -c code as a SINGLE argv
# element, so the code is one NUL-separated element here (not one
# element per word). _c_arg_flat_end relies on that boundary.
unit("B1 direct python -c, standalone ; is code",
     "python3\x00-c\x00import os; import run_batch3\x00",
     True)
unit("B2 direct python -c, standalone && is code",
     "python3\x00-c\x00import os && import run_batch3\x00",
     True)
unit("B8 direct python -c, standalone ; before import",
     "python3\x00-c\x00import os; import run_batch3\x00",
     True)
unit("B10 direct python -c, glued ; is code",
     "python3\x00-c\x00import os; import run_batch3\x00",
     True)
unit("B12 nested python -c, glued ; after closing quote blocks",
     "bash\x00-c\x00python3\x00-c\x00'import\x00os';\x00echo\x00import"
     "\x00run_batch3\x00", False)
unit("d4 nested python -c, glued ; after OPENING quote is code",
     "bash\x00-c\x00python3\x00-c\x00'a=1;\x00import\x00run_batch3\x00",
     True)

# --- R5-1: quote-state bound, codex -c branch (spaced seps) ---
unit("B3 codex -c, spaced && inside prompt",
     "bash\x00-c\x00codex\x00-c\x00'run\x00tests\x00&&\x00restart"
     "\x00marionette'\x00", True, codex=True)
unit("B4 codex -c, spaced | inside prompt",
     "bash\x00-c\x00codex\x00-c\x00'run\x00tests\x00|\x00grep"
     "\x00marionette'\x00", True, codex=True)
unit("B5 codex -c, spaced & inside prompt",
     "bash\x00-c\x00codex\x00-c\x00'run\x00tests\x00&\x00check"
     "\x00marionette'\x00", True, codex=True)
unit("B6 codex -c, spaced ; inside prompt",
     "bash\x00-c\x00codex\x00-c\x00'run\x00tests;\x00restart"
     "\x00marionette'\x00", True, codex=True)
unit("B7 codex -c, spaced || inside prompt",
     "bash\x00-c\x00codex\x00-c\x00'run\x00tests\x00||\x00restart"
     "\x00marionette'\x00", True, codex=True)
unit("B11 R3 control: codex -c hello; echo marionette False",
     "bash\x00-c\x00codex\x00-c\x00'hello';\x00echo\x00marionette\x00",
     False, codex=True)
unit("B13 doc limitation: sep BEFORE last quote in one token",
     "bash\x00-c\x00codex\x00-c\x00'a';'b;marionette'\x00",
     False, codex=True)

# --- C5-1: Council 1 regression cases ---
unit("C5-1 B5 python -c x=1; import run_batch3 True",
     "bash\x00-c\x00python3\x00-c\x00'x=1;\x00import\x00run_batch3\x00",
     True)
unit("C5-1 B6 codex -c x=1; marionette True",
     "bash\x00-c\x00codex\x00-c\x00'x=1;\x00marionette'\x00",
     True, codex=True)
unit("C5-1 B7 codex -c a=1; echo marionette True",
     "bash\x00-c\x00codex\x00-c\x00'a=1;\x00echo\x00marionette'\x00",
     True, codex=True)

# --- C2-3: Council 2 nested codex -c cases ---
unit("C2-3 codex -c 'a & b marionette' True",
     "bash\x00-c\x00codex\x00-c\x00'a\x00&\x00b\x00marionette'\x00",
     True, codex=True)
unit("C2-3 codex -c 'a; b marionette' True",
     "bash\x00-c\x00codex\x00-c\x00'a;\x00b\x00marionette'\x00",
     True, codex=True)
unit("C2-3 codex -c 'a && b marionette' True",
     "bash\x00-c\x00codex\x00-c\x00'a\x00&&\x00b\x00marionette'\x00",
     True, codex=True)
unit("C2-3 codex -c 'a;b marionette' True",
     "bash\x00-c\x00codex\x00-c\x00'a;b\x00marionette'\x00",
     True, codex=True)

# --- C5-2/R5-2: _owning_command flag-value skip ---
unit("C5-2 B1 bash -o pipefail -c run_batch3.py True",
     "bash\x00-o\x00pipefail\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 B22 bash -o pipefail -c codex exec marionette True",
     "bash\x00-o\x00pipefail\x00-c\x00codex\x00exec\x00marionette\x00",
     True, codex=True)
unit("R5-2 A2 sh -o pipefail -c run_batch3.py True",
     "sh\x00-o\x00pipefail\x00-c\x00run_batch3.py\x00", True)
unit("R5-2 A3 bash -O nullglob -c run_batch3.py True",
     "bash\x00-O\x00nullglob\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 control: bash --rcfile /tmp/x -c True",
     "bash\x00--rcfile\x00/tmp/x\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 control: sudo -u root bash -c True",
     "sudo\x00-u\x00root\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 control: env -u FOO bash -c True",
     "env\x00-u\x00FOO\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 control: flock -w 5 /tmp/l bash -c True",
     "flock\x00-w\x005\x00/tmp/l\x00bash\x00-c\x00run_batch3.py\x00",
     True)
unit("C5-2 control: nice -n 5 bash -c True",
     "nice\x00-n\x005\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("C5-2 control: env -i bash -c still True (A5)",
     "env\x00-i\x00bash\x00-c\x00run_batch3.py\x00", True)

# --- C2-4/R5-3: basename truncate at first separator char ---
unit("R5-3 C1 run_foo.py&&echo (no space) True",
     "bash\x00-c\x00python3\x00run_foo.py&&echo\x00done\x00", True)
unit("R5-3 C2 run_foo.py;echo (no space) True",
     "bash\x00-c\x00python3\x00run_foo.py;echo\x00done\x00", True)
unit("R5-3 C3 run_foo.py||echo (no space) True",
     "bash\x00-c\x00python3\x00run_foo.py||echo\x00done\x00", True)
unit("R5-3 C4 run_foo.py|cat (no space) True",
     "bash\x00-c\x00python3\x00run_foo.py|cat\x00", True)
unit("R5-3 C5 run_foo.py&echo (no space) True",
     "bash\x00-c\x00python3\x00run_foo.py&echo\x00done\x00", True)
unit("R5-3 over-strip: md5sum run_foo.py stays False",
     "md5sum\x00run_foo.py\x00", False)
unit("R5-3 over-strip: echo run_foo.py stays False",
     "echo\x00run_foo.py\x00", False)
unit("R5-3 over-strip: vim run_foo.py stays False",
     "vim\x00run_foo.py\x00", False)

# --- C2-5/R5-8: bare-word FP (recorded, expect True) ---
unit("R5-8 echo bash -c run_batch3.py (recorded FP)",
     "echo\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("R5-8 ssh host bash -c run_batch3.py (recorded FP)",
     "ssh\x00host\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("R5-8 cat bash -c run_batch3.py (recorded FP)",
     "cat\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("R5-8 grep bash -c run_batch3.py (recorded FP)",
     "grep\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("R5-8 control: python3 script.py bash -c stays False",
     "python3\x00script.py\x00bash\x00-c\x00run_batch3.py\x00",
     False)

# --- R5-4: _in_shell_c_string skips a non-shell -c across a sep ---
# FIXED in fix pass 6 (was recorded): the nearest -c is the python
# -c in an earlier command, so it is skipped and the bash -c is
# found; the marker in the later command does not count.
unit("R5-4 FIXED: codex -c then echo marionette now False",
     "bash\x00-c\x00python3\x00-c\x00'x';\x00codex\x00exec\x00foo;\x00"
     "echo\x00marionette\x00", False, codex=True)
unit("R5-4 control: codex exec foo; echo marionette False",
     "bash\x00-c\x00codex\x00exec\x00foo;\x00echo\x00marionette\x00",
     False, codex=True)
unit("R5-4 control: codex exec marionette True",
     "bash\x00-c\x00codex\x00exec\x00marionette\x00",
     True, codex=True)

# --- B12: direct python -c argv-boundary (redteam rt-probe) ---
unit("B12 direct python -c, import in later argv elem False",
     "python3\x00-c\x00import\x00os';\x00echo\x00import\x00run_batch3"
     "\x00", False)

# --- Controls: fix5 behaviours that must hold ---
unit("F2 control: codex -c import time; x # marionette True",
     "bash\x00-c\x00codex\x00-c\x00'import\x00time;\x00x\x00#"
     "\x00marionette'\x00", True, codex=True)
unit("R3 control: codex -c hello; echo marionette False",
     "bash\x00-c\x00codex\x00-c\x00'hello';\x00echo\x00marionette\x00",
     False, codex=True)
unit("R4 control: python -c import x; echo import run_batch3 "
     "False (redteam tokenization)",
     "bash\x00-c\x00python3\x00-c\x00'import\x00x';\x00echo\x00import"
     "\x00run_batch3\x00", False)
unit("C5-6 URL case (real URL, Council 1 B15)",
     "python3\x00run_batch3.py\x00http://x/?a=1&b=2\x00", True)
unit("standalone ; after complete codex -c arg truncates (R3)",
     "bash\x00-c\x00codex\x00-c\x00'a'\x00;\x00'b;\x00marionette'\x00",
     False, codex=True)

# --- R2 wrappers (A1-A9 plus 7 further cases) ---
unit("env bash -c run_batch3.py",
     "env\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("sudo bash -c run_batch3.py",
     "sudo\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("timeout 60 bash -c run_batch3.py",
     "timeout\x0060\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("nice bash -c run_batch3.py",
     "nice\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("env -i bash -c run_batch3.py",
     "env\x00-i\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("/usr/bin/env bash -c run_batch3.py",
     "/usr/bin/env\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("env FOO=bar bash -c run_batch3.py",
     "env\x00FOO=bar\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("bash -x -c run_batch3.py",
     "bash\x00-x\x00-c\x00run_batch3.py\x00", True)
unit("flock /tmp/lock bash -c run_batch3.py",
     "flock\x00/tmp/lock\x00bash\x00-c\x00run_batch3.py\x00", True)
unit("flock -c run_batch3.py (flock own -c)",
     "flock\x00-c\x00run_batch3.py\x00", True)
unit("dash -c run_batch3.py",
     "dash\x00-c\x00run_batch3.py\x00", True)
unit("sh -c run_batch3.py",
     "sh\x00-c\x00run_batch3.py\x00", True)
unit("bash -c run_batch3.py (plain)",
     "bash\x00-c\x00run_batch3.py\x00", True)
unit("python3 -c run_batch3.py stays False",
     "python3\x00-c\x00run_batch3.py\x00", False)
unit("env bash -c codex exec marionette",
     "env\x00bash\x00-c\x00codex\x00exec\x00marionette\x00", True,
     codex=True)
unit("sudo bash -c codex exec marionette",
     "sudo\x00bash\x00-c\x00codex\x00exec\x00marionette\x00", True,
     codex=True)

# --- Live checks (real /proc cmdlines) ---
live("R5-1 B1 live: python3 -c import time; sleep; import run_foo",
     ["python3", "-c", "import time; time.sleep(60); import "
      "run_foo"], True)
live("R5-2 A1 live: bash -o pipefail -c run_foo.py",
     ["bash", "-o", "pipefail", "-c", "python3 "
      "/tmp/y14b-dummies/run_foo.py"], True)
live("R5-3 C1 live: bash -c python3 run_foo.py&&echo",
     ["bash", "-c", "python3 /tmp/y14b-dummies/run_foo.py&&echo "
      "done"], True)

print("FAILURES:", len(FAILURES), FAILURES)
sys.exit(1 if FAILURES else 0)
