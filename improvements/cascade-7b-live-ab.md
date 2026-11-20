# Cascade 7B live A/B: verdict LOSS (2026-11-20)

- Owner: Pham Tuan. Worker: Luna 6 Max, cascade 7B live A/B (f1f7edb1). Report to the parent coordinator, not to the user.
- Branch: cascade-local-model, HEAD b7caa16. Both arms ran from the same main checkout on b7caa16 (single-variable design: a baseline on 56f5af4 would have confounded the result, since git diff 56f5af4..b7caa16 shows scripts/cu.py 321 lines changed, H6 prefetch plus speculative pre-capture present in 56f5af4 and absent in b7caa16). Relay MainPID 1433115, started_git_head b7caa16, broker idle at both arm starts.
- 7B server (partial offload, 20/28 layers, ctx 2048, port 8088, PID 1454230): /health ok, VRAM 4895 MiB used / 959 MiB free during the method arm, stopped after the arm (VRAM back to 1570/4284). 3B model never used (failed the gate).
- No em dash or en dash in this file.

## Verdict: LOSS

Success bar (pre-committed): method-arm total wall lower than baseline with no rise in wrong answers, misclicks, refusals, or session deaths. NEITHER leg passed.

- Wall (task spans, session start submit to finish result): baseline 623.812s, method 1437.321s, delta +813.509s (+130.4 percent). Every task slower in the method arm.
- Wrong answers: baseline 0, method 1 seven-B routine wrong answer (P4 finish) plus 1 wrong task answer (P1 11G vs 12G ground truth, executor image misread, not a 7B error; see below). Misclicks 0 both arms, refusals 0 both arms, session deaths 0 both arms.

## Per-task wall (seconds)

| Task | Baseline span | Baseline verified | Method span | Method verified | Span delta |
| --- | --- | --- | --- | --- | --- |
| P1 C-03 | 183.300 | 107.698 | 278.580 | 170.299 | +95.280 |
| P2 E-04 | 55.558 | 27.800 | 130.906 | 75.351 | +75.348 |
| P3 B-01 | 65.905 | 52.583 | 208.926 | 144.092 | +143.021 |
| P4 A-01 | 91.834 | 51.933 | 387.998 | 259.540 | +296.164 |
| D1 fixture | 227.215 | 123.167 | 430.911 | 196.515 | +203.696 |
| TOTAL | 623.812 | 363.181 | 1437.321 | 845.797 | +813.509 |

Think totals (analyze.py gaps): baseline 614.055s, method 1211.453s, delta +597.398s. Broker service: baseline 10.700s, method 11.731s, delta +1.031s. Floor probe (scripted, zero model calls): baseline 59.102s, method 97.017s, delta +37.915s.

## The 7B calls themselves (17 calls)

- Total 7B latency 32.892s, mean 1934.8ms, median 1597.4ms, min 1305.0ms, max 3145.3ms. Slower than the gate mean (1.59s) but the same order.
- By step: windows 5 calls mean 1464.7ms (1365.6-1607.0); verify 7 calls mean 2196.2ms (1351.5-3145.3); finish 5 calls mean 2038.9ms (1305.0-3128.6).
- Escalations: 1 of 17 (P4 final verify, reason "evidence not verbatim in observation"; Luna fallback correct).
- Wrong answers: 1 of 17 (P4 finish, see below). No wrong window picks (all 5 windows calls correct, including D1 picking the Chromium address from the broker list).

## The live 7B judgment error (P4 finish, exact record)

- Task P4 A-01, step finish, model 7B, latency 1394.7ms, confidence 0.7, answer pass=false, evidence "BYTE_MATCH True".
- Correct answer: pass=true. The file /tmp/y-tuong.txt held exactly the 3 requested lines (terminal byte comparison returned BYTE_MATCH True, image showed the exact lines).
- The deterministic postcondition could NOT catch it: a pass=false answer with verbatim evidence passes validation. This is the exact blind spot the gate report section 5 predicted (the false branch is weaker than the true branch by construction), now proven live at 7B, not just at 3B.
- The executor counted it wrong=1, did not retry the CLI, and fell back to Luna (which confirmed the exact lines and BYTE_MATCH True). Artifact still SUCCESS.
- Next step per the gate report: extractor redesign (model extracts a value, code judges typed conditions), not a bigger model. A bigger model does not fix a validator that cannot see this error class.

## The P1 answer error (11G vs 12G, NOT a 7B error)

- Method P1 reported free space 11G; ground truth is 12G (direct df -h /: Size 385G, Used 372G, Avail 12G, 98 percent; df -B1 Avail 12114862080 bytes). Baseline P1 reported 12G correctly.
- Cause chain: tesseract OCR misread "12G" (raw "116"), and the method executor misread the image as 11G, then fed the wrong corrected text into the 7B verify and finish steps. The 7B judged correctly against the text it was given. This is an upstream OCR plus executor misread, the same class as the H5 arms reading 126G, not a 7B judgment error. Counted here as a wrong task answer in the method arm, not as a 7B wrong answer.

## Why the wall went up (attribution, not excuse)

- The 7B call latency is NOT the cause: 32.9s of 7B calls across the whole arm, replacing Luna routine gaps that ran 6-75s each in the baseline. The derived saving (about 8.5s per task) is real at the per-step level but tiny against the noise.
- The delta is Luna think gaps elsewhere in the method arm, which ran far larger than in the baseline: P4 bytecheck gap 76.2s plus finish gap 122.9s (error recovery after the 7B wrong finish, including a byte-comparison round trip); D1 close-observe gap 168.2s; P1 gaps of 60-108s between steps. Method think total 1211.5s vs baseline 614.1s.
- The floor probe proves executor variance alone is the same order as the claimed effect: scripted, zero model calls, yet 59.1s baseline vs 97.0s method (+37.9s). At n=1 per task, an 8.5s per-task effect cannot be resolved against 40-300s of executor think variance.
- So the wall leg is confounded by executor variance and error recovery, but the verdict stays LOSS: the wall did go up by 130 percent as measured, and the wrong-answer leg fails cleanly on the P4 finish error regardless of attribution.

## What did NOT happen

- No misclicks, no refusals (accepted:false), no session deaths in either arm. No lease fights. No relay or broker incidents. Both arms 5/5 task SUCCESS on artifacts (P1 method answer wrong on the number, but the task ran and the file and browser states were correct).
- The 7B server never failed, never needed a restart mid-arm, and held 959 MiB free VRAM alongside voxtype throughout.

## Bai hoc

(Danh cho Pham Tuan, viet bang tieng Viet don gian.)

- Model nho chay nhanh (khoang 2 giay mot lan goi) nhung khong lam ca task nhanh hon, vi phan nghi cua Luna o cac buoc khac moi la phan nang nhat, va no dao dong rat lon giua cac lan chay. Bai hoc: muon do duoc loi ich that cua model nho thi phai do nhieu lan, khong the do mot lan roi ket luan.
- Kiem tra bang code khong bat duoc loi model ket luan sai khi bang chung dung. Bai hoc: muon bat loi nay thi phai de code tu tinh ket qua tu cai model trich ra, dung de model tu ket luan.
- Mot lan chay sai o P4 cho thay loi nay hiem nhung co that: 1 tren 17 lan goi. Bai hoc: ti le sai thap van du de lam hong tieu chi khong tang loi sai, nen can thiet ke lai cach kiem tra truoc khi dung that.
