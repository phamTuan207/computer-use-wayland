# A5 fallback drill (post-migration): one-shot SSH recovery after the broker send migrate

Status: PREPARED ONLY, NOT RUN. Prepared by worker B2-4, 2026-11-23
00:16 +07, worktree HEAD ed4fcd4 (migrate of
scripts/s2_flip_live.py to the broker client, plus the B2-4 fix
round, committed as one fix commit). This drill needs an
explicit GO from Muse tong before any live step runs. No live run,
no browser work, no SSH was done while writing this file. No em
dash or en dash anywhere in this file. No personal info.

## 0. What this drill proves

The A5 gate item 3 (prep log section 5.3): after the S2 flip
class migrates off oneshot_code_exec, the fallback that A5
explicitly keeps still works. With the broker stopped, a one-shot
SSH send completes a code-exec send, then a one-shot SSH restart
of the relay brings the broker back, a fresh lease starts a
batch, and the batch completes. This is the step 8 fallback drill
(step 8 log section 6.2, passed on the second attempt) repeated
on the post-migration code. Step 3 does NOT run the harness:
run() always calls broker_start first, so with the relay stopped
it raises before any send and writes no run JSON. Step 3 uses a
standalone script that calls the one-shot JSONL path directly,
exactly like the step 8 drill script
(~/workspace/c5-step8-run/fallback-drill.py): seed a scratch
tab, pre-count, send the act envelope then the finish line over
mux-wrapper SSH, V12, delayed count. Steps 1 and 5 run the harness
with --chromium-set-value, so Chromium uses set_value and the
pre-count and delayed count exist (a fill run has neither).

## 1. Preconditions (all checked before step 2, any miss aborts)

1. The migrate is in the worktree: scripts/s2_flip_live.py has
   broker_code_exec, _code_exec_send, and the --transport flag.
   Check on the VM: `git -C ~/workspace/mochi-b2-4-work log
   --oneline -1` shows the B2-4 fix commit, and `grep -c
   "def broker_code_exec" scripts/s2_flip_live.py` prints 1.
2. The laptop tree is synced to the same code (the drill is
   meaningless on a stale laptop tree; step 8 spec condition 1
   applies here too). Check the relay head with broker status
   and compare it to the VM HEAD ed4fcd4.
3. The relay env carries CU_CODE_EXEC=1 (drop-in flags.conf,
   coord-click-6 F3). A broker send that returns the disabled
   envelope fails this drill at the broker-send step, not at
   the fallback step. Verify with the broker send in step 1
   itself; there is no separate flag probe.
4. A scratch target exists in Zen on ws1, or the owner hands
   over a scratch tab. NEVER use the owner's live tabs. The
   step 9 live runs used the ws2 clone chats; this drill uses
   a scratch tab with a fake composer, like the harness
   --dry-run seed, so no message lands in a real thread.
5. No live owner session is running (broker status state idle,
   owner null). One runner live at a time (gate G-SINGLE-LIVE).
6. The pill is held for the whole drill (W-PILLCDP, rule 4.29):
   every live action goes through a computer-use session so
   the pill shows. Steps 1 and 5 hold the pill through the
   harness (cdp_pill_hold, agent S2-flip). Step 3 has no
   harness, so no cdp_pill_hold runs there; its one-shot
   session-driver shows the pill through its own guardian
   (the guardian creates the indicator server that shows the
   session pill label), the same shape as the step 8 drill.

## 2. Procedure

All commands run on the VM unless marked laptop. SSH uses the
S0 mux wrapper through the harness; the relay restart uses the
repo mux wrapper scripts/ssh-laptop-mux.sh, the S0 drop-in for
~/workspace/ssh-laptop.sh, which does not exist in this VM.

Step 1, baseline broker send (proves the migrate before the
fallback is tested). Run the harness in dry-run mode against
the scratch target with the default transport:

`python3 scripts/s2_flip_live.py --run 900 --dry-run --browser chromium --chromium-set-value --workdir improvements/mochi-b2-4-fallback-drill`

Record: run JSON transport field is `broker`, each send's
`program.transport` is `broker`, outcome `sent`, V12 found,
pre-count 0, delayed count 1. The --chromium-set-value flag is
what makes the pre-count and the delayed count exist: with
default fill, Chromium has neither (fill has no pre_count and
is not in delayed_targets). If any send shows transport
`broker-fallback-oneshot`, the broker refused the request and
the drill has already proven the fallback path, but the
baseline is NOT a clean broker proof: stop, record it, and
ask the coordinator whether to continue.

Step 2, stop the relay. Over mux SSH to the laptop:

`scripts/ssh-laptop-mux.sh "systemctl --user stop computer-use-relay.service"`

Verify the broker is down from the VM with the exact status
call:

`scripts/ssh-laptop-mux.sh "python3 /home/james/computer-use-wayland/scripts/session_remote.py status"`

It must answer `{"ok": false, "error": "broker_unavailable"}`
with rc 1. Record the time.

Step 3, one-shot fallback send, standalone script (NO harness).
The harness cannot run this step: run() always calls
broker_start first, so with the relay stopped it raises
`broker start failed ... broker_unavailable` before any send
and writes no run JSON, and --transport oneshot does not help
because oneshot only changes the send transport, not the
run-level broker_start. So this step runs the standalone
script below, in the step 8 shape: mux-wrapper SSH
(scripts/ssh-laptop-mux.sh) throughout, seed a scratch tab,
pre-count, send the act envelope then the finish line as two
JSONL lines on the stdin of the one-shot session-driver,
V12, sleep 10s, delayed count. The send program is the same
set_value program the harness builds for Chromium with
--chromium-set-value, imported from scripts/s2_flip_live.py,
so the program shape is identical to step 1. The message is
new (run 901 family, never reuse the step 1 message; a retry
must use a new run number, CB-2 rule). No separate observe
step runs before the send, so the step 8 stale-workspace
failure (observe on ws1, act on ws2) cannot happen here: the
program grounds the composer from its own fresh DOM snapshot
inside the driver session.

Save the script as /tmp/a5-drill-step3.py on the VM and run
`python3 /tmp/a5-drill-step3.py`. It exits 0 only when every
check passes, and prints one JSON summary line.

```
#!/usr/bin/env python3
"""A5 drill step 3: one-shot send with the relay stopped.

Standalone, step 8 shape. No harness, no broker, mux-wrapper
SSH only (scripts/ssh-laptop-mux.sh, the S0 drop-in for
~/workspace/ssh-laptop.sh, which does not exist in this VM;
a dead mux master costs one slow fresh connect and self-heals).
"""
import json
import subprocess
import sys
import time

sys.path.insert(0, '/home/hatch/workspace/mochi-b2-4-work/scripts')
import s2_flip_live

SSH = ['/home/hatch/workspace/mochi-b2-4-work/scripts/ssh-laptop-mux.sh']
CU = '/home/james/computer-use-wayland/scripts/cu.py'
ENDPOINT = 'http://127.0.0.1:9223'
MESSAGE = 'A5-DRILL-R901-CHROMIUM-IGNORE-TEST'


def ssh(remote):
    proc = subprocess.run(SSH + [remote], capture_output=True,
                          text=True, timeout=120)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    rc, out, err = ssh('node /tmp/s2-seed.mjs %s' % ENDPOINT)
    tab = out.strip().splitlines()[-1].strip()
    assert rc == 0 and tab, 'seed failed rc=%d %s' % (rc, err[:200])
    rc, out, err = ssh("node /tmp/c5-count.mjs %s %s '%s'"
                       % (ENDPOINT, tab, MESSAGE))
    pre = json.loads(out.strip().splitlines()[-1])
    assert pre.get('count') == 0, 'pre-count not 0: %s' % pre
    program = s2_flip_live.build_program_set_value(tab, MESSAGE)
    act = {'args': ['code-exec', '--endpoint', ENDPOINT,
                    '--program', '-', '--intent', 'A5 drill step 3'],
           'stdin': program, 'image_policy': 'auto'}
    lines = json.dumps(act, ensure_ascii=False) + '\n' \
        + json.dumps({'args': ['finish']}) + '\n'
    remote = ('CU_CODE_EXEC=1 python3 %s session -- python3 %s '
              'session-driver' % (CU, CU))
    proc = subprocess.run(SSH + [remote], input=lines,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, \
        'one-shot rc=%d %s' % (proc.returncode, proc.stderr[:300])
    envelope = None
    for raw in proc.stdout.splitlines():
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if isinstance(obj, dict) and 'result' in obj:
            envelope = obj['result']
    assert envelope is not None, 'no driver result in one-shot output'
    assert envelope.get('ok') is True, 'envelope not ok: %s' % envelope
    rc, out, err = ssh("node /tmp/s2-v12.mjs %s %s '%s' 10000"
                       % (ENDPOINT, tab, MESSAGE))
    v12 = json.loads(out.strip().splitlines()[-1])
    assert v12.get('found') is True, 'V12 did not find message: %s' % v12
    time.sleep(10)
    rc, out, err = ssh("node /tmp/c5-count.mjs %s %s '%s'"
                       % (ENDPOINT, tab, MESSAGE))
    delayed = json.loads(out.strip().splitlines()[-1])
    assert delayed.get('count') == 1, \
        'delayed count not 1: %s' % delayed
    print(json.dumps({'step': 3, 'transport': 'oneshot-standalone',
                      'tab': tab, 'pre_count': pre,
                      'envelope_ok': True, 'v12_found': True,
                      'delayed_count': delayed}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

Record: the script exit code is 0 and its JSON summary shows
transport `oneshot-standalone`, pre-count 0, envelope ok,
V12 found, delayed count 1. There is NO run JSON for step 3:
no harness ran, so no run-901 JSON exists, and that is
expected, not a missing file.

Step 4, restart the relay. Over mux SSH to the laptop:

`scripts/ssh-laptop-mux.sh "systemctl --user restart computer-use-relay.service"`

Verify: service active, new PID, broker status shows state
idle, owner null, generation changed (a restart invalidates
every lease with broker_changed, so the step 1 lease is dead
by design). Record the new generation and PID. The broker
status call is the same command as step 2, and the service
state call is `scripts/ssh-laptop-mux.sh "systemctl --user show computer-use-relay.service -p ActiveState -p MainPID"`.

Step 5, broker works again. Fresh lease, fresh batch:

`python3 scripts/s2_flip_live.py --run 902 --dry-run --browser chromium --chromium-set-value --workdir improvements/mochi-b2-4-fallback-drill`

Record: broker start ok with the new generation, outcome
`sent`, transport `broker`, pre-count 0, delayed count 1.
Broker finish cleanliness is read from broker status AFTER
the run (state finished, guardian clean, error null), not
from the run JSON: run() ignores the broker_finish return
value, so the run JSON has no broker_finish field.

Step 6, cleanup check. Over mux SSH to the laptop:

`scripts/ssh-laptop-mux.sh "python3 /home/james/computer-use-wayland/scripts/session_cleanup.py --check"`

It must exit 0 afterwards: no snapshot, no indicator socket,
no stop markers, no overlay holders, no guardian process.

## 3. Pass criteria (all must hold)

1. Step 1 broker send: transport `broker`, outcome `sent`,
   V12 found, pre-count 0, delayed count 1.
2. Step 3 one-shot send with the broker dead: the standalone
   script exits 0, its JSON summary shows transport
   `oneshot-standalone`, pre-count 0, V12 found, delayed
   count 1. There is no run-901 JSON, by design.
3. Step 4 relay restart: service active, broker status idle,
   generation changed, new PID recorded.
4. Step 5 broker batch on a fresh lease: transport `broker`,
   outcome `sent`, pre-count 0, delayed count 1, broker
   status after the run shows state finished, guardian clean,
   error null.
5. Step 6 session_cleanup.py --check exits 0.
6. No message appears twice: every delayed count is exactly 1.

## 4. Abort and failure rules

- If the step 1 broker send returns the disabled envelope
  (relay lacks CU_CODE_EXEC=1), STOP. Do not fall back
  automatically: the harness refuses the automatic fallback
  for a disabled envelope by design. Fix the relay flag
  first (drop-in plus restart, coord-click-6 F3 procedure),
  then restart the drill from step 1.
- If a send outcome is `failed-unverified` or `error` with an
  unknown broker result, STOP. Do NOT retry the same message
  with the one-shot path: the outcome is unknown and a retry
  could double-send. Determine the count of the original
  message first (V12 count check): 0 means never sent, safe
  to retry with a NEW run number; 1 means already sent, mark
  already-sent and do not retry.
- If the relay does not come back in step 4, STOP with the
  broker down and report to the coordinator. Do not start
  another live batch. The one-shot path from step 3 stays
  available as the recovery path, but no further sends run
  until the coordinator decides.
- If step 6 fails (leftover snapshot, holder, or guardian),
  STOP and run the recovery procedure (session_cleanup.py
  --clean for the safe parts, then `computer-use recover` if
  a snapshot is retained). No new live run until --check
  exits 0.

## 5. Evidence to collect

- The two run JSONs (runs 900, 902) in
  improvements/mochi-b2-4-fallback-drill/, with the transport
  field and per-send program.transport visible, plus the
  step 3 script JSON summary line (there is no run-901 JSON).
  The run JSONs have no broker_finish field: run() ignores
  the broker_finish return value, so finish cleanliness is
  evidenced by broker status after the run, not by the JSON.
- The broker status outputs before step 2, after step 4, and
  after step 5 (generation, state, owner, driver, guardian,
  recovery, error).
- The relay PID before and after the restart, and the
  session_cleanup.py --check output.
- Times in Asia/Ho_Chi_Minh plus elapsed per step, and the
  commit hash of the code under test.

## 6. What this drill does NOT prove

- It does not prove the live clone-chat send (that is the
  step 9 live proof, already landed for the (b1) program).
- It does not prove the wedge drill (separate file,
  improvements/mochi-b2-4-a3-wedge-drill.md).
- It does not prove the driver holds scope plus cancel latch
  plus lock (A3 gate, B4 lift). That is a separate live run.
