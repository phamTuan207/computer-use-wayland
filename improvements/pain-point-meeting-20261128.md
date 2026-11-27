# Pain-point meeting 2026-11-28: ranked pains and build decisions

Owner order 2026-11-28 06:31-06:32: scan with last30days,
then the whole team discusses remaining pain points, meets,
and decides what to build; redteam + council at full
strength. Part 1 (scan) is
improvements/last30days-scan-20261128.md. This file is
Part 2, the meeting decision.

Meeting form: 4 independent workers, no coordination between
them: performance lens, reliability + architecture lens,
risk/security + cost lens, and a redteam attacking every
proposal. This file is the synthesis; where lenses disagreed,
the disagreement and the deciding condition are recorded.

## The honest headline first

None of the 7 scan candidates touches the largest measured
time pools. On Clock A (staffed-cycle minutes), post-run
processing is 954 of 1,729 minutes (55 percent) in the
R3-L3 partition; the study's largest stated ceilings are
M11d pre-freeze triage (432.5 runner minutes), the M12 429
rule (245.0 min single-task cap), M1 parallel-ledger release
(the only claimant against the 420 min ledger tail), and M4
Class L decoupling (87.1 measured idle minutes). Clock B is
dominated by usage caps (~62.4 h) and coordinator continuity
(~235 min). The scan candidates are browser-primitive items
worth seconds per task. The meeting funds them only where
measured pain exists, and says plainly: the process pools
remain the bigger lever and are already ranked in
improvements/m-remaining-ranking-20261127.md. Deliberation
volume (71,971 lines, Clock C) is itself a cost; this
meeting is kept to one cycle.

## Ranked pain points (evidence-based)

Browser-lane pains, ranked by evidence strength:

1. **F11 terminal wait burn (measured).** Tab closed at
   1023.7 ms, descriptor-destroyed arrived 0.1 ms later,
   poll loop burned the full 8004.6 ms with zero evaluate
   errors (M8). At the shipped 30 s budget that is up to
   ~29 s per dead-tab wait, reported as a plain timeout.
2. **F1 double execution (correctness, HIGH).** Transport
   retry of a delivery_uncertain act eval can fire the
   in-page action twice. P2a closed its instance
   (replay=False on act); non-act evaluate callers still
   inherit replay=True by default. Gates P2b.
3. **Emoji UTF-16 validation (correctness, reproduced).**
   _validate_snapshot compares Python code-point lengths to
   JS UTF-16 lengths; valid snapshots on emoji-bearing
   pages are refused. Fail-safe, but ordinary web content
   trips it.
4. **M1 stale-actor hang (measured raw, shipped
   unmeasured).** First evaluate on the pre-navigation
   console actor hangs the full 5 s timeout. The shipped
   evaluate(replay=True) recovery number was never measured.
5. **Settling / P2b (gate).** Two settling tests landed as
   code; wrong-match frequency unmeasured; digest proves
   descriptor stability, not element identity (two
   identical Confirm buttons can swap).
6. **Focus steal (one incident, 2026-11-21).** Live runner
   navigated fixture tabs in the owner Zen; owner input
   stopped responding ~1 min. Whether our RDP tab open
   switches the visible tab is unmeasured.
7. **POST resend prompt (unmeasured).** Mozilla fixed it
   with one pref; zero recorded incidents on our lane.
8. **Single-client lock (no incident).** One-shot CLI
   already releases per invocation; no measured contention.

Fleet/process pains (already ranked in the M-ranking, not
re-litigated here): post-run processing 954 min, M11d
432.5 ceiling, M12 245 cap, M1 420 tail, M4 87.1, M7 stall
detection (235 min continuity episodes), daemon deaths
(causes mostly unnamed; supervision decision trigger: 2
named-cause deaths or 2026-12-04).

## Decisions: BUILD NOW

1. **Emoji UTF-16 fix.** Unanimous; redteam survivor #1.
   Compare in UTF-16 units at the validation boundary, one
   regression test with astral characters, truncation check
   preserved, full shard green. Never loosen validation to
   make emoji pass.
2. **F11 narrow terminal flag.** Unanimous in narrow form;
   owner approved the build 2026-11-28 06:29 (separate
   coordinator executing). Internal flag in the two demux
   skip paths, pinned descriptor only, URL-free, no log,
   no cursor, no API, never raises, never actuates. Tests
   per the P3 spec: fake-socket units, M8 replication
   <1.5 s, storm pairing 100 percent, shipped wait_load
   before/after (closes the M1 caveat), full shard,
   independent review. Redteam condition recorded: the
   flag must beat a per-iteration listTabs existence check
   (~7 ms) on merit, and F11 frequency in real runs must
   be instrumented; if near zero, the fix is priced as
   insurance.
3. **dom.confirm_repost pref check, dedicated profiles
   only.** 3 lenses build now; redteam: survive as
   dedicated-profile check only. One pref in the D3 launch
   helper behind the profile-marker fail-closed check, one
   POST-reload fixture test on a dedicated session. NEVER
   set in the owner profile (silent resubmission hazard).
   If the fixture shows RDP reload does not block, record
   the negative and close with no change.
4. **P2a M5 evidence: JS-executing count test.** Redteam
   survivor #3. Commit the 100-button fixture and a test
   that executes the shipped counting JS (Node harness,
   reusing the BLOCKING 1 snapshot test pattern), asserting
   true count 100, ambiguous refusal, zero clicks, at and
   above the SCAN_CAP boundary. Must fail when the count
   is artificially capped. No runtime behaviour change.
5. **P2a M3 refusal disposition.** Arrived refusal emits
   delivered_verified + retry=unsafe while the vocabulary
   defines unsafe as "input may have landed"; an arrived
   refusal proves it did not. Fix: arrived refusal becomes
   not_delivered (or verified with retry=safe); lost
   response keeps delivery_uncertain/unsafe. Redteam
   condition: consumer inventory grep for disposition
   readers first, then envelope tests pinning both paths.
6. **wait_for `gone` flag only.** Majority build (perf,
   risk); reliability pilot-first; redteam: fragment
   survives. One-condition inversion in the existing wait
   script (count==0), read-only, pool scope disclosed in
   the verdict. Shadow-root and iframe traversal are NOT
   in this build (see pilots).
7. **F1 caller audit (defines "F1 closure").** Reliability
   wanted a build; redteam killed the idempotency-store
   program and kept the audit; perf wanted the measurements.
   Converged form: enumerate evaluate callers, classify
   idempotent or not, set replay=False on the
   non-idempotent set, one fault-injection test per such
   caller (response dropped after execution, page-side
   counter stays 1, retry=unsafe). No idempotency store.
   P2b's gate condition "F1 closure" means this audit
   complete with tests green.

## Decisions: PILOT FIRST (named measurement decides)

- **Shadow-root / same-origin-iframe waits.** Fixture
  matrix on a dedicated session, with the target only in
  an open shadow root, only in a same-origin iframe. Count current
  wait failures and time the workaround. Build only if
  non-zero in real task shapes, and only with act pool
  scope reconciled in the same change (redteam's wait-act
  mismatch: a wait that finds what act cannot see converts
  honest timeouts into false readiness). Closed shadow
  roots and cross-origin frames stay excluded.
- **Background-tab discipline.** Measure first: selected
  tab identity before and after RDP tab open, 5 reps,
  dedicated session. If unchanged, close as already
  covered. If it switches, build the smallest fix in our
  open path plus a smoke assertion. The Kitsune extension
  route and handoff consent model stay rejected (profile
  install; owner rejected being asked back).
- **Idle-lock contention.** Log flock wait time and attach
  failures for one run cycle. If zero, close as negative.
  No idle timer build (3 lenses: the one-shot shape is the
  release; a timer without data is for-later code).
- **M1 shipped replay timing.** Measured as part of the
  F11 test list (shipped wait_load before/after on the
  navigate fixture). Flip to a build only if shipped
  recovery still exceeds ~500 ms and a tabNavigated-start
  early abort cuts it by more than 500 ms. No general feed.
- **P2b settling + wrong-match rate.** Both settling tests
  as regression tests (fault-injection submit counter
  stays 1; two-Confirm swap proving digest = descriptor
  stability), plus a measured wrong-match frequency that
  P2a leaves behind. Registry stays gated until all three
  plus F1 audit closure.

## Decisions: NOT BUILD (with reopen conditions)

- **Container-scoped sessions.** 3 lenses kill, risk
  pilot. No RDP expression demonstrated, no incident, no
  requirement; tab pinning + denylist + poolScope
  disclosure already cover the honesty need. Reopen: a
  measured cross-agent tab interference that pinning
  cannot solve, or a protocol-level enforcement proof.
- **Static tool presets.** Unanimous kill. P5 already
  rejected with a ~35 KB tools/list trigger that has not
  fired; 7 CLI subcommands, no MCP surface. Reopen only
  when a measured payload crosses the trigger.
- **Saved flows / replay.** Majority kill; redteam's
  hardest kill. Single secondary source for an
  experimental feature; replay bypasses the P2a uniqueness
  count, reintroduces F1-class double submission, and
  directly conflicts with the standing anti-memorization
  rule (held-out validation, 2026-11-17). Run logs remain
  the audit form. Reopen: a primary-source replay design
  that re-verifies per step (snapshotId + digest +
  count==1) and a measured saving on repeated task shapes.
- **P2b registry.** Gate stays shut (unanimous). Benefit
  unproven (wrong-match rate unmeasured); persistent refs
  fight the one-shot CLI shape and go stale.
- **General P3 event feed.** Closed 2026-11-28, reaffirmed
  by all 4 lenses. Happy-path saving 0 to 1.7 ms; replaces
  nothing; overflow proven under storm (86 dropped of
  286); URL-bearing events add redaction surface. Reopen
  only on F11 frequency data showing material burn the
  narrow fix leaves behind, or a completion-bearing event
  class being observed.
- **Standalone MINORs** from Clone2 reviews: batch as
  drive-by with the next substantive change in the same
  files; standalone review-set cost exceeds any saving.

## Scan-quality caveat (redteam, accepted)

The scan is not full forum coverage: the engine ran 2 of 4
subqueries, Reddit search was 403-blocked (partial
fallback), X/YouTube/TikTok were unavailable, and only 16
of 34 engine items are from the last 7 days. Findings 1-4
rest mostly on host web-search supplements verified
against primary sources. Finding 4 (claude-for-zen) rests
on a Glama listing + GitHub API read (0 stars); Finding 5's
agent-browser and Firefox 155 items rest on secondary
aggregators (agentgid.com, en.98ip.com) and are labelled
UNVERIFIED in the scan. Star counts are popularity, not
fit. Mozilla v0.11.1 shipped 2026-11-27; adopting its
semantics on day two carries zero field bug history, which
is why the meeting adopted only the `gone` inversion and
gated the rest behind fixtures.

## Build order (quality first)

1. Emoji UTF-16 fix + regression test.
2. F11 narrow flag (already in flight, owner-approved).
3. F1 caller audit + fault-injection tests (unblocks the
   P2b gate definition).
4. P2a M5 count test + M3 disposition fix (evidence and
   vocabulary; M5 before any P2b work).
5. confirm_repost dedicated-profile check.
6. wait_for `gone` flag.
7. Pilots in parallel: shadow/iframe fixture matrix,
   background-tab measurement, idle-lock contention log,
   P2b settling + wrong-match rate.

Nothing in this list trades correctness for speed. Every
pilot runs on dedicated sessions (zen_cli.py, ports 9225+);
the owner Zen (PID 807599, port 6021) stays read-only;
loopback-only binding and exhaustive count==1 remain
non-negotiable invariants.
