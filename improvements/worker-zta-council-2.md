# Council Voice 2: composite coverage verdict

Reviewer: Council Voice 2 (composite coverage).
File reviewed: `zen-ordinary-user-tests-20261121.md`, branch todolist-push.
Date: 2026-11-21. Scenario file NOT modified.

## Verdict: AMEND

No scenario is missing a channel entirely on paper, so this is not BLOCK.
But the four-channel claim does not survive inspection in 8 of 11 scenarios:
one channel is token, mislabelled, conditional, or a no-op in each case
listed below. Fix the numbered changes, then GO. ZT-B must not run the
file as written and claim composite coverage.

## Per-scenario table

| Scenario | DOM | CLI | Mouse | Keyboard | Result |
|---|---|---|---|---|---|
| ZT-00 | real | mixed, curl vacuous | MISSING, mislabelled | real | AMEND |
| ZT-01 | real | real control + token hyprctl | real, no rect on step 4 | real | AMEND, minor |
| ZT-02 | MISLABELLED, find bar is not DOM | token hyprctl only | no-op click | real | AMEND |
| ZT-03 | real | token hyprctl only | conditional, vision-based | real | AMEND |
| ZT-04 | MISLABELLED, library/star are chrome not DOM | decoration, hyprctl twice | real, chrome coords | real | AMEND |
| ZT-05 | real but same title x3 | real, strongest hyprctl use | move + no-op click | real | AMEND, minor |
| ZT-06 | thin, disjunction in step 2 | real, strongest in file | real, no rect given | real | AMEND, minor |
| ZT-07 | real, strongest DOM in file | real curl + token hyprctl | real, no rect instruction | real | AMEND, minor |
| ZT-08 | real | token hyprctl only | real, chrome coords | real | AMEND |
| ZT-09 | real, strongest tab counts | decoration, hyprctl twice | single token click, vision-based | real, heavy | AMEND |
| ZT-10 | real | token hyprctl only | real, vision-based | real | AMEND |

## Findings

### 1. Systemic: the DOM-rect rule cannot cover browser chrome (lines 40-44)

Lines 40-44 require click coordinates from DOM rects, never vision
estimates. That works for page content (ZT-01 step 6, ZT-07 form fields).
It is impossible for address bar, sidebar rows, toolbar Back/Forward,
bookmark dialog and library, download panel, find bar, and the sidebar
collapse toggle. Those are chrome UI, outside page DOM, with no DOM rect
to fetch. The file therefore violates its own rule in ZT-01 step 1,
ZT-02 step 5, ZT-03 step 5, ZT-04 steps 3, 5, 7, ZT-08 steps 4-6,
ZT-09 step 5, and ZT-10 steps 4-6. Either the rule or the scenarios
must change. See required change R1.

### 2. ZT-00: mouse channel is absent (lines 86-87)

Step 4 is labelled "[MOUSE+KEYBOARD]" but contains only keyboard:
Ctrl+T, type, Enter. There is no mouse action anywhere in ZT-00.
Also lines 79-81: step 2 says curl "must return 200" then says 404
is normal and NOT a failure. A check with a built-in pass on either
outcome verifies nothing. It is decoration, not a CLI verification.

### 3. ZT-02: DOM label is false, mouse is a no-op, CLI is token (lines 141-146)

Step 5 is labelled [DOM] but the find bar is browser chrome, not page
DOM. Marionette cannot read a find-bar match count. The "at least one
match" assertion has no DOM method and its "or" makes it unfalsifiable.
The mouse click on the highlighted match in the same step verifies
nothing new: the step already asserts the match is scrolled into view,
and clicking plain article text navigates nowhere. CLI is one
`hyprctl activewindow` focus check (lines 145-146), nothing else.

### 4. ZT-03: mouse is conditional, sidebar position is vision (lines 166-174)

Step 3 mouse (middle-click or right-click the wordmark) runs only "if
present"; the fallback is keyboard-only, so the mouse channel may never
execute. Step 5 says "get the row position from a fresh observe",
which is vision grounding, directly contradicting lines 40-44.
CLI is one hyprctl check (lines 164-165).

### 5. ZT-04: DOM is mislabelled, CLI is decoration (lines 198-210)

Step 4 (lines 200-201) is labelled [DOM] but the star state is an
observe check, not DOM. Step 5 (lines 202-204) is labelled [DOM] but
the bookmark library is chrome UI, not page DOM; Marionette cannot
list it. Step 7 (lines 207-210) repeats the same mislabelling for the
delete check. CLI is `hyprctl activewindow` twice (lines 199, 206),
the same weak focus check, verifying nothing about bookmark creation.
No CLI check of bookmark storage is given.

### 6. ZT-05: mouse is a move plus a no-op click (lines 231-240)

Step 2 mouse is only "move the pointer to the centre", which asserts
nothing. Step 4 mouse is one click in the page body whose DOM check
is "nothing must change except focus", with no named DOM value to
compare before and after, so it is unverifiable as written. DOM also
repeats the same "Example Domain" title assertion in steps 1, 3, and 5.
CLI here is genuinely real (hyprctl activeworkspace, lines 229-236)
and is the model for what the other scenarios should do.

### 7. ZT-06: mouse rects missing, DOM step 2 is a disjunction (lines 263-275)

Step 2 DOM (lines 263-264) passes if the title contains "dummy.pdf"
OR the viewer renders a page, so a bare title with a blank viewer
passes. Step 4 (lines 268-270) gives no rect or selector for the
download button. Step 6 (lines 274-275) clicks in the download panel,
which is chrome UI with no DOM rect. CLI here is the strongest in the
file (curl control, ls baseline, ls plus file type check, rm plus ls
confirm, lines 265-267, 271-273, 277-278) and needs no change.

### 8. ZT-07: mouse clicks lack the rect instruction that is fixable here (lines 300-308)

Unlike chrome clicks, every ZT-07 mouse target (custname, custtel,
size, comments, submit) IS in page DOM, so a rect is available. The
file never says to fetch it. DOM is the strongest in the file (named
fields, exact values, echo check, lines 296-311). CLI curl control
(lines 298-299) is real; the hyprctl in step 7 (line 311) is token.

### 9. ZT-08 and ZT-09 and ZT-10: CLI is a single token hyprctl (lines 332-333, 366-367, 380-381, 399)

ZT-08 CLI is one hyprctl in step 3, with no curl control even though
steps 1-3 navigate to three sites, unlike ZT-01, ZT-02, and ZT-07.
ZT-09 CLI is the same hyprctl twice (steps 3 and 9). ZT-10 CLI is one
hyprctl in step 2, in a scenario about sidebar state that no hyprctl
check can verify. In all three, hyprctl only proves Zen is focused,
which the successful DOM and keyboard steps already imply.

### 10. Redundancies where two channels test the same thing

- ZT-01 step 1 (lines 103-105): Ctrl+L and a mouse click both focus
  the address bar. One of them is redundant as a focus test.
- ZT-03 steps 5-7 (lines 172-179): sidebar click, Ctrl+Tab, and
  Ctrl+Shift+Tab all assert the same "active tab title changes".
  Keep at most the sidebar click plus one keyboard switch, or state
  explicitly that the point is cross-channel comparison, not three
  independent pass conditions.
- ZT-05 steps 1, 3, 5 (lines 229-242): the same title asserted three
  times. Keep the step 3 and step 5 checks, drop the step 1 record
  as a pass condition, or name a different value for each.
- ZT-09 steps 5-6 (lines 370-373): mouse X close and keyboard Ctrl+W
  close assert the same count drop. State which close method is under
  test in each step.
- ZT-02 step 5 (lines 141-144): DOM match assertion and mouse click
  assert the same "match is visible". See finding 3.

### 11. The repeated hyprctl check is decoration in most scenarios

`hyprctl activewindow must show Zen` appears in ZT-00, ZT-01, ZT-02,
ZT-03, ZT-04 (twice), ZT-07, ZT-08, ZT-09 (twice), and ZT-10. It is a
real verification only where focus is the thing under test. Everywhere
else it adds no information beyond the DOM title check in the same
step. It must not be counted as the scenario's CLI channel on its own.

## Required changes (all in zen-ordinary-user-tests-20261121.md)

- R1, lines 40-44: amend the Tools rule. Add that chrome UI targets
  (address bar, sidebar, toolbar, bookmark dialog and library,
  download panel, find bar) have no DOM rect, so their coordinates
  come from a fresh observe with the screenshot saved as evidence,
  and the DOM-rect requirement stays mandatory for page-content
  targets only. Without this, findings 4, 5, 8, and 9 cannot be fixed.
- R2, lines 86-87 (ZT-00 step 4): add a genuine mouse action, for
  example click the address bar before typing, or relabel the step
  keyboard-only and add a mouse click in step 6 or 7. As written the
  gate claims four channels and uses three.
- R3, lines 79-81 (ZT-00 step 2): make the curl check assert one
  outcome. Either require 200 and fail on 404, or delete the curl step
  and rely on the Marionette check in step 3. Do not keep a step that
  passes on both outcomes.
- R4, lines 141-144 (ZT-02 step 5): relabel the match check [OBSERVE],
  not [DOM], name the exact observable (find-bar match count text, or
  highlighted text visible in the screenshot), and either delete the
  mouse click on the match or state what new state it must produce
  (for example, the find bar stays open and the viewport does not move).
- R5, lines 145-146 (ZT-02 step 6): replace the lone hyprctl with a
  real CLI check, or add one: for example `ps` confirming zen-bin is
  still alive, or a curl control on the article URL as in step 2.
  Hyprctl alone does not satisfy the composite rule here.
- R6, lines 166-169 (ZT-03 step 3): make the mouse step unconditional.
  Name the exact link and its DOM selector, and if the wordmark link
  does not exist, name a different in-page link to middle-click
  instead of falling back to keyboard-only Ctrl+T.
- R7, lines 172-174 (ZT-03 step 5): after R1, state the sidebar row
  position comes from the fresh observe screenshot, and save that
  screenshot path as evidence. Do not leave it as an unlabelled
  observe while lines 40-44 still forbid vision grounding.
- R8, lines 200-210 (ZT-04 steps 4, 5, 7): relabel the star check and
  both library checks [OBSERVE], not [DOM]. Add a real CLI check for
  the bookmark, for example a command that confirms the bookmark
  exists in Zen storage and is gone after step 7, or state explicitly
  that CLI in this scenario is the hyprctl focus check only and the
  scenario therefore relies on observe for the bookmark state.
- R9, lines 231-234 and 239-240 (ZT-05 steps 2, 4): replace the
  pointer move with a mouse action that asserts something, or delete
  it as a pass step. For step 4, name the DOM values compared before
  and after the body click (title and URL must be identical, and the
  page must not reload, checked by a DOM value, not by "nothing must
  change").
- R10, lines 263-264 (ZT-06 step 2): remove the "or". Require both
  the title and the rendered viewer page, or require the rendered page
  alone. A title-only pass must fail.
- R11, lines 268-270 and 274-275 (ZT-06 steps 4, 6): give the download
  button a selector or rect instruction, and after R1 state the
  download-panel click uses the fresh observe. As written both clicks
  are guessed coordinates.
- R12, lines 300-308 (ZT-07 steps 3-7): add "get coordinates from the
  DOM rect of the named field" to each mouse click. The rects exist
  here, so this is a one-line fix per step.
- R13, lines 332-333 (ZT-08 step 3), 366-367 and 380-381 (ZT-09 steps
  3, 9), 399 (ZT-10 step 2): in each of these three scenarios, add one
  CLI check that verifies something the DOM check does not, or delete
  the hyprctl line as a pass condition. Suggestions: ZT-08, curl
  control on the third URL as in ZT-01 step 3; ZT-09, `ps` confirming
  zen-bin alive after the reopen steps; ZT-10, record `hyprctl
  clients` window geometry before and after the collapse toggle, since
  the toggle must not resize or move the window.
- R14, lines 400-403 (ZT-10 step 3): relabel "Look at the sidebar"
  [OBSERVE], not [MOUSE]. Looking is not a mouse action.
- R15, lines 103-105, 172-179, 229-242, 370-373: for each redundancy
  in finding 10, either delete the duplicate pass condition or add one
  sentence stating the duplicate is intentional cross-channel
  comparison. Do not leave three steps asserting the same state with
  no note that they are the same assertion.

## What is good (no change needed)

- ZT-06 CLI (ls baseline, ls plus file type, rm plus ls confirm) and
  ZT-07 DOM (named fields, exact values, echo of all four values) are
  the models for real verification in this file.
- ZT-05 CLI (hyprctl activeworkspace before and after each switch)
  is the only hyprctl use that verifies the scenario's actual claim.
- ZT-01 step 6 (lines 115-116) is the only mouse step that explicitly
  requires DOM rect coordinates. Every page-content click should read
  like that step.
- ZT-00 as a gate is correctly strict (any step fails, stop the run),
  once R2 and R3 are fixed.
