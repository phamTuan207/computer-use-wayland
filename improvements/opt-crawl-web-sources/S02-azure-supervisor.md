# S2. Azure Scheduler Agent Supervisor pattern

- Class: (a) session and guardian startup failures in agent harnesses
- URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/scheduler-agent-supervisor
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

Three logical actors. The Scheduler records every step state (not started, running, completed) plus a complete-by deadline in a durable state store. The Agent wraps one remote call with its own retry logic inside the complete-by time and passes a stable id across retries for dedup. The Supervisor runs on a schedule, scans the store for steps stuck in running past complete-by, and arranges retry or a compensating transaction. Steps must be idempotent because a retry can run twice. Explicit warning: retry limits at every layer multiply, so one durable end-to-end retry budget must own the total, and retries elsewhere must be disabled or capped inside it.

## Evidence shown

Pattern doc, no measured numbers. The durable-store plus complete-by design is the evidence: a step that times out is indistinguishable from a step that failed, and only the store scan finds it.

## Applicability verdict: APPLIES

This is the closest published shape to our guardian problem. Our guardian should be the Supervisor (periodic scan of a durable step log with complete-by times), not a process that only reacts to crashes. Direct consequences for us: (1) every driver step writes state plus a deadline to a file before it runs, so a dead driver is visible as an expired running step; (2) one retry budget owned by the guardian, driver-level retries disabled or counted inside it, because today our retries can stack; (3) the Supervisor must not restart processes itself (Azure: that belongs to hosting), which means our guardian needs a separate watchdog that restarts the guardian, matching the repo's existing watchdog cron.
