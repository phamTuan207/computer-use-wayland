# Council Voice 1 paper: provenance and authenticity of fetched hyprglass commit 03a57c4

- Voice: Council Voice 1, provenance and authenticity only.
- Subject: fetched commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd, claimed upstream hyprglass v1.1.1, 2026-11-03.
- Baseline: HEAD 99f30ca, claimed upstream hyprglass v0.9.1, 2026-10-03.
- Reviewer role: read evidence only. No commit, no checkout, no build, no load, no run of anything from the fetched commit, and no git command inside the vendor repo.
- Date: 2026-11-21, review written after Y6e log entries timed 21:26 to 21:31 +07.
- Verdict: AMEND. See section 5 for the exact check that closes it.

## 1. What I read

- improvements/worker-y6e-rebuild-load-log.md, read in full first.
- improvements/y6e-evidence/diff-99f30ca-03a57c4.txt, checked by grep and line reads, not by trusting the log summary.
- improvements/y6e-evidence/Makefile-pin, Makefile-diff.txt, hyprpm-pin.toml, workflows-diff.txt, hyprland-version-pin, scan-added.txt, scan-removed.txt.
- scripts/build-glass.py, pin lines only (lines 17 to 18, 58 to 59, 67 to 68, 80).

## 2. Claims I verified myself from the evidence files

### 2.1 The diff file is intact and matches the log counts exactly

- md5 of improvements/y6e-evidence/diff-99f30ca-03a57c4.txt is 71ee7ccaef91e73bc61dd1cbebd8e521, identical to the log claim.
- Size 543,272 bytes, 10,070 lines, identical to the log claim.
- 54 `diff --git` headers, matching the log claim of 54 files.
- Added lines: 5,041 lines starting with `+`, minus 54 `+++` file headers, equals 4,987 insertions. This matches the log claim of 4,987 insertions exactly.
- Removed lines: 1,489 lines starting with `-`, minus 54 `---` file headers, equals 1,435 deletions. This matches the log claim of 1,435 deletions exactly.
- The file list is the standard hyprglass layout plus the new files the log names. Non-source files in the diff are .github/workflows/ci.yml, hyprland-update.yml, release.yml, .hyprland-version, CHANGELOG.md, Makefile, README.md, hyprpm.toml. No unexpected top level file appears.

### 2.2 The CHANGELOG chain is internally coherent

In improvements/y6e-evidence/diff-99f30ca-03a57c4.txt, added CHANGELOG headers, in order:

- Line 93: v1.1.1, compare v1.1.0 to v1.1.1, 2026-11-03. Single fix: glass refreshes over video and other GPU-rendered backgrounds, issue 102.
- Line 100: v1.1.0, compare v1.0.0 to v1.1.0, 2026-10-30. Fixes cite issues 98 and 99.
- Line 128: v1.0.0, compare v0.11.0 to v1.0.0, 2026-10-30. Hyprland 0.57 support, issue 100.
- Line 158: v0.11.0, compare v0.10.0 to v0.11.0, 2026-10-19. Credits to Eddie175.
- Line 190: v0.10.0, compare v0.9.1 to v0.10.0, 2026-10-09.

The version chain is continuous with no gap and no duplicate: v0.9.1 to v0.10.0 to v0.11.0 to v1.0.0 to v1.1.0 to v1.1.1. Dates increase monotonically. The compare links use github.com/Hyprnux/hyprglass throughout. The v1.0.0 section also records the pin chores for hyprland 0.56.2 to v0.11.0, v0.10.0, v0.9.1 and v0.9.0, which is consistent with a release automation backfilling pins.

### 2.3 The Hyprland version move is coherent across three files

- diff lines 80 to 86: .hyprland-version changes from 0.56.2 to 0.57.0. hyprland-version-pin contains 0.57.0, confirming the pin side.
- diff lines 970 to 982: hyprpm.toml changes the hyprland 0.56.2 pin from hyprglass v0.8.1 (hash 725383e86a2a79457a81cdbc2ceb33c07363bd8d) to v0.11.0 (hash 7fc328064c63d9fbaaac8d8204eadf85dcdeae19).
- hyprpm-pin.toml line 25: the last commit_pins entry is hyprland 0.56.2 to hyprglass v0.11.0, hash 7fc328064c63d9fbaaac8d8204eadf85dcdeae19. This confirms the log claim that the pin table ends at 0.56.2 to v0.11.0, with no pin for any Hyprland 0.57.x line.
- The README in the diff (line 299) instructs `git checkout hyprland-0.57`, and the release workflow changes in workflows-diff.txt require BUILT_FOR_HYPRLAND_GIT to be false on a stable line. The diff adds src/BuildChannel.hpp at line 1185 with `BUILT_FOR_HYPRLAND_GIT = false`, which is the stable-line value the workflow demands. These four pieces agree with each other.

### 2.4 The build script pins the same hash

- scripts/build-glass.py line 17: REQUIRED_COMMIT is 03a57c4451b4abee38feda2ffb725f55ecc0f2fd, the full form of the pin in the task and the log.
- scripts/build-glass.py lines 58 to 59: the script refuses to run unless HEAD equals that hash. So the hash that gets built is the hash under review here, not a branch name that could move.
- scripts/build-glass.py line 18: REQUIRED_HYPRLAND is 0.57.2. This is a separate fact from the vendor version file, and it is where the version lag in section 3.3 matters.

## 3. Findings

### 3.1 No positive evidence of tampering in the evidence pack

Nothing I re-read contradicts the claimed upstream story. The counts match exactly, the CHANGELOG chain is continuous, the version move is consistent across .hyprland-version, hyprpm.toml and the workflows, and the README, CHANGELOG and workflow text all point at the same vendor, Hyprnux, and the same repository path, github.com/hyprnux/hyprglass. The scan files corroborate the issue numbers and the 0.57 move, for example scan-added.txt lines 93 to 183 carry the same v1.1.1 to v0.11.0 entries.

### 3.2 The core provenance facts rest on the log alone, and I could not re-verify them

This is the material gap. The following claims appear only in the Y6e log, and the evidence pack as handed to me contains no independent record of them:

- Remote origin is https://github.com/hyprnux/hyprglass.git.
- HEAD is 99f30ca, 2026-10-03, github-actions[bot], "chore(release): v0.9.1 [skip ci]".
- The pin is 03a57c4, 2026-11-03, github-actions[bot], "chore(release): v1.1.1 [skip ci]".
- The commit range history between them, including merges into hyprland-0.57 and the release flow.

A diff file carries no commit metadata, no author, no date, no parentage and no remote URL, so none of those claims can be checked from the diff. My brief forbids git commands inside the vendor repo, so I cannot re-run the log or show commands that would have produced that record. The log is a single-source claim for the facts that matter most to this voice: that this hash came from that remote, and that it is the upstream v1.1.1 release commit.

### 3.3 No tag points at the pin locally, and the vendor pin table does not cover this pairing

- The log states no tag points at the pin locally, because the clone is shallow and tags were not fetched. I have no tag list in the evidence pack to check this against, but nothing in the pack contradicts it, and the consequence stands on its own: the link between tag v1.1.1 and hash 03a57c4 is unverified in local evidence.
- hyprpm-pin.toml ends at hyprland 0.56.2 to v0.11.0. The vendor's own pinning system has not paired any commit with Hyprland 0.57.x. The pin under review is a v1.1.1 commit whose own .hyprland-version is 0.57.0, while the laptop runs Hyprland 0.57.2 and build-glass.py requires 0.57.2. This is not evidence of forgery. It is evidence that building this commit against 0.57.2 is outside the vendor's published pinned matrix, so the vendor has not endorsed this exact pairing. The runtime version guard is Voice 2 and Voice 3 territory, not mine, but the provenance record must state the gap plainly.

### 3.4 The release-bot author proves nothing by itself

Both endpoint commits are attributed to github-actions[bot] with the same "chore(release): vX.Y.Z [skip ci]" message shape. That shape is consistent with release automation, and it is also exactly the shape an attacker with repository write access, or a compromised workflow, would produce. A bot author is not a signature and not an identity check. No GPG signature, signed tag, or release artifact hash appears anywhere in the evidence pack.

## 4. Attack analysis: what could make this commit not what it claims to be

### 4.1 Fetch tampering or a poisoned local clone

Attack: the local vendor checkout was fetched over a tampered connection, or from a lookalike remote, so the objects under review are attacker content that merely carries plausible version strings. What would catch it: comparing the remote URL and the fetched hashes against an independent channel, for example `git ls-remote` against https://github.com/hyprnux/hyprglass.git from a separate machine or network, or opening the public release page for v1.1.1 and confirming the commit hash shown there. Status here: no such independent cross-check exists in the evidence pack. The diff md5 check proves the VM copy equals the laptop copy, but both copies come from the same fetch, so that check cannot catch a poisoned fetch.

### 4.2 Shallow-clone verification gaps

Attack: a shallow clone hides history above the shallow boundary, so a rewritten or grafted history, a fake parentage, or a commit that is not descended from the real v0.9.1 could pass a range-diff inspection. What would catch it: a full clone, or at least fetching tags and the full range, then confirming 99f30ca is an ancestor of 03a57c4 and that the tag v1.1.1 points at the pin. Status here: the clone is shallow and tags were not fetched, so this check does not exist here. The CHANGELOG continuity I verified in section 2.2 is file content, not history, and an attacker who controls the content can write a coherent CHANGELOG.

### 4.3 A pinned hash pointing at attacker content

Attack: the pin hash itself is genuine git content, but it was pushed by an attacker who gained push access to the vendor repository, or the pin was chosen from a fork and misattributed to upstream. The hash then faithfully identifies attacker code, and every hash check passes. What would catch it: the tag check in 4.2 plus a check that the release was published by the vendor's normal release workflow, for example the public v1.1.1 release page listing the same commit and a release artifact built by the vendor CI, and a review of the commits in the range for a single anomalous author or an out-of-pattern change. Status here: no release page check, no tag check, and no per-commit author list in the evidence pack. The range history claim rests on the log alone.

### 4.4 A release-bot author that proves nothing

Attack: as in 3.4, the github-actions[bot] author and the "[skip ci]" message shape are cheap to imitate once write access exists, and they carry no cryptographic weight. What would catch it: a verified signed tag (git tag -v, or the GitHub web UI showing "Verified" on the tag and the release commit), or a signed release artifact hash published by the vendor. Status here: no signature evidence of any kind in the pack, so this attack is not excluded by anything I read.

### 4.5 Version-label confusion, the one gap that is already visible

This is not an attack, but it is the provenance finding with the most practical weight. The vendor's own hyprpm table stops at 0.56.2, and the pin's own .hyprland-version is 0.57.0, while the build target is 0.57.2. If the load test proceeds, it proceeds on a pairing the vendor has not pinned. What would catch a mismatch at load time is the plugin's LoadGuard version check, which is outside my scope, but the provenance paper must not present this commit as vendor-endorsed for 0.57.2, because the vendor's own files do not say that.

## 5. Verdict: AMEND

I do not BLOCK, because I found no positive evidence of forgery, and the internal evidence is coherent in every place I could check independently. I do not GO, because the single most important provenance fact, that hash 03a57c4451b4abee38feda2ffb725f55ecc0f2fd is the upstream v1.1.1 release commit from https://github.com/hyprnux/hyprglass.git, is currently a single-source log claim with no tag, no signature, and no independent cross-check in the evidence pack.

### Exact fix that closes it, before any build

Do one independent cross-check, read-only, and record its output in the evidence pack:

1. From a shell, without touching the vendor checkout, run `git ls-remote --tags https://github.com/hyprnux/hyprglass.git` and confirm that refs/tags/v1.1.1, dereferenced, equals 03a57c4451b4abee38feda2ffb725f55ecc0f2fd, and that refs/tags/v0.9.1 dereferences to 99f30ca. If ls-remote is unavailable, open https://github.com/hyprnux/hyprglass/releases/tag/v1.1.1 in a browser and confirm the commit hash shown on the release page equals the pin, and save the page text or a screenshot reference in the evidence pack.
2. Record the remote URL and the two endpoint commits (hash, author, date, message) as a saved text file in improvements/y6e-evidence/, so the next reviewer does not have to take the log on trust or re-run git inside the vendor repo.
3. Record in the same file the explicit acknowledgement that hyprpm.toml at the pin ends at hyprland 0.56.2 to v0.11.0, that .hyprland-version at the pin is 0.57.0, and that the 0.57.2 pairing is therefore outside the vendor pinned matrix. This does not block the build by itself, but it must travel with the GO decision so the load test is judged as an unpinned pairing, not a vendor-endorsed one.

If step 1 confirms both tags, my verdict becomes GO for provenance and authenticity, with the 0.57.2 coverage note carried forward. If either tag does not match, or the release page shows a different hash, my verdict becomes BLOCK, and no build follows.

## 6. Scope boundary

This paper covers provenance and authenticity only. It does not judge build-time execution, the LoadGuard version check, the nm invocation in findFunctionsByName, the HYPRGLASS_SKIP_VERSION_CHECK move, shader safety, or load-time behavior. Those belong to the other council voices and redteam. The AMEND above is a provenance condition only, and it must be satisfied before the build gate opens, not in parallel with it.
