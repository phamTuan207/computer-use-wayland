#!/usr/bin/env python3
"""A8 _proven_no_body + AST comparison (Y13g re-verification).

A8: _proven_no_body AST-extracted from the runner. The required
case is eval_error "" with a good snapshot: it must return False
(the Y13g R9 (C2-11) key-presence check, `"eval_error" in diag`;
an explicitly-None eval_error also returns False, not True).
The full 12-case table from the redteam paper is
re-run against the NEW code.

AST comparison: the 14 tokenizer functions must be AST-identical
between the runner and the launcher copies (docstrings stripped;
the only allowed text differences are the two sync-direction
notes). Also diffs the raw tokenizer-block text to show any
non-docstring difference.

Usage: python3 attack_a8_ast.py
"""
import ast
import difflib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify", "ships")
CLEAN = os.path.join(WORK, "clean")
RUNNER = os.path.join(REPO, "tests", "realistic", "run_codex_y5.py")
LAUNCHER = os.path.join(REPO, "tests", "realistic", "launch_y13.py")
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []
GOOD = {"hasBody": False, "readyState": "complete"}

# (label, diag, expected)
A8_CASES = [
    ("eval_error + good snapshot", {"eval_error": "timeout",
                                    "snapshots": [GOOD]}, False),
    ("eval_error '' + good snapshot (REQUIRED)",
     {"eval_error": "", "snapshots": [GOOD]}, False),
    ("eval_error None + good snapshot (R9: now False)",
     {"eval_error": None,
      "snapshots": [GOOD]}, False),
    ("no eval_error + good snapshot", {"snapshots": [GOOD]}, True),
    ("hasBody key missing",
     {"snapshots": [{"readyState": "complete"}]}, False),
    ("hasBody None",
     {"snapshots": [{"hasBody": None, "readyState": "complete"}]},
     False),
    ("no snapshots", {"snapshots": []}, False),
    ("eval_error + no snapshots", {"eval_error": "timeout",
                                   "snapshots": []}, False),
    ("contradictory snapshots",
     {"snapshots": [GOOD, {"hasBody": True,
                           "readyState": "complete"}]}, False),
    ("not complete",
     {"snapshots": [{"hasBody": False, "readyState": "loading"}]},
     False),
    ("eval_error '' + no snapshots", {"eval_error": "",
                                      "snapshots": []}, False),
    ("non-dict snapshot ignored",
     {"snapshots": ["junk", GOOD]}, True),
]


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def tokenizer_block_lines(path):
    """Lines of the shared tokenizer block: from the '# Y13g B3'
    comment to the end of _is_codex_process."""
    lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("# Y13g B3"))
    tree = ast.parse("".join(lines))
    end = None
    for node in tree.body:
        if (isinstance(node, ast.FunctionDef)
                and node.name == "_is_codex_process"):
            end = node.end_lineno
    return lines[start:end]


def main(argv):
    t0 = time.time()
    log("A8-AST START")
    # --- A8 ---
    ns = extract_lib.extract_funcs(
        RUNNER, ("_proven_no_body",), (),
        extra={"_SHIP_DIR": CLEAN, "SHIP_DIR": CLEAN})
    fn = ns["_proven_no_body"]
    for label, diag, want in A8_CASES:
        got = fn(diag)
        check(f"A8 {label}", got == want,
              f"_proven_no_body({diag!r}) = {got}, want {want}")
    # --- AST comparison ---
    for name in extract_lib.TOKENIZER_FUNCS:
        dump_r = extract_lib.func_ast_dump(RUNNER, name)
        dump_l = extract_lib.func_ast_dump(LAUNCHER, name)
        check(f"AST {name} identical",
              dump_r == dump_l,
              f"ast.dump (docstrings stripped) "
              f"runner==launcher: {dump_r == dump_l}")
    # --- raw block text diff (shows only the sync notes) ---
    block_r = tokenizer_block_lines(RUNNER)
    block_l = tokenizer_block_lines(LAUNCHER)
    diff = list(difflib.unified_diff(
        block_r, block_l, fromfile="run_codex_y5.py",
        tofile="launch_y13.py", lineterm=""))
    diff_lines = [l for l in diff
                  if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    log(f"raw tokenizer-block text diff lines: {len(diff_lines)}")
    for l in diff_lines:
        log(f"  diff: {l.rstrip()}")
    allowed = all(("launch_y13" in l or "run_codex_y5" in l)
                  and ("sync" in l.lower() or "Keep in sync" in l
                       or "identical block" in l)
                  for l in diff_lines)
    check("AST raw block diff is only the sync-direction notes",
          allowed and len(diff_lines) <= 6,
          f"{len(diff_lines)} differing lines, all naming the "
          f"counterpart file: {allowed}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A8-AST DONE {npass}/{len(RESULTS)} pass "
        f"in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
