# A4 deterministic postcondition verify: implementation report

- Owner: Pham Tuan. Date: 2026-11-19, evening Asia/Ho_Chi_Minh.
- Worker: Luna 6 Max (Track 2 resume round 2, lever A4 + A3 core).
- Branch: `algo-a4`, from origin/speed-swarm 8727135.
- Status: IMPLEMENTED, unit-tested, committed, pushed.
  NOT live-measured yet: the broker is single-owner and busy with
  the R3 live run. A live-measure worker tests it on the broker
  after R3. No live measurement was attempted in this round.
- Source: `algorithm-research.md` section A4 (R5 from the planning
  survey, narrowed to the verify step). No em dash or en dash in
  this file.

## 1. What A4 changes

Where the end state has an exact local proof, verify with it and
skip the verify observe plus its think call. Measured split: verify
think is 6.7s mean (18% of a 36.4s clean task) plus 1 model call
and about 0.16-0.21s observe service. On P1-P4-class tasks the file
proof already exists (df output, python result, mkdir listing, file
bytes), so 1 call and about 6.7s think per task are removable.
Expected effect is an estimate from the measured split: about 18%
of clean wall on file-provable tasks, recurring on every task.
On GUI tasks without a file proof, 0 calls removable; vision
verify stays.

## 2. What was built

### `scripts/postcondition.py` (new, pure, no broker imports)

`verify_postconditions(checks, *, read_bytes, list_windows,
dom_observe, dir_exists, max_bytes)` returns a verdict dict:

- `status`: `verified`, `failed`, or `inconclusive`.
- `ok`: True only when `verified`.
- `needs_vision`: True only when `inconclusive`. The supervisor
  MUST take a vision verify observe then; inconclusive is never
  success.
- `passed` / `failed`: check names. `checks`: per-check results
  with kind, passed, detail, subject. `elapsed_ms`: local verify
  time (milliseconds, no model).

Check kinds: `file_exists`, `file_contains`, `file_equals`,
`file_sha256`, `window_present`, `window_absent`, `dom_text`.
Every check is re-read from its exact source at verify time,
never trusted from a program variable or a cached observation.
Evidence reports SHA-256, sizes, and matched window/DOM refs,
never file contents (the only text in a detail is the needle the
caller supplied). File checks are read-only.

Pairing rule (the A4 research note: hash change PLUS file bytes,
never a single signal): a spec is verifiable only when it carries
at least one exact-bytes proof (`file_contains`, `file_equals`),
or a DOM text proof (`dom_text`), or at least two passed checks
that are independent signals (different kinds, or the same kind
on a different path/target, e.g. two different directories), or
a single `window_present` that matched BOTH class and title. A
lone `file_exists`, a lone `file_sha256`, or a lone class-only
`window_present` is `inconclusive`, not verified.

Fail-closed rules: malformed specs become `inconclusive` verdicts
(a non-list spec raises PostconditionError, since there is no spec
to report on); a check whose backend the caller did not supply is
`inconclusive` (it cannot prove anything either way); a supplied
backend that raises makes its check `failed`; any check that runs
and disproves the end state makes the verdict `failed`, and the
supervisor must replan, not finish. Limits: at most 16 checks,
text at most 10000 chars, paths absolute, SHA-256 exactly 64 hex
chars, file reads at most 64 KiB in code-exec (1 MiB in the CLI).

### `scripts/code_exec.py` (wired)

- New allowlisted API: `verify_postcondition(checks)`, counts as
  1 API call. File reads stay under /tmp (the code-exec sandbox);
  window and DOM checks go through the same backend the other API
  calls use. Returns the verdict dict; it never raises on a check
  outcome, so the program branches on it.
- The run envelope carries `postcondition` (the verdict) and
  `postcondition_verified` whenever the program called it.
- Docstring verification invariant amended: when
  `verify_postcondition()` reports `verified`, that exact source
  IS the verification and the final observation image is skipped;
  when it reports `inconclusive`, the program must still take a
  verify observe before finishing. The pairing rule decides which
  case applies, not the program.

### `scripts/cu.py` (new `verify` subcommand)

`cu.py verify --spec <file|->` reads a JSON spec (a checks list,
or an object with a `checks` list) from a file or stdin and prints
the verdict envelope. Gated by the same opt-in flag as code-exec
(`CU_CODE_EXEC=1`, default OFF). A verdict is a result envelope,
not a session-ending error: return 0 so the supervisor can finish
on `verified`, replan on `failed`, or fall back to vision verify
on `inconclusive`. Window/DOM checks require a session (same
`require_session` + `locked()` discipline as code-exec);
file-only checks run without one. The CLI file reader is
read-only, absolute paths, regular files, 1 MiB cap.

### `scripts/session_driver.py` (relay)

`verify` added to the relay allowlist, so the supervisor can send
it as a driver command like `observe` or `code-exec`.

### A3 minimal core (also in this branch)

`scripts/procedure_library.py` plus `tests/test_procedure_library.py`:
exact-key procedure store (JSON, mode 0600), `procedure_key()`,
register (validates program with the code-exec AST sandbox and
checks with the postcondition validator), retrieve (exact match
only, None when missing or quarantined), quarantine after 2
consecutive checkpoint failures (threshold imported from
`subgoal_policy`), checkpoint via the A4 verifier. No execution
path of its own: retrieve returns program source, the caller runs
it through code-exec. Full design in
`improvements/a3-procedure-library-design.md`.

## 3. How a program uses it (P4 example)

Old shape (template rule, unchanged when no local proof exists):

```
windows() -> observe() -> act() -> observe() -> assert
```

A4 shape, file-provable end state:

```python
wins = windows()
term = [w for w in wins if w["title"] == "speed-pick1-term"][0]
obs = observe(window=term["address"])
result = act([{"type": "type", "text": "printf '...' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\\n"}], obs)
assert_state(result["ok"], "act failed")
verdict = verify_postcondition([
    {"kind": "file_contains", "path": "/tmp/y-tuong.txt", "text": "Ý tưởng 1: app nhắc uống nước."},
    {"kind": "file_contains", "path": "/tmp/y-tuong.txt", "text": "Ý tưởng 2: bot tóm tắt bài giảng."},
    {"kind": "file_contains", "path": "/tmp/y-tuong.txt", "text": "Ý tưởng 3: web bán đồ secondhand."},
])
assert_state(verdict["status"] == "verified", "postcondition failed")
```

No second observe, no verify image. If the verdict is
`inconclusive`, the program must still do the verify observe and
assign `verify_image` before finishing. The template file
(`improvements/pick1-program-template.md`) carries the A4 shape
section; the P1-P4 programs in it are unchanged (they are the
measured programs).

## 4. Unit test evidence

New tests, all passing on the laptop worktree 2026-11-19 evening:

- `tests/test_postcondition.py`: 37 tests. File checks (contains,
  equals, sha256 alone inconclusive, sha256 mismatch fails,
  missing file fails, two-kind pairing, paired helper, real
  temp-file round trip), directory checks, window checks
  (class+title verifies, class-only inconclusive, absent,
  backend error fails closed), DOM checks, verdict shape.
- `tests/test_procedure_library.py`: 19 tests. Key determinism,
  register/retrieve, validation rejections, store persistence
  and mode 0600, corrupt store loads empty, quarantine after 2
  failures, success resets the count, quarantine survives reload,
  re-register clears quarantine, checkpoint pass/fail.
- `tests/test_code_exec.py::VerifyPostconditionTests`: 7 tests.
  In-program verify, envelope reporting, failed verdict as data,
  single-signal inconclusive, window check, unknown kind
  inconclusive, non-list sandbox error, no-verify envelope clean.

New-test total: 63 tests, 0 failures, 0.010s.

Full suite (worktree, branch algo-a4): RAN, see section 5.
Baseline (8727135, before this work): 1339 tests, 7 failures,
2 skipped, 102.621s. The 7 baseline failures are pre-existing
and untouched by this change (1 chromium CLI wiring, 5 session
driver doctor probes, 1 session policy refusal flow); the
baseline log is kept at `~/workspace/a4-staging/
baseline-8727135-tests.log` on the VM.

## 5. Full-suite comparison (worktree /home/james/cu-a4-wt)

- Baseline 8727135 (main checkout, 19:38): 1339 tests, FAILED
  (failures=7, skipped=2), 102.621s. Log kept at
  `~/workspace/a4-staging/baseline-8727135-tests.log` on the VM.
- algo-a4 worktree, run 3 (19:54-19:56): 1402 tests, FAILED
  (failures=7, skipped=2), 105.922s. 1402 = 1339 baseline + 63
  new tests. The 7 failures are byte-identical to the baseline
  set (1 chromium CLI wiring, 5 session-driver doctor probes, 1
  session-policy refusal flow): ZERO new failures, ZERO errors.
- Two earlier worktree runs diagnosed worktree-environment gaps,
  not code: run 1 (1379 tests, 9 failures, 66 errors) lacked the
  gitignored native binaries (`native/wtype` etc.) and generated
  protocol sources (`native/keyboard-protocol.c` etc.); run 2
  (1379 tests, 7 failures, 1 error) still lacked the protocol
  sources, so `test_wtype_native` (23 tests) errored at setUpClass.
  After copying those build artifacts from the main checkout into
  the worktree (ignored files, never committed), run 3 is clean.
  Lesson for other worktree workers: a fresh worktree needs the
  native binaries plus the generated `*-protocol.c/.h` files
  copied over before the suite can pass.

## 6. Live-measure plan (for the live-measure worker, after R3)

1. Use the A4 shape (section 3) for P3 and P4; P1/P2 have no
   file proof, so they keep the verify observe (their A4
   removable call is 0; report that honestly).
2. Same 4 held-out tasks, same timed.py wrapper, fresh broker
   session and fresh lease per task, baseline arm first, then A4
   arm. Per task: wall, think total, think-before-verify-observe,
   model calls, broker service, refusals, misclicks, session
   deaths, program retries, postcondition status per run.
3. Success bar: fewer calls AND lower wall with no rise in
   refusals/misclicks/deaths, and a false-accept rate of 0 (a
   local check that proves the wrong thing is a failed run).
   Expected (estimate from the measured split): about 6.7s think
   plus 1 model call per file-provable task.
4. Also live-test the `verify` CLI once: `CU_CODE_EXEC=1 cu.py
   verify --spec -` with a file_contains spec inside a session,
   and confirm the envelope and the flag-off behavior (disabled
   message, no session started).
5. Do NOT live-measure yet in this round. Broker is single-owner
   and busy with R3; the relay must be restarted after any broker
   code change or it silently runs old code, so the live worker
   restarts the relay when idle before measuring.

## 7. Files changed (branch algo-a4)

- `scripts/postcondition.py` (new, ~430 lines)
- `scripts/procedure_library.py` (new, ~230 lines)
- `scripts/code_exec.py` (77 lines: API, envelope, docs)
- `scripts/cu.py` (80 lines: `verify` subcommand)
- `scripts/session_driver.py` (1 line: relay allowlist)
- `tests/test_postcondition.py` (new, 37 tests)
- `tests/test_procedure_library.py` (new, 19 tests)
- `tests/test_code_exec.py` (+7 VerifyPostconditionTests)
- `improvements/pick1-program-template.md` (A4 shape section)
- `improvements/a3-procedure-library-design.md` (new)
- `improvements/a4-postcondition-verify.md` (this file)
