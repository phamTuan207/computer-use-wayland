# R3-049 runner brief (Codex lane, R3-L3, position 32)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-049")

Use the loan calculator at calculator.net to compute monthly payments for 3
allocated loans. Write ket-qua.txt with 3 rows (principal, annual rate, term,
monthly payment, total interest) and save a timestamped screenshot of each of
the 3 results to ~/rung3-chung-cu/R3-049/.

## Allocated loans (from docs/rung3-answer-keys.json, allocated.R3-049)

1. Principal 500,000,000 VND, annual rate 8%, term 120 months (10 years)
2. Principal 300,000,000 VND, annual rate 7.5%, term 60 months (5 years)
3. Principal 1,000,000,000 VND, annual rate 9%, term 240 months (20 years)

## Drive method (shimmed Zen, per re-plan F3 and R3-046)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox danger-full-access,
  --skip-git-repo-check) with the GUI env exported in every command:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/ (re-read
  per launch, never hardcode). Zen is already running (PID 578117, v1.24.3b).
- Proxy shim mandatory: holder-fixb.mjs sha256
  70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213,
  probe-fixb.mjs sha256 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
  (verify both hashes in /tmp/fixb-runner/ before the drive; re-transfer by
  base64 pipe if wiped). Shim functionDeclaration sha256
  bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8. Probe
  fail-loud per drive: webdriver false, own_on_proto true, own_on_navigator
  false, get_name "get webdriver", toString verbatim; save the probe result
  JSON into the evidence dir (it enters the snapshot manifest chain). Mismatch
  stops the drive. NEVER drive unshimmed.
- Open calculator.net in the shimmed Zen and navigate to the Loan Calculator
  through the visible UI (site search box or Financial Calculators menu), like
  a normal user. Never deep-link straight to a calculator subpage URL. If a
  bot-wall or challenge appears, stop after ONE navigation attempt, save a
  screenshot, and report the block (do not hammer the site).
- For each loan: enter principal, annual rate, and term into the visible form
  fields, calculate, read the Monthly Payment and Total Interest from the
  result page, save a timestamped screenshot of the result.
- Write ~/rung3-chung-cu/R3-049/ket-qua.txt with EXACTLY this format (L3 rule):
  3 lines, one per loan, comma-separated:
  principal, rate_pct, term_months, monthly_payment, total_interest
  Numbers as shown on the site (keep decimals as displayed; no currency symbols
  or thousand separators in the numbers).
- Also record the calculation formula the page shows, if any, in the same file
  after the 3 lines (label it `formula:`).
- Save timestamped result screenshots for all 3 loans into
  ~/rung3-chung-cu/R3-049/ (names like loan1-YYYY-MM-DDTHH-MM-SS+07-00.png).
  Also write start_time.txt and end_time.txt (ISO with +07:00).

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active"). Verify
  visible=true during the drive and gone after; save a grim screenshot of the
  desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs, essentials,
  or anything on ws3. Close only your own task tabs/windows after use. One
  driver at a time on the shared Zen.
- NEVER touch the FCC tmux pane (PID 22399) or the fcc-server on port 8082.
- No personal info anywhere in files or reports. English only.
- Full access (Codex --sandbox danger-full-access). Log wall-clock
  Asia/Ho_Chi_Minh + elapsed. Do NOT score. Do NOT write coordinator state.
  Do NOT commit. Report facts only.

## Coordinator bookkeeping (driver script duties)

- Before launch: confirm Zen PID 578117 alive, no cursor.lock holder, no pill
  process; clear any stale /tmp/fixb-rpc ready.json; record task_start +
  runner PID in the laptop event log via log-event.sh immediately (the
  coordinator copies them into state).
- Launch detached (setsid nohup ... > log 2>&1 < /dev/null & disown). SSH dies
  ~30 s; poll with short SSH calls (ps + tail log).
- On completion: pull evidence to /tmp/r3-049-evidence/ on the VM, sha256 every
  file, confirm the runner PID is gone, grim-check the pill is gone, log
  completion via log-event.sh, report facts (PID, start/end wall-clock,
  evidence paths + sha256, pill status, anything unusual).
- Hard timeout 30 minutes from launch.
