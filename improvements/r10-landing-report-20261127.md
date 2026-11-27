# R10 landing report: seamless-control toolset (route 3c, RDP-primary) (27/11/2026)

Coordinator report on landing the toolset decided in
`r10-seamless-decision-20261127.md`. The owner accepted silent
attach (RT-04) on 27/11 14:00 +07 (prompt-connection=false,
loopback-only); the written record lives in the laptop machine
layer next to the port registry. The interim two-profile split
remains the operating configuration; nothing has been switched.
The toolset is landed in the repo, unselected.

## What landed

Repo `scripts/zen-rdp/` (commits `73f3f80d` + hardening `cd6d45b5`,
branch fix-review-20261127, ls-remote verified, pii-scan clean):
scoped RDP client, per-update smoke, tests, README. Generic,
OPTIONAL, opt-in, default off (RT-22). Machine layer (laptop only):
RDP prefs set, port registry (owner: Muse parent, all channels
unselected, fail-closed rule), RT-04 acceptance record, runnable
smoke + client copies in the machine bin (sha256-matched to repo).

## Per-item evidence

### RT-03 Zen-internals control via RDP parent target: PROVEN (throwaway)
Reads (workspace list, active workspace, folder list, pinned count,
essentials count) median 0.6 ms; writes with read-back + revert:
workspace create/switch/remove, folder create/delete
(`folder.delete()`; bare `removeTabGroup` failed first, root-caused
live), pin/unpin. Visible-effect screenshots. Report:
`r10-landing-l1/report-l1-rt03.md` (VM work dir). The parent API is
now in the landed client, gated (`--allow-parent`, drive-reported).

### RT-20 tool-enforced tab scoping: DONE + HARDENED
Scope guard (tab ids and/or URL globs) on evaluate/navigate/
getTarget; credential denylist with logged approval path; drive
report (probe, tab diff, refusals, approvals, retries). Redteam
bypasses closed in W-L7: denylist ON by default in the CLI
(`--no-denylist` explicit + recorded); unscoped refused without
`--unscoped-test`; empty-URL lazy tabs treated as denylisted;
scope AND semantics; URL-verified pinned re-attach; diff keyed by
(url,title) on id shift; `request()` refuses evaluate/navigate
packets outside the guarded methods; `bench` gated. Unit 29/29,
live throwaway 19/19. Reports: `r10-landing-l3/report-l3-rt20.md`,
`r10-landing-l7/report-l7-hardening.md`.

### RT-06 DevTools concurrency: PASS (throwaway)
321/322 evaluates OK across DevTools open/console/close (medians
1.17-1.41 ms); typing intact while another tab navigates; no focus
theft. Sharp edge: closing DevTools can kill the held consoleActor
once (`noSuchActor`, 1/322); the landed client re-attaches pinned
(by canonical id, URL-verified) with one retry (unit-proven; live
firing still unobserved: 0/60 in L5, 0/31 in L6). Report:
`r10-landing-l2/report-l2-rt06.md`.

### RT-05/RT-18 per-update smoke + port registry: DONE
`rdp_smoke.py`: checks (a) port owner, (b) attach, (c) webdriver
probe CLEAN, (d) evaluate, (e) parent typeof x3, (f) loopback-only
bind, (g) latency, (h) navigate (added in hardening). Distinct exit
codes, fail-closed (port + marker required). PASS + FAIL cases
proven live; PASS on the real profile during RT-21 (attach 4.5 ms,
evaluate 0.2 ms). Registry installed in the machine layer (7
channels, named owner Muse parent, fail-closed rule verbatim,
marker set, selected count 0). Watch integration applied:
`r3l3-zen-laptop-health` step 1b runs the smoke on Zen version
change (cron.update + cron.view verified 27/11); while no channel
is selected it logs "skipped: no selected channel". Report:
`r10-landing-l4/report-l4-rt05-rt22.md`.

### RT-22 placement: DONE
Placement audit in the L4 report: client + smoke + tests = repo
generic opt-in; prefs, registry, scope-config entries, drive
reports = machine layer; latency medians repo-ok, raw runs
machine-layer. Machine-specific findings (docstring path,
fail-open marker default, test example values, fixture coupling)
fixed at landing (L5) and re-verified (L7). `prompt-connection=false`
stays machine-layer behind the RT-04 record, never a repo default.

### RT-21 real-profile acceptance: PARTIAL PASS
9-step test on the owner's real profile, 14:36-15:11 +07, with
record/restore (tab record, user.js + prefs.js backup/restore
sha256-identical, agent actions only in new tasked tabs, restore
to flag-free launch, probe CLEAN, tabs 57/57 pairs 0 diff):
- Steps 1, 3, 4, 5, 6, 7 PASS (same pid, scoped DOM read 0.9 ms /
  write 0.8 ms median, trusted OS click, internals pin/unpin,
  concurrency 31/31, loopback-only + smoke exit 0).
- Step 2 PARTIAL: Google 5/5 SERPs PASS; landings P1/P5/C1/Q5
  PASS, P2 coolors CHALLENGE-CF. Flagged-raw control challenged on
  both P1+P2 (panel not void). Kill criterion 6 (Google-entry
  failure) NOT triggered. Panel is probabilistic; no "never
  blocked" claim.
- Step 8 PROCEDURE-READY (smoke proven + registry + watch step 1b;
  no real update today).
- Step 9 DONE (below).
Report: `r10-landing-l6/report-l6-rt21.md`.

### Speed (item 7)
W4 baselines held or beaten: attach-to-first-evaluate 3.0-4.5 ms,
evaluate 0.2-0.5 ms, DOM read 0.3-0.9 ms, navigate ~54 ms
poll-bound. End-to-end vs split baseline (RT-21 step 9, n=1 each):
example.com+title 0.162 s vs 1.3 s; local DOM write 0.083 s vs
1.106 s; Google search+click+title: RDP lane completed in 39.3 s
(OS-input batches dominate) while the flagged baseline was blocked
at google.com/sorry in 6.3 s (task never completed). Honest claim:
DOM verbs are ~8-13x faster; user-path tasks with trusted input
remain OS-lane-bound.

## Reviews

- Council (`r10-landing-review/council-review-20261127.md`):
  LANDING-READY WITH CONDITIONS C1-C8, no blockers.
- Redteam (`r10-landing-review/redteam-review-20261127.md`):
  DO NOT switch yet; 5 must-close items + conditions.

Disposition of every redteam blocker / council condition:
1. RT-04 written record: CLOSED (machine-layer record written
   27/11; acceptance 14:00 relayed by parent).
2. Mandatory scoping: CLOSED in code (W-L7: denylist default ON,
   explicit `--unscoped-test`, lazy-tab refusal, AND semantics,
   URL-verified re-attach, `request()` guard, bench gate).
   Residuals documented in the L7 report (TOCTOU guard snapshot,
   navigate destination scope, substring over-match, list_tabs
   disclosure, report probe side effect) - accepted as known
   limits, listed below.
3. Positional tab ids: CLOSED for the held-session + URL-pattern
   paths (AND semantics, URL-verified pin, (url,title) diff).
   Cross-connection tab-id-only scope remains unsafe by design;
   URL-pattern scope is the required form for owner drives
   (council C3).
4. Parent target: CLOSED (landed, gated, audited; smoke uses the
   landed API). Chrome-JS power is inherent to RT-04 acceptance.
5. Update gate mechanized: CLOSED (watch step 1b applied +
   verified; registry marker set; smoke gained navigate check;
   Google spot check remains a step-8 drill action, not in the
   smoke script).
6. Single-drive lock: CLOSED as a mechanism (flock `--lock-file`,
   second client refused, holder in drive report). The owner-drive
   wrapper must always pass it (switch-time act; RT-23 design
   still owed).
7. longString: CLOSED (L1 substring fetching ported; live-proven
   20k-char reads).
8. Council C5 automation: CLOSED (cron step 1b). C6 monitoring
   debts (cold repeats across hours; first live noSuchActor
   firing review) and C7 (RT-02 suite) remain open as post-switch
   monitoring, not switch blockers per council.

## What still blocks switching (parent decision)

The toolset is landed; the operating-configuration switch is not
done and is the parent's call. Switching concretely requires, in
order:
1. Launch config (machine layer): owner user.js gains the generic
   RDP pref set; owner launch path adds `--start-debugger-server
   6021` (still flag-free). The switch launch must pass
   `--profile` so the registry marker matches, or the smoke
   refuses (fail-closed by design).
2. Registry: `zen-rdp-owner.selected=true` (exactly one channel).
3. Smoke PASS on the landed launch config recorded in the registry
   before the first drive (council C8).
4. Owner-drive discipline in every brief: scoped (URL-pattern),
   denylist ON (default), `--lock-file` set, `--allow-parent` only
   for internals asks, `--unscoped-test` and
   `--allow-unmarked-test-attach` banned on the owner channel.
5. First Zen update after switch = supervised drill (smoke +
   Google spot check before agent use resumes; FAIL retires to
   the split per kill criterion 1).

Still open (not switch blockers per council; redteam conditions):
RT-02 isTrusted suite (upload/clipboard/drag/Turnstile via OS
lane); RT-23 locking design beyond the flock fence; cold panel
repeats across hours; first live noSuchActor firing review;
residual scoping limits listed in the L7 report. R10 stays OPEN
until the first post-update drill passes.

## Recommendation

Land as-is (done). Switch only as a deliberate parent act with
steps 1-4 above, keeping the split as fallback. The evidence
supports the RDP lane as strictly better than the flagged
baseline on Google entry and DOM speed, with a probabilistic
Cloudflare panel (P2 challenged once on the real profile) that
must be stated plainly wherever the landing is announced.

Coordinator, 27/11/2026. English only. No personal information in
this document; machine-specific configuration lives only on the
laptop machine layer.
