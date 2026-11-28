# Prior-art checks: prompt caching (item 12) + structured output (item 13)

- Worker: prior-art checks worker (Luna 6 Max), 2026-11-19 01:17-01:30 +07, Asia/Ho_Chi_Minh
- Scope: read-only. No broker session started, no relay restart, no repo changes, no config changes. Laptop reads via ~/workspace/ssh-laptop.sh, short calls only.
- Sources: prior-art entries 2.9 (OpenAI prompt caching) and 11.3 (provider structured outputs) in speed-prior-art.md; Codex CLI 0.169.0 on the laptop; repo ~/computer-use-wayland, branch speed-swarm, HEAD c1b7034 (verified, untouched).
- Verdicts marked PROVISIONAL (non-Astra; Astra 6 out of credit).

## Check 1 - Prompt caching (shortlist item 12, prior-art 2.9)

### Question
Is prompt caching already hitting on the repeated system prompt, and is the prompt prefix stable?

### Answer in one line
YES, caching is already hitting hard, and the prefix is stable. There is nothing to fix. No config change, no prompt reordering needed.

### Evidence: Codex CLI usage records (rollout files, ~/.codex/sessions/2026/11/19/)
The Codex CLI records per-turn token usage in `token_usage_record` events. Fields present: `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens`. Note the counters in these records are CUMULATIVE over the thread (turn_token_usage == thread_token_usage), so the per-request fresh-token count is `input_tokens - cached_input_tokens` for that turn.

Session A: rollout-2026-11-19T00-43-54 (gpt-6-luna, 120 turns, runs computer-use task work, 106 "observe" mentions, 113 exec tool calls):
- Turn 0: in=21,627, cached=10,752 (49.7% cached on the very first turn, warm cache from an earlier identical-prefix session)
- Turn 1: 67.7% cached. Turn 3: 79.4%. Turn 5: 86.6%. Turn 7: 89.9%.
- Last turn: in=11,848,494, cached=11,630,720 (98.2% cached).
- Cumulative over 120 turns: in=549,690,728, cached=534,186,112 (97.2%).
- Per-request fresh tokens after warm-up are about 10% of input (turn 7: 25,549 fresh of 252,749). The fresh slice is the new turn content: the new screenshot plus new tool results.

Session B: rollout-2026-11-19T00-54-08 (gpt-6-luna, 33 turns, Pick 4 measurement worker session):
- Turn 0: in=21,061, cached=0 (0.0%, cold start on a brand-new thread).
- Turn 1: 47.3% cached. Turn 5: 80.3%. Turn 11: 87.9%.
- Cumulative over 33 turns: in=24,863,619, cached=22,899,712 (92.1%).

### Prefix stability
- The cached share climbs monotonically turn after turn in both sessions. If anything at the front of the prompt changed per turn (timestamps, changing window lists), the cache would miss every turn and the share would stay flat and low. It does not.
- The developer system prompt is 4 FIXED messages, about 46k chars total (17,793 + 25,530 + 2,400 + 271 chars), byte-identical across turns and across sessions.
- New content (observations, screenshots, tool results) is APPENDED at the end of the transcript, so it never breaks the cached prefix. It only adds the ~10% fresh slice each turn.
- `grep` over scripts/cu.py found NO wall-clock timestamp or datetime in any observation envelope, so broker output cannot destabilise the prefix either.
- One cold-start cost exists: the first turn of a brand-new thread can be 0% cached (session B turn 0). A warm cache (same prefix used minutes earlier) gave 49.7% on turn 0 of session A. This is one turn per session, not a per-turn cost.

### What this means
- Prior-art 2.9's open check is ANSWERED: caching is already hitting via the Codex CLI's automatic server-side prefix caching. It works through the ChatGPT-side Codex path, so the out-of-credit OpenAI API key does not block it; no direct API check was needed or attempted.
- Nothing to build. Do NOT reorder the prompt, do NOT add cache-control breakpoints (Codex CLI exposes none), do NOT build a caching layer.
- The remaining lever is not caching but the ~10% fresh tokens per turn (new screenshot + new results) and the reasoning tokens themselves. That is the masking / fewer-calls work (items 3.1, 3.4), not a caching fix.

### Caveat
The sampled sessions are worker sessions running on the laptop (session B is the Pick 4 worker's own session; session A runs computer-use task work via shell exec calls), not a pristine executor-loop-only session. The mechanism is identical for any Codex CLI session on this machine (same CLI, same model, same server-side caching), so the conclusion transfers, but the exact percentages are from these sessions, not from a dedicated executor-loop measurement.

## Check 2 - Structured output for the action envelope (shortlist item 13, prior-art 11.3)

### Question
Does the Codex CLI expose a structured-output / JSON-schema option for the action envelope, and does the broker already validate the envelope?

### Answer in one line
YES, the CLI exposes it (`codex exec --output-schema <FILE>`), and YES, the broker already validates the envelope strictly. But the flag constrains only the FINAL message of a `codex exec` invocation, so it does NOT apply to the main loop's per-step act envelope as the loop runs today. It applies to the separate-invocation supervisor shape Pick 2 is already building.

### Evidence: CLI option (exposed)
- `codex exec --help` (Codex CLI 0.169.0): `--output-schema <FILE>` - "Path to a JSON Schema file describing the model's final response shape".
- No config-file key for it was found in ~/.codex/config.toml (model and model_reasoning_effort are there; no output-schema key). It is a per-invocation CLI flag only, as far as observed.
- No other structured-output / JSON-mode option exists in `codex exec --help` (checked: --json is JSONL event printing, not schema enforcement).

### Evidence: already wired in-repo by Pick 2 (in progress, not disturbed)
- scripts/subgoal_policy.py:142, `codex_args_for_level()`: for LEVEL_ROUTINE (level 2) it appends `['--output-schema', str(l2_schema_path())]` to the `codex exec` args, with `-m gpt-6-luna -c model_reasoning_effort="low"`.
- Schema file scripts/pick2-l2-schema.json (written by `write_l2_schema()`, mode 600): flat object, `additionalProperties: false`, exactly 3 required keys: action (string 1-64), target (string 1-256), confidence (number 0-1).
- Local fail-closed validator `validate_l2_decision()` in the same file: rejects non-objects, wrong/missing/extra keys, empty action/target, confidence outside [0, 1], irreversible actions.
- Gated OFF by default: `pick2_enabled()` reads env `CU_PICK2_SUBGOAL_ONLY` (subgoal_policy.py:58). `codex_args_for_level()` has no callers outside subgoal_policy.py yet, so the wiring exists but the loop does not call it yet. Pick 2 worker is still building it; do not duplicate this work.

### Evidence: broker validation (present, strict)
- scripts/cu.py:1011 `validate_actions(actions, backend)`, called at cu.py:1388 inside `desktop_act()`, BEFORE any side effect, after `validate_desktop_observation()`.
- What it checks (desktop backend): actions must be a list of 1..32 items; type must be in {click, double_click, move, drag, scroll, type, key, wait}; x/y must be present, numeric and finite for pointer actions, and in-image (`image_point()` bounds check, cu.py:1393-1397); modifiers allowlisted (Ctrl/Shift/Alt/Super/AltGr, max 5); text string <= 10,000 chars, non-BMP rejected for desktop type; wait ms 0..2000; drag ms 50..2000; key repeat 1..30, hold_ms 0..2000; button left/right/middle only. Equivalent checks exist for the a11y backend (ref required) and browser backend (ref/selector mutual exclusion, assert typing).
- `act` takes `--actions` as a JSON path or `-` for stdin (cu.py:2077, 2227); `read_json()` (cu.py:598) raises on empty input, >8 MiB input, or malformed JSON.

### Failure cost: worse than one extra think cycle
- On malformed JSON or failed validation, the ValueError propagates to the top-level handler (cu.py:2368-2371), which prints `{'ok': false, 'error': ...}` and exits 1.
- In the session-driver path (scripts/session_driver.py), that is NOT a transient refusal: `is_transient_refusal()` (cu.py:1327) matches only 'screen changed' / 'focus changed'. So `session_continues` is False, the relay emits `session_ended` and exits.
- Consequence: a malformed action envelope does NOT cost one repair think cycle (14.9s). It kills the whole task session; the agent must start a new session. That makes the structured-output win LARGER than prior-art 11.3 assumed (it kills a session restart, not a retry), but only for invocations where the flag can apply.

### How to turn it on for act steps (if wanted)
1. Do NOT build a proxy (per prior-art 11.3). Do NOT expect `--output-schema` to constrain tool-call arguments inside the long interactive executor session; it shapes only the final message of a `codex exec` run.
2. The applicable shape is Pick 2's: make the act step its OWN `codex exec` invocation whose final message IS the action envelope, e.g. `codex exec -m gpt-6-luna -c model_reasoning_effort="low" --output-schema <act-envelope-schema.json>`, then feed that final message to `cu.py act --actions -`. Keep the broker's own `validate_actions()` as the fail-closed gate after it; it already runs.
3. Schema shape to copy: scripts/pick2-l2-schema.json (flat, depth-1, additionalProperties false, required fields, numeric coordinate fields). Per prior-art 11.2, depth-1 JSON is about 15% faster than depth-4.
4. Guardrail from prior-art 11.4 (CRANE): constrain ONLY the final action JSON, never the reasoning trace. If the model must reason in the same call, let it reason unconstrained and constrain only the output envelope.

## What was cut / not done
- No prompt-caching build, no prompt reordering, no cache breakpoints: the check proved there is nothing to build (item 12 closed as already-hitting).
- No structured-output proxy: the CLI already exposes the flag, and Pick 2 already wires it; duplicating either would be wasted work.
- No config changes, no broker/relay changes, no repo writes on the laptop. All laptop access was read-only (grep/sed/python reads of rollout files and scripts).
