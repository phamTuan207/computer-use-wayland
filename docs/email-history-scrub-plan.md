# Plan to remove the leaked email from the entire git history

Status: plan only. Nothing in this file has been run. Do NOT run
filter-repo on the live repo, do NOT force push, do NOT rewrite any
history until the owner says go in the coord file.

## 1. Current state, checked 2026-11-21

- The leaked value is one real email address, in
  improvements/live-test-log.md line 3288, introduced in commit
  a46b3c68 on 2026-11-18. This plan never writes the address itself.
  It is referred to only as [email redacted], or by commit and line.
- Commit 1c7d252 deleted that line from current main. The file at
  HEAD has 0 matches for the address domain. The address is still in
  history: only 2 commits in all fetched history touch the string,
  a46b3c68 (added it) and 1c7d252 (removed it).
- Main has 445 commits at HEAD 2757ff1, checked 2026-11-21, 0 tags,
  .git is 6.0M. Main is NOT branch protected, so a force push is
  technically allowed. Re-check the commit count at run time; main
  keeps moving, and the expected rewritten count in section 7 is
  always the current count minus 1.
- One other ref still carries the leaked line at its tip:
  origin/todolist-push. origin/coord-clone2-setup (the head of open
  PR #1) has a clean tip now, checked 2026-11-21, but its history
  still contains commit a46b3c68, so it still needs the rewrite.
  Both branched from main before 1c7d252.
- There are 31 remote branches. A mirror clone fetches all of them,
  so the rewrite below covers them.
- git filter-repo is NOT installed on this machine. It must be
  installed before the run.

## 2. Freeze first, no exceptions

1. Post in coord/clone1.md and coord/clone2.md that a history
   rewrite is starting, and get confirmation from clone1, clone2,
   the VM, and the laptop that nobody has unpushed work and nobody
   will push until the rewrite is done.
2. Anyone with unpushed work must push it first, or the rewrite will
   orphan it. Check `git status` on every machine before proceeding.
3. Keep one pre-rewrite backup clone of origin/main on the laptop,
   offline, until section 7 verification passes. That backup is the
   rollback. Make it at /tmp/computer-use-wayland-backup, so section 7
   can read the old history from it. Delete it only after verification.

## 3. Install the tool

On the laptop, the machine that runs the rewrite:

```
pip install git-filter-repo
git filter-repo --version
```

Use pipx instead of pip if the laptop prefers it. Do not install it
inside the live repo. Any machine that only re-clones afterwards does
not need the tool.

## 4. Make a separate mirror clone

Never run filter-repo in the live working repo. Use a throwaway
mirror clone in /tmp:

```
cd /tmp
git clone --mirror https://github.com/phamTuan207/computer-use-wayland.git computer-use-wayland-scrub
cd computer-use-wayland-scrub
```

A mirror clone has all branches and no working tree, so the rewrite
covers every ref and cannot touch live work.

## 5. Build the replacements file without typing the address

The replacements file itself contains the literal address, so it must
never be committed, never be pushed, and must be deleted right after
the run. Build it mechanically from the known line, do not type the
address by hand:

```
git show a46b3c68:improvements/live-test-log.md | sed -n '3288p' | grep -o '[^ ]*@[^ ]*' > /tmp/email.txt
wc -l /tmp/email.txt
```

The count must be exactly 1. If it is not 1, stop and inspect the
line, because the extraction picked up the wrong text.

```
printf '%s==>[email redacted]\n' "$(cat /tmp/email.txt)" > /tmp/replacements.txt
```

The replacements file format is one rule per line:
literal text, then `==>`, then the replacement text. This rule replaces
the address with the placeholder [email redacted] in every file of
every commit.

## 6. Run the rewrite

In the mirror clone from section 4:

```
git filter-repo --replace-text /tmp/replacements.txt --force
```

What this does, and what to expect:

- It rewrites every commit that contains the address, across all
  branches, and drops the address from file contents.
- Commit 1c7d252 becomes empty in the rewritten history, because the
  line it deleted never existed there. filter-repo prunes empty
  commits by default, so rewritten main should have 444 commits,
  one fewer than the current 445 at HEAD 2757ff1. Re-check the
  current count at run time; the expected rewritten count is always
  the current count minus 1. Verify that exact count in section 7.
- filter-repo runs `git reflog expire --expire=now --all` and
  `git gc --prune=now` at the end, so the old objects are purged from
  the scrub clone.
- filter-repo removes the origin remote from the scrub clone when it
  finishes, as a guard against an accidental push. Re-add it before
  pushing:

```
git remote add origin https://github.com/phamTuan207/computer-use-wayland.git
```

- Delete the replacements file and the extracted address now:

```
rm /tmp/replacements.txt /tmp/email.txt
```

## 7. Verify the rewritten history before any push

Run all of these in the scrub clone, in one shell session. Every
check must pass. If any check fails, stop, do not push, and keep the
backup clone from section 2.

First, get the full address string into a shell variable, extracted
mechanically from the backup clone (section 2), which still has the
old history. Never type the address by hand, and never write it into
this plan. The scrub clone itself cannot provide it, because its
history is already rewritten. Do NOT use the domain alone for these
checks: the domain string also appears in doc commits 6599706,
6e57183, aeaa006, and 2757ff1, so a domain check can never return
empty after the rewrite. Only the full address string is unique to
the leaked line.

```
EMAIL=$(git -C /tmp/computer-use-wayland-backup show a46b3c68:improvements/live-test-log.md | sed -n '3288p' | grep -o '[^ ]*@[^ ]*')
echo "$EMAIL" | wc -w
```

The word count must be exactly 1. If it is not 1, stop and inspect
the extraction, because it picked up the wrong text.

```
git rev-list --count HEAD
```

Expected output: 444, one fewer than the 445 commits on main at
HEAD 2757ff1. Re-check the current main count at run time; the
expected rewritten count is always the current count minus 1.

```
git log --all --oneline -S "$EMAIL"
```

Expected output: empty. No commit in the rewritten history may touch
the full address string.

```
git grep "$EMAIL" $(git rev-list --all)
```

Expected output: empty. This greps the file contents of every commit
in every branch, not just the log.

```
git show HEAD:improvements/live-test-log.md | grep -c "$EMAIL"
```

Expected output: 0.

```
git for-each-ref --format='%(refname)' | while read r; do echo "$r $(git rev-list --count $r)"; done
```

Record the commit count per branch, and confirm every branch tip has
0 matches:

```
git branch -a | while read b; do git show "$b:improvements/live-test-log.md" 2>/dev/null | grep -c "$EMAIL"; done
```

Every line of output must be 0, or the file is absent at that tip.
Also confirm the rewritten main still contains the merge of
todolist-push, commit 96438bb, by checking that its subject is still
in the log:

```
git log --oneline --grep="merge todolist-push" -i
```

Expected output: the merge commit, with a new hash. If it is gone,
stop, the rewrite dropped history it should have kept.

## 8. Force push

Only after every check in section 7 passes, and only from the scrub
clone:

```
git push --force --all origin
```

There are 0 tags, so no tag push is needed. If tags ever appear later,
add `git push --force --tags origin`.

The old commits stay reachable on GitHub until the push completes.
After the push, the old main history is unreferenced on origin, but
anyone who already cloned the repo still has it locally. That is why
section 9 exists.

## 9. Re-clone order

Nobody may push from an old clone after the force push. Pushing from
an old clone would restore the leaked commits to origin. Order:

1. Laptop (owner): the rewrite machine. After the push, make a fresh
   normal clone for daily work, or keep working from a fresh clone
   made from the rewritten origin. Delete the old working clone.
2. Clone1: delete the old clone, make a fresh clone, confirm the
   full address string is gone before doing any work. The fresh clone
   cannot provide the address string itself, so extract it first
   from the OLD clone, before deleting it:
   `git -C <old-clone> show a46b3c68:improvements/live-test-log.md |
   sed -n '3288p' | grep -o '[^ ]*@[^ ]*' > /tmp/email.txt`,
   then in the fresh clone run
   `git log --all --oneline -S "$(cat /tmp/email.txt)"` and confirm
   it is empty, then delete /tmp/email.txt. Do NOT check the domain
   alone here either: the fresh clone contains doc commits that
   mention the domain, so a domain check would return matches even
   after a clean scrub. Only the full address string proves the
   leak is gone.
3. Clone2: same as clone1, fresh clone, same check, before any work.
4. VM: same as clone1, fresh clone, same check.

Do not skip the check on any machine. A machine that reuses an old
clone by mistake will push the old history back. If a machine cannot
re-clone at once, it must not push anything until it does.

## 10. Open PR #1 and the todolist-push branch

PR #1 is OPEN, head branch coord-clone2-setup, base main, state
MERGEABLE at the time this plan was written. Its head tip is clean
now, checked 2026-11-21, but its history still contains the leaked
commit a46b3c68, because it descends from main before 1c7d252.

- The `git push --force --all origin` in section 8 rewrites the PR
  head branch too, because the mirror clone contains it and
  filter-repo rewrites all refs. After the push, open the PR page and
  check two things: the diff no longer shows the address anywhere,
  and the PR is still mergeable. If either check fails, close PR #1
  and open a new PR from the rewritten head branch.
- Do not merge PR #1 before the rewrite. Merging first would put the
  leaked line into main through the merge, and the rewrite would then
  have to cover it anyway. Either merge after the rewrite, from the
  rewritten head, or close and reopen as above.
- todolist-push is already merged into main in commit 96438bb, so the
  branch itself is no longer needed. After section 7 confirms the
  merge is intact in rewritten main, and after all machines have
  re-cloned, delete it from origin:

```
git push origin --delete todolist-push
```

If the branch is kept for any reason, it must be the rewritten ref
from section 8, never the old ref. An old todolist-push ref pushed
back would reintroduce the leaked commits.

## 11. What this scrub cannot clean

- GitHub web caches of the old commit page for a46b3c68, and cached
  PR diffs. These usually expire, but the owner should check the old
  commit page after the push, and contact GitHub support if the
  address is still visible in a cached view.
- Forks of the repo. A fork keeps its own copy of the old history.
  Check the fork list before the run, and contact any fork owner.
- Any local clone, backup, or downloaded zip that already contains
  the old history. The scrub only cleans origin. Every holder must
  delete or re-clone.
- Email notifications or chat messages that quoted the line. Those
  are outside git and cannot be scrubbed from here.

## 12. Rollback

- Before the force push, rollback is trivial: delete the scrub clone
  in /tmp and nothing on origin has changed.
- After the force push, rollback is a force push of the old refs back
  from the backup clone in section 2. Only do that if section 7
  verification was wrong and real work was lost. Rolling back restores
  the leaked address to origin, so it must be followed by a fresh
  rewrite attempt, not left as the final state.

## 13. UNVERIFIED

- Installing git filter-repo was not tested on this machine. The tool
  is not installed here, and this plan was written, not run.
- The exact rewritten commit hashes cannot be known until the run.
  The expected count of 444 commits on main is a prediction from the
  empty-commit pruning rule, not a measurement. It was computed from
  445 commits at HEAD 2757ff1, checked 2026-11-21. Re-check the
  current main count at run time; the expected rewritten count is
  always the current count minus 1.
- Whether any fork of the repo exists was not checked.
- Whether clone2 or the VM hold unpushed work was not checked here.
  That must be confirmed in the coord files during the freeze in
  section 2.
- GitHub cache expiry for the old commit page and PR diffs is
  UNVERIFIED. Check the pages after the push.
- The commands in this plan were not executed. The first live run is
  the real test, on the laptop, from the mirror clone in /tmp.
