# Council Member 3 verdict: Worker Y11 integration and JSONL schema

- Role: Council Member 3, debating one question only: where the hooks go, and what the exact JSONL schema is.
- Verdict: AMEND. The design direction is right (one file, one wrapper module, no changes to timing.py or hit_rate.py, metrics optional and off by default behavior). The design as proposed is not shippable as written: it names two file writers and one id validator that, used as described, would produce duplicate summary rows, rejected selectors, and a hit-rate field collision. Every flaw below is fixable by a listed amendment. No flaw requires a redesign.
- Single weakest point: the proposal treats TimingLogger and hit_rate.py as drop-in writers when both are already file writers with incompatible assumptions. TimingLogger always writes its own rows and its own summary row; hit_rate.append_attempt validates ids that live selectors fail and verifies the whole file on every call. Wrapping them without intercepting their writes does not give one clean file. It gives three writers fighting over one file. Amendment A1 (single writer) is the load-bearing fix. Everything else is detail.

## Work log (wall-clock Asia/Ho_Chi_Minh, elapsed from task receipt)

- 18:52:40 +07 (elapsed 0s): task received. Council Member 3 brief, Y11 integration and schema.
- 18:52-18:54 +07 (elapsed about 0-2 min): read worker-y3-fcc-verification.md lines 233-234 and 253 (H2, I8, G22 gap statements), scripts/timing.py (full), scripts/jsonlutil.py (full), scripts/hit_rate.py (full), scripts/calibration_e2.py (full), tests/test_timing.py, tests/test_hit_rate.py, tests/realistic/run_live.py (full, including run_one and main), tests/realistic/run_agyq2.py (imports, bootstrap, main), tests/realistic/run_agyq.py (run_one, main), tests/realistic/run_fcck.py (run_one, main), tests/realistic/run_agy_y2.py (Y9WD, Y9Runner, main loop), tests/realistic/hand_drive.py (full).
- 18:54 +07 (elapsed about 2 min): line numbers confirmed by grep for citation (run_live.py LOG_PATH:54, log_step:69, WD:262, Runner:559, run_one:1408, main:1427; timing.py _write:98, think_step:102, note_action:109, _finish_step:116, pace:129, summary:140; hit_rate.py BACKENDS:8, ISSUES:9, append_attempt:20, summarize:58).
- 18:54-18:56 +07 (elapsed about 2-4 min): verdict written to this file. No git commands run, nothing committed, no live run made.

## Evidence base (what was actually read, not assumed)

- Y3 gap audit (improvements/worker-y3-fcc-verification.md): H2 says TimingLogger exists but zero production files import it and no run-timing JSONL exists anywhere; I8 says hit_rate.py exists for calibration fixtures only (calibration_e2.py:27,110 uses it; tests/calibration-e2-hits.jsonl has 87 records) and the realistic harness records only pass/fail; G22 says timing "always on" is dead code in production. The gap is wiring, not invention.
- scripts/timing.py: TimingLogger(path, run_id, clock=time.monotonic). Rows use keys run, wall (wall_text, "%Y-%m-%d %H:%M:%S %Z", Asia/Ho_Chi_Minh), elapsed_s, event. _write opens the file in text append mode per row and writes json.dumps with default separators plus "\n". It repairs a missing trailing newline only once, in __init__ via _ensure_trailing_newline. think_step is a context manager that calls note_model_call() on entry and _finish_step on exit. note_action writes an action row immediately and increments self.actions. _finish_step writes a step row with think_s, act_s, total_s, actions, slow_think (think_s > SLOW_THINK_S, 60.0). pace() computes model_calls, actions, actions_per_call, slow_think (ratio < MIN_ACTIONS_PER_CALL, 1.0), slow_steps. summary() writes a second row, {"event": "summary", **totals}, and returns totals. Totals include run, wall, elapsed_s, steps, think_median_s, think_max_s, total_median_s, total_max_s, pace fields, over_small_task_budget (elapsed > 300 and steps <= 6).
- scripts/jsonlutil.py: append_jsonl(path, record) opens in binary append mode, writes b"\n" first when the file is non-empty and lacks a trailing newline, then writes one compact-separators JSON line. verify_jsonl parses every line and reports bad 1-based line numbers; a blank line counts as bad.
- scripts/hit_rate.py: BACKENDS = {dom, desktop, a11y}. ISSUES = {wrong_target, coordinate_mapping, visual_grounding, occlusion, unresponsive, unknown}. _SAFE_ID = ^[a-z0-9][a-z0-9_-]{0,63}$. append_attempt validates case_id, intended_target and actual_target against _SAFE_ID, requires attempt to be a positive int, requires a known issue_group on any miss, computes hit as actual == intended, writes via append_jsonl, then checks the trailing newline and runs verify_jsonl over the whole file on every call. summarize(path) reads the whole file, filters event == click_attempt, raises on duplicate (case_id, attempt) keys, and returns attempts, hits, misses, hit_rate (None when zero attempts), by_backend, misses_by_issue.
- tests/realistic/run_live.py: LOG_PATH = Path(os.environ.get("LIVE_LOG", "/tmp/worker-p-live.jsonl")) at line 54. log_step(test, step, op, elapsed_ms, ok, detail, error) at line 69 appends {"ts": now_iso() (UTC ISO), "test", "step", "op", "elapsed_ms", "ok", "detail", "error"} with a plain open(LOG_PATH, "a") write and no newline repair. WD at line 262, Runner at line 559, run_one at line 1408, main at line 1427. WD.click(css) at line 507 does scroll_into_view, find, then POST /element/{id}/click. WD.click_js(js_expr) at line 512 does eval(f"({js_expr}).click()") with no scroll, no find, no return value despite its docstring saying it returns the element. Runner.step(name, op, fn) at line 568 times fn with perf_counter, calls log_step, prints "[test] name ok/FAIL {ms}ms detail=... error=...", appends to failures and raises on failure. Runner.check at line 584 only prints and records, never logs a step. run_one creates Runner(test_id, base_url), runs fn(r, d) inside WD(), prints "RESULT " + json summary. main loops tests and prints "SUMMARY {passed}/{total} passed, total_ms=...".
- tests/test_timing.py and tests/test_hit_rate.py: unittest, sys.path insert of scripts/, FakeClock for timing, tmp dirs, assertions on rows and on verify_jsonl == [].
- run_agyq2.py: imports WD, Runner, log_step, diagnose_body, start_server from run_live. No run_one function. main at line 1501 creates Runner(tid, base) inline in the loop, manages WD() with manual __enter__/__exit__, and creates Runner("bootstrap", base) in bootstrap_tab at line 1301. Its own _log_diag and ensure_visible call log_step directly.
- run_agyq.py: own run_one at line 692 and main at line 706, both local copies of the run_live shape, importing only WD, Runner, start_server from run_live.
- run_fcck.py: own run_one at line 829 and main at line 843, same local-copy shape.
- run_agy_y2.py: imports WD, Runner, diagnose_body, log_step as _rl_log_step from run_live, then defines its own module-local log_step (lines 181-190) with an extra "attempt" field from the _CURRENT_ATTEMPT global, Y9WD(WD) at line 248 (overrides _wd to count wd_calls, adds find_in, click_el, type_in, screenshot), Y9Runner(Runner) at line 291 (overrides step entirely with its own attempt-aware log_step call, adds gaps list and gap()), and main at line 2265 which rotates LOG_PATH at launch, retries infra-blocked tests once (attempt 1 then 2), and builds its own suite summary.
- hand_drive.py: standalone stdin JSON loop, no WD import, no Runner, no log_step. Own wd() helper, hardcoded WD_PORT 4450, commands new_session, new_tab, find, clear, type, click, click_js, eval, text, value, set_file, close_tab, delete_session, quit. Prints one JSON result per command with ms.

## Q1. One file vs two files, and is mixed writing safe?

Answer: ONE file per run. The proposal is right on this point and must not be changed to two files.

Why one file wins for a single run's before/after comparison:

- One file preserves chronological order across event kinds. A reader sees step, then the click_attempts inside that step, then the next step, then the summary, with no join. Two files force a join on run_id plus wall/elapsed_s across files, and the join is the thing that breaks first in practice.
- One file has one run_id, one rotation story, one path to cite. Two files double the chance that one file gets rotated, renamed, or left behind while the other is read. run_agy_y2.py main already rotates LOG_PATH at launch; a second metrics file would need its own rotation rule, and any mismatch desyncs the pair.
- hit_rate.summarize already filters by event == click_attempt, and TimingLogger.pace reads in-memory steps, so a mixed file does not confuse the existing readers as long as each reader filters by event. The summary row is the merge point, and it lives in the same file.
- The before/after comparison the user wants (H2 think time, I8 hit rate, same run) is a single-row-set question: one run_id, one file, filter by event.

What breaks with two files (timing JSONL + clicks JSONL):

- The click-to-step attribution breaks. A click_attempt in file B can only be tied to a step in file A by timestamp proximity, which is approximate and fails whenever two steps are fast or a click happens outside a step.
- The summary merge breaks. A merged summary needs both files present and both parsed; if either file is missing, truncated, or from a different run_id, the merged number is silently wrong instead of loudly absent.
- Rotation and retention break independently per file. One file rotated, the other not, and the pair no longer describes the same run.
- hit_rate.summarize on a clicks-only file works, but then the timing summary in the other file cannot see the clicks, so the "one reader judges the run without opening another file" requirement (Q6) fails by construction.

Is mixed writing safe as proposed? NO, not as proposed. The proposal says LiveMetrics wraps one TimingLogger plus click_attempt recording into one file, with timing.py and hit_rate.py unmodified. That means two, in fact three, writers would touch the file:

1. TimingLogger._write (timing.py:98): text-mode open-append per row, default json separators, trailing-newline repair only in __init__. It does NOT repair before each row.
2. jsonlutil.append_jsonl (via hit_rate.append_attempt): binary append, compact separators, repairs a missing trailing newline before every write, then runs verify_jsonl over the whole file.
3. LiveMetrics itself, if it writes anything directly.

In a single process, single thread, sequential writes, with every row ending in "\n", this usually does not tear a line. "Usually" is not safe. The failure modes are concrete:

- A torn tail (killed process mid-write, disk full, truncated file) is repaired only when the NEXT writer is append_jsonl. If the next writer is TimingLogger._write, the new row glues onto the torn line and the whole file fails to parse. verify_jsonl then reports the glued line, and every row after it is suspect.
- TimingLogger.summary() writes its own {"event": "summary", ...} row. If LiveMetrics also writes a merged summary row, the file has TWO summary rows with different shapes (TimingLogger's has no test field, no click fields, no schema version; LiveMetrics' has test null plus merged fields). A reader taking the last summary, or the first, gets a different answer. This is a duplicate-summary bug, not a style issue.
- hit_rate.append_attempt runs verify_jsonl over the whole file after EVERY attempt. On a merged file that cost is O(file size) per click, so total cost is O(clicks x file size), and it raises ValueError on any bad line anywhere in the file, including a line TimingLogger wrote. A metrics write failure then raises inside a click path, which is exactly the failure mode Q5 forbids.
- hit_rate.append_attempt rejects live selectors. "#btn-save-board" contains "#", "button[onclick=\"clickCell('a2')\"]" contains brackets, quotes, and parens. Both fail _SAFE_ID (hit_rate.py:11). The proposal's click_attempt row (hit_rate fields + selector) cannot pass through append_attempt unchanged. See Amendment A2.
- hit_rate.summarize raises on duplicate (case_id, attempt). On a merged file where "attempt" means the Y9 re-run attempt (1 or 2), two clicks in the same test in the same re-run attempt share (case_id, attempt) and summarize raises. See Amendment A3.

The fix is not two files. The fix is one file with exactly ONE writer function. Amendment A1 states it precisely: LiveMetrics is the sole writer, every row goes through jsonlutil.append_jsonl, TimingLogger is used as an in-memory calculator only (its _write overridden to stash, never to touch the file), hit_rate.append_attempt is never called on the live path, and hit_rate.summarize is never called on the merged file. TimingLogger.__init__ still runs _ensure_trailing_newline on the metrics path at construction, which is harmless and desirable, but no TimingLogger row ever reaches the file except through LiveMetrics._write.

## Q2. Exact schema

Conventions for every row:

- JSON object, one per line, compact separators (append_jsonl), UTF-8, trailing "\n", no blank lines (verify_jsonl treats a blank line as bad).
- No typed text values, no file contents, no page titles, no URLs with query strings in any row. Selectors are identifiers, not content. Type actions log text length, never the text. Set-file actions log the basename, never the full path.
- Numbers are JSON numbers, not strings. Times in seconds are floats rounded to 3 decimals. Booleans are JSON booleans. Null is JSON null, used only where the field definition says nullable.
- The envelope below is required on EVERY row. A row missing any envelope field is malformed.

### Envelope (every row, required)

| Field | Type | Required | Meaning |
|---|---|---|---|
| schema | int | yes | Schema version. Value 1 for this design. Readers must reject or warn on any other value, never guess. |
| run | string | yes | run_id, formation below. Same value on every row of one main() invocation. |
| wall | string | yes | Wall clock, TimingLogger.wall_text format "%Y-%m-%d %H:%M:%S %Z", Asia/Ho_Chi_Minh. This deliberately matches timing.py, and deliberately differs from log_step ts, which is UTC ISO. Do not "fix" one to match the other. Record the difference here so a join between the metrics file and the log_step file uses run plus test plus step name, never wall vs ts. |
| elapsed_s | float | yes | Seconds from LiveMetrics t0 (time.monotonic at construction), rounded to 3 decimals. |
| event | string | yes | One of step, action, click_attempt, summary. No other value. |
| test | string or null | yes | Test id (t01, f03, q01, and so on) on step, action, and click_attempt rows. Null only on the summary row. The string "bootstrap" must never appear here: bootstrap and preflight setup are excluded from metrics (see Q4). |
| attempt | int or null | yes | Re-run attempt number in the Y9 sense. 1 on run_live, run_agyq, run_fcck, run_agyq2, and hand_drive. 1 or 2 on run_agy_y2, taken from the same source as its log_step attempt field. Null only on the summary row, which covers all attempts. |

### run_id formation

- LIVE_RUN_ID env var, when set and matching ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$, is used verbatim. When set but invalid, ignore it, print one "[metrics] invalid LIVE_RUN_ID, generated one instead" line to stderr, and generate. Never fail the run over a bad run id.
- Otherwise generated once, in main(), never in run_one(): f"{YYYYMMDD-HHMMSS}-{pid}-{token_hex_6}", where YYYYMMDD-HHMMSS is wall clock Asia/Ho_Chi_Minh at main() start, pid is the main process pid, token_hex_6 is 6 lowercase hex chars from secrets.token_hex(3). Example: 20261121-185240-4821-9f3c2a. Length 28 chars, inside the 64 char limit.
- Stable across a run's tests because it is created once in main() and passed down. Creating it in run_one would give one run_id per test and destroy the before/after comparison. This is a named amendment (A5).
- Two concurrent mains in the same second differ by pid; pid reuse plus same second plus same 6 hex chars is negligible and, if it ever happened, rows would still be separable by wall and elapsed_s. Do not add hostname or user info to the run id.

### step event

One row per Runner.step call, including failed steps. Written after log_step, never before it, never instead of it.

| Field | Type | Required | Meaning |
|---|---|---|---|
| step | string | yes | Runner.step name, verbatim. |
| op | string | yes | Runner.step op, verbatim (goto, type, click, click_js, wait, text, eval, select, and so on). |
| think_s | float or null | yes | Null when think_source is scripted. A number, rounded to 3 decimals, only when think_source is agent or hand. Never 0.0 as a placeholder for scripted steps: 0.0 would drag every think median to zero and lie about the headline metric. |
| act_s | float | yes | Step wall time in seconds, equal to Runner.step elapsed_ms / 1000, rounded to 3 decimals. For scripted steps this is the whole step: machine act time, the floor under any agent run, not agent think time. |
| total_s | float | yes | think_s + act_s when think_s is a number, else act_s. |
| actions | int | yes | Count of action rows emitted inside this step. Zero is allowed and honest (a wait step may emit no WD action rows, a check-only step emits none). |
| slow_think | bool | yes | True only when think_s is a number and think_s > 60.0 (SLOW_THINK_S). False whenever think_s is null. |
| think_source | string | yes | Enum: agent, scripted, hand. scripted for every Runner.step in run_live, run_agyq, run_fcck, run_agyq2, run_agy_y2. hand for hand_drive commands. agent only for a future real agent driver that measures its own decisions, never for scripted runs. |
| ok | bool | yes | Same value Runner.step computed. |
| error | string or null | yes | Null on ok. On failure, the same "TypeName: message" string Runner.step builds. No stack trace. |

### action event

One row per WD driver call that LiveMetrics is told about, when metrics is set. Written by the WD method, after the call returns or raises.

| Field | Type | Required | Meaning |
|---|---|---|---|
| kind | string | yes | WD method name: click, click_js, type, eval, goto, refresh, find, text, value, visible, wait_for, set_file, switch, new_tab, close_tab, alert_accept, alert_dismiss, alert_send, scroll_into_view. Only methods that actually ran. Never invent a kind. |
| step | string or null | yes, nullable | Enclosing Runner.step name when the call happens inside a step, else null. WD calls outside any step (bootstrap, tab cleanup, recheck) get null and do not count toward any step's actions. |
| op | string or null | yes, nullable | Enclosing step op, same rule as step. |
| detail | object | yes | Per-kind, JSON-safe, no free text. click: {"selector": css}. click_js: {"js": js_expr, "js_len": n}. type: {"selector": css, "text_len": n}, never the text. eval: {"script_len": n}. goto: {"url": url}. set_file: {"selector": css, "filename": basename}. find/text/value/visible: {"selector": css}. switch/new_tab/close_tab/alert_*: {} or {"handle_prefix": first 8 chars} where applicable, never a full handle. Empty object {} is allowed when there is nothing safe to record. |

Note: action rows are the raw material for step.actions and for the summary actions count. A step lambda that calls two type_text calls (run_agyq2 run_q01 "set coords" does four) emits four action rows and step.actions is 4. That is correct: the count is driver calls, not steps.

### click_attempt event

One row per WD.click call, when metrics is set. Never emitted for click_js. Never emitted for eval-driven clicks, select changes, or keyboard input.

| Field | Type | Required | Meaning |
|---|---|---|---|
| case_id | string | yes | Test id, same value as the envelope test field. Kept under the hit_rate.py name so the vocabulary matches, but see the attempt collision note below. |
| click_n | int | yes | 1-based click counter within this test within this run_attempt. Resets to 1 for each test and for each Y9 re-attempt. This is deliberately NOT named attempt: hit_rate.py uses attempt for the per-case attempt number, while the envelope attempt means the Y9 re-run attempt. Reusing one key for both meanings makes hit_rate.summarize raise on duplicate (case_id, attempt) and is the exact collision Amendment A3 removes. |
| backend | string | yes | Enum dom, desktop, a11y (hit_rate.BACKENDS). Live WD clicks are dom. desktop or a11y only if a future driver records them. Never invent a backend. |
| intended_target | string | yes | Slug of the intended element, matching ^[a-z0-9][a-z0-9_-]{0,63}$ (the hit_rate._SAFE_ID rule). Derived from the selector by slugify (below). |
| selector | string | yes | Raw CSS selector as passed to WD.click, verbatim. This is the debuggable value; intended_target is the comparable value. |
| point | object or null | yes | {"x": float, "y": float}, viewport CSS pixels of the intended element center from getBoundingClientRect at probe time, rounded to 1 decimal. Null when the element was not found or had no rect. |
| rect | object or null | yes, nullable | {"x": float, "y": float, "w": float, "h": float} from the same getBoundingClientRect call, rounded to 1 decimal. Null exactly when point is null. |
| actual_target | string or null | yes | Slug of the top element at point from document.elementFromPoint, derived the same way as intended_target (element id when present, else tag plus first class, else tag). Null when point is null or elementFromPoint returns null. |
| hit | bool | yes | True when hit_basis is contains or slug. False otherwise. |
| hit_basis | string | yes | Enum contains, slug, none. contains: the elementFromPoint element is the intended element or a descendant of it (checked in the probe eval with contains()). slug: slugs are equal but containment could not be proven. none: no hit (actual is a different element, or point/actual is null). A child span inside a button is a hit by contains, and that is correct: the click lands on the button. |
| issue_group | string or null | yes | Null on hit. On a miss, one of hit_rate.ISSUES, mapped as: actual is a different element, wrong_target; point outside the viewport or rect zero size, coordinate_mapping; the WebDriver click raised an interactability or timeout error, unresponsive; anything else, including element not found, unknown. Never invent a new issue value. |
| error | string or null | yes | Null when the click call succeeded. On exception, "TypeName: message" truncated to 300 chars, matching the WD._wd error truncation style. |

Slugify rule (must be implemented once in live_metrics.py and unit tested, never reimplemented per runner): lowercase the selector; strip a single leading "#" or "."; replace every run of [^a-z0-9_-] with one "-"; strip leading and trailing "-"; truncate to 63 chars; if the result is empty, use the tag name when known, else "el". Examples: "#btn-save-board" becomes "btn-save-board". "#rows tr:nth-child(2) a" becomes "rows-tr-nth-child-2-a". "button[onclick=\"clickCell('a2')\"]" becomes "button-onclick-clickcell-a2". The raw selector stays in selector, so slug collisions are debuggable and never silent.

Why WD.click can record a hit at all, and what it cannot prove: WD.click drives the element endpoint, not screen coordinates. The probe (rect center plus elementFromPoint, run after scroll_into_view and find, before the element click) asks whether the element the driver is about to click is actually the top element at its own center. That catches occlusion and wrong-element cases. It does not measure vision grounding: no vision estimate exists on this path, and a dom click that passes this probe says nothing about whether an agent looking at a screenshot would have aimed at the same point. The summary must disclose this (Q6). A dom hit rate near 100 percent is expected by construction and must never be quoted as agent click accuracy.

### summary event

Exactly one row per main() invocation, test null, attempt null, written last, in a finally block. If LiveMetrics is disabled (unwritable path), no summary row is written to the file; the in-memory summary is still available to main for a stderr line. Never write two summary rows. Never call TimingLogger.summary(), which would write its own.

| Field | Type | Required | Meaning |
|---|---|---|---|
| tests | array of string | yes | Test ids in run order. Empty array when zero tests ran. |
| tests_pass | int | yes | Count of tests whose Runner summary says pass, as reported by main, not recomputed from metrics. |
| tests_fail | int | yes | tests_total minus tests_pass. |
| tests_total | int | yes | Length of tests. |
| steps | int | yes | Total step rows. |
| steps_ok | int | yes | Step rows with ok true. |
| steps_fail | int | yes | Step rows with ok false. |
| think_median_s | float or null | yes | Median over steps with think_s not null only. Null when no step has a think_s number (every scripted run). Never 0.0 by default. |
| think_max_s | float or null | yes | Same population as think_median_s. Null when empty. |
| total_median_s | float | yes | Median total_s over all steps. Null is not allowed here; when steps is 0, use null and say so in the implementation, because a median over zero steps does not exist. Correction: when steps is 0, total_median_s and total_max_s are null. |
| total_max_s | float or null | yes | Same rule as total_median_s. |
| model_calls | int | yes | TimingLogger model_calls. 0 on every scripted run. Never faked upward by calling think_step. |
| actions | int | yes | Total action rows. |
| actions_per_call | float or null | yes | actions / model_calls when model_calls > 0, rounded to 3 decimals. Null when model_calls is 0. Never actions / 1. |
| slow_steps | int | yes | Count of steps with slow_think true. 0 on scripted runs. |
| slow_step_names | array of string | yes | Names of slow steps, in order. Empty array on scripted runs. |
| slow_think | bool | yes | True when slow_steps > 0. False otherwise. This is NOT TimingLogger.pace()["slow_think"], which is ratio < 1.0 and would be true on a scripted run with zero actions. Do not copy pace()["slow_think"] verbatim. |
| clicks | object | yes | {"attempts": int, "hits": int, "misses": int, "hit_rate": float or null, "by_backend": {"dom": {"attempts": int, "hits": int, "misses": int}}, "misses_by_issue": {"wrong_target": int, ...}}. Same shape as hit_rate.summarize output, computed by LiveMetrics from its in-memory click rows, not by calling hit_rate.summarize on the merged file. hit_rate is null when attempts is 0. by_backend includes only backends that actually appear. |
| js_clicks_excluded | int | yes | Count of click_js action rows. These clicks bypass hit testing entirely (el.click() fires regardless of visibility, occlusion, or coordinates) and are excluded from clicks.attempts, clicks.hits, and hit_rate. |
| js_clicks | array of object | yes | [{"test": string, "selector": string}] for every click_js call, in order. Empty array when none. This is the disclosure that stops a reader from mistaking a high dom hit rate for full coverage. |
| clicks_excluded_reason | string | yes | Constant text: "click_js calls .click() on the element directly and bypass hit testing, so they are counted here and excluded from hit rate." |
| think_source | string | yes | "scripted" for Runner runs. "hand" for hand_drive runs. "mixed" only if one file ever contains both, which the current runners never do. |
| think_disclaimer | string | yes | Constant text: "think_s is null: the scripted DOM driver has no model decisions; step wall time is machine act time, the floor under any agent run, not agent think time." |
| metrics_dropped | int | yes | Rows that failed to write after construction (0 normally). See Q5. |
| metrics_path | string | yes | Path of the metrics file, as resolved. |
| live_log | string | yes | Path of the log_step file (LOG_PATH effective value), so a reader can join the two files by run plus test plus step name. |
| tests_detail | array of object | yes | One object per test, in run order: {"test": string, "pass": bool, "steps": int, "steps_ok": int, "total_s": float, "over_small_task_budget": bool, "clicks_attempts": int, "clicks_hits": int, "hit_rate": float or null, "js_clicks_excluded": int}. over_small_task_budget is per test (elapsed test wall > 300 and steps <= 6, the TimingLogger rule applied per test, not per run). The run-level TimingLogger over_small_task_budget is meaningless across a multi-test run and must not appear at run level. |

## Q3. Backward compatibility: prove nothing changes when metrics is None

The design is additive only. The proof is per touch point in run_live.py, with exact behavior when metrics is unset. Y4d's in-flight modifications (diagnose_body, _DIAG_JS, _classify_snapshot, require_visible, _diagnose_or_raise, the goto/refresh choke points) are not touched at all.

| Touch point | Location | When metrics is None | When metrics is set |
|---|---|---|---|
| WD.__init__ | run_live.py:265 | Adds one attribute, self.metrics = None. No other change. No extra WebDriver call, no extra eval, no timing change. | WD gains an optional metrics attribute set by the caller. No behavior change in __init__ itself. |
| WD.click | run_live.py:507 | Exact current code: scroll_into_view, find, element click. Zero extra calls. The probe eval (rect plus elementFromPoint) runs only when metrics is set, so step timing is unchanged when metrics is off. | Probe eval runs after scroll and find, before the element click; click_attempt row written after the click returns or raises; any metrics exception is swallowed (see Q5) and the click result stands. |
| WD.click_js | run_live.py:512 | Exact current code: eval(f"({js_expr}).click()"). | Emits one action row (kind click_js) and no click_attempt row. The js click itself is unchanged. |
| WD other methods (type_text, eval, goto, find, text, value, visible, set_file, switch, new_tab, refresh, wait_for, alert_*) | run_live.py:382-557 | Exact current code. | Each emits one action row when metrics is set, after the call. No method changes its return value, its arguments, or its error behavior. |
| Runner.__init__ | run_live.py:560 | New signature Runner(test_id, base_url, metrics=None). Default None preserves every existing call site. Stores self.metrics. | Stores the passed LiveMetrics. |
| Runner.step | run_live.py:568 | Identical: time fn, call log_step, print the same line, append to failures and raise on failure. No metrics call of any kind. | Same as None, plus: metrics.start_step before fn, metrics.finish_step after log_step, both inside try/except that can never raise, never change ok, never change the print line, never change the raise. The step row is written after log_step so a metrics failure cannot reorder or suppress the log_step row. |
| Runner.check | run_live.py:584 | Unchanged. | Unchanged. Checks are not steps and never emit metrics rows. Do not invent step rows for checks. |
| Runner.summary | run_live.py:592 | Unchanged. | Unchanged. Metrics totals are not added to the RESULT dict. |
| log_step | run_live.py:69 | Unchanged: same record shape, same file, same order, same plain open(LOG_PATH, "a") write. | Unchanged. Metrics rows go to the metrics file only. The log_step stream is never read, parsed, or rewritten by LiveMetrics. |
| run_one | run_live.py:1408 | New signature run_one(test_id, base_url, metrics=None). Default None preserves the call. Runner created without metrics. | Passes metrics through to Runner. Does NOT create a LiveMetrics (that would give one run_id per test). Does NOT write a summary (that would give one summary per test). |
| main | run_live.py:1427 | Behavior identical, including usage error return 2 on bad args and the SUMMARY print line. | Creates one LiveMetrics after arg validation, passes it to each run_one, writes exactly one summary row in a finally block around the test loop. The SUMMARY stdout line is unchanged. |
| stdout RESULT lines | run_one print | Byte-identical. | Byte-identical. Metrics never prints to stdout. Metrics warnings go to stderr only. |

What the implementation must NEVER do:

- Never modify log_step, its record shape, its file, or its write order. Never add a metrics field to log_step rows.
- Never change a stdout RESULT line ("RESULT " + json) or the SUMMARY line, in shape or in content, whether metrics is on or off. Adding a metrics field to RESULT would break every existing parser that reads those lines.
- Never print metrics diagnostics to stdout. All metrics warnings go to stderr with a "[metrics] " prefix, so stdout stays parseable.
- Never call TimingLogger.think_step, note_model_call, or summary() on the Runner path. think_step would increment model_calls for every scripted step and fabricate think time; summary() would write a duplicate summary row.
- Never call hit_rate.append_attempt or hit_rate.summarize on the live path. append_attempt rejects live selectors and verifies the whole file per call; summarize raises on the (case_id, attempt) collision described in Q2.
- Never let a metrics exception propagate into Runner.step, WD.click, run_one, or main. Every metrics call site is wrapped, and a metrics failure is recorded as dropped rows, never as a test failure.
- Never add a WebDriver call, eval, sleep, or retry when metrics is None. The off path must be exactly the current path, including timing.
- Never rewrite Y4d's diagnose code, _DIAG_JS, or the goto/refresh choke points. The design is additive and must land on top of the working tree without touching those functions.

## Q4. How the four sibling runners adopt the hooks

Free via shared WD/Runner is only partly true. The WD.click probe and the Runner.step hook are free wherever the base classes are used unchanged. The run_id, the LiveMetrics construction, and the summary write are NOT free: each file owns its own main loop, and two of them own their own run_one. Exact change per file:

- run_agyq2.py: NOT free. It has no run_one. main (line 1501) creates Runner(tid, base) inline in the loop and manages WD() with manual __enter__/__exit__. Change: in main, after arg validation and after preflight plus bootstrap_tab succeed, create one LiveMetrics (run_id once) and pass metrics=metrics to each loop Runner(tid, base, metrics=metrics). Do NOT pass metrics to the bootstrap Runner("bootstrap", base) (line 1301): bootstrap is setup, excluded from metrics, and its steps must not pollute step medians. Do NOT create LiveMetrics before bootstrap: if bootstrap fails, main returns 2 with no metrics file and no summary row, which is honest (no run happened). Write the summary in a finally-equivalent path before every return from the test loop (handover abort, infra abort, normal end). Its _log_diag and ensure_visible call log_step directly and need no change. Its open_fixture uses r.step, so its steps are covered by the Runner hook with no further change.
- run_agy_y2.py: NOT free, and the most work. It has its own log_step with attempt, its own Y9WD, and its own Y9Runner.step override. Change: (a) Y9WD inherits the WD.click probe and action rows for free, including its click_el and type_in helpers only if those helpers are also instrumented in live_metrics-aware WD methods; click_el and type_in call self._wd directly, so they bypass WD.click and WD.type_text and emit no action or click_attempt rows unless Y11 instruments them explicitly. Name them in the implementation: either route click_el through the same probe as click, or record click_el as excluded like click_js with a summary disclosure. Do not leave them silent and uncounted. (b) Y9Runner.step (line 305) overrides base Runner.step entirely and calls the module-local log_step, so a hook added only to base Runner.step is bypassed. Change: duplicate the same metrics.start_step and metrics.finish_step calls inside Y9Runner.step, and add metrics=None to Y9Runner.__init__ with self.attempt preserved. Do NOT refactor Y9Runner.step to call super().step: that would switch its log line to run_live.log_step and lose the attempt field. (c) main (line 2265) rotates LOG_PATH at launch and retries infra-blocked tests (attempt 1, then 2, via _CURRENT_ATTEMPT). Change: create one LiveMetrics after preflight plus bootstrap_tab succeed; set metrics attempt from _CURRENT_ATTEMPT before each attempt (metrics.set_attempt(n)); pass metrics to each Y9Runner. The metrics file is NOT rotated by the LOG_PATH rotation code. If the operator wants a fresh metrics file, they set a new LIVE_METRICS path or delete the file; LiveMetrics appends and run_id separates runs. (d) Y9Runner.gap() records fixture gaps via log_step with op gap-probe. No metrics row for gaps. A gap is not a step and not an action.
- run_agyq.py: HALF free. WD and base Runner hooks are free (it uses both unchanged). Its own run_one (line 692) and main (line 706) are local copies, so they need the same two-line change as run_live: run_one gains metrics=None and passes it to Runner; main creates one LiveMetrics after arg validation and writes one summary in a finally block. No test function changes.
- run_fcck.py: HALF free, same as run_agyq. Own run_one (line 829) and main (line 843) need the identical change. No test function changes.
- hand_drive.py: NOT free at all, and the proposed "--metrics flag" is underspecified as written. It imports neither WD nor Runner and has no test id, no run id, and no step concept. See Amendment A7 for the exact flag set and semantics. Do not bolt a --metrics boolean onto hand_drive and call it done.

No test function (run_t01, run_q01, and so on) changes in any file. No fixture changes. No change to start_server, _recheck_shared_tab (it reuses the passed Runner), or tab cleanup (WD calls outside a step get step null).

## Q5. Env vars, defaults, and metrics failure

- LIVE_METRICS: path to the metrics file. Default: derived from the effective LIVE_LOG value at runtime: replace a trailing ".jsonl" with "-metrics.jsonl" in the same directory, else append "-metrics.jsonl". Examples: /tmp/worker-p-live.jsonl becomes /tmp/worker-p-live-metrics.jsonl; /tmp/worker-y4-live.jsonl becomes /tmp/worker-y4-live-metrics.jsonl. Derive from the effective value, never hardcode /tmp/worker-p-live-metrics.jsonl, because each sibling runner sets its own LIVE_LOG. If LIVE_METRICS is set to the exact string "off", metrics is disabled entirely: no file, no LiveMetrics construction, no overhead, behavior identical to metrics None. If LIVE_METRICS is empty or unset, use the default. Any other value is a path.
- LIVE_RUN_ID: formation in Q2. Validated against ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$. Invalid values are ignored with one stderr warning, never fatal.
- LIVE_LOG: unchanged, still controls the log_step file. No new semantics.
- Unwritable metrics path at construction: LiveMetrics.__init__ must NOT raise. It sets self.disabled True, self.error to the exception string, prints one "[metrics] disabled: <reason>" line to stderr, and returns a degraded object whose record methods are no-ops. main continues exactly as if metrics were None. No metrics file is created, no summary row is written to a file, and the run is not failed. The disabled reason is available in memory for main to print once more to stderr at the end if it wishes, but must never be added to RESULT or SUMMARY stdout lines.
- Unwritable or failing metrics path mid-run (disk full, permission change, parent deleted): the first failing write disables further writes, increments metrics_dropped for every row that fails after that (including the summary write attempt, tried once), prints one "[metrics] write failed, metrics disabled for the rest of this run: <reason>" line to stderr, and never raises. No retry per row (retrying a dead disk on every click would slow the run and spam the log). No test ever fails because metrics failed. This is a hard rule, not a preference: metrics is evidence, and evidence must never become the verdict.
- Append-only: LiveMetrics never truncates, never rotates, never deletes the metrics file. A previous run's rows stay, separated by run_id. The only writer is append_jsonl.
- Concurrency: the runner is strictly single-session and sequential (run_live.py WD.__init__ comment). Two mains writing the same metrics path concurrently are out of scope and must be avoided by giving each run its own LIVE_METRICS path or its own LIVE_RUN_ID. If two processes ever share a path, append_jsonl per-row appends usually do not interleave mid-line for small rows, but that is not guaranteed and is not a supported configuration. Document it, do not engineer for it.

## Q6. What belongs in the summary so a reader can judge a run without opening another file

The summary fields are specified exactly in Q2. The reasoning behind the required disclosures:

- tests_detail per test (pass, steps, total_s, per-test budget flag, per-test clicks and hit rate, per-test js exclusions) is what makes the summary self-contained. Run-level medians alone hide a single slow or broken test.
- think_median_s and think_max_s are null on scripted runs, with think_disclaimer stating why. A scripted run has no think time to report, and reporting 0.0 would be the exact fabrication H2 warns about: a headline number that looks measured and is not.
- actions_per_call is null when model_calls is 0. The TimingLogger pace() default (calls or 1) would report actions_per_call equal to actions, which is meaningless without model calls. Null is honest.
- clicks uses the hit_rate.summarize shape (attempts, hits, misses, hit_rate, by_backend, misses_by_issue) so a reader can compare it directly with calibration numbers, but it is computed by LiveMetrics from in-memory rows, never by calling summarize on the merged file.
- js-click exclusions are disclosed twice, as a count and as a list of {test, selector}. The list matters because a run with 40 dom clicks at 100 percent hit rate and 12 js clicks is a different claim from a run with 52 dom clicks at 100 percent. run_live.py alone has js clicks in f01 (TRAP click), f03 (slot click), f04 (source cards), f05 (move file); run_agyq.py and run_fcck.py have more. Without the list, the exclusion is invisible.
- think_source=scripted is disclosed as a field, not buried in prose, so any script that reads the summary can branch on it.
- metrics_dropped, metrics_path, and live_log let a reader know whether the summary is complete and where the two files live for a join.
- What does NOT belong in the summary: pass/fail recomputed from metrics (pass/fail comes from Runner summaries as reported by main), any per-click detail (that lives in click_attempt rows), typed text, file contents, or a second copy of the TimingLogger summary shape. One summary row, one shape, last row in the file.

## Amendments (exact, in implementation order)

- A1, single writer (load-bearing): LiveMetrics is the sole writer to the metrics file. Every row goes through jsonlutil.append_jsonl. TimingLogger is used as an in-memory calculator only: subclass it inside live_metrics.py as _CalcLogger with _write overridden to append to an in-memory list and never touch the file. LiveMetrics calls logger.note_action (public) for actions and logger._finish_step (private, documented in a code comment as intentional, pinned by a unit test) for steps, and calls logger.pace() for counts. It never calls logger.think_step (fabricates model calls and think time), never calls logger.note_model_call on the scripted path, and never calls logger.summary() (writes a duplicate summary row). hit_rate.append_attempt and hit_rate.summarize are never called on the live path. Calibration workflows (calibration_e2.py, tests/calibration-e2-hits.jsonl) are untouched and keep using append_attempt on their own hits-only files.
- A2, no append_attempt on live clicks: LiveMetrics writes click_attempt rows directly via append_jsonl, using the Q2 schema. It does not route through hit_rate.append_attempt, which rejects live selectors ("#btn-save-board", "button[onclick=...]") under _SAFE_ID. Slugify is implemented once in live_metrics.py per the Q2 rule, unit tested with the examples in Q2, and the raw selector is always kept in selector.
- A3, fix the attempt collision: envelope attempt means the Y9 re-run attempt (1, or 1-2 on run_agy_y2). Per-test click numbering uses the new field click_n, never attempt. LiveMetrics computes the clicks summary itself from in-memory rows in the hit_rate.summarize shape. hit_rate.summarize is not called on the merged file: it would raise on duplicate (case_id, attempt) and it expects a clicks-only file.
- A4, scripted think semantics: Runner steps are recorded with think_s null, think_source scripted, act_s equal to step wall time, total_s equal to act_s, slow_think false. model_calls stays 0. actions_per_call, think_median_s, and think_max_s are null on scripted runs. The summary carries think_disclaimer verbatim. Any future agent driver that measures real decisions uses think_source agent and real think_s; it must not reuse the scripted path.
- A5, run_id created once in main: each main() creates the run_id (from LIVE_RUN_ID or generated per Q2) once, after arg validation, and passes the LiveMetrics object down. run_one never creates a LiveMetrics and never generates a run_id. run_agyq2 and run_agy_y2 create it after preflight plus bootstrap succeed. The summary is written once, in a finally block, test null, attempt null.
- A6, WD.click probe contract: when metrics is set, WD.click runs one probe eval after scroll_into_view and find and before the element click: getBoundingClientRect of document.querySelector(selector) (same first-match semantics as find) plus document.elementFromPoint at the rect center, returning rect, center point, top element identity, and a contains() check against the intended element. The click_attempt row is written after the click returns or raises. When metrics is None, WD.click runs zero extra calls. WD.click_js emits only an action row, never a click_attempt row. Y9WD.click_el and Y9WD.type_in are named in the implementation: either route click_el through the same probe as click, or record it as excluded with a summary disclosure in the same style as js_clicks_excluded. Silent and uncounted is not allowed.
- A7, hand_drive needs more than a flag: --metrics alone is insufficient. Add --metrics-path (default from LIVE_METRICS env, else /tmp/hand-drive-metrics.jsonl), --test (default "hand"), --run-id (default from LIVE_RUN_ID env, else generated per Q2). Metrics is created at startup, not on new_session. Think time per command is the gap between the previous command's completion and the next stdin line's arrival (think_s, think_source hand); the first command has think_s null. act_s is the command execution ms. quit and delete_session write the summary row; an EOF on stdin also writes it. Click commands record click_attempt rows by the same probe rule as A6; click_js commands are excluded and disclosed the same way. If any of --test or --run-id is missing, hand_drive must not invent them silently: defaults above apply and are printed once to stderr at startup.
- A8, Y9 adoption: Y9Runner.__init__ gains metrics=None; Y9Runner.step duplicates the metrics.start_step and metrics.finish_step calls (it must not delegate to super().step, which would lose the attempt field); main sets metrics.set_attempt(n) from _CURRENT_ATTEMPT before each attempt and passes metrics to each Y9Runner; the metrics file is not rotated by the LOG_PATH rotation. Y9Runner.gap() emits no metrics row.
- A9, failure discipline: every metrics call site is wrapped so a metrics exception can never propagate, never change ok, never change a print line, never change a raise. Construction failure degrades to disabled with one stderr line. First mid-run write failure disables further writes with one stderr line and counts dropped rows. Metrics warnings go to stderr only, prefixed "[metrics] ".
- A10, defaults and off switch: LIVE_METRICS default derived from effective LIVE_LOG per Q5; exact string "off" disables metrics entirely. LIVE_RUN_ID validated per Q2. No other new env vars. Document both in the live_metrics.py module docstring and in the run_live.py usage text.
- A11, unit tests in tests/test_live_metrics.py, following tests/test_timing.py conventions (sys.path insert of scripts/, FakeClock, tmp dirs, unittest): single-writer file parses clean with verify_jsonl == [] after mixed step plus action plus click_attempt writes; exactly one summary row per LiveMetrics lifetime; selector "#btn-save-board" accepted via slugify while hit_rate.append_attempt rejects it (assert the rejection, do not work around it); scripted step rows have think_s None and think_source scripted; metrics=None Runner writes no metrics file and its log_step rows are byte-identical to the no-metrics run; unwritable path degrades to disabled without raising (parent is a file, not a directory); two LiveMetrics have different run_ids; summary hit math matches hand-computed attempts/hits/misses and js clicks are excluded from hit_rate but listed; envelope fields present on every row; torn-tail repair (file ending without "\n" before a LiveMetrics write parses clean afterwards).
- A12, live proof: after the unit tests pass, a live proof run of 2-3 tests (t01 plus one click-heavy test) on the laptop, after the current live-slot holder clears (the slot passed to Y8 for E1 A/B; do not run in parallel with another live runner, the Marionette session slot is single). Proof acceptance: metrics file parses with verify_jsonl == [], exactly one summary row, step rows match log_step rows one-to-one by test plus step name, click_attempt count equals WD.click call count in those tests, js clicks appear only in js_clicks, and the run's RESULT and SUMMARY stdout lines are identical to a metrics-off run of the same tests.

## What the proposal got right (keep)

- One file, not two. Correct, for the reasons in Q1.
- A new module scripts/live_metrics.py wrapping existing instruments, with timing.py and hit_rate.py unmodified. Correct, with Amendment A1 making the wrapping real instead of nominal.
- WD gets an optional metrics attribute defaulting to None, Runner gains metrics=None, run_id unique per run. Correct, with Amendment A5 fixing where the run_id is created.
- Unit tests in tests/test_live_metrics.py following existing conventions. Correct, with Amendment A11 naming the cases that pin the tricky parts.
- Live proof run of 2-3 tests after the live slot. Correct, with Amendment A12 adding the acceptance checks and the no-parallel-runner condition.

## Open questions for Y11 (not blockers, answer in the implementation)

- Should WD.type_text and WD.set_file probe anything, or only emit action rows? Council view: action rows only. Typing has no hit/miss concept on this path, and probing it would add evals with no decision attached.
- Should the probe eval run before or after scroll_into_view? Council view: after scroll, before click, as in A6. Before scroll the rect is the pre-scroll position and elementFromPoint answers the wrong question.
- Should LiveMetrics record Runner.check results anywhere? Council view: no. Checks are assertions about end state, not steps. If a future design wants check coverage in metrics, that is a separate schema version, not a silent addition to schema 1.
