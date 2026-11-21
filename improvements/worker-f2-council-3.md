# Council Voice 3 verdict: Worker F2 silence fix (rule + error-file plan)

Date: 2026-11-21. Reviewer: Council Voice 3 (rule + error-file plan).
Scope: the rule doc `improvements/first-visible-action-rule-20261121.md`,
the fix log `improvements/worker-f2-silence-fix-log.md`, and the error-file
plan for Part H (H2) and Part G (new G28), against the error file
`~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md` (Parts G, H, J).
Code checked: `scripts/first_action.py`, `scripts/cu.py` (act-now wiring,
`desktop_act` at line 1475, `focus` at line 541), `tests/test_first_action.py`
(21 tests). No code modified. No live driving. No commit (parent commits).

## Verdict: AMEND

The mechanism inside `act-now` is real and measured, and most findings check
out against file and line evidence. But the rule doc overclaims in three
places that matter: it calls the rule deterministic and binding for every
live run when the code only binds runs that already choose `act-now`; it
presents the 30 s and 60 s numbers as enforced when neither is enforced in
code; and the planned H2 fix line would mark a still-open think-time problem
as fixed. All six required changes below are doc or wording fixes, plus one
small recommended code hardening. None requires re-running the rehearsal.

## What checked out (verified, no change needed)

- Priority order (b): FAST, CONTINUOUS, OVERLAY VISIBLE, in that order, with
  narration explicitly NOT required. Matches the owner correction 22:21.
  Rule doc section "The rule", items 1-3, states this correctly.
- Rehearsal numbers match the log exactly: overlay 314-346 ms, batches
  0.87-2.0 s, run 1 refused in 638 ms, run 2 4/4 in 1477 ms, run 3 3/3 in
  1592 ms, run 4 5/5 in 1998 ms, run 5 1/1 in 865 ms, baseline about 330 s.
  Rule doc "Measurement" vs log "Rehearsal verdict". Consistent.
- Typing refusal fact (cu.py:1475): the exact string "screen observations
  support pointer actions only; use a window or accessibility target for
  typing" is at `scripts/cu.py:1475`. Run 1 refusal is correctly described
  as the right outcome.
- Zen urlbar finding: stated as a Zen UI behavior, not an act-now defect,
  with the Ctrl+L workaround recorded and proven by run 3. 2/2 mouse-click
  failures, 0 px click error. ZT-A owns the scenario fix. Correct.
- CLI-first focus form: `hl.dsp.focus({ window = "address:0x..." })` matches
  the repo pattern at `scripts/cu.py:541` and was proven live at 22:51:56
  (rc 0, activeWs 1). `hl.dsp.workspace` failing as a table (rc 7, log
  22:51:32) and plain string dispatch broken (G4) are both accurate.
- Log-every-event, commit-small-and-many (including the graph counts main
  only by UTC day, todolist-push via MERGE worker), and Lauren Tan
  no-cutting-steps companion rules are accurate against the owner orders
  22:40, 22:47, 22:48, 22:49 and the log 22:49-22:51 correction.
- Failure-mode division is stated clearly for three of four modes:
  guardian failure is F1's fix with F2 fallback (rule doc "What this rule
  does NOT do"); urlbar click is ZT-A; Marionette slot re-break is F3.
  See F7 for the one stale item in the division.

## Required changes

### R1. Narrow the determinism claim, or add real enforcement (finding a)

The rule doc says act-now "is the default command for a live action batch"
and "enforces the rule", and calls the rule "a deterministic rule, not a
reminder". Inside `act-now` that is true: `acquire_overlay`
(`scripts/first_action.py:68-88`) raises unless the pill is visible, `run`
returns exit 2 on overlay refusal, the session attempt has a 20 s deadline
with process-group kill, and fallback runs only when
`is_session_start_failure` returns true (tests cover ready, fast-fail,
timeout, and never-replay-act-failure). But nothing makes `act-now` the
default: `scripts/cu.py` contains no overlay reference outside the act-now
wiring (lines 2311, 2491-2493). `act` and direct `desktop_act` remain callable
with no overlay gate, so an agent that calls `act` out of habit still runs
invisibly, exactly tonight's failure. The rule is therefore deterministic
inside one command and still a reminder at the point where the agent picks
the command. Required: either add enforcement (for example `act` refuses
without a live overlay holder, or `act-now` becomes the only entry point
for live batches), or change the doc to state the gap honestly: "act-now
enforces the rule when used; adoption is by brief until entry-point
enforcement lands." The doc must not claim it "binds every live run" until
one of those two is true.

### R2. H2 must be marked PARTIALLY fixed, not fixed (finding d)

The planned update ("H2 fix line updated from CHUA XAC DINH to the act-now
path", log section 4) would mislabel the error file. H2 as written is about
slow DECISIONS: "Muse/Codex mất thời gian bất thường lâu để đưa ra quyết
định (think time quá dài)", with suspected causes "prompt quá dài, context
quá lớn, hoặc model reasoning quá sâu". F2 fixes only the visible-silence
slice of that (R1-R4: no fast path, swallowed guardian error, overlay
untied from action, serial chain). It does not shorten think time, prompts,
or context, and it adds no think-time measurement. The error file itself
confirms H2 is still open: J10 says "H2 think-time van OPEN nhung todolist
2.3.1 da tick", the 2.3.1 tick was scripted only (think null by design), and
only an agent-driven run with real think instrumentation closes H2
(todolist 4.18). Marking H2 fixed would also contradict J10 in the same
file. Required: use the exact H2 fix-line wording below, which splits the
fixed part from the open part.

Recommended exact H2 fix line (paste as the new "Cách sửa" for H2):

"Cách sửa (cập nhật 21/11, Worker F2): PHẦN ĐÃ SỬA: im lặng trước hành động
đầu tiên đã hết nhờ `computer-use act-now` (overlay lên trong 314-346 ms,
batch xong trong 0,87-2,0 s trong rehearsal ZT-00 22:44-23:01 21/11, so với
gần 5 phút im lặng 22:11:30-22:17). PHẦN CÒN MỞ: thời gian suy nghĩ (think
time) từng bước vẫn chưa được đo và chưa được rút ngắn; nguyên nhân nghi ngờ
(prompt dài, context lớn, reasoning sâu) chưa được kiểm chứng. Cần đo think
time thật trên run agent-driven (xem J10, todolist 4.18). Trạng thái: SỬA
MỘT PHẦN, chưa xong hẳn."

### R3. Correct the FAST and CONTINUOUS enforcement claims (findings a, b)

- The 30 s target is not enforced: `FIRST_VISIBLE_ACTION_TARGET_MS = 30000`
  is defined at `scripts/first_action.py:57` and referenced nowhere else
  (grep count 1 in the file). The envelope carries no pass or fail verdict
  against the target. The rehearsal beat it by a wide margin, but the doc
  must not present 30 s as a code-enforced bound.
- The 60 s CONTINUOUS rule has no enforcement at all: `act-now` runs one
  batch, nothing watches gaps between batches or fails a run after 60 s
  idle. It is a stated expectation measured post-hoc from the JSONL
  timestamps, not a gate.
- The design note overstates the ordering: the log section 4 and the rule
  doc say "overlay + first move happen BEFORE session/observe diagnosis".
  In `run()` the order is overlay acquire, fresh observation, session
  attempt (up to the 20 s deadline), then the move. Only the overlay
  precedes diagnosis; the first pointer move waits for the session attempt
  to resolve or time out. Worst case first move is about 20 s plus capture
  time, still under 30 s but with no enforced margin. Required: fix the
  ordering sentence to "overlay first; the move follows as soon as the
  session attempt resolves or times out (deadline 20 s)", add a target
  verdict to the envelope or drop the "enforced" wording for 30 s and 60 s,
  and record a gap watchdog as follow-up if CONTINUOUS is to be enforced.

### R4. Correct the typing-refusal exit code and state the precondition (finding e)

The rule doc section "Typing needs a window observation" says "act-now
refuses loudly (exit 2)". That is wrong for this refusal. Exit 2 is only
the overlay-unavailable refusal (`run` returns 2 in the acquire except
branch). A typing batch on a screen observation raises ValueError from
`desktop_act` (`scripts/cu.py:1475`) inside the fallback branch, where there
is no try/except around the call, so it propagates as an uncaught exception
(exit 1 with traceback) after the finally block prints the envelope. It is
loud, but it is not exit 2 and not a clean refusal. Required: correct the
exit code in the doc, and state the precondition the 30 s guarantee depends
on: a typing batch given a screen observation is refused, not executed, and
the caller must re-run with a window observation. Recommended code
hardening (not required for GO): catch the `desktop_act` refusal in the
fallback branch and return exit 1 with a clean JSON envelope instead of a
traceback. The underlying fact (screen obs cannot type, window obs can) and
the follow-up (auto-capture a window observation, not implemented) are
correct as written.

### R5. Complete the CLI-first companion rule against J23 (finding c)

The focus and workspace-table claims are verified (see above), but the
bullet says "Open the Omarchy menu and switch workspaces by COMMAND" without
giving the menu command, and it implies workspace switching by command is
solved. J23 in the error file, written after the rule doc, says it is not:
`hl.dsp.workspace` methods are swap_monitors, rename, move, change_id,
toggle_special, with no goto or switch; `hl.dispatch("workspace", "1")`
also fails; the exact launcher command from config is
`omarchy-menu toggle root`. Required: add the launcher command to the
bullet, state that switching workspaces by command is still unsolved except
via the focus side effect (focusing a window pulls its workspace), and cite
J23. Related: the log entry 22:51 lists "candidates: goto/switch/change"
for the workspace sub-function; J23 rules those out, so add a one-line
supersession note in the log rather than leaving the candidates open.

### R6. Add G28 as scoped, and give the urlbar finding its own number (finding e)

Yes, add G28 for the screen-observation typing refusal. It is correctly
scoped as a design constraint of `desktop_act`, not an act-now defect, and
the rule doc section matches it (caller must pass a window observation;
auto-capture follow-up not implemented). Numbering is clean: G25 and G26 do
not exist in the error file (the list jumps from G24 to G27), so G28 is the
next number with no collision. But the urlbar-click finding also needs a
home and must not be folded into G28: the log says "Record in the error file
as a new finding (H3 family...)". Required: add G29 for the urlbar click
with ZT-A as owner, and cross-reference H3. Recommended exact texts:

G28:

"### G28. Screen observation không gõ phím được, act-now từ chối batch có typing (22:53 21/11)
- Lỗi: batch có type/key chạy trên screen observation bị `desktop_act` từ
chối: "screen observations support pointer actions only; use a window or
accessibility target for typing" (`scripts/cu.py:1475`). Rehearsal act-now
run 1 (22:53:57) bị từ chối trong 638 ms, hoàn thành 0/4, overlay đã lên
trong 356 ms. Đây là giới hạn thiết kế của `desktop_act`, không phải lỗi
của act-now.
- Cách sửa: batch nào có gõ phím phải dùng WINDOW observation
(`observe --window 0x...`). Follow-up chưa làm: act-now tự chụp window
observation của cửa sổ đang focus khi batch có typing mà observation đưa
vào là screen observation."

G29:

"### G29. Click chuột vào urlbar Zen không focus ô địa chỉ, gõ phím đi đâu mất (22:55-23:00 21/11)
- Lỗi: click chuột vào ô urlbar/search trên cùng sidebar của Zen chạm đúng
tọa độ (cursorpos 2629,974, sai số 0 px) nhưng KHÔNG focus ô nhập URL; gõ
phím sau đó đi đâu mất, Enter không điều hướng. Gặp 2/2 lần (run 2 không
chờ, run 4 chờ 500 ms sau Ctrl+N). Đây là hành vi UI của Zen, không phải
lỗi act-now (act-now đưa click đúng vị trí).
- Cách sửa: focus urlbar bằng Ctrl+L rồi gõ URL và Enter (đã chứng minh:
run 3, Example Domain load được). ZT-A phải sửa kịch bản ZT-00 bước 4
(không dùng click chuột vào ô địa chỉ nữa). Xem thêm H3 (click chạm đúng
nhưng không có tác dụng)."

## Minor notes (not required for GO)

- M1. Fallback predicate is string matching: `is_session_start_failure`
  matches 'session guardian startup failed', 'Expecting value', and
  'cursor guard' in the session output. If F1 rewords the guardian error,
  the fallback silently stops matching and act-now reports failure instead
  of falling back. Consider a structured error or a comment pinning the
  strings. Tests cover the current strings, so this is robustness, not a
  defect.
- M2. Stale suspicion in the log: the 22:56:33 entry suspects the act-now
  Ctrl+N or the eval session DELETE caused the Marionette re-break. J22
  (F3) later pins it to close3 DELETE of a BiDi-navigated tab, and F2's own
  Example Domain tab was closed by Ctrl+W at 23:01:21 and verified gone, so
  F2's tab is not the zombie. Add a one-line supersession note so the log
  does not keep blaming act-now's Ctrl+N.
- M3. R6 in the log body still says "Cause UNKNOWN" while the update section
  at the end says SOLVED (self-deleting shim from Redteam Y13r2, VMFIX
  c16dd4e). Edit R6 in place to KNOWN so a reader who stops at section 2
  does not carry the stale unknown.
- M4. The urlbar finding rests on n=2 in one Zen layout at window coords
  (120,60). That is enough for a finding with ZT-A as owner, but ZT-A
  should confirm generality before the scenario is rewritten around Ctrl+L.

## Scope check (finding f)

Covered by F2 with a stated owner: session guardian failure (F1 fixes,
F2 falls back and logs), screen-obs typing refusal (F2 caller rule plus
future auto-capture), urlbar click (ZT-A scenario fix), Marionette slot
re-break (F3). The rule doc states each division. The one division gap is
M2 above (the log's stale suspicion vs J22). Part J is accounted for: J4
is the guardian failure, J5 is the silence itself that this rule fixes,
J1/J2/J3/J22/J24 are F3's Zen and Marionette scope, J21/J23 are the
menu and workspace CLI scope partly covered by R5, J7 is the resolved R6
incident, J10 is the still-open H2 think-time measurement cited in R2.

## What must change before GO

1. R1: narrow the determinism claim or add entry-point enforcement.
2. R2: use the exact H2 partial-fix wording above, not "updated to the
   act-now path".
3. R3: fix the D2 ordering sentence and the 30 s / 60 s enforcement wording.
4. R4: correct the typing-refusal exit code and state the window-obs
   precondition.
5. R5: add `omarchy-menu toggle root` and the J23 unsolved-workspace-switch
   note to the CLI-first bullet.
6. R6: add G28 and G29 with the exact texts above.
