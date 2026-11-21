#!/usr/bin/env python3
"""Search and describe over all repo scripts (Code Mode, missing piece 1).

Cloudflare Code Mode exposes search() and describe() so the model finds
the operation it needs without loading the whole API catalog into
context. This module does the same for the scripts in scripts/: the
model calls search_ops(query) to get ranked short descriptions, then
describe_op(name) for one script only. A whole file is never returned.

Registry: every .py, .mjs and .sh file directly under scripts/ is one
op, scanned live at import, so the count moves as scripts are added.
The description is the first docstring paragraph (Python) or the first
comment lines (JS and shell), capped at 200 chars. describe_op adds the
top-level entry point names and the first 6 non-empty lines, capped at
800 chars. Total describe output is capped at 2000 chars.

Token numbers in this file are estimates: characters divided by 4,
labeled as estimates, same proxy Worker N used in
docs/research/2026-11-21-code-mode-integration.md.

Snippets: list_snippets() and get_snippet(name) read
snippets/registry.json, the Pick 1 template programs (P1-P4).
"""

import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SNIPPETS_FILE = REPO_ROOT / "snippets" / "registry.json"

SCRIPT_SUFFIXES = {".py", ".mjs", ".sh"}
MAX_DESCRIPTION_CHARS = 200
MAX_HEAD_CHARS = 800
MAX_DESCRIBE_CHARS = 2000
MAX_ENTRY_POINTS = 20
MAX_SEARCH_RESULTS = 10

# Words that add a tag when they appear in a filename or description.
KEYWORD_TAGS = (
    "zen", "dom", "bidi", "marionette", "session", "overlay", "browser",
    "chromium", "cdp", "polygon", "codeforces", "timing", "visual",
    "screenshot", "a11y", "cursor", "glass", "indicator", "drive",
    "git", "test", "check", "task", "plan", "plugin", "vscode", "mcp",
    "cancel", "watchdog", "cleanup", "sync", "calibration",
)


class CodemodeSearchError(ValueError):
    """Unknown op name, bad query, or unreadable registry."""


def estimate_tokens(text):
    """Rough token estimate: characters divided by 4. Labeled estimate."""
    return len(text) / 4.0


def _first_paragraph(text):
    """First paragraph of a docstring or comment block, one line."""
    lines = [line.strip() for line in text.splitlines()]
    out = []
    for line in lines:
        if not line:
            if out:
                break
            continue
        out.append(line)
    return " ".join(out)


def _py_description(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree)
    return _first_paragraph(doc) if doc else ""


def _comment_description(path):
    """First // or # comment lines of a JS or shell script."""
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            lines.append(stripped[2:].strip())
        elif stripped.startswith("#") and not stripped.startswith("#!"):
            lines.append(stripped[1:].strip())
        elif lines:
            break
    return _first_paragraph("\n".join(lines))


def _entry_points(path):
    """Top-level function and class names, capped. Python only for now."""
    if path.suffix != ".py":
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            names.append(node.name)
        if len(names) >= MAX_ENTRY_POINTS:
            break
    return names


def _head_lines(path):
    """First 6 non-empty lines, each truncated, total capped."""
    lines = []
    total = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) > 160:
            stripped = stripped[:157] + "..."
        if total + len(stripped) > MAX_HEAD_CHARS:
            break
        lines.append(stripped)
        total += len(stripped)
        if len(lines) >= 6:
            break
    return lines


def _tags(name, description):
    hay = (name + " " + description).lower()
    tags = set(re.split(r"[-_]", name.lower()))
    tags.discard("")
    for word in KEYWORD_TAGS:
        if word in hay:
            tags.add(word)
    return sorted(tags)


def build_registry(scripts_dir=SCRIPTS_DIR):
    """Scan scripts/ and return a list of op dicts, one per script file."""
    ops = []
    for path in sorted(scripts_dir.iterdir()):
        if not path.is_file() or path.suffix not in SCRIPT_SUFFIXES:
            continue
        if path.suffix == ".py":
            description = _py_description(path)
        else:
            description = _comment_description(path)
        if not description:
            description = "No description in file head."
        description = description[:MAX_DESCRIPTION_CHARS]
        stem = path.stem
        ops.append({
            "name": stem,
            "file": path.name,
            "bytes": path.stat().st_size,
            "description": description,
            "tags": _tags(stem, description),
        })
    return ops


REGISTRY = build_registry()
_OP_BY_NAME = {op["name"]: op for op in REGISTRY}


def search_ops(query, limit=MAX_SEARCH_RESULTS):
    """Rank ops by whole-word match. Returns short descriptions, never files.

    Empty query returns ops sorted by name, up to limit. Each result has
    name, file, description, tags and score only. A query word scores 3
    for an exact op name, 2 for a whole word in the op name, and 1 for
    a whole tag or a whole word in the description. Partial substrings
    never match.
    """
    if not isinstance(query, str):
        raise CodemodeSearchError("query must be a string")
    words = [w for w in query.lower().split() if w]
    scored = []
    for op in REGISTRY:
        if not words:
            scored.append({"name": op["name"], "file": op["file"],
                           "description": op["description"],
                           "tags": op["tags"], "score": 0})
            continue
        name = op["name"].lower()
        name_parts = set(re.split(r"[-_]", name)) - {""}
        tags = set(op["tags"])
        desc_words = set(re.split(r"[^a-z0-9_]+",
                                  op["description"].lower())) - {""}
        score = 0
        for word in words:
            if word == name:
                score += 3
            elif word in name_parts:
                score += 2
            elif word in tags or word in desc_words:
                score += 1
        if score == 0:
            continue
        scored.append({"name": op["name"], "file": op["file"],
                       "description": op["description"],
                       "tags": op["tags"], "score": score})
    if words:
        scored.sort(key=lambda item: (-item["score"], item["name"]))
    else:
        scored.sort(key=lambda item: item["name"])
    return {"total": len(scored), "results": scored[:limit]}


def _cap_describe(result):
    """Trim a describe result until its JSON form fits the cap.

    Sheds head lines, then entry points, then tags, then description
    text, in that order. Always terminates: each description cut
    strictly shortens it. The only way the result could still exceed
    the cap after everything is shed is a script name or file name
    near 2000 chars long, which cannot exist (filesystem names are
    capped at 255 bytes).
    """
    def size():
        return len(json.dumps(result, ensure_ascii=False))
    while size() > MAX_DESCRIBE_CHARS and result["head"]:
        result["head"] = result["head"][:-1]
    while size() > MAX_DESCRIBE_CHARS and result["entry_points"]:
        result["entry_points"] = result["entry_points"][:-1]
    while size() > MAX_DESCRIBE_CHARS and result["tags"]:
        result["tags"] = result["tags"][:-1]
    while size() > MAX_DESCRIBE_CHARS:
        desc = result["description"]
        if len(desc) <= 3:
            break
        over = size() - MAX_DESCRIBE_CHARS
        keep = max(0, len(desc) - over - 3)
        result["description"] = desc[:keep] + "..."
    return result


def describe_op(name):
    """Short typed info for one op. Never returns a whole file.

    Returns name, file, size, description, top-level entry point names
    and the first 6 non-empty lines. Total output never exceeds 2000
    chars: _cap_describe enforces it by trimming head, entry points,
    tags, then description.
    """
    op = _OP_BY_NAME.get(name)
    if op is None:
        raise CodemodeSearchError("unknown op: %s" % name)
    path = SCRIPTS_DIR / op["file"]
    result = {
        "name": op["name"],
        "file": op["file"],
        "bytes": op["bytes"],
        "description": op["description"],
        "tags": op["tags"],
        "entry_points": _entry_points(path),
        "head": _head_lines(path),
    }
    return _cap_describe(result)


def catalog_before_text():
    """Full-catalog proxy: first 3 lines of every script, as one text."""
    chunks = []
    for op in REGISTRY:
        path = SCRIPTS_DIR / op["file"]
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        chunks.append(op["file"] + "\n" + "\n".join(lines[:3]))
    return "\n".join(chunks)


def measure_tokens(query, limit=5):
    """Before/after token estimates (chars/4) for one query.

    Before: the whole catalog, first 3 lines per script. After: the
    search results for the query, capped at limit. Both are estimates.
    """
    before = catalog_before_text()
    after = json.dumps(search_ops(query, limit=limit), ensure_ascii=False)
    return {
        "query": query,
        "before_chars": len(before),
        "before_tokens_estimate": round(estimate_tokens(before), 1),
        "after_chars": len(after),
        "after_tokens_estimate": round(estimate_tokens(after), 1),
        "saved_tokens_estimate": round(
            estimate_tokens(before) - estimate_tokens(after), 1),
    }


def _load_snippets():
    """Read snippets/registry.json.

    A corrupt file (bad JSON, or valid JSON with the wrong shape)
    raises CodemodeSearchError with a clear message instead of a raw
    JSONDecodeError or KeyError. The CLI catches CodemodeSearchError
    and prints it as a JSON error with exit 1.
    """
    try:
        data = json.loads(SNIPPETS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CodemodeSearchError(
            "snippets registry is corrupt: %s: %s" % (SNIPPETS_FILE, exc))
    if not isinstance(data, dict) or not isinstance(data.get("snippets"),
                                                    list):
        raise CodemodeSearchError(
            "snippets registry is corrupt: %s: expected "
            "{\"snippets\": [...]}" % SNIPPETS_FILE)
    return data["snippets"]


def list_snippets():
    """Short list of the snippets registry: name, title, description."""
    return [{"name": item["name"], "title": item["title"],
             "description": item["description"]}
            for item in _load_snippets()]


def get_snippet(name):
    """One snippet: description, program, input, sample output."""
    for item in _load_snippets():
        if item["name"] == name:
            return item
    raise CodemodeSearchError("unknown snippet: %s" % name)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="Search and describe repo scripts (Code Mode)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=MAX_SEARCH_RESULTS)
    describe = sub.add_parser("describe")
    describe.add_argument("name")
    tokens = sub.add_parser("tokens")
    tokens.add_argument("query")
    tokens.add_argument("--limit", type=int, default=5)
    sub.add_parser("list")
    snippet = sub.add_parser("snippet")
    snippet.add_argument("name")
    args = parser.parse_args(argv)
    if args.cmd == "search":
        print(json.dumps(search_ops(args.query, args.limit), indent=2,
                         ensure_ascii=False))
    elif args.cmd == "describe":
        try:
            print(json.dumps(describe_op(args.name), indent=2,
                             ensure_ascii=False))
        except CodemodeSearchError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}))
            raise SystemExit(1)
    elif args.cmd == "tokens":
        print(json.dumps(measure_tokens(args.query, args.limit), indent=2))
    elif args.cmd == "list":
        print(json.dumps({"total": len(REGISTRY), "ops": [
            {"name": op["name"], "file": op["file"]} for op in REGISTRY]},
            indent=2))
    elif args.cmd == "snippet":
        try:
            print(json.dumps(get_snippet(args.name), indent=2,
                             ensure_ascii=False))
        except CodemodeSearchError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}))
            raise SystemExit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
