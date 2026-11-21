# Worker Y11 design: live metrics in the realistic harness (FROZEN)

- Owner: Worker Y11. Date: 2026-11-21. Status: FROZEN after council + redteam.
- Verdicts: C1 AMEND (improvements/worker-y11-council-1-think-time.md), C2 AMEND (improvements/worker-y11-council-2-hit-rate.md), C3 AMEND (improvements/worker-y11-council-3-integration-schema.md), redteam BLOCK (improvements/worker-y11-redteam.md).
- The redteam BLOCK is lifted by this document: all 8 cheapest fixes (B1-B8) are landed here before implementation. Nothing in this design is implemented as originally proposed; every change below is traceable to a verdict.

## Work log (wall-clock Asia/Ho_Chi_Minh)

- 18:50:40 task received. 18:52:40 council + redteam spawned (4 agents). 18:55 C1 done, 18:54 C2 done, 18:55 redteam done, 18:56 C3 done. Synthesis written after all four verdicts were read in full.

## 0. What this closes, and what it does NOT close

- CLOSES the wiring gap: after this lands, every live run through run_live.py (and hand_drive.py in metrics mode) emits timed JSONL with per-step think/act/wait/exec and per-click records next to the pass/fail record.
- PARTIALLY closes I8: the selector-delivery rate (pointer-occlusion/intercept on selector-resolved clicks) is now measured live. The vision-grounding hit rate is NOT measured by this harness and stays open; it lives only in calibration (E2, 58.6 percent). The summary says so in plain words.
- Does NOT close H2: scripted runs carry no think measurement (think_s null). H2 stays OPEN until a real agent-driven run (hand-drive with an agent operator, or a future agent runner) produces agent-source think rows. This design makes that measurement possible; it does not fake it.

## 1. Names: two rates, never one

- `selector_delivery_rate`: pointer-occlusion and intercept rate for selector-resolved DOM clicks. This is what WD.click measures. A value near 100 percent is expected by construction and must never be quoted as agent click accuracy.
- `hit_rate` (vision): clicks where the point came from agent vision coordinates and was executed through a real pointer. NOT measured by this harness. Reserved name; the summary states vision grounding is not measured here.
- The clicks object keeps the hit_rate.summarize shape (attempts, hits, misses, hit_rate, by_backend, misses_by_issue) for comparability, but the summary carries a `clicks_disclaimer` constant stating the selector-delivery scope. Never merge live selector numbers with calibration vision numbers in one output (C2 A9).

## 2. Think time: null, never zero (C1, redteam B2)

- Scripted steps: think_s = null, think_source = "scripted", act_s = step wall time, total_s = act_s, slow_think = false. Never 0.0. Summary think medians are null on scripted runs, with think_disclaimer verbatim (C3 Q2).
- model_calls stays 0 on scripted runs. actions_per_call is null when model_calls is 0. Never actions / 1.
- TimingLogger.think_step is NEVER called on the scripted path: its __enter__ auto-calls note_model_call(), which would invent one model call per step (C1 Q4). LiveMetrics implements the think/act split itself; TimingLogger is not used in the live path at all. Deviation from C3 A1 recorded: C3 proposed subclassing TimingLogger as an in-memory calculator; that couples the live path to TimingLogger's private _finish_step and to the auto-count trap. The arithmetic LiveMetrics needs (medians, counts) is small and is implemented directly. The single-writer rule (the load-bearing part of A1) is preserved in full.
- pace()["slow_think"] is never copied: it means ratio < 1.0, colliding with the per-step flag. Our summary uses `low_pace` for the ratio flag (C1 A5, redteam N2) and `slow_think` only as slow_steps > 0.
- act() is called by the issuer of the first action: WD action methods mark exec start as the fallback; agent loops call it explicitly when they issue their first action after a model call. Runner.step never calls act() (C1 A3).
- hand_drive: per-command inter_command_gap_s (t_arrive minus t_print of the previous result) is an UPPER BOUND, never think_s (C1 A4, redteam B7). Real think_s requires a driver self-reported decided_at (epoch float) in the JSON command; think_s = decided_at minus t_print. First command gap is null. Operator kind (human/agent) is logged per session; a human-typed session has zero model calls.
- SLOW_THINK is suppressed when think_s is null (C1 A5).
- Step op kinds are tagged (op field); wait/poll/download steps are excluded from think aggregates when agent-source rows exist (C1 A7). Medians use statistics.median, not sorted[mid] (redteam N1).
- H2 stays OPEN until agent-source think rows exist (C1 A6).

## 3. Hit oracle: pre-click probe, exact match first (C2, redteam B4)

- The probe runs BEFORE the click, in the same eval that resolves the rect, after scroll_into_view and find (C2 A2, C3 A6). There is no post-click elementFromPoint read: on navigation clicks it reads a different document, on destructive clicks it manufactures false misses.
- Probe returns, in one eval: rect, center point, top element identity, and the relation of the top element to the intended element: exact (top is the intended element), contains (top is a descendant), ancestor, other. Plus a clickable-descendant flag: whether any element on the path from the top element up to (excluding) the intended element is natively clickable (tag a/button/input/select/textarea/label, or has an onclick attribute, or role button/link).
- Hit rules:
  - exact = hit.
  - contains with NO clickable element on the path = hit (a click on a child span bubbles to the intended handler; cdp.mjs precedent). The row records hit_basis "contains".
  - contains WITH a clickable element on the path = miss, wrong_target (a nested delete button at a card center deletes instead of opening; redteam B4 scenario B). This resolves C2 descendant=hit vs redteam exact-match default: both are honored, split by whether the descendant would intercept.
  - ancestor = miss, wrong_target (events bubble up, never down; C2 Q2).
  - other (unrelated covering element) = miss, occlusion.
  - intended element itself has pointer-events none = miss, wrong_target, never occlusion (C2 Q2).
  - point outside viewport or zero-size rect = miss, coordinate_mapping.
  - elementFromPoint returns null = miss, unknown, with rect in the row.
  - WebDriver click raises (intercept, not interactable, stale) = miss, unresponsive, logged on the exception path BEFORE re-raising (C2 A3). If the probe already said covered, the probe's issue wins; a probe hit plus a click raise is unresponsive.
- Iframe / shadow DOM: no recursion is needed and none is implemented. Intended elements are always top-document: document.querySelector cannot reach inside an iframe or a shadow root, so an intended element can never live there. A covering iframe or shadow host at the point is correctly an occlusion miss by the rules above. Recorded here so a reader does not mistake this for an oversight (deviation from C2 A5 documented with reasons).
- Movement between probe and click is a known blind spot; it is covered by the step's own end-state checks, not by elementFromPoint (C2 Q3).
- click_js emits an action row only, never a click_attempt row. Raw eval calls whose script contains ".click(" are counted as eval_click actions (substring heuristic, documented as such). Both are excluded from the selector-delivery denominator and disclosed (section 5).
- type_text gets a post-type value read-back as a separate event type type_attempt (hit = read-back value equals typed text; null when the read-back is unavailable, e.g. contenteditable). It is input fidelity, not click hit, and never enters the click denominator (C2 Q5).

## 4. IDs: element identity, one namespace (C2 A8, redteam B8)

- intended_target and actual_target come from the SAME namespace: the resolved element's identity, never the selector. Prefer the element's id attribute when present, else a deterministic DOM path (tag plus nth-of-type chain from the nearest id ancestor or body).
- Slugify (implemented once in live_metrics.py, unit tested): lowercase, replace every run of [^a-z0-9_-] with one "-", strip leading/trailing "-", truncate to 63 chars. Per-run collision registry: on collision append a 6-hex sha1 suffix of the full source string and re-check. Never a bare class slug (two buttons sharing a class would manufacture false hits).
- The raw selector is kept in the selector field. The raw DOM path is kept in the row so misses are auditable.
- Click numbering uses click_n (1-based per test per run attempt). The envelope attempt field means the Y9 re-run attempt only (C3 A3). hit_rate.append_attempt and hit_rate.summarize are never called on the live path (C3 A1): append_attempt rejects live selectors and summarize raises on the (case_id, attempt) collision.

## 5. Reporting: shares printed together, UNRELIABLE flag (C2 Q4, redteam B3)

- Every summary prints together: selector-delivery rate (dom clicks only), js-click count and share, eval-click count and share, type-action count. A pointer rate printed alone is a misleading number.
- UNRELIABLE flag: js + eval share above 10 percent of all click actions, OR any DOM-to-JS retry in the run (a click_js or eval_click in a step that already has a failed DOM click attempt). Redteam's 10 percent is adopted over C2's 25 percent because it is stricter and covers eval clicks; the shares are always printed, so the 25 percent grounding-representativeness line is subsumed.
- Retry masking is closed by logging on the exception path (section 3): a failed DOM attempt exists in the file even when the step later retries through JS and succeeds.
- Summary disclosure sentence (constant): "Click hit rate covers N pointer clicks only. It excludes M js-clicks and K eval-clicks and L type actions. It is not an overall action success rate."

## 6. Timing buckets: think, wait, exec (redteam B5)

- Step rows carry think_s, wait_s, exec_s, act_s, total_s. act_s is the whole step wall time. wait_s is time inside wait/poll/settle/diagnose (WD.wait_for, WD.wait_ready, goto/refresh/new_tab/switch settle sleeps, diagnose_body). exec_s is time inside outermost WD action methods (click, click_js, type_text, set_file, eval, find, text, value, visible, scroll_into_view, alert_*), with a reentrancy guard so nested calls (click calling scroll_into_view and find) count once.
- think_s is null on scripted steps; wait_s + exec_s <= act_s, the remainder is harness overhead (log_step, prints, lambda overhead), unaccounted by design. Lambda-direct time.sleep calls in test code are unaccounted; the design recommends routing waits through WD.wait_for.
- This pins the attribution: the same seconds cannot be quoted as either think or act depending on an unpinned call site.

## 7. File: one writer, fail-open, loud off (C3 A1/A9, redteam B6)

- One file per run (C3 Q1). LiveMetrics is the SOLE writer; every row goes through jsonlutil.append_jsonl. TimingLogger and hit_rate.py never open the file.
- At construction LiveMetrics verifies the tail: if the file exists and its last line does not parse, the torn tail is quarantined (moved to <path>.torn-<run_id>, file truncated to the last good newline) and one stderr line is printed. append_jsonl's repair (prepend a newline) is NOT relied on: it preserves a corrupt line as its own bad line.
- run_id: generated once in main(), never in run_one(): f"{YYYYMMDD-HHMMSS}-{pid}-{token_hex_6}" (wall Asia/Ho_Chi_Minh at main start, pid, 6 lowercase hex chars). LIVE_RUN_ID env, when set and valid (^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$), is used verbatim; invalid values are ignored with one stderr warning. Deviation from redteam B6 recorded: no exclusive-create path and no uuid4; the metrics file is the append sibling of a rotating LIVE_LOG and operators expect one file per log, with run_id separating runs. Concurrent mains sharing one path are unsupported and must be avoided by giving each run its own LIVE_METRICS path.
- Metrics is ON by default: LIVE_METRICS defaults to the effective LIVE_LOG value with trailing ".jsonl" replaced by "-metrics.jsonl" in the same directory. Exact string "off" disables it entirely. Deviation from C3's verdict header ("off by default") recorded: A10's operative rule is the derived default, and silent-off is the exact H2/G22 failure this task fixes. When disabled, main prints one "[metrics] OFF (LIVE_METRICS=off)" line to stderr.
- Every metrics call site is wrapped: a metrics exception never propagates, never changes ok, never changes a print line, never changes a raise. Construction failure degrades to disabled with one stderr line. First mid-run write failure disables further writes, counts dropped rows, prints one stderr line. Summary write is fsync'd. A summary row with metrics_dropped > 0 marks the run UNMEASURED in the summary.
- Metrics warnings go to stderr only, prefixed "[metrics] ". Nothing metrics-related goes to stdout.

## 8. Schema (schema 1; C3 Q2 with the amendments above)

- Envelope on EVERY row: schema (int, 1), run (string), wall (string, "%Y-%m-%d %H:%M:%S %Z", Asia/Ho_Chi_Minh, matching timing.py; elapsed_s is the precise clock, wall is human-readable only; redteam N3 accepted), elapsed_s (float, seconds from LiveMetrics t0 via time.monotonic, 3 decimals), event (step, action, click_attempt, type_attempt, summary), test (string or null; null only on summary), attempt (int or null; Y9 re-run attempt; null only on summary).
- step: step, op, think_s (float or null), think_source (agent, scripted, hand), act_s, wait_s, exec_s, total_s, actions (int), slow_think (bool; false when think_s is null), ok, error (string or null).
- action: kind (WD method name), step (string or null; null outside any step), op (string or null), detail (object, JSON-safe, no free text: click {selector}, click_js {js, js_len}, type {selector, text_len}, eval {script_len, has_click}, goto {url}, set_file {selector, filename}, find/text/value/visible {selector}, others {} or {handle_prefix}).
- click_attempt: case_id (= test), click_n, backend (dom), intended_target (slug), selector, point ({x, y} or null), rect ({x, y, w, h} or null), dom_path (string, intended element identity source), actual_target (slug or null), actual_dom_path (string or null), hit (bool), hit_basis (exact, contains, none), issue_group (null on hit, else one of hit_rate.ISSUES), click_method ("dom"), error (string or null, truncated to 300 chars).
- type_attempt: case_id, type_n, selector, expected_len, readback_len (int or null), hit (bool or null), error (string or null).
- summary: exactly one row per main() invocation, test null, attempt null, written last in a finally block. Fields: tests, tests_pass, tests_fail, tests_total, steps, steps_ok, steps_fail, think_median_s (null on scripted runs), think_max_s, total_median_s (null when steps is 0), total_max_s, model_calls, actions, actions_per_call (null when model_calls is 0), low_pace (bool; ratio < 1.0; null when model_calls is 0), slow_steps, slow_step_names, slow_think (slow_steps > 0), clicks {attempts, hits, misses, hit_rate (null when 0), by_backend, misses_by_issue}, js_clicks_excluded (int), js_clicks [{test, selector}], eval_clicks_excluded (int), eval_clicks [{test, script_len}], dom_to_js_retry (bool), unreliable (bool), unreliable_reason (string or null), type_attempts {attempts, hits, misses, unknown}, think_source, think_disclaimer (constant), clicks_disclaimer (constant), metrics_dropped, metrics_path, live_log, tests_detail [{test, pass, steps, steps_ok, total_s, over_small_task_budget, clicks_attempts, clicks_hits, hit_rate, js_clicks_excluded}].
- think_disclaimer constant: "think_s is null: the scripted DOM driver has no model decisions; step wall time is machine act time, the floor under any agent run, not agent think time."
- clicks_disclaimer constant: "Selector-delivery rate for DOM-selector clicks (pointer occlusion and intercept). Vision grounding error is not measured by this oracle; see calibration E2 for the vision hit rate."

## 9. Integration points (run_live.py + hand_drive.py only, this task)

- run_live.py: WD gains optional metrics attribute (default None); WD.click runs the probe eval after scroll_into_view and find, before the element click, and writes the click_attempt row after the click returns or raises; WD.click_js emits an action row only; all other WD methods emit one action row when metrics is set; Runner gains metrics=None; Runner.step calls metrics.begin_step/finish_step guarded so they can never raise or change behavior; run_one gains metrics=None and never creates a LiveMetrics; main creates one LiveMetrics after arg validation and writes one summary in a finally block. No test function changes. No change to log_step, RESULT lines, SUMMARY lines, or Y4d's diagnose code (NEVER list, C3 Q3).
- hand_drive.py: flags --metrics-path (default from LIVE_METRICS env, else /tmp/hand-drive-metrics.jsonl), --test (default "hand"), --run-id (default LIVE_RUN_ID else generated), --operator (agent/human, default human). Metrics created at startup. One step row per command (think_s from decided_at when self-reported, else null; think_source hand; act_s = execution ms; inter_command_gap_s recorded per command, first null). Click commands run the same probe rule as WD.click; click_js excluded and disclosed. quit, delete_session, and stdin EOF all write the summary row.
- Sibling runners (run_agyq2.py, run_agy_y2.py, run_agyq.py, run_fcck.py) are NOT wired in this task: their mains are owned by in-flight work (Y8 E1, Y9 agy-y2) and their adoption needs main-loop changes (C3 Q4, A8) that would collide. The base WD/Runner hooks are in place, so adoption is a small main-only change afterwards. Recorded as follow-up, not skipped silently.
- Y9WD.click_el and Y9WD.type_in bypass WD.click/WD.type_text and are named here for the follow-up: route click_el through the same probe or record it as excluded with a summary disclosure. Silent and uncounted is not allowed (C3 A6).

## 10. Unit tests (tests/test_live_metrics.py)

- Single-writer file parses clean (verify_jsonl == []) after mixed step/action/click_attempt/type_attempt writes; exactly one summary row per LiveMetrics lifetime.
- Slugify examples from C3 Q2 and C2 Q6, including "#btn-save-board" accepted via slugify while hit_rate.append_attempt rejects it (assert the rejection).
- Scripted step rows have think_s None and think_source scripted; think medians null; actions_per_call null when model_calls is 0.
- metrics=None Runner writes no metrics file and its log_step rows are byte-identical to a no-metrics run.
- Unwritable path degrades to disabled without raising; torn-tail quarantine repairs a file ending without "\n" to parse clean.
- Two LiveMetrics have different run_ids; run_id formation matches the spec.
- Summary hit math matches hand-computed attempts/hits/misses; js/eval clicks excluded from hit_rate but listed; UNRELIABLE flag fires above 10 percent and on a DOM-to-JS retry; dom_to_js_retry detection works.
- Hit classification: exact hit, inert-descendant hit (contains), clickable-descendant miss (wrong_target), ancestor miss, occlusion miss, pointer-events-none miss (wrong_target), null elementFromPoint miss (unknown); exception-path miss logging; wait/exec buckets accumulate and sum within act_s.
- Envelope fields present on every row; schema is 1.

## 11. Live proof (after Y9 clears the slot; no parallel runner)

- Tests t01 + f01 (click-heavy) via run_live.py with metrics on, on the laptop.
- Acceptance (C3 A12): metrics file parses with verify_jsonl == []; exactly one summary row; step rows match log_step rows one-to-one by test plus step name; click_attempt count equals WD.click call count in those tests; js clicks appear only in js_clicks; RESULT and SUMMARY stdout lines identical to a metrics-off run of the same tests; wait_s + exec_s <= act_s on every step row.
- The proof run is scripted, so its summary carries think_s null and H2 stays OPEN. The proof closes the wiring gap, not H2.
