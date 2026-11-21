# S3. DCC-MCP-Core gateway guardian

- Class: (a) session and guardian startup failures in agent harnesses
- URL: https://dcc-mcp.github.io/dcc-mcp-core/guide/gateway
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

A three-layer daemon setup on one workstation. On startup, a single-flight lock file (gateway-launch.lock) guarantees N concurrent launches spawn at most one gateway process. A guardian watchdog in each backend probes /health every 5s (probe timeout 0.5s); after 2 consecutive misses it re-runs the daemon ensure path under the same lock and restarts the daemon. A stale lock is reclaimable after 30s. A terminal host-died envelope triggers immediate deregistration, no waiting for heartbeat.

## Evidence shown

Concrete parameters (5s probe, 0.5s timeout, 2 misses, 30s stale lock, 300s idle timeout for auto-ensure), no measured uptime numbers.

## Applicability verdict: APPLIES

This is the most directly copyable guardian design of the three: probe interval, miss count, single-flight lock, stale-lock reclaim. Our Marionette/BiDi guardian can copy the numbers as a starting point (probe every 5s, restart after 2 missed health checks, lock file so two runners never spawn two drivers). Note the lock solves a failure mode we have: two live runners racing to start one driver. The 0.5s probe timeout is a warning too: our Marionette socket can stall longer than 0.5s under load, so a too-tight timeout would restart a healthy driver.
