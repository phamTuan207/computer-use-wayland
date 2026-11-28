# Pilot 3 build record: machine-layer RDP lock wiring (2026-11-28)

Decision authority: improvements/pilot-first-decisions-20261128.md,
Pilot 3 section (BUILD-SCOPED, machine layer only). Council-risk
conditions 1-6 all applied. Machine-layer changes are not in git;
this record is the audit trail. Concrete machine paths stay on the
laptop; this record uses generic home-relative forms only.

## The gap (before)

rdp_client.py supports the single-drive flock via --lock-file or
the RDP_LOCK_FILE env var (fail-fast, envelope lock_held), and
LOCK-MAP.md plus the zen-rdp README require the machine-layer
wrapper for owner drives to set it. No wrapper did: drives called
the machine copy of rdp_client.py directly, the env var was set
nowhere on the laptop, and no choke point existed. The RT-23
single-drive fence was fictional for owner drives.

## What was wired (laptop machine layer only)

New files under ~/.config/agent-computer-use/machine/:

- bin/rdp-drive (executable): the choke point. Parses --port,
  sets RDP_LOCK_FILE to the per-port lock unless --lock-file or
  the env var is already set, then execs rdp_client.py with the
  original args. --no-lock is a logged opt-out for throwaway
  probes on dedicated ports only; it is refused on the owner
  channel (port 6021).
- bin/rdp-lock-path.sh: prints the per-port lock path
  (locks/rdp-<port>.lock), creating the locks dir. The one place
  allowed to create it.
- bin/rdp-lock-env.sh: sourceable snippet for library callers
  (probes importing RDPClient) that do not go through rdp-drive;
  sets RDP_LOCK_FILE from RDP_PORT.
- locks/README.md: lock semantics, stale-file rule (never unlink;
  kernel releases on exit), and the watchdog decision below.

Edited files (timestamped backups taken first, suffix
.bak.20261128-104407):

- bin/machine-preflight.sh: new read-only lock report section.
  Reports each known per-port lock as free or HELD (holder record
  shown) by a non-blocking flock try on a throwaway fd; changes
  nothing. Prints the choke-point reminder.
- PLAYBOOK.md: new section 7, RDP drives and the single-drive
  lock choke point (wrapper rule, library rule, watchdog
  decision summary, opt-out, owner-channel and dedicated
  recipes). Old section 7 renumbered to 8.

All six files byte-verified VM-to-laptop by sha256 after install.
rdp_client.py is unchanged and stays opt-in (council condition 1).
No repo code change. No repo doc correction needed: LOCK-MAP.md
and the zen-rdp README already state the wrapper requirement in
generic terms; the requirement is now true, so no PR rides.

## Watchdog / smoke decision (made before wiring)

Read-only checks are EXEMPT from the lock; drives are fenced.

- rdp_smoke.py constructs RDPClient without a lock argument and
  would inherit RDP_LOCK_FILE from a dirty environment. Rule:
  run smoke with the variable unset (env -u RDP_LOCK_FILE).
  Smoke must never be refused by a drive lock, and must never run
  while a drive is in progress (existing drill order). If a check
  ever meets lock_held, a drive is in progress on that port:
  stop, do not retry around it.
- Watchdog, screen checks, and machine-preflight.sh never take
  the lock. Preflight only reports held locks.
- Read-only library probes follow the smoke rule (unset);
  probes that navigate, act, open, or close follow the drive
  rule (lock).

Rationale: the fence stops two drives interleaving on one
session (the 2026-11-21 incident class). Refusing a read-only
gate adds no safety and would break the update drill, where
smoke must pass before drives resume.

## Live two-client refusal test (dedicated session, port 9331)

Harness: dedicated Zen via launch_dedicated.py on port 9331;
client A (separate process) held the lock through the new wiring
(RDP_LOCK_FILE from rdp-lock-path.sh) and attached; client B ran
through rdp-drive. Owner Zen (pid 807599, port 6021) verified
alive before and after; untouched throughout.

- CLI refusal via rdp-drive, 3 reps: 76.5 / 72.1 / 65.1 ms wall,
  exit 1 every rep, envelope code lock_held, message names the
  holder pid (process alive) and the single-drive fence. The
  ~70 ms floor is Python startup, not the lock.
- Library refusal, 5 reps: 0.159 / 0.084 / 0.059 / 0.054 /
  0.053 ms (median 0.059 ms), all LOCK REFUSED. Refusal precedes
  any socket connect.
- After client A released: rdp-drive eval succeeds, exit 0,
  72.1 ms, result 2.
- Stale record: lock file overwritten with a dead-pid holder
  record; next acquire succeeds in 0.945 ms, evaluate returns 2.
  No wedge.
- Post-test preflight: rdp-9331.lock reported free. Dedicated
  session stopped by recorded pid immediately at test end;
  throwaway profile and harness files removed. Lock file left in
  place per the never-unlink rule.

First harness attempt failed before the test proper (holder
output handling bug in the harness, traceback lost); the
dedicated session from that attempt was stopped by recorded pid
at once and the owner session verified alive. The numbers above
are from the corrected harness, full run, result ok.

## Reopen condition

lock_held appearing in a real drive report means the fence is
working; log it, do not treat it as a defect. Contention
question reopens only on a real-drive lock_held or a recorded
concurrent-drive incident.
