#!/usr/bin/env python3
"""Architecture guard (agent-desktop comparison I13).

Two checks, both mechanical defences of project principles:

1. Import map: every local import in scripts/ must be listed in
   rung3-ci/import-map.txt. A new dependency edge fails the guard
   until the map is updated in the same commit, making each new
   edge a deliberate decision. The map was generated from the
   graph at integration start (2026-11-27); it freezes the
   current graph, it does not bless it.

2. Machine values: a small denylist scanned over scripts/,
   skill/, docs/ and README.md: personal name forms, real
   Firefox/Zen profile dir names (8-char hash + .Default),
   home-dir paths with a real username, and the owner's
   Tailscale address. Historical records (improvements/,
   rung3-run-log/, coord/) are out of scope by design; test
   fixtures with fake values are allowlisted by path below.

Exit 1 on any violation. Python standard library only.
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Denylist patterns. The personal-name forms live here (rung3-ci/
# is not itself scanned) so the guard can match them in the
# scanned trees.
DENY_PATTERNS = [
    ("personal-name", re.compile(r"Pham Tuan|Tuan Huy|Phạm|Tuấn")),
    ("profile-dir", re.compile(r"\b[a-z0-9]{8}\.Default\b")),
    ("home-path", re.compile(r"/home/(?!user\b)[a-z][a-z0-9_-]*/")),
    ("tailscale-ip", re.compile(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
]
SCAN_DIRS = ["scripts", "skill", "docs"]
SCAN_FILES = ["README.md"]
# Paths (relative, prefix match) exempt from the machine-value scan:
# fixtures use fake values by design.
ALLOW_PREFIXES = ("tests/fixtures/", "scripts/plans/")
TEXT_SUFFIXES = (".py", ".md", ".txt", ".json", ".sh", ".yml", ".yaml",
                 ".toml", ".mjs", ".js")


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


def local_imports(path, module_names):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except SyntaxError:
        return set()
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                found.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return {i for i in found if i in module_names}


def check_imports(root=ROOT, map_path=None):
    scripts = os.path.join(root, "scripts")
    modules = {f[:-3] for f in os.listdir(scripts) if f.endswith(".py")}
    allowed = load_import_map(map_path or os.path.join(
        HERE, "import-map.txt"))
    violations = []
    for mod in sorted(modules):
        actual = local_imports(os.path.join(scripts, mod + ".py"),
                               modules)
        extra = actual - allowed.get(mod, set())
        for dep in sorted(extra):
            violations.append(
                f"import: scripts/{mod}.py imports {dep} "
                f"(not in import-map.txt)")
    return violations


def scan_machine_values(root=ROOT):
    violations = []
    targets = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        for dirpath, _dirs, files in os.walk(base):
            for f in files:
                if f.endswith(TEXT_SUFFIXES):
                    targets.append(os.path.join(dirpath, f))
    targets += [os.path.join(root, f) for f in SCAN_FILES]
    for path in sorted(targets):
        rel = os.path.relpath(path, root)
        if rel.startswith(ALLOW_PREFIXES):
            continue
        try:
            text = open(path, encoding="utf-8", errors="strict").read()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for name, pat in DENY_PATTERNS:
                if pat.search(line):
                    violations.append(
                        f"machine-value: {rel}:{i}: {name}: "
                        f"{line.strip()[:80]}")
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
