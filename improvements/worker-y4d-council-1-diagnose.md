# Council 1 verdict: Y4d diagnose-first layer (Council Member 1)

- Date: 2026-11-21
- Scope: ONLY the diagnosis layer in `tests/realistic/run_live.py` (uncommitted diff, branch `todolist-push`): `_DIAG_JS`, `_RAF_INSTALL_JS`, `_classify_snapshot`, `diagnose_body`, and the `WD.goto` choke point change.
- Checked against: `improvements/worker-y4b-hidden-body-root-cause.md` (fix design section).
- Verdict: **APPROVE WITH FIXES**

## Q1. Field coverage: complete against the fix design

Every field the Y4b fix design lists is captured in `_DIAG_JS` (`tests/realistic/run_live.py`, lines 86-119):

| Design field | Captured as | Line |
|---|---|---|
| readyState | `readyState` | 95 |
| html classList (tz-hidden, tz-initialized) | `htmlClassList` (+ `htmlClass` string) | 98 (97) |
| body computed visibility / opacity / display | `bodyVis` / `bodyOpacity` / `bodyDisplay` | 102-104 |
| html visibility | `htmlVis` | 105 |
| body inline style | `bodyInline` | 101 |
| transition property / duration / delay | `transition` / `transitionDuration` / `transitionDelay` | 106-108 |
| body rect | `rect` | 109 |
| innerText length | `innerLen` | 110 |
| hasFocus / visibilityState | `hasFocus` / `visState` | 111-112 |
| URL | `url` | 94 |
| rAF tick count | `rafTicks` | 113-114 |

Extras captured beyond the design list, all good: `htmlInline` (line 99, needed for the Y4b wound-2 check on the `--zen-logo-path` marker), `bodyClass` (line 100), `nowMs` (line 115).

Nothing is missing from the fix-design list. On `tz-initialized`: yes, the classList array is enough for capture, since both `htmlClassList` (line 98) and the `htmlClass` string (line 97) carry it, and the snapshot is saved in the log. But no code anywhere reads it, and the classification ignores it entirely. That is acceptable per the design, which defines no classification use for it. Recommended, not required: expose `tzHidden` / `tzInitialized` booleans in the snapshot so a consumer never has to re-parse the array.

Not captured, but out of this function's scope: the decisive-experiment payload extras (recursive matching-rules scan, Transparent Zen `::before`/`::after` logo markers, screenshot, largest rAF gap over a 5 s window, geckodriver ps table). Those belong to the experiment harness, not to a per-diagnose snapshot. Only the rAF-gap item touches this layer, see Q3.

## Q2. Classification: correct on the main paths, one real misclassification

`_classify_snapshot`, lines 130-153. Verified case by case:

- VISIBLE requires `bodyVis == "visible"` AND opacity > 0 (lines 140-146). Body visible but opacity 0 falls through to `OTHER_HIDDEN` (line 146). Correct.
- `bodyVis == "hidden"` plus `tz-hidden` in `htmlClassList` gives `TZ_STUCK_V1` (lines 147-149). Correct.
- `bodyVis == "hidden"` with no `tz-hidden` gives `OTHER_HIDDEN` (line 150). Correct, and there is no V2 category anywhere: the only V2 mentions are the docstring stating its removal (lines 133-136) and a comment in `run_agyq2.py` line 236. `TRANSITION_FROZEN_V2` does not occur in either file.
- Transition property present but class absent: `OTHER_HIDDEN`. Correct per the design (V2 is dead).
- Body missing gives `FIXTURE_FAILURE` (line 138-139). Debatable, see F3 below.

Misclassified cases found:

1. **Second-sample eval error overwrites a hidden finding with FIXTURE_FAILURE (REQUIRED FIX F1).** In `diagnose_body` (lines 170-176), if `snap1` says hidden (TZ_STUCK_V1 or OTHER_HIDDEN) and the second eval raises, `snap2` becomes `{"eval_error": ...}`, the `"bodyVis" in snap2` test fails, and the returned classification is `FIXTURE_FAILURE`. A transport or session error is not a fixture failure, and it discards the snap1 evidence. Downstream effect in `ensure_visible` (`run_agyq2.py` lines 250-263): a persistent eval error skips the `tz-hidden` removal step (it only runs for `TZ_STUCK_V1`) and jumps straight to rebootstrap. Fail-safe direction, wrong label and wrong ladder path.
2. **Body missing is called FIXTURE_FAILURE even while the page is still loading (recommended fix F3).** If `readyState` is `loading` or `interactive` and `document.body` is not yet parsed, the page is transient, not broken. `goto` waits for `complete` first, so this is rare there, but `rebootstrap_tab` diagnoses a switched-to tab with no readiness wait, so it can hit this.
3. **Opacity parsing fails open (minor).** Line 142, `float(snap.get("bodyOpacity") or "1")`: a numeric 0 would be coerced to `"1"` and read as VISIBLE (unreachable in practice, `getComputedStyle` returns strings, but fragile), and a genuinely unparseable opacity string returns VISIBLE via the `except` branch (lines 143-144). An unreadable opacity should be `OTHER_HIDDEN`, not VISIBLE.
4. **Edge: `bodyVis == "collapse"` plus `tz-hidden` gives OTHER_HIDDEN, not TZ_STUCK_V1 (minor).** The `hidden` branch (line 147) is the only one that checks the class, so any other hidden-ish computed value bypasses the V1 check. Near-unreachable (the extension rule sets `hidden`, an author rule would need higher specificity to win with `collapse`), but the class check should sit outside the `hidden` branch.
5. **Inconsistent missing-`bodyVis` handling (minor).** `_classify_snapshot` falls through to `OTHER_HIDDEN` when `bodyVis` is absent (line 153), while `diagnose_body` maps a `bodyVis`-less `snap2` to `FIXTURE_FAILURE` (lines 173-176). Pick one meaning and use it in both places.

## Q3. Double sample and rAF counter: sound for its stated purpose, with limits

- The counter install runs on the first `diagnose_body` call (lines 161-164), i.e. after `goto` plus the 1.0 s settle, NOT at `document_start`. That is fine: a counter installed after load still ticks, because `requestAnimationFrame` fires on any document that is being rendered, independent of the body's visibility CSS. The install is idempotent per document (`typeof window.__y4dRafTicks === "undefined"` guard, `_RAF_INSTALL_JS` lines 120-128), so repeated `diagnose_body` calls in the poll loop do not reset it.
- The counter does NOT survive `goto` + `refresh` in `open_fixture` (`run_agyq2.py` lines 288-291): `refresh()` loads a new document and wipes `window.__y4dRafTicks`. This is harmless for the 300 ms delta, because `diagnose_body` reinstalls on every call and both samples of one diagnose live in the same document. But it means `rafTicks` values are NOT comparable across diagnoses (each post-refresh diagnose restarts at 0), and `nowMs` (line 115, `performance.now()`) resets per document too. The delta IS consumed: `_log_diag` in `run_agyq2.py` lines 154-159 computes `rafDelta300ms` from the two snapshots.
- Two genuine limits:
  a. A single 300 ms window cannot distinguish 1 Hz background throttling from a stopped compositor, and cannot produce the experiment payload's "largest gap over a 5 s window". The double sample shows whether ticks flow while hidden, which is what the fix design asks for, but it is not the 5 s gap measurement the decisive experiment wants. That measurement belongs in the experiment harness, not in this function.
  b. If a navigation lands between the install eval and `snap1`, both snapshots report `rafTicks: null` (the install belonged to the old document, no reinstall happens), and the delta silently becomes `None` in `_log_diag`. Rare race, no crash, but a null delta is logged without any flag that the counter was never installed.

## Q4. `goto` does not raise: NOT acceptable as implemented (REQUIRED FIX F2)

The design says: "`WD.goto` is the choke point: diagnose after the 1.0 s settle, never return a hidden page as ready."

The implementation (`run_live.py` lines 325-349) stores the diagnosis in `self.last_diagnosis`, prints a `[diag]` warning, and returns normally. The comment claims "run_agyq2's `open_fixture` does [consult]; other runners print the warning below." That claim does not hold as a guarantee:

- The only `goto` caller in the agy-q2 rerun path, `open_fixture` (`run_agyq2.py` lines 277-313), does run `ensure_visible` immediately after every `goto` + `refresh` and raises `INFRA: hidden-body` on failure. For the rerun itself, the deviation is harmless.
- But `goto` is also reached by `new_tab` (line 315) and by the suite teardown `goto("about:blank")` (line 1305), and `run_live.py`'s own tests plus `run_agyq.py` and `run_fcck.py` drive through `goto`/`refresh` without ever reading `last_diagnosis` (grep over `tests/realistic/*.py` finds zero references to `last_diagnosis` outside `run_live.py` itself). A hidden body in any of those runners proceeds straight to element interaction and fails as a misleading Marionette error, not as `INFRA: hidden-body`.
- Worse, `refresh()` (lines 351-358) never diagnoses at all. It is the more common reload path in `run_live.py`, `run_agyq.py`, and `run_fcck.py` (lines 622, 645, 674, 861 and equivalents), so the choke point as implemented covers only half the reload paths.

I hold plainly: the deviation breaks the design as a library-level guarantee, even though it does not affect the agy-q2 rerun path. The ladder genuinely needs `goto` to return so it can run, so the fix is not "make goto always raise" but "make goto raise by default, with an explicit opt-out for ladder callers" (see F2). A print plus an unchecked attribute is not a choke point.

## Q5. JS bugs: none found that throw

- Every body access in `_DIAG_JS` is null-guarded: `cs`, `rect`, `bodyClass`, `bodyInline`, `bodyVis`, `bodyOpacity`, `bodyDisplay`, `transition`, `transitionDuration`, `transitionDelay`, `innerLen` all use `b ? ... : null` or `cs ? ... : null` (lines 92-114). `documentElement` always exists in an HTML document, so `getComputedStyle(de)` cannot throw on a missing node. There is no `getComputedStyle` call on a detached node: `document.body`, when non-null, is attached by definition.
- `[...de.classList]` (line 98), `b.getBoundingClientRect()` (line 93), `b.innerText` (line 110), `document.hasFocus()` (line 111), `performance.now()` (line 115) are all safe on the guarded values. `innerText` forces a layout flush on a hidden body and returns `""`, which is the expected corroboration (length 0), not a bug.
- `_RAF_INSTALL_JS`: the self-referencing `const tick` arrow (lines 122-123) is fine, the closure body runs after the `const` initializes, so there is no TDZ fault. The `typeof ... === "undefined"` guard (line 121) makes reinstall a no-op.
- One latent weakness, not a throw: if the install eval fails, the `except: pass` (lines 163-164) leaves `rafTicks` null in both snapshots with no flag anywhere. Recommend logging that case.

## Required fixes (must land before the rerun)

- **F1. Second-sample eval error must keep snap1's classification.** In `diagnose_body` (lines 170-176): when the `snap2` eval raises, return `snap1`'s classification with the error attached (e.g. `"eval_error"` on the result), never `FIXTURE_FAILURE`. A transport error is not a fixture failure and must not skip the `tz-hidden` removal step.
- **F2. Enforce the choke point by default.** `WD.goto` must raise `INFRA: hidden-body` on a non-VISIBLE diagnosis unless the caller passes an explicit `allow_hidden=True`. Thread `allow_hidden=True` only through the ladder paths: `open_fixture`'s `goto` calls and `rebootstrap_tab`'s `new_tab` path. All other callers get the raise. `WD.refresh()` must diagnose the same way (same default, same opt-out), since it is the reload path the current code leaves completely uncovered.

## Recommended fixes (do before the rerun if cheap, otherwise track)

- **F3.** Only classify missing-body as `FIXTURE_FAILURE` when `readyState` is `complete`; while still loading, re-sample once instead of returning a fixture verdict.
- **F4.** Harden the opacity parse (line 142): do not use `or "1"` on a value that could be numeric 0, and treat an unparseable opacity as `OTHER_HIDDEN`, not VISIBLE.
- **F5.** Move the `tz-hidden` check out of the `bodyVis == "hidden"` branch so `collapse` (or any other hidden-ish value) with the class present still classifies `TZ_STUCK_V1`; use one meaning for a missing `bodyVis` in both `_classify_snapshot` and `diagnose_body`.
- **F6.** Expose `tzHidden` / `tzInitialized` booleans in the snapshot (capture via the array is sufficient, this is consumer convenience), and log a warning when `rafTicks` is null in both snapshots so a silently missing counter is visible.

## Notes for the other council members (out of my scope, not judged here)

- The poll / remove / rebootstrap ladder in `ensure_visible` (`run_agyq2.py` lines 222-276) and the `preflight` / orphan-fix changes in `WD.__enter__` are outside this review. I read them only to check what the diagnosis layer feeds.
- `run_agyq2.py` line 291: `open_fixture` calls `d.refresh()` after `goto`, which wipes the rAF counter installed by `goto`'s diagnose. Harmless for the delta (see Q3) but worth knowing when reading tick counts across the two diagnoses.
