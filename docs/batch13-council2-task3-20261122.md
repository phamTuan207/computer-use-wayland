# Batch 13 council 2: review of task 3 Y13g round-3 adjudication

- Reviewer: batch 13 council 2 (task 3 review).
- Date: 2026-11-22.
- Repo: ~/workspace/computer-use-wayland. Report branch: main.
- Adjudication under review: docs/batch13-task3-y13g-round3-adjudication-20261122.md, commit e7d9a1c.
- Code read (read-only): branch todolist-push, HEAD 3167c76, via a detached worktree. No file on todolist-push was modified. No shared code was changed.
- Round-2 reviews cross-checked: redteam commit 167a2e9, verifier commit 75dff55, council 1 commit 1e49436, council 2 commit 6d83401, council 3 commit 31c1126, fix log commit ab0b62c. Round-2 fix diff: commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8 (all verified present; 5a9b9e8 is an ancestor of 3167c76; no commit touched launch_y13.py or run_codex_y5.py between 5a9b9e8 and 3167c76, so the reviewed file state is the round-2 state).
- Method: I re-read every cited code line first-hand on todolist-push and re-derived the key reasoning (the F1 conjunction, the F2 env pass-through, the F5 marshal comparison, the F4 git log call, the defect 2 unlink path). I recomputed the pins, the 14-def AST identity, and the _SHIP_FILES identity myself. I did not re-run any live battery and I ran no live run; live numbers below are the reviewers' numbers as recorded in their review docs on todolist-push, and I checked each number against the doc that states it.
- Rules: no personal information in this report; no em dashes or en dashes, only commas, periods, or short hyphens; no ydotool; every number below was verified first-hand or is quoted from a named review doc with its commit.

## Overall verdict: AGREE, BLOCK stands

I agree with the adjudication's overall verdict (BLOCK stands, no live run) and with every UPHELD decision in its decision table. Both HIGH findings stand, both MEDIUM _check_entry_pyc defects stand, and no finding should be downgraded or rejected. I found no missing HIGH or MEDIUM finding in the five round-2 reviews that the adjudication left out: the table covers redteam F1-F7, verifier defects 1-2, council 1 F1-F8, council 2 C2-1 to C2-10, and council 3 C3-1 to C3-8, which is the complete finding set of all five reviews.

I found one framing disagreement (resolution 2, see E2) and 12 line-range citation errors (see E1), none of which changes any verdict. The round-3 fix instructions stand as written, with the corrected line numbers in E1.

## Per-decision verdicts

AGREE means I verified the code facts first-hand and the review-doc evidence the adjudication cites, and I accept the verdict and severity. DISAGREE means otherwise, with evidence.

| Finding | Adjudication | My verdict | Evidence checked |
|---|---|---|---|
| Redteam F1, check_manifest exemption dead code | UPHELD, HIGH | AGREE | launch_y13.py:1197 condition verified; _is_entry_pyc_rel 295-303 verified; main order check_manifest 1475 before _check_entry_pyc 1476 verified; scan exemption 354-355 verified; redteam A2L 7/7 and A2x 8/8 confirmed in redteam doc (167a2e9); severity HIGH accepted, council 2 MEDIUM vote noted and overruled for the reasons given |
| Redteam F2, PYTHONPATH plants execute under -P | UPHELD, HIGH | AGREE | grep over both entry files: zero matches for PYTHONPATH, PYTHONHOME, PYTHONSTARTUP; env = dict(os.environ) at launch_y13.py:1484; comment 1495-1497 verified; fresh-compile subprocess at 1289 inherits env (no env argument); redteam A6 117 cases, 101 pass, 16 FAIL, 13 .py names, shlex.so, launcher-process execution, delegating shim all confirmed verbatim in redteam doc; severity HIGH accepted |
| Redteam F3, tokenizer residuals | UPHELD, MEDIUM | AGREE | _SINKS launch_y13.py:569-572 and run_codex_y5.py:3984 verified, getoutput/getstatusoutput/popen/exec/spawn/__import__/pty.spawn absent; _m_module_is_runner 586-614, pdb only at 600, trace absent; `python3 -- -` falls through to _token_is_runner_script("-") False, verified at 534-543 and 620-691; wrapper list 706-855 lacks the 12 named wrappers; _is_timeout_dur 697-703 rejects "0x10" (isdigit False); redteam A4 59/59, 28/31 + 5/6, FRESH 2/29 and verifier A4 81/81, 17/17 confirmed in the review docs |
| Redteam F4, topo-order does not order across merges | UPHELD, MEDIUM | AGREE | git log call launch_y13.py:1119-1122, --topo-order at 1121, no --first-parent anywhere in the file (grep); redteam A5 cases 10 and 11 confirmed verbatim; verifier A5 10/10 linear-only confirmed |
| Redteam F5, relative-path py_compile co_filename mismatch | UPHELD, MEDIUM | AGREE | Fresh compile uses absolute src at 1281-1283, comparison marshal.dumps at 1302; verifier A3h 2 checks and council 1 P3b confirmed in the review docs |
| Verifier defect 2, symlink-unsafe deletion in _check_entry_pyc | UPHELD, MEDIUM | AGREE | _check_entry_pyc 1242-1313 uses plain os.listdir (1263-1265) and os.unlink (1307), no realpath check; guard helper _entry_pyc_paths 190-213 has the realpath check; verifier A7 shape-6b confirmed (legit .pyc deleted outside the ship, proven twice; forged refuses intact) |
| Redteam F6, -m guard leaves empty nested dir | UPHELD, LOW | AGREE | Both guards unlink files only, never prune dirs; _is_exempt_cache_dir top-level only (runner 293-310); redteam F6, council 2 C2-5 P4b, verifier A2l all confirmed; downgrade from LOW-MEDIUM to LOW accepted |
| Redteam F7, check_manifest gaps | UPHELD, LOW | AGREE | check_manifest walk 1182-1204 flags only symlinks, .pyc, top-level .py; redteam F7 text confirmed verbatim |
| Verifier defect 1, filename-sensitive marshal comparison | UPHELD (same as F5), MEDIUM | AGREE | Same code facts as F5; verifier A3h confirmed |
| Council 1 F1, runner docstring launch lines lack -P | UPHELD, Medium-Low | AGREE | run_codex_y5.py:103 and 105 lack -P, 106 has -P; council 1 P7 confirmed |
| Council 1 F2, -m guard runs after _derive_ship_dir | UPHELD, Medium-Low | AGREE | SHIP_DIR derived at launch_y13.py:185, guard at 227, repo-tree refusal at 170 inside _derive_ship_dir; council 1 P4a/P4b/P4c confirmed |
| Council 1 F3, SHIPPED.md note omits constants | UPHELD, Low | AGREE | SHIPPED.md:43-49 lists only os/json/hashlib/re/shlex/subprocess/time/marshal and _SHIP_DIR; the 4 constants exist at run_codex_y5.py:3861-3865 and 4032; council 1 P2c and council 3 P6 confirmed |
| Council 1 F4, -c sink docs vs code | UPHELD, Low | AGREE | _SINKS verified; council 1 P6 (getoutput False, run form True) confirmed |
| Council 1 F5, stale two entry .pyc comment | UPHELD, Low | AGREE | run_codex_y5.py:750 reads "the two entry .pyc files (0, 1, or 2)"; grep over the runner, launcher, SHIPPED.md, and plan finds no other "two entry" mention; the parenthetical is a count of files present (0 to 3 with three stems), so the adjudication fix text "three entry .pyc files (0, 1, 2, or 3)" is correct and matches plan B1 "(0-3)" |
| Council 1 F6, repo-tree wording overgeneralizes | UPHELD, Low | AGREE | Plan 714-716 and SHIPPED.md:20-24 verified; council 1 live probe (--ship-dir at tests/realistic exits 2 with tampered-ship mixed message) confirmed in council 1 doc |
| Council 1 F7, main exec subprocess.run unwrapped | UPHELD, Low | AGREE | launch_y13.py:1503 unwrapped; the other five calls at 1068, 1110, 1119, 1206, 1289 are all wrapped in try/except (OSError, TimeoutExpired); council 2 C2-7 code-reading note confirmed |
| Council 1 F8, marshal comparison docs silent | UPHELD (same as F5) | AGREE | Same code facts as F5; council 1 P3b confirmed |
| Council 2 C2-1, R2 not fixed, exemption unsatisfiable | UPHELD (same as F1), HIGH | AGREE | Same code facts as F1; council 2 rated MEDIUM, adjudication keeps HIGH, accepted |
| Council 2 C2-2, tokenizer new generation | UPHELD (same as F3), MEDIUM | AGREE | Same code facts as F3; council 2 C2-2 (a)-(d) live proofs confirmed in council 2 doc |
| Council 2 C2-3, PYTHONPATH survives -P | UPHELD (same as F2), HIGH | AGREE | Same code facts as F2; council 2 rated LOW, adjudication keeps HIGH, accepted; council 2 probe1 P1f confirmed |
| Council 2 C2-4, ship missing SHIPPED.md passes every gate | UPHELD, Low | AGREE | Scan iterates files present; _scan_ship adds codex-y5/SHIPPED.md to the allowed set but never requires presence; manifest has 27 entries and SHIPPED.md is not one; council 2 P1c confirmed in council 2 doc |
| Council 2 C2-5, leftover empty nested dir | UPHELD (same as F6), Low | AGREE | Same code facts as F6 |
| Council 2 C2-6, codex warning fires on path mentions | UPHELD, Low | AGREE | _is_codex_process 872-890, loop over parts[1:] with endswith "/codex"; council 2 P6 (grep/echo/ls) confirmed |
| Council 2 C2-7, main exec unwrapped | UPHELD (same as C1-F7), Low | AGREE | Same code facts as C1-F7 |
| Council 2 C2-8, ssh:// remote form refuses | UPHELD, Low | AGREE | _normalize_remote_url 1033-1055: strips one trailing slash only, strips .git case-sensitively, ssh:// form is not converted to https; council 2 P7 (20 cases) confirmed |
| Council 2 C2-9, docs overclaim | UPHELD, Low | AGREE | Plan B1 638-639 false claim verified; B3 sink list "subprocess.*" verified at plan 660-682; LIMIT paragraph documents string-concatenation only; B2 "non-entry .pyc" wording confirmed via council 2 line 88; Amend 2 wording confirmed at plan 700-704 |
| Council 2 C2-10, wrapper unit gaps | UPHELD, Low | AGREE | Wrapper list verified; council 2 probe3_unit misses and probe3wrap2 nil live impact confirmed |
| Council 3 C3-1, --ship-dir= and --repo= silently ignored | UPHELD, Moderate | AGREE | _derive_ship_dir exact-match block 144-157 verified; main() stripping 1464-1471 handles the exact token only; council 3 probes P2d, P2e, P3b, P3d, P3e, P3e2 confirmed |
| Council 3 C3-2, SHIPPED.md How to verify fails literally | UPHELD (same as C1-F3), Moderate | AGREE | Same code facts as C1-F3; council 3 P6 confirmed |
| Council 3 C3-3, runner docstring -P not fixed | UPHELD (same as C1-F1), Moderate-Low | AGREE | Same code facts as C1-F1; council 3 P7d confirmed |
| Council 3 C3-4, scan fix hint misleads for directories | UPHELD, Moderate-Low | AGREE | Hint text verified at run_codex_y5.py:363 and launch_y13.py:367-369; council 3 P5a/P5a2/P5a3 confirmed |
| Council 3 C3-5, B1 wording contradictory, stale comment | UPHELD (same as C1-F5/F6), Low | AGREE | Same code facts as C1-F5 and C1-F6 |
| Council 3 C3-6, _scan_ship md5 message does not distinguish edited case | UPHELD, Low | AGREE | Message "(stale or edited ship; re-stage)" verified at launch_y13.py:1373-1374; council 3 P5e/P5d confirmed |
| Council 3 C3-7, hint-less refusal legs | UPHELD, Low | AGREE | check_manifest legs at 1188-1203 lack hints while the .pyc leg at 1199-1200 has one; _scan_ship legs at 1346-1365 lack hints; council 3 C3-7 confirmed |
| Council 3 C3-8, write_token runs before integrity checks | UPHELD, Low | AGREE | write_token at 1474, check_manifest 1475, _check_entry_pyc 1476, _scan_ship 1477; SHIPPED.md:18-20 forbids the direct form for live runs, as the adjudication states |

## Disagreement resolutions: my verdicts

1. Council 1 R2, check_manifest half REJECTED: AGREE. Council 1 line 62 says "launcher scan + check_manifest exempt top-level entry .pyc (any tag)". The scan half is true (354-355); the check_manifest half is false by the F1 proof. The adjudication is right.
2. Council 2 C2-4, R4 FIXED as applied to _check_entry_pyc REJECTED: DISAGREE with the framing, AGREE with the substance. Council 2 never applied R4 FIXED to _check_entry_pyc. Its R4 FIXED text (council 2 lines 13 and 115) is explicitly scoped to the -m guard: symlinked __pycache__ shapes "delete NOTHING outside the ship on -m (P4a/P4f/P4g)". I grepped every "symlink" mention in the council 2 paper (lines 13, 88, 115, 134, 141); none extends the claim to _check_entry_pyc. So the adjudication rejects an application council 2 did not make. The technical point is correct and I agree with it: R4 FIXED covers only the guard helper, and verifier defect 2 stands. The resolution should have been written as a scope clarification, not as a REJECT of a council 2 claim.
3. Severity votes (council 2 MEDIUM/LOW vs redteam HIGH): AGREE, redteam ratings stand. Council 2 C2-1 MEDIUM and C2-3 LOW confirmed in council 2 doc; the adjudication's reasons (headline fix failing on the live path; poisoned operator environment with silent execution at rc 0) are sound.
4. Redteam F3 vs council 2 C2-10 on wrapper live impact: AGREE, both stand. Redteam live proof and council 2 probe3wrap2 (child python separately visible in /proc, caught by the per-process scan) are both recorded in their docs and are compatible.
5. Verifier 277/280 vs redteam BLOCK consistent: AGREE. "277 of 280 checks pass" and "280 checks total, 277 pass" verified in the verifier report (75dff55); the battery contents confirm the verifier did not cover F1 (A2h/A2i isolation only), F2 (A6d ship-dir only, 15 .py names and 16 .so stems), F3 (A4 specified table only), or F4 (A5 linear only).
6. Fix-log Design C vs implemented code: AGREE. The fix log (ab0b62c, lines 43-45) says the blind entry .pyc exemption was REMOVED from the scan and from _verify_manifest; git blame shows the :1197 exemption attempt was added by 8bdd5aa, a round-2 diff commit. The adjudication is right to follow the fixed behavior rather than the log wording.

## First-hand recomputations

- Pins: runner run_codex_y5.py md5 d5047ff573820491263a2eb3805105f4, launcher launch_y13.py md5 8e72a5ce85cbaf8382f998987e8890e5, manifest codex-y5-manifest.json md5 7c76383402e4c50b28adab6b25a22e09, manifest has 27 entries. All confirmed by recomputation on todolist-push. The run_live pin 84fa106c253d5e7f16daccf2ce3f14a5 is the manifest entry for run_live.py (codex-y5-manifest.json line 13), the shipped content from 1e3901c; see E3.
- AST identity: all 14 tokenizer defs are AST-identical between the two copies with docstrings stripped (13 of 14 including docstrings; only _is_runner_cmdline differs, by the docstring self-reference naming the counterpart file). The 14 are the 12 TOKENIZER_FUNCS in improvements/y13g-verify/extract_lib.py plus _m_module_is_runner and _is_timeout_dur. This matches the verifier's own AST comparison (14 functions, docstrings stripped).
- _SHIP_FILES: 29 paths in both files, identical sets, symmetric diff empty. Confirmed by AST extraction.
- R9 _proven_no_body counts: redteam A8 14/14, verifier A8 12/12, council 2 12/12, all confirmed in the review docs; the count difference is the row set, as the adjudication states.

## Errors, gaps, and missing fixes in the adjudication

### E1. Line-range citation errors (12, none verdict-changing)

The adjudication's method section says it re-read the cited code itself, but the ranges below are wrong on todolist-push HEAD 3167c76. Four of them (a, g, h, i) match the round-2 reviews' wrong ranges verbatim (round-2 council 2 line 25; round-2 council 3 C3-6, C3-7, C3-8), which shows they were copied from the reviews, not re-derived. The file is unchanged since the round-2 diff (verified: no commit touched either entry file between 5a9b9e8 and 3167c76), so these ranges were already wrong when the reviews wrote them. The round-3 fix pass should use the corrected numbers. Correct line is given after the arrow in each item.

(a) F1 main order, cited "1468-1472" -> 1472-1478. check_go 1472, check_marker 1473, write_token 1474, check_manifest 1475, _check_entry_pyc 1476, _scan_ship 1477, check_token 1478. Lines 1468-1471 are the --ship-dir strip block.
(b) F1 _is_entry_pyc_rel, cited "295-300" -> 295-303.
(c) F2 launcher exec env, cited "1486-1498" -> env = dict(os.environ) is at 1484; the update block is 1485-1501; the PYTHONSAFEPATH comment is 1495-1497. The cited range misses line 1484.
(d) F6 runner _is_exempt_cache_dir, cited "290-312" -> 293-310.
(e) C1-F6 B1 wording, cited "plan :633-638" -> plan lines 630-631. Lines 633-638 cover the following sentences, including the false check_manifest claim.
(f) C3-4 runner scan hint, cited "run_codex_y5.py:347-353" -> 363 (the "fix" field). The launcher citation "367-371" is correct (hint at 367-369).
(g) C3-6 _scan_ship md5 message, cited "1340-1345" -> 1373-1374.
(h) C3-7 _scan_ship legs, cited "1336-1345" -> 1346-1365 (symlink dir 1346, unexpected directory 1356, bytecode 1363, unexpected file 1365; the md5 leg is 1373).
(i) C3-8 main order, cited "1474-1479" -> 1472-1478. Line 1479 is check_runner_quiet, not part of the seven-call order.
(j) C2-6 _is_codex_process, cited "872-888" -> 872-890 (the loop return True is at 889, return False at 890).
(k) C2-8 _normalize_remote_url, cited "1033-1056" -> 1033-1055 (1056 is blank). Trivial.
(l) F3 _m_module_is_runner, cited "586-600" -> 586-614 (the pdb branch starts at 600; the function ends at 614).

### E2. Resolution 2 framing (one framing disagreement)

As detailed above: the adjudication presents council 2 as having extended R4 FIXED to _check_entry_pyc and rejects that extension. Council 2 did not make that extension. The resolution's substance is correct; its attribution is not. Correct the record in the round-3 pass: R4 FIXED was always guard-only, and defect 2 is a separate, additional gap in _check_entry_pyc.

### E3. Run_live pin wording (clarification, not an error)

The adjudication lists "run_live 84fa106c253d5e7f16daccf2ce3f14a5 (pin 1e3901c holds)". That md5 is the manifest entry for run_live.py and the shipped content from 1e3901c, verified in codex-y5-manifest.json line 13 and in SHIPPED.md line 4. The working-tree run_live.py at todolist-push HEAD has md5 d8e2b14d7456b2866790f4a87ec1919e (the later Y11 version, not shipped). The adjudication's wording is accurate in context, but a reader could misread it as the working-tree file md5. Add one clarifying sentence in the round-3 record: the pin is the manifest entry, not the working-tree file.

### E4. What I checked for gaps and did not find

- No round-2 finding is missing from the decision table.
- No UPHELD finding should be REJECTED: every code fact I re-read supports the adjudication, and every live number I checked is stated the same way in the review doc that owns it.
- No severity is wrong: F1 and F2 HIGH, F3-F5 and defect 2 MEDIUM, the rest LOW or Moderate-Low, all match the code facts and the live evidence.
- The adjudication's fix instructions are complete and consistent with the fixes the reviews proposed (F1 one-line condition change plus launcher-path test; F2 env scrub plus module-top refusal plus docstring correction; F5 co_filename normalization; defect 2 realpath check; F4 --first-parent; F3 tokenizer classes (a)-(f); F6 bottom-up rmdir; F7 allowlist walk; the C-series doc and ordering fixes). I found no missing fix.
- Rules compliance of the adjudication doc: zero em dashes or en dashes (grep count 0); no personal information in the doc (file paths, line numbers, and commit hashes only).

## Limits of this council review

- I did not re-run any live battery or any live run. Live numbers cited are the reviewers' numbers from their review docs on todolist-push; my first-hand verification is the code reading and recomputation cited by file and line.
- The reviewers' live logs (for example logs/a2launcher-run3.log, logs/a6-run3.log, logs/a5-run1.log) live in the reviewers' work dirs, not on todolist-push, so I could not verify the log files themselves, only that the review docs state the numbers the adjudication quotes.
- I did not re-review round 1. Findings above are round-2 diff items or round-2 interactions with existing code.

## Council verdict

AGREE with the adjudication in full, except the framing correction in E2 and the citation corrections in E1. BLOCK stands, no live run. The round-3 fix pass should proceed on the adjudication's instructions, using the corrected line numbers in E1.
