# Council Voice 2 (live safety) verdict on Worker F1 guardian fix

Verdict: AMEND.

The live activation may proceed only after every numbered precondition in
section 5 is met, in order. The code fix is sound. The root cause chain is
verified live. The remaining risk is not the diagnosis, it is the live
operation itself: two in-process plugin loads into a compositor that has been
alive since 15:17, with the owner asleep and no one able to recover a crash by
hand. The preconditions below close the holes I found. Do not proceed on a GO
reading of this file. This is an AMEND.

## 1. What I verified independently (read only, no live changes)

All live checks were read only queries over SSH. Nothing was loaded, started,
driven, or committed by this review.

- Commit 5033c9d read in full. Four files, code plus tests only.
- Commit 708bef0 log read in full (improvements/worker-f1-guardian-fix-log.md).
- Live Hyprland is 0.57.2, commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947,
  abiHash 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6.
  The abiHash exactly matches the installed manifest abi, and the commit
  exactly matches the PIN in scripts/activate-cursor-guard.py:14.
- Live plugin list is hyprbars 1.0 only. The setup baseline gates pass.
- Installed manifest pins library hyprglass-199153aea84a833d86f3eee21708e186c5a722c52259397735898b52f86df07f.so,
  cursor guard cursor-guard-06712eafb74c15297f7c63cdd2ebdb752c1026e988660bb0c319ee1bb7f2c800.so,
  profile_sha256 9a15163491b543dde09c8388a8faf01f9b491c831647320ce2949d5737d8993c.
- Optics sha256 is 9a151634 in both the installed tree and the laptop repo.
  The two manifests are byte identical (diff empty). The drift repair is
  confirmed on disk.
- Loader log visuals.jsonl last record (time 1795275379) fails at stage
  fresh_login_gate, not manifest_validation, for the current instance
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825. The loader now
  passes manifest_validation. The two earlier records for this instance and
  the previous instance failed at manifest_validation, as the F1 log claims.
- Both plugin .so files re-checked live just now: ldd reports 0 not found for
  hyprglass-199153ae and for cursor-guard-06712eaf.
- hyprctl configerrors is empty right now.
- No session is active: no /run/user/1000/agent-computer-use/ directory, no
  session.json in the installed state dir. Only the relay (PID 1821) is
  running, no other computer-use process.
- Installed copies of scripts/activate-glass.py, scripts/activate-cursor-guard.py,
  and scripts/plugin_inventory.py are byte identical to the laptop repo copies.
  scripts/indicator.py is NOT identical: the installed copy is newer (metrics,
  label command, capture nesting). The liquid gate logic itself is identical
  in both copies, so the activation gates are unaffected. See finding F7.
- VM repo optics sha256 is 9a151634, current. The VM repo has no visuals.json
  (gitignored local state), which matches the b2afcd1 commit message.
- Zen was restarted by F3: old PID 27958 is gone, new PID 426338, about 8
  minutes old at check time, with remote debugging and marionette up. Live
  clients are 4 windows, including a Zen window titled Offline Whiteboard App.
  The tab layout and coordinates from the 22:39 negative test are stale.
- scripts/activate-glass.py reload path: hyprland.lua line 54 dofiles
  native/visuals-login.lua. On a config reload the loader file runs again. If
  hyprglass 1.1.1-cu.1 is loaded it applies the optics file directly, else it
  registers a hyprland.start handler that does not fire mid session. The reload
  step therefore applies optics from the LAPTOP REPO copy of
  native/hyprglass-local-optics.lua, not the installed copy. Both are 9a151634
  now, so this is safe tonight, and it is a second reason the drift repair had
  to cover the laptop repo copy. See finding F6.

## 2. The code fix (5033c9d): sound, narrow, live proven

- scripts/cursor_theme.py:99-113 (guard_reply): catches JSONDecodeError,
  decodes bytes and bytearray as UTF-8 with replace before formatting, and
  raises a RuntimeError naming the reply and the remedy (activate-glass.py
  plus activate-cursor-guard.py, or re-run visuals.py). The bytes path matters
  because the guard socket passes a bytearray. Correct.
- scripts/cursor_session.py supervise: pipes the guardian stderr, drains it on
  a daemon thread into a deque of 32 lines, tees every line to the supervisor
  stderr as it arrives, and includes the tail (last 1200 chars) in the
  startup failure error. The tee matters: the first version swallowed the
  hotkey warning and broke a test, and the fix preserves it. Correct.
- Live negative test at 22:39 proves the envelope now names the cause
  (unknown request, backend may not be loaded) where 22:19 gave only the bare
  message. This is the fix working as designed.
- New tests cover the str, bytes, and bytearray paths and the unloaded backend
  lifecycle case (driver never runs, no session.json). Good.
- Minor verification gap, not a safety issue: tests/test_cursor_session.py
  does not compile on the VM Python 3.12 (SyntaxError, too many statically
  nested blocks, line 566, pre-existing, file unmodified). The new Lifecycle
  test therefore never ran on the VM. It ran on the laptop Python 3.14.10
  (37 tests OK after the tee fix). The VM suite gap should be recorded, not
  treated as a pass.
- Minor code note: supervise cleanup calls guard.stderr.close() after
  guard.wait(). If the drain thread is mid iteration this can raise inside the
  thread, but the thread catches OSError and ValueError, so it is benign.

## 3. The drift repair: right direction, incomplete as a durable fix

The repair (copy installed optics plus manifest over the laptop repo copies)
was the right call, and it is verified. The laptop repo sits at detached HEAD
56f5af4 with uncommitted changes, so force syncing it to b2afcd1 would have
destroyed uncommitted work. The installed tree is the setup published state,
so copying from installed to repo is the correct direction. The sha256 proof
and the loader now failing at fresh_login_gate instead of manifest_validation
confirm it worked.

What is still wrong, and why it must not be called fixed:

- Both repaired files are gitignored local state, so the repair is invisible
  to git. The next sync, install, or checkout touching these files silently
  reintroduces the drift, and nothing will warn anyone.
- The loader failure is silent by design: hl.exec_cmd redirects child output
  to /dev/null and never records the exit code. The only record is the jsonl
  log. The same failure mode will recur on the next optics change unless the
  re-pin becomes part of setup or sync.
- The same drift class is live right now in scripts/indicator.py: the
  installed copy is newer than the laptop repo copy. A repo to installed sync
  would regress it. The repo and the installed tree must be reconciled as a
  follow up, not assumed in sync.
- F1 log note: the laptop manifest profile_sha256 674441ea matched no known
  optics version. That value was never explained. It suggests a manual edit or
  a partial re-pin at some point. Worth one line in the follow up, not a
  blocker tonight.

## 4. Findings: holes in the live activation plan

F1. Blast radius of a plugin load crash (activate-glass.py:55-57,
activate-cursor-guard.py:38-40). hyprctl plugin load dlopens the .so inside
the compositor process. A segfault in plugin init kills Hyprland PID 1515
outright, and with it every window: Zen (F3 restored, PID 426338), the
Offline Whiteboard App client, and any unsaved work. There is no sandbox, no
pre crash snapshot, and no documented auto recovery. Mitigations that lower
but do not remove this risk: exact ABI match (verified live), ldd 0 not found
(re-verified live), and the strongest evidence, these exact binaries loaded
successfully before on instance 1795086072 (glass 199153ae, guard 06712eaf,
loader stage complete). Same build, same ABI, same files. Residual risk is
low but nonzero and unrecoverable while the owner sleeps. This is why the
activation needs the preconditions, not a bare GO.

F2. activate-glass.py takes no owner lock. Its main() runs with no
cursor_session.owner_lock, unlike activate-cursor-guard.py main() (which holds
the lock) and visuals.py login() (which holds the lock). Two concurrent
activate-glass runs, or a manual run racing a login loader run, can both pass
the pre load ownership check (activate-glass.py:44-53) and both issue plugin
load. The second load of an already loaded plugin is undefined in these
scripts, and a retry after a partial success fails closed at setup_baseline
with the misleading message unsupported plugin inventory
(plugin_inventory.py:38-44). activate-glass.py also has no CU_SESSION_TOKEN
or SNAPSHOT check, unlike the guard activation (activate-cursor-guard.py:16-17).
Precondition 4 closes this.

F3. Time of check versus time of use on the .so files. The digest is computed
from file bytes (activate-glass.py:17-20, activate-cursor-guard.py:22-25) and
the file is then loaded by path, with no re-hash after load. A concurrent
writer (another sync, another worker copying plugins) could swap bytes between
the hash and the load. Files are 0600 and user owned, so the writer would be
same user, but several workers share this laptop tonight. Also
assert_glass_added and assert_guard_added (plugin_inventory.py:71-88) verify
only name, author, and version, not the loaded handle sha. A different build
carrying the same version string would pass. Preconditions 2 and 4 close this
by re-hashing immediately before load and by excluding concurrent writers.

F4. Half loaded rollback gap. If plugin load returns ok but the config reload
refuses (activate-glass.py:59-61), or wait_for_profile times out after 8s
(scripts/activation_checks.py:6-22), glass stays loaded and the script exits 1
with no rollback and no documented recovery. There is no unload path by
design. A retry of activate-glass then fails at the baseline check with a
misleading message. If glass loads but the guard load is refused
(activate-cursor-guard.py:38-42), the state is glass only: sessions still
fail, but now with the clear error, and a guard only retry is valid. The plan
must define the half state recovery before starting. Precondition 5.

F5. Hyprctl timeout leaves state unknown. activate-glass.py query uses
timeout 5, activate-cursor-guard.py uses timeout 10. If hyprctl hangs (busy
compositor) the call raises TimeoutExpired and the script exits 1, but the
load may or may not have happened. A blind retry could double load.
Precondition 5: re-query the plugin list before any retry, never blind retry
a load.

F6. The reload applies the laptop repo optics, not the installed optics.
hyprland.lua:54 dofiles visuals-login.lua, and on reload that file applies
native/hyprglass-local-optics.lua from the laptop repo when glass is loaded.
Tonight both copies are 9a151634, so this is safe. But it means the drift
repair had to cover the laptop repo copy (it did), and any future drift in the
laptop repo optics would be applied by the reload even if the installed tree
were correct. This is a second durable reason for the re-pin follow up in
precondition 8.

F7. Indicator drift. The installed scripts/indicator.py is newer than the
laptop repo copy (metrics, label command, capture nesting). The liquid gate
logic is identical, so activation is unaffected tonight. But a future
repo to installed sync would regress the installed copy. Reconcile as a
follow up. Precondition 8.

F8. Proof click coordinates are stale and the target is unknown. F1 plans one
harmless click on the already selected tab row. Zen was restarted by F3 since
the 22:39 test (old PID 27958 dead, new PID 426338), and a live client is an
Offline Whiteboard App window. Coordinates from before the restart are
meaningless. A click at stale coordinates can hit the wrong tab, the tab close
button, or start a tab drag. If the active tab is the whiteboard with unsaved
content, even a correct tab row click is not provably harmless. Also F3 may
still be restoring Zen: two drivers on the same Zen would fight over focus and
cursor. Owner order 22:45 reinforces this: open the Omarchy menu and switch
workspaces by COMMAND (hyprctl dispatch, hl.dsp form), never by clicking
workspace or menu buttons on the bar, CLI first and mouse last. That order
followed a stray click at about 22:44 that opened the Omarchy menu, worker
unidentified. Clicks are misfiring tonight, so the proof must contain at most
the one planned click and no bar clicks at all. Precondition 6.

F9. Shader warm up timing. After glass loads, wait_for_profile allows 8s, and
the guard activation requires liquid_available with shaders ready or pending
(scripts/indicator.py liquid_available, ready=False path). First use shader
compilation can exceed 8s. A first guard refusal of accepted glass backend is
unavailable may then mean only slow shaders, not a bad load. Retry after a
longer wait is the recovery. Precondition 5.

F10. No crash contingency is written down. If the compositor dies mid load,
there is no agreed recovery: relaunching Hyprland, relaunching Zen, and
deciding what to do about unsaved work are all owner decisions, and the owner
is asleep. The plan must state in advance that a crash means stop, report to
the parent at once, and relaunch nothing blindly. Precondition 7. Note in
mitigation: Zen was already restarted once tonight by F3 and its tabs came
back, so tab restore works, but unsaved in page state (notably the whiteboard)
is not proven restorable.

## 5. Preconditions (numbered, all required before the live activation)

1. Sequence after F3. Confirm F3 restore is complete and signed off, Zen PID
   is stable, and no other worker is driving the screen, holding owner_lock,
   or running a session. One operator runs the whole activation plus proof.
   No parallel driving at any point.
2. Pre-flight re-verification in the same minute as the load: hyprctl version
   abiHash equals the manifest abi; plugin list is exactly hyprbars 1.0;
   configerrors empty; no session.json, no CU_SESSION_TOKEN in the
   environment, no agent-computer-use socket directory; sha256 of both .so
   files matches their filenames and the manifest pins; ldd on both files
   reports 0 not found.
3. Run the installed tree copies of activate-glass.py and
   activate-cursor-guard.py (verified byte identical to the laptop repo for
   these two scripts and for plugin_inventory.py). Pass the abi from the
   manifest and profile-sha256 9a151634. Run glass first, then guard, in that
   order, with no other step between them.
4. Hold owner_lock across the whole glass plus guard sequence, so no second
   activation, login loader run, or session can interleave. Confirm no other
   process is writing to the plugins directory and no sync-installed run is in
   progress or started during the sequence.
5. Half state recovery, agreed before starting. If glass loads but the reload
   refuses or wait_for_profile times out, do not re-run activate-glass.
   Capture configerrors and hyprglass status, verify glass is healthy, then
   run the guard activation alone. If the guard load is refused, retry the
   guard alone after re-checking liquid_available with a longer wait (slow
   shaders, finding F9). If any hyprctl call times out, re-query the plugin
   list before any retry. Never blind retry a load.
6. Proof plan, corrected. Take a fresh observe first and identify the active
   tab from that observe only. Only then, one single click at the center of
   the already active tab, no drag, no double click. If the active tab is the
   Offline Whiteboard App or any tab with unsaved state, skip the click and
   verify with cursorpos plus observe only. Any workspace or menu navigation
   during the proof is by hyprctl command only, never by clicking bar buttons
   (owner order 22:45, fastest path first, CLI before mouse). Verify with
   cursorpos and a second fresh observe that the active tab is unchanged. Stop
   cleanly and verify the desktop is clean (pill gone, no stray processes,
   plugin list unchanged).
7. Crash contingency, agreed before starting. If the compositor dies or the
   desktop freezes during either load, stop, report to the parent at once, and
   relaunch nothing blindly. Recovery of the session is the parent decision
   with the owner, not a field decision while the owner sleeps.
8. Drift durability, tracked as a follow up (not a precondition to tonight).
   Record the repair in the F1 log with file paths and shas. Open a follow up
   to add a re-pin check to sync-installed or setup (manifest profile_sha256
   must equal sha256 of the optics file at deploy time), to reconcile
   scripts/indicator.py between the installed tree and the laptop repo, and to
   make the silent loader failure visible. The root cause is not durably fixed
   until that follow up lands.

## 6. Summary

Root cause verified end to end and the code fix is good. The drift repair was
the right repair and it is proven on disk and in the loader log. The live
activation itself is the risky step, and only because a plugin load crash
kills the whole compositor with the owner asleep. The gates in the activation
scripts are real (filename sha256, profile provenance, ABI match, inventory
baseline, load must return ok, post load assertions), and the prior successful
load of these exact binaries into this same Hyprland build is the strongest
safety evidence. The holes are the missing lock on activate-glass, the
time of check gap on the .so files, the undefined half loaded recovery, the
stale proof coordinates, and the silent drift recurrence. All are closed by
preconditions 1 to 8. Meet them, then proceed.
