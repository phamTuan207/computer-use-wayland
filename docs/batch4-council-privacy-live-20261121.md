# Batch 4 council verification: privacy scan, scrub plan, AT-SPI live, MCP re-run

Council member 3, independent verification. Date 2026-11-21.
Local HEAD at verification time: beffa19. Remote main in sync at the
same commit when checked. This report contains no real personal
values anywhere. Every finding is recorded by type, file, line, and
commit only, with values redacted.

Method note: nothing here trusts coord/clone1.md or any agent claim.
Every number below comes from a check done in this session.

## 1. Personal-info re-scan, different method

Method: ripgrep 14.1.0 with my own patterns, not the audit patterns.
Main tip scanned on the working tree. Every branch tip scanned by
extracting it with git archive into a scratch dir on the home disk
and running ripgrep there (31 remote branches plus origin/HEAD).
Pickaxe checks with git log -S for the full address, the domain,
and the name forms. Binary files not scanned (same limit as the
audit). Historical versions of files not individually grepped.

### 1.1 Name, main tip

- At beffa19 (current main): 70 lines in 44 files. Split: 66 lines
  ascii short form, 4 lines diacritic short form.
- At 1c7d252 (the audit commit): 71 lines in 45 files. Split: 66
  ascii, 5 diacritic. This matches the audit exactly: 71 lines, 45
  files.
- The 1 line drop from 71 to 70 is coord/clone1.md, which was
  rewritten as the batch 2 and 3 report and no longer carries the
  name. File count drops 45 to 44 for the same reason.
- File list at 1c7d252 verified identical to the audit list by diff:
  same 45 files, no file missed, no file wrongly included.
- Line spot checks at 1c7d252 verified identical to the audit:
  improvements/speed-swarm-report.md lines 4, 485, 514, 542, 554,
  558; improvements/live-test-log.md lines 3987, 4089, 4150, 4155,
  4195, 4196 (3 ascii, 3 diacritic).
- CORRECTION to the audit wording: the audit says "Real name (full
  name and short form)". The three-part full name appears 0 times
  anywhere: 0 lines on the main tip, 0 lines at 1c7d252, and
  git log --all --oneline -S for the three-part form returns 0
  commits. All 71 lines are the two-part short form only (ascii and
  diacritic). The leak is real, the short form still identifies the
  person, but the report should not claim the full three-part name
  is present. Pickaxe for the short form returns 66 commits.
- The fullName test value in
  tests/realistic/fcc-k/fixtures/test-08-form.html:29, 35, 38 is
  still there at beffa19, unchanged since the audit.

### 1.2 Name, branch tips

Name lines per branch tip (ripgrep on extracted trees, ascii plus
diacritic short forms combined):

- origin (HEAD symref, same as main): 70
- main: 70
- coord-clone2-setup: 70
- todolist-push: 75
- speed-swarm: 96
- harness-warm-browser-land: 53
- cascade-local-model: 50
- effort-dial: 50
- algo-a4: 49
- latency-probe: 49
- det-finish: 49
- event-wait-seq: 48
- harness-drop-old-shots: 48
- a2-preflight: 47
- action-grouping: 47
- change-only-obs: 47
- harness-hyprctl-batch: 47
- harness-jpeg-q90: 47
- harness-prefetch: 47
- harness-warm-browser: 47
- instrfix: 47
- lowres-obs: 47
- vault-move: 47
- pill-bottle-fix: 41
- pill-shayxo-fix: 41
- speed-swarm-pick4a11y: 31
- speed-swarm-brokerfix: 30
- speed-swarm-pick1p34fix: 11
- speed-swarm-masking: 10
- speed-swarm-pick1fix: 9
- rust-rewrite-eval: 5
- cli-anything-integration: 0

Total: 1425 lines across the 32 rows scanned, which is 1355 lines
across the 31 distinct branch tips (the origin row duplicates main).
The audit claimed 1427 lines across 31 branch tips, measured at
older tip SHAs on 2026-11-21 around 09:36 UTC. Tips have moved
since (main advanced 1c7d252 to beffa19, coord-clone2-setup and
todolist-push advanced, other branches moved), so an exact match is
not expected and the small difference is consistent with tip
movement, not with an audit error. My per-branch numbers above are
the current measurement.

### 1.3 Email

- Main tip: 0 full address matches. Confirmed.
- Branch tips carrying the full address now: 24 branches.
  a2-preflight, action-grouping, algo-a4, cascade-local-model,
  change-only-obs, det-finish, effort-dial, event-wait-seq,
  harness-drop-old-shots, harness-hyprctl-batch, harness-jpeg-q90,
  harness-prefetch, harness-warm-browser, harness-warm-browser-land,
  instrfix, latency-probe, lowres-obs, pill-bottle-fix,
  pill-shayxo-fix, speed-swarm, speed-swarm-brokerfix,
  speed-swarm-pick4a11y, todolist-push, vault-move.
- The audit claimed 25 branches. The one that changed is
  coord-clone2-setup: its tip no longer carries the address
  (verified: git show origin/coord-clone2-setup for the file returns
  0 matches). The tip advanced past the fix since the audit. So the
  audit was right at audit time, and the count is now 24.
- todolist-push tip still carries the address (1 match). Confirmed.
- Generic email pattern on the main tip: 37 matches, all placeholder
  domains. example.com 15, example.local 12, example.org 6,
  users.noreply.github.com 2, example.invalid 2. No real address.
- Domain-only mentions of gmail.com on the main tip: 9 lines, all in
  verification commands and docs (audit doc, scrub plan, coord
  report), not addresses.

### 1.4 Phones, tokens, keys, passwords

- Strict bounded VN mobile pattern: 14 matches on the main tip.
  All 14 are false positives, verified by masked context: Oklab
  decimal coefficients in tests/test_glass_shayxo_contract.py,
  native/hyprglass-shayxo-legacy.patch, and
  improvements/pill-shayxo-port-design.md, plus one SHA hash string
  in docs/benchmarks/r4_isolation_aggregate.json. No real phone.
- Loose 10-digit pattern: 704 raw matches, dominated by benchmark
  JSON files (long numeric values) and the same Oklab coefficients.
  None classified as a phone after the strict check above.
- Tokens and private keys: 0 matches on the main tip, 0 on every
  branch tip (patterns: ghp_ long, AKIA, Slack xox long, BEGIN
  PRIVATE KEY). The 5 short "sk-" strings the audit cleared were not
  in my pattern set (mine required 20 plus chars), which is a
  difference in method, not a disagreement: short 15-char strings
  inside .json filenames are not keys.
- Password and secret assignments: 0 matches on the main tip.
- Home address, personal schedule: nothing found. Same as audit.

### 1.5 What the audit missed or got wrong

- Missed nothing material on the main tip or branch tips for the
  patterns I used. Totals, file list, and spot-checked lines all
  match.
- Wrong wording: "full name" is not present anywhere. Only the
  two-part short form occurs. Correction recorded in section 1.1.
- Stale count: branch tips carrying the email are 24 now, not 25,
  because coord-clone2-setup moved. Recorded in section 1.3.
- Method note from my own work: my first branch-tip scan produced
  zeros for most branches because /tmp is a 512M tmpfs and it filled
  up mid-extraction, leaving empty files. I discarded that run and
  redid the whole scan on the home disk. The zeros were my artifact,
  not a finding.

## 2. Scrub plan verification, read-only

Checked docs/email-history-scrub-plan.md claim by claim. Nothing
was run, no history rewritten, no branch touched, no force push.

- Main commit count: plan says 432 at write time. Measured now:
  444. The plan expected rewritten main count of 431 (432 minus 1
  pruned empty commit). With 444 now, the expected rewritten count
  is 443, not 431. The plan number is stale, the rule behind it
  (one pruned commit) still holds.
- Commits touching the full address: exactly 2, confirmed by
  pickaxe over all refs. a46b3c6 (introduced, 2026-11-18) and
  1c7d252 (removed, 2026-11-21). Confirmed.
- Branch tips carrying the address: plan implies 25 and names
  todolist-push and coord-clone2-setup as the two refs to watch.
  todolist-push still carries it (1 match). coord-clone2-setup no
  longer does (0 matches). Current count is 24 branches. The plan
  text about coord-clone2-setup is stale.
- git filter-repo: NOT installed on this machine. Confirmed:
  "git filter-repo" is not a git command, no git-filter-repo binary
  on PATH, nothing matching filter-repo in pip list. The plan is
  right that it must be installed before the run.
- Mechanical extraction: git show a46b3c68 for the file, line 3288,
  grep for the address pattern returns exactly 1 match. Confirmed.
  The plan extraction command works as written.
- Merge commit 96438bb: present in main log, subject "merge
  todolist-push into main (Zen DOM control + error fixes, 21/11)".
  Confirmed.
- .git size: plan says 6.0M. Measured now: 7.5M. Stale, harmless.
- Tags: 0. Confirmed. Remote branches: 31 plus origin/HEAD.
  Confirmed.
- Main branch protection: plan says main is NOT branch protected.
  Confirmed via GitHub API: GET branch protection returns 404
  "Branch not protected". Force push is technically allowed.
- FLAW in the plan, section 7 verification: two checks use the
  domain string and expect empty output, but they cannot be empty
  after a correct rewrite. git log --all --oneline -S "gmail.com"
  returns 5 commits now: a46b3c6, 1c7d252, aeaa006, 6e57183,
  6599706. The last three only mention the domain in verification
  commands and docs (audit doc, scrub plan, coord report). A rewrite
  that replaces only the full address leaves those three commits
  touching the domain string, so the check would return 3, not 0.
  The same applies to git grep "gmail.com" over all commits: the
  docs contain domain mentions, so it would not be empty. Both
  checks must use the full address string, not the domain, or they
  will report failure after a successful scrub. The third check in
  the same section (git show HEAD for the file, grep -c "gmail.com",
  expect 0) is fine as written.
- The plan says the rewrite covers all branches through a mirror
  clone. That part is sound. The plan also says todolist-push can be
  deleted after verification because it is merged. The merge
  96438bb is confirmed present, so that step is still valid.
- UNVERIFIED (same as the plan states): whether any fork exists,
  whether clone2 or the VM hold unpushed work, GitHub cache expiry
  for old commit pages. I did not check forks.

## 3. AT-SPI live reproduction

Environment at start of this check: the whole stack was gone from
this machine. /tmp/firefox did not exist, python3-pyatspi was not
installed (ModuleNotFoundError), at-spi2-core was not installed.
This machine is root (uid 0). Xvfb and dbus-run-session were
present. /tmp is a 512M tmpfs.

Rebuild, all measured in this session:
- apt-get update: exit 0, fetched 35.7 MB in 10min 1s (59.3 kB/s,
  slow mirror).
- apt-get install at-spi2-core, python3-pyatspi, gir1.2-atspi-2.0,
  dbus-x11: exit 0. Installed at-spi2-core 2.52.0-1build1,
  python3-pyatspi 2.46.1-1. pyatspi imports OK after install.
- Firefox 160.0.1 re-downloaded from ftp.mozilla.org, pinned
  release 160.0.1, 90,943,956 bytes, same size the batch 3 report
  gave. Extracted to /tmp/firefox. /tmp/firefox/firefox --version
  prints Mozilla Firefox 160.0.1.

First attempts FAILED, exactly like the coordinator earlier:
- dbus-run-session with the AT-SPI bus launcher, AT_SPI_BUS_ADDRESS
  exported, registry activated before Firefox: probe dump fails,
  find_app timeout 30 s, desktop childCount 0, even though Firefox
  was alive (firefox-bin plus children) and the bus answered
  GetAddress. Two orderings tried (registry before and after
  Firefox start), both childCount 0.

Working recipe, found in this session:
- eval $(dbus-launch --sh-syntax) for the session bus (not
  dbus-run-session), at-spi-bus-launcher, AT_SPI_BUS_ADDRESS
  exported from GetAddress, GNOME_ACCESSIBILITY=1,
  GTK_MODULES=gail:atk-bridge, registry activated with a trivial
  pyatspi getDesktop call BEFORE Firefox starts, fresh profile with
  user.js accessibility.force_disabled=false, then Firefox on
  tests/bidi_fixture.html. Desktop then shows 1 app, Firefox.
- The batch 3 doc does not record GNOME_ACCESSIBILITY or
  GTK_MODULES or the dbus-launch detail. That missing detail is
  likely why the coordinator could not reproduce it. Batch 5 task 2
  (self-contained probe) must capture this recipe.

Results with the working recipe, Firefox 160.0.1, 2026-11-21:
- Dump mode, probe exit 0. find_app ok, 20.3 ms, app Firefox.
  Batch 3 reported 11.0 to 31.9 ms, so 20.3 ms is inside their
  range. Dump ok, 51 nodes, walk 48.2 ms. Batch 3 reported 71 nodes
  in 15.4 to 29.9 ms AFTER dismissing onboarding. Mine is 51 nodes
  with the onboarding dialog still up, so the web content tree is
  blocked. That is consistent, not a discrepancy. No Increment,
  Counter, or Name nodes in the dump, for the same reason.
- Full mode, probe exit 2 (expected, typing fails). find_app ok,
  17.0 ms. dismiss_onboarding ok, label Continue, click 3.1 ms.
  find_button ok, 2038.5 ms. click ok, click 0.3 ms, read back
  "Counter: 1". find_field ok, name Name. type_editabletext FAIL,
  detail "EditableText returned True, read back ''", type 0.6 ms.
  type_keysyms_fallback FAIL, detail "keysym typing, read back ''",
  type 809.7 ms. final_readback ok, paragraph "Counter: 1", entry
  "", counter_seen true.
- Conclusion: all three batch 3 AT-SPI claims REPRODUCED. Tree read
  works, Action click works and is verified by Counter: 1,
  EditableText typing fails exactly as reported (returns True, reads
  back empty). The keyboard fallback also fails, same as batch 3.
- Click timing matches batch 3 (0.3 ms vs their 0.2 to 0.3 ms).
  Dismiss click was 3.1 ms here vs their 0.2 to 0.3 ms, same order
  of magnitude.
- Cleanup done: 0 Firefox, Xvfb, registryd, or AT-SPI processes left
  from my runs. Verified by process list after the runs.
- UNVERIFIED: everything on real Zen, everything on Wayland (all
  runs here are Xvfb, X11), large-page tree walks, the tab switch
  action. Same limits as batch 3.

## 4. MCP server re-run

- Suite: python3 tests/test_mcp_server.py, 12 tests, OK, 1.838 s.
  Batch 2 reported 1.372 s for the same 12 tests. Same result,
  slower wall clock here (machine load).
- Manual stdio smoke against the fake backend, real run in this
  session: initialize returns server computer-use-mcp version 0.1.0,
  protocol 2024-11-05. tools/list returns 8 tools (session_start,
  session_status, session_finish, locate, click, type, screenshot,
  overlay). session_status returns inactive. session_start with
  backend fake returns active, session_id fake-1. locate with a
  wrong argument name returns isError true with "selector must be a
  non-empty string", which is correct argument checking. locate,
  click, and type with selectors outside the fake fixture return
  "no element matches selector", which is expected for those
  selectors; the happy paths are covered by the 12 unit tests.
  screenshot returns ok, mime image/png, 68 bytes. overlay status
  returns ok, holders empty. session_finish returns inactive.
  Stderr logs only tool name and elapsed ms, no typed text.
- UNVERIFIED: all live paths (session_start on real Zen, locate,
  click, type, screenshot on a real tab, overlay on a real desktop,
  handshake with a real MCP client). Same limit as batch 2.

## Summary of corrections found

1. Audit wording: the three-part full name appears 0 times anywhere
   in the repo or its history. Only the two-part short form occurs.
2. Audit branch count for the email is now 24, not 25.
   coord-clone2-setup tip is clean since the audit.
3. Scrub plan: expected rewritten main count is 443 now, not 431
   (main grew 432 to 444). The plan section 7 domain checks are
   wrong as written: git log -S "gmail.com" and git grep "gmail.com"
   cannot return empty after a correct rewrite, because three doc
   commits only mention the domain. Use the full address string in
   those checks. The plan text naming coord-clone2-setup as still
   carrying the line is stale.
4. AT-SPI: batch 3 results fully reproduced, but only with a session
   recipe the batch 3 doc does not record (dbus-launch plus
   GNOME_ACCESSIBILITY=1 plus GTK_MODULES=gail:atk-bridge plus
   registry before Firefox). dbus-run-session alone does not work
   on this machine.
5. MCP server: 12 of 12 pass on re-run, manual smoke confirms
   protocol, 8 tools, session lifecycle, and error paths.
