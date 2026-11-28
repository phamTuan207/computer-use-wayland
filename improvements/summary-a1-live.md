# A1 live measurement, 2026-11-19

**Verdict: FAIL success bar, PROVISIONAL (non-Astra).** All three tasks passed functionally, but none met its speed bar. Astra 6 was out of credit.

## Preconditions and setup

- Repo: `~/computer-use-wayland`, branch `speed-swarm`, HEAD `f95807d5115b84f527f143e60e1f3a85e850fea5`. The A1 DOM implementation commit `83f4224` is in its history. The worktree was clean before and after. `main` was not touched.
- Relay at 2026-11-19 14:06 +07: `computer-use-relay` active and running. Drop-in `a1.conf` was present with `CU_CODE_EXEC=1` and `CU_PICK4_FASTPATH=1`. Broker was idle, owner null, driver idle, guardian idle, active sequence null. Its `started_git_head` matched the repo HEAD. I did not change the relay or drop-in.
- Smoke: fresh broker session, sequence 1 `code-exec`, result `ok: true`, one in-program API call, 2.076 ms. Session finished cleanly.
- Fixture: recreated at `/tmp/speed-pick4-20261118/pick4-fixture.html`, byte check passed, 320 bytes, SHA-256 `ddfc86fa82d6962dc6409be6eed9ce62a02b810edf7e05b7066a77ba364fc881`. This is a faithful recreation from the specified content, not the byte-original.
- The D1 source was copied from `improvements/a1-dom-program-template.md` with the required `dom_start()` and success check added before `windows()`. The referenced `improvements/pick1-program-template.md` contains P3/P4 code blocks but no P1/P2 blocks. I used its documented P1/P2 shape, and commands documented in the repo: `df -h /` and `python3 -c "print(144/150*100)"`. The actual programs and hashes are in this run directory. All program and request files were mode 0600.
- Timing zone: Asia/Ho_Chi_Minh, UTC+07. Wall is broker start submit through verified task result. Think is the sum of intervals from driver-ready or the previous timed result to the next operation request. Service is start-submit to driver-ready plus timed request service, including the D1 diagnostic calls. Model calls below count task operation requests plus finish, excluding session start and status polling. D1 includes the diagnostic `windows` request. The full local timeline is `wall-clock.log`.

## Per-task measurements

| Task | Wall, start submit to verified | Think total | Think before code-exec | Service | In-program elapsed | Model calls | Refusals / misclicks / deaths | Program retries | Requests and images |
|---|---:|---:|---|---:|---|---:|---|---:|---|
| D1 | 128.736 s, 14:08:10.567 to 14:10:19.303 | 126.034 s | 26.773 s before attempt 1; 61.060 s before successful retry; 87.833 s cumulative before code-exec calls | 2.702 s | 868.815 ms successful; 688.263 ms failed attempt | 4 | 0 / 0 / 0 | 1 | Sequences 1, 2, 3; 3 images, 64,228 bytes |
| P1 | 30.769 s, 14:14:13.519 to 14:14:44.288 | 29.165 s | 29.165 s | 1.604 s | 675.058 ms | 2 | 0 / 0 / 0 | 0 | Sequence 1; 3 images, 1,538,461 bytes |
| P2 | 19.387 s, 14:15:26.831 to 14:15:46.218 | 17.705 s | 17.705 s | 1.683 s | 757.276 ms | 2 | 0 / 0 / 0 | 0 | Sequence 1; 3 images, 1,555,242 bytes |

D1 had two code-exec attempts. Attempt 1 returned `IndexError: list index out of range` after `dom_start()` and `windows()`, before any desktop input. A read-only status and `windows` diagnostic showed the managed Chromium had appeared as `about:blank`; the same program then succeeded on sequence 3. Successful program evidence: `result.ok: true`, button ref `e2` was `Show result`, DOM click completed, and `dom_assert` returned without error. The post-click screenshot `~/.cache/agent-computer-use/fefd1e5f4a4e.png` shows `pick4-ok hello stranger`.

P1's verified terminal image shows `df -h /`, root available space `18G`, usage `96%`. P2's verified terminal image shows `96.0` from the documented calculation. Both programs had the requested four in-program API calls and no file asserts.

## Baseline comparison and outcome

- **D1:** DOM-first baseline had 10 operation requests and about 82 seconds to verified, derived from n=1. A1 used 3 operation requests including the failed attempt and diagnostic, so its request count was lower. Its 128.736 second wall was 46.736 seconds higher than the baseline. The call-count part passed; the lower-wall part failed, so D1 fails the combined bar. The 126.034 second think total includes the startup race, diagnosis, and retry, so it is not a like-for-like comparison with the baseline 20.7 second core-loop think.
- **P1:** Pick 1 rerun baseline was 18.89 seconds wall, 17.38 seconds think, 0.63 seconds service, 2 model calls. A1 was 30.769 seconds wall, 29.165 seconds think, 1.604 seconds service, and 2 model calls. Functional pass, speed bar fail.
- **P2:** Pick 1 rerun baseline was 10.18 seconds wall, 8.59 seconds think, 0.72 seconds service, 2 model calls. A1 was 19.387 seconds wall, 17.705 seconds think, 1.683 seconds service, and 2 model calls. Functional pass, speed bar fail.
- P1/P2 mean wall was 25.078 seconds versus the Pick 1 rerun mean of 17.59 seconds, a 7.488 second increase. No precise speedup factor is claimed. These are n=1 measurements.

## Teardown verification

- Each task broker session finished with `status: finished`, driver stopped, guardian clean. Final broker status at 14:27:05 +07 was `finished`, driver `stopped`, guardian `clean`, active sequence null.
- Chromium was closed with a brokered desktop Alt+F4 act. The act completed one key action and reported `window no longer exists` while capturing its after-image. A new broker session then verified `windows` listed only Jarvis, with no Chromium.
- The terminal Alt+F4 act completed, but a fresh `windows` request still listed `speed-a1-term`. I verified the exact Kitty window was active, closed that exact window through the Hyprland wm-ops close command, then confirmed its PID exited. Final Hyprland clients listed Jarvis only. Zen was absent from the client list throughout; Zen, Jarvis, and music were not otherwise touched.
- Final checks passed: relay still active with `a1.conf` and both flags, repo unchanged and clean, no test windows or terminal, local cancellation clear. I did not use ydotool.

## What remains open

- The D1 program needs a readiness check between `dom_start()` and the immediate Chromium window lookup. The successful run used a retry after Chromium appeared. No repo code was changed in this measurement.
- The named Pick 1 template is missing P1/P2 code blocks. Add or point to those program definitions so the next run can copy them directly.
- The A1 live path is functionally working, but this run did not meet any requested speed threshold. Re-measure after addressing the D1 startup race and clarifying the P1/P2 source programs.
