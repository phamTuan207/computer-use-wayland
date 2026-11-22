# Worker C5-Y6-PAPER log: todolist 2.2.3 (I11) + 4.13, Y6 A1-A7/A9-A10 paper fixes + fresh re-review
# Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
# Task received: Sun 2026-11-22 16:03:27 +07. T+0 at 16:03.
# Wall clock Asia/Ho_Chi_Minh + elapsed time per entry. No em/en dash. No personal info.
# Scope: PAPER ONLY. No live runs, no browser work, no plugin load into any compositor.
# The only laptop-side writes in this lane are staging inert nest-only files under
# /tmp/y6-nested/conf/ (A1 conf + A3 hook/optics), after the re-review says GO.
# No reboot, no live reload, no touch of the live Hyprland config or live PID 1515.

## 0. Baseline verified before any edit (T+3m, 16:06 +07)

- SSH VM to laptop works (VMFIX repaired /usr/lib/python3.12/re.py; `import re` OK on VM).
- Laptop /tmp/y6-nested/conf md5s match the Y6r record exactly:
  - nested-visuals-hook.lua 9d68b2f54f920c6aec2351ab7abe27fc
  - optics.lua b011ea91c3b831651f55fdd096d54c46
  - hyprland-wayland.lua (staged) 0d4ac7a9c2437fb48ecfc505ccd9046b (backup 1, dead ABI)
  - hyprland-wayland-y6e.lua 9ccb27017ab63a9d2bce1d9651425d3b (rebuilt .so path)
- Repo copies match laptop: runner 692d427174fa1c335eb02a46fc5e0a18, y6e conf 9ccb2701,
  load-test script 65fe4c43a026b9aeb89048ff17a3b610 (Y6r open item O4 CLOSED: laptop
  md5s of the load-test script and the runner equal the repo md5s exactly).
- Live Hyprland PID 1515 alive, single signature
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825. Untouched throughout.
- V3 runner has NO AMEND4/AMEND5 (grep for HYPRGLASS_SKIP_VERSION_CHECK and
  live-plugin-list-before returns nothing). Confirmed gap, not assumed.
- Pin-diff checks done on the VM before writing any fix:
  - layers.enabled default false (diff line 6270), status field is the dereferenced
    config value (diff lines 1913-1915, 6507). R1 stands.
  - Per-layer mask_mode is a per-layer override of layers.mask_mode (diff line 634).
    optics.lua config layers.mask_mode="region" + layer mask_mode="contour" is
    coherent, not a contradiction. The A3 marker reports the pill layer's
    effective mode (contour). Checked, not a gap.
  - `hyprctl hyprglass stats` JSON key is contourRebuilds (diff line 1856);
    the table column is contour_build (diff line 885). Council 3 G6 naming stands.
  - `hyprctl configerrors` empty-output semantics confirmed in
    scripts/activation_checks.py wait_for_profile (lines 8-27): stripped output
    must be empty. G4 follows that pattern exactly.

## 1. Fix list (Y6r adjudicated A1-A10; A8 is the trial procedure, not run here)

### A1: Stage the y6e conf as the active conf (STAGED after re-review GO, see section 4)

- Procedure (run on the laptop, /tmp only, no live config):
  1. `cp /tmp/y6-nested/conf/hyprland-wayland.lua /tmp/y6-nested/conf/hyprland-wayland.lua.bak-y6c5-20261122`
     (keeps the backup-1 conf as the rollback source; old md5 0d4ac7a9 recorded).
  2. `cp /tmp/y6-nested/conf/hyprland-wayland-y6e.lua /tmp/y6-nested/conf/hyprland-wayland.lua`
  3. `md5sum /tmp/y6-nested/conf/hyprland-wayland.lua` must print
     9ccb27017ab63a9d2bce1d9651425d3b.
  4. Run ldd on the conf's plugin path (first hyprglass.so match), rc=0, zero
     "not found" lines, and SAVE the output to
     improvements/y6c5-evidence/ldd-y6e-conf.txt (closes Council 2 artifact gap:
     Y6e's own run had no saved ldd log).
  5. Do NOT edit the v3 runner (its md5 is part of the C2 verdict).
- Rollback: `cp /tmp/y6-nested/conf/hyprland-wayland.lua.bak-y6c5-20261122 /tmp/y6-nested/conf/hyprland-wayland.lua`,
  verify md5 0d4ac7a9, delete nothing else. The staged conf is nest-only; the live
  session never reads /tmp/y6-nested/conf, so staging cannot affect live PID 1515.
- Test/proof: md5 check + ldd rc=0 + saved ldd file (section 4 transcript).

### A2: Replace U6 with a positive applied gate (runner lines 298-305 replaced)

- File: improvements/worker-y6b-run-nested-wayland-v2.sh, delimited block
  BEGIN/END Y6C5-A2 positive profile gate.
- New gate: poll the LIVE per-instance log ($NEST_LOG) plus stdout log ($LOG) for
  `Y6-NEST-OPTICS: applied` up to 15 s (Y6C5_GATE_TIMEOUT_S, default 15, 1 s
  interval); fail on timeout with a 30-line nested log tail. The parse-1
  `Y6-NEST-HOOK: hyprglass not ready` marker is logged as EXPECTED, never a fail.
  The hook `Y6-NEST-HOOK: profile applied` line is printed as corroboration.
  Second positive signal: features.layers.enabled == true parsed from the status
  JSON already fetched ($NEST/nest-glass-status.json). Then re-run the nested
  plugin-list and hyprglass status checks (version 1.1.1-cu.1, versionCheck match)
  after the marker. Old fail string and old echo `hook marker absent, profile
  applied` are deleted.
- Precision note (checked, not hidden): the second signal is an early read of the
  same field the liquid gate already requires (scripts/indicator.py _valid_liquid
  requires layers.enabled True). It is not independent evidence beyond the liquid
  gate; its value is failing fast at the gate point instead of after a 60 s
  liquid wait. The marker is the independent signal (it proves config()+layer()
  returned); layers.enabled proves the config effect.
- Deviation from redteam A2(ii), recorded openly: the gate polls the OPTICS marker
  (`Y6-NEST-OPTICS: applied`, values-carrying) as the primary signal, not the
  hook marker (`Y6-NEST-HOOK: profile applied`). Justification: the optics print
  is the last line of optics.lua, so its presence implies dofile() returned,
  which implies the hook print on the next line runs; the two markers are the
  same event, and the optics marker additionally carries the material values.
  The hook marker is still printed and logged as corroboration. The re-review
  (section 5) judges this deviation.
- Test/proof: tests/test_y6c5_positive_gate.py, 4 executed gate cases (see section 2).

### A3: Positive marker (nest copies only)

- Files: improvements/y6-nested-conf/nested-visuals-hook.lua and
  improvements/y6-nested-conf/optics.lua (new repo copies; no repo copies existed
  before, only laptop /tmp copies at the md5s in section 0).
- Hook: success branch does `dofile(...)` then prints
  `Y6-NEST-HOOK: profile applied`. Bare dofile, no pcall: a throw propagates and
  no marker prints, so a half-applied profile cannot pass the gate. Else branch
  keeps the parse-1 `not ready` print unchanged.
- Optics: prints `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour
  namespace=computer-use-indicator` AFTER hl.plugin.hyprglass.config(config) and
  layer() return. Comment records that layers.mask_mode="region" is the global
  default and the layer call overrides it to contour for this namespace.
- Never edited: live native/hyprglass-local-optics.lua (blur 0.0), live
  visuals-login.lua. Nest copies only.
- Landing: after re-review GO, copy both files to /tmp/y6-nested/conf/ on the
  laptop with backups, verify md5s (section 4). Inert until a nested launch reads
  them; the live session never reads /tmp/y6-nested/conf.
- Test/proof: luac -p syntax check on the laptop (no load, parse only) +
  order assertions in tests/test_y6c5_positive_gate.py (marker print after
  layer()/dofile lines).

### A4: Correct the record

- Wrong statements corrected (all four named by Y6r A4, plus two premises found
  while re-reading):
  1. improvements/worker-y6e-rebuild-load-log.md line 561: "the profile was not
     applied in this run". Correct: config applied on parse 2 (layers.enabled
     true, default false, optics.lua the only setter); layer() registration and
     material values unproven until the A3 marker lands.
  2. improvements/worker-y6r-council-2-evidence.md section 1g: "The profile was
     not applied in the 21:57 load run... any pill measurement from that run
     would have measured an un-glassed indicator". Correct: same as (1); the
     21:57 run never measured a pill, so no verdict is affected either way.
  3. improvements/worker-y6r-council-3-safety.md F3: "optics.lua was therefore
     never executed in the Y6e load test, and the profile was NOT applied".
     Correct: optics.lua executed on parse 2 (proven by R1); layer() and
     material values unproven until the marker.
  4. Council 3 F6/F7 premise: status "recorded with the profile NOT applied".
     Correct premise: recorded with the profile config applied; the conclusion
     (status JSON carries no blur/refraction/layer-namespace fields, so the
     liquid gate cannot prove the profile) stands as a code fact.
  5. Council 3 section 1b (line 67): "When the marker appears, the profile
     genuinely was not applied... Failing the run there is correct fail-fast
     behavior". Correct: the marker appears on parse 1 of every successful run;
     the profile is applied on parse 2. Failing on it is a false fail (R3).
  6. Y6r log V4/V5: already self-corrected in the Y6r log (Correction C-V4/V5).
     No edit needed; recorded here as verified.
  7. Hook comment claiming liquid_available catches a missing profile: corrected
     in the new hook copy (A3 file): the comment now states the liquid gate is
     metadata-only and cannot prove the profile.
  8. Load-test script note lines (improvements/worker-y6e-nested-load-test.sh):
     the "profile not applied" NOTE and the "hook marker absent, profile
     applied" echo carry the same wrong claim in code form; both corrected to
     the R1 wording. This changes the script md5 from
     65fe4c43a026b9aeb89048ff17a3b610; new md5 recorded in section 3.
- Method: dated errata blocks APPENDED to the three committed papers (history
  preserved, nothing silently rewritten) + the two code-comment fixes above.
- Test/proof: grep for the old wrong strings in the amended files returns nothing
  except inside the errata blocks themselves (which quote them as corrected
  history); asserted in tests/test_y6c5_positive_gate.py.

### A5: Port AMEND4 + AMEND5 into the v3 runner

- Delta verified first (R5): the v3 runner had neither check (section 0 grep).
  Ported verbatim in shape from improvements/worker-y6e-nested-load-test.sh:
  - AMEND4: skip-var unset check (env grep HYPRGLASS_SKIP_VERSION_CHECK) placed
    after the file-presence checks, before the ldd pre-flight; `unset` after.
  - AMEND5-before: live-config no-hyprglass-load-path walk (python walker over
    ~/.config/hypr/hyprland.lua + hyprland.conf + sourced files, matching
    plugin.load.*hyprglass or hyprglass*.so) placed after the ldd pre-flight,
    before live identity resolution. Guarded API refs stay non-failing by
    design (same as the load test).
  - Live plugin list BEFORE: recorded to $NEST/live-plugin-list-before.json right
    after live identity resolution. Teardown compares before/after with cmp and
    FAILS (exit 1) on any difference, replacing the old print-only after list.
    A failed after-read warns instead of misreporting a change.
- Test/proof: static presence assertions in tests/test_y6c5_positive_gate.py +
  a bash -n syntax check of the runner + a dry parse of the walker block.

### A6: G4 configerrors gate + G6 stats corroboration

- G4 (supporting gate): after the A2 positive gate, before the liquid gate:
  `nest hyprctl configerrors` output stripped must be empty, following
  scripts/activation_checks.py wait_for_profile exactly. A throwing optics.lua
  surfaces as a config error, so this is the only gate catching case (iii).
  A failed configerrors call fails closed (never silently passes).
- Known tension, recorded openly (not hidden): if parse-3 duplicate layer()
  registration errors (open item O1, unresolved), configerrors would be
  non-empty while the parse-2 profile stands, and G4 would false-fail a healthy
  profile. The A8 load-only trial observes the exact configerrors content; if
  the trial shows a parse-3 duplicate-layer error with marker present and
  layers.enabled true, G4 must be narrowed to allow that specific error. The
  trial procedure (A8 doc) lists this as an observation item.
- G6 (corroboration, never a gate): `nest hyprctl hyprglass stats` recorded
  before arm A and after arm B to $NEST/nest-glass-stats-before-arms.json /
  -after-arms.json, raw output printed. JSON key contourRebuilds. No threshold,
  no baseline yet, no fail on missing stats (warn only).
- Test/proof: static presence assertions in tests/test_y6c5_positive_gate.py.

### A7: Do NOT add a manual nest hyprctl reload (R2)

- Fix: an explicit R2 comment block in the runner at the gate (one application
  path only, the automatic parse-2 path; reload buys nothing, risks O1
  duplicate layer() and live-touch surface; reload becomes the next hypothesis
  only if the positive gate ever shows the marker absent).
- Test/proof: tests/test_y6c5_positive_gate.py asserts no non-comment line in
  the runner contains `hyprctl reload`, and asserts the R2 comment exists.

### A8: Load-only trial procedure (written, NOT run)

- File: improvements/worker-y6c5-a8-load-only-trial.md. Proves the amended fix
  (staged y6e conf + positive gate + G4 + AMEND4/5), no pill, no arms, no
  backdrop, no grim captures. Uses the amended v3 runner with the new
  Y6_STOP_AFTER_GATES=1 flag (exits 0 after the liquid gate; teardown still
  runs and re-verifies live). Full preconditions, measured outputs, and abort
  conditions are in the doc. NOT run by this lane (paper only; the live trial
  comes after re-review, in a nested Hyprland per option C, never on live).
- The Y6_STOP_AFTER_GATES flag is a small runner addition, tested statically.

### A9: Fresh re-review (this lane, section 5)

- Re-review of the whole Y6 set as a new reviewer, no trust in the fix author's
  claims. Every remaining gap recorded with severity. Retry GO only on zero HIGH
  gaps. Written after the fixes, in section 5 of this log.

### A10: Method (no saved-log marker counts as parse evidence)

- Fix: the A2 gate greps the LIVE per-instance log ($NEST_LOG) during the run
  (plus the stdout log $LOG); a comment at the gate states saved-log marker
  counts are not parse evidence (ofstream buffering, saved logs are 188-line
  flushed prefixes, tail lost on SIGKILL teardown). No gate in the runner reads
  a hypr-saved directory.
- Test/proof: static assertion in tests/test_y6c5_positive_gate.py (gate
  references $NEST_LOG; no `hypr-saved` reference in any gate block).

## 2. Tests run (VM, paper lane; no nest launched, no plugin loaded)

- tests/test_y6c5_positive_gate.py, 16:09:53 +07 (T+6m): all 17 checks PASS, exit 0.
  5 A2 gate execution cases under bash with stubbed fail()/nest() and fake logs
  (healthy via stdout log, healthy via nest log, no marker fails, layers false
  fails, parse-1 marker expected passes), 2 G4 execution cases (empty passes,
  non-empty fails), plus static checks for A2/A3/A5/A6/A7/A8/A10/A4/A1 and
  bash -n on both scripts. Three initial failures were test bugs, not fix
  bugs (pcall word in a comment, first Y6_STOP_AFTER_GATES occurrence in a
  header comment, hypr-saved word in a gate comment); fixed in the test, reran
  to 17/17 PASS. Command: `python3 tests/test_y6c5_positive_gate.py`.
- `luac -p` (parse only, no load) on the laptop via ssh, 16:10 +07: new hook
  and optics both OK under default luac and under luac5.4 (Hyprland 0.57
  embeds Lua 5.4). Old laptop copies also pass under the same luac, so the
  check is consistent. New file md5s: hook 6dd68aeadbe7e1c9049436dc7361ee7a,
  optics 85298d2035697710d95117355c9830ca.
- `bash -n` on the amended runner and load-test script: PASS (in the test run).
- A4 grep checks: old strings "hook ran before plugin load (profile not
  applied)" and "hook marker absent, profile applied" absent from the runner
  and the load-test script; errata blocks present in all three papers
  (in the test run).
- New md5s after the fixes (recorded because Y6r V8 pinned the old ones):
  runner f197ac651baff574e6b3e6de1d9c8d53 (was 692d427174fa1c335eb02a46fc5e0a18),
  load-test script 486fd1ce9bd9118932ea10a1d7aae680 (was
  65fe4c43a026b9aeb89048ff17a3b610). The load-test script is a historical
  artifact (its run already happened); the edit is a record correction only.
  The three errata papers changed by append-only additions at the end
  (verifiable via git diff: additions only, nothing above rewritten).

## 3. Commit record

- 66ad103 (T+10m): C5-Y6-PAPER fix commit. 6 files, 736 insertions, 13 deletions:
  improvements/worker-y6b-run-nested-wayland-v2.sh (A2/A5/A6/A7/A8),
  improvements/worker-y6e-nested-load-test.sh (A4 note lines),
  improvements/y6-nested-conf/nested-visuals-hook.lua (new, A3/A4),
  improvements/y6-nested-conf/optics.lua (new, A3),
  improvements/worker-y6c5-a8-load-only-trial.md (new, A8),
  tests/test_y6c5_positive_gate.py (new, 17 checks).
- 2634471 (T+11m): C5-Y6-PAPER A4 errata commit. 3 files, 41 insertions
  (append-only): improvements/worker-y6e-rebuild-load-log.md,
  improvements/worker-y6r-council-2-evidence.md,
  improvements/worker-y6r-council-3-safety.md.
- [log commit + staging commit to fill below; push verified with git ls-remote]
- Push verification: [TO FILL after push]

## 4. Staging record (laptop /tmp/y6-nested/conf, after re-review GO)

- [TO FILL: exact commands, md5s before/after, ldd output file, rollback]

## 5. Fresh re-review (new reviewer, no trust in the fix author)

- Reviewer stance: re-read the Y6r adjudication, the redteam mechanism
  (Hyprland 0.57.2 tag 11cbc6c57 citations), the pin diff, the runner diff,
  the new hook/optics, and the test run as if seeing them for the first time.
  Every fix-author claim below was re-derived or explicitly marked unproven.
- What was re-derived independently in this lane:
  - R1 (profile config applied on parse 2): the default-false leg was
    re-verified from the repo pin diff (diff line 6270: LAYERS_ENABLED
    default false; lines 1913-1915, 6507: status field is the dereferenced
    config value). The parse-2 mechanism itself (STAGE_LATE loads the plugin
    synchronously, reload(), parse 2 sees count=1) was NOT re-derived from
    Hyprland source in this lane; it is taken from redteam section 1.2 with
    its file/line citations. See gap M1.
  - The A2 gate logic: executed, not just read (5 bash cases with stubs).
    Healthy passes on either log file; missing marker fails on timeout;
    layers false fails; parse-1 marker present passes and is logged expected.
  - G4: executed (empty passes, non-empty fails).
  - Hook/optics syntax: luac -p and luac5.4 -p, both pass.
  - Staging inputs: repo y6e conf md5 equals laptop y6e conf md5 (9ccb2701);
    staged conf md5 0d4ac7a9; hook/optics laptop md5s match the Y6r record.
  - O4 closed: laptop load-test script and runner md5s equal repo md5s.
  - Mask coherence: config layers.mask_mode="region" + layer mask_mode
    "contour" is a global default plus a per-layer override (pin diff line
    634), not a contradiction. The marker reports the effective layer mode.
  - Stats key: contourRebuilds is the JSON key (pin diff line 1856).
  - configerrors semantics: stripped output must be empty
    (activation_checks.py wait_for_profile).
- Gaps found, with severity:
  - M1 (MEDIUM): parse-2 application mechanism not independently re-derived
    from Hyprland source in this lane (redteam citations only). Mitigation:
    the A8 trial IS the empirical test of exactly this claim (trial item 1:
    the applied marker must appear in the live per-instance log). If parse 2
    does not apply the profile, the trial fails and the retry stays blocked.
    Not HIGH for the trial; would be HIGH for the measurement retry if the
    trial had not run first.
  - M2 (MEDIUM): parse-2 print delivery to $NEST_LOG is inferred, not
    observed. The parse-1 marker reached the per-instance log (redteam P2,
    saved log line 15), but no parse-2 print has ever been observed in any
    log (the old optics.lua printed nothing). Same mitigation as M1: the
    trial observes it directly. The gate's 15 s poll is a margin for log
    flush lag; if the marker never lands, the gate fails on timeout with a
    log tail, fail-closed.
  - M3 (MEDIUM): G4/O1 tension. If parse-3 duplicate layer() registration
    errors, configerrors is non-empty while the parse-2 profile stands, and
    G4 false-fails a healthy profile. Documented in the runner comment, the
    log, and the trial procedure as an observation item with a defined
    outcome (G4-NARROW-NEEDED). Not HIGH: the trial is designed to observe
    it, and the failure mode is a loud fail, not a silent false pass.
  - L1 (LOW): the second positive signal (layers.enabled) is not independent
    evidence beyond the liquid gate (indicator.py _valid_liquid already
    requires it); its role is early fail-fast. Documented in the log and the
    gate comment. No action.
  - L2 (LOW): A2 deviation from redteam A2(ii): the gate polls the OPTICS
    marker as primary, not the hook marker. Justification recorded: the
    optics print is the last line of optics.lua, so its presence implies
    dofile() returned, which implies the hook print runs next; the two
    markers are the same event and the optics marker carries the values.
    The hook marker is still printed and logged as corroboration. Accepted.
  - L3 (LOW): top-level `enabled = false` in the optics config table has an
    unresolved semantic (which feature it gates). Empirically inert: the Y6e
    run reported status active true with this config. No effect on the gate
    (marker + layers.enabled prove the profile). No action.
  - L4 (LOW): teardown `exit 1` inside the EXIT trap overrides signal exit
    codes (143/130 become 1) when the live plugin list changed. Cosmetic;
    the FAIL line is printed. No action.
  - L5 (LOW): file pins from Y6r V8 are now stale by design (runner
    f197ac65, load-test 486fd1ce; three papers gained append-only errata).
    Recorded in section 2 with old and new values. Anyone re-verifying
    against the old pins must use the new ones.
  - L6 (LOW): staging touches the laptop repo working tree by one file (the
    amended runner copy for the trial). Mitigation: backup first with md5,
    rollback is restore-from-backup. The staged nest files live under
    /tmp/y6-nested/conf, which the live session never reads.
- Scope boundary (not a gap): nothing after the gates has been proven live.
  The liquid readiness window (O3), the pill arms, the verdict logic, and
  the runner's file-presence preconditions for BACKDROP/PILL were never
  executed against a real nest (Y6r section 4). The A8 trial does not cover
  them either. They are covered by the measurement retry, which stays gated.
- Verdict: ZERO HIGH gaps.
  - GO for the A8 load-only trial (improvements/worker-y6c5-a8-load-only-trial.md),
    in a nested Hyprland per option C, with the staged files from section 4.
  - The PILL MEASUREMENT retry (serial item 4) is NOT cleared by this
    re-review. It stays gated on: (a) the A8 trial passing on all 7 measured
    items, and (b) a fresh re-review of the trial evidence. A GO here must
    not be read as permission to run the pill measurement.
  - If the trial shows a parse-3 duplicate-layer config error (M3), the
    outcome is G4-NARROW-NEEDED, and the fix diff goes back to re-review
    before any measurement run.
