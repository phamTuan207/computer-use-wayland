# Actions JSON robustness fix  -  19/11/2026

**Verdict: PROVISIONAL, non-Astra.** Astra 6 is out of credit. The malformed-actions failure is fixed, regression-tested, pushed, and verified against the restarted live relay. `main` stayed frozen.

## Root cause and fix

`read_json()` / `read_json_file()` in `scripts/cu.py:583-601` raise `ValueError` for malformed, empty, or oversized JSON. Before this change, the desktop `act` parser at `scripts/cu.py:2241-2244` let that exception escape. `session_driver.execute()` at `scripts/session_driver.py:30-38` only treats `cu.PreflightRefusal` as recoverable; other exceptions call `stop_session_on_error()`. The continuation rule at `scripts/session_driver.py:137-151` then ends the relay. `scripts/session_remote.py:740-748` treats `session_continues: false` as terminal and marks the task failed.

The same fatal path existed for a11y act and browser act. Each of the three call sites now converts only a `ValueError` from reading the actions input into `PreflightRefusal(str(exc))` (`scripts/cu.py:2243-2244`, `2297-2299`, `2344-2346`). Validation stays outside the catch. `OSError`, including a missing actions file, stays fatal. `validate_actions`, the continuation decision, and the broker code were not changed.

The regression test in `tests/test_session_driver.py:47-110` exercises malformed JSON through real `cu.main()` and `execute()` for desktop, a11y, and browser act; it then sends a valid windows request through `relay_commands()` and confirms the driver continues. A second test confirms a missing file remains fatal. Existing valid act-path tests passed.

The scripted-probe rule was added to `improvements/pick2-executor-brief.md:134-141`: write every JSON file with Python `json.dump`; never use `printf` or shell `echo` for JSON. This is the brief that documents the timed relay request and actions-file flow.

## Pre-change reproduction

Reproduced in-process before editing code. The raw actions bytes contained byte `0a` (a real LF) inside the JSON string. The script exercised actual `cu.main()`, `session_driver.execute()`, and `relay_commands()` while stubbing only compositor/session setup and stop side effects.

- `execute()`: return code 1, `preflight_refusal: false`, output `ok: false` with `Invalid control character at: line 1 column 49 (char 48)`.
- `relay_commands()`: return code 1, `session_continues: false`, `session_ended.reason` equal to the parse error; it did not process the following request.
- Evidence: `/tmp/actions-json-fix-20261119/repro-current.json`. Reproduction script/output timestamps: 12:42:28.387-12:42:28.423 +07.

## Regression suites

Exact command, run from the repository root:

```text
PYTHONPATH=tests:scripts python3 -m unittest -v test_session_remote test_session_driver test_act_diagnostics test_code_exec
```

| Run | Tests by suite | Total | Result |
|---|---|---:|---|
| Immediately before change, 12:43:02.152-12:43:28.930 +07 | remote 53, driver 28, act diagnostics 20, code exec 32 | 133 | 5 failures, 0 errors |
| After change, 12:46:01.883-12:46:28.696 +07 | remote 53, driver 30, act diagnostics 20, code exec 32 | 135 | 5 failures, 0 errors |

The prior envelope-validator report counted 129 before its four `test_session_remote` additions. At this checkout's starting HEAD (`abe1f1d`), those four tests were already present, so the immediate-before run was 133. This fix adds two tests, both passed; targeted run: 2/2, 12:45:48.067-12:45:48.168 +07.

The same five pre-existing `test_session_driver.DoctorCliTests` failed in both suite runs:

- `test_base_exception_from_probe_is_not_converted_to_ime_error`
- `test_first_failure_skips_second_probe`
- `test_long_crlf_probe_error_is_single_line_bounded`
- `test_remote_success_keeps_schema`
- `test_second_probe_failure_after_first_success`

There were no `ERROR` cases. The sorted FAIL/ERROR set diff is empty. SHA-256 of the sorted list (both runs): `9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd`.

## Relay restart and live verification

Restarted `computer-use-relay` at 12:47:57.073-12:47:57.304 +07. The first status call raced socket startup and returned `broker_unavailable`; retry at 12:48:20.074 verified service active, MainPID `128083`, broker idle, driver idle, guardian idle, `next_sequence: 1`, and `started_git_head` exactly `6786c1e95b04c2cda725689ee39b5a39e74950ba` (the new checkout HEAD). The service has no drop-in; its environment contains no `CU_*` variables. No CU variable was set for this fix.

A first scripted harness attempt at 12:51:05.828 started a session but stopped before sending requests: `timed.py` returned `status: starting` while its readiness poll had already reached `running/ready`; the harness had expected the wrong status string. It finished that session cleanly at 12:51:06.878 and the broker was free. The assertion was corrected to check `ready_mono`, and the full probe was rerun with a fresh lease.

Successful live probe, 12:51:30.473-12:51:32.173 +07, via the copied G1 `timed.py` wrapper and relay socket:

1. Started a fresh session; driver reached ready in about 0.82 s.
2. Sequence 1 `windows` succeeded. The only listed window was `omarchy: Jarvis`.
3. Sequence 2 `act` carried the malformed file with the actual newline. Broker accepted the envelope; driver returned code 1 and recoverable result `{ok:false, completed:0, recoverable:true}`, error `Invalid control character at: line 1 column 49 (char 48)`, and next step said no input was sent.
4. Status immediately after the malformed request was `state: running`, `driver: ready`, `next_sequence: 3`.
5. Sequence 3 `windows` succeeded; again only `omarchy: Jarvis` was listed.
6. Finish returned `finished`, driver `stopped`, guardian `clean`. Final broker status had `active_sequence: null`; the broker is free. No GUI window was opened or altered.

Detailed records are in `/tmp/actions-json-fix-20261119/records.jsonl`, `wall-clock.log`, and the `out-*.json` files. Probe lease directories were removed after finishing.

## Commits and final state

- Code and tests: `507e1f35e600cb5ebb08a263db0ab4696dd9436a`  -  pushed; `git ls-remote` matched.
- Documentation: `6786c1e95b04c2cda725689ee39b5a39e74950ba`  -  pushed separately; `git ls-remote` matched.
- Final local and remote `speed-swarm` HEAD: `6786c1e95b04c2cda725689ee39b5a39e74950ba`; working tree clean. `main` was not touched.
- Relay remains active on that HEAD, broker finished/free, driver stopped, guardian clean, and no CU environment flags or drop-ins are present.

## Open

The five unrelated, known-flaky Doctor CLI tests remain failing with the same names before and after. No live-verification blocker remains. The result is provisional and non-Astra as requested.
