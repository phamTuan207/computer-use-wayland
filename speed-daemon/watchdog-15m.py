#!/usr/bin/env python3
"""15-minute watchdog for mei/mochi: read back replies, poke on silence.

Runs every 5 minutes via cron. Enforces the owner's 15-minute auto-poke
rule (2026-11-23 23:14): if mei/mochi is silent over 15 minutes without a
reply reaching Muse, message them directly and discuss, do not stay silent.

What it does per recipient (mei, mochi), sequentially, never concurrent:
  1. Ensures the speed daemon is alive; restarts it once if down.
  2. Reads the last sent message (timestamp + run) from daemon.log.
  3. Reads back the latest replies via read.py --count 3 --raw (read-only).
  4. If the latest reply is NEW (hash differs from state), logs it and
     flags it if it looks like a question/blocker needing an answer.
  5. If no new reply and silence since my last sent message exceeds
     15 minutes (and no poke in the last 15 minutes), sends one poke
     via send.py with run = last_run + 1, and logs it.
  6. Saves state to watchdog-15m-state.json; appends a log line to
     watchdog-15m.log. Prints a short summary to stdout.

It never kills anyone, never touches the repo, never modifies a task.
It only reads and, when the 15-minute rule fires, sends one short
check-in message per recipient per 15-minute window.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    TZ = timezone.utc

HERE = Path(__file__).resolve().parent
DAEMON_LOG = HERE / "daemon.log"
DAEMON_SH = HERE / "daemon.sh"
READ_PY = HERE / "read.py"
SEND_PY = HERE / "send.py"
STATE_FILE = HERE / "watchdog-15m-state.json"
LOG_FILE = HERE / "watchdog-15m.log"
RECIPIENTS = ["mei", "mochi"]
SILENCE_MIN = 15
QUESTION_WORDS = ["?", "khong thay", "khong co", "can ", "giup", "blocker",
                  "cho ", "xac nhan", "kiem tra", "sao ", "the nao", "duoc khong"]


def now_hcm():
    return datetime.now(TZ)


def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S +07")


def parse_hcm(s):
    # daemon.log ts_hcm looks like "2026-11-23 23:28:26 +07"
    try:
        return datetime.strptime(s.replace(" +07", " +0700"), "%Y-%m-%d %H:%M:%S %z")
    except Exception:
        return None


def log_line(msg):
    line = f"{fmt(now_hcm())} {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def daemon_alive():
    r = subprocess.run([str(DAEMON_SH), "status"], capture_output=True,
                       text=True, timeout=20)
    return "NOT running" not in r.stdout


def daemon_restart():
    env = dict(os.environ, DAEMON_RESTARTER="watchdog-15m.py")
    r = subprocess.run([str(DAEMON_SH), "restart"], capture_output=True,
                       text=True, timeout=60, env=env)
    return "started" in r.stdout


def last_sent(recipient):
    """Return (ts datetime, run int) of the last successful send to recipient."""
    try:
        lines = DAEMON_LOG.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None, None
    last = None
    for line in reversed(lines):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("event") == "send" and e.get("recipient") == recipient \
                and e.get("outcome") == "sent":
            last = e
            break
    if not last:
        return None, None
    return parse_hcm(last.get("ts_hcm", "")), last.get("run")


def read_latest(recipient):
    """Return the latest assistant reply text, or None on read failure."""
    r = subprocess.run([sys.executable, str(READ_PY), "--recipient", recipient,
                        "--count", "3", "--raw"],
                       capture_output=True, text=True, timeout=90)
    try:
        data = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return None
    if not data.get("ok"):
        return None
    msgs = data.get("messages") or []
    if not msgs:
        return None
    return msgs[-1].get("text") or ""


def send_poke(recipient, run, last_sent_hcm):
    msg = (f"Em oi, anh nhan em luc {last_sent_hcm}, em doc duoc chua? "
           "Co gi can anh giup khong, cu noi nhe. Anh dang cho em tra loi day.")
    r = subprocess.run([sys.executable, str(SEND_PY), "--recipient", recipient,
                        "--run", str(run), "--message", msg],
                       capture_output=True, text=True, timeout=90)
    return "outcome=sent" in r.stdout or '"outcome": "sent"' in r.stdout


def main():
    state = load_state()
    now = now_hcm()
    summary = []
    if not daemon_alive():
        log_line("DAEMON DOWN, restarting (restarter: watchdog-15m.py)")
        if daemon_restart():
            log_line("DAEMON restarted ok (restarter: watchdog-15m.py)")
        else:
            log_line("DAEMON restart FAILED (restarter: watchdog-15m.py), "
                     "continuing with read-only checks")
    for recipient in RECIPIENTS:
        st = state.get(recipient, {})
        sent_ts, sent_run = last_sent(recipient)
        text = read_latest(recipient)
        if text is None:
            log_line(f"{recipient}: READ FAILED, skipping poke this round")
            summary.append(f"{recipient}: read failed")
            continue
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        if h != st.get("last_seen_hash"):
            st["last_seen_hash"] = h
            st["last_seen_hcm"] = fmt(now)
            snippet = text.replace("\n", " ")[:200]
            needs = any(w in text.lower() for w in QUESTION_WORDS)
            flag = " NEEDS ANSWER" if needs else ""
            log_line(f"{recipient}: NEW REPLY{flag}: {snippet}")
            summary.append(f"{recipient}: new reply{flag}")
            state[recipient] = st
            continue
        # No new reply. Check silence since my last sent message.
        if sent_ts is None or sent_run is None:
            log_line(f"{recipient}: no new reply, no sent message on record")
            summary.append(f"{recipient}: no new reply, nothing sent")
            state[recipient] = st
            continue
        # No new reply. Only poke if there is an OUTSTANDING message from me
        # she has not answered: my last sent message must be NEWER than when
        # I first saw her current latest reply. If her latest reply was seen
        # after my last sent message, she already answered it, so no poke
        # even if a long time has passed (this was the 01:28 false poke to
        # mei: she had answered at 23:15:52, I just saw it late).
        last_seen_dt = parse_hcm(st.get("last_seen_hcm", "")) \
            if st.get("last_seen_hcm") else None
        outstanding = (sent_ts is not None and last_seen_dt is not None
                       and sent_ts > last_seen_dt)
        silence_min = (now - sent_ts).total_seconds() / 60.0 if sent_ts else 0
        last_poke = parse_hcm(st.get("last_poke_hcm", "")) if st.get("last_poke_hcm") else None
        poked_recently = last_poke is not None and \
            (now - last_poke).total_seconds() / 60.0 < SILENCE_MIN
        if outstanding and silence_min > SILENCE_MIN and not poked_recently:
            ok = send_poke(recipient, sent_run + 1, fmt(sent_ts))
            if ok:
                st["last_poke_hcm"] = fmt(now)
                log_line(f"{recipient}: POKED (run {sent_run + 1}, "
                         f"silent {silence_min:.0f} min since {fmt(sent_ts)})")
                summary.append(f"{recipient}: poked after {silence_min:.0f} min")
            else:
                log_line(f"{recipient}: POKE FAILED (run {sent_run + 1})")
                summary.append(f"{recipient}: poke failed")
        else:
            log_line(f"{recipient}: silent {silence_min:.0f} min, "
                     f"within 15-min rule, no poke")
            summary.append(f"{recipient}: silent {silence_min:.0f} min, ok")
        state[recipient] = st
    save_state(state)
    print("WATCHDOG-15M SUMMARY: " + "; ".join(summary))


if __name__ == "__main__":
    main()
