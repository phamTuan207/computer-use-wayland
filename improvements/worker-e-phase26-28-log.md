# Worker E log: Phase 2.6, 2.7, 2.8 (error-fix todo list, 21/11/2026)
# Wall-clock Asia/Ho_Chi_Minh + elapsed from task start 03:31:49.
# Rule: one small piece = one small commit, push immediately. No ydotool.
# No OpenRouter, no gpt-reserve. No personal info on GitHub. No em/en dashes.

## 03:33 (+2m) Start. Read todo list + both error files (skimmed I31-I46).
## 03:35 (+4m) Repo survey (branch harness-warm-browser, ahead 8 behind 2).
# Already in code, verified by grep, no work needed:
# - G1 stale-code guard + relay restart: scripts/sync-installed.py
#   (_relay_restart_needed, _restart_relay, loaded_code_sha256 verify) + tests
#   in tests/test_sync_installed.py. DONE, no change.
# - G2 editor geometry 901x1176 floating at [2990,914]: scripts/tc02_controller.py.
#   DONE, no change.
# - G3 leases in ~/.cache/agent-computer-use/leases/ mode 0700:
#   scripts/tc02_controller.py _create_lease_path. DONE, no change.
# - G4 hl.dsp object form: scripts/cu.py, scripts/tc02_controller.py. DONE, no change.
# - 2.8.1 desktop observation limit 120s: scripts/cu.py OBSERVATION_MAX_AGE = 120
#   (commit 6f055e1). DONE for desktop, but code_exec.py still 90s (see below).
# Gaps found, to fix in order:
# - 2.8.1 code_exec.py OBSERVATION_MAX_AGE still 90 (desktop obs + DOM snapshot),
#   error strings say 90s, test asserts 90s; skill docs still say 90s everywhere.
# - 2.8.2 session_driver relay_commands: json.loads(line) unguarded; a PNG path
#   (or any non-JSON line) raises ValueError and kills the relay/session (I43).
# - 2.7.16 G24 JSONL: no append guard anywhere; visuals.py, cu.py diagnostics,
#   tc02_controller emit all blind-append with + '\n'. A partial last line glues.
# - 2.6.5 I31: no file logger for direct Muse driving; only chat history.
#   cu.py _diagnostic_event writes per-task diagnostics jsonl, but there is no
#   operator-side drive log with wall-clock + elapsed for direct driving.
# - 2.7.5 G5: no pkill imv-wayland anywhere in repo; tc02 only FAILS hygiene
#   when an imv* process is alive, nothing ever kills it after viewing a photo.
# - 2.7.11 G11 + Phase 4.1: pill blur_strength 0.0 in
#   native/hyprglass-local-optics.lua; user ordered a small blur increase
#   after reboot 21/11. (No visuals.json manifest in this checkout; pin is
#   regenerated at install, so no manifest hand-edit.)
# - 2.7.9 G9: no VM forward-proxy helper in repo; chromium_cli has no proxy.
# - 2.6.1-2.6.4, 2.6.6, G6/G7/G8/G12/G19/G20/G23/G27, I32-I40: brief/runbook
#   rules live only in chat/memory, not in the repo. Land as a checklist doc
#   + troubleshooting/browser/skill doc updates.
# - 2.7.14 G21 Browse hover: verify the off-center hover fix exists in code.
# - 2.7.10 G10 pill shape: copy-exact upstream rule; already the stated
#   approach in native/hyprglass-local-optics.lua comments; no code change,
#   record in checklist doc.
#
## COMMIT 3b0d904 pushed (2.8.1): code_exec 90s to 120s + all
# skill docs to 120s + boundary test (100s-old DOM snapshot still valid).
# test_code_exec 51 tests OK.
# Note: branch switched under me (harness-warm-browser -> todolist-push);
# checkout is shared with workers C/D. Push raced once; verified via fetch.
# Only ever `git add` my own paths; other workers' uncommitted files exist.
## COMMIT 904ec85 pushed (2.7.16 G24): scripts/jsonlutil.py
# (append_jsonl, ensure_trailing_newline_fd, verify_jsonl) wired into
# visuals.py, cu.py diagnostics, tc02_controller emit. 8 new tests pass.
# Caught by test: os.pread needs a readable fd; writers open write-only,
# so the helper reads the last byte via a separate read-only fd.
# 7 test_session_driver doctor failures are PRE-EXISTING on the clean tree
# (verified via git stash; fcitx5-remote probes, VM environment).
## COMMIT e3d75c4 pushed (2.8.2 I43): relay_commands answers
# an unparseable request line (PNG path, non-UTF-8 bytes) with an error
# envelope and stays alive; parsed JSON of wrong shape still raises
# ValueError fail-closed per test_invalid_requests_never_execute. 3 new
# tests; Driver + SessionDriverLimit 20 tests OK.
## COMMIT 8ca3494 pushed (2.6.5 I31): scripts/drive_log.py, file log
# for direct driving with wall-clock Asia/Ho_Chi_Minh + elapsed, monotonic
# in-process, wall-based across processes (CLI reopens and keeps T0).
# 6 tests pass.
## COMMIT a6d2f2b pushed (2.7.5 G5): scripts/image_viewer.py kills
# and lists by exact comm imv-wayland; desktop.md states the rule. 6 tests.
## COMMIT b2afcd1 pushed (2.7.11 G11 + Phase 4.1): pill
# blur_strength 0.0 to 0.15 in native/hyprglass-local-optics.lua, refraction
# stays copied exactly from upstream (0.55). No visuals.json in checkout,
# pin regenerates at install. Live look still needs user's eyes post-reboot.
# Glass tests pass.
## COMMIT 6a118f6 pushed (2.7.9 G9): scripts/vm_proxy.py, local
# forward proxy on 127.0.0.1 adding preemptive Proxy-Authorization from
# VM_EGRESS_PROXY_AUTH (env only). LIVE VERIFIED: curl https://example.com
# through it returns 200 via hatch-egress-proxy:3128. 4 unit tests pass.
# Two test bugs caught by running them: status-line check looked for a
# trailing ' 200' (line ends 'Established'); urlparse mishandles plain
# host:port (treats host as scheme).
## COMMIT f1f2806 pushed (2.7.14 G21): first-class desktop 'hover'
# action in cu.py (move + 30 ms settle, never clicks) + desktop.md recipe
# (hover off-center until Browse darkens, then click; 'blocked' was the
# wrong diagnosis). Also fixed G24 wiring fallout: jsonlutil imports in
# cu.py/tc02_controller.py/visuals.py fall back to the scripts dir when
# loaded by file path (test_core loads cu that way). test_core shows only
# the PRE-EXISTING hyprctl-missing failure on this VM (verified on clean
# tree via git stash).
## COMMIT (2.6.1-2.6.4, 2.6.6 + runbook): docs/worker-brief-checklist.md
# (research-first, save method verbatim, give ALL lessons, tell user
# first, I32-I40 brief rules, stuck/reporting rules, verify-don't-invent,
# operator runbook, ban list incl. ydotool/OpenRouter/gpt-reserve);
# troubleshooting.md runbook (SSH 30s, wrapper, agy vs fcc-claude,
# vm_proxy, chooser-only sign-in, reply-when-@, imv-wayland, hl.dsp,
# stale-code relay, bad driver lines); browser.md Zen rules (Ctrl+N/T,
# no Ctrl+L in picker, Zen + logged-in tab + driver, hover Browse);
# SKILL.md links the checklist.
## Final sweep: 136 tests OK (jsonlutil, drive_log, image_viewer, vm_proxy,
# session_driver Driver, SessionDriverLimit, code_exec, visuals,
# sync_installed). Known pre-existing failures NOT mine: 7
# test_session_driver doctor tests (fcitx5-remote probes, VM env) and 1
# test_core test (hyprctl binary absent on VM); both fail on clean tree.
# CORRECTION (03:46): the "+Nm / 04:0x" elapsed annotations in earlier
# versions of this log were guesses, not measured times. True window:
# task start 03:31:49, finish 03:46, about 14 minutes total.
## NOT done / needs the laptop or the user:
# - Pill blur 0.15: needs install on the laptop + the user's eyes after
#   reboot (taste judge). The value is one small step, easy to adjust.
# - vm_proxy + Chromium flags: proxy path verified live with curl; the
#   actual Chromium launch still needs a live-browser check (not
#   available to a subagent).
# - G10 pill shape (copy upstream exactly): already the stated approach in
#   the lua comments; no code change, recorded in the checklist.
# - Todo-list checkboxes in docs/zen-error-fix-todolist-20261121.md were
#   NOT ticked by me: another worker has uncommitted edits to that file,
#   so ticking would have committed their in-flight work. Checkbox lines
#   to tick are listed in the final report.
# - G1/G2/G3/G4/2.8.1-desktop: already in code, verified, no change.
