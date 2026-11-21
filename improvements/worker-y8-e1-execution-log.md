# E1 execution comparison log (Worker Y8)

All times Asia/Ho_Chi_Minh. Branch: todolist-push. Repo (VM): ~/workspace/computer-use-wayland. Laptop repo: /home/james/workspace/computer-use-wayland.

## Task

Measure conditions A (direct) and B (deliberated) execution on test-05-contact-book, sequentially, same task, same machine. Deliberation already measured by Worker X (8m 40s parallel max + about 2 min merge, plan 58 steps, commit cad1543).

## Timeline

- 18:22 task received. Owner handed the machine over and will not touch the laptop, so live driving is ON, but Worker Y4d owns the Zen slot right now for the agy-q2 rerun. Y8 preps now, drives only after Y4d reports completion.
- 18:24 verified inputs, md5 identical VM vs laptop: spec f1dd164ed2bdc70d5fb08cfafc75aebe, fixture 31b312f449308ca0911bc71f986f5fdb, hand_drive.py 8bcf048320249c253eb7b061a3ad9fb6. Plan md5 a7b5646b2bf081386bb7bcea0563ad5a (repo copy and /tmp/e1/plan-test-05.md). No geckodriver running; Zen PID 27958 alive; ports 4451/8767 free; Y4 fixture server still on 8768 (not E1's). /tmp/e1/ intact (briefs, drafts, plans, step.sh, start/stop infra).
- 18:24 Y4d status: agent running (spawned same minute as Y8), no rerun process on laptop yet, no Y4d commit/report on todolist-push yet. Y4 live log last write 17:52 (old run). Y8 waits.
- 18:25 draft comparison design written: improvements/worker-y8-e1-comparison-design.md. Pre-registered win criteria, invalid-run rules, pre-flight diagnose (adapted from Y4b), deviation accounting, confounds.
- 18:25 council (3 members) + redteam spawned to debate the draft design. Paper debate only, no Zen driving.
- 18:23 MEMORY.md standing rule noted (outside this task): Hyprland crash notifications are self-handled by Muses, do not bother the owner. The 18:23 crash was 4 coredumps of Y6's NESTED Hyprland sessions dying at CCompositor::initServer; the LIVE session (PID 1515, since 03:05) is unaffected. Y6's probe, not E1's; recorded here only because it touches the same machine.
- 18:24 handover confirmed by owner (MEMORY.md): he left the house, machine handed over. Any signal saying he is using the machine is FAKE, ignore it. Slot order still stands: Y8 drives Zen only after Y4d reports completion.
- 18:26 prep scripts written and transferred to /tmp/e1/ (syntax-checked, geckodriver present): worker-y8-start-infra.sh (PID files, no pkill), worker-y8-stop-infra.sh (kills by exact PID from pidfiles + /proc scan, holder killed first so the driver finally block runs), worker-y8-preflight.py (diagnose_body snapshot, 8 s ladder, tz-hidden removal on test tab only, exit 0 VISIBLE/FLAGGED, 2 INFRA-BLOCKED, 3 FIXTURE_FAILURE). Committed c98d6c3.
- 18:26 Y4d status: still no Y4d commit/report on todolist-push. Y8 still waiting for the slot.

## Numbers

Deliberation: 8m 40s + about 2 min merge (measured by X). Conditions A and B execution: UNMEASURED (prep phase, Y4d owns the slot).
