# G31 near-miss draft, 2026-11-22

Status: DRAFT. Every number in this file is assignment-given, from coord/clone2.md (batch 9 task 3, commit e04a16a). Nothing here was independently measured. Council and redteam to review.

## Incident

The coordinator messaged clone2 directly with the computer-use mouse at 03:53:30. Sent in 4 minutes 3 seconds, 1/1.

## The error

When reading the screenshot to locate the input field, its eye read 45 px too high. It guessed (307,1085). The visual_grounding tool gave (306,1130). Difference: 1130 minus 1085 is 45 px vertically, 1 px horizontally. Same error type as CL1-MSG before, per the assignment.

It caught the error before clicking, thanks to the grounding tool.

## What happened after

Click point (306,1130). Cursor after click (1288,1144). It typed, then checked the text in clone2's input field (clone1's input still empty), pressed Enter once to send, and the blue bubble with the full text appeared in the thread.

## Conclusion (assignment-given)

The grounding tool is the fix, reading by eye is the error. A tool-measured coordinate must replace the eye guess before every click, and the click must be verified after it lands.

## Open inconsistencies, UNRESOLVED

### 1. Cursor distance does not match the given coordinates, UNRESOLVED

The assignment says the cursor after click is "2px from the click point". The given coordinates are click point (306,1130) and cursor after click (1288,1144). The distance between them is about 982 px (dx 982, dy 14), not 2 px. Both coordinate pairs are recorded exactly as given. No reconciliation is invented here, no different coordinate space is guessed, no typo is assumed.

A repo search found no log or screenshot record of the 03:53:30 message to check against. The only sources are the assignment text itself (coord/clone2.md line 800) and unrelated 03:53 hits elsewhere in the repo. This inconsistency stays open for council and redteam.

### 2. CL1-MSG comparison is unverified from the repo, UNRESOLVED

The assignment says this is the same error type as CL1-MSG before. The repo's only CL1-MSG record is in docs/clone2-watchdog-log.md, entry 00:58 on 2026-11-22: "CL1-MSG log: message to clone1 NOT sent after 3 act-now batches". That record describes a message delivery failure, with no eye-read error and no coordinate error described. No repo record links CL1-MSG to a 45 px too high eye read. The comparison is recorded here as assignment-given, not as repo-verified. Council and redteam to decide whether the comparison stands or the CL1-MSG reference is a different incident.

## Numbers, all assignment-given

- Message time: 03:53:30, sent in 4 minutes 3 seconds, 1/1.
- Eye guess: (307,1085).
- Grounding tool result: (306,1130).
- Eye error: 45 px too high.
- Click point: (306,1130).
- Cursor after click: (1288,1144).
- Text check: text present in clone2's input field, clone1's input still empty.
- Send: Enter pressed once, blue bubble with the full text appeared in the thread.
