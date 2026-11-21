# Realistic tests by clone2, batch 2

Ten realistic agent tasks, each self contained, offline, timed,
with an automatic checker. Each test builds its own fixture in a
fresh temp folder, performs the task with real file, process and
terminal operations, then verifies the outcome independently.
Nothing here needs a display, a browser, or the network, so the
suite runs anywhere, including a headless VM. Timings are wall
clock plus monotonic elapsed, per phase and per test, and the
runner reports a suite total.

Run everything:

    python3 tests/realistic_clone2/run_all.py --out /tmp/suite-results.json

Run one test:

    python3 tests/realistic_clone2/test01_fix_buggy_module.py

| Test | Topic | Task in one line | Pass condition |
| --- | --- | --- | --- |
| test01 | code editing | fix a buggy pricing module | its unit tests pass, test file untouched |
| test02 | code editing | rename a function across 5 files plus README | no stale references, same program output |
| test03 | file management | organize 30 messy files by written rules | exact ruled tree, all content hashes intact |
| test04 | file management | bulk rename to slugs with a collision | no overwrite, both collision files survive |
| test05 | terminal and editor | reconfigure an app through shell tools | the app own checker prints the expected settings |
| test06 | terminal and editor | make a broken build green | build exits 0, bundle prints the expected line |
| test07 | error handling | finish a batch job that dies halfway | 9 good outputs, 1 reported failure, rerun is a noop |
| test08 | error handling | repair a corrupt CSV with an audit | clean and rejects match ground truth, nothing dropped silently |
| test09 | reading documentation | implement a library from SPEC.md | every documented example and edge case passes |
| test10 | data work | diff two catalog versions into a report | report deep equals the independent expectation |

Measured suite results from the clone2 machine are recorded in
coord/clone2.md under the batch 2 status, and the runner JSON is
the raw evidence behind them.
