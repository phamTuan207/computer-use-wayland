# Repo redo research 2026-11-28: clone2 seat answer

Question put to the team: should we redo the
computer-use-wayland repo and rewrite its git history? Prior
audit (2026-11-23, git history PII audit) recommended REWRITE,
deferred until after R3-L3. R3-L3 is now closed, main is at
53e61e50, arch-guard reports 0 violations, CI is wired.

Honesty note: the 23/11 audit report file is not present on
clone2's VM (searched, not found), so this answer works from
its headline as relayed by the coordinator (REWRITE, deferred
until after R3-L3) plus clone2's own measurements taken
2026-11-28. The full audit was not re-read.

## 1. Verdict: hybrid

Fresh history for the future, old repo kept as the archive.
Not a filter-repo rewrite of the live repo.

The decision turns on what the redo is for, and the two goals
point different ways:

- If the goal is PII purge from history, a rewrite of this
  repo cannot deliver it. The tip is already clean (pii-scan
  gate green; the 2026-11-28 scrub rewrote 160 files on
  todolist-push; the skill files were scrubbed on main via
  PR #1140). The exposure is history-only, measured today:
  pickaxe over all refs finds the owner's name in the diffs
  of 311 commits (unaccented form), 13 commits for the
  accented form, 8 of those on main's own history. But this
  repo has 1,245 PRs, and GitHub keeps every PR's commits
  reachable under refs/pull/* regardless of branch rewrites;
  unreachable objects also linger, and every existing clone
  keeps the old history anyway. A filter-repo pass would pay
  the full breakage cost (every hash changes, every PR ref
  orphaned) and still leave the name fetchable by SHA in the
  same repo. That is the worst of both worlds.
- A fresh repo (new object store, initial commit equal to
  the scrubbed tree of 53e61e50) is the only form that
  actually removes the history from the public surface.
  Keeping the old repo alive, renamed and read-only, as the
  archive preserves hash resolvability for the entire study
  record. Whether the archive should also go private is the
  owner's call; the purge is only complete if it does.
- If the goal were only size or tidiness, the verdict flips
  to tip-only: 384 MB of .git and 5,071 commits across all
  refs (2,376 on main) are nothing git struggles with, and
  the pain-point audit shows the project's real costs are
  process costs, not repo costs.
- Timing: the 23/11 deferral condition is met (R3-L3
  closed), but a redo is a team-wide freeze: all lanes stop,
  re-clone, re-point tooling. It should run in one planned
  window after the pain-point meeting picks the build list,
  not interleaved with it. One constraint either way: the
  owner's 2026-11-27 exception for the 5 frozen watchdog-log
  lines was a deliberate keep decision; whichever home that
  file ends in, the exception should be honored or
  explicitly re-decided by the owner, not scrubbed by
  default.

## 2. What breaks for clone2 specifically

- Clones: 8 clone and worktree directories on clone2's VM
  and 50 worktrees registered on the main clone. Under any
  same-repo rewrite all of them are stale at once. Under the
  hybrid, clone2 re-clones once from the fresh repo and
  retires the spent review worktrees (p1, p2a, adopt-final,
  adopt-fix2, integration-review), which is owed anyway.
- Hash references: the big one. The improvements/ tree alone
  carries roughly 15,000 short-hash tokens across 637
  documents (upper-bound count; includes studies, reviews,
  lane files, coord logs) plus about 150 PR references, and
  clone2's local memory and every delivered review cite
  specific commits as evidence anchors (the zen-mcp adoption
  chain, the R17 proof, the queue pilots). Under a same-repo
  rewrite, every one of those citations dies unverifiable,
  and the reviews' core discipline (every claim traces to a
  commit) breaks retroactively. Under the hybrid, they stay
  resolvable in the archive. This is the decisive practical
  argument for keeping the old repo readable.
- Workflow: the watchdog runs on PR branches; clone2 has
  539 watchdog PRs open, of 796 open PRs repo-wide, and per
  the pain-point audit zero of them ever merged and the
  on-main log has been frozen since 2026-11-23. Losing them
  costs almost nothing; they are already dead weight. The
  coord-file protocol loses its in-repo history under a
  fresh start, but the live coord files carry forward in the
  initial import. Graphify is built over the working tree,
  so it survives any history decision (rebuild after the
  move regardless). The pii-scan gate, arch-guard
  (0 violations), and CI are all tip-based and carry over
  unchanged.

## 3. Structure: incremental cleanup, not a restructure

The code tree is not the problem: 45 MB working tree, 1,489
files on main, arch-guard at 0 violations, CI wired, 7,570
tests discoverable. A restructure would invalidate the
graphify graph, doc links, and every lane's path knowledge
for no measured gain. The structural debt is process
sediment, and it is measurable:

- 1,061 remote branches. Cleanup target: delete merged and
  stale lane branches, keep a handful.
- 796 open PRs of 1,245 total (64 percent never closed),
  most of them watchdog noise. Bulk-close the dead watchdog
  PRs.
- docs/ is 20 MB of the 45 MB tree, mostly the watchdog log
  and run logs; improvements/ is 189,554 lines with
  deliberation at about 45 percent (pain-point audit, lane A
  recount). Logs and lane scratch should stop being
  committed to the code repo at all; move them to the
  archive or local-only storage.
- All of this is doable incrementally with no history
  surgery, and if the hybrid route is taken, the fresh repo
  should import the cleaned tree, not the sediment.

Net: hybrid (fresh repo from the scrubbed tip, old repo
archived read-only), cleanup incremental and starting now,
restructure no.
