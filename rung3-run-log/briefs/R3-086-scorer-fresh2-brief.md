# R3-086 scorer brief, Fresh 2 (Pair B scorer 2, R3-L3, Class S, Tier B)

You are scorer 2 for task R3-086 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-086, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-086-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-086 (Tier B)" plus the
  R3-086 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  command outputs, not live values now): 2 domains in this order:
  1. example.com 2. en.wikipedia.org. Per domain: ping -c 4 (packets sent,
  packets received, loss rate; packets sent expected 4 per domain), DNS
  (returned IP address), curl -L (HTTP status code). Status code 200 for
  both. The IP address must be inside the DNS answer list of each domain
  at run time (as shown in the saved dns file). Loss rate correct as the
  command result at run time. Grading evidence: the 6 timestamped command
  output files (ping, dns, curl per domain) + the report nd06-bao-cao.txt.
  Compare the report against the saved command files line by line.

## Grade

PASS: report has both domains, loss rates match the ping files, IP
addresses inside the DNS answer lists in the dns files, status code 200
for both domains, no item missing, report matches the saved command files.
FAIL: missing domain, wrong loss rate, IP not in the DNS answer list,
status code not 200, report not saved.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-086-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, measured values per domain) and
  ~/workspace/rung3-verdicts/R3-086-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
