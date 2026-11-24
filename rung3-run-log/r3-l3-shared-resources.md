R3-L3 shared-resource table and pause rule (precondition 15).
Written 2026-11-24 17:32 +07 by the Phase 0 coordinator.

SHARED RESOURCES (two runners + two scorer pairs + coordinator all use these;
only one user at a time, or a rate limit is shared):

1. Laptop session (the single driver slot, cursor.lock).
   - Owner: whoever holds it (one runner at a time). The other runner waits.
   - Rule: the coordinator grants the slot to one runner per task. The runner
     releases it by finishing the task and the coordinator confirming the
     snapshot. The /proc fd scan (see r3-l3-interleaving-rule.md) proves it
     is free. Never two drivers at once.
2. ecommerce-playground.lambdatest.io (R3-029).
   - Shared by: the R3-029 runner only (one task). The test account is
     rung3-029-test@example.com. Only one login at a time; if the session
     expires, log in again (Mochi verified this during prep).
   - Rate limit: none observed. If the store returns 429, pause 5 minutes.
3. Wayback Machine / web.archive.org (R3-003, R3-040, R3-042).
   - Shared by: the B-hybrid tasks (R3-003, R3-040, R3-042) and the R3-L2
     retry evidence. Wayback returns 429 under load.
   - Rate limit: Wayback 429 is common. If any runner hits a Wayback 429,
     it waits 60 seconds and retries once. If it hits 429 twice, it uses the
     CDX API or moves on and reports BLOCKED honestly (do not fabricate).
   - Only one B-hybrid task runs at a time (they are sequential in the run
     order anyway), so no concurrent Wayback load from our side.
4. Google Docs (R3-003, R3-004, R3-036, R3-040, R3-042).
   - Shared by: the online-doc tasks. Each task creates its own doc. No
     shared doc. No rate limit observed.
5. WAVE (wave.webaim.org, R3-009).
   - Shared by: the R3-009 runner and the pre-run WAVE gate (already done).
   - Rate limit: none observed. WAVE loads live pages; if it is slow, wait.
6. Browser session (Zen / Chromium / Brave on the laptop).
   - Shared by: the runner driving the browser and the scorer (Mochi) who
     uses Chromium. The runner and Mochi do not drive the same browser at
     the same time. Mochi uses her own Chromium tab (A67A718D...); the runner
     uses Zen. Do not close or navigate any tab the owner opened.
7. GitHub (repo todolist-push, run-log commits).
   - Shared by: the coordinator (ledger pushes, state updates) and any
     scorer who writes a note (via PR, not direct push). The coordinator is
     the only one who pushes to todolist-push during the run. Scorers do not
     push. Rate limit: GitHub allows many pushes; the coordinator pushes at
     least hourly and immediately on INVALID/dispute.
8. Speed daemon (Messenger to Mei/Mochi).
   - Shared by: the coordinator (messages to Mochi) and the watchdog. One
     message at a time (send.py is serial; never concurrent sends). The
     daemon died once during prep (restarted 17:16:43 +07, PID 2423). If
     send.py fails with ConnectionRefused, restart the daemon (daemon.sh
     restart) and retry once. If it fails again, use the fallback channel
     (see r3-l3-daemon-fallback.md).
9. Laptop disk (~/rung3, ~/rung3-chung-cu, snapshots).
   - 228G free at prep. Each task uses a few MB. No disk pressure expected.
   - If disk falls below 10G free, the coordinator pauses the run and
     reports to the owner (do not delete evidence to free space).
10. Codex rate limit (gpt-6-luna).
    - The Codex runner uses gpt-6-luna. Rate limit was 100 percent at
      10:34 23/11, resets Sat 2026-12-12 19:17 +07. The run is well inside
      the limit. If Codex returns a rate-limit error, the coordinator pauses
      the Codex lane and reports to the owner.

PAUSE RULE (429 / bot check / rate limit):
- If ANY runner or scorer hits a 429, a bot check, or a rate-limit error on a
  shared resource, it STOPS using that resource immediately and tells the
  coordinator.
- The coordinator pauses ONLY the affected task/lane, not the whole run,
  unless the resource is the laptop session (then the whole run pauses).
- The coordinator waits 10 minutes, then lets the affected runner retry once.
- If the 429/bot check persists after the retry, the coordinator records the
  task as BLOCKED in the state file, grades it from the evidence that exists
  (FAIL if incomplete, INVALID only if the site itself is down for everyone
  and the key's invalid condition is met), and moves to the next task.
- A 429 or bot check is NEVER a reason to fabricate evidence or to mark a
  task INVALID without proof the site is down for everyone (curl 403 alone
  is never sufficient, per the R3-011 ruling).
- If BOTH runners hit 429s on the same resource within 30 minutes, the
  coordinator pauses the whole run for 30 minutes and reports to the owner.
