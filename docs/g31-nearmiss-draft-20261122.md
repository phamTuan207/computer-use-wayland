# G31 near-miss draft, 2026-11-22

Status: DRAFT. Every number in this file is assignment-given, from coord/clone2.md (batch 9 task 3, commit e04a16a). Nothing here was independently measured. Council and redteam to review. Fix pass applied: sections 1 and 2 rewritten from the real CL1-MSG records on origin/todolist-push, conclusion downgraded to a hypothesis, the 2 px warning carried into the narrative and the Numbers table, "1/1" flagged as undefined.

## Incident

The coordinator messaged clone2 directly with the computer-use mouse at 03:53:30. Sent in 4 minutes 3 seconds, 1/1. "1/1" is undefined: no source says what it counts (1 of 1 attempts, 1 message of 1, or something else). It is recorded here exactly as given, with no meaning assigned.

## The error

When reading the screenshot to locate the input field, its eye read 45 px too high. It guessed (307,1085). The visual_grounding tool gave (306,1130). Difference: 1130 minus 1085 is 45 px vertically, 1 px horizontally. The assignment calls this the same error type as CL1-MSG before. That comparison is contradicted by the repo evidence, see section 2.

It caught the error before clicking, thanks to the grounding tool.

## What happened after

Click point (306,1130). Cursor after click (1288,1144). WARNING: those two points are about 982 px apart (dx 982, dy 14), not 2 px as the assignment claims. The discrepancy is unresolved, see section 1. The claim that the click landed at (306,1130) is itself unverified: after a click the pointer stays at the click point unless moved, and no move is recorded, so a cursor 982 px away means either the click did not land at (306,1130), the pointer was moved afterward (unrecorded), or one of the two coordinates is wrong.

It typed, then checked the text in clone2's input field (clone1's input still empty), pressed Enter once to send, and the blue bubble with the full text appeared in the thread.

## Conclusion (assignment-given)

The grounding tool is the fix, reading by eye is the error.

## Draft hypothesis (drafter-added, NOT assignment-given)

Hypothesis, not a rule: a tool-measured coordinate might replace the eye guess before a click, and the click might be verified after it lands. This is a hypothesis only. A single uncorroborated near-miss with internally contradictory coordinates (the cursor is 982 px from the click point, not 2 px) cannot carry a universal rule. If the click point (306,1130) is wrong, the "tool was right" story collapses, and with it this hypothesis. The assignment prescribes nothing about replacing the eye guess "before every click" and says nothing about verifying the click after it lands; the earlier draft sentence stating that as a rule has been removed from the assignment-given conclusion.

## Open inconsistencies, UNRESOLVED

### 1. Cursor distance does not match the given coordinates, UNRESOLVED

The assignment says the cursor after click is "2px from the click point". The given coordinates are click point (306,1130) and cursor after click (1288,1144). The distance between them is about 982 px (dx 982, dy 14), not 2 px. Both coordinate pairs are recorded exactly as given. No reconciliation is invented here, no different coordinate space is guessed, no typo is assumed.

Consequence of the 982 px gap: after a click the pointer stays at the click point unless moved, and no move is recorded. So a cursor 982 px from the click point means either the click did not land at (306,1130), the pointer was moved afterward (unrecorded), or one of the two coordinates is wrong. If the click point is wrong, the "tool was right" story collapses, and with it the conclusion. The click-landing claim is itself unverified.

A repo search found no log or screenshot record of the 03:53:30 message to check against. The only sources are the assignment text itself (coord/clone2.md line 800) and unrelated 03:53 hits elsewhere in the repo. This inconsistency stays open for council and redteam.

### 2. CL1-MSG comparison is contradicted by the repo evidence, UNRESOLVED

The repo's only independent record describing what CL1-MSG was is on origin/todolist-push, not on main: improvements/worker-cl1msg-log.md (commit 334cf69, the full worker log of the three failed send batches) and improvements/worker-cl1msg2-log.md (commits 682d061 and dd5b0f5, the follow-up retry with a ground-truth pointer probe). The string CL1-MSG also appears in coord/clone2.md line 800, but that is the assignment text itself, not an independent record. The one-line entry in docs/clone2-watchdog-log.md (00:58 on 2026-11-22, "CL1-MSG log: message to clone1 NOT sent after 3 act-now batches") is only a summary pointer to the worker log, not the record. The draft author searched main only and missed the coordinator's branch; this section is rewritten from the real records.

What CL1-MSG actually was, from worker-cl1msg-log.md: three act-now batches at 00:49, 00:51 and 00:55, all reported ok or completed, with zero visible effect on clone1's Brave thread. Batch 1 silent no-effect, batch 2 refused (screen-observation fallback), batch 3 atomic with the given window observation used, 7/7 completed, still no effect. The worker read a possible coordinate offset from two after-captures: batch 3, "the cursor at window coords about (216,1073), about 50px down-left of the input click point (250,1037). Batch 1's after-capture showed the SAME about 50px down-left offset. Two independent after-captures agree, so this is a systematic offset, not a reading error."

The follow-up probe in worker-cl1msg2-log.md (probe 01:20, three clicks with hyprctl cursorpos after each) refuted that reading: "P1 (300,960): expected global (2833,1874). CURSORPOS 2833, 1874. EXACT, 0px error." "P2 (750,1150): expected (3283,2064). CURSORPOS 3282, 2063. Off by (-1,-1), 1px, rounding." Its verdict: "There is NO systematic about 50px down-left offset. CL1-MSG's offset reading was an artifact of reading the tiny cursor arrow in JPEG after-captures (it hedged itself: pixel reading +-30-50px error). The 3 send failures must have another cause: click-focus consumption, type target, or Enter/send, NOT coordinates." And: "CL1-MSG's 3 failures are a DIFFERENT fault (its envelopes were ok, actions executed, text never entered)." The retry later confirmed it: a 9/9 executed send left the input empty, and the probe verdict stands, clicks exact (0 px, 1 px). The remaining suspect is the TYPE action on that specific Brave chat input, unproven.

So the assignment's "same error type as CL1-MSG" fails in the causal sense. CL1-MSG's apparent coordinate error was proven to be a misreading artifact, not a real grounding error, and its failures had a different cause (text never entered despite executed actions). The 03:53:30 incident claims a real 45 px eye error that the tool corrected. Those are not the same error type. The comparison does not stand as an endorsement; it is recorded here as contradicted.

Irony, stated plainly: CL1-MSG's about 50 px was itself a JPEG eye-reading artifact, the same failure mode the draft's conclusion claims the tool fixes. Nothing rules out that the 45 px eye error is also a reading artifact rather than a real error, since the tool point (306,1130) was never independently verified either. The 982 px cursor gap in section 1 makes that doubt concrete: if the tool point is wrong, the "tool was right" story collapses.

## Numbers, all assignment-given

- Message time: 03:53:30, sent in 4 minutes 3 seconds, 1/1. WARNING: "1/1" is undefined in every source; no meaning is assigned here.
- Eye guess: (307,1085).
- Grounding tool result: (306,1130).
- Eye error: 45 px too high.
- Click point: (306,1130). WARNING: the cursor after click is about 982 px away, not 2 px; the click-landing claim is unverified, see section 1.
- Cursor after click: (1288,1144). WARNING: about 982 px from the click point (dx 982, dy 14), contradicting the assignment's "2px from the click point"; unresolved, see section 1.
- Text check: text present in clone2's input field, clone1's input still empty.
- Send: Enter pressed once, blue bubble with the full text appeared in the thread.
