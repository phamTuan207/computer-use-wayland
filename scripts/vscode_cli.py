#!/usr/bin/env python3
"""Repo-owned VS Code CLI wrapper. Stdlib only.

VS Code ships a `code` CLI for opening files and folders, jumping to a
line, diffing files, and managing extensions, but the CLI documents no
way to list open tabs or read editor buffers. This wrapper adds the
missing read side by parsing VS Code's own persisted workspace state,
and passes the rest through to `code` with argv only.

What is verified (laptop, VS Code 1.146.0, 2026-11-18):
- `code --version`, `code --help`, `code --list-extensions
  --show-versions` (51 extensions) all run read-only.
- `code --status` exits 0 with empty output when no VS Code instance
  is running; it only reports diagnostics for a running instance.
- Open tabs ARE readable without a running instance: every workspace
  under ~/.config/Code/User/workspaceStorage/<hash>/ has a
  state.vscdb sqlite DB, and the key `memento/workbench.parts.editor`
  holds a serialized editor grid whose leaf editors carry
  `resourceJSON.fsPath`. Verified across all 10 workspace dirs on the
  laptop (iac-eval, Reasearch-IaC, Legacy-link, LTHDT and others).
  The DB is always copied to a temp file first and opened read-only,
  so a running VS Code (locked live DB) is never touched.
- Saved file content is just the file on disk; `read` reads it.
- Unsaved/dirty buffer text is NOT verified readable: the only
  Backups entry on the laptop is a 94-byte metadata blob for an
  untitled editor (no text content observed), so this wrapper never
  claims buffer reads. `backups` only lists backup files.

What is NOT wrapped: extension install/uninstall (unverified live,
and mutating the profile). Run raw `code --install-extension <id>`
from the shell only when explicitly requested.

Commands (each prints exactly one JSON object on stdout):
  workspaces              List known workspaces from workspaceStorage.
  tabs [--workspace PATH] [--all]
                          Open tabs per workspace, from state.vscdb.
                          Default is all workspaces.
  read <file> [--max-chars N]
                          Read a saved file (default cap 20000 chars,
                          hard cap 1 MiB file size).
  files <folder> [--max N]
                          List files under a folder (default cap 200;
                          skips .git, node_modules, __pycache__).
  extensions              List installed extensions with versions.
  open <path> [--new-window|--reuse-window] [--goto LINE[:COL]]
                          Open an existing file or folder. Refuses a
                          nonexistent path, because `code` would
                          create a missing file.
  diff <file> <file>      Open a two-file diff. Both must exist.
  status                  `code --status` diagnostics (empty when
                          VS Code is not running).
  version                 `code --version`, first line only.
  backups                 List VS Code backup files (metadata only).

Global flags (before the subcommand): --config-dir DIR (default
~/.config/Code, or $VSCODE_CONFIG_DIR; tests only).
Exit 0 on success, 1 on error. No REPL mode, no shell, argv only.
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

CODE_TIMEOUT_SECONDS = 30
MAX_READ_BYTES = 1_048_576
DEFAULT_MAX_CHARS = 20000
DEFAULT_MAX_FILES = 200
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
EDITOR_STATE_KEY = "memento/workbench.parts.editor"

USAGE = (
    "usage: vscode_cli.py [--config-dir DIR] "
    "workspaces|tabs|read|files|extensions|open|diff|status|version|backups ..."
)


def default_config_dir():
    """VS Code user-data dir, overridable for tests via env or flag."""
    override = os.environ.get("VSCODE_CONFIG_DIR")
    if override:
        return Path(override)
    return Path.home() / ".config" / "Code"


def print_result(result):
    """Print exactly one JSON object on stdout."""
    print(json.dumps(result, ensure_ascii=False), flush=True)


def fail(message):
    """Print an error envelope and exit 1."""
    print_result({"ok": False, "error": message})
    return 1


def workspace_storage(config_dir):
    """Return the workspaceStorage dir, or None when it is absent."""
    path = Path(config_dir) / "User" / "workspaceStorage"
    return path if path.is_dir() else None


def decode_file_uri(uri):
    """Turn a file:// URI into a plain filesystem path."""
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return uri
    return unquote(parsed.path)


def list_workspaces(config_dir):
    """Parse workspace.json in every workspaceStorage dir."""
    storage = workspace_storage(config_dir)
    if storage is None:
        return []
    workspaces = []
    for entry in sorted(storage.iterdir()):
        if not entry.is_dir():
            continue
        meta_path = entry / "workspace.json"
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if "folder" in meta:
            kind, uri = "folder", meta["folder"]
        elif "workspace" in meta:
            kind, uri = "workspace", meta["workspace"]
        else:
            continue
        workspaces.append({"hash": entry.name, "kind": kind,
                           "path": decode_file_uri(uri)})
    return workspaces


def extract_editor_path(editor):
    """Best-effort path or label for one serialized editor entry."""
    try:
        value = json.loads(editor.get("value", ""))
    except (TypeError, json.JSONDecodeError):
        return str(editor.get("id", "unknown"))
    if not isinstance(value, dict):
        return str(value)[:200]
    resource = value.get("resourceJSON") or value.get("resource") or {}
    if isinstance(resource, dict):
        path = resource.get("fsPath") or resource.get("path")
        if path:
            if resource.get("scheme") == "untitled":
                return "untitled:" + path
            return path
    uri = value.get("uri")
    if isinstance(uri, str):
        return decode_file_uri(uri)
    return str(editor.get("id", "unknown"))


def parse_editor_grid(state):
    """Walk a serialized editor grid into groups of open editors."""
    groups = []

    def walk(node, group_index):
        if isinstance(node, dict):
            if "editors" in node and isinstance(node["editors"], list):
                editors = [extract_editor_path(ed)
                           for ed in node["editors"]]
                active = None
                mru = node.get("mru") or []
                if mru and isinstance(mru[0], int) and 0 <= mru[0] < len(editors):
                    active = editors[mru[0]]
                groups.append({"group": group_index, "editors": editors,
                               "active": active})
                return group_index + 1
            for child in node.values():
                group_index = walk(child, group_index)
            return group_index
        if isinstance(node, list):
            for child in node:
                group_index = walk(child, group_index)
        return group_index

    walk(state, 0)
    return groups


def read_open_tabs(config_dir, workspace_hash):
    """Copy a workspace state.vscdb to temp, read the editor key."""
    db_path = (Path(config_dir) / "User" / "workspaceStorage"
               / workspace_hash / "state.vscdb")
    if not db_path.is_file():
        return None, "no state.vscdb"
    try:
        with tempfile.TemporaryDirectory(prefix="vscode-tabs-") as tmp:
            copy = Path(tmp) / "state.vscdb"
            shutil.copyfile(db_path, copy)
            conn = sqlite3.connect("file:%s?mode=ro" % copy, uri=True)
            try:
                row = conn.execute(
                    "SELECT value FROM ItemTable WHERE key = ?",
                    (EDITOR_STATE_KEY,)).fetchone()
            finally:
                conn.close()
    except (OSError, sqlite3.Error) as exc:
        return None, "cannot read state.vscdb: %s" % exc
    if row is None:
        return [], None
    try:
        state = json.loads(row[0])
    except json.JSONDecodeError:
        return None, "editor state is not valid JSON"
    return parse_editor_grid(state), None


def run_code(argv, timeout=CODE_TIMEOUT_SECONDS):
    """Run `code` with argv only; return (returncode, stdout, stderr)."""
    binary = shutil.which("code")
    if binary is None:
        return None, "", "code binary not on PATH"
    try:
        result = subprocess.run([binary, *argv], capture_output=True,
                                text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "", "code timed out after %ds" % timeout
    except OSError as exc:
        return None, "", "failed to run code: %s" % exc
    return result.returncode, result.stdout, result.stderr


def cmd_workspaces(args):
    """List known workspaces from workspaceStorage."""
    workspaces = list_workspaces(args.config_dir)
    print_result({"ok": True, "workspaces": workspaces})
    return 0


def cmd_tabs(args):
    """Open tabs per workspace, from the persisted editor state."""
    workspaces = list_workspaces(args.config_dir)
    if args.workspace:
        wanted = str(Path(args.workspace).resolve())
        workspaces = [ws for ws in workspaces
                      if str(Path(ws["path"]).resolve()) == wanted]
        if not workspaces:
            return fail("no known workspace matches: %s" % args.workspace)
    out = []
    for ws in workspaces:
        groups, error = read_open_tabs(args.config_dir, ws["hash"])
        entry = {"workspace": ws["path"], "kind": ws["kind"],
                 "hash": ws["hash"]}
        if error is not None:
            entry["groups"] = []
            entry["note"] = error
        else:
            entry["groups"] = groups
        out.append(entry)
    print_result({"ok": True, "workspaces": out})
    return 0


def cmd_read(args):
    """Read a saved file, bounded."""
    path = Path(args.file)
    if not path.is_file():
        return fail("not a regular file: %s" % args.file)
    try:
        size = path.stat().st_size
    except OSError as exc:
        return fail("cannot stat %s: %s" % (args.file, exc))
    if size > MAX_READ_BYTES:
        return fail("file too large (%d bytes, cap %d): %s"
                    % (size, MAX_READ_BYTES, args.file))
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        return fail("cannot read %s: %s" % (args.file, exc))
    truncated = len(text) > args.max_chars
    print_result({"ok": True, "path": str(path), "size_bytes": size,
                  "truncated": truncated,
                  "content": text[:args.max_chars]})
    return 0


def cmd_files(args):
    """List files under a folder, bounded, skipping junk dirs."""
    root = Path(args.folder)
    if not root.is_dir():
        return fail("not a directory: %s" % args.folder)
    found = []
    truncated = False
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if len(found) >= args.max:
                truncated = True
                break
            full = Path(current) / name
            try:
                size = full.stat().st_size
            except OSError:
                size = None
            found.append({"path": str(full.relative_to(root)),
                          "size_bytes": size})
        if truncated:
            break
    print_result({"ok": True, "folder": str(root), "files": found,
                  "truncated": truncated})
    return 0


def cmd_extensions(args):
    """List installed extensions with versions, via `code`."""
    argv = ["--list-extensions", "--show-versions"]
    returncode, stdout, stderr = run_code(argv)
    if returncode is None:
        return fail(stderr)
    if returncode != 0:
        return fail("code --list-extensions failed (%s): %s"
                    % (returncode, stderr.strip()[:500]))
    extensions = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if "@" in line:
            ext_id, _, version = line.rpartition("@")
        else:
            ext_id, version = line, ""
        extensions.append({"id": ext_id, "version": version})
    print_result({"ok": True, "extensions": extensions})
    return 0


def cmd_open(args):
    """Open an existing file or folder in VS Code."""
    path = Path(args.path)
    if not path.exists():
        return fail("path does not exist (refusing to let code create "
                    "it): %s" % args.path)
    argv = []
    if args.new_window:
        argv.append("--new-window")
    if args.reuse_window:
        argv.append("--reuse-window")
    if args.goto:
        if not path.is_file():
            return fail("--goto needs a file, not a folder: %s" % args.path)
        argv.extend(["--goto", "%s:%s" % (args.path, args.goto)])
    else:
        argv.append(args.path)
    returncode, stdout, stderr = run_code(argv)
    if returncode is None:
        return fail(stderr)
    print_result({"ok": returncode == 0, "path": args.path,
                  "returncode": returncode,
                  "stdout": stdout[:4096], "stderr": stderr[:4096]})
    return 0 if returncode == 0 else 1


def cmd_diff(args):
    """Open a two-file diff. Both files must exist."""
    for path in (args.left, args.right):
        if not Path(path).is_file():
            return fail("not a regular file: %s" % path)
    returncode, stdout, stderr = run_code(
        ["--diff", args.left, args.right])
    if returncode is None:
        return fail(stderr)
    print_result({"ok": returncode == 0, "left": args.left,
                  "right": args.right, "returncode": returncode,
                  "stdout": stdout[:4096], "stderr": stderr[:4096]})
    return 0 if returncode == 0 else 1


def cmd_status(args):
    """`code --status` diagnostics (empty when VS Code is not running)."""
    returncode, stdout, stderr = run_code(["--status"], timeout=15)
    if returncode is None:
        return fail(stderr)
    print_result({"ok": returncode == 0,
                  "running": bool(stdout.strip()),
                  "returncode": returncode,
                  "stdout": stdout[:4096], "stderr": stderr[:4096]})
    return 0 if returncode == 0 else 1


def cmd_version(args):
    """`code --version`, first line only."""
    returncode, stdout, stderr = run_code(["--version"], timeout=15)
    if returncode is None:
        return fail(stderr)
    lines = stdout.splitlines()
    print_result({"ok": returncode == 0,
                  "version": lines[0].strip() if lines else "",
                  "returncode": returncode})
    return 0 if returncode == 0 else 1


def cmd_backups(args):
    """List VS Code backup files (metadata only, never parsed)."""
    root = Path(args.config_dir) / "Backups"
    found = []
    if root.is_dir():
        for path in sorted(root.rglob("*")):
            if path.is_file():
                try:
                    size = path.stat().st_size
                except OSError:
                    size = None
                found.append({"path": str(path.relative_to(root)),
                              "size_bytes": size})
    print_result({"ok": True, "backups": found,
                  "note": "backup content is not parsed; unsaved buffer "
                          "text is not verified readable"})
    return 0


def build_parser():
    """Argument parser: global flags, then one subcommand."""
    parser = argparse.ArgumentParser(
        prog="vscode_cli.py", description="Repo-owned VS Code CLI wrapper.")
    parser.add_argument("--config-dir", default=None,
                        help="VS Code user-data dir (default ~/.config/Code)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("workspaces", help="list known workspaces")
    tabs = sub.add_parser("tabs", help="list open tabs per workspace")
    tabs.add_argument("--workspace", default=None,
                      help="only this workspace folder path")
    tabs.add_argument("--all", action="store_true",
                      help="all workspaces (the default)")
    read = sub.add_parser("read", help="read a saved file")
    read.add_argument("file")
    read.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    files = sub.add_parser("files", help="list files under a folder")
    files.add_argument("folder")
    files.add_argument("--max", type=int, default=DEFAULT_MAX_FILES)
    sub.add_parser("extensions", help="list installed extensions")
    open_cmd = sub.add_parser("open", help="open a file or folder")
    open_cmd.add_argument("path")
    open_cmd.add_argument("--new-window", action="store_true")
    open_cmd.add_argument("--reuse-window", action="store_true")
    open_cmd.add_argument("--goto", default=None,
                          help="line or line:column for a file")
    diff = sub.add_parser("diff", help="open a two-file diff")
    diff.add_argument("left")
    diff.add_argument("right")
    sub.add_parser("status", help="code --status diagnostics")
    sub.add_parser("version", help="code --version")
    sub.add_parser("backups", help="list VS Code backup files")
    return parser


def main(argv):
    """Dispatch one subcommand; one JSON object on stdout."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.config_dir = (Path(args.config_dir) if args.config_dir
                       else default_config_dir())
    dispatch = {"workspaces": cmd_workspaces, "tabs": cmd_tabs,
                "read": cmd_read, "files": cmd_files,
                "extensions": cmd_extensions, "open": cmd_open,
                "diff": cmd_diff, "status": cmd_status,
                "version": cmd_version, "backups": cmd_backups}
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
