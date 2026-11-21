# Tracked item: Transparent Zen 0.9.4 hides new-tab bodies (hidden-body defect)

- Status: OPEN, decision owed by the owner
- Opened: 2026-11-21, by Worker Y4d (created as the pairing the Y4b fix design requires)
- Owner: Muse (coordinator); the decision is the owner's, not the runner's

## The defect

Transparent Zen 0.9.4, installed in the live Zen profile, injects a
content script at `document_start` on every page. It adds class
`tz-hidden` to `<html>`; its CSS then sets `body { visibility: hidden;
opacity: 0 }`. Removal is async (fetch of `data/ContentScripts.json`,
then `browser.storage.local.get`, then branch paths) with no timeout
or fallback. When that chain stalls, every new tab opens blank for
minutes. A real user opening a new tab during such a window sees a
blank page. Two incidents: 2026-11-21 16:36-16:44 and 17:52-17:59 +07.

Evidence: `improvements/worker-y4b-hidden-body-root-cause.md`
(mechanism proven by code; V1 badly wounded but not dead, V2 dead,
third mechanism possible if the "no class" record is accurate),
`improvements/worker-y4b-evidence-pack.md`.

## Why this file exists

The Y4b fix design allows the runner to remove `tz-hidden` on a test
tab as a recovery step ONLY paired with a tracked item to fix or
disable the extension. Removing the class masks a real user-facing
defect, so a test that passes after removal is a FLAGGED pass, counted
separately, never folded into the headline pass count. Without this
item, the removal step is unapproved masking, not legitimate recovery.

## Decision owed (pick one)

1. Blacklist `127.0.0.1` in Transparent Zen settings (scoped,
   reversible; premise unverified, settings never read).
2. Disable Transparent Zen (one-off diagnostic with immediate
   re-enable first, to prove the mechanism; standing disable only
   if the owner agrees).
3. Leave the extension as is and accept flagged passes + the
   diagnose-first ladder as the standing harness defense.
4. Fix the extension settings some other way the owner names.

## Runs that touched this item

- Worker Y4d agy-q2 rerun, 2026-11-21: see
  `improvements/worker-y4d-rerun-log.md` and
  `tests/realistic/RUN-REPORT-AGYQ2-20261121.md`. The suite JSON
  carries `bootstrap_intervention`, per-test `flagged`, and this
  file's path under `tracked_item`.
