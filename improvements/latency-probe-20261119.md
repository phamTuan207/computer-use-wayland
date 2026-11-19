# Latency probe: gpt-6-luna vs gpt-6-astra vs gpt-6.1-sol (M4 fast-tier check)

- Owner: Pham Tuan. Date: 2026-11-19, 19:41-19:44 Asia/Ho_Chi_Minh.
- Worker: latency probe worker (Luna 6 Max). Report to the resume coordinator round 2, not to the user.
- Branch: `latency-probe`, from origin/speed-swarm 8727135. Report only, no code changes. Main stays FROZEN.
- Source brief: model-side-speedup-research.md section 2, M4 (routing / cascade). The probe the research required before any router is built.
- Status: DONE. Verdict is NEGATIVE, and the negative is decisive, not a near miss.

## Verdict

There is NO fast model tier available on this system. gpt-6-astra and gpt-6.1-sol are both REJECTED by the server on the Codex CLI subscription route (ChatGPT account). Both failed 10 of 10 calls with the same error. gpt-6-luna is the only one of the three that runs at all.

Do NOT build a router (M4). A router needs at least two runnable tiers; this system has one. The M4 proposal is CLOSED unless the account or the route changes (the OpenAI API route is out of credit and was not tested here; no other route was tested).

The ~3.0s wall time on the astra and sol calls is error-return latency, NOT inference. It must never be quoted as "astra/sol are faster". They produced no answer and no usage object.

## Method

- Fixed prompt, identical for all 30 calls: "What is 347 * 28? Reply with only the final number, no explanation." Correct answer 9716. A routine step, same shape as the M1 gate-check arithmetic question.
- Order: round-robin, 10 rounds, one call per model per round in fixed order luna, astra, sol. Round-robin (not 10+10+10 blocks) so server-load drift cannot masquerade as a model difference.
- Invocation per call: `codex exec -m <model> -c model_reasoning_effort="max" --sandbox read-only --ephemeral --skip-git-repo-check --json -o <tag>.answer "<prompt>"`, Codex CLI 0.169.0, subscription route. Effort max matches the Luna baseline. No broker, no code changes, no GUI, no relay touch.
- Wall time per call: `date +%s.%N` before and after, to 0.001s. Usage (input, cached, output, reasoning tokens) from the `turn.completed` usage object in the `--json` JSONL.
- Runner: /tmp/latency-probe/run-probe.sh, detached nohup, pid 559685, 19:41:38 to 19:44:43 +07. Raw data: /tmp/latency-probe/results.csv plus one .jsonl, .answer and .err file per call (30 calls, laptop /tmp, not committed).
- Accuracy check: the answer file must contain 9716.

## Results

| Model | Calls | Success | Wall mean | Wall median | Wall range | Reasoning tokens (mean, range) |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | 10 | 10/10, answer 9716 every time | 6.177s | 5.891s | 5.518-7.636s | 41.3, 34-55 |
| gpt-6-astra | 10 | 0/10, identical server error every time | 3.192s (error return, not inference) | 3.123s | 2.834-3.913s | none (no usage object) |
| gpt-6.1-sol | 10 | 0/10, identical server error every time | 3.062s (error return, not inference) | 2.963s | 2.718-3.876s | none (no usage object) |

### gpt-6-luna, per-call wall (s) and reasoning tokens

| Round | Wall | Reasoning | Input tokens | Cached input |
| --- | --- | --- | --- | --- |
| 1 | 5.595 | 42 | 18092 | 0 |
| 2 | 7.636 | 37 | 18092 | 10752 |
| 3 | 5.518 | 34 | 18092 | 0 |
| 4 | 5.870 | 44 | 18092 | 0 |
| 5 | 5.912 | 42 | 18092 | 0 |
| 6 | 6.813 | 36 | 18092 | 0 |
| 7 | 5.600 | 43 | 18092 | 10752 |
| 8 | 5.850 | 41 | 18092 | 0 |
| 9 | 6.716 | 39 | 18092 | 0 |
| 10 | 6.261 | 55 | 18059 | 0 |

Mean wall 6.177s, median 5.891s, sum 61.771s. Mean reasoning 41.3, median 41.5, range 34-55. Output tokens 42-63 per call.

Two side observations from the luna usage objects, both MEASURED:

1. A fresh `codex exec` invocation carries about 18,092 input tokens for a trivial prompt. That is system-prompt and instruction overhead, not the question. It matches the research note that a fresh sub-invocation pays ~18k input tokens with 0 cached (Pick 2 L2 route). It is another reason the in-session dial (M1) beats the per-decision sub-invocation shape.
2. Prompt caching on this route is weak for fresh invocations: only 2 of 10 calls got a cache hit (10,752 cached on rounds 2 and 7, 0 on the other 8). The 97.2% cache hit in the research is a within-session figure; fresh `codex exec` calls mostly pay full input. This does not change the verdict, but it is the correct cache number for the sub-invocation shape.

### gpt-6-astra and gpt-6.1-sol, per-call wall (s), all failures

| Round | astra wall | sol wall |
| --- | --- | --- |
| 1 | 2.863 | 2.851 |
| 2 | 3.437 | 3.470 |
| 3 | 2.943 | 2.955 |
| 4 | 2.932 | 2.971 |
| 5 | 3.399 | 3.003 |
| 6 | 3.435 | 2.898 |
| 7 | 2.864 | 3.008 |
| 8 | 2.834 | 2.867 |
| 9 | 3.913 | 3.876 |
| 10 | 3.303 | 2.718 |

Astra mean 3.192s, median 3.123s, sum 31.923s. Sol mean 3.062s, median 2.963s, sum 30.617s. Exit code 1 on all 20 calls, empty answer file on all 20.

Error, identical in all 10 rounds per model (from the JSONL `error` event):

- astra: "The gpt-6-astra model is not supported when using Codex with a ChatGPT account."
- sol: "The gpt-6.1-sol model is not supported when using Codex with a ChatGPT account."

Each call also logged: "Model metadata for `gpt-6-astra` (resp. `gpt-6.1-sol`) not found. Defaulting to fallback metadata; this can degrade performance and cause issues."

## Correction to the research premise

The research (section 2, M4; section 5 sources) says "The Codex config lists gpt-6-astra and gpt-6.1-sol as available models". That is a misread, now corrected by reading the config. The two names appear ONLY under `[tui.model_availability_nux]` in ~/.codex/config.toml (lines 36-37, value 4 each), which is a TUI "new model available" notice counter, not an availability list and not a usable-models list. The server is the authority, and it refuses both names on this account. The premise "listed, latency unverified" should read "advertised by a UI notice, not runnable on this route".

## What this means for the ranked list

- M4 routing / cascade: CLOSED on the subscription route. No router, no cascade, no per-step model tiering, until a second runnable model exists. If the API route ever regains credit, the probe must be re-run there, because availability on the API route is a different question and this probe says nothing about it.
- M1 effort dial (in-session): still the top open model-side lever. This probe does not test it. Note the luna baseline for a trivial prompt at max effort is 6.177s mean with 41.3 reasoning tokens; the M1 gate check (same shape, low vs max) found 6.0s low vs 7.6s max, so the dial gap on trivial prompts is small and the real test is on routine vision steps, not arithmetic.
- M3 local grounder: unaffected. It never depended on a second hosted model.
- Nothing else in the ranking changes.

## Branch and workspace note

The main laptop working tree was NOT on `latency-probe` when the report was written: it was on `change-only-obs` with uncommitted changes from another worker (modified scripts and pick2 brief, untracked scripts/det_finish.py), and an event-wait worker was running tests concurrently. To avoid touching that work, this report was written, committed and pushed from a separate worktree (/tmp/latency-probe-wt) on the `latency-probe` branch. The main tree was never checked out, modified, or cleaned by this worker. No GUI was opened, no broker session was started, no relay restart, no Zen tabs touched. Desktop verified clean at the end (Jarvis only).

## Bai hoc

(Danh cho Pham Tuan, viet bang tieng Viet don gian.)

- Model ghi trong file cau hinh chua chac da dung duoc. Bai hoc: cai ten xuat hien trong config chi la thong bao gioi thieu model moi, may chu moi la nguoi quyet dinh cho dung hay khong. Muon biet model nao nhanh thi phai goi thu that, khong doan tu ten trong file.
- Ket qua am cung la ket qua. Bai hoc: probe nay khong tim ra model nhanh hon, nhung no dong lai mot huong di (lam router) truoc khi ton them gio xay router cho hai model khong chay duoc.
- Moi lan goi codex exec moi tra gan 18.000 token dau vao du cau hoi chi co vai chu. Bai hoc: goi model theo kieu moi lan mot lenh rieng rat ton kem; giu model trong mot phien roi doi muc do suy luan ben trong phien moi la cach re.
