# R10 Step 1: interim two-profile Zen split - adoption report (2026-11-27)

Status: ADOPTED (interim). Human profile launches flag-free on every audited
path from the owner's next Zen launch. The owner's currently running session
predates adoption and is reported LEGACY-FLAGGED by the startup probe until
he relaunches; it was not restarted, killed, or touched.

Decision reference: improvements/r10-stage2-decision-20261127.md (Step 1,
redteam amendments S2-S8). Stage 1 evidence:
improvements/r10-stage1-report-20261127.md. R10 stays OPEN; this is the
interim split only, pending the A5 A/B gate and any conditional build.

## What changed

- Human profile (the owner's default Zen profile): no
  --remote-debugging-port, no --marionette on any launch path.
- Agent profile: flagged dedicated sessions via the zen_cli session
  machinery (BiDi, dedicated profile under ~/.cache/cli-anything-zen/,
  ports scanned from 9222 upward; gate used 9225).
- Interim shim residue retained per decision: pinned shim hash, probe
  result in every drive report, dirty probe = stop. (The shim itself is
  unchanged by this step; nothing in this adoption reads or runs it.)

## S6 - launch-path audit

Every way Zen launches on this machine was enumerated and audited:

| Path | Before | After |
| --- | --- | --- |
| ~/.local/bin/zen-ai wrapper | execs zen-bin with --remote-debugging-port=9222 --marionette | left in place, no longer referenced by any entry point |
| User desktop entry (~/.local/share/applications/zen.desktop, 5 Exec lines) | Exec=zen-ai | Exec=~/.local/bin/zen-human (flag-free) |
| System desktop entry (/usr/share/applications/zen.desktop, 5 Exec lines) | Exec=zen-ai | Exec=~/.local/bin/zen-human (flag-free) |
| omarchy-launch-browser (Super+Z) | extracts Exec first token, drops args, resolved to zen-ai | resolves to zen-human, flag-free |
| xdg-mime http/https/text-html | zen.desktop | unchanged (now flag-free via the entry) |
| Autostart | no Zen entry | unchanged |
| Shell aliases / PATH | zen and zen-bin not on PATH; /usr/bin/zen-browser is a flag-free plain wrapper | unchanged |
| Manual terminal launch | owner could run zen-ai by hand | zen-human is the documented human path; zen-ai remains only as the flagged manual route under the S2 escape hatch |

Backups of both desktop entries kept next to the originals
(zen.desktop.bak-20261127-presplit). Post-change grep over applications,
autostart, systemd user units, and Hyprland config: no active zen-ai
references remain (backups excluded).

New launcher ~/.local/bin/zen-human: fires the startup probe detached
(5 s delay, cmdline mode), then execs zen-bin with no automation flags.

## S6 - human-profile startup probe

~/.local/bin/zen-human-probe (reference copy:
improvements/zen-human-probe.py; launcher reference:
improvements/zen-human). Two modes:

- cmdline: scans zen-bin main processes on real profiles (default profile
  or --profile under ~/.config/zen; throwaway /tmp profiles ignored) and
  verdicts CLEAN / LEGACY-FLAGGED (flagged process started before the
  adoption timestamp in ~/.local/state/zen-split/adopted-at) /
  ESCAPE-HATCH (flagged at or after adoption with a fresh escape marker)
  / FAIL (exit 1 + critical desktop notification). Start times from
  /proc stat + btime. Every run appends one JSON line to
  ~/.local/state/zen-split/probe.log.
- full: cmdline plus a throwaway headless flag-free instance that beacons
  its page-visible signals to a local listener: navigator.webdriver
  value and type, descriptor shape, getter toString, documentElement
  webdriver attribute, plugin count, suspicious automation globals.
  Asserts false / boolean / native getter / no attribute / no globals.

Probe runs (2026-11-27, Asia/Ho_Chi_Minh):

1. 06:47 pre-adoption: LEGACY-FLAGGED; throwaway_ok=true (webdriver
   false, boolean, getter "function webdriver() { [native code] }",
   document attribute null, 5 plugins, no suspicious globals).
2. Post-adoption (after desktop-entry fix): LEGACY-FLAGGED (running
   session started 06:37:47, adoption 06:49:02); throwaway_ok=true.
3. 07:04 post-cleanup: LEGACY-FLAGGED; only the owner's pre-adoption
   session on a real profile; a parallel lane's throwaway /tmp instance
   correctly ignored.

Verdict logic unit-tested (5 asserts, all pass). The probe never touches
the running browser; the full-mode instance is a throwaway profile killed
by pid + cmdline check.

## S3 - headed concurrency gate (PASSED)

Gate ran on ws2 alongside the owner's live Zen and a parallel lane's BiDi
drive (all gate driving was BiDi/grim, OS-focus independent):

- Human throwaway: headed, flag-free (cmdline verified), own profile.
- Agent instance: zen_cli dedicated session, BiDi port 9225, headed.
- Both ran concurrently with the owner's Zen: no port or profile
  collision (owner keeps 9222/2828; agent never uses them).
- Pill acquired for the agent instance (holder key agent:pid), visible,
  label "Computer use active", alongside the other lane's holder.
- Agent drive verified: BiDi navigate to a local page, read back title
  and text.
- RAM during gate: human throwaway 255 MB, agent 653 MB, owner 588 MB.
- Restart cycle: session stop left human + owner alive; session start
  again came up clean (session_up=true). No profile-lock errors.
- Cleanup: pill released, agent stopped, human throwaway killed by pid +
  cmdline check, owner Zen alive with ports up at the end.

Evidence (VM-local, not committed; screenshots are large):
~/workspace/r10-split-adoption/evidence/ on the coordinator VM
(gate-screen1.png, gate-screen2.png, ram.txt, agent-page.json,
agent-status2.json, pill-status.json, clients1.json,
session-log-tail.txt, human-cmdline.txt, agent-cmdline.txt, gate.log).

## S2 - continuity escape hatch (logged exception only)

Silent flagged drive of the human profile is FORBIDDEN. If a task
genuinely needs the owner's live session, the drive is allowed only as an
explicitly logged exception:

1. Write the marker ~/.local/state/zen-split/escape-hatch-active BEFORE
   any flagged launch (the probe reads a marker up to 4 h old as
   ESCAPE-HATCH instead of FAIL).
2. Record the tabs in scope before driving.
3. Include the probe result in the drive report.
4. Remove the marker when the exception ends.

Full procedure: machine layer ~/.config/agent-computer-use/machine/
zen-profile-split.md (laptop only).

## S5 - agent-profile credential policy

- Task-scoped test accounts are the default for the agent profile.
- Owner-account use only via the S2 logged escape hatch, per-task
  approval, logged.
- The owner never daily-drives the agent profile.
- Written into the machine layer (zen-profile-split.md).

## S4 - parity mechanism

- Named owner: Muse (parent coordinator).
- Nothing syncs automatically between the two profiles. Cookies,
  logins, history, and session state are NEVER synced.
- Bookmarks/settings drift is checked via drive reports (probe result +
  profile state noted per drive); parity fixes are deliberate, manual,
  and logged. Details in the machine layer.

## S8 - update drill

After any Zen package update, before agent use:

1. Run zen-human-probe --mode full (human flag-free + page-visible
   signals clean).
2. Cold-call the agent lane (dedicated session start, navigate, read,
   stop) and confirm the pill shows.
3. Record both results in the drive report. A dirty probe stops agent
   use until resolved.

## Human-leg verification (normal-user path)

Throwaway flag-free headed profile (cmdline verified: no
--remote-debugging-port, no --marionette), driven by OS input with the
pill visible. Entry, path, action, resulting state:

- Entry: browser new-tab page (Zen onboarding skipped via
  zen.welcome-screen.seen=true in the throwaway profile's user.js).
- Path: Ctrl+L, typed "codeforces", Enter - Google results page.
- Action: clicked the codeforces.com result.
- Resulting state: Codeforces homepage fully loaded, no Cloudflare
  interstitial. (The same site was Cloudflare-blocked in the flagged
  live session at 06:33 per the Stage 1 report.)

Evidence (VM-local): humanleg-relaunch.png (entry), humanleg-search.jpg
(results), humanleg-site.jpg (site loaded). This verifies the mechanism
on a throwaway profile. Verification on the owner's own profile is
pending his next natural relaunch, which the probe will record as CLEAN
(the current session is LEGACY-FLAGGED by design; it was not restarted).

## Follow-ups (not blockers for the interim split)

1. Health-watch revive path must launch via zen-human, never the flagged
   wrapper - parent to confirm the cron body.
2. Marionette lane (zen_dom.py defaults to port 2828) must not default to
   the human profile after the split; a dedicated flagged Marionette
   launch recipe is a follow-up.
3. Laptop zen_cli.py copies lack the pill integration present in the VM
   worktree copy; align them (separate change).
4. Owner's next relaunch: probe should flip LEGACY-FLAGGED to CLEAN;
   record it when it happens.

## Files

- Laptop (machine layer): ~/.local/bin/zen-human,
  ~/.local/bin/zen-human-probe, ~/.local/state/zen-split/adopted-at,
  ~/.local/state/zen-split/probe.log,
  ~/.config/agent-computer-use/machine/zen-profile-split.md,
  desktop entries + presplit backups.
- Repo reference copies: improvements/zen-human-probe.py,
  improvements/zen-human, this report.
