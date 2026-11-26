# R3-L3 council decision: INVALID event 6 (R3-045) — 2026-11-26

Council worker session: b41ef5ed-520f-43dd-851d-f45db99b9daf. Convened by the parent at 2026-11-26 ~15:16 +07 after coordinator epoch 21 held all releases. All times Asia/Ho_Chi_Minh.

## Question

R3-045 (frozen position 29, Codex lane, ezgif GIF-maker task) was graded INVALID at 2026-11-26T15:17:00+07:00, both Pair B scorers agreeing (Clone2 B1 15:13:00, fresh B2 15:13:58). This is invalid event 6; the budget was 5. The re-plan (section 5) requires a new recorded team decision before further releases. This file is that decision record, for the parent to adopt.

## 1. Is the INVALID grade correct? Yes — accept it, do not challenge, no re-run.

Evidence read: state file current_task (epoch 21), ledger row 36 (R3-045), verdict files R3-045-B1.json / R3-045-B2.json and both grade files, snapshot rung3-run-log/rung3-snapshots/R3-045-L3 (block-evidence.txt, probe-ready.json, file inventory).

- The block is ezgif's own server-side fetch failure: the maker page returned https://ezgif.com/maker?err=http with the banner "The HTTP request has failed. The URL may be incorrect, or the remote server has blocked our access." (screenshot 20261126-150806-block.jpg, sha256 907a5590..., tied to block-evidence.txt). It struck at list step 2 (URL upload, source image 1 of 3), before any scorable output could exist. No anh-dong.gif, no ket-qua.txt.
- It is not a bot wall on the shimmed browser: the page loaded, probe-ready.json shows webdriver false with the pinned shim (bb49ff3f...630b8). Check 11 re-proof trigger correctly NOT fired.
- The runner behaved per the rules: correct service reached via search (20261126-145853-serp.jpg), one upload attempt, 60-second wait after the block, evidence capture, stop, clean teardown. Drive 14:54:14 to 15:09:37, inside the 30-minute limit. No hammering, no substitute service, no fabricated output.
- Both scorers graded independently from snapshot plus key, verified all 8 manifest hashes and both frozen key hashes, and agreed. Scorer 2 recorded the one honest caveat (no pre-submit screenshot of the filled URL field, so the exact characters entered cannot be re-read). There is no snapshot evidence of a mistyped URL, a wrong service, or any runner error; overturning a unanimous two-scorer verdict on speculation would break the scoring-independence discipline the run is built on.
- No re-run: the failure is a service condition (ezgif's fetcher refused by the remote image host), not a runner failure. A re-run would test ezgif's fetcher again, not the runner, and the re-plan's per-task fallback default for a service block is the INVALID path.

## 2. Recomputed numbers (verified independently from the ledger)

- Ledger: 36 rows (1 TEST + 25 PASS + 6 INVALID + 4 FAIL). Re-runs ledger: 3 rows, all PASS (R3-001, R3-002, R3-003).
- Rule-A counted: 28 PASS, 1 FAIL (R3-037 only).
- Invalid events: 6 (R3-011, R3-022, R3-024, R3-026, R3-027, R3-045). Medium group (trung_binh) 5, over the per-group cap of 2 (breach recorded pre-run; R3-045 adds one more medium). No medium backup remains (DP-05 is very-hard tier and is not a medium substitute); R3-045 drops from the denominator.
- Valid original set: 52 (was 53 before this event).
- Bars (pre-declared valid N needs N-2): 50/52 original set; 51/53 with task 56.
- Remaining: 23 original positions (R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100), none graded yet, plus task 56.
- Need: 22 more PASS from 23 remaining original positions (23 from 24 counting task 56). Slack: 1 further FAIL among the remaining tasks. Bar unreachable if Rule-A FAILs reach 3 (2 more).
- Bar reachable: YES.

## 3. Decision: CONTINUE the run with recomputed bars

Exact decision text to record:

"Invalid event 6 (R3-045, ezgif server-side fetch failure, Pair B unanimous INVALID) is accepted into the count. The invalid budget of 5 is exceeded by this event; the run continues under the pre-declared bar table. Valid original set 52, bars 50/52 (original) and 51/53 (with task 56). Rule-A stands at 28 PASS / 1 FAIL; 22 more PASS needed from 23 remaining original positions (23 from 24 with task 56). Releases resume from R3-046. No re-run of R3-045. DP-05 is not substituted for medium drops; each further drop recomputes valid N minus 2 and is notified via the parent. Triggers unchanged: valid 50 pauses releases for council + redteam reconvene; Rule-A FAILs reaching 3 makes the bar unreachable and is notified via the parent before further drives."

Conditions carried with the decision:

- R3-046 (next release, timeanddate class): the pre-declared shared-cause counting with R3-011 still applies only with per-task browser evidence plus scorer-2 confirmation (0 new cap events). R3-028 and R3-036 both ran PASS on the shim, so the expected path is a normal drive. If R3-046 drops, valid 51, bar 49/51, need 21 from 22.
- Any further invalid that is not a proven shared-cause member, or valid reaching 50, pauses releases for a council + redteam reconvene under the delegated gate.
- Check 11 re-proof trigger stays armed; this event does not fire it (server-side fetch failure, page loaded, webdriver false).
- Closure states both countings as before, with event 6 named and this decision file cited.

## Rationale for continuing rather than stopping

The bar is still reachable with slack 1, the counted record is 28 PASS / 1 FAIL, and the remaining 23 positions are unaffected by the ezgif condition. Stopping now would discard a run that is passing at a high rate for a service failure outside runner control, which is exactly the case the INVALID mechanism exists to absorb. The pre-declared bar table already defines how to proceed after a drop; this decision only records that the run proceeds past the 5-event budget line under that table, with the valid-50 and fails-reach-3 triggers still guarding the downside.
