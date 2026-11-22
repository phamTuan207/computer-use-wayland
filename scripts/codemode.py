"""Minimal Code Mode interface for computer-use-wayland (prototype).

Pattern copied from Cloudflare Code Mode (blog 2026-02-20, SDK in
cloudflare/agents packages/codemode) and adapted to this repo:

- The model sees only TWO functions: search_ops(query) and execute_op(code).
- search_ops returns ranked op paths plus one-line descriptions, never full
  schemas. describe_op(path) returns the full typed signature of one op.
- execute_op runs model-written Python against a registry of typed repo
  operations. The code runs under the same safety shape as
  scripts/code_exec.py: AST scan rejects imports, dunder access, eval,
  exec, open, __import__ and attribute access outside a safe whitelist;
  restricted builtins; a wall-clock budget and a trace step budget.
- Ops that need the laptop are registered with laptop_only=True. On the VM
  their execution returns a requires_laptop envelope instead of touching
  the laptop. This prototype never touches the laptop or the user's Zen.

This is a prototype for evaluation, not production code. It does not
replace scripts/code_exec.py, which is the live client-side Code Mode
equivalent in this repo (Track 2, Pick 1, merged).
"""

import ast
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_PROGRAM_CHARS = 8192
DEFAULT_WALL_SECONDS = 30
MAX_WALL_SECONDS = 60
MAX_TRACE_STEPS = 20000
MAX_READ_BYTES = 65536
MAX_ENVELOPE_BYTES = 65536

SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "len": len, "str": str, "int": int, "float": float, "bool": bool,
    "list": list, "dict": dict, "set": set, "tuple": tuple,
    "range": range, "enumerate": enumerate, "zip": zip,
    "min": min, "max": max, "sum": sum, "abs": abs,
    "sorted": sorted, "reversed": reversed, "isinstance": isinstance,
    "round": round, "chr": chr, "ord": ord,
}
SAFE_ATTRIBUTE_NAMES = {
    "get", "keys", "values", "items",
    "startswith", "endswith", "strip", "split", "join", "lower", "upper",
    "replace", "count", "find", "index",
    "append", "extend", "pop", "remove",
}
BANNED_NAMES = {
    "__import__", "eval", "exec", "compile", "open", "input", "globals",
    "locals", "vars", "getattr", "setattr", "delattr", "hasattr",
    "breakpoint", "memoryview", "object", "type", "help", "dir",
    "os", "sys", "subprocess", "socket", "pathlib", "shutil", "time",
    "json", "re", "io", "importlib", "builtins", "__builtins__",
}


class CodemodeError(Exception):
    """A rejected program or a failed op, returned as an envelope."""


# ---------------------------------------------------------------- ops
def _op_list_scripts(pattern=""):
    """List repo scripts whose filename contains pattern (case-insensitive)."""
    out = []
    for path in sorted((REPO_ROOT / "scripts").glob("*")):
        if not path.is_file():
            continue
        if pattern and pattern.lower() not in path.name.lower():
            continue
        out.append({"name": path.name, "bytes": path.stat().st_size})
    return {"count": len(out), "scripts": out}


def _op_script_info(name):
    """First docstring lines plus size of one repo script."""
    path = REPO_ROOT / "scripts" / name
    if not path.is_file():
        raise CodemodeError("no such script: %s" % name)
    text = path.read_text(errors="replace")
    lines = [line.strip() for line in text.splitlines()[:12] if line.strip()]
    return {"name": name, "bytes": path.stat().st_size,
            "head": lines[:6]}


def _op_py_compile(name):
    """Compile-check one repo script with py_compile, timed."""
    import py_compile
    import tempfile
    path = REPO_ROOT / "scripts" / name
    if not path.is_file() or path.suffix != ".py":
        raise CodemodeError("not a python script: %s" % name)
    started = time.monotonic()
    with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as tmp:
        py_compile.compile(str(path), doraise=True, cfile=tmp.name)
    return {"name": name, "ok": True,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1)}


def _op_read_file(path, max_bytes=MAX_READ_BYTES):
    """Read a file under the repo root or /tmp, size-capped."""
    target = Path(path)
    if not target.is_absolute():
        target = REPO_ROOT / target
    resolved = target.resolve()
    allowed = (REPO_ROOT.resolve(), Path("/tmp").resolve())
    if not any(str(resolved).startswith(str(root) + os.sep)
               or resolved == root for root in allowed):
        raise CodemodeError("path outside repo root and /tmp: %s" % path)
    if not resolved.is_file():
        raise CodemodeError("not a file: %s" % path)
    data = resolved.read_bytes()[:max_bytes]
    return {"path": str(resolved), "bytes": len(data),
            "text": data.decode("utf-8", errors="replace")}


def _op_zen_dom_locate(selector):
    """Locate one DOM element rect in the live Zen (LAPTOP ONLY)."""
    raise CodemodeError("requires_laptop")


def _op_overlay_status():
    """Read the overlay holder state (LAPTOP ONLY)."""
    raise CodemodeError("requires_laptop")


OPS = [
    {"path": "repo.list_scripts",
     "description": "List repo scripts, optionally filtered by filename pattern.",
     "params": {"pattern": "string, optional, substring match on filename"},
     "returns": "{count, scripts: [{name, bytes}]}",
     "fn": _op_list_scripts, "laptop_only": False, "requires_approval": False,
     "tags": ["repo", "scripts", "list", "inventory"]},
    {"path": "repo.script_info",
     "description": "First docstring lines plus size of one repo script.",
     "params": {"name": "string, filename under scripts/"},
     "returns": "{name, bytes, head}",
     "fn": _op_script_info, "laptop_only": False, "requires_approval": False,
     "tags": ["repo", "scripts", "docs", "info"]},
    {"path": "repo.py_compile",
     "description": "Compile-check one repo Python script, timed.",
     "params": {"name": "string, filename under scripts/"},
     "returns": "{name, ok, elapsed_ms}",
     "fn": _op_py_compile, "laptop_only": False, "requires_approval": False,
     "tags": ["repo", "scripts", "test", "compile", "timing"]},
    {"path": "repo.read_file",
     "description": "Read a file under the repo root or /tmp, size-capped.",
     "params": {"path": "string", "max_bytes": "int, optional"},
     "returns": "{path, bytes, text}",
     "fn": _op_read_file, "laptop_only": False, "requires_approval": False,
     "tags": ["repo", "file", "read"]},
    {"path": "zen.locate",
     "description": "Locate one DOM element rect in the live Zen via zen_dom.",
     "params": {"selector": "string, CSS selector"},
     "returns": "{rect, visible} (laptop only)",
     "fn": _op_zen_dom_locate, "laptop_only": True, "requires_approval": False,
     "tags": ["zen", "dom", "locate", "rect", "browser"]},
    {"path": "overlay.status",
     "description": "Read the overlay holder state.",
     "params": {},
     "returns": "{holders, visible} (laptop only)",
     "fn": _op_overlay_status, "laptop_only": True, "requires_approval": False,
     "tags": ["overlay", "pill", "status"]},
]

_OP_BY_PATH = {op["path"]: op for op in OPS}


# ---------------------------------------------------------------- search
def search_ops(query):
    """Rank op paths by keyword match. Returns paths + one-liners, no schemas."""
    words = [w for w in query.lower().split() if w]
    scored = []
    for op in OPS:
        hay = " ".join([op["path"], op["description"]] + op["tags"]).lower()
        score = sum(1 for w in words if w in hay)
        if words and score == 0:
            continue
        scored.append({"path": op["path"], "description": op["description"],
                       "laptop_only": op["laptop_only"], "score": score})
    scored.sort(key=lambda item: (-item["score"], item["path"]))
    return {"total": len(scored), "results": scored}


def describe_op(path):
    """Full typed signature of one op."""
    op = _OP_BY_PATH.get(path)
    if op is None:
        raise CodemodeError("unknown op: %s" % path)
    return {"path": op["path"], "description": op["description"],
            "params": op["params"], "returns": op["returns"],
            "laptop_only": op["laptop_only"],
            "requires_approval": op["requires_approval"]}


# ---------------------------------------------------------------- execute
def _scan(code):
    """Reject banned constructs before execution. Returns the parsed tree."""
    if len(code) > MAX_PROGRAM_CHARS:
        raise CodemodeError("program over %d chars" % MAX_PROGRAM_CHARS)
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise CodemodeError("syntax error: %s" % exc)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise CodemodeError("imports are banned")
        if isinstance(node, ast.Name):
            if node.id in BANNED_NAMES:
                raise CodemodeError("banned name: %s" % node.id)
            if node.id.startswith("__"):
                raise CodemodeError("dunder access is banned")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise CodemodeError("dunder attribute access is banned")
        if isinstance(node, ast.Attribute) \
                and node.attr not in SAFE_ATTRIBUTE_NAMES:
            raise CodemodeError("attribute not allowlisted: %s" % node.attr)
        if isinstance(node, (ast.Lambda, ast.AsyncFunctionDef, ast.AsyncFor,
                             ast.AsyncWith, ast.Await, ast.Yield,
                             ast.YieldFrom, ast.Global, ast.Nonlocal)):
            raise CodemodeError("lambda/async/yield/global are banned")
    return tree


def _serialized_size(value):
    try:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                              allow_nan=False).encode("utf-8"))
    except (TypeError, ValueError, OverflowError):
        return MAX_ENVELOPE_BYTES + 1


def _bounded_envelope(envelope, started):
    envelope["elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
    if _serialized_size(envelope) <= MAX_ENVELOPE_BYTES:
        return envelope
    return {"status": "error", "error": "serialized result envelope exceeds %d bytes" % MAX_ENVELOPE_BYTES,
            "error_type": "result_too_large",
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1)}


def _module_code(tree):
    """Keep legacy final return statements without a reachable wrapper function."""
    body = list(tree.body)
    if body and isinstance(body[-1], ast.Return):
        final_return = body[-1]
        body[-1] = ast.Assign(
            targets=[ast.Name(id="result", ctx=ast.Store())],
            value=final_return.value or ast.Constant(value=None))
    module = ast.Module(body=body or [ast.Expr(ast.Constant(value=None))],
                        type_ignores=[])
    ast.fix_missing_locations(module)
    return module


def execute_op(code, wall_seconds=DEFAULT_WALL_SECONDS):
    """Run model-written Python against the op registry. Returns an envelope.

    The code runs as one function body. Op functions are exposed as plain
    names derived from their paths (repo.list_scripts -> repo_list_scripts).
    Returns {status, result} or {status, error}. Laptop-only ops return a
    requires_laptop envelope on the VM instead of touching the laptop.
    """
    started = time.monotonic()
    wall_seconds = max(1, min(int(wall_seconds), MAX_WALL_SECONDS))
    deadline = started + wall_seconds
    try:
        tree = _scan(code)
    except CodemodeError as exc:
        return {"status": "error", "error": str(exc),
                "elapsed_ms": round((time.monotonic() - started) * 1000, 1)}

    namespace = dict(SAFE_BUILTINS)
    namespace["__builtins__"] = dict(SAFE_BUILTINS)
    namespace["print"] = lambda *args: None
    for op in OPS:
        namespace[op["path"].replace(".", "_")] = op["fn"]

    steps = [0]

    def tracer(frame, event, arg):
        # Only model code counts toward the step budget. Lines inside op
        # implementations do not count (same rule as scripts/code_exec.py),
        # otherwise a legit op like py_compile would exhaust the budget.
        if frame.f_code.co_filename == "<codemode>":
            steps[0] += 1
            if steps[0] > MAX_TRACE_STEPS:
                raise CodemodeError("trace step budget exceeded")
        if time.monotonic() > deadline:
            raise CodemodeError("wall-clock budget exceeded")
        return tracer

    old_tracer = sys.gettrace()
    sys.settrace(tracer)
    try:
        compiled = compile(_module_code(tree), "<codemode>", "exec")
        exec(compiled, namespace)  # noqa: S102 - scanned code only
        result = namespace.get("result")
    except CodemodeError as exc:
        message = str(exc)
        if message == "requires_laptop":
            return _bounded_envelope({"status": "requires_laptop",
                    "error": "op needs the laptop, not runnable on the VM"}, started)
        return _bounded_envelope({"status": "error", "error": message}, started)
    except Exception as exc:  # noqa: BLE001 - envelope the failure
        message = str(exc)
        return _bounded_envelope({"status": "error", "error": "%s: %s" % (type(exc).__name__, message)}, started)
    finally:
        sys.settrace(old_tracer)
    return _bounded_envelope({"status": "completed", "result": result,
                              "steps": steps[0]}, started)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Mode prototype CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    search = sub.add_parser("search")
    search.add_argument("query")
    describe = sub.add_parser("describe")
    describe.add_argument("path")
    execute = sub.add_parser("execute")
    execute.add_argument("code")
    execute.add_argument("--wall-seconds", type=int, default=DEFAULT_WALL_SECONDS)
    args = parser.parse_args()
    if args.cmd == "search":
        print(json.dumps(search_ops(args.query), indent=2))
    elif args.cmd == "describe":
        try:
            print(json.dumps(describe_op(args.path), indent=2))
        except CodemodeError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}))
            raise SystemExit(1)
    else:
        print(json.dumps(execute_op(args.code, args.wall_seconds), indent=2))


if __name__ == "__main__":
    main()
