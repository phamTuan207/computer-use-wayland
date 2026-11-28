# Worker VMFIX log: VM system Python `re` breakage, SSH down 22:25-22:31 +07
# Owner order 22:34 21/11/2026 (via Muse): SSH from this VM to the laptop is
# DOWN and blocks all laptop work (F3 restoring Zen, F1 guardian diagnostics,
# F2 live tests). Fix it. All times +07 (Asia/Ho_Chi_Minh) + elapsed.
# NOTE: the breakage PARTIALLY HEALED before VMFIX started (another worker,
# F1, had already restored the file at 22:31). VMFIX verified, investigated
# the cause, and proved the repair durable. VMFIX changed NOTHING under
# /usr/lib itself: the on-disk state was already correct and verified.

## 22:34 test start (T+0)
- VM repo todolist-push. Spawned as Worker VMFIX after Y6r reported SSH dead:
  `/usr/lib/python3.12/re.py` missing, `/usr/lib/python3.12/re/` a directory
  with 3.13-style files but NO `__init__.py`, `import re` an empty namespace
  package without `compile`. Directory mtime 15:25:39 UTC (22:25:39 +07).

## Verification (22:34-22:35, T+0-1m): the state had ALREADY changed
- `python3 -c "import re; print(re.compile('x'))"` -> prints `re.compile('x')`,
  rc=0. WORKS.
- `/usr/lib/python3.12/re/` now contains `__init__.py` (16315 B, mtime
  15:31:12 UTC = 22:31:12 +07) plus `__pycache__`. Dir mtime 15:29:58 UTC.
- `python3 --version` -> 3.12.3. `re.__file__` =
  `/usr/lib/python3.12/re/__init__.py`. `re.match`/`re.sub`/`re.findall`
  all correct. `~/workspace/ssh-laptop.sh 'echo SSH_OK'` -> `SSH_OK`, rc=0.
- Running as root on this VM (uid=0); sudo works. No suspicious processes
  (only my own exec shells). dpkg.log last entry 11:14:10. No /var/log/apt.
  No bash history files. No crontab binary; /etc/cron.d has only e2scrub_all.

## Investigation (22:35-22:38): who added `__init__.py`, what broke `re.py`
### 1. The `re/` package layout is CORRECT for this system, not a 3.13 Frankenstein
- `dpkg -S /usr/lib/python3.12/re.py` -> NO path found. Ubuntu's
  libpython3.12-stdlib does NOT ship `re.py` at all.
- `dpkg -S /usr/lib/python3.12/re/__init__.py` and `_compiler.py` ->
  `libpython3.12-minimal:amd64` OWNS them. `dpkg -L libpython3.12-minimal`
  lists the whole package: `re/`, `re/__init__.py`, `re/_casefix.py`,
  `re/_compiler.py`, `re/_constants.py`, `re/_parser.py`.
- Correction to Y6r's "3.13-style" label: this package layout IS what Ubuntu
  3.12.3-1ubuntu0.17 ships. `re.py` must NEVER be created here; it would
  shadow/conflict with the packaged `re/` package. The task brief's "restore
  re.py" instruction was based on the wrong premise and is OVERRIDDEN by the
  dpkg evidence.
- `__init__.py` header is the stock SRE header, `__version__ = "2.2.1"`.

### 2. Who restored it: F1 (journal + F1 log agree exactly)
- journalctl 15:29-15:31 UTC:
  - 15:29:56 `sudo apt-get update` (session to 15:30:50)
  - 15:31:12 `sudo cp /tmp/re-init.py /usr/lib/python3.12/re/__init__.py`
  - 15:31:12 `sudo chmod 644 /usr/lib/python3.12/re/__init__.py`
  - 15:31:12 `sudo chown root:root /usr/lib/python3.12/re/__init__.py`
- F1's log (improvements/worker-f1-guardian-fix-log.md, section "VM incident
  blocking SSH (22:26-22:31, fixed)"): SSH broke ~22:26 with
  `AttributeError: module 're' has no attribute 'compile'` in
  tailscale-proxy.py. `dpkg -V libpython3.12-minimal` reported exactly ONE
  missing file. F1 downloaded the authentic file from CPython v3.12.3 tag
  (raw.githubusercontent.com/python/cpython/v3.12.3/Lib/re/__init__.py),
  md5 `14c5eb10123bc6623861305257e1c156` EXACTLY matches dpkg's expected md5,
  installed with sudo (644, root:root). Verified `import re` OK, `dpkg -V`
  clean, SSH OK 22:31:17 +07. apt NOT usable (azure.archive unreachable).
- /tmp evidence: `/tmp/re-init-3.12.py` (15:29, 16315 B) and `/tmp/re-init.py`
  (15:31, 16315 B), both md5 `14c5eb10123bc6623861305257e1c156`, identical to
  the installed file (`diff` IDENTICAL).
- Y13r2-council-1.md:83 corroborates authenticity independently: the restored
  file "compiles to a code object marshal-identical to the surviving cached
  __init__.cpython-312.pyc" (the .pyc the ORIGINAL file generated at 11:21
  UTC). The parent independently verified md5 pristine.
- The `re/` dir mtime 15:29:58 is F1's first (unsudoed, as root) restore of
  __init__.py into the dir; the 15:31:12 sudo cp overwrote it in place
  (overwrite does not change dir mtime). Consistent, no anomaly left.

### 3. An earlier stopgap: Y14b (22:30 +07)
- Y14b's log (line ~633): its verification was BLOCKED at 22:30 by the same
  breakage. `__pycache__` still held `__init__.cpython-312.pyc`, so Y14b
  restored it sourceless as `/usr/lib/python3.12/re/__init__.pyc` (system's
  own bytecode, no reconstruction, no internet). Verified `import re` OK.
  Y14b flagged it as a stopgap, not a proper fix, and asked for a proper
  repair when the fleet is quiet.
- That sourceless `__init__.pyc` is GONE now (current `ls` of `re/` shows no
  top-level `__init__.pyc`): superseded by F1's proper `.py` restore at
  22:31. No action needed.

### 4. The original deletion (~22:25:39 +07): cause UNKNOWN, all leads exhausted
- `re/` dir mtime was 15:25:39 UTC per Y6r; Y14b: "probes ran fine at 22:09
  and the re/ directory mtime is 15:25, so the deletion predates the failure
  window". F1: "deletion window is unclear (mtime anomaly noted, not
  resolved)".
- Ruled out: no sudo command in journal 15:15-15:30 except F1's own
  (15:29:12 `true`, 15:29:56 `apt-get update`), both AFTER the breakage.
  No dpkg/apt activity (dpkg.log last 11:14:10). No cron job touches
  /usr/lib (crontab binary absent; only e2scrub_all in /etc/cron.d;
  systemd timers show only home-assistant-ensure firing every ~65s,
  unrelated). Y14b: "no Y14b command touches /usr/lib". Y13r2-council-1:
  "No probe of mine touches /usr/lib". F1: cause unknown. /tmp at 15:25
  holds only my observe screenshot + bidi-count.txt (my own files).
- Conclusion: deleted by an unsudoed root process (every agent on this VM
  runs as root directly, so a plain `rm` leaves no journal trace) or a
  filesystem event. No log identifies the actor. Recorded as UNKNOWN, not
  guessed. Mitigation: `dpkg -V libpython3.12-minimal` detects a recurrence
  instantly (it reported exactly the one missing file this time).
  RECOMMENDATION to parent: add `python3 -c "import re"` (or `dpkg -V
  libpython3.12-minimal`) to the watchdog's 15-min checks.

## Guardian question (parent coordination 22:36): does the broken `re` explain the guardian failure?
- YES, the guardian chain imports `re` at module top: cursor_session.py:8,
  cursor_theme.py:6, indicator.py:7, cu.py:13. `re.fullmatch` validates the
  32-hex session tokens (cursor_session.py:33,50; cursor_theme.py:64,129,186;
  indicator.py:37,48,150). 19 scripts under scripts/ import `re`.
- NO, the VM's broken `re` did NOT cause the guardian startup failure. The
  guardian runs ON THE LAPTOP (via SSH + relay); the laptop's Python was
  never affected. The VM breakage broke `tailscale-proxy.py` (which imports
  `re`) -> SSH died -> ALL laptop work blocked (F1/F2/F3 diagnostics
  included). F1's `re` restore fixed the TRANSPORT, not the guardian.
- The guardian's own root cause (F1 live probes, in F1's log): the
  cursor-guard Hyprland plugin is NOT loaded on the live session
  (`hyprctl cu-cursor status` returns "unknown request", rc=0; plugin list
  hyprbars only; no cursor-guard.sock). `cursor_theme.check_guard` does
  `json.loads` on that reply -> JSONDecodeError -> guardian dies instantly.
  F1's guardian fix (code fixes C/D + live restoration B/E) is separate and
  still in progress. (Had the guardian run on the VM, its top-level
  `import re` would have failed the same way; noted, not the cause.)

## Proof the repair is durable (22:38)
- `python3 -c "import re; print(re.compile('x'))"` -> `re.compile('x')`, rc=0.
- `re` functional exercise 12/12 OK (fullmatch incl. guardian's exact
  32-hex + theme patterns, named groups, IGNORECASE, search, findall, sub,
  split, lookahead, MULTILINE|DOTALL, escape).
- Stdlib smoke OK: json, logging, urllib.request, argparse, ssl, re import
  clean. `re.__version__` 2.2.1.
- `dpkg -V libpython3.12-minimal` -> empty, rc=0 (ALL files match package
  checksums). `dpkg -V libpython3.12-stdlib` -> empty, rc=0.
- md5 `14c5eb10123bc6623861305257e1c156` for /tmp/re-init-3.12.py,
  /tmp/re-init.py, and installed `re/__init__.py` (all identical).
- `ssh-laptop.sh 'echo SSH_OK'` -> `SSH_OK`, rc=0.
- Fresh `computer-use observe` on the laptop 22:38:16 +07 -> id
  e64afc7de683, capture 36ms, image
  ~/.cache/agent-computer-use/e64afc7de683.jpg. End-to-end path
  (VM python -> tailscale-proxy -> SSH -> laptop observe) proven.
- NOTE on `python3 -m test test_re`: reports FAILURE with run=0 because
  `test.test_re` is NOT INSTALLED (libpython3.12-testsuite absent:
  `ModuleNotFoundError: No module named 'test.test_re'`). That is a missing
  testsuite package, NOT a `re` defect. The 12/12 functional exercise above
  is the `re` proof instead.

## Verdict
- The current state is the CORRECT, stock, durable state: Ubuntu
  3.12.3-1ubuntu0.17's `re/` package, byte-identical to the packaged files,
  verified three ways (dpkg -V clean, md5 matches dpkg's expected md5,
  restored source compiles marshal-identical to the surviving original
  .pyc). NOT a 3.13 Frankenstein. Do NOT create `re.py`; do NOT touch
  /usr/lib/python3.12/re again without a dpkg-verified reason.
- VMFIX made NO system changes: nothing to repair remained. No council +
  redteam is owed for this verification: the repair (F1's) touched only the
  single packaged file `re/__init__.py`, nothing beyond the `re` module,
  and VMFIX itself touched no system file. (F1's guardian code fixes get
  their own council + redteam per F1's plan.)
- SSH is back; F1/F2/F3 laptop work unblocked (they were told to resume
  at 22:33). Open item: the original deletion cause is UNKNOWN; watchdog
  check recommended (see above).
