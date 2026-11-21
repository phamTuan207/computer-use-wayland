# Council Member 2 verdict: Worker Y11 hit-rate design (what counts as a hit)

- Role: Council Member 2, debating one question: what counts as a grounding hit or miss per click, and is the proposed hit oracle real or theater?
- Work log (Asia/Ho_Chi_Minh): started 18:52:40, read Y3 gap audit lines 234 and 253, scripts/hit_rate.py, tests/realistic/run_live.py WD class, scripts/calibration_e2.py, docs/calibration-e2-report.md Part B and conclusions, scripts/cdp.mjs elementFromPoint precedent (lines 225-320), calibration hits sample (tests/calibration-e2-hits.jsonl head), click_js vs click vs type_text counts in run_live.py; finished writing 18:54, elapsed about 2 minutes.
- Verdict: **AMEND**. The design is salvageable, but amendment 1 is load-bearing: without it the shipped metric is theater and the verdict becomes BLOCK.
- No git commands run, no commits, no pushes. No ydotool. No personal info. No em dash or en dash used in this file.

## Evidence base (all from the files, with line anchors)

- Y3 gap audit (worker-y3-fcc-verification.md, gap 2 / I8): hit-rate measurement exists only for calibration fixtures, 87 records in tests/calibration-e2-hits.jsonl; the realistic harness records only pass/fail; the G14 25/25 held-out live runs record no per-click hit/miss.
- scripts/hit_rate.py: `hit = actual_target == intended_target` (plain string equality). A miss REQUIRES a known issue_group from ISSUES = wrong_target, coordinate_mapping, visual_grounding, occlusion, unresponsive, unknown. `_SAFE_ID = ^[a-z0-9][a-z0-9_-]{0,63}$`. `summarize()` counts only rows with event == click_attempt.
- scripts/calibration_e2.py: intended target is a calibration grid id (T01, R-series, lowercased with `.lower()`); actual target is the target rect containing the estimated point, OR, when actual-hits data exists, the element that received the click event (`window.__hits`), which wins over geometry. Miss with a different containing rect is wrong_target; miss with no containing rect is visual_grounding.
- tests/realistic/run_live.py: `WD.click(css)` scrolls into view, finds the element by CSS selector, Marionette-clicks it (lines about 505-511). `WD.click_js(js_expr)` runs `el.click()` in JS (no pointer, no hit testing). `WD.type_text(css, text)` clears then sets value via Marionette. Counts in run_live.py: 48 `d.click(` calls, 9 `click_js` calls, 17 `d.type_text` calls.
- docs/calibration-e2-report.md, finding 2.1: pointer/coordinate math is exact (0.5-0.9 px error on 29/29 real clicks); every miss is vision grounding error. End-to-end first-try hit rate 17/29 = 58.6 percent, Grid A 8/20 = 40 percent, Grid B 9/9 = 100 percent.
- scripts/cdp.mjs precedent: elementFromPoint is used as a PRE-click guard, never a post-click oracle. Line about 236: `if(!hit||!(e===hit||e.contains(hit)))throw new Error('element covered; observe again')`, then mouse events are dispatched. The hover path repeats the same check immediately before the click and re-validates the point during hover.

## Q1. Is elementFromPoint after a Marionette element click a REAL oracle, or theater?

Mostly theater as a measure of agent grounding; real only as a narrow occlusion and intercept detector. The distinction matters because the two quantities have opposite values: calibration hit rate is 58.6 percent (vision error), while this oracle on selector clicks would sit near 100 percent by construction.

Why it is a tautology for the stated goal: `WD.click(css)` resolves the target from the CSS selector, and the proposed check reads elementFromPoint at that same element's own rect center. The point being tested is derived from the intended element itself, not from any agent estimate. The agent's vision grounding, the only miss source E2 proved matters ("every miss is vision grounding error", pointer exact to 0.5-0.9 px), never enters the measurement. The live harness bypasses vision entirely: the test script hands the runner a selector, and the oracle then asks the page whether the selector-resolved element is on top of itself. A wrong-element choice by an agent (it aimed at the wrong control) is invisible, because the oracle checks the chosen element against itself.

Failure modes it DOES catch (real, but narrow):

- An overlay, sticky header, toast, cookie banner, or modal covering the element's center at click time, where the cover appeared after Marionette's own interactability check, or where Marionette's check and the oracle disagree about the point.
- The element scrolled out of view, or the viewport changed, between scroll_into_view and the click.
- The element was replaced or re-rendered between resolution and click (a new node with the same selector, so the click lands on a different instance).
- A zero-size, display none, or pointer-events none target that Marionette somehow accepted.

Failure modes it CANNOT catch:

- Vision grounding error (the dominant E2 miss source). The oracle never sees the agent's estimated point.
- Wrong-target selection by the agent (wrong selector, wrong card, wrong row). The oracle only verifies the selected element, not the selection.
- A handler attached somewhere other than the clicked element (delegation on a removed parent, handler on a sibling). The click lands right and still does nothing.
- Hover-dependent behavior. The Polygon Browse button lesson: a click on the exact center does nothing until the cursor hovers off-center and the button darkens. elementFromPoint reports a hit; the action fails.
- Anything about timing or effect: the oracle says where a pointer would land, not whether the click did its job.
- Post-click layout change caused by the click itself (see amendment 2). A successful click that opens a modal, navigates, or removes its own element changes what elementFromPoint returns afterwards, so a post-click read measures the new page, not the click.

One more redundancy to name honestly: Marionette's element click already performs an interactability check and raises ElementClickInterceptedError when another element would receive the click. The oracle therefore mostly duplicates a check the driver already does. Its real marginal value is converting that exception into a counted miss instead of an unlogged step failure, and catching the race between the driver's check and the mouse dispatch. That is worth having, but it is an intercept detector, not a hit-rate oracle.

## Q2. Descendant = hit, ancestor, pointer-events none

Descendant = hit is CORRECT, and it matches the cdp.mjs precedent (`e===hit||e.contains(hit)`). A click on a child bubbles to the intended element's handler, so the click does the intended job. The implementation must collapse the descendant to the intended id BEFORE calling append_attempt, because hit_rate.py computes hit by string equality (actual_target == intended_target). If the wrapper passes the child's slug as actual_target, hit_rate.py records a false miss.

Ancestor = MISS, issue_group wrong_target. If elementFromPoint returns an ancestor of the intended element, the intended element itself is not hit-testable at that point. Events bubble upward from the target, never downward to a child, so a handler attached to the intended child does not fire. Caveat, to record in the log: if the handler lives on the ancestor through event delegation, the click still works, so this rule is conservative. Conservative is the right default for a metric: a false miss is cheaper than a false hit, and delegation cases can be allow-listed per fixture if a test proves the handler is on the ancestor.

Pointer-events none on a child of the intended element: elementFromPoint skips the child and returns what is below it. If that is the intended element itself, it is a HIT (the click lands on the intended element; the transparent child is irrelevant). If the intended element itself has pointer-events none, elementFromPoint returns whatever is beneath it, and the click does not reach the intended element: MISS, issue_group wrong_target (nothing covers it; the element simply is not clickable at that point). Do not call that occlusion; occlusion means an unrelated element is on top, and mislabeling it corrupts misses_by_issue.

## Q3. Movement, null, iframe, shadow DOM

Movement between rect resolution and the click: the oracle is blind here. The pre-click elementFromPoint read passes, the element moves (animation, layout shift, lazy content pushing the page down), and the dispatched click lands elsewhere. Marionette re-resolves the center internally at click time, so the wrapper's own rect read is not even the point that gets clicked. Mitigation is not a better oracle, it is a settle wait plus a post-click EFFECT check (did the expected DOM state change happen), not a post-click elementFromPoint read. Movement cases must be logged with the before and after rects when they are detected by the effect check failing.

elementFromPoint returns null: this happens when the point is outside the viewport or the element scrolled away. Record it as a MISS with issue_group unknown, and attach the rect and viewport bounds in a sidecar log (append_attempt has no field for them). Note the survivorship trap: in run_live.py, a null case usually means Marionette raises first (element not interactable), the step fails, and no append_attempt ever runs. If the wrapper only logs on the success path, every such miss vanishes from the denominator and the rate is biased upward. The wrapper MUST log the miss on the exception path too, before re-raising.

Iframe: elementFromPoint in the top document returns the iframe element itself, never the inner target. Under the proposed descendant rule, the iframe is an ancestor, so a correct iframe click would be recorded as a MISS. The fix is recursion: when the top-level hit is an iframe, run elementFromPoint inside the iframe's contentDocument at translated coordinates, and compare against the inner target. If recursion is not implemented, iframe clicks must be EXCLUDED from the denominator and counted separately, never recorded as hits or misses.

Shadow DOM: elementFromPoint does not pierce a shadow root; it returns the shadow host. Same treatment as iframes: recurse with shadowRoot.elementFromPoint, or exclude from the denominator and count separately. A bare class or tag slug for the host would otherwise produce false hits (the host is not the intended inner element) or false misses, depending on which slug the wrapper picks.

## Q4. Excluding click_js from the denominator: honest or gaming?

Excluding it from the pointer-hit denominator is correct; reporting only the pointer rate is NOT honest. click_js bypasses hover and hit testing entirely, and it is used heavily where the real interaction is hardest: run_live.py has 9 click_js calls against 48 pointer clicks, and run_agyq.py / run_fcck.py route sidebar navigation, card clicks, and grid-slot clicks through JS. A headline rate that silently drops a fifth of the clicks, and the hardest fifth, is gameable by construction: any worker that wants a better number routes hard clicks through JS.

Also, js-clicks have their own silent failure mode the design ignores: `el.click()` on a detached, hidden, or disabled element throws nothing and does nothing. The fcc-k trap in run_f01 proves the point from the other side: a click_js on a td is EXPECTED to do nothing (the fixture trap), so a js-click must never be counted as a success anywhere either.

Honest reporting, required:

- Report three numbers together, always: pointer hit rate (denominator = WD.click attempts only), js-click count and share, and type-action count. The summary must print all three; a pointer rate printed alone is a misleading number.
- Add a guardrail: if js-click share exceeds 25 percent of all click actions in a run, the headline rate is flagged as not representative of agent grounding, and the run summary must say so in plain words.
- Give js-clicks their own companion check, separate from the hit rate: a post-click effect verification (did the expected DOM change happen). A js-click whose expected effect did not happen is a failed action, logged as such, even though it is not a pointer miss.

## Q5. type_text: hit check or out of scope?

Out of scope for the CLICK hit rate, but not out of scope for measurement. A post-type value read is cheap and real: run_live.py already has `WD.value(css)`, so reading back the value after typing costs one eval. Typing into the wrong field is a genuine grounding failure (wrong target), and a value read-back catches it. But it is a different quantity: input fidelity, not click hit. Mixing it into the click denominator would corrupt both numbers.

Required disclosure in every summary: "Click hit rate covers N pointer clicks only. It excludes M js-clicks and K type actions. It is not an overall action success rate." Type attempts should be logged as a separate event type (for example type_attempt, with hit defined as read-back value equals typed text). Note that hit_rate.py summarize() counts only event == click_attempt, so a new event type needs either a summarize extension or a separate summary function; silently writing type records that summarize() ignores would be worse than not logging them.

## Q6. ID slug rules: collisions and what hit_rate.py forbids

The proposed slug rule ("strip leading #/.") is not implementable as stated, and the collision problem is real. hit_rate.py `_SAFE_ID` forbids: uppercase letters, dots, spaces, colons, brackets, parentheses, combinators, and anything longer than 64 characters, and the id must start with [a-z0-9]. calibration_e2.py already lowercases ids (`.lower()`); the live design must do the same.

Concrete collisions in the current fixtures:

- `#upload` and `.upload` both slug to `upload`.
- `#rows tr:nth-child(2) a` cannot be slugified by stripping a leading character: it contains spaces, a colon, and parentheses, all forbidden. A naive replace-everything-non-alphanumeric rule turns `#rows tr:nth-child(2) a` and `#rows tr:nth-child(2) button` into different slugs only by luck of the surviving tokens, and turns `#login-btn` and `#login_btn` into the same slug.
- Two elements sharing a class slug (for example two buttons with class btn) are indistinguishable if actual_target is a tag.class slug. A wrong-element click then compares equal to the intended id and records a FALSE HIT. That is the worst failure mode in this whole design: it manufactures hits.

Required rules:

- Intended and actual must come from the SAME namespace, because hit_rate.py decides by string equality. A selector slug for intended and an element-id slug for actual can never be equal by construction, so the comparison is meaningless unless both sides are derived the same way.
- The namespace must be the resolved element's identity, not the selector: prefer the element's id attribute when present (unique per document), else a deterministic DOM path (tag plus nth-of-type index chain from a stable ancestor). Never a bare class slug. The CSS selector is metadata, not identity.
- Slugify deterministically: lowercase, replace every run of characters outside [a-z0-9_-] with a single dash, strip leading and trailing dashes, truncate to 64 characters. Then handle collisions: keep a per-run registry of slug to full source string; on collision, append a short hash suffix (first 6 hex chars of sha1 of the full source) and re-check. A collision that is silently overwritten is a false hit or a false miss waiting to happen.
- append_attempt's fixed schema (schema 1) has no field for the selector, the point coordinates, the rect, or the viewport. The design needs either a schema bump with those fields or a sidecar JSONL log keyed by (case_id, attempt). Without it, a miss cannot be audited back to what was clicked, and the collision registry has nowhere to live. Do not smuggle the selector into case_id; case_id is the test identity and summarize() groups by it.

## Verdict: AMEND (amendment 1 is load-bearing)

Exact amendments, in order:

1. Rename and re-scope the metric. It is a pointer-occlusion and intercept rate for selector-resolved clicks, NOT an agent grounding hit rate. The summary must call it that, and must state that vision grounding error (the E2-proved dominant miss source) is not measured by this oracle. Ship it under the name "hit rate" without this change and the verdict is BLOCK, because a near-100 percent number would be quoted as proof that grounding is fixed when grounding was never tested.
2. Move the elementFromPoint check to BEFORE the click, in the same eval that resolves the rect, following the cdp.mjs precedent. Delete the post-click elementFromPoint read: on navigation clicks it reads a different document, and on destructive clicks (an element that removes itself) it manufactures false misses.
3. Log on the exception path. A Marionette raise (intercept, not interactable, stale element) must append a miss record before re-raising, or the denominator silently drops every hard miss.
4. Descendant = hit (collapse to the intended id before calling append_attempt); ancestor = miss with wrong_target; pointer-events none on the intended element itself = miss with wrong_target, never occlusion. Occlusion is reserved for an unrelated covering element on top.
5. Recurse into iframes (contentDocument.elementFromPoint with translated coordinates) and shadow roots (shadowRoot.elementFromPoint). If recursion is not implemented, exclude those clicks from the denominator and count them separately.
6. Null from elementFromPoint = miss with unknown, with rect and viewport in a sidecar log. Movement between check and click is a known blind spot; cover it with a post-click effect check, not with elementFromPoint.
7. Report pointer rate, js-click count and share, and type-action count together in every summary, with the disclosure sentence from Q5. Flag any run with js-click share above 25 percent as not representative of grounding. Give js-clicks a separate post-click effect check.
8. Fix the id namespace: element identity (id attribute, else deterministic DOM path), one namespace for intended and actual, lowercase slugify with dash-collapsing and truncation to 64 chars, per-run collision registry with a 6-hex hash suffix on collision, never a bare class slug. Bump the record schema (or add a keyed sidecar log) to carry the selector, point, and rect, so misses are auditable.
9. Do not merge live selector-click numbers with calibration vision numbers in one summarize() output. They measure different quantities (58.6 percent vision grounding vs near-100 percent selector occlusion). Report them side by side with their definitions, or the combined number is meaningless.

## Single weakest point

The tautology in Q1: the oracle tests a selector-resolved element against itself, so it cannot see vision grounding error, the only miss source the E2 calibration proved exists. Everything else in the design is fixable mechanics (ordering, ids, exceptions). This one is conceptual: if the headline number is called a hit rate while measuring something else, every downstream decision (is grounding fixed, is A1 working, can we stop optimizing) rests on a number that was near 100 percent before the first agent ever ran. Amendment 1 exists to kill that misreading; without it, no other amendment matters.
