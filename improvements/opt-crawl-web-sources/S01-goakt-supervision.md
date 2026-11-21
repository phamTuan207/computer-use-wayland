# S1. GoAkt supervision docs

- Class: (a) session and guardian startup failures in agent harnesses
- URL: https://docs.goakt.dev/actor/supervision
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:50 +07

## What they did

Actor supervision with explicit strategies (OneForOne: restart only the failing child; OneForAll: restart all siblings), directives (Resume, Restart, Stop, Escalate), a restart budget (max consecutive restarts inside a time window, then suspend instead of restart), and exponential backoff (nth restart waits min(initialDelay shifted by n-1, maxDelay)). Example given: restarts at 200ms, 400ms, 800ms, 1.6s, 3.2s, then the 6th consecutive fault suspends the child; the counter resets after 30s fault-free.

## Evidence shown

Design doc with worked backoff sequence, no measured failure-rate numbers. The numbers are the configured parameters, not benchmark results.

## Applicability verdict: PARTIAL

The pattern maps directly onto our guardian: OneForOne restart of the driver only (not the whole runner), a restart budget (our kill rules need exactly this: a number, not "retry forever"), exponential backoff from 200ms. But GoAkt is a Go actor framework, not a Python browser driver, so the code does not transfer, only the policy shape. Missing piece for us: GoAkt assumes the supervisor itself never dies; our guardian needs the Azure-style split (see S2) where a second watcher watches the watcher.
