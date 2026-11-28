# Pilot 2 outcome 2026-11-28: zen_cli cmd_open re-activate landed (PR #1245)

Decision authority: improvements/pilot-first-decisions-20261128.md
(todolist-push 209f1d92), Pilot 2 section. Evidence:
pilot2-background-tab.md, pilot-council-perf.md,
pilot-council-risk.md, pilot-redteam.md (VM
~/workspace/pilot-first-20261128/).

## Landed

PR #1245 merged to main as e7367d10 (2026-11-28). Branch
pilot2-open-reactivate-20261128, 5 commits (rebased onto 53e61e50
after PR #1244 landed mid-build; import-map conflict resolved by
keeping both sides):

- e604c9cf zen_cli: re-activate opener after open so selection does
  not move (Pilot 2)
- 877963f2 zen-rdp: dual-protocol live smoke for zen_cli open
  selection (Pilot 2)
- cd040927 zen-rdp: live smoke asserts tab identity via RDP, not
  lazy BiDi URL
- 75f24223 zen_cli: align flash_window_ms wording (review nit)
- 2d9aa955 rung3-ci: import-map entry for test_zen_cli_open_live

Files: scripts/zen_cli.py, tests/test_zen_cli.py,
scripts/zen-rdp/test_zen_cli_open_live.py (new),
skill/cli-anything/zen.md, rung3-ci/import-map.txt (1 line).

## What the fix does

cmd_open session path only (--live byte-unchanged; the session
path can never attach to the owner Zen, no BiDi port there). After
the new tab is found, browsingContext.activate on the opener runs
immediately, before the title fetch. Poll checks before sleeping
to shrink the steal window. track_current(new_tab) kept: tracked
stays the new tab, visible returns to the opener (visible !=
tracked after open). Re-activate failure fails open with
selection_restored=false plus selection_restore_error and note,
never silent. Result adds selection_restored and flash_window_ms
(window.open call send to re-activate completion; slight
overestimate, starts before the new tab lands).
browsingContext.createContext is unknown-command in this build;
not used. Limitation documented in code and skill: BiDi has no
selected-tab read, so opener != pre-open selected restores to the
opener, not the original selected tab. Skill doc gains the
addTrustedTab index-shift line (inserts before selected; never
cache indices across an open).

## Tests

- Unit/fake: tests/test_zen_cli.py 18/18 (3 new: re-activate
  order + tracked state, failure disclosure, --live remoting
  unchanged). Fake BiDi server models window.open tab creation
  and records call order/params.
- Zen-rdp unit shard green locally and in CI (rung3-checks pass
  5m19s on PR head 2d9aa955; gitleaks pass). Arch-guard initially
  failed on the missing import-map edge; fixed with one line.
- Live dual-protocol verification, dedicated session on the
  laptop (Zen 1.24.3b, BiDi 9321 + RDP 9322, one instance, pid
  recorded and stopped by pid with cmdline profile check
  immediately after; owner Zen verified alive after, ports
  free): 5 reps, selected identity unchanged 5/5 (RDP listTabs +
  gBrowser.selectedTab ground truth), new tab never selected,
  Hyprland focus constant, flash 19-23 ms (median 21 ms, max
  23 ms). Run 1 failed only on a harness assertion (lazy
  about:blank BiDi URL at open-return vs RDP real URL,
  pre-existing zen_cli behavior); fixed in cd040927, run 2 PASS.
  Raw JSON preserved in VM build evidence
  (pilot2fix-result.json md5 b6a474e9fd9c94038871fad1d53f02e7,
  byte-verified against the laptop copy; run 1 kept alongside).
- pii-scan: zero new hits (11 pre-existing false positives on
  main from the variable name session; added lines clean).

## Independent review

FCC worker who did not write the code (read-only diff review +
evidence check + local unit run): VERDICT: NO BLOCKING. All 8
scope points verified; run 1 confirmed as harness assertion bug,
not a selection defect. One low wording nit (flash clock start)
fixed in 75f24223, docs only, tests re-run 18/18. Verdict posted
on PR #1245 before merge.

## Flip condition

A flash remains by construction (window.open selects, then
re-activate restores): measured 19-23 ms. The ban stands as:
zen_cli open stays dedicated-session-only. That already holds by
construction (owner Zen has no BiDi port; session commands cannot
attach to it). --live still foregrounds by design (owner-intended
remoting, no session to re-activate with). Any future
live-capable reuse of cmd_open must revisit this fix before
reuse.

## Side finding (not fixed, out of scope)

zen_cli reports tab.url as about:blank at open-return while the
new tab is lazy (pre-existing; RDP shows the real URL). Tracked
URL can therefore be about:blank until a later command re-lists.
Unchanged by this diff; noted for a future small fix if tracked
URL freshness matters.

Owner is referred to as Pham Tuan in repo-facing text; no
personal info in this record (fixture URLs are 127.0.0.1 only).
