# R3-086 runner brief (Codex lane, R3-L3, position 44, Class S, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-086")

Network check with ping, DNS, and curl, record the results. The 2 domains
in this order: 1. example.com 2. en.wikipedia.org.

1. Open a terminal, run `ping -c 4` to the first domain, record packets
   sent, packets received, loss rate.
2. Run a DNS lookup for the same domain, record the returned IP address.
3. Run `curl -L` to fetch the head of the homepage of the same domain,
   record the HTTP status code. Save each command output to its own
   timestamped file in ~/rung3-chung-cu/R3-086/: ping-YYYYMMDD-HHMMSS.txt,
   dns-YYYYMMDD-HHMMSS.txt, curl-YYYYMMDD-HHMMSS.txt.
4. Repeat `ping -c 4` for the second domain, DNS lookup for the second
   domain, `curl -L` for the second domain homepage, record the HTTP
   status code. Save: ping-2-YYYYMMDD-HHMMSS.txt,
   dns-2-YYYYMMDD-HHMMSS.txt, curl-2-YYYYMMDD-HHMMSS.txt in
   ~/rung3-chung-cu/R3-086/.
5. Write the report ~/rung3/nd06-bao-cao.txt with both domains, loss
   rates, IP addresses of both domains, status codes of both domains.
6. Re-check the report by reading each line back and comparing with the
   command outputs.

Pass: report has both domains, loss rates correct as the command results
at run time, IP addresses of both domains inside the DNS answer list of
each domain at run time, HTTP status code 200 for both domains, no item
missing, report matches the saved command output files.
Fail: missing domain, wrong loss rate, IP address not in the DNS answer
list, status code not 200, report not saved.

Amendment (R3-L3, 2026-11-24): both ping commands use `ping -c 4` (a bare
ping runs until SIGINT; the runner has no instructed way to stop it).

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal like a normal user
  and run the commands exactly as the task steps say (the task itself
  defines these commands as the entry point), then read the outputs back
  and compare with the report.
- (b) Forbidden shortcuts for this test: do NOT fabricate ping/DNS/curl
  outputs, IP addresses, or status codes; every value in the report must
  come from the saved command output files produced at run time. Do NOT
  reuse outputs from any earlier run.
- Evidence must show: entry (terminal open), path (6 commands run),
  action (outputs saved), resulting state (6 files + nd06-bao-cao.txt).
  End-state only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-086/:
  - The 6 command output files (ping, dns, curl per domain, timestamped
    names) (mandatory).
  - A copy of ~/rung3/nd06-bao-cao.txt (the report itself stays in
    ~/rung3/ until scored) (mandatory).
  - bao-cao.txt: steps, re-check result, any anomaly with full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active")
  while any agent controls the machine. Verify visible during the drive
  and gone after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own windows after use.
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the
  overlay daemon). Pre-flight: `hyprctl configerrors` must be empty
  before launch (clear with `hyprctl eval "return true"` if needed,
  record the result).
- Class S: after scoring, the coordinator removes the evidence outputs
  (reset). Leave them in place until then.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-086/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, both domains' results, and every anomaly chain.
  No score.
