# BUILD NOW outcome 2026-11-28: pain-point items 1-5 landed

Execution of the BUILD NOW list from
improvements/pain-point-meeting-20261128.md (commit 631e685c).
Owner order 2026-11-28: whole team works, council+redteam
decide, build the best solutions. F11 (item 2 of the meeting
list) was executed by a separate coordinator and landed as
PR #1225 (merge 6dfa99c5); this record covers the remaining
five items, landed as PR #1227 (merge fae59654) on branch
buildnow-20261128, rebased onto the F11 merge.

## Per item

1. **Emoji UTF-16 fix. LANDED.** `_validate_snapshot` compared
   Python code-point `len(textPreview)` against JS UTF-16
   `textLength`, refusing every valid snapshot of an
   emoji-bearing page (reproduced before the fix: textLength 14
   vs len 13 refused). Fix compares in UTF-16 units
   (`_utf16_len`, surrogatepass for cap-split pairs);
   truncation checks unchanged. Independent review found the
   same mismatch pre-existing in `_fetch_long_string` (grip
   length + substring indices are UTF-16 units); fixed in the
   same PR with a JS-faithful astral longString test
   (Utf16LongStringTransport slices at unit boundaries). The
   item-1 claim is now complete on both paths.
2. **F1 caller audit. LANDED; F1 CLOSED.** Every evaluate
   caller in scripts/zen-rdp enumerated and classified:
   act replay=False (P2a, already); CLI eval was the one
   non-idempotent caller left on replay=True, now replay=False;
   wait_for predicates / wait_load / snapshot / probe / bench /
   smoke are read-only (idempotent, keep RT-06 replay);
   parent_evaluate has no retry (exactly-once; zen_spaces
   create paths inherit); navigate retries same-URL GET
   (idempotent). Fault-injection tests (test_f1_replay.py):
   execute-then-die transport; replay=False keeps the page
   counter at 1 and classifies delivery_uncertain/unsafe; the
   replay=True control double-executes (counter 2), proving the
   harness catches F1. No idempotency store built, per the
   meeting. **P2b gate condition "F1 closure" is now satisfied**
   (audit complete, tests green); P2b still needs its settling
   tests + wrong-match rate before the registry opens.
3. **P2a M5 + M3. LANDED.** M5: test_act_count_js.py executes
   the shipped `_ACT_JS` under Node against the committed
   100-button fixture (fixtures/act-100-buttons.html): true
   count 100, ambiguous refusal, zero clicks; above SCAN_CAP
   the verdict is honest scan_truncated; cutting SCAN_CAP to 6
   breaks the count==100 assertion (sensitivity proven). M3:
   arrived refusals now emit not_delivered/safe
   (ActRefusal.disposition()); the breach path (acted on a
   truncated scan) and lost responses stay
   delivery_uncertain/unsafe. Consumer inventory before the
   change: only this lane's own tests read refusal disposition.
4. **dom.confirm_repost pref. LANDED, live-proven.** Fixture
   test on dedicated sessions first: without the pref,
   location.reload() on a POST result page blocks on the
   confirm-repost dialog (no second POST within 6 s); with
   `dom.confirm_repost.testing.always_accept=true` the reload
   proceeds (second POST ~1 s). Pref added to
   launch_dedicated.py `user_js_text`, which only ever writes
   dedicated throwaway profiles (temp-dir only, marker-guarded,
   owner roots refused by name); never the owner profile.
5. **wait_for gone flag. LANDED.** One-condition inversion
   (gone=True polls until falsy) + wait_for_selector counting
   over the top document with poolScope disclosed in the
   verdict; CLI --wait-gone on eval/navigate/act. A transient
   error is never "gone" (only an observed falsy counts), and
   the F11 terminal check runs before a falsy is accepted, so
   a dead tab raises tab_destroyed instead of falsely
   reporting gone. Shadow-root/iframe traversal stays out
   (pilot-first, unchanged).

## Verification

- Full shard on the branch: 1785 tests in 184.1 s, ok=1708
  error=54 fail=5 skip=18, identical to the main baseline
  (0 status changes).
- zen-rdp unit suites green (140 tests incl. F11 terminal
  tests, 3 live skips).
- Independent review (worker who did not write the code):
  no BLOCKING; MAJOR M-1 (longString UTF-16) + minors m-1/m-2
  fixed in-branch before landing; m-3 (CLI wait-failure result
  hardcodes status "timeout" even for tab_destroyed), m-4
  (invalid selector polls to timeout), m-5 (M5 tests skip
  without Node) recorded as follow-ups, all pre-existing or
  safe-direction.
- gitleaks SUCCESS on PR #1227; merged fae59654.
- Machine layer refreshed on the laptop (rdp_client.py +
  launch_dedicated.py byte-identical by sha256; backup at
  /tmp/machine-bin-backup-20261128-buildnow). rdp_smoke PASS
  on dedicated session port 9253 (137.9 ms, attach 26.4 ms,
  evaluate median 0.3 ms); session stopped by recorded pid.
  Owner Zen (PID 807599) untouched throughout.
- pii-scan delta clean on every commit, gate chained with &&
  (a scan failure blocks the commit; verified live when an
  early mis-invocation exited non-zero and blocked).

## Follow-ups left open (not in this task)

- PILOT FIRST items from the meeting (shadow/iframe fixture
  matrix, background-tab measurement, idle-lock contention
  log, M1 shipped replay timing, P2b settling + wrong-match
  rate) still need their named measurements.
- Review minors m-3/m-4/m-5 above.
- navigate() keeps its own RT-06 retry re-sending navigateTo
  (pre-existing; same-URL re-navigation is near-idempotent;
  the F1 audit classified it idempotent, reviewer noted it as
  a replay of a non-read operation outside the audit's scope).
