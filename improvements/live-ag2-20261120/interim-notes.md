# Task 3 interim notes (baseline arm in progress, G2 recovery)

## G1 baseline (8727135) DONE, SUCCESS
- Wall 90.629s (start submit 00:59:49.456 to verify observe 01:01:20.085).
- Requests: windows 1, observe 1, act 3, status 0. Act requests 3, actions 11.
- Group sizes [1, 9, 1]: the nano chain went as ONE mega-batch of 9 actions
  (type, Return, type, Return, type, Return, Ctrl+O, Return, Ctrl+X).
- OCR verified all 3 lines. 0 refusals, 0 deaths.
- Coordinator note: /tmp/ghi-chu.txt was removed by the executor during G2
  setup (per the brief, before each task), before I byte-checked it. The OCR
  quote in the summary plus the ls sighting stand as the evidence.

## G2 baseline (8727135) in progress, with incidents
- VS Code launched, File menu opened, New Text File clicked, line typed.
- Tail mega-batch [type line, Ctrl+S, type path, Return] (4 actions, seq 11):
  completed 3 of 4, then driver refusal focus_changed (Save As dialog,
  xdg-desktop-portal-gtk, stole focus mid-batch). Error verbatim:
  "session refusal: error=focus changed action=require_reobserve".
  The 4th action (Return) never ran; the typed path went into an uncertain
  state (dialog Name field showed suffix "ng-2.txt" after the retry Return,
  dialog stayed open, no file saved).
- Executor recovered per the brief: logged the refusal, listed windows,
  observed the Save As dialog, pressed Return (dialog stayed open), then
  the G2 session DIED: seq 16 windows returned accepted:false,
  request_error task_stopped; broker state failed, owner ag2-base-g2.
  Cause of the session death is NOT yet established (no error in the later
  status; the new session shows recovery active, stop_reason null).
- Executor restarted with a FRESH session (g2-restart1, generation 84f259ee),
  new lease dir, and is retrying the save carefully (observe dialog,
  navigate to /tmp, Ctrl+L location entry). A path typo on the first retry
  request (missing ag2-baseline/ segment) cost one failed call; the retry
  with the fixed path succeeded.
- /tmp/y-tuong-2.txt still absent as of 01:14. G2 wall is running long
  (started about 01:02, 30-min cap about 01:32).

## What this already shows
- The unconstrained baseline DOES batch aggressively (G1 group of 9 in one
  request), which is the behavior the grouping method is meant to discipline.
- The G2 tail batch crossed a focus change (dialog opening) and broke
  mid-batch: 3/4 completed, save failed, session died later. Whether the
  method arm avoids this (by splitting at the menu/dialog boundaries) is
  the discriminating question; the method arm will tell.

## G1 method (ab5011a) - grouping validation FIRED live, 4 rejections
- Executor attempted the full 9-action chain first (g1-full-chain), then
  re-attempted each remainder as one batch, exactly as briefed.
- Rejection 1 (full 9, [type,key,type,key,type,key,key,key,key]): ok false,
  completed 0, recoverable true. Verbatim: "action 2 is the first unsafe
  boundary before action 3; split the group after action 2 and observe
  again before the remaining actions: a terminal key or newline typing
  cannot be followed by another input action".
- Pair 1 [type, key] accepted, completed 2. Rejection 2 (remainder 7):
  identical message, completed 0. Pair 2 accepted. Rejection 3
  (remainder 5): identical, completed 0. Pair 3 accepted.
  Rejection 4 (save remainder 3, [Ctrl+O, Return, Ctrl+X]): identical,
  completed 0 (Return is terminal, must be last, Ctrl+X follows).
- Save pair [Ctrl+O, Return] accepted; file created 01:32. Exit [Ctrl+X]
  sent as a single key.
- So G1 method act requests so far: launch [1], full-9 (rejected),
  pair1 [2], rem-7 (rejected), pair2 [2], rem-5 (rejected), pair3 [2],
  rem-3 (rejected), save-pair [2], exit [1]. Accepted actions: 1 + 2 + 2
  + 2 + 2 + 1 = 10 (launch + 3 pairs + save pair + exit), plus the cat.
  Rejected actions: 9 + 7 + 5 + 3 = 24 actions in 4 rejected requests.
- Byte-check (coordinator, before G2 setup removes it): /tmp/ghi-chu.txt
  62 bytes, "Note 1: drink water.\nNote 2: read books.\nNote 3: go
  running.\n\n" (3 exact lines plus one trailing blank line from the
  third Return), sha256 66fb03fafc002bbffad2a60c9a1b9784a3f27f6ab3258b1232c1a5f4b48cd043.
- The brief predicted 5 requests with 3 rejections; actual is 4
  rejections (the save [Ctrl+O, Return, Ctrl+X] batch is a 4th boundary
  the prediction did not count separately). The mechanism is confirmed
  working and discriminating: the baseline sent the same 9-action chain
  in ONE accepted request; the method arm needed 4 rejections + 5
  accepted split requests to do the same work.
