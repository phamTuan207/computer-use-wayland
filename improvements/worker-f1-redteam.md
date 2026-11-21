# Redteam verdict: Worker F1 guardian-startup fix (commits 5033c9d, 708bef0)

Verdict: AMEND

Date: 2026-11-21, about 22:50 +07. Reviewer: independent redteam, VM repo only.
Read-only laptop checks via ssh-laptop.sh. Nothing modified, nothing loaded,
no session started, no screen driven, no commit. No ydotool used.

## What was checked

- Full diff of 5033c9d (scripts/cursor_theme.py, scripts/cursor_session.py,
  tests/test_cursor_session.py, tests/test_cursor_theme.py).
- Full log improvements/worker-f1-guardian-fix-log.md.
- scripts/visuals.py, scripts/activate-glass.py,
  scripts/activate-cursor-guard.py, scripts/indicator.py,
  scripts/plugin_inventory.py, scripts/sync-installed.py,
  scripts/check-visuals-manifest.py, scripts/refresh-visuals-manifest.py,
  scripts/cu.py (session, doctor, error path).
- Laptop read-only state: optics sha, both manifests, plugin dir listing,
  visuals.jsonl tail, laptop repo git status, visuals-login.lua.
- Live code probes on the VM: guard_reply on 9 edge inputs, drain-thread
  race simulation (300 trials exact supervise pattern, 200 trials variant),
  non-UTF8 stderr test, py_compile of both test files.

## What held up under attack

- The fix fails closed. The new Lifecycle test asserts the driver never runs,
  no session.json is written, and no leases are released on an unloaded
  backend. The live negative test at 22:39 proves the error envelope now
  names the cause instead of the bare message.
- The bytes and bytearray socket path in guard_reply is handled; the earlier
  TypeError regression was caught and fixed.
- The tee preserves the hotkey warning on the success path, so the first
  version's regression is fixed.
- The drift repair itself is verified on the laptop right now: laptop optics
  sha is 9a151634, both manifests are identical, and the loader log shows the
  mid-session re-run failing at fresh_login_gate, not manifest_validation.
- The d086bc43 library file exists in the installed plugins dir and hashes to
  its own name, so that field was self-consistent, only stale.

## Findings, ranked by severity

### R1 (High): the loader still fails silently at login, so the same incident recurs
The fix improves only the session error message. It does nothing to the
login loader path. visuals-login.lua fires visuals.py once on hyprland.start
through hl.exec_cmd, whose stdout and stderr go to /dev/null and whose exit
code is never recorded. If the loader fails for any reason, nothing alerts
anyone until the first session attempt hours later, exactly as happened here.
Trigger: edit native/hyprglass-local-optics.lua again without re-pinning, or
any other loader failure, then log in and try a session. The same opaque
symptom returns, only now with a better message.
Fix: run scripts/check-visuals-manifest.py inside sync-installed.py and
setup.py on every sync, and add a post-login self-check (a doctor probe that
reports plugin and guard state, or a visible log line the owner sees) so a
loader failure is noticed at login, not at first use.

### R2 (High): the drift repair is not durable, it lives only in uncommitted local state
The optics repair is an uncommitted change in a repo at detached HEAD 56f5af4
with other uncommitted changes (verified: git status on the laptop shows M
native/hyprglass-local-optics.lua, M scripts/cu.py, M
improvements/live-test-log.md). The manifest is gitignored local state, not
versioned at all. Any git checkout, reset, clean, or fresh clone wipes the
repair and re-introduces the exact drift. The repair was also done by manual
copy, not through scripts/refresh-visuals-manifest.py, which exists precisely
to re-validate every other manifest field before writing.
Fix: move the laptop repo forward to a commit that contains the blur 0.15
optics (b2afcd1 or later) or commit the optics change, and re-pin the
manifest through refresh-visuals-manifest.py, recording the resulting hashes.

### R3 (High): the session never gates on hyprglass, so a paused or dead glass starts a session with no pill
check_guard only checks cu-cursor. indicator.liquid_available is consulted
only by activate-cursor-guard.py, never by the guardian or the session start.
indicator.Native fails closed on missing glass only when the
native/require-liquid marker exists, and that marker is gitignored and
absent from the installed tree (verified: ls of the installed native dir
shows no require-liquid). So if hyprglass is loaded then paused, or crashes
after load, while cursor-guard stays loaded, check_guard passes and the
session starts with a non-glass indicator. The original symptom, no pill
ever appears, returns silently, this time with a successful session.
Trigger: pause hyprglass (its own docs say a paused hyprglass answers
unknown request to its status command), or let glass crash, then start a
session. It starts, and the pill is missing or wrong.
Fix: the guardian must check indicator.liquid_available(env, ready=True)
before print('ready'), and fail closed naming glass; or publish the
require-liquid marker in the installed tree so Native fails closed.

### R4 (Medium-high): guard_reply misdiagnoses a truncated or corrupt JSON reply as a missing backend
Verified on the VM: guard_reply('{"ok": true, "schema": 1, "active": false,')
raises RuntimeError saying the cursor backend may not be loaded and
prescribing activate-glass.py and activate-cursor-guard.py. The backend is
loaded in that scenario; the reply is truncated. The prescribed remedy then
fails confusingly, because plugin_inventory.setup_baseline rejects a plugin
inventory that already contains hyprglass.
Trigger: any truncated, cut-off, or corrupt reply from hyprctl or the guard
socket (slow pipe, partial write, compositor hiccup). The user follows the
wrong remedy and wastes a live slot.
Fix: distinguish the cases. If the raw reply starts with { or [ and JSON
parsing fails, say the reply is truncated or corrupt and show the decoder
position, and do not prescribe activation. Reserve the missing-backend
message for replies that are plainly not JSON at all, such as unknown
request.

### R5 (Medium): the drain thread dies silently on non-UTF8 stderr, and the tail is lost
Verified with a test program: Popen uses text=True with strict decoding.
One non-UTF8 byte (0xff) in the guardian stderr raises UnicodeDecodeError,
which is a ValueError subclass, so the except (OSError, ValueError) in
_drain swallows it, the thread exits, the deque stays empty, and every later
line, including the real cause, is lost. The startup error then goes opaque
again, the exact failure this fix was meant to kill.
Trigger: any non-UTF8 byte on guardian stderr (binary plugin output,
locale-mangled traceback, corrupt log line).
Fix: open the pipe with errors='replace' (or binary mode with manual
decode), and log if the drain thread ever exits early.

### R6 (Medium): no drain settle before the detail is composed, the tail can be empty or partial
supervise reads guard_errors immediately after stdout EOF with no wait and
no join of the drain thread, and the finally block calls
guard.stderr.close() which can discard lines still buffered in the
reader. My exact-pattern simulation showed 0 empty tails in 300 trials,
and a variant showed 1 partial tail in 200 trials, so the window is small
but real, and it grows under load on a 1.5 CPU VM.
Fix: after a failed ready check, wait for the guard process to exit, then
join the drain thread with a short timeout (for example 0.5s) before
composing the detail, and join before closing guard.stderr.

### R7 (Medium): deque maxlen 32 plus detail[-1200:] can drop the root cause
The guardian finally block prints cleanup lines after the root traceback
(for example session cleanup failed, snapshot retained), and those lines
are appended to the same deque before supervise reads it. A long traceback
plus cleanup output pushes the root-cause lines out of the 32-line window,
and the 1200-char cut can remove the exception line itself.
Trigger: a guardian death whose finally cleanup also fails, which is the
common case when the desktop is already broken.
Fix: raise the deque maxlen (for example 200) and keep a larger tail, or
keep the first lines and the last lines instead of only the last 1200 chars.

### R8 (Medium): the second gate and the mid-session guard death are still opaque
Only the ready gate got the tail treatment. The driver registration gate
raises bare RuntimeError('driver registration failed') with no detail, and
a mid-session guard death just terminates the driver with outcome 1 and no
message at all. This is the same bug class F1 fixed at gate 1, left
unfixed at gates 2 and 3.
Trigger: the guardian dies between ready and registered (indicator dies,
guard socket drops), or the guard dies mid-session. The user gets no cause.
Fix: include the guard_errors tail in the registration failure, and print
the guard death cause when guard.poll() is not None mid-session.

### R9 (Medium): the root-cause claim overstates what was proven
The log proves the profile mismatch threw at manifest_validation, but it
never proves the second drifted field would have worked. The old library
hyprglass-d086bc43 was self-consistent (hash matches name, verified), yet
nothing shows it passes liquid_available (version 1.1.1-cu.1, versionCheck
match) or the loader. If only the profile had been fixed, the loader may
have failed one step later. The old manifest pin 674441ea matches no known
optics version, and its origin is unexplained: it looks like an unrecorded
local optics edit, not the setup re-pin story in the log.
Fix: record how 674441ea arose, and either test d086bc43 acceptance or
state explicitly that the drift was two fields and only one was proven to
throw.

### R10 (Low-medium): the 30-second fresh-login gate is a single-shot race with no retry
require_fresh_login accepts only a loader started within 30 seconds of
compositor start. This login spawned at 4 seconds, but a slow boot past 30
seconds fails at fresh_login_gate and leaves the plugins unloaded for the
whole login, with no retry. Combined with R1, that failure is silent.
Fix: retry the loader once after a short delay, or add the R1 post-login
check so a missed window is noticed immediately.

### R11 (Low): no redaction in the supervise tail or in guard_reply output
visuals.py _loader_log redacts 32-hex tokens and paths, but supervise
includes the raw stderr tail in the error envelope, and guard_reply echoes
up to 120 chars of raw compositor reply. A truncated busy reply can carry
a partial session token, and the tee writes raw stderr lines unsanitized,
so ANSI escapes could spoof terminal output.
Fix: apply the same 32-hex redaction to the detail and shown strings, and
strip control characters before echoing.

### R12 (Low): the new session test cannot be independently re-run on the VM
tests/test_cursor_session.py does not compile on the VM Python 3.12
(SyntaxError, too many statically nested blocks, line 570). The new
Lifecycle test was therefore only run on the laptop. Redteam could not
re-run it here. Pre-existing, not introduced by F1, but it weakens review.
Fix: refactor the test file to compile on 3.12, or record the Python
version requirement and run it in CI on 3.14.

### R13 (Low): the lock message misleads when activation holds the lock
activate-cursor-guard.py holds cursor_session.owner_lock, so a session
attempt during live activation fails with 'another automation session is
active'. It fails closed, which is correct, but the message is wrong and
will confuse the owner.
Fix: distinguish the lock holder, or note activation in the message. Do not
change locking behavior.

## Notes on the pending live activation (plan B)

- The activation itself is the correct remedy and may proceed; the code fix
  is safe to keep because every failure path found here fails closed.
- Positive proof must include a hyprglass active check (R3), not only
  cu-cursor status and the socket. A session that starts without glass
  must be treated as a failure, not a pass.
- Do not declare the fix complete until R1, R2, R3, R4, and R5 are fixed.
  R6 to R13 should follow in the same round where cheap, and R8 in
  particular should not be left for later since it is the same bug class.

## Required fixes, in order

1. R1: login-time detection of loader failure, plus check-visuals-manifest
   in sync and setup.
2. R2: make the drift repair durable (commit or rebase the optics change,
   re-pin through refresh-visuals-manifest.py).
3. R3: gate the session on hyprglass active, or publish require-liquid so
   Native fails closed.
4. R4: guard_reply must distinguish truncated JSON from a missing backend.
5. R5: drain thread must survive non-UTF8 stderr (errors='replace').
6. R6: join the drain thread before composing the startup-failure detail.
7. R7: raise the deque limit and keep more of the tail.
8. R8: name the cause at the registration gate and on mid-session guard death.
9. R9: close the root-cause gap on d086bc43 and on the 674441ea pin origin.
10. R10: retry or visibly report a missed 30-second fresh-login window.
11. R11: redact 32-hex tokens in the tail and in guard_reply output.
12. R12: make test_cursor_session.py compile and run on the VM Python 3.12.
13. R13: correct the lock message when activation holds owner_lock.
