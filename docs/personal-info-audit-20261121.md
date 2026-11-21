# Personal info audit, 2026-11-21

Audit date: 2026-11-21. Repo: computer-use-wayland. Local HEAD at audit
time: 1c7d252, remote main in sync at the same commit. This report contains
no real personal values. Every finding is recorded by type, file, line, and
commit only, with values redacted.

## Scope and method

- All 32 refs scanned: local main plus origin/HEAD and 30 remote branches
  (a2-preflight, action-grouping, algo-a4, cascade-local-model,
  change-only-obs, cli-anything-integration, coord-clone2-setup, det-finish,
  effort-dial, event-wait-seq, harness-drop-old-shots, harness-hyprctl-batch,
  harness-jpeg-q90, harness-prefetch, harness-warm-browser,
  harness-warm-browser-land, instrfix, latency-probe, lowres-obs,
  pill-bottle-fix, pill-shayxo-fix, rust-rewrite-eval, speed-swarm,
  speed-swarm-brokerfix, speed-swarm-masking, speed-swarm-pick1fix,
  speed-swarm-pick1p34fix, speed-swarm-pick4a11y, todolist-push, vault-move).
- Patterns searched with git grep on every branch tip: email addresses,
  Vietnamese and generic phone numbers, GitHub tokens, OpenAI keys, AWS keys,
  Slack tokens, private key blocks, password and secret assignments, the
  user real name (full name and common short forms), school schedule phrases,
  and home address phrases.
- Every match was printed only in masked form (type, file, line, and a
  redacted placeholder). All 36 unique pattern matches were then classified
  by hand from masked context (surrounding words, file type, match length and
  shape). Counts below count branch tips separately, so one line present in
  many branches counts many times. The main tip table is the authoritative
  list for the current state of main.
- Raw scan totals: 1075 regex matches across all branch tips, of which 167
  are placeholder values and 908 matched a real-looking pattern. After
  classification, almost all of the 908 are false positives (see section 4).
  Two real leaks were found (sections 1 and 2).

## Summary

| Finding | Type | Status on main | Status elsewhere |
| --- | --- | --- | --- |
| 1 | Real name | LIVE, 71 lines in 45 files | 1427 lines across 31 branch tips |
| 2 | Real email, domain gmail.com | FIXED in 1c7d252 | Still in history from a46b3c68, and at the tip of 25 branches |

No real phone number, password, token, private key, home address, or
personal schedule was found anywhere in the repo.

## 1. Real name, LIVE on main

- Type: real name (full name and short form).
- Main tip: 71 lines in 45 files. Full list:
  - coord/clone1.md:3, coord/clone2.md:3
  - docs/cli-anything.md:32, docs/zen-error-fix-todolist-20261121.md:2
  - improvements/a1-code-exec-dom-design.md:3
  - improvements/brokerfix-report.md:3
  - improvements/det-finish-implementation.md:3, 187
  - improvements/dom-replication-interim-20261119.md:3, 7, 14, 30
  - improvements/live-test-log.md:3987, 4089, 4150, 4155, 4195, 4196
  - improvements/pick1-p34fix-report.md:4, 74
  - improvements/pick2-executor-brief.md:3, 4
  - improvements/pick4a11y-fix-report.md:3
  - improvements/speed-prior-art.md:4
  - improvements/speed-proto-pick1.md:3
  - improvements/speed-proto-pick2-rerun.md:3
  - improvements/speed-proto-pick2.md:3
  - improvements/speed-proto-pick3.md:3
  - improvements/speed-proto-pick4-arm2-summary.md:3
  - improvements/speed-proto-pick4-baseline-browser.md:3
  - improvements/speed-proto-pick4-summary.md:3
  - improvements/speed-proto-pick4.md:3
  - improvements/speed-swarm-profile.md:4
  - improvements/speed-swarm-prototype-plan.md:5, 107
  - improvements/speed-swarm-report.md:4, 485, 514, 542, 554, 558
  - improvements/speed-swarm-rerun-plan.md:4, 31, 104, 108
  - improvements/summary-a1-landing.md:3, 4
  - improvements/summary-a1-remeasure.md:3
  - improvements/summary-envelope-validator-fix.md:3
  - improvements/summary-g1-sidebar.md:5
  - improvements/summary-pick1-landing.md:4, 5
  - scripts/zen_cli.py:22, 202
  - skill/cli-anything/chromium.md:40, skill/cli-anything/zen.md:42
  - tests/realistic/fcc-k/README.md:3
  - tests/realistic/fcc-k/fixtures/test-08-form.html:29, 35, 38
  - tests/realistic/fcc-k/test-01-spreadsheet-formula.md:10, 11
  - tests/realistic/fcc-k/test-02-email-triage-reply.md:10
  - tests/realistic/fcc-k/test-03-calendar-conflicts.md:10
  - tests/realistic/fcc-k/test-04-research-notes.md:10
  - tests/realistic/fcc-k/test-05-image-organize-rename.md:10
  - tests/realistic/fcc-k/test-06-settings-two-apps.md:10
  - tests/realistic/fcc-k/test-07-bug-reproduction.md:10
  - tests/realistic/fcc-k/test-08-form-validation-fix.md:10
  - tests/realistic/fcc-k/test-09-copy-format-convert.md:10
  - tests/realistic/fcc-k/test-10-long-document-edit.md:10
- Forms it takes: Owner headers on improvement reports, possessive use in
  code and docs (for example the safety note in scripts/zen_cli.py about the
  owner own Zen), assignment intros in coord/clone1.md and coord/clone2.md,
  prose mentions in live-test-log.md, and a fullName test value in the
  test-08 form fixture (a realistic test that uses the real name as sample
  data, which is the most directly fixable case).
- Since which commit: at least 2026-11-18. Blame samples:
  scripts/zen_cli.py:22 goes back to commit 2045020 (2026-11-18),
  improvements/a1-code-exec-dom-design.md:3 goes back to commit 3f29fe3
  (2026-11-19).
- Across branches: 1427 name lines across 31 branch tips. Most of these are
  the same files carried across branches, not 1427 distinct leaks.
- Fixed: NO. Still live on main.
- Why not fixed in this audit: the name sits in 45 files on main, including
  coordinator-owned coord/clone1.md and coord/clone2.md (which this audit
  was told not to edit) and in-flight reports other workers are using. A
  blanket redaction would touch assignment text and active work, so it needs
  a coordinator decision on the replacement wording (role label instead of a
  name, for example), the same decision class as the history purge in
  section 2. The test fixture value in test-08-form.html is the one isolated
  fix that needs no decision.
- Note: the GitHub handle phamTuan207 as commit author and remote URL is
  NOT counted as a leak. It is a public account handle, public by the nature
  of GitHub, not a real name.

## 2. Real email, FIXED on main, still in history and other branches

- Type: real email address, domain gmail.com. Value redacted everywhere in
  this report.
- File and line: improvements/live-test-log.md:3288, in a D3-EXECUTE log line
  recording a git config check.
- Introduced: commit a46b3c68, 2026-11-18 ("speed: sync live-test-log").
  A history-wide pickaxe search for the email domain shows only two commits
  touching it in the whole repo history: a46b3c68 (introduced) and 1c7d252
  (removed). The address never appeared in any other file.
- Fixed on main: YES, commit 1c7d252, 2026-11-21 ("clone1: remove leaked
  email line 3288 from live-test-log.md"), which deleted the line.
  Verified: a grep for the email domain on origin/main after that commit
  returns no real address.
- NOT fixed: the address is still in git history from a46b3c68 onward, and it
  is still at the tip of 25 branches: a2-preflight, action-grouping, algo-a4,
  cascade-local-model, change-only-obs, coord-clone2-setup, det-finish,
  effort-dial, event-wait-seq, harness-drop-old-shots, harness-hyprctl-batch,
  harness-jpeg-q90, harness-prefetch, harness-warm-browser,
  harness-warm-browser-land, instrfix, latency-probe, lowres-obs,
  pill-bottle-fix, pill-shayxo-fix, speed-swarm, speed-swarm-brokerfix,
  speed-swarm-pick4a11y, todolist-push, vault-move.
- Removing it from history needs a history rewrite with force push, and the
  25 branch tips above would need to be rebased or deleted after the purge.
  That step was already planned by the coordinator and is not done here.
  No history was rewritten in this audit.

## 3. Zero findings

These patterns were searched repo-wide across all 32 refs and found nothing
real:

- Phone numbers: no real phone number. The Vietnamese mobile pattern
  (plus 84 or 0 plus a 3, 5, 7, 8, or 9 prefix) had zero matches.
- Passwords and secrets: no password, api key, access token, or secret
  assignment with a real value.
- Tokens: no GitHub token (ghp, gho, ghu, ghs, ghr, or github_pat), no AWS
  key, no Slack token.
- Private keys: no private key block.
- Home address: no street address, house number, ward, or district.
- Personal schedule: no school schedule or personal calendar. The only
  schedule words found are in the ban text itself in coord/clone1.md:43 and
  coord/clone2.md:56, which lists the categories that must never be pushed,
  not any actual schedule.

## 4. False positives investigated and cleared

- "sk-" tokens, 5 unique lines: improvements/dom-replication-interim-20261119.md:20,
  improvements/live-test-log.md:4197, 4198, 4338, 4393. Every match is 15
  characters long and sits inside a ".json" filename in a log line (a task
  verification filename). A real OpenAI key is 48 characters or longer, so
  none of these is a key.
- Ten digit strings matching a generic phone pattern, 29 unique lines. All
  are decimal fractions, not phone numbers:
  - Oklab color matrix coefficients (digits after a decimal point) in
    improvements/pill-shayxo-port-design.md (8 lines),
    native/hyprglass-shayxo-legacy.patch (8 lines), and
    tests/test_glass_shayxo_contract.py (8 lines).
  - The sequential digit string 0123456789 used as sample data: a
    readability test sample in improvements/live-test-log.md:2902, the
    allowed character set in a duration check in native/indicator.c:471
    (the same string also appears at indicator.c:343 on some branch tips
    where line numbers differ), and a fuzz test string in
    tests/test_cursor_session.py:555.
- Email pattern in docs/research/2026-11-21-atspi-desktop-control.md:58:
  a public mailing list archive URL on lists.debian.org, not a personal
  address.
- Placeholder emails, 167 matches across branch tips: example.com,
  example.local, example.invalid, example.org, users.noreply.github.com,
  and test or demo local parts. None is a real address.

## 5. What this audit did not cover (UNVERIFIED)

- Binary files: git grep skips binary content, so text hidden in images,
  screenshots, or other binary files was not scanned.
- Historical versions of files: branch tips were scanned in full, and the
  email was traced through history with a pickaxe search, but every
  historical version of every file was not individually grepped. A name or
  address that was added and then removed from a file before the branch tip
  would only be found by the pickaxe check, which was run for the email
  domain only.
- Untracked or ignored files on any machine: the working tree was clean at
  audit time, so there was nothing untracked to scan here. Files that exist
  only on other machines were not scanned.
- Values that do not match the searched patterns: a phone number in an
  unusual format, or personal info written without a standard pattern, would
  not be caught by regex.

## 6. Recommended actions

1. Decide the redaction wording for the real name (section 1) and apply it
   to the 45 files on main, then to the other branch tips or by deleting
   stale branches. Easiest first step: replace the fullName test value in
   tests/realistic/fcc-k/fixtures/test-08-form.html with a clearly fake name.
2. Run the planned history purge for the email (section 2), then rebase or
   delete the 25 branch tips that still carry the line.
3. Add a pre-push check for the patterns in section 3 so a new leak is
   caught before it reaches the public repo. The owner headers that
   reintroduce the name on every new report are the main source to block.
