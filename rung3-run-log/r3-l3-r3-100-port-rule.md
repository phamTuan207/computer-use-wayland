R3-100 port check rule (precondition 21).
Written 2026-11-24 17:38 +07 by the Phase 0 coordinator.

R3-100 (position 55, Codex, the LAST task) checks that a port is free / a
service state, and saves an HTML page. The task reads live port state on the
laptop. The port state is transient (a port can be in use by a leftover
process from an earlier task, or free). The rule below makes the check
deterministic.

RULE:
- Before R3-100 starts, the coordinator verifies no leftover process from
  the run is listening on the port R3-100 checks. The coordinator lists
  listening ports (ss -tlnp) and confirms the target port is in the state
  the key expects (free, or occupied by the expected service, per the key).
  If a leftover process from an earlier task holds the port, the coordinator
  kills it (it is a leftover, not part of R3-100) and re-verifies before
  starting R3-100.
- The runner records the port state at run time (the ss output and the saved
  HTML) and copies both into the evidence folder. The port state is recorded
  at run time, not reconstructed later (a later check would see a different
  state).
- The scorer grades from the snapshot (the saved ss output + HTML). It does
  NOT re-check the live port (the live state will have changed by scoring
  time). R3-100 is Class S for this reason.
- If the port is in an unexpected state at task start (held by an unrelated
  process that is not a run leftover and cannot be killed, e.g. a system
  service), the coordinator stops and reports to the owner before starting
  R3-100. Do not run R3-100 on a port whose state cannot be made to match
  the key.
- After R3-100, the run is complete. The coordinator does a final ledger
  validation, pushes, and reports the final tally (PASS/FAIL/INVALID counts
  against the 53/55 bar).

PORT TO CHECK: the key names the port. The coordinator reads the port number
from the frozen key (docs/rung3-answer-keys.md, R3-100 section) at run time
and uses that number. This file does not hard-code the port number (the key
is the source of truth).
