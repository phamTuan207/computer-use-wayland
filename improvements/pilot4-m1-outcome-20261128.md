# Pilot 4 M1 build outcome 2026-11-28: stale-actor fixes landed

Owner approved the build 2026-11-28 11:10 (including running code
from the fresh worktree ~/workspace/pilot4-build-wt). Spec:
improvements/pilot-first-decisions-20261128.md Pilot 4 section +
pilot4-build-plan-BLOCKED.md (VM ~/workspace/pilot-first-20261128/).
Branch pilot4-m1-fixes-20261128, commit 4bd26e57, PR #1248.

## What was built (scripts/zen-rdp/rdp_client.py)

Fix 1 (TimeoutError replay): evaluate() now replays on
TimeoutError for replay=True callers only, exactly once, F11
terminal check first, receive-buffer guard (non-empty buffer =
partial frame held, fail closed), and only when re-attach yields
a DIFFERENT console actor (same actor = slow-but-alive JS, the
original TimeoutError propagates, script never re-runs). act and
CLI eval stay replay=False (F1 exactly-once preserved);
parent_evaluate and navigate untouched. Sender guard in
_evaluate_once: an evaluationResult whose sender is not the
current console actor is observed and skipped, so a late packet
from a dead actor cannot be consumed as the retry result.

Fix 2 (nav-aware re-attach, scoped form): _reattach_pinned takes
expected_url_substr (wait_load passes its url_substr). A URL
change on the pinned id re-attaches only when ALL hold: F11
terminal flag clear, tab count unchanged since pin (new
_pinned_tab_count field, set only in get_target on success,
list_tabs never updates it, unknown count fails closed), pinned
URL absent from the whole tab list (old URL under another id
still refuses), and url_substr contained in the new URL when
given. The URL guard is never deleted outright; get_target still
applies scope/denylist guards to the new URL.

Drive-by: Pilot 1 README paragraph (top-document-only waits,
gone can be false one root down, traversing workaround
unsupported with the hard count gate: count first, act only on
count==1, never first-match).

## Tests

10 new fake-transport tests: execute-then-silence dead actor
(replay=False counter 1 + TimeoutError + unsafe classification;
replay=True recovers, counter 2), exactly-once under two
silences, slow-JS no-replay (same actor), partial-frame buffer
guard, late-packet desync (sender guard returns fresh result,
next request in sync); nav-aware recovery (old
test_reattach_url_mismatch_refused updated to the new contract),
id-shift / count-changed / url_substr / F11 refusals.

- zen-rdp suites (direct unittest): 203 tests OK, 3 skipped.
- Full shard (4 shards): 1788 tests, ok=1711 error=54 fail=5
  skip=18. Same-tree origin/main (e7367d10) shard: 1788 tests,
  ok=1709 error=55 fail=6 skip=18. No regression; the small
  delta is run-to-run flake in environment-dependent tests.

## Live re-measure (dedicated session port 9311, fixed client)

Same fixture shapes as pilot4-m1-replay.md (1.2 s slow page on
loopback; success = location.href shows the new page):

- S1 fast navigate+wait_load: median 53.6 ms (pre-fix 53.7 ms,
  no regression).
- S2 slow navigate+wait_load(timeout=8): 5/5 COMPLETE, median
  6239.7 ms, retries 5 (one replay per rep). Pre-fix: 8/8
  timeouts at ~11.3 s elapsed. Headline win: wait_load now
  completes inside budget.
- S3 page-initiated nav + immediate evaluate loop (timeout=5):
  median 5019.7 ms, errors_seen [] (pre-fix: 5017.6 ms median
  with 12/12 socket_timeout, replay 0/12). Same wall time (one
  5 s timeout + re-attach + retry, per recovery honesty), but
  the evaluate now recovers internally instead of raising.
- S6 direct evaluate() default timeout=20 after page nav: 3/3
  returned the new-page value at median 20033.8 ms (pre-fix:
  ~20 s timeouts raising). Bounded at caller timeout + retry.

Recovery honesty: fixes 1+2 bound recovery at one timeout plus
~5 ms re-attach plus one fast retry. No sub-500 ms claim; that
would need shorter poll timeouts with measured false-timeout
cost (not in scope). tabNavigated sentinel remains out of scope
(arrival unproven on the shipped attach shape).

Session closed by recorded pid (2142301) with cmdline profile
check immediately after the run; owner Zen 807599 verified alive;
laptop scratch removed.

## Independent review

MAY LAND, no BLOCKING (pilot4-review-20261128.md). Three MAJOR
follow-ups, none spec deviations: (1) same-actor late-packet
desync (pre-existing on main, narrowed by this PR; Fix 1 makes
post-timeout client reuse the norm, so a poison/drain rule or
documented reconnect rule is owed); (2) nav-aware wrong-tab
window under close+open with preserved count + id shift
(inherent to the council-approved guard set; count equality is
necessary-not-sufficient); (3) late-packet shipped test delivers
the stale packet synchronously, so its next-request assertion
does not prove async arrival handling (reviewer probe shows the
code handles it). MINORs include wait deadline overshoot roughly
doubling per tick, stale error packet can kill a retry, and a
few untested nav-aware edges (count-None fail-closed,
denylist-on-new-URL, wait_load end-to-end substr).
