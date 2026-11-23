# PII prevention

## What was installed and why

Past leaks happened because the only protection was a written instruction telling agents not to commit personal data. A written instruction is the weakest layer: it can be forgotten, misread, or bypassed by a prompt injection, and it cannot stop a commit by itself. This stack moves the guarantee up to deterministic checks that run as code, locally before the commit and again on the server where no agent can skip them.

There are five layers in the research report (section 5). Four are installed in this repo; the fifth, sandboxing, is deliberately not installed (see below). Each installed layer catches what the layer above it missed.

### Layer 1: CI secret scan (the enforcement)

The `.github/workflows/secret-scan.yml` workflow runs gitleaks over the pushed commits only (pull-request base to head, or the push range) on every push and pull request, with a pinned gitleaks v8.30.1 binary and the scan config pinned to the version from before the push (or from the PR base branch), never the version in the pushed commits. On a new-branch push the push event has no before SHA, so the base is the newest merge-base of HEAD with the todolist-push and main integration branches (this repo lands via todolist-push, not main, so main alone gives an ancient merge-base and the gate would fail on old-history findings); an explicit base ref can also be passed via workflow_dispatch. The first PR introducing the config falls back to the reviewed config in HEAD when the PR base has no `.gitleaks.toml` yet, and to the default gitleaks config when HEAD has none either. CI runs on GitHub servers, not on an agent machine, so `git commit --no-verify`, a missing `pre-commit install`, or a disabled hook cannot bypass it. The `secret-scan / gitleaks` job is already a required status check on main (set 2026-11-23), so a push to main is blocked until the pushed SHA has a green check. This layer is the enforcement; the local hook is only feedback.

### Layer 2: pre-commit hook (fast local feedback)

The `.pre-commit-config.yaml` file wires hooks that run before every commit: gitleaks v8.30.1 with the shared `.gitleaks.toml` config, TruffleHog v3.99.9 as a local hook running the trufflehog binary with `--results=verified,unknown --fail`, and a local exact-values hook (`scripts/check-pii.sh`). Gitleaks catches known-format credentials plus custom PII patterns (personal email, street address, phone number, private IP). TruffleHog adds live verification against provider APIs, which cuts false positives; `unknown` results also block, so an offline commit does not silently pass when verification cannot run. The exact-values hook catches specific known personal values that no pattern can express, such as an address in a format no regex covers. A pre-push hook (`scripts/check-pre-push.sh`) runs gitleaks over the pushed range plus the exact-values grep over the pushed diff, as a second local net for commits made with `--no-verify` or before the hook was installed. A commit-msg hook (`scripts/check-pii-msg.sh`) greps the commit message for the exact values and runs gitleaks over the message text. This layer is fast feedback in seconds, on the machine doing the commit.

### Layer 3: GitHub push protection and secret scanning (already enabled)

GitHub push protection plus secret scanning are already enabled on this repo (verified 2026-11-23). They catch supported credential formats at push time as a second server-side net, and alerts cover the whole history. Limit: they catch credentials, not a home address or a personal email. Push protection is a net for tokens, not a net for personal data, and anyone with write access can bypass a push-protection block by giving a reason. Do not count this as a PII layer.

### Layer 4: ignore entries and synthetic fixture data (design)

The `.gitignore` additions (`.claude/settings.local.json`, `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`, `secrets.json`, `sensitive-values.txt`) stop an accidental `git add` from sweeping a local secret file into the tree. An ignore entry is a tripwire, not a security boundary: it does not stop an agent from reading the file, only from committing it. The fixture rule below fixes the address leak at its root: fixtures contain only generated fake data, so any realistic-looking value in a fixture is a violation by definition, because a scanner cannot tell a real address from a realistic fake one.

## One-time setup (every agent, every machine)

Install the two scanner binaries on PATH first. The TruffleHog local hook and the pre-push and commit-msg hooks call the binaries directly, so they fail closed (block the commit or push) when a binary is missing:

```
# gitleaks v8.30.1
curl -sL -o /tmp/gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
tar -xzf /tmp/gitleaks.tar.gz -C /tmp gitleaks
sudo mv /tmp/gitleaks /usr/local/bin/gitleaks

# trufflehog v3.99.9
curl -sL -o /tmp/trufflehog.tar.gz https://github.com/trufflesecurity/trufflehog/releases/download/v3.99.9/trufflehog_3.99.9_linux_amd64.tar.gz
tar -xzf /tmp/trufflehog.tar.gz -C /tmp trufflehog
sudo mv /tmp/trufflehog /usr/local/bin/trufflehog
```

Then run this once in the repo root:

```
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg
```

Without this step the local hooks never run, because hooks live in `.git/hooks` and do not travel with the repo. A fresh clone has no hooks until these commands run. The CI layer still protects the repo when this step is skipped, but the fast local feedback is lost.

## First run: build time and disk space

The first `pre-commit run` builds the gitleaks hook environment from source and took about 18 minutes on this VM (1.5 shared CPUs). Later runs reuse the installed environment and take seconds. Two things to know before the first run:

- `/tmp` on this VM is a 512M tmpfs. The build fails there with no space left, so before the first run, point the temporary and Go build directories at the home disk, for example `export TMPDIR="$HOME/.cache/pre-commit-tmp" GOCACHE="$HOME/.cache/go-build" GOTMPDIR="$HOME/.cache/go-tmp"`, and run the clone from the home disk, not from `/tmp`.
- Do not conclude the hooks are broken because the first run is slow. Wait for the build to finish, then re-run; a clean commit passing is the proof the hooks work.

## How each layer works and its limits

- Local hook: runs gitleaks over staged changes, TruffleHog verified-plus-unknown, and the exact-values grep over added lines of the staged diff. It blocks the commit with exit code 1 on a finding. Limit: it is bypassable with `git commit --no-verify`, or by never running `pre-commit install`. Treat a bypassed hook as a process failure, not as a clean commit. A value already in a file on an untouched line is missed by the staged-diff scan; the pre-push hook, CI, and the weekly sweep are the nets for that case.
- Pre-push hook: runs gitleaks over the pushed commit range and the exact-values grep over the pushed diff. It catches commits made with `--no-verify` or before the pre-commit hook was installed. Limit: like every local hook it is skippable, so it is defense in depth, not enforcement.
- Commit-msg hook: greps the commit message for exact known values and runs gitleaks over the message text. Limit: it only runs locally, so a message pushed with `--no-verify` is caught late, by CI, after the value is already on the branch.
- CI: runs gitleaks over the pushed range only (PR base to head, or the push range) on push and pull request, with the config pinned to the pre-push version. Limit: it runs after the push, so a leaked value can sit in a pushed branch until the check fails and the branch is fixed. It is the enforcement layer, not the fast layer. A config change in a push takes effect on subsequent pushes, because the gate pins the pre-push config; config changes need human review, and the outside exact-values list cannot be weakened by a push at all, since it lives outside the repo.
- Weekly sweep: the `secret-scan-history` workflow runs every Monday 06:00 UTC plus on demand, scanning the full history and the working tree in dir mode (which sees binary files). It is not a required check. A red run is the signal that starts triage; it blocks nothing. At landing time the full-history scan reports 413 findings, mostly false positives of the deliberately broad custom rules; triage of those is a separate task.
- Binary files: git patches never show binary content, so the staged-diff hook, the pre-push hook, and CI git-mode all miss a value inside a `.pyc`, database, zip, or image metadata. The weekly sweep dir-mode step scans raw bytes and catches some of these. There is no pre-commit hook rejecting binary files yet.
- GitHub push protection: catches supported credential formats at push time. Limit: it catches credentials, not a home address or a personal email. It is a net for tokens, not a net for personal data. Anyone with write access can bypass a push-protection block by giving a reason.
- Exact-values hook: greps added lines for literal values from a list that lives outside the repo. Limit: it only catches values that are on the list. A new personal value that was never added to the list is not caught by this hook, only by the pattern rules, if it matches one. A re-spaced, re-punctuated, or split-across-lines value does not match the literal grep.
- Street regex: US-only by design (number first, up to 4 name words, capitalized US street suffix). It misses non-US formats, lowercase suffixes, suffix-less addresses, and number-last addresses. The exact-values hook covers listed values in any format. Never put a real street name into a regex; the config itself would become the leak.
- TruffleHog offline: verification needs network. With `--results=verified,unknown`, a verification that cannot run still blocks instead of silently passing. Disclosure: TruffleHog sends candidate credentials to vendor APIs for verification, so a value that matches a detector is sent off-machine. Gitleaks is the offline layer; it never sends anything anywhere.

## Synthetic-only fixture data rule

All test fixtures, examples, demonstrations, and CI runs use synthetic data only. Never copy a value from a real record, a real person, or a real machine into a fixture, even masked or de-identified. Use Faker libraries or factory functions with a fixed deterministic seed, and use only reserved placeholder values: example.com, example.net, example.org, or .test / .example / .invalid domains for emails and web addresses; phone numbers 555-0100 to 555-0199; the placeholder address 123 Main Street. Every fixture file states at its top that its data is synthetic. This rule is the only control that fixes the address leak at its root, and the scanners in layers 1 and 2 enforce it.

## Layer 5 not installed, and why

The research report describes a fifth layer, sandboxing and environment separation, where the agent physically cannot read personal files because they are not in its environment. That layer is NOT installed here. It conflicts with the fleet standing rule of full access for agents, and this repo does not impose a sandbox or a separate workspace on the fleet. That tradeoff is explicit: with no read boundary, layers 1 to 4 above must carry the whole guarantee. If full access ever changes, revisit sandboxing first, because it is the strongest layer.

## The outside exact-values list

The exact-values hook reads a list of literal sensitive values from outside the repo, one value per line, at:

```
$HOME/.config/computer-use-wayland/sensitive-values.txt
```

That file is never committed and never lives in the repo. A separate setup step creates it on each machine that commits to this repo. The hook is fail-closed: if the list file is missing, the commit is blocked with exit code 1 rather than silently allowed. Do not create a copy of the list inside the repo, in a commit message, in a log, or in any report. The list itself is sensitive data.

## What to do when the hook blocks a commit

1. Read the hook output. It names the rule that fired (for example, personal-email, street-address, private-ip, or the exact-values hook).
2. Remove the flagged value from the staged files. Replace it with a reserved placeholder (example.com address, 555-0100 to 555-0199 phone, 123 Main Street, RFC 5737 documentation IP such as 192.0.2.1) or delete the line.
3. If the value is a real credential, rotate or revoke it first, then remove it. Removing it from the tip does not remove it from history.
4. If you believe the flag is a false positive, check the allowlist in `.gitleaks.toml` first. The allowlist is narrow by design: placeholder domains, the 123 Main Street placeholder, 555-01xx phones, and RFC 5737 documentation IPs. Do not widen an allowlist to cover a whole directory, and never add a blanket exemption for tests or fixtures. That is exactly where a real value would hide.
5. Do not bypass the hook with `--no-verify` to get past a block. If a block looks wrong, fix the value or fix the rule, and let the CI layer confirm it.

## Main-merge caveat (current state, verified 2026-11-23)

The required status check `secret-scan / gitleaks` is ALREADY set on main, with enforce_admins true, and force pushes and deletions blocked. PRs are NOT required, and direct pushes to main are allowed when the pushed SHA already has a green check. The landing path is therefore: push the change to the `todolist-push` branch first (unprotected), wait for `secret-scan / gitleaks` to go green on that SHA, then push that same SHA to main. A brand-new commit pushed directly to main has no green check on its SHA and stays blocked until the workflow file is on main. Do not land the workflow file to main until a push to `todolist-push` has gone green with the fixed workflow.

Land only the PII files, with an explicit pathspec, in one commit: `.pre-commit-config.yaml .gitleaks.toml scripts/check-pii.sh scripts/check-pre-push.sh scripts/check-pii-msg.sh .github/workflows/secret-scan.yml .github/workflows/secret-scan-history.yml docs/pii-prevention.md .gitignore`. Never use a bare `git add -A` or a `git commit` with no pathspec: a plain commit sweeps in any other staged file, including another worker's change.
