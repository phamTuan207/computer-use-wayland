# zen-sidebar: programmatic Zen folder / workspace / pin control

Two small tools from the 2026-11-27 research (see
`../zen-folder-tool-research-20261127.md` for the full report, sources,
and the laptop test protocol). Research prototypes: not integrated into
the machine layer, not run against any live profile yet.

## zen_live.py - live route (rank 1)

Controls the sidebar of a running Zen through Marionette chrome-context
JavaScript (the listener Zen already exposes on 127.0.0.1:2828). No
restart, no vision. Stdlib only.

Caution: the default port is the LIVE profile's listener. Run against
a throwaway profile first (the report's section 5 protocol); live
mutations have no rollback other than a closed-browser file backup.

```
python3 zen_live.py preflight --profile <throwaway-profile-dir>  # before any launch
python3 zen_live.py introspect        # always first on a new build
python3 zen_live.py list
python3 zen_live.py move-folder --tab-url example.com --to <folder-id>
python3 zen_live.py move-workspace --tab-url example.com --to <space-uuid>
python3 zen_live.py create-folder --label Work --tab-url example.com
python3 zen_live.py pin --tab-url example.com
python3 zen_live.py move-tab --tab-url example.com --index 0
```

## zen_sessions.py - offline route (rank 2)

Edits `zen-sessions.jsonlz4` (where Zen 1.18+ keeps Spaces, folders,
pins and Essentials) while Zen is fully closed. Dry-run by default;
`--apply` refuses while Zen appears to be running with the profile
(lock probe in both lock domains plus a process scan), validates
referential integrity (including sibling cycles and the positional
pinned region), backs up both session files and both backup folders
OUTSIDE the profile with a sha256 manifest (default
`zen-editor-backups/` next to the profile, `--backup-dir` overrides),
writes atomically, and verifies by reading back, restoring the
original on failure. Pin and unpin move the tab entry to the
pinned-region boundary. Needs the Python `lz4` package.

```
python3 zen_sessions.py --profile <profile-dir> dump
python3 zen_sessions.py --profile <profile-dir> move-workspace --tab-url example.com --to <space-uuid> --apply
python3 zen_sessions.py --profile <profile-dir> move-folder --tab <zenSyncId> --to <folder-id> --apply
python3 zen_sessions.py --profile <profile-dir> reorder-pins --order <id1,id2,...> --apply
```

## Tests

```
python3 -m unittest test_zen_sidebar -v
```

27 tests: mozlz4 round-trip and corruption handling, integrity
validation (dangling ids, sibling cycles, workspace mismatch), the
state operations and every refusal case, positional pin moves, CLI
dry-run vs apply against a synthetic profile, the backup-restore path,
the POSIX-lock refusal, JS payload contents, the Marionette client
against an in-process fake server (including split frames, error
frames, and mismatched response ids), and the M11c launch pre-flight
(synthetic env, D-Bus socket, port and profile cases).

## Pre-flight (M11c)

`zen_live.py preflight` verifies the launch preconditions before any
Zen launch attempt and fails fast with a named reason: the
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 env gate, a reachable D-Bus session
bus, a free Marionette port, and (with --profile) a sane throwaway
profile dir outside the real profile home. Detection only: it never
launches, restarts or kills anything.
