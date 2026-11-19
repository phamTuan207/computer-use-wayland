#!/usr/bin/env python3
"""Derive brief-pf2-method.md from brief-pf2-baseline.md (Task 4)."""
import pathlib

BASE = pathlib.Path("/home/hatch/workspace/omarchy-tasks/cu-fix-20261114/improvements/live-pf2-20261120")
src = (BASE / "brief-pf2-baseline.md").read_text()

METHOD_RULE = (
    "ARM RULE (read first): this arm measures the H6 PAGE PREFETCH method: prefetch the page in a background "
    "tab, then open it. Relay env has CU_PRECAPTURE=0 (desktop pre-capture OFF in both arms, so only page "
    "prefetch differs; verify with `systemctl --user show computer-use-relay -p Environment` and stop and "
    "report if CU_PRECAPTURE=0 is absent). This checkout is 56f5af4. Do NOT call det_finish.py anywhere on "
    "this arm. After the verify, close the task the stock way: deliberate the close in-session, write the "
    "per-task summary section into summary.md yourself, THEN call `timed.py finish`. No det-finish, no Pick 2 "
    "rules, no L2 sub-invocations, no code-exec, no other lever. Record: prefetch ok and tab id, open "
    "load_ms, prefetched flag, whether the opened tab id matches the prefetched tab id, "
    "time-to-first-interaction, total wall, capture_ms per desktop observe."
)

METHOD_STEP3 = (
    "3. Prefetch, then open, in ONE shell burst with NO deliberation between them (BASELINE step 3 is "
    "replaced by this step). Run in your own shell (plain shell, CDP only, no pointer or keyboard input): "
    "first `CU_SESSION_TOKEN=$(python3 -c \"import json; print(json.load(open('/home/james/.local/share/agent-computer-use/session.json'))['token'])\") "
    "python3 /home/james/computer-use-wayland/scripts/chromium_cli.py prefetch https://example.com` and "
    "record ok, prefetched, and the prefetched tab id; then sleep 3 seconds (log the sleep first, it lets "
    "the tiny example.com page finish loading in the background tab); then, in the same burst, "
    "`CU_SESSION_TOKEN=$(python3 -c \"import json; print(json.load(open('/home/james/.local/share/agent-computer-use/session.json'))['token'])\") "
    "python3 /home/james/computer-use-wayland/scripts/chromium_cli.py open https://example.com` and record "
    "ok, prefetched flag, load_ms, and the opened tab id. The token comes from your own session state file; "
    "use it transiently in those commands only. NEVER print the token, never write it to any file or log, "
    "never put it in the summary. Record the wall-clock time you submitted the open command. Check the "
    "opened tab id matches the prefetched tab id and say so in the summary. If open returns "
    "prefetched=false, record WHY with the evidence (prefetch result, the seconds between prefetch and "
    "open, any error) and continue with the fresh load; that outcome IS the measurement, do not retry the "
    "prefetch. WRONG-ADOPTION WATCH: if open returns prefetched=true but the page you then observe is not "
    "example.com, STOP, record a WRONG-ADOPTION incident with the evidence, close the tab, and report."
)

PREFETCH_NOTE = (
    "PREFETCH NOTE: a prefetch record lives at most 30 seconds (PREFETCH_TTL_SECONDS=30) and open adopts "
    "it only when the background page state is ready complete, not failed, and the URL matches. That is why "
    "prefetch and open run in ONE shell burst with only a 3 second sleep between them: a model think gap "
    "between them would expire the prefetch and the open would silently fall back to a fresh load. The 3 "
    "second sleep is enough for the tiny example.com page; do not lengthen it. If the page had not finished "
    "loading when open runs, open falls back to a fresh tab by design (safe, not an error); record it as "
    "prefetched=false with the prefetch timing as the reason.\n\n"
)

text = src
text = text.replace(
    "ARM PF2-BASELINE (no page prefetch, direct open)",
    "ARM PF2-METHOD (H6 page prefetch, prefetch + open)")
text = text.replace("/tmp/live-pf2-20261120/pf2-baseline",
                    "/tmp/live-pf2-20261120/pf2-method")
text = text.replace("pf2-base", "pf2-method")
i = text.index("ARM RULE (read first):")
j = text.index("Record: open load_ms, prefetched flag, tab id, time-to-first-interaction, total wall, capture_ms per desktop observe.") + len("Record: open load_ms, prefetched flag, tab id, time-to-first-interaction, total wall, capture_ms per desktop observe.")
text = text[:i] + METHOD_RULE + text[j:]
k = text.index("3. Open the page directly (BASELINE: no prefetch).")
k2 = text.index("4. Read the page through the broker:")
text = text[:k] + METHOD_STEP3 + "\n" + text[k2:]
m = text.index("PAGE PREFETCH INVOCATION NOTE:")
text = text[:m] + PREFETCH_NOTE + text[m:]
(BASE / "brief-pf2-method.md").write_text(text)
print("wrote brief-pf2-method.md", len(text), "chars")

LAUNCH_TMPL = """#!/bin/bash
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
setsid -f kitty --single-instance=no --title {exec_title} bash -c 'cd /home/james/computer-use-wayland && codex exec -m gpt-6-luna -c model_reasoning_effort="max" -s danger-full-access - < /tmp/live-pf2-20261120/{rundir}/brief.md > /tmp/live-pf2-20261120/{rundir}/codex.log 2>&1'
echo "launched {exec_title}"
"""
for rundir, exec_title in [("pf2-baseline", "pf2-base-exec"), ("pf2-method", "pf2-method-exec")]:
    (BASE / ("launch-" + rundir + ".sh")).write_text(
        LAUNCH_TMPL.format(exec_title=exec_title, rundir=rundir))
    print("wrote launch-" + rundir + ".sh", exec_title)
