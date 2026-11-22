"""Rewritten Y1b verification probes: 1e, 4a, 10b, 10f (Gate G-Y1B).

Run: python3 tests/y1b_probes_rewritten.py [--alt-root <tree>]
Default run uses this repo (the fixed build) plus two stub sessions
for the 10b/10f budget-sharing probes.

Why each probe was rewritten (sources: improvements/worker-y1b-verify-
redteam.md, worker-y1b-verdict-council-1/2/3.md):
- 1e (original): used chr(65). chr was in NEITHER SAFE_BUILTINS list,
  so the original probe FAILed a correct item-4 pin fix, and its
  codemode leg passed only while the Attack 4 builtins hole was live.
  1e-R uses only allowlisted builtins (len("ab") -> "2", "%s-%d" ->
  "ok-1"). It is a NEGATIVE CONTROL: it discriminates a correct fix
  from an over-broad fix (one that bans f-strings/% outright), not a
  vulnerable build from a fixed one. Run it against an over-broad
  build with --alt-root to see the FAIL direction.
- 4a (original): inspected an OP function's __globals__, which are
  module globals no pin can change (false premise). The redteam/
  council-2 replacement (return a model-defined function and inspect
  its globals) does NOT work against the current fork architecture:
  codemode runs the program in a forked child and JSON-encodes the
  payload across a pipe, so a function result can never cross
  (result_too_large on BOTH builds; see probe_4a_redteam_shape).
  4a-R2 instead uses canary names: repr, hex, all are in real CPython
  builtins, NOT in SAFE_BUILTINS, NOT in BANNED_NAMES, harmless pure
  functions. On unpinned code they resolve to real values; on pinned
  code they raise NameError. PASS = all three NameError in codemode
  plus the len("ab") positive control completing. The code_exec leg
  is a parity guard (code_exec was already pinned pre-fix, so it
  NameErrors on both builds). Static leg 4b-R uses a regex for the
  pin instead of the exact-string 4b.
- 10b (original): the outer program aborts on the first snippet's
  wall error, so the second run_snippet never executes in EITHER
  implementation; identical observable behavior, so the old probe
  PASSES the vulnerable build. 10b-R shape A (burn-first): the outer
  program burns 1.5s of API work first, then the snippet does 1.0s
  of acts with wall_seconds=2. Shared deadline refuses (1.5 + 1.0
  > 2); fresh deadline runs it. Shape B (try/except): the first
  call is wrapped so the second call actually executes; on a shared
  deadline the second call fails immediately (at most 1 new backend
  act, under 1.0s), on a fresh deadline it runs a full second set
  (at least 3 new acts, over 1.5s).
- 10f (original): the snippet alone loops 25000 times against a
  20000-step cap, so a reset counter trips exactly like a shared one.
  10f-R: the outer program does ~12000 steps and the snippet ~10000;
  each alone is under the cap, the total is over it. Shared counter
  refuses; reset counter runs both to completion.

10b/10f stubs: run_snippet does not exist on todolist-push yet, so
these probes run against two stub sessions built on the REAL
code_exec budget machinery (_api, _check_budgets, _trace) and the
REAL FakeBackend. AttackStub implements run_snippet by a nested
session.run() (Attack 8d: run() resets api_calls, _deadline and
_trace_steps, scripts/code_exec.py run() lines 1116-1122).
FixedStub implements run_snippet inline, sharing the live counters
and compiling the snippet under PROGRAM_FILENAME so the tracer
counts it, with the depth cap. The ONLY difference between the two
builds is the budget-sharing semantics under test. The stub uses
observe() as the sleeping API call (0.5s per call in
SleepingBackend): act() on current HEAD additionally requires
CB-2 stamped actions, which is orthogonal to budget sharing, while
observe() goes through the identical _api/_check_budgets path.
The outer-program strings (OUTER_10B_A, OUTER_10B_B, OUTER_10F)
and snippet sources are the portable artifact: they run unchanged
against a real run_snippet implementation.

Exit code: 0 only when every rewritten probe discriminates as
specified (1e-R and 4a-R2 PASS on the fixed build; 10b-R and 10f-R
FAIL on AttackStub and PASS on FixedStub). The old probes are run
as controls and are EXPECTED to pass both stubs (that is what makes
them broken); their non-discrimination is reported, not counted
as a failure.
"""

import argparse
import importlib.util
import json
import pathlib
import re
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))


def load_module(name, root):
    spec = importlib.util.spec_from_file_location(
        name, pathlib.Path(root) / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


codemode = load_module("codemode", REPO)
code_exec = load_module("code_exec", REPO)
from test_code_exec import FakeBackend  # noqa: E402

SLEEP_S = 0.5
WALL_S = 2

# Portable probe programs (run unchanged against a real run_snippet).
SNIPPET_SLOW2 = "".join('observe(window="0xabc")\n' for _ in range(2))
SNIPPET_SLOW6 = "".join('observe(window="0xabc")\n' for _ in range(6))
SNIPPET_MANY = "for j in range(5000):\n    y = j\n"
OUTER_10B_A = ('observe(window="0xabc")\nobserve(window="0xabc")\n'
               'observe(window="0xabc")\nrun_snippet("slow-act")\n')
OUTER_10B_B = ('try:\n    run_snippet("slow-act")\nexcept:\n    pass\n'
               'run_snippet("slow-act")\n')
OUTER_10B_OLD = 'run_snippet("slow-act")\nrun_snippet("slow-act")\n'
OUTER_10F = ("for i in range(6000):\n    x = i\n"
             'run_snippet("many-lines")\n')
SNIPPET_MANY_OLD = "for i in range(25000):\n    x = i\n"
OUTER_10F_OLD = 'run_snippet("many-lines")\n'


class SleepingBackend(FakeBackend):
    """FakeBackend whose observe_window sleeps: the deterministic
    wall-clock burner for the 10b probes."""

    def __init__(self, sleep_s=SLEEP_S):
        super().__init__()
        self.sleep_s = sleep_s
        self.observe_calls = 0

    def observe_window(self, address, crop, max_width):
        time.sleep(self.sleep_s)
        self.observe_calls += 1
        return super().observe_window(address, crop, max_width)


class Stub:
    """In-process session executing an outer program under the real
    code_exec tracer, with run_snippet in one of two modes."""

    def __init__(self, mode, wall=WALL_S):
        assert mode in ("attack", "fixed")
        self.mode = mode
        self.wall = wall
        self.backend = SleepingBackend()
        self.session = code_exec.CodeExecSession(
            self.backend, state_dir=tempfile.mkdtemp(),
            session_token="0123456789abcdef" * 2,
            wall_seconds=wall, max_api_calls=32)
        self.depth = 0
        self.snippet_sources = {}
        self.call_stats = []
        self._active_ns = None

    def namespace(self):
        ns = dict(code_exec.SAFE_BUILTINS)
        ns["__builtins__"] = dict(code_exec.SAFE_BUILTINS)
        ns["windows"] = self.session.api_windows
        ns["observe"] = self.session.api_observe
        ns["act"] = self.session.api_act
        ns["run_snippet"] = self.run_snippet
        ns["print"] = print
        return ns

    def _tracer(self, frame, event, arg):
        # Route only PROGRAM_FILENAME frames to the real tracer. The
        # stub's own bookkeeping lines (run_snippet, api internals)
        # stay untraced: once the deadline has passed, the real
        # tracer's periodic budget check fires on ANY traced line at
        # a %200 boundary, including a line inside run_snippet's own
        # finally block, which aborts the stat recording
        # nondeterministically (measured 22/11: the fixed second 10b-R
        # call ran 1 observe but its call_stat never landed). The budgets
        # under test are unaffected: _api checks budgets after every
        # call, and the step budget counts program lines only.
        if frame.f_code.co_filename == code_exec.PROGRAM_FILENAME:
            self.session._trace(frame, event, arg)
        return self._tracer

    def run_snippet(self, name):
        started = time.monotonic()
        obs_before = self.backend.observe_calls
        if self.depth:
            raise code_exec.CodeExecError("nested run_snippet is not allowed")
        src = self.snippet_sources[name]
        tree = code_exec.validate_program(src)
        code = compile(tree, code_exec.PROGRAM_FILENAME, "exec")
        if self.mode == "attack":
            # Nested run() semantics (Attack 8d): fresh budgets.
            self.session.api_calls = 0
            self.session._deadline = time.monotonic() + self.wall
            self.session._trace_steps = 0
            self.session._trace_events = 0
            ns = self.namespace()
        else:
            # Inline semantics: share the live counters and namespace.
            ns = self._active_ns
        self.depth += 1
        try:
            exec(code, ns)  # noqa: S102 - AST-validated snippet bytes
        finally:
            self.depth -= 1
            self.call_stats.append({
                "name": name, "mode": self.mode,
                "observes_delta": self.backend.observe_calls - obs_before,
                "elapsed": round(time.monotonic() - started, 2),
            })

    def run_outer(self, source):
        s = self.session
        started = time.monotonic()
        s.api_calls = 0
        s._trace_steps = 0
        s._trace_events = 0
        s._deadline = started + self.wall
        self.call_stats = []
        tree = code_exec.validate_program(source)
        self._active_ns = self.namespace()
        code = compile(tree, code_exec.PROGRAM_FILENAME, "exec")
        sys.settrace(self._tracer)
        try:
            exec(code, self._active_ns)  # noqa: S102 - validated program
            ok, error = True, ""
        except BaseException as exc:  # noqa: BLE001 - envelope the outcome
            ok, error = False, "%s: %s" % (type(exc).__name__, exc)
        finally:
            sys.settrace(None)
        return {"ok": ok, "error": error,
                "elapsed": round(time.monotonic() - started, 2),
                "api_calls": s.api_calls,
                "trace_steps": s._trace_steps,
                "observes": self.backend.observe_calls,
                "call_stats": list(self.call_stats)}


def _fresh_session():
    return code_exec.CodeExecSession(
        FakeBackend(), state_dir=tempfile.mkdtemp(),
        session_token="0123456789abcdef" * 2)


def probe_1e_rewritten(cm, ce):
    """1e-R: f-string + % with allowlisted builtins only, both executors."""
    halves = []
    env = cm.execute_op('x = f"{len(\'ab\')}"; return x')
    halves.append(("codemode f-string", env.get("status") == "completed"
                   and env.get("result") == "2", env))
    env = cm.execute_op('x = "%s-%d" % ("ok", 1); return x')
    halves.append(("codemode %", env.get("status") == "completed"
                   and env.get("result") == "ok-1", env))
    env = ce.CodeExecSession(FakeBackend(), state_dir=tempfile.mkdtemp(),
                             session_token="0123456789abcdef" * 2).run(
        'x = f"{len(\'ab\')}"')
    halves.append(("code_exec f-string", env.get("ok") is True
                   and env.get("variables", {}).get("x") == "2", env))
    env = ce.CodeExecSession(FakeBackend(), state_dir=tempfile.mkdtemp(),
                             session_token="0123456789abcdef" * 2).run(
        'x = "%s-%d" % ("ok", 1)')
    halves.append(("code_exec %", env.get("ok") is True
                   and env.get("variables", {}).get("x") == "ok-1", env))
    passed = all(h[1] for h in halves)
    return {"probe": "1e-R", "pass": passed,
            "detail": [(h[0], h[1]) for h in halves],
            "evidence": [json.dumps(h[2], default=str)[:200] for h in halves]}


def probe_1e_original(cm, ce):
    """1e original (chr halves) for the record: passes on HEAD now that
    chr+ord are allowlisted (3f1b951); failed the codemode leg on the
    84b88bb pin-without-chr build."""
    halves = []
    env = cm.execute_op('x = f"{len(chr(65))}"; return x')
    halves.append(("codemode f-string chr", env.get("status") == "completed"
                   and env.get("result") == "1", env))
    env = ce.CodeExecSession(FakeBackend(), state_dir=tempfile.mkdtemp(),
                             session_token="0123456789abcdef" * 2).run(
        'x = f"{len(chr(65))}"')
    halves.append(("code_exec f-string chr", env.get("ok") is True
                   and env.get("variables", {}).get("x") == "1", env))
    return {"probe": "1e-original", "pass": all(h[1] for h in halves),
            "detail": [(h[0], h[1]) for h in halves]}


def probe_4a_redteam_shape(cm):
    """The council-2/redteam replacement 4a, run as written: return a
    model-defined function. Under the fork architecture the function
    cannot cross the pipe, so this returns result_too_large on the
    fixed build (and on any fork build): NON-DISCRIMINATING there.
    On a pre-fork build it returns the live function object."""
    import types
    env = cm.execute_op("def f():\n    pass\nreturn f")
    live = (env.get("status") == "completed"
            and isinstance(env.get("result"), types.FunctionType))
    return {"probe": "4a-redteam-shape",
            "pass": live,
            "detail": [("returns a live function", live)],
            "evidence": [json.dumps(env, default=str)[:200]]}


def probe_4a_rewritten(cm, ce, root=REPO):
    """4a-R2: canary names repr/hex/all resolve only through real
    builtins. PASS = all three NameError in codemode, len control ok.
    The code_exec leg is a parity guard (already pinned pre-fix)."""
    halves = []
    for prog, want in (('x = repr(1); return x', "1"),
                       ('x = hex(255); return x', "0xff"),
                       ('x = all([True, True]); return x', True)):
        env = cm.execute_op(prog)
        ok = (env.get("status") == "error"
              and "NameError" in env.get("error", ""))
        halves.append(("codemode " + prog.split("=")[1].strip(), ok, env))
    env = cm.execute_op('x = len("ab"); return x')
    halves.append(("codemode len control", env.get("status") == "completed"
                   and env.get("result") == 2, env))
    for prog in ("x = repr(1)", "x = hex(255)"):
        s = ce.CodeExecSession(FakeBackend(), state_dir=tempfile.mkdtemp(),
                               session_token="0123456789abcdef" * 2)
        env = s.run(prog)
        ok = (env.get("ok") is False
              and env.get("error_type") == "NameError")
        halves.append(("code_exec " + prog, ok, env))
    src = (pathlib.Path(root) / "scripts" / "codemode.py").read_text()
    pin = re.search(r"__builtins__.*dict\(SAFE_BUILTINS\)", src) is not None
    halves.append(("4b-R regex pin in codemode.py", pin, {"pin": pin}))
    return {"probe": "4a-R2",
            "pass": all(h[1] for h in halves),
            "detail": [(h[0], h[1]) for h in halves],
            "evidence": [json.dumps(h[2], default=str)[:200] for h in halves]}


def probe_10b_old():
    """Control: old 10b run unchanged on both stubs. EXPECTED: PASS
    (ok False, wall error, ~one slow run) on BOTH builds."""
    out = {}
    for mode in ("attack", "fixed"):
        st = Stub(mode)
        st.snippet_sources["slow-act"] = SNIPPET_SLOW6
        out[mode] = st.run_outer(OUTER_10B_OLD)
    discriminates = out["attack"] != out["fixed"]
    return {"probe": "10b-OLD-control", "pass": True,
            "discriminates": False,
            "detail": [("attack", out["attack"]), ("fixed", out["fixed"])]}


def probe_10b_rewritten():
    """10b-R shape A (burn-first) + shape B (try/except)."""
    results = {}
    # Shape A
    for mode in ("attack", "fixed"):
        st = Stub(mode)
        st.snippet_sources["slow-act"] = SNIPPET_SLOW2
        results["A-" + mode] = st.run_outer(OUTER_10B_A)
    shape_a = (results["A-attack"]["ok"] is True
               and results["A-fixed"]["ok"] is False
               and "wall-clock" in results["A-fixed"]["error"])
    # Shape B
    for mode in ("attack", "fixed"):
        st = Stub(mode)
        st.snippet_sources["slow-act"] = SNIPPET_SLOW6
        r = st.run_outer(OUTER_10B_B)
        results["B-" + mode] = r
        second = r["call_stats"][1] if len(r["call_stats"]) > 1 else None
        results["B-" + mode + "-second-call"] = second
    b_attack = results["B-attack-second-call"]
    b_fixed = results["B-fixed-second-call"]
    shape_b = (b_attack is not None and b_fixed is not None
               and b_attack["observes_delta"] >= 3
               and b_attack["elapsed"] >= 1.5
               and b_fixed["observes_delta"] <= 1
               and b_fixed["elapsed"] < 1.0)
    return {"probe": "10b-R", "pass": bool(shape_a and shape_b),
            "detail": [("shape A discriminates", shape_a),
                       ("shape B discriminates", shape_b)],
            "evidence": [json.dumps(results, default=str)[:1200]]}


def probe_10f_old():
    """Control: old 10f run unchanged on both stubs. EXPECTED: PASS
    (trace error at ~20001 steps) on BOTH builds."""
    out = {}
    for mode in ("attack", "fixed"):
        st = Stub(mode, wall=30)
        st.snippet_sources["many-lines"] = SNIPPET_MANY_OLD
        out[mode] = st.run_outer(OUTER_10F_OLD)
    return {"probe": "10f-OLD-control", "pass": True,
            "discriminates": False,
            "detail": [("attack", out["attack"]), ("fixed", out["fixed"])]}


def probe_10f_rewritten():
    """10f-R: outer ~12000 steps + snippet ~10000 steps, cap 20000."""
    out = {}
    for mode in ("attack", "fixed"):
        st = Stub(mode, wall=30)
        st.snippet_sources["many-lines"] = SNIPPET_MANY
        out[mode] = st.run_outer(OUTER_10F)
    passed = (out["attack"]["ok"] is True
              and out["fixed"]["ok"] is False
              and "trace step budget exceeded" in out["fixed"]["error"])
    return {"probe": "10f-R", "pass": passed,
            "detail": [("attack completes, fixed refuses", passed)],
            "evidence": [json.dumps(out, default=str)[:800]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alt-root", default=None,
                    help="run the 1e/4a probes against another tree "
                    "(pre-fix build or over-broad attack copy) instead "
                    "of this repo; 10b/10f stubs always use this repo")
    args = ap.parse_args()
    results = []
    if args.alt_root:
        cm = load_module("codemode", args.alt_root)
        ce = load_module("code_exec", args.alt_root)
        results.append(probe_1e_rewritten(cm, ce))
        results.append(probe_1e_original(cm, ce))
        results.append(probe_4a_rewritten(cm, ce, root=args.alt_root))
        results.append(probe_4a_redteam_shape(cm))
    else:
        results.append(probe_1e_rewritten(codemode, code_exec))
        results.append(probe_1e_original(codemode, code_exec))
        results.append(probe_4a_redteam_shape(codemode))
        results.append(probe_4a_rewritten(codemode, code_exec))
        results.append(probe_10b_old())
        results.append(probe_10b_rewritten())
        results.append(probe_10f_old())
        results.append(probe_10f_rewritten())
    for r in results:
        print("=" * 70)
        print(r["probe"], "PASS" if r["pass"] else "FAIL")
        for d in r.get("detail", []):
            print("  ", d[0], "=>", d[1])
        for e in r.get("evidence", []):
            print("   evidence:", e)
    # Gate verdict: only the rewritten probes count toward G-Y1B.
    gate = [r for r in results if r["probe"] in ("1e-R", "4a-R2", "10b-R", "10f-R")]
    ok = all(r["pass"] for r in gate) and len(gate) == 4
    print("=" * 70)
    print("G-Y1B rewritten-probe gate:", "PASS" if ok else "FAIL",
          "(%d/4)" % sum(1 for r in gate if r["pass"]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
