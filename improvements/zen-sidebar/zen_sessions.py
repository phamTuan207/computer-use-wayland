#!/usr/bin/env python3
"""Offline editor for Zen Browser's zen-sessions.jsonlz4.

Zen 1.18+ keeps Spaces, folders, pinned tabs and Essentials in
<profile>/zen-sessions.jsonlz4 (mozlz4 container), NOT in Firefox's
sessionstore.jsonlz4. This tool reads that file, prints its state, and
applies small, validated edits while Zen is fully closed:

  dump                      list spaces, folders and tabs
  move-workspace --tab ID --to SPACE_UUID
  move-folder    --tab ID --to FOLDER_ID | --to none
  pin / unpin    --tab ID
  reorder-pins   --order SYNCID,SYNCID,...

Tabs are identified by their zenSyncId (see dump), or by a URL substring
with --tab-url. Writes are dry-run unless --apply is given. An --apply
write refuses to run while Zen appears to be running with the profile
(profile lock probe in both lock domains, plus a process scan),
validates referential integrity before and after the edit, keeps a
timestamped backup with a sha256 manifest OUTSIDE the profile (default
<profile>/../zen-editor-backups/, override with --backup-dir),
round-trip verifies the written file, and restores the backup if
verification fails. Pin and unpin also move the tab entry to the
pinned-region boundary, because tabs[] order is positional.

Schema basis (Zen 1.24.3b, from zenform's session-format documentation;
the format is undocumented and version-sensitive, so validate always):
top level {lastCollected, tabs, folders, splitViewData, groups, spaces};
spaces[] {uuid, name, containerTabId, ...}; folders[] {id, name,
collapsed, workspaceId, prevSiblingInfo, emptyTabIds}; tabs[] entries
carry pinned, zenEssential, zenWorkspace (uuid, null for Essentials),
groupId (folder membership), zenSyncId, entries[index-1].url.

Requires: python3 + the lz4 package (lz4.block). Stdlib otherwise.
Ponytail: one file, no abstraction beyond the operations above.
"""

import argparse
import fcntl
import json
import os
import shutil
import struct
import sys
import tempfile
import time

import lz4.block

MAGIC = b"mozLz40\x00"
SESSION_FILE = "zen-sessions.jsonlz4"


# ---------- mozlz4 codec ----------

def read_mozlz4(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12 or data[:8] != MAGIC:
        raise ValueError(f"{path}: bad magic, not a mozlz4 file")
    (size,) = struct.unpack("<I", data[8:12])
    try:
        raw = lz4.block.decompress(data[12:], uncompressed_size=size)
    except Exception as exc:
        raise ValueError(f"{path}: LZ4 decompress failed ({exc})") from exc
    if len(raw) != size:
        raise ValueError(f"{path}: size mismatch after decompress")
    return json.loads(raw.decode("utf-8"))


def encode_mozlz4(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # store_size=False: the mozlz4 header already carries the size, and the
    # payload must be one pure LZ4 block (python-lz4's default store_size
    # prefix is NOT part of the format and makes Zen reject the file).
    return MAGIC + struct.pack("<I", len(raw)) + lz4.block.compress(raw, store_size=False)


def write_mozlz4_atomic(path, obj):
    payload = encode_mozlz4(obj)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(os.path.dirname(path), os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ---------- state helpers ----------

def tab_url(tab):
    entries = tab.get("entries") or []
    idx = tab.get("index", 1) - 1
    if 0 <= idx < len(entries):
        return entries[idx].get("url", "")
    return entries[-1].get("url", "") if entries else ""


def find_tab(state, ident=None, url_part=None):
    tabs = state.get("tabs", [])
    if ident:
        hits = [t for t in tabs if t.get("zenSyncId") == ident]
    elif url_part:
        hits = [t for t in tabs if url_part in tab_url(t)]
    else:
        raise ValueError("identify the tab with --tab or --tab-url")
    if len(hits) != 1:
        raise ValueError(f"tab selector matched {len(hits)} tabs, need exactly 1")
    return hits[0]


def validate(state):
    """Return a list of referential-integrity problems (empty = sound)."""
    problems = []
    spaces = {s.get("uuid") for s in state.get("spaces", [])}
    folders = {f.get("id") for f in state.get("folders", [])}
    groups = {g.get("id") for g in state.get("groups", [])}
    folder_ids = folders | groups
    folder_by_id = {f.get("id"): f for f in state.get("folders", [])}
    seen_sync = set()
    seen_unpinned = False
    for tab in state.get("tabs", []):
        sid = tab.get("zenSyncId")
        if sid in seen_sync:
            problems.append(f"duplicate zenSyncId {sid}")
        seen_sync.add(sid)
        ws = tab.get("zenWorkspace")
        if ws is not None and ws not in spaces:
            problems.append(f"tab {sid}: zenWorkspace {ws} not in spaces[]")
        gid = tab.get("groupId")
        if gid is not None and gid not in folder_ids:
            problems.append(f"tab {sid}: groupId {gid} not in folders[]/groups[]")
        if gid is not None and gid in folder_by_id:
            folder_ws = folder_by_id[gid].get("workspaceId")
            if folder_ws != ws:
                problems.append(
                    f"tab {sid}: in folder {gid} (workspace {folder_ws}) "
                    f"but tab workspace is {ws}")
        if tab.get("pinned"):
            if seen_unpinned:
                problems.append(f"tab {sid}: pinned tab sits after unpinned tabs "
                                "(tabs[] pinned region must come first)")
        else:
            seen_unpinned = True
    for folder in state.get("folders", []):
        ws = folder.get("workspaceId")
        if ws is not None and ws not in spaces:
            problems.append(f"folder {folder.get('id')}: workspaceId {ws} not in spaces[]")
        prev = (folder.get("prevSiblingInfo") or {}).get("id")
        if prev is not None and prev not in folders:
            problems.append(f"folder {folder.get('id')}: prevSiblingInfo {prev} not in folders[]")
        for empty_id in folder.get("emptyTabIds", []):
            if empty_id not in seen_sync:
                problems.append(f"folder {folder.get('id')}: emptyTabId {empty_id} has no tab")
    # prevSiblingInfo chains must terminate at a null link, without cycles.
    for folder in state.get("folders", []):
        chain_seen = {folder.get("id")}
        cur = folder
        while (cur.get("prevSiblingInfo") or {}).get("id") is not None:
            nxt = cur["prevSiblingInfo"]["id"]
            if nxt in chain_seen:
                problems.append(f"folder {folder.get('id')}: prevSiblingInfo cycle at {nxt}")
                break
            if nxt not in folder_by_id:
                break  # dangling link already reported above
            chain_seen.add(nxt)
            cur = folder_by_id[nxt]
    return problems


# ---------- operations (pure state transforms) ----------

def op_move_workspace(state, tab, space_uuid):
    spaces = {s.get("uuid") for s in state.get("spaces", [])}
    if space_uuid not in spaces:
        raise ValueError(f"space {space_uuid} not in spaces[]")
    if tab.get("zenEssential"):
        raise ValueError("Essentials span all workspaces (zenWorkspace is null); refusing")
    gid = tab.get("groupId")
    if gid:
        folder = {f.get("id"): f for f in state.get("folders", [])}.get(gid)
        if folder is not None and folder.get("workspaceId") != space_uuid:
            raise ValueError(
                f"tab is in folder {gid}, which belongs to workspace "
                f"{folder.get('workspaceId')}; leave the folder first "
                "(move-folder --to none) or move the folder instead")
    tab["zenWorkspace"] = space_uuid
    return f"tab {tab.get('zenSyncId')} -> workspace {space_uuid}"


def op_move_folder(state, tab, folder_id):
    if folder_id in (None, "none"):
        tab.pop("groupId", None)
        return f"tab {tab.get('zenSyncId')} removed from its folder"
    by_id = {f.get("id"): f for f in state.get("folders", [])}
    folder = by_id.get(folder_id)
    if folder is None:
        raise ValueError(f"folder {folder_id} not in folders[]")
    if folder.get("workspaceId") != tab.get("zenWorkspace"):
        raise ValueError(
            "folder belongs to workspace "
            f"{folder.get('workspaceId')}, tab is in {tab.get('zenWorkspace')}; "
            "move the tab's workspace first"
        )
    tab["groupId"] = folder_id
    return f"tab {tab.get('zenSyncId')} -> folder {folder_id}"


def _move_to_pinned_boundary(state, tab):
    """Reinsert tab at the end of the pinned region of tabs[].

    tabs[] is positional (pinned region first), so a pin or unpin must
    move the entry, not just flip the flag: a newly pinned tab belongs
    at the end of the pinned region, a newly unpinned tab at its start
    (the same boundary, seen from the other side).
    """
    tabs = state.get("tabs", [])
    tabs.remove(tab)
    boundary = 0
    for i, other in enumerate(tabs):
        if other.get("pinned"):
            boundary = i + 1
    tabs.insert(boundary, tab)


def op_set_pinned(state, tab, pinned):
    if not pinned and tab.get("zenEssential"):
        raise ValueError(
            "refusing to unpin an Essential offline: an Essential carries "
            "zenWorkspace null, so the result would be an ordinary tab in no "
            "workspace. Remove the Essential via the live route instead.")
    tab["pinned"] = bool(pinned)
    _move_to_pinned_boundary(state, tab)
    return f"tab {tab.get('zenSyncId')} pinned={bool(pinned)}"


def op_reorder_pins(state, ordered_sync_ids):
    """Reorder the movable pins: pinned tabs that are neither Essentials
    nor folder placeholders. Essentials and placeholders keep their
    positions (their order is structural, not user ordering)."""
    tabs = state.get("tabs", [])
    movable_positions = [i for i, t in enumerate(tabs)
                         if t.get("pinned") and not t.get("zenEssential")
                         and not t.get("zenIsEmpty")]
    by_id = {tabs[i].get("zenSyncId"): tabs[i] for i in movable_positions}
    if set(ordered_sync_ids) != set(by_id) or len(ordered_sync_ids) != len(movable_positions):
        raise ValueError(
            "--order must list every movable pinned tab's zenSyncId exactly "
            "once (pinned, not an Essential, not a folder placeholder); "
            f"movable set is {sorted(by_id)}")
    for pos, sid in zip(movable_positions, ordered_sync_ids):
        tabs[pos] = by_id[sid]
    return f"reordered {len(movable_positions)} movable pinned tabs"


# ---------- profile safety ----------

def _lock_is_held(path):
    """True if another process holds a lock on the file, in either lock
    domain. Gecko's profile lock uses POSIX fcntl record locks (NSPR
    PR_LockFile), which flock(2) cannot see on Linux, so both domains
    are probed. Any unexpected error fails closed (treated as held):
    a wrong "running" answer only costs a retry, a wrong "not running"
    answer can corrupt the session."""
    try:
        fd = os.open(path, os.O_RDWR)
    except FileNotFoundError:
        return False
    except OSError:
        return True
    try:
        for lock_fn in (fcntl.lockf, fcntl.flock):
            try:
                lock_fn(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                return True
            lock_fn(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


def _profile_in_process_cmdline(profile):
    """Best-effort /proc scan: a zen process started with this profile
    on its command line (Linux only; silently skipped elsewhere)."""
    if not os.path.isdir("/proc"):
        return False
    profile = os.path.realpath(profile)
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                if profile.encode() in fh.read():
                    return True
        except OSError:
            continue
    return False


def zen_is_running(profile):
    """True if Zen appears to be running with this profile: the
    .parentlock is held (either lock domain) or a process command line
    references the profile. A missing lock file plus no process is the
    not-running case; a stale lock file alone does not block."""
    lock = os.path.join(profile, ".parentlock")
    if os.path.exists(lock) and _lock_is_held(lock):
        return True
    return _profile_in_process_cmdline(profile)


def _sha256(path):
    import hashlib
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zen_version_hint(profile):
    """Best-effort Zen/Firefox version from the profile's
    compatibility.ini, recorded with each backup so a post-upgrade
    schema change is visible in the record."""
    try:
        with open(os.path.join(profile, "compatibility.ini"),
                  encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "version" in line.lower():
                    return line.strip()
    except OSError:
        pass
    return None


def make_backup(profile, backup_root):
    """Copy both session files and both backup folders into a fresh
    timestamped directory OUTSIDE the profile, with a sha256 manifest.
    The zen-sessions copy is parse-verified before anything is written,
    so a truncated backup can never be 'restored' over a good file."""
    stamp = time.strftime("%Y%m%d-%H%M%S") + f".{time.time_ns() % 1_000_000:06d}"
    dest = os.path.join(backup_root, stamp)
    os.makedirs(dest)
    manifest = {"created": stamp, "profile": os.path.abspath(profile),
                "zen_version_hint": _zen_version_hint(profile), "files": {}}
    for name in (SESSION_FILE, "sessionstore.jsonlz4"):
        src = os.path.join(profile, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, name))
            manifest["files"][name] = _sha256(src)
    for folder in ("zen-sessions-backup", "sessionstore-backups"):
        src = os.path.join(profile, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, folder))
            for root, _dirs, files in os.walk(os.path.join(dest, folder)):
                for name in files:
                    copied = os.path.join(root, name)
                    rel = os.path.relpath(copied, dest)
                    manifest["files"][rel] = _sha256(copied)
    read_mozlz4(os.path.join(dest, SESSION_FILE))  # raises if truncated
    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return dest


def apply_edit(profile, state, summary, problems_before=(), backup_root=None):
    if zen_is_running(profile):
        raise SystemExit("Zen appears to be running with this profile; quit Zen first")
    if not os.path.exists(os.path.join(profile, "sessionstore.jsonlz4")):
        print("warning: sessionstore.jsonlz4 is absent from the profile root; "
              "the last shutdown may have been unclean", file=sys.stderr)
    new_problems = [p for p in validate(state) if p not in problems_before]
    if new_problems:
        raise SystemExit("edited state introduces validation problems:\n  "
                         + "\n  ".join(new_problems))
    if backup_root is None:
        backup_root = os.path.join(os.path.dirname(os.path.abspath(profile)),
                                   "zen-editor-backups")
    backup_dir = make_backup(profile, backup_root)
    backup_file = os.path.join(backup_dir, SESSION_FILE)
    path = os.path.join(profile, SESSION_FILE)
    if zen_is_running(profile):  # re-check immediately before the write
        raise SystemExit("Zen started during the edit; nothing written")
    write_mozlz4_atomic(path, state)
    try:
        reread = read_mozlz4(path)
        if reread != state:
            raise ValueError("round-trip mismatch")
        new_problems = [p for p in validate(reread) if p not in problems_before]
        if new_problems:
            raise ValueError("written file has new problems: " + "; ".join(new_problems))
    except BaseException:
        shutil.copy2(backup_file, path)
        raise SystemExit(f"write verification failed; original restored from {backup_dir}")
    print(f"applied: {summary}")
    print(f"backup:  {backup_dir} (manifest.json records sha256 of every file)")


# ---------- CLI ----------

def cmd_dump(state):
    print("spaces:")
    for s in state.get("spaces", []):
        print(f"  {s.get('uuid')}  {s.get('name')!r} container={s.get('containerTabId')}")
    print("folders:")
    for f in state.get("folders", []):
        print(f"  {f.get('id')}  {f.get('name')!r} workspace={f.get('workspaceId')} "
              f"collapsed={f.get('collapsed')}")
    print("tabs:")
    for t in state.get("tabs", []):
        print(f"  {t.get('zenSyncId')}  pinned={t.get('pinned')} "
              f"essential={t.get('zenEssential')} ws={t.get('zenWorkspace')} "
              f"folder={t.get('groupId')} {tab_url(t)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--profile", required=True, help="Zen profile directory")
    ap.add_argument("--backup-dir", default=None,
                    help="where --apply backups go (default: zen-editor-backups "
                         "next to the profile, outside it)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("dump")

    for name in ("move-workspace", "move-folder", "pin", "unpin"):
        p = sub.add_parser(name)
        p.add_argument("--tab", help="zenSyncId of the tab")
        p.add_argument("--tab-url", help="URL substring identifying the tab")
        p.add_argument("--apply", action="store_true", help="write (default: dry run)")
        if name in ("move-workspace", "move-folder"):
            p.add_argument("--to", required=True,
                           help="target space uuid / folder id ('none' leaves the folder)")

    p = sub.add_parser("reorder-pins")
    p.add_argument("--order", required=True,
                   help="comma-separated zenSyncIds of the movable pins (pinned, "
                        "not Essentials, not folder placeholders), full movable set")
    p.add_argument("--apply", action="store_true")

    args = ap.parse_args(argv)
    path = os.path.join(args.profile, SESSION_FILE)
    state = read_mozlz4(path)
    problems_before = validate(state)
    if problems_before:
        print("WARNING: loaded state has pre-existing integrity problems "
              "(an --apply write is rejected only for NEW problems):", file=sys.stderr)
        for prob in problems_before:
            print(f"  {prob}", file=sys.stderr)

    if args.cmd == "dump":
        cmd_dump(state)
        return 0

    if args.cmd == "reorder-pins":
        summary = op_reorder_pins(state, [s.strip() for s in args.order.split(",") if s.strip()])
    else:
        tab = find_tab(state, ident=args.tab, url_part=args.tab_url)
        if args.cmd == "move-workspace":
            summary = op_move_workspace(state, tab, args.to)
        elif args.cmd == "move-folder":
            summary = op_move_folder(state, tab, args.to)
        elif args.cmd == "pin":
            summary = op_set_pinned(state, tab, True)
        elif args.cmd == "unpin":
            summary = op_set_pinned(state, tab, False)

    if args.apply:
        apply_edit(args.profile, state, summary,
                   problems_before=problems_before, backup_root=args.backup_dir)
    else:
        print(f"dry run: {summary} (re-run with --apply to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
