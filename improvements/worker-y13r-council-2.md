# Council 2 re-review: Y13 fixed runner diff (cb26d1d), scope F9, F10, F11, H4, M6

- Commit under review: `cb26d1d` ("Y13: adjudicate Council A + redteam re-review (BLOCK -> fixed); launcher + manifest regen")
- Parent (last reviewed state): `bd89b62`
- Scope: Council A F9, F10, F11 + redteam H4, M6 + the plan amendment (redteam M5 / Council A F11)
- Reviewer: Council 2 of Worker Y13r, independent re-review, changed lines only
- Method: all line numbers refer to the exact `cb26d1d` bytes, extracted with `git show cb26d1d:tests/realistic/run_codex_y5.py` into `/tmp/y13r/run_cb26d1d.py`, because the working tree HEAD (`b8a2ff6`) already carries later Y8b changes on top. No code or test file was modified. No live driving was done. All checks below were run mechanically and timed.
- Verdict scale per finding: FIXED, PARTIAL, NOT FIXED
- Overall verdict: AMEND (exact fixes listed at the end; no BLOCK-level hole found)

## Timing log (wall-clock Asia/Ho_Chi_Minh)

- 20:20:02 +07, +0.0s: review started, repo on branch `todolist-push`, `git show --stat cb26d1d` confirmed 8 files changed
- 20:20:02 to 20:22:54 +07, about 2.9 min: read the full diff hunks for `run_codex_y5.py` (289 insertions, 39 deletions), the plan diff (22 lines), Council A F9/F10/F11, redteam H4/M5/M6, Y13 adjudication log lines 138-208, and `diagnose_body` in the frozen base `run_live.py` at `1e3901c`
- 20:22:54 +07, +0.1s: replication harness imported the exact `cb26d1d` runner bytes (stubbed `run_live`, frozen base out of scope)
- 20:22:54 to 20:23:02 +07, 8.1s: F9 fake-driver replication (7 cases), H4 10-case replication, M6 attack replication, all in `/tmp/y13r/repl.py`, exit 0
- 20:23:02 to 20:25:22 +07, about 2.3 min: follow-up reads (after-rebootstrap diagnose site, `open_fixture` swap handling, plan `infra_blocked` cross-check, exact line numbers)
- 20:25:22 to 20:27:00 +07, about 1.6 min: this paper written
- Total: about 7 min wall, replication itself 8.1s

## F9 (reload marker): FIXED

Claim (Council A F9, same defect as redteam H3): `_reload_settings` tolerated any click error, and at step 26 the persistence `wait_for` could pass on stale text set by step 21. Fix: set `window.__y13_reload_probe` before the click; a surviving marker raises a step failure.

### Ordering verified in the `cb26d1d` bytes

`tests/realistic/run_codex_y5.py`, `_reload_settings`, lines 2918-2991:

- Marker set BEFORE the click: lines 2941-2942 (`d.eval("window.__y13_reload_probe = 'before-reload'; ...")`), click in `try` at lines 2943-2946.
- `wait_ready` + 1.0s settle, then `ensure_visible` ladder: lines 2947-2949.
- Swap raise BEFORE the marker check: lines 2950-2960 raise `RuntimeError("INFRA: hidden-body after settings reload; ladder swapped ...")` when the ladder swapped tabs.
- Not-ok raise: lines 2961-2962.
- Marker checked AFTER `ensure_visible` and after the swap raise, BEFORE `wait_for`: line 2963 (`marker = d.eval("return typeof window.__y13_reload_probe;")`), lines 2964-2972 raise on survival, `wait_for` only at lines 2973-2978.
- Tolerance return only after the marker proves a reload happened: lines 2986-2991.

Call sites: both steps share `_reload_settings`, step 21 at line 3110 (`lambda: _reload_settings(d, r, "21")` inside `r.step`) and step 26 at line 3159 (`lambda: _reload_settings(d, r, "26")`). Confirmed, no duplicated logic.

### Fake-driver replication (real `_reload_settings` + real `ensure_visible`, stubbed `diagnose_body` returning VISIBLE)

| Case | Result | Matches Y13 claim |
|---|---|---|
| 1. raise + reload (click raises stale element, marker cleared by the navigation) | RETURN `'reloaded (click raised, tolerance)'`, `wait_for` called once | Yes |
| 2. raise + no reload (click raises, marker survives) | RAISE `RuntimeError: reload settings: click raised RuntimeError: stale element; and the reload did not land (marker survived)`, `wait_for` called 0 times | Yes |
| 3. ok + reload | RETURN `'reloaded'`, `wait_for` called once | Yes |
| 4. ok + no reload (not in Y13 log, tested here) | RAISE `RuntimeError: reload settings: reload did not land (marker survived the click)`, `wait_for` called 0 times | Yes, extra case passes |
| 7. swapped ladder (patched `ensure_visible` to `(False, True)`) | RAISE `RuntimeError: INFRA: hidden-body after settings reload; ladder swapped ...`, `wait_for` called 0 times, marker typeof eval never reached | Yes, ordering holds |

### Edge probes (task asked, both fail-safe, both misattributed)

- 5. Marker eval itself raises (transport failure): the raw `RuntimeError("fake transport down")` propagates out of line 2963 unguarded, `wait_for` 0 calls. No false pass is possible (the step fails), but the failure carries no reload context: through `r.step` it becomes `"step failed: 21 reload settings: RuntimeError: fake transport down"`, and main then diagnoses. If the driver recovers and the body is visible, this reads as a plain live failure even when the reload did land. Nit, message accuracy only.
- 6. Marker eval returns `None` instead of a string: line 2964 tests `marker != "undefined"`, so `None` counts as survived and raises `"reload did not land (marker survived the click)"`, `wait_for` 0 calls. In real Marionette `return typeof ...` always yields a string, so `None` only arises from a transport oddity (for example an eval returning null while the document is being replaced, which is exactly when a reload is in flight). Again no false pass is possible, only a spurious failure with a wrong message. Nit, message accuracy only.

Verdict: FIXED. The three claimed cases behave as claimed, the ordering is exactly as specified, and both call sites share the helper. The two edge probes are recorded as optional hardening (fix list items 6a, 6b), not as blockers.

## F10 (handover re-check per attempt): FIXED

Claim (Council A F10): the handover was checked only at the top of the per-test loop, not before a re-run attempt. Fix: check before every attempt, abort exit 2.

### Exact lines (`cb26d1d` bytes of `run_codex_y5.py`)

- Per-test check: lines 3813-3818, `ok, detail = _check_handover()`, on failure prints `HANDOVER EXPIRED before {tid}`, sets `aborted_handover = True`, `break`.
- Per-attempt check, INSIDE the attempt loop: lines 3826-3832, immediately after `_CURRENT_ATTEMPT["n"] = attempt`, same pattern with message `HANDOVER EXPIRED before {tid} attempt {attempt}`, sets `aborted_handover = True`, `break` out of the attempt loop. Attempt 1 is checked twice (once per-test, once per-attempt); harmless duplication, no gap.
- Flag traced to the return: line 4120 `if aborted_handover: break` exits the outer test loop; lines 4215-4216 `if aborted_handover: return 2`, placed BEFORE the `return 0 if total_passed == len(results) ... else 1` at lines 4216-4217. The tab-cleanup block between them (lines 4197-4214) is wrapped in `try/except` and cannot swallow the return.
- Note: `summary` may be `None` if the abort fires before any attempt runs; the guard at line 4121 (`if summary is not None and ...`) handles that, so no crash precedes the exit 2.

No replication of `main()` was attempted (it needs a live browser); the verdict rests on the read trace, which is complete and has no branch that can lose the flag. Verdict: FIXED.

## H4 (`_proven_no_body` split): PARTIAL

Claim (redteam H4): `diagnose_body` conflated "no body element" with "eval transport failure", so a hung driver mid-test was reported as fixture-unavailable, never incrementing `infra_blocked`. Fix: new helper `_proven_no_body(diag)`, applied at the ladder sites and in main's mid-test handler.

### The four required sites: all present, all with the correct split

Helper at lines 818-836:

```python
def _proven_no_body(diag):
    snaps = diag.get("snapshots") or []
    if not snaps:
        return False
    if any(isinstance(s, dict) and s.get("hasBody") for s in snaps):
        return False
    return any(isinstance(s, dict)
               and not s.get("hasBody")
               and s.get("readyState") == "complete" for s in snaps)
```

- Site 1, initial diagnose in `_ensure_visible_inner`: lines 889-898. `FIXTURE_FAILURE` plus proven raises `FIXTURE-UNAVAILABLE`, else raises `INFRA: diagnose transport error, not a proven no-body fixture: ...`.
- Site 2, poll loop: lines 909-918. Same split, same wording.
- Site 3, post-removal: lines 957-968. Same split, same wording.
- Site 4, main mid-test handler: lines 3944-3967. `elif cls == "FIXTURE_FAILURE":` at 3944, `_proven_no_body(diag)` at 3945, proven sets outcome `fixture-unavailable`, unproven sets `raised_infra = True`, outcome `infra-blocked`, with the transport detail recorded. The handler reads in full: `diag = {}` initialized before the `try` at line 3931, `diag = diagnose_body(d)` and `cls = diag["classification"]` inside `try`, `except Exception: cls = "UNKNOWN"` at lines 3932-3936. Trace for `diagnose_body` itself raising: it cannot return a non-dict in the frozen base (it catches eval failures internally and returns dicts), but if it did raise, `cls` becomes `UNKNOWN`, `diag` stays `{}`, the `FIXTURE_FAILURE` branch is not entered, and the test falls through to the timeout check or a live failure. That is fail-closed. The `diag.get('eval_error', 'no snapshots')` read in the unproven branch is safe on `{}`.

### Independent 6-case replication (my own cases, real `_proven_no_body` from `cb26d1d`)

| Case | Input | Result | Correct? |
|---|---|---|---|
| 1. snapshots empty + eval_error | `{"snapshots": [], "eval_error": "URLError: timed out"}` | `False` (INFRA) | Yes, this is the hung-driver trace |
| 2. hasBody true present | `[{"hasBody": True, "readyState": "complete"}]` | `False` | Yes, contradictory sample is not proof |
| 3. hasBody false + readyState complete | `[{"hasBody": False, "readyState": "complete"}]` | `True` (fixture) | Yes |
| 4. hasBody false + readyState loading | `[{"hasBody": False, "readyState": "loading"}]` | `False` | Yes, document not complete, no proof |
| 5. snapshot missing hasBody key | `[{"readyState": "complete"}]` | `True` | Debated, see below |
| 6. eval_error present with proven no-body snapshot | `[{"hasBody": False, "readyState": "complete"}]`, `eval_error` set | `True` (fixture) | Debated, see below |

Extra cases run for completeness, all as expected: mixed body + no-body snapshots `False`; non-dict entry in the list plus a proven one `True` (the `isinstance` guard works); no `snapshots` key at all `False`; proven snapshot plus a loading snapshot `True`.

### Dissent 1: case 6, ignoring `eval_error` when a snapshot proves no-body

This is the one real debate in this review, and I record both sides.

- Side A (redteam prescription, the helper docstring, the amended plan clause): a diagnose transport error is INFRA. Redteam said "inspect `diag.get('eval_error')` ... reclassify to INFRA; only a diagnose that positively proves ... stays fixture-unavailable". The helper docstring at lines 818-829 says the same: "A transport error (eval_error present, or no snapshots at all) is NOT a proven no-body fixture; callers must treat it as INFRA." The amended plan clause at lines 378-380 says "a diagnose transport error (eval_error present, or no snapshots) is INFRA". The code checks none of this: it never reads `eval_error`.
- Side B (the code as written): the only real producer of a proven snapshot plus `eval_error` is `diagnose_body`'s second-sample failure path in the frozen base (`run_live.py` at `1e3901c`): snap1 is a successful eval returning `hasBody` false with `readyState` complete, then the snap2 eval raises, and the function returns the snap1 classification with `eval_error` attached. Snap1 is a genuine, complete observation: the document was loaded and had no body at that moment. A driver hang after snap1 does not put a body back. Calling it fixture-unavailable is substantively right; calling it INFRA would grant a re-run against a fixture that provably has no body, and the re-run would hit the same no-body fixture.
- My judgment: Side B is right on behavior, Side A is right that the words are wrong. The code's answer for case 6 is correct, but the helper docstring and the plan clause both state a rule the code does not implement. The fix is to correct the words to the actual rule (fix list items 2 and 5), not to change the code to follow Side A. A future reader who trusts the docstring will misjudge this function, which is exactly how the original H4 conflation survived review once already.

### Dissent 2: case 5, a snapshot missing the `hasBody` key counts as proof

Line 834-836 uses `not s.get("hasBody")`, so a missing key counts as no-body. Strictly, "positively proves" should require `s.get("hasBody") is False`. Mitigations, both real: the frozen `_DIAG_JS` always emits `hasBody: !!b`, so a real snapshot never lacks the key (this case is unreachable from real `diagnose_body` output); and the frozen `_classify_snapshot` uses the identical `not snap.get("hasBody")` test, so the helper is consistent with the base. I do not treat this as a live hole, only as a one-line hardening (fix list item 3).

### Additional gap found: the after-rebootstrap diagnose is not split

`_ensure_visible_inner` calls `diagnose_body` a fourth time after rebootstrap, lines 987-993. A `FIXTURE_FAILURE` there is NOT split: it falls through to `_log_diag` and `return (False, True)`. `open_fixture` (lines 1236-1276) treats `(False, True)` as a swap, reloads the fixture on the new tab, runs the ladder again, and ends in an `INFRA: hidden-body` raise. Consequence, fail-safe but wrong: a genuinely proven no-body fixture that only surfaces after rebootstrap is reported as INFRA (incrementing `infra_blocked`, possibly aborting the run after two such tests) instead of fixture-unavailable, after burning extra tabs. Reachability is narrow: for a no-body fixture the initial diagnose at line 884 would normally already raise `FIXTURE-UNAVAILABLE` before any rebootstrap, so this path needs the fixture to be hidden-but-present on the first tab and no-body on the fresh tab (for example the fixture server dying mid-ladder). Y13's log claim ("applied at all 3 ladder raise sites") is literally true about raise sites, but this fourth diagnose consumption point was missed. Fix list item 1.

Verdict: PARTIAL. The core H4 defect is fixed at all four required sites and the hung-driver trace now yields INFRA. The partial is carried by the unsplit after-rebootstrap site (real behavior gap, fail-safe direction) plus the docstring and plan wording that contradict the code on `eval_error`.

## M6 (sha256 handover fingerprint): FIXED

Claim (redteam M6): the fingerprint was `(asserted_at_unix, mtime_ns, size)`, so a rewrite preserving mtime with identical `asserted_at` and size passed. Fix: fingerprint the token content (sha256 of the file bytes).

### Verified in the `cb26d1d` bytes, `_check_handover`, lines 251-283

- One read serves both parse and fingerprint: line 264 `raw = HANDOVER_FILE.read_bytes()`, line 265 `tok = json.loads(raw)`, line 279 `fp = hashlib.sha256(raw).hexdigest()`. There is no `.stat()` call anywhere inside `_check_handover` (grep over lines 251-283 returns nothing), so there is no read-vs-stat TOCTOU window at all.
- Pin-and-compare: lines 280-282, first call pins `_HANDOVER_FP["fp"]`, later calls refuse on mismatch with `"handover token changed mid-run; refusing"`.
- `_HANDOVER_FP` initialized at line 162, `HANDOVER_MAX_AGE_S = 4 * 3600` at line 146.

### Attack reproduced (real `_check_handover` from `cb26d1d`, temp token file)

- First call on token `{"asserted_at_unix": <fixed>, "basis": "AAAA-owner-away", "run": "y13-test"}`: `ok=True`, `"handover token age 0s, basis: AAAA-owner-away"`, pinned fp `2ee0547a4d5f147306a08a5c39d300b7fcbba34a875a03b729f70b5bb6c4884e`.
- Attack: rewrote the token with basis `"BBBB-owner-away"`, same `asserted_at`, same size (86 bytes both), then restored mtime exactly with `os.utime` (verified `st_mtime_ns` equal). Second call: `ok=False`, `"handover token changed mid-run; refusing"`. The exact attack redteam described is refused.
- Non-dict JSON: a JSON list token `[1, 2, 3]` returns `(False, "handover file has no valid asserted_at_unix")`, no raise. A JSON string token and a dict missing `asserted_at_unix` fail closed the same way, no raise. The `tok["asserted_at_unix"]` lookup raising `TypeError` on a list is caught by the `except Exception` at line 271.

Note: pinning happens on the first call, so a swap before the first call becomes the baseline. That is inherent to any pinning scheme, not a hole in this fix.

Verdict: FIXED.

## F11 / M5 (plan amendment): FIXED on its point

Claim (Council A F11, redteam M5): fixture-unavailable left `infra_blocked` unchanged while plan v2 said it "resets on any non-INFRA failure". Resolution chosen: amend the plan to the code's fail-safe rule (Y9 precedent), no code change.

### Amended lines quoted (plan at `cb26d1d`, lines 355-372)

> `- ABORT: infra_blocked counts hidden-body-unrecoverable only; session-creation failures use the separate wd_failures counter (own two-consecutive abort; only a failure to CREATE the session counts, a step failure URL contains "/session/<id>/..." and must never count; wd_failures resets to 0 after a successful session creation). infra_blocked resets on any pass and on any non-INFRA failure, EXCEPT fixture-unavailable and guard outcomes (guard defect / guard inconclusive), which leave the streak unchanged. AMENDMENT (redteam re-review M5, 21/11): the plan's original wording said "any non-INFRA failure", but the runner (following Y9's code precedent) deliberately does NOT reset on fixture-unavailable / guard outcomes. The fail-safe direction is kept: a fixture failure between two INFRA tests does not hide the streak, so the run aborts sooner rather than later. First INFRA counts, a successful re-run resets it to 0, a second INFRA increments again.`

### Cross-check: no other plan clause contradicts the code on the reset rule

- Plan line 56-57: "First INFRA counts; a successful re-run resets infra_blocked to 0; a second INFRA increments again." Consistent with code lines 4025-4031 (`raised_infra` increments, pass resets in the `else` branch).
- Plan line 96 (C3 G3): "guard-pass failure has no effect on infra_blocked." Consistent.
- Plan line 330: guard outcomes leave `infra_blocked` unchanged. Consistent.
- Code lines 4025-4031: `if raised_infra: infra_blocked += 1; elif guard_defect or guard_inconclusive: pass; elif outcome == "fixture-unavailable": pass; else: infra_blocked = 0`. Matches the amended plan exactly. The suite JSON comment at the `fixture_unavailable` count states the same fail-safe rationale.

### One stale clause found, on the neighboring classification point (not the reset rule)

Plan lines 81-82 (C3 F11 / RT H4/H7) still say "FIXTURE_FAILURE and UNKNOWN stay live failures." That contradicts both the amended clause at lines 376-380 and the code: a proven `FIXTURE_FAILURE` now becomes the `fixture-unavailable` outcome, and an unproven one becomes `infra-blocked` (with a re-run). Only the `UNKNOWN` half is still true. This is a leftover from the pre-split wording that the 22-line plan diff did not touch. It is a plan inconsistency, not a code bug, and it belongs to H4's amendment set. Fix list item 4.

Verdict: FIXED on the F11/M5 point (the reset rule is now stated, the amendment note records why, and no clause contradicts the code on that rule). The stale C3 F11 clause is carried as an exact fix under H4.

## Overall verdict: AMEND

No BLOCK-level hole: nothing in this scope can produce a false pass, a false green, or a live-driving safety issue. The reload proof is real, the handover re-check aborts with exit 2, the handover fingerprint closes the described attack, and the hung-driver misclassification is fixed at all four required sites. The amendments below are exact, small, and all fail-safe in their current (unfixed) form except as noted.

### Exact fixes required

1. H4a (behavior): split the after-rebootstrap diagnose in `_ensure_visible_inner`, lines 987-993. On `FIXTURE_FAILURE` there: if `_proven_no_body(diag)` raise `RuntimeError("FIXTURE-UNAVAILABLE: ... no body element")`; else raise `RuntimeError("INFRA: diagnose transport error, not a proven no-body fixture: ...")`, using the same wording as the other three sites. Do not let it fall through to `return (False, True)`.
2. H4b (words, not code): correct the `_proven_no_body` docstring, lines 818-829, to the actual rule: a transport error (`eval_error` present) does NOT by itself defeat proof; only empty snapshots, any snapshot with a body, or no snapshot with `hasBody` false and `readyState` complete defeat proof. Record the dissent: the alternative (code follows the redteam literal rule and checks `eval_error` first) would discard a valid snap1 observation; this review judges the current code behavior correct and the docstring wrong.
3. H4c (hardening, one line): in `_proven_no_body`, lines 832-836, tighten `not s.get("hasBody")` to `s.get("hasBody") is False`, so a snapshot missing the key is not counted as proof. Unreachable from real `_DIAG_JS` output today, but it is what "positively proves" means.
4. Plan lines 81-82 (C3 F11): amend "FIXTURE_FAILURE and UNKNOWN stay live failures" to the split: "FIXTURE_FAILURE splits: a positively proven no-body document is fixture-unavailable; a diagnose transport error is INFRA; UNKNOWN stays a live failure."
5. Plan lines 378-380 (mid-test H4 clause): amend "a diagnose transport error (eval_error present, or no snapshots) is INFRA" to the actual rule: "a diagnose transport error with no qualifying snapshot (eval_error present and no snapshot with hasBody false and readyState complete, or no snapshots) is INFRA."
6. F9 nits (optional, message accuracy only, no false pass today): (a) wrap the marker typeof eval at line 2963 so a transport raise is reported as a reload marker check failure rather than propagating raw; (b) treat a `None` typeof result as inconclusive rather than "marker survived" (line 2964).

### Out of scope, noted only

- F1-F8, H1-H3, H5-H6, M1-M4, M7, L1-L3 were not re-reviewed here; Y13's log claims them fixed or declined with reason, and this paper takes no position on them.
- No manifest or SHIPPED.md check was run in this scope; F1 regen is Council A territory, not mine.
- The queue gate (no Y6c marker) is still closed per Y13's log; nothing in this review changes that, and no live driving is authorized by this paper.
