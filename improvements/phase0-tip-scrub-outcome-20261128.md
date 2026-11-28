# Phase 0 tip scrub outcome (2026-11-28)

**Trigger:** repo redo + git history research (improvements/repo-redo-research-20261128.md, todolist-push 66c8715b), Phase 0: land the tip scrub on main by normal commits, no history rewrite.
**Owner decision recorded (2026-11-28 11:19):** make the repo's git history look professional and clean, no personal info leaked, written objectively and easy to understand so outsiders can use it as a tool. This sets the direction for Phase 2 as well: professional public history, zero personal info, outsider-friendly documentation.
**Redaction rule for this document:** no personal value is quoted. Findings are named by category plus file path only.

## What was scanned

Main tip tree at e7367d10, all files including the trees arch-guard previously skipped (improvements/, coord/, probes/, snippets/; rung3-run-log/ does not exist on main). Tools: arch-guard denylist patterns (personal-name, profile-dir, home-path, tailscale-ip) plus pii-scan categories (credential assignment, email, phone, known token prefixes, high-entropy, owner URLs). gitleaks is absent on the VM; CI runs gitleaks on PRs (passed on both PRs below).

## Exposures found at the tip (by category)

- Home street address category: 1 file (improvements/worker-y2b-agy-log.md, 3 lines). Scrubbed to a redacted placeholder, matching the redaction todolist-push already carries.
- Combined machine-spec line: 1 file (improvements/speed-prior-art.md). Genericized.
- Home-dir paths with a real username: 291 hits in improvements/ + coord/. Replaced with home-relative forms (~, %h in the systemd unit, expanduser in Python, HOME-based path in Lua).
- Personal name forms (spaced, hyphenated, diacritic): 173 hits in improvements/ + coord/. Replaced with a generic owner reference. Vietnamese common words that share a syllable with the surname (the words for "violation" and "scope") are not name references and were left intact; the guard pattern was refined in PR #1251 so they no longer false-positive.
- Zen profile dir names: 7 hits. Genericized, with distinct placeholders where a record contrasts two profiles.
- Tailscale-range addresses: 4 hits. Replaced with the documentation range address.
- Bare laptop username: 45 hits (window titles, ssh user@host forms, one loginctl match). Genericized; the loginctl match now compares against the runtime USER value.
- Nickname attributions: replaced with the generic owner reference where the nickname was used as a person reference (including three quoted memory-line fragments found by delta review). Vietnamese progressive and noun forms that share the same spelling were left untouched.
- Capitalized alias token in a vault title: 2 lines. Genericized.
- Emails at the tip: all fixture/example domains or GitHub noreply commit addresses. No personal mailbox at the tip.
- Phone-shaped strings: the owner-confirmed fake fixture plus color-coefficient floats in design/test files. No real phone number.
- Credential/token values at the tip: none found. All credential-pattern hits are prose about sessions/tokens; high-entropy hits are C++ mangled symbols in evidence diffs; owner-URL hits are public documentation sites.
- rung3-run-log/: not present on main. probes/ and snippets/: clean.

## Written exceptions (kept deliberately)

- The public GitHub handle (repo identity, clone URLs, noreply commit addresses): not a denylist hit per the arch-guard boundary decision (rung3-ci/arch-guard.py). Kept; scrubbing it from file contents would gain no privacy and would break references.
- GPU model mentions in benchmark records: test-condition metadata needed for reproducibility, not personal data. The one combined machine-spec line was genericized; standalone GPU model references in benchmark tables stay.
- School acronym in historical records: a public institution name, kept per the todolist-push scrub precedent (verifier GO with it kept). Listed here so the owner can re-decide.
- Frozen records inside arch-guard allowlist prefixes (docs/ frozen runs, test fixtures): unchanged, per the guard's own convention, including the owner 2026-11-27 exception for frozen watchdog-log lines.
- Quoted evidence text (commit subjects, log lines, memory-line quotes) in scrubbed files is genericized, not verbatim, after this scrub.

## What landed

- PR #1250 (tip scrub): merged a563e314 (commits b9d63756 + 21f53c85). 115 files in improvements/ + coord/. Two independent reviews: the first returned BLOCKING (line-wrapped common word, literal-tilde code paths, one record-accuracy contradiction, residual username/nickname); all fixed. Delta review found 3 remaining nickname-subject quotes plus a vault-title token; fixed in 21f53c85 before merge. CI: checks PASS, gitleaks PASS.
- PR #1251 (gate extension + identity CI): merged 284c6082 (commit 9ea04f55, restacked by merge c4bc3a75). arch-guard now scans improvements/, coord/, probes/, snippets/, rung3-run-log/ for the machine-value denylist; personal-name pattern refined for the two Vietnamese common words (unit tests added, 24 guard tests OK); new CI check requires noreply author/committer emails on PR commits (unit tests added). Delta review: MAY LAND, no changes needed. CI: checks PASS (including the new identity step), gitleaks PASS.
- Test shard on the scrubbed tree: SHARD MATCH, 1788 tests, ok=1711 error=54 fail=5 skip=18. Baseline 1785 (ok=1708 error=54 fail=5 skip=18); the +3 tests are PR #1245 additions, all passing. The 4-file delta-review fix after that run touches no test or script file (verified: no test references them).
- pii-scan delta on scrubbed files: 78 hits before, 78 after (all pre-existing false positives: session wording, example domains, color-coefficient floats, public doc URLs).
- Post-merge verification on main 284c6082: extended arch-guard PASS; zero home-address fragments; zero real home paths in the previously unscanned trees.

## Token rotation: owner action required

- Polygon session-token category: present in git history (tab-list evidence, scrubbed from the todolist-push tip in an earlier commit, never on the main tip). Not present at the current tip. Rotation status: NO PROOF FOUND. Owner action: rotate the Polygon session (log out all sessions / change password) and confirm, per research owner-decision item 5. Assume the historical value is burned.
- GitHub email privacy: recent merge commits on main still carry a personal mailbox as author (web-merge identity). Owner action: enable "Keep my email addresses private" and "Block command line pushes that expose my email" in GitHub settings, so future merges use the noreply form. The new CI check enforces noreply on PR branch commits; merge-commit author identity is controlled by the account setting.
- No other token/credential categories were found at the tip. History-wide rotation proof remains a Phase 2 input.

## What Phase 0 does not fix

History still contains the categories above (602 content-PII commits across all refs per the research). Phase 2 (gated rewrite or fresh-repo variant) remains owner-gated and out of scope here. Phase 1 (one week of clean fleet pushes with pasted scan evidence) starts now. Fleet note: the new CI identity check will fail PRs whose commits use non-noreply emails; set git config user.email to the noreply form before pushing.
