# Repo redo + git history research: council and redteam decision

**Date:** 2026-11-28 (research run 10:55-11:30 Asia/Ho_Chi_Minh)
**Trigger:** owner order 2026-11-28 10:29: after the arch-guard cleanup, the whole team meets and researches redoing the entire repo and its git history.
**Status of the arch-guard cleanup:** done. PR #1244 merged (53e61e50), 131 violations to 0, rung3-checks CI wired.
**Mode:** RESEARCH ONLY. No history was rewritten, no force push, no deletions, no repo edits were made by this research.
**Prior audit:** `git-history-pii-audit-REPORT.md` (2026-11-23, local record) recommended REWRITE deferred until after the acceptance campaign. R3-L3 closed 2026-11-27, so the deferral condition is met and the question is live again.

**Redaction rule for this document:** no personal value is quoted anywhere. Findings are named by category plus commit hash or file path only. The owner is called Pham Tuan in repo-facing text.

## Verdict in one paragraph

Two questions were asked. They get opposite answers. **Repo structure: do not redo.** A restructure buys about zero tokens, zero test seconds, and zero error-rate gain, because Graphify already avoids whole-file reads, test sharding already exists, and the arch-guard already gates the observed error classes. The real structural debt is small and incremental (4 to 7 agent-days). **Git history: hybrid with hard gates.** Land the tip scrub on main now by normal commits (the home-address category is still public at the main tip today), rotate the exposed token category with proof, and switch committer identity to the noreply form enforced in CI. Prove that holds for one week of fleet pushes. Only then, and only if Pham Tuan accepts partial privacy (the account handle stays visible regardless), run a filter-repo rewrite of the public history with a private archive of the original, a published commit-map, a PR-ref purge through GitHub support, and a fetch test proving old hashes are unfetchable. Real anonymity is not available under the same account; it requires an account or organization move, which is an owner decision listed at the end.

## Seats and method

Four independent seats answered first, then the redteam attacked every option, then this synthesis debated the positions against each other.

- **Seat A, history scan (evidence):** fresh full-history pickaxe over ALL refs (5,085 commits, 1,146 refs) with the arch-guard denylist categories plus the prior audit's categories. gitleaks is absent on the VM; pickaxe only.
- **Seat B, rewrite options:** six options compared with costs, breakage inventory (branches, tags, PRs, hash citations), and an 8-step safest procedure for the recommended option.
- **Seat C, repo structure:** Graphify-first measurement on an export of origin/main 53e61e50; verified import-map rot, the three dead test gates, suite error classes, hermetic count.
- **Seat D, redteam:** attacked rewrite, fresh repo, orphan branch, and tip-only with equal force; named procedure failure modes and falsifiers.
- **Clone2 and Mei** were asked for independent seat answers in their own chats. Clone2's full seat answer landed as `improvements/clone2-repo-redo-seat-20261128.md` (991fd0ad) and is debated below. Mei ran three research lanes plus an independent verifier; her verdict had not landed at synthesis time and will be appended when it arrives. The remaining gap does not block the verdict, and Mei's clone-breakage answers are captured as open questions below rather than assumed.

## Evidence: what is in history now (Seat A)

| Metric | 2026-11-23 audit | 2026-11-28 refresh |
|---|---|---|
| Content-PII commits (union, excl. fake fixture) | 463 | **602** |
| Total commits, all refs | about 1,560 (3 branches) | **5,085** |
| origin/main commits | 1,562 | **2,376** |
| Metadata PII (handle or Gmail as author/committer) | about 98-99% | **still about 98-99%** |
| Corrupted author name (handle + terminal escape) | 7 commits | **370 commits** |
| Open PRs | not counted | **797** |
| Branches | 3 audited | 63 local + 1,078 remote-tracking |
| Tags | not counted | 4 freeze tags |
| Worktrees on the VM | not counted | **55** |

Growth is partly wider scope (all refs, not 3 branches) and partly 2,608 new commits since the audit. Identifiability verdict is unchanged: YES, a stranger can identify the owner, the account, and the machine. No real phone number, no real private keys, no GitHub tokens were found. The one phone-like string is the owner-confirmed FAKE fixture (2026-11-24), classified as fixture and excluded from the union.

### Tip state at origin/main 53e61e50 (after PR #1244)

PR #1244 removed exactly **one of the five** baseline tip exposures: the Gmail local part plus second account handle in `docs/cookie-session-summary.md`, the only one inside arch-guard scan scope. The rest survive because arch-guard deliberately does not scan `improvements/`, `rung3-run-log/`, or `coord/`:

- **Home street address category: STILL PRESENT at the public tip** (`improvements/worker-y2b-agy-log.md`, introduced in `eba3bce1`). Only todolist-push carries the redacted placeholder (scrubs `5998626` / `8b9f5da4` never reached main).
- Machine spec line: still present at all tips (`improvements/speed-prior-art.md:20`, commit `2a50390a`).
- Home paths 349 lines, Tailscale-range addresses 63 lines, school acronym 427 hits remain repo-wide at the origin/main tip, concentrated in the unscanned historical trees and allowlisted frozen files.
- Post-audit leak rate slowed but did not stop: 2 Tailscale-range and 5 home-path touches in origin/main commits after 2026-11-23; 0 new Gmail, click-ID, or document-URL touches there.

This is the single most urgent finding of the whole research: the audit's phase-1 tip fix for main was due 2026-11-23 and the most sensitive category is still public five days later. Phase 0 below fixes it with normal commits; no rewrite is needed for the tip.

## Evidence: what breaks under each history option (Seats B and D)

Scale of breakage, measured: 1,078 remote branches, 797 open PRs (about 720 watchdog-disposable, about 76 coord evidence, 1 real code PR at review time), 2,041 `refs/pull/*` entries, 4 freeze tags (R3-L1-FREEZE, R3-L1-FREEZE-2, R3-L2-FREEZE, R3-L3-FREEZE), 55 worktrees on this VM alone, 41,226 hash-like citations across run-log, improvements, coord, and docs (7,787 in rung3-run-log alone; 248 full SHAs are real commits across 1,094 files).

| Option | Cost | Privacy gain | Provenance | Verdict |
|---|---|---|---|---|
| (f) Hybrid: filter-repo on public main + private archive | 32-48h | High for content categories; handle stays | Preserved in private archive + commit-map | **Recommended, gated** |
| (a) Full filter-repo rewrite | 24-40h | Same as (f) | Commit-map only; converges to (f) once a backup archive is added | Fallback |
| (c) Fresh public repo + old repo private | 6-10h | Same content gain as rewrite; handle stays | Destroyed in public | Needs owner value judgment; dominated on provenance |
| (d) Orphan branch, same repo | 8-12h | False cleanliness: old objects stay reachable via PR refs | Destroyed | **Rejected** |
| (e) Tip-only fix, accept history | 2-4h | Casual-viewing exposure near zero; determined exposure 100% | Perfect | **Required now as Phase 0; rejected as final state** |
| (b) BFG | 20-32h + still needs filter-repo | Cannot rewrite author/committer emails | Same as (a) | **Rejected: strictly dominated** |

Redteam's three decisive points, which the council accepts:

1. **Rewrite false-clean is the highest risk.** `refs/pull/*` (2,041 entries) keep old commits fetchable after any branch force-push; filter-repo does not touch them. Without bulk PR handling, a GitHub support purge, and a fetch test proving `eba3bce1` is unfetchable by SHA and via pull ref, the team will believe history is clean while it is one fetch away. Any stale clone pushing during or after the window resurrects everything; watchdog PRs land about every 15 minutes, so the freeze must silence the whole fleet including crons.
2. **Provenance destruction is real and the handle stays anyway.** The R3-L3 evidence chain (52 PASS / 1 FAIL, dual scorers, reruns) is anchored to hashes and freeze tags. Rewrite orphans the citations; fresh repo destroys them. And the repo remains public under the owner handle (URL, LICENSE, contribution graph), so no option under the same account delivers anonymity. A rewrite buys content privacy only. Selling it as anonymity would be false.
3. **Tip-only drift is the failure mode of doing nothing.** Tip-only leaves all 602 content commits and about 99% metadata commits pickaxe-retrievable forever and keeps the weekly full-history secret scan red (413 findings at landing), training the team to ignore it. It is acceptable only as explicit owner-signed accepted risk, never as silent default. The 5-day tip-fix delay is the precedent.

Sequencing point the council adopts from the redteam: new commits at 53e61e50 still carry handle-plus-Gmail-category metadata. Rewriting the past while the present leaks is a treadmill. Identity hygiene first, proven for a week, then discuss the past.

### The Clone2 dissent, and how the council resolves it

Clone2's seat answer agrees on hybrid, on incremental structure cleanup, and on rejecting same-repo orphan and BFG, but disagrees on mechanism: **fresh repo from the scrubbed tip plus the old repo kept as a read-only archive**, explicitly not a filter-repo rewrite of the live repo. Its decisive argument is the redteam's own point 1 pushed to its conclusion: this repo has 1,245 PRs, GitHub keeps every PR's commits reachable under `refs/pull/*` regardless of branch rewrites, and unreachable objects linger, so an in-place filter-repo pass pays the full breakage cost (every hash changes, every PR ref orphaned) and still leaves the old history fetchable by SHA in the same repo. A fresh repo with a new object store is the only form that removes the history from the public surface without depending on a GitHub support purge. Clone2 also quantifies its own breakage: 8 clone and worktree directories on its VM, 50 worktrees registered on the main clone, roughly 15,000 short-hash tokens across 637 documents in `improvements/` alone, and 539 watchdog PRs of its own (of 796 open repo-wide, zero ever merged). It adds one constraint the council adopts: the owner's 2026-11-27 exception keeping 5 frozen watchdog-log lines was a deliberate keep decision; whichever home that file ends in, the exception is honored or explicitly re-decided by the owner, never scrubbed by default.

Council resolution: the disagreement is real but narrow, and it turns on one testable fact. Seat B's option (f) keeps URL and PR-number continuity and public provenance via a published commit-map, but its completeness depends on GitHub support purging PR refs and cached views. Clone2's variant needs no support purge for the public surface, but loses URL continuity and PR numbering, and its purge is only complete if the old repo goes private, which then makes hash resolvability team-internal only (the archive stops being public evidence). **The council keeps (f) as the recommendation with Clone2's fresh-repo variant as the named fallback, and makes the choice evidence-gated:** during the Phase 2 dry run, test whether a known old hash stays fetchable via pull ref after a simulated purge path; if GitHub support cannot or will not purge, (f) is false cleanliness and Clone2's variant becomes the recommendation. Either way, Phase 0 and Phase 1 are identical, so the choice does not block starting now. Clone2's sediment numbers (1,061 remote branches, 796 open PRs, docs/ 20 MB of a 45 MB tree) also strengthen Seat C's incremental cleanup list: branch and PR hygiene plus stopping log sediment from being committed to the code repo are added to the structure track.

## Evidence: repo structure (Seat C)

Measured on origin/main 53e61e50: 1,489 files / 382,888 lines, but production code is only about 10% (scripts 35,411 Python lines + native). Frozen records (docs + improvements + coord) are 57% of lines. Tests are 30%.

- **Import-map rot confirmed:** 13 stale keys, 4 missing keys. Correction to the arch-guard outcome note: phantom edges measure **11** on main with the guard's own resolver, not 5 (the 5 fits the integration tree). Root cause is branch drift: the 13 modules never existed on main; they live on the integration line (the cu.py split, about 5,100 lines) and the map was generated from that graph. The guard never flags stale keys or phantoms, so rot is silent.
- **Three dead gates confirmed with root causes:** test-seal 2/3 fail (collect-evidence.py absent), test-check-spare-scorer 2/10 (sign-off record absent), test-pre-freeze-gate 5/5 (verify-list.py absent). 719 lines that cannot pass on main; CI already excludes them.
- **Suite re-measured:** 1785 total, ok=1701 error=59 fail=7 skip=18 (baseline 1708/54/5/18; environment delta). All bad tests categorized by traceback: 52 of 54 baseline errors trace to one class (tests needing a built native tree error instead of skipping). No error traces to repo layout.
- **Hermetic re-measured:** 31 tool-dependent tests on the VM (the outcome doc says 35; environment delta), across 8 modules.
- **Dead code:** zero dead production modules (51 unimported files are all entrypoints). Live docs: 0 broken links, 0 stale-path hits (all 47 stale hits are frozen dated records).
- **Velocity:** 1,976 commits in 7 days on main. Main advanced during the research itself.

**Structure verdict: do not redo.** A restructure buys about 0 tokens (Graphify already avoids whole-file reads), about 0 test seconds (sharding exists: 2.50x on the laptop), about 0 error-rate gain (the guard already gates the observed error classes), while paying lockstep re-pinning (97 map keys, 24 allowlist prefixes, sync manifests, 18 CI filenames), machine-layer reinstall plus live re-verify, and daily conflicts at about 282 commits/day. The actual structural debt is the unlanded cu.py split, which is already written and lands incrementally.

**Incremental cleanup list (4 to 7 agent-days total):**
1. Guard flags stale keys and phantom edges (S).
2. Prune the 13 stale keys or land the split; team decision (S).
3. Delete the 719 lines of dead gates, or port them properly (S).
4. Built-tree skip guards so native-dependent tests skip instead of error (S-M).
5. Fix the 31 hermetic tests, then flip the hermetic gate to blocking in CI (M).
6. Frozen-record search hygiene in SKILL.md (XS).
7. Graphify rebuild to include zen-rdp (XS).
8. Land the cu.py split module by module (L spread; the only real token upside, about 25k tokens per task for whole-file readers).

## Recommended plan

### Phase 0: now, normal commits, no rewrite (2-4h)

1. Land the tip scrub on main: home-address category (`improvements/worker-y2b-agy-log.md`), machine-spec line (`improvements/speed-prior-art.md:20`), and the remaining tip categories Seat A listed, using the same redaction todolist-push already carries. Verify by `git show` on the new tip.
2. Rotate the Polygon session-token category with proof (rotation plus old-session revocation; check provider logs). This is required regardless of the history decision; assume the old value is burned.
3. Switch committer identity for the whole fleet to the noreply email form plus the decided name policy (owner-decision item 4 below), enforced by CI so regressions fail the push.
4. Triage the weekly full-history secret-scan findings into an accepted-risk list with owner sign-off, so a red signal means something again.

### Phase 1: prove it holds (1 week)

Normal fleet pushes for one week with zero new findings in pushed-range scans and zero metadata regressions. No phase counts as done without pasted evidence (scan output) in the record. This gate exists because the redteam's biggest-risk finding is that phase 2 never happens while the team declares victory on tip fixes alone; the evidence rule makes that impossible to fake.

### Phase 2: gated rewrite, only on owner acceptance (32-48h, option f)

Only if Pham Tuan accepts partial privacy (content cleaned, handle stays) and decides the freeze-tag policy:

1. Fleet freeze: stop every pusher (agents, crons, watchdogs) by name; verify silence.
2. Bundle backup of all refs; private archive repo holding the original history for campaign verifiability.
3. Inventory: every clone and worktree on every machine, confirmed by asking each agent directly (never assume). Clone census is currently open (see below).
4. Dry run on a copy: filter-repo with the full replace list (including diacritic and partial variants, local-part-only email, alternate handles, the corrupted-author form), author/committer rewrite per the decided policy, tag handling per the decided policy. Re-audit the rewritten history with the same pickaxe suite plus a binary scan; CI green on rewritten history; arch-guard still 0.
5. Publish the commit-map (old to new) so citations can be translated.
6. Force-push all heads and tags in the frozen window; branch protection handled explicitly.
7. GitHub support request to purge PR refs and cached views of old SHAs; bulk-close the disposable watchdog PRs (owner-decision item 6).
8. Verification: fetch test proving `eba3bce1` and a sample of old hashes are unfetchable by SHA and via pull ref; fresh clone audit returns zero for all audit categories. Rollback path: the bundle backup and private archive.
9. Re-clone protocol per agent and per machine; unfreeze only after every clone is confirmed new.

### Structure track (parallel, incremental)

Execute Seat C's 8-item cleanup list as normal PRs, plus Clone2's sediment items: delete merged and stale lane branches (1,061 remote branches down to a handful), bulk-close dead watchdog PRs (owner-decision item 6), and stop committing log and lane-scratch sediment to the code repo (move to archive or local-only storage). No restructure, no layout change. The cu.py split lands module by module behind the existing guard. If the fresh-repo fallback is ever taken, it imports the cleaned tree, not the sediment.

## Owner-decision items (not decided by the team)

1. **Account move:** is moving the repo to a different account or an organization on the table? Without it, no option delivers anonymity; with it, fresh-repo-plus-move becomes viable and provenance loss may be an acceptable price. This decision gates everything else in Phase 2.
2. **Campaign docs:** public (rewritten, redacted) or private-archive-only? Determines whether the R3-L3 evidence chain stays publicly verifiable.
3. **Freeze tags:** re-issue on rewritten commits (freeze semantics change) or keep on old objects (keeps PII reachable) or delete (destroys campaign anchors)? No clean choice exists; Pham Tuan picks.
4. **Author-name policy:** keep the handle as author name (standard GitHub behavior, matches repo owner) or rewrite to a generic name (breaks scorer provenance)? Emails go to noreply either way.
5. **Token rotation proof:** has the Polygon token category actually been rotated with old sessions revoked, and provider logs checked? (Ask Pham Tuan directly; do not assume.)
6. **Watchdog PR mass closure:** approve bulk-closing about 720 disposable watchdog PRs as part of any Phase 2 PR-ref purge?
7. **Accepted risk if Phase 2 is declined:** if the answer is tip-only as the final state, it needs explicit owner sign-off that history exposure (address, email, tokens-in-history, machine identifiers) remains public, plus the Phase 0 items. Silent drift is not a decision.

## Open questions (ask directly, never assumed)

- Clone census off this VM: laptop dev copy, Mei, Mochi, Clone1, Clone2, Codex/FCC/opencode clones: paths, dirty state, worktree counts. (Seat A counted 55 worktrees on the VM; off-VM counts are UNVERIFIED-ASK.)
- Laptop pinning: does the installed laptop machine layer pin or compare commit hashes? (Ask laptop agents directly.)
- Tag messages: do the four freeze tag messages contain hashes or personal categories? (Read-only check not yet done.)
- Mei's seat verdict: requested 2026-11-28, three lanes plus independent verifier in progress at synthesis time; append on arrival. Clone2's seat text landed (991fd0ad) and is debated above. If Mei's verdict contradicts this synthesis, the council reconvenes before Phase 2.

## What would change this verdict

- Owner approves an account or organization move: Phase 2 becomes rewrite-plus-move (or fresh repo under the new account), and the provenance calculus changes.
- Dry-run evidence fails (re-audit nonzero, CI red on rewritten history, PR refs unpurgeable): fall back to honest tip-only with signed accepted risk rather than theatrical hybrid.
- New leak categories appear in Phase 1: stop, fix prevention first; rewriting the past while the present leaks stays the worst sequencing.

*End of synthesis. Research only; nothing was rewritten, force-pushed, or deleted. Seat files: seatA-history-scan.md, seatB-rewrite-options.md, seatC-structure.md, seatD-redteam.md (research workspace, 2026-11-28).*
