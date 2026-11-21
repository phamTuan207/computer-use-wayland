# Verify last30days ef01dab on this machine, 2026-11-22

## Verdict

The installed commit IS ef01dab. Version 4.5.0. No discrepancy in the install.
The test suite is not green on this machine: 5 failed out of 9,953, and all 5
failures trace to this environment (sandbox UDP block, root user), not to the
skill code. See below.

## Identity

- Clone: ~/workspace/tools/last30days-skill, installed by git clone only, no
  installer run.
- HEAD: ef01dab92d8ef0da673b18e7f90d69fde77c495b
- Date: 2026-11-21 12:22:38 -0800
- Subject: feat(tiktok): free top comments for every kept TikTok from the
  public comment endpoint (#1555)
- Remote: https://github.com/mvanhorn/last30days-skill
- Working tree: clean, no local modifications.
- Version: skills/last30days/SKILL.md line 3, version "4.5.0";
  pyproject.toml version 4.5.0, requires-python >=3.12, dependencies = [].
- Diff vs the reviewed f5d0e44: 7 files, +238/-7 (CONFIGURATION.md,
  changelog.d/+tiktok-public-comments.added.md, skills/last30days/scripts/lib/
  env.py, lib/pipeline.py, lib/tiktok.py, tests/test_pipeline_v3.py,
  tests/test_tiktok.py). Matches the batch 8 install report exactly.

## Test suite

- Runner: Python 3.12.3, pytest 9.2.0, pyyaml 6.0.4, installed from PyPI
  into a scratch venv /tmp/l30-venv (no pytest existed on this machine
  before). The skill's dev deps pytest-cov, pytest-xdist and towncrier were
  NOT installed, so the coverage gate (fail_under 81 in pyproject.toml) was
  not evaluated.
- Collection: 372 test files, 9,953 tests, 0 collection errors.
- Run: 2026-11-21T23:13:14Z to 23:18:48Z, 331.75 s (0:05:31).
- Result: 5 failed, 9929 passed, 19 skipped, 93 warnings, 292 subtests
  passed. Exit code 1. Full log: /tmp/l30-run.log (kept on this machine
  only, not in the repo).

## The 5 failures

Four are in tests/test_network_guard.py, all the same cause:

- test_localhost_bind_preserves_real_owned_transport[SOCK_DGRAM]
- test_owned_udp_transport_remains_real[sendto]
- test_owned_udp_transport_remains_real[sendmsg]
- test_guard_restores_every_patched_socket_function

Each spawns a probe subprocess that does a real localhost UDP sendto or
sendmsg, and each gets PermissionError: [Errno 1] Operation not permitted
from tests/network_guard.py:125 (sendto) or :130 (sendmsg). The sandbox on
this VM blocks UDP socket operations, so the real UDP send is refused by
the environment. The guard code under test is not at fault.

The fifth is tests/test_setup_wizard.py::TestWriteApiKey::
test_unwritable_target_returns_false. It creates a directory with chmod
0o500 and expects write_api_key to return False. This VM runs as root
(uid=0, verified with id), and root bypasses file permission bits, so the
write succeeds and returns True. Environment artifact, not a skill defect.

## Warnings

93 warnings, mostly one DeprecationWarning in
skills/last30days/scripts/store.py:1175 (sqlite3 named parameter binding
supplied as a sequence; becomes a ProgrammingError in Python 3.14).

## Discrepancies

- None in the install: commit, version and diff all match ef01dab.
- Test result is not green here, but every failure is environment-caused.
  Re-running as a non-root user on a machine that permits localhost UDP
  would be the check that confirms this; not done here.
