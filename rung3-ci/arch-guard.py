#!/usr/bin/env python3
"""Architecture guard (agent-desktop comparison I13).

Two checks, both mechanical defences of project principles:

1. Import map: every local import in scripts/ (recursive,
   including subdirectories) must be listed in
   rung3-ci/import-map.txt. Static imports and string-literal
   dynamic loads (importlib.import_module, __import__,
   importlib.util.spec_from_file_location, runpy.run_path /
   run_module, and local loader helpers wrapping them) all
   count as edges. A file that does not parse is a violation
   (fail closed). A new dependency edge fails the guard until
   the map is updated in the same commit, making each new edge
   a deliberate decision. The map was generated from the graph
   at integration start (2026-11-27); it freezes the current
   graph, it does not bless it.

2. Machine values: a small denylist scanned over scripts/,
   skill/, docs/, .github/, tests/, skills/, native/ and the
   repo root files: personal name forms (any case, spaced or
   separator-joined; diacritic forms matched by hash,
   not by literal), real Firefox/Zen profile dir names
   (8-char hash + .Default), home-dir paths with a real
   username, and Tailscale-range addresses (the CGNAT range
   literal 100.64.0.0/10 in documentation is not a hit).
   Split string literals and values split across lines are
   caught by a normalized second pass. Files are decoded with
   errors="replace" so invalid UTF-8 cannot hide content.
   Historical records (improvements/, rung3-run-log/, coord/)
   and this directory (rung3-ci/, which holds the patterns
   themselves) are out of scope by design; test fixtures with
   fake values and frozen ship/bench records are allowlisted
   by path below, each with a stated reason.

Exit 1 on any violation. Python standard library only.
"""
import ast
import hashlib
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Denylist patterns. The personal-name forms live here (rung3-ci/
# is not itself scanned) so the guard can match them in the
# scanned trees. Diacritic forms are stored as hashes below,
# not as literals, so this file does not itself contain the name.
#
# Boundary decision (explicit): the public GitHub handle is NOT
# a denylist hit. It is the repo identity, used intentionally in
# the README clone URL, skill files and docs. The personal-name
# pattern therefore requires a separator between the first two
# name parts, or the full three-part name, so the handle (first
# part + second part + digits, no separator, no third part)
# never matches, while spaced, hyphenated, underscored and
# concatenated full-name forms do.
DENY_PATTERNS = [
    ("personal-name", re.compile(
        r"(?<![A-Za-z])pham[\s._-]+tuan(?![A-Za-z])"
        r"|(?<![A-Za-z])phamtuan[\s._-]*huy(?![A-Za-z])"
        r"|(?<![A-Za-z])tuan[\s._-]*huy(?![A-Za-z])",
        re.IGNORECASE)),
    ("profile-dir", re.compile(r"\b[a-z0-9]{8}\.Default\b")),
    # user/demo/testuser are placeholders and synthetic fixture
    # homes, not real usernames. Any other username is a hit,
    # with or without a trailing slash, in any case.
    ("home-path", re.compile(
        r"/home/(?!user\b|demo\b|testuser\b)[A-Za-z][A-Za-z0-9_-]*\b")),
    # A bare address in the Tailscale CGNAT range is a hit; the
    # range literal itself (100.64.0.0/10) in documentation is not.
    ("tailscale-ip", re.compile(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b(?!/10\b)")),
]
# Diacritic personal-name tokens, stored as SHA-256 digests (of
# the NFC, lowercased tokens) so the guard still detects the
# name without spelling it in this file. The literal was itself
# the leak.
_NAME_TOKEN_SHA256 = frozenset({
    "8ac0e9a490bb1da8b1afed99f7a95d81375ca5ee628112d06351bd4ec3c90809",
    "8dd48718607f71d250804bd446ebc8439077893b15897adc2fa5225851822d9e",
})


def _name_token_hit(text):
    """Return the matched 4-character name-token window, or None.

    Hashes every 4-character window of every letter run in the
    lowercased, NFC-normalized text and compares digests, so the
    guard detects the diacritic name forms without containing
    them.
    """
    text = unicodedata.normalize("NFC", text.lower())
    for run in re.findall(r"[^\W\d_]+", text, re.UNICODE):
        for i in range(len(run) - 3):
            window = run[i:i + 4]
            digest = hashlib.sha256(
                window.encode("utf-8")).hexdigest()
            if digest in _NAME_TOKEN_SHA256:
                return window
    return None


SCAN_DIRS = ["scripts", "skill", "docs", ".github", "tests",
             "skills", "native"]
# Paths (relative, prefix match) exempt from the machine-value
# scan, each with its reason:
ALLOW_PREFIXES = (
    "tests/fixtures/",   # fixtures use fake values by design
    "scripts/plans/",    # plan data, exempt by design
    # Frozen Y9 ship manifests: the VM checkout path is
    # historical provenance of a past ship, not live config.
    "SHIPPED-y9.md",
    "tests/realistic/SHIPPED.md",
    # Frozen bench manifest record: artifact paths describe a
    # past bench run; editing them would falsify the record.
    "deploy-manifest.json",
    # Frozen run output embedding the allowlisted ship record.
    "tests/realistic/live-run-y9-agy-y2-20261121.stdout.log",
)
TEXT_SUFFIXES = (".py", ".md", ".txt", ".json", ".sh", ".yml",
                 ".yaml", ".toml", ".mjs", ".js", ".lua", ".html",
                 ".css", ".c", ".h", ".cpp", ".hpp", ".jsonl",
                 ".patch", ".xml", ".service", ".hook", ".template",
                 ".svg", ".csv", ".conf", ".log")


def _is_text_name(name):
    _, ext = os.path.splitext(name)
    return ext in TEXT_SUFFIXES or ext == ""


def load_import_map(path):
    allowed = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            mod, _, rest = line.partition(":")
            allowed[mod.strip()] = {x.strip() for x in rest.split(",")
                                    if x.strip()}
    return allowed


def _module_index(scripts):
    modules = {}
    for dirpath, _dirs, files in os.walk(scripts):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(dirpath, f)
                key = os.path.relpath(path, scripts)[:-3]
                modules[key.replace(os.sep, "/")] = path
    return modules


def _func_name(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _strings_in(expr, consts):
    out = set()
    for node in ast.walk(expr):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.add(node.value)
        elif isinstance(node, ast.Name) and node.id in consts:
            out |= consts[node.id]
    return out


def _consts_in(body):
    """Simple Name -> string-constants map for one scope body."""
    consts = {}
    stack = list(body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            continue
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            vals = {c.value for c in ast.walk(node.value)
                    if isinstance(c, ast.Constant)
                    and isinstance(c.value, str)}
            if vals:
                consts.setdefault(node.targets[0].id, set()).update(vals)
        stack.extend(ast.iter_child_nodes(node))
    return consts


def _fname_to_key(value, modules, by_base):
    value = value.replace("\\", "/")
    base = value.rsplit("/", 1)[-1]
    keys = by_base.get(base, [])
    if len(keys) == 1:
        return keys[0]
    for key in modules:
        if value.endswith(key + ".py"):
            return key
    return None


def local_imports(path, key, modules, by_base):
    """Local dependency edges of one file: (deps, error).

    error is None on success; on read/parse failure deps is
    empty and error describes the failure (fail closed).
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
    except OSError as exc:
        return set(), f"unreadable ({exc})"
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return set(), f"unparseable (SyntaxError: {exc.msg})"

    importer_dir = key.rsplit("/", 1)[0] if "/" in key else ""

    def resolve_static(name):
        if importer_dir:
            cand = importer_dir + "/" + name
            if cand in modules:
                return cand
        if name in modules:
            return name
        return None

    helpers = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Call) and _func_name(sub) in
                        ("spec_from_file_location", "run_path",
                         "run_module")):
                    helpers.add(node.name)

    found = set()

    def visit(node, consts):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            local = dict(consts)
            local.update(_consts_in(node.body))
            for child in node.body:
                visit(child, local)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                dep = resolve_static(alias.name.split(".")[0])
                if dep:
                    found.add(dep)
            return
        if isinstance(node, ast.ImportFrom):
            if node.module:
                dep = resolve_static(node.module.split(".")[0])
                if dep:
                    found.add(dep)
            elif node.level:
                for alias in node.names:
                    dep = resolve_static(alias.name.split(".")[0])
                    if dep:
                        found.add(dep)
            return
        if isinstance(node, ast.Call):
            fname = _func_name(node)
            if fname in ("import_module", "__import__",
                         "run_module") and node.args:
                for val in _strings_in(node.args[0], consts):
                    dep = resolve_static(val.split(".")[0])
                    if dep:
                        found.add(dep)
            elif fname == "spec_from_file_location" and len(node.args) >= 2:
                for val in _strings_in(node.args[1], consts):
                    if val.endswith(".py"):
                        dep = _fname_to_key(val, modules, by_base)
                        if dep:
                            found.add(dep)
            elif fname == "run_path" and node.args:
                for val in _strings_in(node.args[0], consts):
                    if val.endswith(".py"):
                        dep = _fname_to_key(val, modules, by_base)
                        if dep:
                            found.add(dep)
            elif fname in helpers:
                for arg in node.args:
                    for val in _strings_in(arg, consts):
                        if val.endswith(".py"):
                            dep = _fname_to_key(val, modules, by_base)
                            if dep:
                                found.add(dep)
        for child in ast.iter_child_nodes(node):
            visit(child, consts)

    visit(tree, _consts_in(tree.body))
    found.discard(key)
    return found, None


def check_imports(root=ROOT, map_path=None):
    scripts = os.path.join(root, "scripts")
    modules = _module_index(scripts)
    by_base = {}
    for key, path in modules.items():
        by_base.setdefault(os.path.basename(path), []).append(key)
    allowed = load_import_map(map_path or os.path.join(
        HERE, "import-map.txt"))
    violations = []
    for key in sorted(modules):
        actual, error = local_imports(modules[key], key, modules,
                                      by_base)
        if error:
            violations.append(f"import: scripts/{key}.py: {error}")
            continue
        extra = actual - allowed.get(key, set())
        for dep in sorted(extra):
            violations.append(
                f"import: scripts/{key}.py imports {dep} "
                f"(not in import-map.txt)")
    return violations


def _normalized(text):
    """Join split string literals and collapse whitespace so
    values split across literals or lines match the patterns."""
    text = text.replace("\\\n", "")
    text = re.sub(r'["\']\s*\+\s*["\']', "", text)
    text = re.sub(r'["\']\s+["\']', "", text)
    return re.sub(r"\s+", " ", text)


def scan_machine_values(root=ROOT):
    violations = []
    targets = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        for dirpath, _dirs, files in os.walk(base):
            for f in files:
                if _is_text_name(f):
                    targets.append(os.path.join(dirpath, f))
    for f in sorted(os.listdir(root)):
        path = os.path.join(root, f)
        if f == ".git" or not os.path.isfile(path):
            continue
        if _is_text_name(f):
            targets.append(path)
    for path in sorted(set(targets)):
        rel = os.path.relpath(path, root)
        if rel.startswith(ALLOW_PREFIXES):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        seen = set()
        for i, line in enumerate(text.splitlines(), 1):
            line_personal = False
            for name, pat in DENY_PATTERNS:
                if pat.search(line):
                    violations.append(
                        f"machine-value: {rel}:{i}: {name}: "
                        f"{line.strip()[:80]}")
                    seen.add(name)
                    if name == "personal-name":
                        line_personal = True
            # The hash check runs on every line, like the regex
            # patterns above: the per-file `seen` set gates only
            # the split-form pass below. Skip it on a line the
            # regex already flagged, so a line still reports at
            # most one personal-name violation, as before.
            if not line_personal and _name_token_hit(line):
                violations.append(
                    f"machine-value: {rel}:{i}: personal-name: "
                    f"{line.strip()[:80]}")
                seen.add("personal-name")
        flat = _normalized(text)
        for name, pat in DENY_PATTERNS:
            if name in seen:
                continue
            match = pat.search(flat)
            if match:
                lo = max(0, match.start() - 20)
                snippet = flat[lo:match.end() + 20].strip()[:80]
                violations.append(
                    f"machine-value: {rel}:0: {name} "
                    f"(split form): {snippet}")
        if "personal-name" not in seen:
            hit = _name_token_hit(flat)
            if hit:
                idx = flat.lower().find(hit)
                if idx >= 0:
                    lo = max(0, idx - 20)
                    snippet = flat[lo:idx + 24].strip()[:80]
                else:
                    snippet = flat.strip()[:80]
                violations.append(
                    "machine-value: "
                    f"{rel}:0: personal-name (split form): "
                    f"{snippet}")
    return violations


def main(argv=None):
    violations = check_imports() + scan_machine_values()
    for v in violations:
        print(v)
    if violations:
        print(f"arch-guard FAIL: {len(violations)} violation(s)")
        return 1
    print("arch-guard PASS: import map holds, no machine values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
