#!/usr/bin/env python3
"""Fix-pass-7 probe for run_batch3.py (Y14b).

Covers the consolidated fix-pass-7 scope from the fix-pass-6
reviews (redteam worker-y14b-fix6-redteam.md [UNCOMMITTED in
the working tree, landing blocked by an execution-risk check;
see the log], Council 1 0cc8e27, Council 2 4e905e2,
Council 3 7bd6516), all AMEND, none BLOCK.

R6-1/U1 (redteam, REQUIRED): backslash escapes in the quote
  state tracking. _quote_states and _top_level_sep_index now
  skip the char after a backslash when outside single quotes
  (the shell rule). Proven forms: codex prompt 'a \"b;
  marionette', python -c code 'x=\"a\\\"b\"; import run_batch3',
  the shell apostrophe idiom 'don'\''t stop; marionette'.
R6-2/C6-3 (redteam + Council 2, REQUIRED): "(" and ")" dropped
  from the _runner_basename_head cut set (cut at ";", "&", "|"
  only). Council 2's fix subsumes the redteam's "(" only; the
  ")" cut was pre-existing fix5 behaviour, dropped by the same
  correction.
C6-1 (doc): log line 1006 stale rstrip set, fixed in the log
  (not probed here).
C6-2 (doc): _top_level_sep_index docstring now states the
  helper DOES return a top-level index for an unquoted "a=1;"
  (verified: returns 3, not -1).
C6-4 (doc): B12 example corrected to the no-separator form
  `python3 -c "import os" echo import run_batch3` (not probed
  here; the code fix itself is the B12 direct case below).
U-C3-1 / INFO-1 (doc): the "(fail-closed)" label replaced with
  the synthetic-only wording (not probed here).
R6-4/U3 (doc): one sentence in the _in_shell_c_string
  docstring bounding the R5-4 fix (not probed here).
C6-3 doc note: `grep -r bash -c run_batch3.py` added to the
  _is_runner_cmdline docstring C2-5 list (not probed here).

Base: the fix6 probe (71 checks, committed in 57fcdb2),
unchanged except this header. New cases use argv lists joined
with NUL (the redteam's construction) for the backslash forms,
so the escaping matches the redteam's proven cases exactly.

Run: python3 y14b-fix7-probe.py (from tests/realistic).
Exit 0 = all PASS. Counts are by PASS lines, not the summary.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, ".")
import run_batch3

FAILURES = []


def check(name, got, want):
    ok = got == want
    print(("PASS" if ok else "FAIL"), name,
          "got", got, "want", want)
    if not ok:
        FAILURES.append(name)


def cmd(argv):
    return "\x00".join(argv) + "\x00"


def unit(name, cmdline, want, codex=False):
    if codex:
        got = run_batch3._is_codex_executor(cmdline)
    else:
        got = run_batch3._is_runner_cmdline(cmdline)
    check("unit " + name, got, want)


def argv_unit(name, argv, want, codex=False):
    unit(name, cmd(argv), want, codex=codex)


def live(name, argv, want, codex=False):
    """Live check: spawn the argv (stub sleeps), read the
    WRAPPER's real /proc cmdline, run the predicate on it,
    kill children first then the wrapper by exact PID."""
    env = dict(os.environ,
               PATH="/tmp/y14b-dummies:" + os.environ["PATH"])
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env)
    time.sleep(0.3)
    try:
        raw = open(f"/proc/{p.pid}/cmdline", "rb").read()
        cmdline = raw.decode("utf-8", "replace")
    except Exception:
        cmdline = ""
    children = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat") as f:
                stat = f.read()
            rest = stat[stat.rfind(")") + 2:].split()
            if int(rest[1]) == p.pid:
                children.append(int(entry))
        except Exception:
            pass
    for pid in children:
        try:
            os.kill(pid, 9)
        except Exception:
            pass
    try:
        p.kill()
    except Exception:
        pass
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

# --- Live checks (real /proc cmdlines, fix6) ---
live("R5-1 B1 live: python3 -c import time; sleep; import run_foo",
     ["python3", "-c", "import time; time.sleep(60); import "
      "run_foo"], True)
live("R5-2 A1 live: bash -o pipefail -c run_foo.py",
     ["bash", "-o", "pipefail", "-c", "python3 "
      "/tmp/y14b-dummies/run_foo.py"], True)
live("R5-3 C1 live: bash -c python3 run_foo.py&&echo",
     ["bash", "-c", "python3 /tmp/y14b-dummies/run_foo.py&&echo "
      "done"], True)

# --- R6-1: backslash escapes (fix pass 7, redteam U1) ---
# Argv-list construction, exactly the redteam's proven cases.
argv_unit("R6-1 (a) codex prompt escaped double quote True",
          ["bash", "-c", 'codex -c "a \\"b; marionette"'],
          True, codex=True)
argv_unit("R6-1 (b) python -c escaped double quote True",
          ["bash", "-c",
           'python3 -c "x=\\"a\\\\\\"b\\"; import run_batch3"'],
          True)
argv_unit("R6-1 (c) shell apostrophe idiom don'\\''t True",
          ["bash", "-c",
           "codex -c 'don'\\''t stop; marionette'"],
          True, codex=True)
argv_unit("R6-1 control: apostrophe in double quotes True",
          ["bash", "-c", 'codex -c "don\'t; marionette"'],
          True, codex=True)
argv_unit("R6-1 control: bare dont, marker in later cmd True "
          "(redteam unreachable form: returns True at unit level, "
          "but bash exits 2 syntax error live, never reaches a "
          "scan; the unbalanced apostrophe makes the tracker read "
          "everything after it as inside quotes, fail-closed)",
          ["bash", "-c", "codex -c don't stop; echo marionette"],
          True, codex=True)

# --- R6-2/C6-3: paren cut dropped (fix pass 7) ---
unit("R6-2 C15 python3 run_foo.py(x now False",
     "python3\x00run_foo.py(x\x00", False)
unit("R6-2 C15b bash -c python3 run_foo.py(x now False",
     "bash\x00-c\x00python3\x00run_foo.py(x\x00", False)
unit("C6-3 b19 python3 run_foo.py) now False",
     "python3\x00run_foo.py)\x00", False)
unit("C6-3 python3 run_foo.py() now False",
     "python3\x00run_foo.py()\x00", False)
unit("C6-3 control: run_foo.py;echo still True",
     "bash\x00-c\x00python3\x00run_foo.py;echo\x00done\x00", True)
unit("C6-3 control: run_foo.py&&echo still True",
     "bash\x00-c\x00python3\x00run_foo.py&&echo\x00done\x00", True)
unit("C6-3 control: run_foo.py|cat still True",
     "bash\x00-c\x00python3\x00run_foo.py|cat\x00", True)
unit("C6-3 control: run_foo.py&echo still True",
     "bash\x00-c\x00python3\x00run_foo.py&echo\x00done\x00", True)

# --- Live checks (fix pass 7, R6-1) ---
live("R6-1 (a) live: codex prompt escaped double quote",
     ["bash", "-c", 'codex -c "a \\"b; marionette"; sleep 60'],
     True, codex=True)
live("R6-1 (c) live: shell apostrophe idiom",
     ["bash", "-c", "codex -c 'don'\\''t stop; marionette'; "
      "sleep 60"], True, codex=True)

print("FAILURES:", len(FAILURES), FAILURES)
sys.exit(1 if FAILURES else 0)
