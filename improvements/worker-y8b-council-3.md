# E1: Council Member 3 verdict, Y8b round (instrument and fix implementation)

Status: PAPER DEBATE ONLY. No Zen driving, no tab opened, no infra started, no live browser use, no ydotool. This paper judges the v2.2 fix proposal and the A1/A2 failures against the actual implementation files, not just the design text.

- Role: Council Member 3 for the E1 experiment (Worker Y8b's council). Independent of Council Members 1 and 2; verdicts below are my own from the evidence cited.
- Task received: 2026-11-21 19:33 +07. Verdict written: 2026-11-21 about 19:40 +07. Branch: todolist-push.
- Design judged: `improvements/worker-y8-e1-comparison-design.md` (v2.1 frozen, commit 695efea).
- Execution log judged: `improvements/worker-y8-e1-execution-log.md` (commit ad64bc6, A1/A2 failures and root-cause section at 19:31).
- Implementation read, with line numbers cited: `improvements/worker-y8-executor-a-brief.md`, `improvements/worker-y8-executor-a2-brief.md`, `improvements/worker-y8-executor-b-brief.md`, `improvements/worker-y8-driver-reference.md`, `improvements/worker-y8-preflight.py` (all v2.1, commit 695efea).
- Laptop evidence read via short SSH calls only (`~/workspace/ssh-laptop.sh`, each under 10 s): `/tmp/e1/plan-test-05.md` (112 lines, md5 a7b5646b2bf081386bb7bcea0563ad5a, matches the frozen value), `/tmp/e1/events-a.jsonl` (A1 command stream), `/tmp/e1/events-a2.jsonl` (A2 command stream), `/tmp/e1/repro-quote.sh` (coordinator's live reproduction script), `/tmp/e1/out.log` (five `500: Internal Server Error` lines), `/tmp/e1/preflight-a.json` (verdict VISIBLE), `/tmp/e1/step.sh` and `/tmp/e1/hand_drive_e1.py` (transport: step.sh writes `$1` to the FIFO, hand_drive does `json.loads(line)` then POSTs the JS to Marionette `/execute/sync`).
- Independent reproductions done by me on the VM (no Zen state touched): shell-argument reproduction with a stub (`/tmp/quote-repro.sh`, 19:35 +07), JSON parse checks (`/tmp/quote-json-check.py`), JS parse checks with node v24.22.1 (`new Function`, 19:36 +07). Results are quoted in Q1 and Q2 below.
- Limit, stated plainly: I did not re-run the live Marionette reproduction myself (a subagent has no live browser). The live leg rests on the coordinator's `/tmp/e1/repro-quote.sh` run on A2's tab as recorded in the log at 19:31, corroborated by `events-a.jsonl`, `events-a2.jsonl`, and the five 500 lines in `out.log`. My independent reproductions cover the shell layer, the JSON layer, and the JS layer, which is where the claimed mechanism lives; the SyntaxError to HTTP 500 mapping is corroborated by the 2 to 4 ms timings and the out.log 500s, not re-proven live by me.

## Verdicts at a glance

| Question | Verdict | One line |
| --- | --- | --- |
| Q1 quoting mechanism proven as root cause of A1 and A2? | GO | Proven. Shell parse reproduced, JS error identified by node, live repro is a controlled A/B on one tab, identical failure 2/2. |
| Q2 v2.2 fix correct and complete? | AMEND | Direction correct, wording wrong: a literal single-to-double swap breaks JSON parsing, and the escaped swap breaks plan steps 21 and 55. Exact transform specified below. Convert the plan; do not let the B executor convert at runtime. |
| Q3 A1/A2 void, budget reset, next start A3? | GO | Yes. Zero task steps in both, deterministic instrument defect, narrow void rule stated. A1/A2 stay in the record as evidence. |
| Q4 what else must change before any executor runs? | AMEND | The proposed proof is necessary but insufficient as specified. Exact expanded proof below, with commands and expected results. |
| Q5 overall: GO or NO-GO for v2.2 re-freeze + A3? | AMEND | Conditional GO: apply the Q2 and Q4 amendments, pass the expanded pre-launch proof with outputs saved, commit the v2.2 note, then run A3. No executor runs before that commit. |

## Q1. Is the shell-quoting mechanism proven as the root cause of both A1 and A2? Verdict: GO

### The shell parse, reproduced on paper from the exact command in events-a.jsonl

A1's diagnose command, decoded from `events-a.jsonl` (8 step.sh calls; the eval items are byte-identical in both attempts), is:

```
/tmp/e1/step.sh '{"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector('#contacts-count');return{...};})()"}'
```

The JSON is passed as one single-quoted shell word. POSIX shell parsing of that word:

- Quoted segment 1: `{"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector(`
- The `'` before `#contacts-count` ENDS the quoted string. `#` does not start a comment here because it is mid-word (no whitespace before it), so the unquoted segment `#contacts-count` is concatenated into the same word, quotes stripped.
- Quoted segment 2 resumes at the `'` after `#contacts-count`: `');return{readyState:document.readyState,...};})()"}`

Concatenated argument received by step.sh as `$1`:

```
{"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector(#contacts-count);return{...};})()"}
```

I reproduced this on the VM with a stub in place of step.sh (`/tmp/quote-repro.sh`, 19:35 +07). The stub received exactly `querySelector(#contacts-count)`, quotes stripped, matching the reconstruction above character for character.

### The two layers after the shell

- JSON layer: the mangled argument is still VALID JSON (`#contacts-count` sits inside the JSON string value, and JSON does not care). My check (`/tmp/quote-json-check.py`): `json.loads` succeeds and the decoded `js` is `return document.querySelector(#contacts-count)`. So step.sh accepts it, hand_drive_e1.py `json.loads(line)` accepts it (step.sh writes `$1` to the FIFO; hand_drive parses per line, line 49), and the bad value reaches Marionette.
- JS layer: `document.querySelector(#contacts-count)` is a JS SyntaxError. Verified with node v24.22.1: `new Function("return document.querySelector(#contacts-count)")` throws `SyntaxError: Private field '#contacts' must be declared in an enclosing class`. Marionette `/execute/sync` returns HTTP 500 for an invalid script. That is the 500 the executors saw, in 2 to 4 ms: an immediate syntax rejection, not a timeout and not a dead driver.

### The evidence chain, each link checked

1. `events-a.jsonl`: A1's diagnose eval carries the single-quoted form `querySelector('#contacts-count')` inside the single-quoted shell word, twice (diagnose plus retry). `events-a2.jsonl`: A2's eval is the same form (10 step.sh calls; the eval command opens with the identical pattern, `set -o pipefail` prefix aside). Both executors ran only 4 driver commands: new_session ok, new_tab ok (1101 ms A1, 1128 ms A2), diagnose eval HTTP 500 twice. No task step was attempted in either run.
2. `out.log`: five `500: Internal Server Error` lines (A1 two, A2 two, plus the coordinator's repro case A). The 2 to 4 ms timings in the log falsify a driver death or a hang: a dead driver or a stuck Marionette call fails on a seconds-scale timeout, not in 2 ms.
3. Live reproduction (`/tmp/e1/repro-quote.sh`, on A2's own tab, read-only evals): case A, the executor's exact quoting, returns HTTP 500; case B, the identical JS with the selector in double quotes (written `\"#contacts-count\"` in the shell single-quoted string, so the JSON decodes to `"#contacts-count"`), returns `"6"`. Same tab, same JS modulo quote style, opposite outcomes. That is a controlled experiment, and it kills the log's earlier guess ("tab mid-state at eval time"): tab state was held constant while quoting varied.
4. The two paths diverge, which is why pre-flight passed and the executors failed: `preflight.py` calls step.sh via `subprocess.run([STEP, json.dumps(cmd)], ...)` (list argv, no shell), so its single quotes survive intact, and `preflight-a.json` is VISIBLE with countText "6". The coordinator's own diagnosis at 19:23:17 used double quotes and returned the full VISIBLE snapshot on the executor's own tab. The briefs and the driver reference prescribe the single-quoted shell path and give no quoting guidance, so the executor did the natural thing and the instrument punished it for it.
5. A2 replicates A1 exactly (same step, same command, same 500s). A deterministic mechanism failing 2/2, plus a live A/B on one tab, plus my shell/JSON/JS reproductions, is proof, not a guess.

### What evidence would falsify it

Any one of these, had it obtained, would have falsified the mechanism; none did:

- (a) The fixed double-quoted form through the identical shell path also returning HTTP 500 on the same tab. It returned `"6"`.
- (b) `events-a.jsonl` showing the executor used double quotes, a heredoc, a file, or any transport other than the single-quoted shell word. It shows the single-quoted word with single quotes inside.
- (c) The coordinator's double-quoted eval on the same tab also returning 500. It returned the full VISIBLE snapshot.
- (d) The reconstructed `$1` still containing the quotes around `#contacts-count`. My stub run shows them stripped.
- (e) A slow failure (seconds) instead of 2 to 4 ms, which would point at a driver or Marionette stall. The failures are immediate.

A residual note, not a falsifier: the mapping "JS SyntaxError becomes Marionette HTTP 500" is corroborated by out.log and timing, not re-proven live by me (see the limit at the top). If a future reader wants that leg re-proven, the repro script already on the laptop does it in one run.

## Q2. Is the v2.2 fix correct and complete? Verdict: AMEND

The fix direction is correct: JS string literals inside the JSON must use double quotes, because the JSON travels inside a single-quoted shell word. But the proposal as worded ("single to double quotes", "mechanical single-to-double conversion ... only quote characters change") is wrong in two places, and the audit below shows exactly where. The correct transform is specified in item 2.

### Audit: every single quote in the briefs, the driver reference, preflight.py, and the plan

Briefs (A line 25, A2 line 25, B line 25): the diagnose JS contains exactly one single-quoted JS string each: `document.querySelector('#contacts-count')`. That is the trap, in all three briefs identically. Covered by fix (a) once the transform is specified as in item 2.

Must NOT be converted (prose, not JS):

- Briefs A/A2/B line 17 and driver reference line 7: `step.sh '<json>'`. This describes the shell form itself. It must stay single-quoted; changing it would misdescribe the transport and hide the reason the rule exists.
- A2 brief line 13: `the first attempt's artifacts` (prose apostrophe). Must not be converted.
- Plan line 3: `step.sh '<json>'` (same prose as above). Must not be converted.

Driver reference line 9: the click_js template is `document.querySelector('...')`, single quotes. This is NOT covered by fix (a) as listed (fix (a) names only the diagnose JS), and it matters: it is the example an executor copies literally when writing its own click_js, and as written it teaches the trap. It must change to the double-quoted form with the escaping note from item 2. The eval line on the same line already carries the `return` rule from v2.1; the quoting rule belongs next to it, not in an appendix.

Preflight.py: JS single quotes at lines 37 (`querySelector('#contacts-count')`), 43 (`getAttribute('style')`), 45 (`getAttribute('style')`), 48 (`' '`), 60 (`remove('tz-hidden')`), 61 (`removeProperty('--zen-logo-path')`). Prose apostrophes that must NOT be converted: line 7 (`extension's`), line 14 (`executor's`), line 145 (`extension's`), all in the docstring or comments. Note on necessity: preflight.py is NOT affected by the trap (subprocess list argv, no shell), so changing it is uniformity, not correctness. I still support changing it, because three paths with two quote styles is what made this bug hard to see (pre-flight passed, executors failed, coordinator diagnosis passed), and unifying the style removes a future copy-paste reintroduction. But the change must be verified by re-running preflight live afterwards (Q4 item 3f), because a typo there breaks the gate rather than the executor.

Plan (`/tmp/e1/plan-test-05.md`, md5 a7b5646b2bf081386bb7bcea0563ad5a): 25 lines contain a single-quote character (grep). One is prose (line 3, `'<json>'`, do not convert). The other 24 lines are JSON commands, and they contain 78 single-quoted JS string literals in 24 commands: 17 evals (steps 4, 7, 16, 21, 24, 30, 32, 35, 38, 41, 42, 43, 44, 45, 53, 54, 55) and 7 click_js commands (steps 6, 20, 23, 29, 31, 34, 47). Line numbers: 44, 46, 47, 56, 60, 61, 63, 64, 69, 70, 71, 72, 74, 75, 78, 81, 82, 83, 84, 85, 87, 93, 94, 95. Two corrections to the task text's shorthand: the plan has 19 eval commands in total (steps 3, 4, 7, 16, 21, 24, 30, 32, 35, 38, 41, 42, 43, 44, 45, 53, 54, 55, 56), not 21; steps 3 (`localStorage.clear()`) and 56 (`return window.__agyVerify()`) contain no single quotes and need no change. No JS string in the plan contains an apostrophe in prose, and no plan JS string contains a prose apostrophe; the only double quotes inside plan JS are the two `italic` selectors below.

### 1. The naive transform breaks JSON parsing (proven)

A literal character swap `'` to `"` in the file text turns the brief diagnose JSON into:

```
{"cmd":"eval","js":"return document.querySelector("#contacts-count")"}
```

That is INVALID JSON: the bare `"` after `querySelector(` terminates the `js` string. My check: `json.loads` fails with `Expecting ',' delimiter: line 1 column 52 (char 51)`. Applied to the plan, the same swap fails the same way (column 53 on the step 21 test string). A fix applied literally as worded would swap a JS SyntaxError (HTTP 500 from Marionette) for a JSON parse error (`{"ok": false}` from hand_drive), and both arms would still fail at the same step. The v2.2 text must not say "single to double quotes" without the escaping.

### 2. The correct transform, specified exactly

Inside a JSON string value in the briefs and the plan, a JS single-quoted string `'...'` becomes `\"...\"` in the FILE TEXT (backslash-doublequote). The shell single-quoted word passes the backslash through literally; `json.loads` decodes `\"` to `"`; the JS engine receives `"..."`. Proven: repro-quote.sh case B uses exactly this form and returns `"6"`, and my JSON check confirms `json.loads` succeeds and the decoded JS is `return document.querySelector("#contacts-count")`, which node parses OK.

In preflight.py (Python triple-quoted string, no JSON layer), the transform is a plain character swap `'` to `"`. No backslash is involved there.

### 3. Steps 21 and 55 are special cases: even the escaped transform breaks them (proven)

Steps 21 (line 61) and 55 (line 95) contain `.meta-line[style*=\"italic\"]` inside a single-quoted JS string. The decoded JS today is valid: `'.meta-line[style*="italic"]'`. Apply the escaped transform from item 2 and the decoded JS becomes `".meta-line[style*="italic"]"`, where the inner `"` terminates the JS string. Node: `SyntaxError: missing ) after argument list`. So the mechanical conversion, even done with correct JSON escaping, breaks exactly these two steps, and they are final-verification-adjacent (step 21 checks the Frank card notes; step 55 is the final Frank DOM read). A B run with a naive conversion would 500 at step 21 and fail the Frank checks.

The fix for these two selectors, frozen explicitly (pick one, do not leave it to the converter):

- Preferred, content-preserving: JS-escape the inner quotes, so the decoded JS is `".meta-line[style*=\"italic\"]"`. In file text that is `\".meta-line[style*=\\\"italic\\\"]\"`. Node: PARSES OK (verified). The selector text is unchanged; only its quoting layers change.
- Acceptable alternative: drop the inner quotes, `.meta-line[style*=italic]`, which is valid CSS for a single-token value. Simpler to read, but it changes the selector text, so it needs the same live probe as the preferred form (Q4 item 3d).

Either way, the diff proof in fix (c) cannot be "only quote characters change": the correct transform also adds backslashes, and for steps 21/55 it adds backslashes in a different pattern. The honest diff proof is semantic: decode the old and new JSON commands, and show the decoded JS string values are identical except for quote style, and that every decoded `js` value parses (Q4 item 3e).

### 4. Convert the plan; do not let the B executor convert at runtime

Converting the plan once, by the coordinator, with the diff proof above, is the right call. Runtime conversion by the B executor is the wrong call, for four reasons:

- It violates the B brief steps 2 and 3 ("execute ONLY that plan", "where the plan gives an exact command, run exactly that command"). An executor that rewrites 24 commands before running them is re-deciding, and a B pass afterwards could be credited to executor improvisation rather than to the plan.
- It injects nondeterministic agent judgment into 24 commands, including the two nested-quote special cases, with no advance audit. The coordinator's one-time conversion is checkable; a live conversion is not.
- It does not fix the briefs' diagnose JS, which the B executor must also paste verbatim before plan step 3. The brief fix is needed regardless.
- The A executor cannot runtime-convert a brief it is ordered to follow exactly, and A writes its own evals freely, so the durable protection for A is the driver-reference rule (item 5), not a runtime instruction.

Converting the plan does change the frozen deliberated artifact (its md5 changes), and that must be recorded as a v2.2 re-freeze with the new md5, exactly as v2.1 did for the `return` fix. The change is to the encoding layer only, not to deliberated content: same selectors, same values, same order, same 58 steps. The semantic diff proof in item 3 is what makes that claim checkable rather than asserted.

### 5. What fix (b) must actually say

The driver-reference quoting rule must be written next to the eval line, in this substance: "The JSON is passed to step.sh inside a single-quoted shell word. Therefore every JS string literal inside the JSON MUST use double quotes, written as `\"` in the file text; a single quote anywhere inside the JSON ends the shell quoting, is stripped, and reaches Marionette as a JS SyntaxError, which Marionette reports as HTTP 500 in a few milliseconds while the driver, geckodriver, and port 4451 are all alive. Symptom: HTTP 500 in 2 to 4 ms on an eval or click_js, driver stack alive, is the quoting trap until proven otherwise. The click_js template on this page uses double quotes for the same reason. Any eval or click_js you write yourself must follow the same rule." The rule must also state the A-arm residual: A writes its own evals, so no advance grep can cover A's future commands; the rule is the mitigation, and the coordinator's DRIVER DEAD checklist (Q4 item 3h) is the backstop.

### 6. A2 brief: do not edit it

Fix (a) as listed names "briefs A/A2/B". The A2 brief is now a historical artifact of a voided run (Q3). Editing it rewrites evidence. Fix the base A brief and the B brief, and create a new A3 brief from the fixed A brief (Q4 item 3g). Leave the A2 brief byte-identical as the record of what A2 was actually ordered to do.

Q2 verdict: AMEND. The fix is correct in direction and wrong in its stated mechanics. Apply the exact transform in items 2 and 3, the driver-reference text in item 5, and the A3-brief point in item 6, then the fix is complete.

## Q3. Are A1/A2 void as instrument artifacts with the retry budget reset and the next A start labelled A3, or is arm A exhausted at 2 starts per the design cap? Verdict: GO (void, reset, A3)

A1 and A2 are VOID as instrument artifacts. The retry budget is reset. The next A start is labelled A3. The strict reading (arm A exhausted, comparison aborted) is rejected, for the reasons below.

### Why void, not FAIL and not exhausted

1. Zero task observations exist to preserve. Both runs stopped at the executor-tab diagnose, before the first spec step. Zero spec steps attempted, zero checks read, zero task driver commands beyond new_session and new_tab. There is no data to discard, so voiding discards nothing.
2. The cause is a deterministic defect in the frozen instrument, not executor luck and not browser health. The brief's own prescribed JS, pasted through the shell path the brief itself prescribes, cannot run. The failure is 2/2 identical, reproduced live on demand, and reproducible by me at the shell layer. The design's retry cap exists to prevent re-running bad draws until a lucky pass (Council 3 round 1, Q2 BLOCK: selection bias from discarding failing partials). That rationale does not apply here: no luck was sampled, no partial run exists to select on, and A3 will test a fixed instrument, not a new draw from the same distribution.
3. Precedent in the same run, already accepted by the coordinator: the 18:55:40 pre-flight failure (missing `return`, v2.1) consumed no retry budget because "no valid pre-flight had run, no classification was made". The 19:06 pre-flight #2 failure (driver died) was treated as "infra fault, not an arm retry (no valid pre-flight had yet run, no arm started)". A1/A2 are the same in substance: no valid arm start had run, no task classification was made. The only difference is formal (the executor process had spawned and opened a tab), and that formality is exactly what the instrument defect caused: the executor could not get past the gate the instrument itself wrote.
4. The design's post-start rule ("the first started run IS the arm's result") presupposes a runnable instrument. It was written for crashes, DRIVER DEAD, and mid-run hidden body. None of those occurred: no crash, the driver was proven alive by three checks plus live evals, and the tab was proven VISIBLE. Applying the post-start rule here would score a coordinator instrument bug as an executor failure, and would kill the experiment over a typo-class defect that was never part of the treatment. The "second crash ends the arm as BLOCKED" rule likewise does not apply: there was no crash.
5. Symmetry is preserved. B has not run; its 2-start budget is intact. The fix applies identically to both arms (briefs, driver reference, plan), so A3 and B1 both run under the same v2.2 instrument. Resetting A's budget does not favor A over B; it restores the starting position both arms were promised.

### The narrow void rule (so this cannot be reused to void a genuine failure)

A start is void as an instrument artifact ONLY when all four hold: (i) the failure occurs before the first task step (here: at the executor-tab diagnose, step 3 of the brief); (ii) the root cause is proven to be a defect in the frozen instrument (brief, plan, driver reference, preflight.py), not an executor choice; (iii) the defect is deterministic and reproducible on demand (here: 2/2 identical plus live repro); (iv) the fix is applied identically to both arms before any further start. A mid-task executor failure, a genuine DRIVER DEAD, or a hidden-body hit does not meet this rule and is governed by the existing invalid-run rules unchanged.

### Consequences, frozen in the v2.2 note

- A1 and A2 stay in the record, labelled VOID (instrument artifact), with their evidence attached (events-a.jsonl, events-a2.jsonl, out.log 500s, repro-quote.sh). Nothing is deleted or relabelled as a clean run.
- The next A start is A3, with its own brief (Q4 item 3g) and report file run-a3-report.md. It is the first VALID A start, not a retry of a valid run.
- Voided-start wall time is EXCLUDED from A's execution total (A1 coordinator wall 151 s, A2 wall to be recorded from its report), and the exclusion is frozen here, not chosen after A3 runs. The design's "retry waiting time and failed-attempt wall time count toward the arm's total" was written for genuine retries; applying it here would bake the coordinator's instrument bug into A's total. The voided walls are still reported separately in the run record for transparency.
- The "no clean win/loss if either arm needed an infra retry" clause is NOT triggered by the void: A1/A2 were not infra retries, and A3 does not run under a confound. This is a judgment call, flagged as such: the void and its cause must still be disclosed prominently in the final verdict, so a reader can disagree with the call on the record.
- The replication trigger is re-evaluated on the pilot pair (A3, B1), not on the voided runs.

## Q4. What else must change before any executor runs? Verdict: AMEND

The task's proposed proof (fixed diagnose JS through the executor's exact shell path returning a real snapshot, plus a grep sweep proving zero single quotes remain in any JS the executors will paste) is necessary and is the core of the gate. As specified it is insufficient: it omits the plan probes, the JSON/JS parse sweep, the steps 21/55 probe, the md5 re-freeze, the archiving, and the DRIVER DEAD checklist. The exact expanded proof is below. No executor runs until every item passes and the v2.2 note is committed.

### 1. Apply the corrected fix first (from Q2)

- Base A brief and B brief: diagnose JS converted with the `\"` transform (Q2 item 2).
- Driver reference: quoting rule added next to the eval line (Q2 item 5) and the click_js template converted to double quotes.
- Preflight.py: JS strings converted with the plain swap (Q2, preflight note); prose apostrophes at lines 7, 14, 145 untouched.
- Plan: all 78 JS string literals converted with the `\"` transform, except steps 21 and 55 which use the JS-escaped inner-quote form (Q2 item 3, preferred form). Prose line 3 untouched.
- New A3 brief created from the fixed A brief (item 3g below). A2 brief left byte-identical.

### 2. Pre-launch proof, exact commands and expected results (all on the laptop, in /tmp/e1, live Zen, through step.sh)

All probes use the executor's exact shell path (`/tmp/e1/step.sh '<json>'`, single-quoted JSON), NOT the preflight.py argv path. The argv path is proven incapable of catching this bug class, so a proof that uses it proves nothing about the fix. Each probe runs on a fresh sacrificial tab (new_session, new_tab to the fixture URL, 1.0 s settle), and the tab is closed and the session deleted afterwards. Save every probe output to `/tmp/e1/v22-proof-<name>.log` and commit the log excerpts to the execution log.

- (a) Fixed diagnose JS, copied verbatim from the fixed A brief, through step.sh. Expected: `{"ok": true}` with a real VISIBLE snapshot: bodyVis "visible", bodyOpacity "1", bodyDisplay "block", countText "6", readyState "complete". This is the direct regression test for A1/A2.
- (b) Plan step 4 eval (the widest eval: four selectors, Array.from, map) through the same shell path on the same tab. Expected: `{"ok": true}`, count "6", cardCount 6, all six card ids, all six names. This proves the multi-selector evals survive the conversion, not just the one-selector diagnose.
- (c) Plan step 31 click_js (`document.querySelector(\"#btn-fav-contact-david-kim\")`) through the same shell path, followed by the plan step 32 eval. Expected: click_js `{"ok": true}`, step 32 read starActive true, cardFavorite true. This proves the click_js commands survive. Note: the star toggles fixture state on the proof tab; the proof tab is sacrificial and is closed afterwards, never reused for an arm.
- (d) Steps 21/55 italic-selector probe: a standalone eval containing the converted selector, `document.querySelector(".meta-line[style*=\"italic\"]")`, run through the same shell path on the fresh tab (Frank does not exist yet on a fresh tab, so the selector matches nothing). Expected: `{"ok": true}` with result null, NOT a 500. A null proves the JS parses and runs; a 500 would prove the conversion is still broken. Do not skip this probe: it is the only live check of the one transform the mechanical conversion gets wrong.
- (e) Plan step 56 eval (`return window.__agyVerify()`) through the same shell path. Expected: `{"ok": true}` with the verifier JSON (on a fresh tab it will report the unmodified state, which is fine; the point is the eval path, not the values).

### 3. Sweep and freeze (all before A3 launches)

- (a) JSON parse sweep: every JSON command in the fixed plan (all 58 steps) must parse with `python3 -c "import json; ..."` (extract each backticked JSON object, `json.loads` each). Any failure stops the launch.
- (b) JS parse sweep: every decoded `"js"` value in the fixed plan and in the fixed briefs must parse with node (`new Function(js)` parses without executing). Any SyntaxError stops the launch. This sweep is what would have caught steps 21/55.
- (c) Single-quote sweep, scoped correctly: grep for `'` inside decoded `"js"` values only, across the fixed briefs, the driver reference examples, and the plan. Expected: zero. A whole-file grep is the WRONG sweep: it would flag the prose that must stay (plan line 3, briefs line 17, driver reference line 7, A2 line 13 `attempt's`, preflight.py lines 7, 14, 145). Confirm each of those prose exceptions is untouched and list them in the proof log.
- (d) Semantic diff proof for the plan: decode the old and new JSON commands step by step and show the decoded JS string values are identical except for quote style, and the decoded JSON keys, order, values, and step count (58) are unchanged. The diff must NOT be claimed as "only quote characters change" (Q2 item 3: the correct transform adds backslashes).
- (e) Fresh pre-flight A3 under the fixed preflight.py (proves the uniformity edit did not break the gate). Expected: VISIBLE, exit 0, real snapshot, countText "6", saved to `/tmp/e1/preflight-a3.json`.
- (f) md5 re-freeze, recorded in the design v2.2 note and the execution log before A3 launches: new plan md5, brief A md5, brief A3 md5, brief B md5, driver reference md5, preflight.py md5. The design v2.2 note records, in the same pattern as the v2.1 note: the root cause in one paragraph, the exact fix, the Q3 void rule and wall-time exclusion, the new md5s, and the pre-launch proof outputs by filename.
- (g) A3 brief: new file `improvements/worker-y8-executor-a3-brief.md`, derived from the fixed A brief, with report file run-a3-report.md and an explicit ban on A1/A2 artifacts (run-a-report.md, run-a2-report.md, events-a.jsonl, events-a2.jsonl, out.log), mirroring the A2 brief's ban on A1 artifacts. A3's executor is a fresh codex process that must not see the previous attempts.
- (h) Coordinator DRIVER DEAD checklist, added to the design: before accepting any future DRIVER DEAD declaration, the coordinator must inspect the failed command's JS in the events file for single quotes (the quoting trap) and record the check with the result. This is the one-minute check that would have caught the trap at A1 without a council round. It also applies to any future HTTP 500 in 2 to 4 ms with the driver stack alive.
- (i) Archiving and evidence: archive the current `/tmp/e1/out.log` (containing the five 500s) to a timestamped file before A3 starts, per the per-arm archiving rule; commit `/tmp/e1/repro-quote.sh` to the repo under `improvements/` as the evidence artifact for the root cause (it currently exists only on the laptop); record A1/A2 as VOID in the execution log with the evidence filenames.

## Q5. Verdict: AMEND (conditional GO for the v2.2 re-freeze + A3)

GO, conditional on all of the following, in order: (1) the Q2 amendments are applied exactly as specified (the `\"` transform in JSON text, the steps 21/55 special case, the driver-reference rule and click_js template, the A3 brief, the A2 brief left frozen); (2) the Q4 expanded pre-launch proof passes in full, with its outputs saved and its md5s recorded; (3) the design v2.2 re-freeze note is written and committed with the void rule, the wall-time exclusion, and the new md5s. Then, and only then, A3 launches.

If any pre-launch probe returns HTTP 500, fails JSON parsing, or fails JS parsing, stop: do not fix forward live, return to council with the failing output. If the proof passes, A3 is the first valid A start, B1 follows under the same v2.2 instrument, and the pilot pair (A3, B1) is judged under the frozen v2.1 win criteria, with the replication trigger re-evaluated on that pair.

No executor runs before the v2.2 commit. This verdict does not decide alone; the parent reconciles all council verdicts.

## Timing log (all Asia/Ho_Chi_Minh)

- 19:33 task received; read design (156 lines), execution log (57 lines), briefs A/A2/B, driver reference, preflight.py (198 lines).
- 19:34 to 19:36 laptop evidence via short SSH calls: plan md5 + line count, full plan text (112 lines), plan grep (25 lines with single quotes), repro-quote.sh, events-a.jsonl exact command, events-a2.jsonl, out.log 500s, preflight-a.json VISIBLE, step.sh + hand_drive transport.
- 19:35 shell reproduction on the VM (`/tmp/quote-repro.sh`): executor form received as `querySelector(#contacts-count)`; fixed form received with `\"` intact; naive form received as broken JSON text.
- 19:35 JSON checks (`/tmp/quote-json-check.py`): executor form JSON OK with broken JS; naive form JSON FAIL; escaped form JSON OK; escaped step 21 JSON OK but JS broken (confirmed by node).
- 19:36 node JS checks: broken selector SyntaxError (private field); escaped step 21 SyntaxError (missing `)`); JS-escaped step 21 PARSES OK; fixed selector PARSES OK.
- 19:37 read Council 1 and Council 2 verdicts for format and consistency (no coordination on conclusions).
- About 19:40 verdict written to `improvements/worker-y8b-council-3.md`; committed and pushed on todolist-push.

Council Member 3 (Y8b round), 2026-11-21. Verdicts: Q1 GO, Q2 AMEND, Q3 GO, Q4 AMEND, Q5 AMEND (conditional GO).
