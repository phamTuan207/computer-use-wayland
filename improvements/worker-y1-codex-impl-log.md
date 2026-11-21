# Worker Y1 Codex implementation log

## Setup

Elapsed origin is the first setup inspection, approximately 2026-11-21 18:01:43 Asia/Ho_Chi_Minh. The initial setup commands ran before this log could be created inside the required worktree. Their order is exact; timestamps below are reconstructed from the command sequence and are approximate to a few seconds. Later entries are captured at each phase/test.

| Approx local time | Elapsed | Step and result |
| --- | --- | --- |
| 2026-11-21 18:01:43 | +00:00 | Read-only `git status --short --branch` in main checkout. Actual checkout was branch `todolist-push`, not detached HEAD as stated; existing untracked files and `node_modules/` were present. No files changed. |
| 2026-11-21 18:01:45 | +00:02 | Ran `git fetch origin` from main checkout. Updated remote refs, including `origin/todolist-push` from `4500a18` to `70ac187`. No checkout files changed. |
| 2026-11-21 18:01:47 | +00:04 | Added `/home/james/workspace/y1-snippets` with branch `y1-snippets` at `origin/todolist-push` (`70ac187`). All implementation work is confined to this worktree. |
| 2026-11-21 18:01:50 | +00:07 | Ran `python3 scripts/build.py` in the worktree. Success: `pointer`, `indicator`, `modifiers`, and `wtype` built. Compiler emitted unused-parameter warnings in vendored `wtype`; command exit was 0. No binary-copy fallback needed. |
| 2026-11-21 18:02:00 | +00:17 | Configured worktree-local commit identity as `Codex <codex@localhost>` to avoid personal information in commits. |

## Decision log

- 2026-11-21 18:02:00 Asia/Ho_Chi_Minh, elapsed +00:17: The checkout metadata did not match the owner's described detached state, but the requested fetch and worktree creation succeeded from the specified remote branch. Proceed in the isolated worktree and preserve all main checkout files.
- 2026-11-21 18:02:00 Asia/Ho_Chi_Minh, elapsed +00:17: Worktree-local generic commit identity is used for all commits. Push target is restricted to `origin y1-snippets`.

## Phases

Pending.

## Phase A: executor hardening

Started about 2026-11-21 18:07:00 Asia/Ho_Chi_Minh, elapsed about +05:17. Finished 2026-11-21 18:14:30 Asia/Ho_Chi_Minh, elapsed +12:47. Log entry written 2026-11-21 18:15:33 Asia/Ho_Chi_Minh.

Decisions and changes:

- Removed `format` from both safe attribute lists. Regression probes cover the three format-string payloads in both executors.
- Pinned codemode `__builtins__` to a copy of `SAFE_BUILTINS`. A test captures the actual execution namespace and checks it has no builtins module or `eval`.
- Codemode now rejects dunder names, yield/yield-from, async-for, and async-with. It executes at module level, with no `__codemode_main__` function. For compatibility with existing callers and tests that end their code with `return`, only a final top-level return is lowered to an assignment to `result` before compilation. Nested or non-final returns remain invalid module code.
- Both executors bound serialized result envelopes to 65536 bytes. An oversized result returns `result_too_large`; code_exec restores the prior persistent variables instead of saving the oversized result.
- No em dash or en dash characters were added. `git diff --check` passed.
- Setup log commit `87cd34f` (`docs: record Y1 implementation setup`) was pushed to `origin y1-snippets` before Phase A.

Test runs:

| Approx local time | Command | Result |
| --- | --- | --- |
| 2026-11-21 about 18:10 | `python3 -m unittest tests.test_codemode tests.test_code_exec` | 81 tests, OK, 11.591s. Exit 0. |
| 2026-11-21 about 18:10 to 18:12 | `python3 -m unittest discover -s tests -p 'test_*.py'` | First invocation completed, but the exec wrapper did not retain its final output or exit status. It is not counted as evidence. |
| 2026-11-21 18:12:16 to 18:14:19 | `python3 -m unittest discover -s tests -p 'test_*.py'` | 1530 tests, OK, 2 skipped, 123.611s. Exit 0. This is the required Phase A full-suite result. |

Phase A verdict: PASS. Full suite succeeded, so Phase B may proceed. Phase A implementation and this log entry are committed and pushed in the next recorded commit.

## Phase B progress: runner and CLI integration

Started about 2026-11-21 18:15:33 Asia/Ho_Chi_Minh, elapsed about +13:50. Progress checkpoint 2026-11-21 18:39:26 Asia/Ho_Chi_Minh, elapsed +37:43. The registry program files, manifest, and end-to-end registry tests are still being completed; Phase B is not yet complete.

Implemented in this checkpoint:

- Added metadata-only manifest parsing with a 1MB cap, 128-entry cap, duplicate JSON key and duplicate name rejection, per-entry warnings, kebab-case names, path containment, API/op collision checks, parameter schema checks, and text-only source validation.
- Added one-read SHA-256 verification, AST and API-name pre-checks, inline snippet execution, shared API/deadline/trace budgets, call depth 1, frame-local params, one declared output, per-session retry ledger, stale age checks, stale override logging, and observation/DOM binding cleanup.
- Added `--snippet`, `--allow-stale`, and `--approve-snippet` under the existing code-exec gate. The approval flag is required for entries marked `requires_approval`.
- Added `search_snippets` and `describe_snippet`; codemode search places snippets after ops and scores snippet tags only.
- Extended existing fake shell backends to isolate the P3/P4 target paths under test-owned temporary directories.

Verification runs at this checkpoint:

| Approx local time | Command | Result |
| --- | --- | --- |
| 2026-11-21 about 18:38 | `python3 -m py_compile scripts/code_exec.py scripts/codemode.py scripts/cu.py tests/test_snippets.py tests/test_code_exec.py tests/test_codemode.py` | Compile check passed, exit 0. |
| 2026-11-21 about 18:38 | Four targeted registry tests: loop budgets, binding scope, nested-call refusal, approval and applied ledger | 4 tests, OK, 1.078s. Exit 0. |

Phase B pre-change full-suite reference: Phase A result was 1530 tests, OK, 2 skipped, 123.611s, exit 0.

Decisions and deviations under review:

- The API-name pre-check allows names assigned locally in the snippet in addition to safe builtins, API names, and declared params. P1-P4 need local names such as `wins`, `term`, and `verify`; rejecting those `Store` and matching `Load` names would make the required snippets impossible to execute. Unbound loaded names still fail closed.
- The existing code-exec API has no non-raising file-state predicate for checking a target before an action. P3/P4 therefore require approval, clear their fixed task targets first, and assert the resulting state. The session ledger blocks a same-parameter retry. Adding a new file-state API is deferred and recorded as a spec limitation.
