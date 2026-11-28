# Phase 2 git history rewrite: dry-run record (COMPLETE)

**Date:** 2026-11-28, dry run executed 15:12-16:45 Asia/Ho_Chi_Minh (owner approved 15:12, including running code from a repo checkout despite the execution-risk flag; the flag fired again during the run and work proceeded under that approval).
**Mode:** DRY RUN ONLY. No force push, no branch/tag deletion, no PR closing, no changes to the real repo. All rewrite work happened on VM clones. One throwaway private test repo was created for the purge test (see below); it could not be deleted afterwards because the gh token lacks the delete_repo scope (interactive re-auth needed), so it remains private and is listed as a pending owner action.
**Redaction rule:** no personal value is quoted anywhere, except the repo's own public handle and the owner's repo-facing name form (Pham Tuan), per repo convention. Findings are named by category plus commit hash or file path only.

## Owner decisions applied (28/11 15:03, final)

1. Keep the current GitHub account (no move).
2. Campaign docs: clean them and keep public.
3. Delete the freeze tag R3-L3-FREEZE in the rewrite. The other three freeze tags (R3-L1-FREEZE, R3-L1-FREEZE-2, R3-L2-FREEZE) were kept in the dry run; disposition still open for the owner.
4. Author/committer in rewritten history: generic identity with noreply email. The dry run collapsed ALL identities to one generic identity (Maintainer, users.noreply.github.com address); execution can choose a per-identity mapping instead, flagged below.
5. Polygon session rotation: owner action, still pending.
6. Bulk-close the disposable watchdog PRs: approved; 743 PR numbers listed (watchdog-prs.txt, local); NOT closed in this dry run.
7. Rewrite the history (do not accept exposure as final state).

## Ref and PR inventory (measured 2026-11-28 ~15:15, read-only)

| Metric | Value |
|---|---|
| Total refs | 3,159 by ls-remote; bundles record 3,156 heads (original) / 3,155 (rewritten) |
| Remote branches | 1,074 |
| PR refs (refs/pull) | 2,077 |
| Tags | 4 freeze tags |
| Commits on main | 2,390 |
| Open PRs | 813 (of 1,265 total); 743 watchdog-titled |
| Repo size | about 247 MB |
| main tip at clone | 284c6082 |
| todolist-push tip at clone | cbcf3e1e |

Watchdog PRs are still created about every 15 minutes (743rd observed during the dry run). Any execution window must silence the whole fleet including crons.

## Exposure inventory (measured this dry run, full-history blob scan)

Method: every unique blob reachable from all refs scanned once (9,564 blobs), hits mapped to commits in one `git log --all --raw` pass. 4,136 hit blobs; 3,351 commits touch a hit blob. (The morning research counted 602 content-PII commits by pickaxe; the methods differ: pickaxe counts commits where a string's count changed, this scan counts commits whose diff touches a hit blob. Both are reported; neither is wrong.)

| Category | Blobs | Matches | Files |
|---|---|---|---|
| personal-name | 2,661 | 25,722 | 287 |
| home-path | 1,580 | 26,279 | 583 |
| profile-dir | 127 | 390 | 22 |
| tailscale-ip | 327 | 368 | 38 |
| session-token-shape | 19 | 22 | 12 |
| ccid-shape | 19 | 22 | 12 |
| bare-username | 410 | 3,818 | 78 |
| street-marker | 3 | 13 | 2 |
| email-personal | 95 | 96 | 17 |
| nickname (broad) | 2,546 | 581,107 | 113 |

Nickname note: the broad pattern matches the Vietnamese word for "currently" (written without diacritics) which dominates the count (top followers: chay, cho, lam, hoat). Name-attribution contexts were replaced in the rewrite; verb usage was left untouched by design and is not personal information.

Gitleaks (8.24.3) over all refs: 4,670 commits scanned, 128 findings, all rule generic-api-key, 59 commits, 71 files. None of the 128 is a session token; they are heuristic hits on hashes and IDs in run records. The count is identical before and after the rewrite (see verification).

Metadata: about 98-99% of commits carry a personal-category author/committer identity (research figure); 370 commits carry the corrupted author form (handle plus terminal escape).

## Rewrite performed on the clone

Tool: git-filter-repo 2.47.0 on a mirror clone (5,918 commits parsed, 434s first pass; second pass 500s after the case-variant fix below). Replacements: 3 literal street-address rules (extracted programmatically, never printed) + 29 regex rules covering all categories above, including URL-encoded token forms and diacritic case variants. Author/committer rewritten to the generic identity. Commit messages rewritten with the same rules. Tag R3-L3-FREEZE deleted in the clone.

Two defects found and fixed during the dry run:
1. Diacritic case variants: filter-repo's regex is byte-mode, so case-insensitive matching does not fold diacritic case. The first pass left ALL-CAPS diacritic name forms (66 blobs, one file). Fixed by enumerating case forms; second pass rescans to zero.
2. Guard self-mangling: the replacements rewrote one line of rung3-ci/arch-guard.py (its own denylist literals became the replacement text), making the guard flag its own replacement phrase (558 false violations on the rewritten tip). Test fixtures in rung3-ci/test-arch-guard.py were likewise altered. Execution must carve out rung3-ci/arch-guard.py and rung3-ci/test-arch-guard.py (restore them post-rewrite; they contain name fragments as regex pieces by design and are outside the guard's scan scope).

Rewritten tips: main 85c08dd6 (from 284c6082), todolist-push 516b6f64 (from cbcf3e1e). Commit-map: 5,918 entries, tip mappings verified.

## Verification on the rewritten history

- Full-history rescan (same scanner): **zero hits** in personal-name, profile-dir, home-path, tailscale-ip, session-token-shape, ccid-shape, bare-username, street-marker, email-personal. Nickname residual 580,604 matches, sampled contexts all verb usage. Independent shape-level spot-check (FCC, broader regexes): session-token shape 0 matches; home-path shape 23,898 matches across 1,474 blobs, all 3 distinct directory tokens are generic placeholders; Tailscale shape 365 matches across 326 blobs, exactly 1 distinct address, the generic CGNAT range base (documentation form, not a host address). Read "zero hits" as **zero personal values; generic placeholders remain**.
- arch-guard on rewritten main tip: **PASS** (after restoring the two guard files per the carve-out above).
- Test shard, rewritten tip vs original tip measured the same day on the same VM: rewritten total=1788 error=57 fail=5 ok=1708 skip=18; original total=1788 error=55 fail=5 ok=1710 skip=18. Fails identical. Delta: 3 errors only in rewritten, all in test_perf_evidence.EvidenceChecks, all the pinned-hash class (check-perf-evidence.py verifies an R5 source commit/blob by old hash; the hash no longer exists). 1 error only in original (flaky). The 3 are fixable by translating pinned hashes through the commit-map in a post-rewrite fix-up commit.
- Gitleaks on rewritten history: 128 findings, identical count and file set to the original (generic-api-key heuristics, unchanged by the rewrite; session-token category is zero per the blob rescan).
- Hash citations: 129 distinct old full SHAs are cited in the rewritten main tip tree (698 distinct 40-hex strings total); all 129 resolve through the published commit-map.

## Purge test (live, throwaway private repo)

Procedure: created private repo phamTuan207/phase2-purge-test-20261128; committed a fake secret on main (d09d2ac7); branched, committed, opened PR #1 (95baee11, refs/pull/1/head created); rewrote history with filter-repo removing the secret; force-pushed both branches; closed the PR. Then from a fresh clone:

- `git fetch origin <old-main-sha>` **succeeded**; the old secret content was readable.
- `git fetch origin <old-feature-sha>` **succeeded**.
- GitHub API commit lookup for the old SHA **succeeded**.
- After PR closure the old SHA remained fetchable.

**Verdict (now evidence-based, not provisional): in-place filter-repo + force push does NOT purge old objects from GitHub.** Old commits stay fetchable by SHA indefinitely (GitHub serves them until its own GC or a Support purge, neither on our timetable). Therefore the mechanism must be **fresh repo** (new repo created from the rewritten history, old repo made private as the archive), which removes history from the public surface without depending on Support. The in-place variant is viable only if GitHub Support confirms the purge in writing beforehand; the fresh-repo variant needs no such confirmation. Costs of fresh repo: URL and PR-number continuity lost; public provenance replaced by the private archive plus published commit-map. The throwaway test repo remains private (delete_repo scope missing on the gh token); deleting it is a pending owner action.

## Private archive

Bundle of the full original history (247 MB, all refs) created and verified (complete history; restore clone reproduced both tips and 3,155 refs). Copies: VM ~/workspace/phase2-dryrun/original-history-archive-20261128.bundle and laptop ~/repo-archive-20261128/ (sha256 verified identical). The rewritten-history bundle and commit-map were also copied to the laptop for the independent review. Never on GitHub.

## What breaks (updated with dry-run measurements)

- Every commit hash changes (5,918 commits rewritten). 129 old full SHAs cited in the main tip tree need the commit-map; the research counted 41,226 hash-like citations across all trees (248 full SHAs across 1,094 files at that scope).
- Evidence files pinning old hashes break: 3 perf-evidence tests error (pinned-hash class). Fix: post-rewrite fix-up commit translating pinned hashes via commit-map.
- Patch files in history have context lines rewritten; tests that apply patches to pinned upstreams may break the same way (one glass-build patch failure observed in test output; the affected test was already in the pre-existing failure set on the original tip, so no new break measured).
- 813 open PRs must be closed or merged first (743 watchdog bulk-close approved; about 70 need triage). Under the fresh-repo mechanism PRs do not migrate.
- 1,074 remote branches; 55 VM worktrees plus off-VM clones (census still open) are recontamination vectors; every stale clone must be deleted, never pulled.
- Signatures stripped by filter-repo (documented side effect).
- Identity collapse: the dry run mapped every author/committer to one generic identity. Execution may instead map per-identity (owner to generic, others to their handles' noreply forms); owner to confirm at execution go-ahead.
- Guard carve-out: rung3-ci/arch-guard.py and rung3-ci/test-arch-guard.py must be restored post-rewrite (see defect 2 above).

## Execution plan (ready, not started)

Prerequisites:
1. Owner execution go-ahead (this dry run's report is the input).
2. Polygon session rotation by the owner, with proof.
3. GitHub email privacy enabled by the owner.
4. Freeze-tag disposition for R3-L1-FREEZE, R3-L1-FREEZE-2, R3-L2-FREEZE (R3-L3-FREEZE deletion already decided).
5. Identity policy confirm: full collapse (dry-run choice) vs per-identity mapping.
6. Phase 1 hygiene gate: research asked for one week of clean fleet pushes; owner may shorten explicitly.
7. Clone census: ask each agent directly (never assume); laptop copy of the archive already in place.

Execution window (fresh-repo mechanism):
1. Fleet freeze: stop every pusher by name (agents, crons, watchdogs); verify silence for at least two watchdog cycles.
2. Final bundle backup of all refs; verify; copy to laptop.
3. Close/merge all open PRs on the old repo (743 watchdog bulk-close; rest triaged).
4. Create the new repo under the same account; push the rewritten history (heads and tags minus R3-L3-FREEZE); restore the two guard files; land the pinned-hash fix-up commit (hash translation via commit-map); publish the commit-map in the new repo.
5. Make the old repo private. Update remotes everywhere.
6. Verification gates: fresh clone of the new repo, full-history audit returns zero for all categories; old hashes unfetchable from the new repo (they were never there); test shard matches the dry-run rewritten numbers or better; arch-guard PASS; CI green.
7. Re-clone protocol per agent and per machine (delete old clones); unfreeze only after every clone is confirmed new. Rollback: the bundle and the now-private old repo restore the original state.

**Time estimate:** dry run measured: clone 9 min, scan 12 min, rewrite 7-8 min per pass, rescan 7 min, test shard about 6 min per tip. Execution repo operation (fresh repo): 6-10h of agent work including freeze, archive, fix-up commit, verification, and re-clone protocol. The in-place variant would add Support purge wait time (outside our control) and is not recommended without written Support confirmation.

## Independent review

**FCC (laptop), 2026-11-28 ~17:05: PASS WITH NOTES.** The reviewer (who did not run the rewrite) verified from fresh bare clones of both bundles: commit-map tips match the rewritten refs (main 85c08dd6, todolist-push 516b6f64); R3-L3-FREEZE absent, other 3 freeze tags present; session-token shape 0; home paths reduced to generic placeholders only; Tailscale shape reduced to one non-personal range-base address; exactly one generic noreply identity; test deltas exactly as recorded (1788 both, fails identical, 57 vs 55 errors, 3 rewritten-only perf-evidence errors); both bundles verify as complete histories; purge-test logic sound, no hole found; execution plan consistent, no missing step found. Notes applied to this record: "zero hits" reworded to "zero personal values; generic placeholders remain"; ref-count figure corrected to bundle heads (3,156 original / 3,155 rewritten). Not re-verified by the reviewer (not failures): gitleaks 128-finding parity, 129-old-SHA citation resolution, 98-99% identity figure, time estimates.

## Pending owner actions

1. Execution go-ahead (or decline, which requires explicit sign-off accepting history exposure).
2. Polygon session rotation with proof (log out all sessions / change password; assume the historical value is burned).
3. GitHub email privacy: enable "Keep my email addresses private" and "Block command line pushes that expose my email."
4. Freeze-tag disposition for the other three tags; identity policy (collapse vs per-identity); Phase 1 week gate (keep or shorten).
5. Delete the throwaway private repo phamTuan207/phase2-purge-test-20261128 (gh token lacks delete_repo scope; contains only a fake secret).

## What did NOT happen in this dry run

No force push to the real repo. No branch or tag deletion on the real repo. No PR closing. No GitHub state change except creating the throwaway private test repo (and its PR, now closed). The real repo is untouched: main still at 284c6082, todolist-push still at cbcf3e1e.

*End of dry-run record. Research basis: improvements/repo-redo-research-20261128.md (66c8715b) and improvements/phase0-tip-scrub-outcome-20261128.md (cbcf3e1e).*
