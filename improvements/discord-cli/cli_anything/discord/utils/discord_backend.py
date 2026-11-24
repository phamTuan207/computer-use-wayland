"""Backend for cli-anything-discord: drives the REAL Discord desktop client
(Electron) over Chrome DevTools Protocol on 127.0.0.1:9229.

The real software is a hard dependency (HARNESS principle). This module never
reimplements Discord and never touches a user token: it talks to the running
official client through CDP. Transport is Node >= 22 (global WebSocket, no npm
deps) via utils/cdp_client.mjs; Python only shells out to it.

Launch env (from Phase 1, verified live): Discord needs DISPLAY=:0 (XWayland)
plus XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus and
HYPRLAND_INSTANCE_SIGNATURE from `ls /run/user/1000/hypr/ | head -n1`.
"""

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

CDP_PORT = int(os.environ.get("DISCORD_CDP_PORT", "9229"))
DISCORD_BIN = "/home/james/.local/opt/Discord/discord"
CDP_LOG = "/tmp/discord-cdp-9229.log"
TEST_DM_CHANNEL_ID = "865272264831139840"  # DM with Violet Joestar (owner-designated test DM)

_CDP_CLIENT = Path(__file__).resolve().parent / "cdp_client.mjs"


class DiscordError(RuntimeError):
    """Loud, actionable failure (HARNESS: fail loudly and clearly)."""


def _node():
    import shutil
    node = shutil.which("node")
    if not node:
        raise DiscordError("node is not installed. Discord CDP transport needs Node >= 22 "
                           "(global WebSocket). Install Node, then retry.")
    return node


def _run_node(args, stdin_text=None, timeout=60):
    """Run cdp_client.mjs; returns parsed JSON stdout. Raises DiscordError on failure."""
    if not _CDP_CLIENT.is_file():
        raise DiscordError(f"CDP client missing: {_CDP_CLIENT}")
    proc = subprocess.run(
        [_node(), str(_CDP_CLIENT)] + args,
        input=stdin_text, capture_output=True, text=True, timeout=timeout,
    )
    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except (json.JSONDecodeError, IndexError):
        raise DiscordError(f"cdp_client produced no JSON output (rc={proc.returncode}): "
                           f"{proc.stdout[:500]} {proc.stderr[:500]}")
    if not data.get("ok"):
        raise DiscordError(data.get("error", f"cdp_client failed rc={proc.returncode}"))
    return data


def _http_json(path, timeout=5):
    with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}{path}", timeout=timeout) as r:
        return json.loads(r.read().decode())


def cdp_reachable():
    try:
        _http_json("/json/version")
        return True
    except Exception:
        return False


def find_discord():
    if Path(DISCORD_BIN).is_file():
        return DISCORD_BIN
    import shutil
    p = shutil.which("discord")
    if p:
        return p
    raise DiscordError(
        "Discord desktop is not installed at /home/james/.local/opt/Discord/discord "
        "and no `discord` is on PATH. Install the official Discord desktop client first."
    )


def _gui_env():
    env = dict(os.environ)
    env.update({
        "DISPLAY": ":0",
        "XDG_RUNTIME_DIR": "/run/user/1000",
        "WAYLAND_DISPLAY": "wayland-1",
        "XDG_SESSION_TYPE": "wayland",
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
    })
    hypr_dir = Path("/run/user/1000/hypr")
    if hypr_dir.is_dir():
        entries = sorted(p.name for p in hypr_dir.iterdir())
        if entries:
            env["HYPRLAND_INSTANCE_SIGNATURE"] = entries[0]
    return env


def ensure_running(wait_s=60):
    """Attach if CDP answers; otherwise launch Discord detached with the debug port.

    Returns {"running": True, "launched": bool}. Never kills Discord.
    Cold launch after a full quit can take >20s to answer CDP on this
    machine (observed 2026-11-24: 20s poll expired, CDP came up just after),
    so the default wait is 60s.
    """
    if cdp_reachable():
        return {"running": True, "launched": False}
    binary = find_discord()
    log = open(CDP_LOG, "ab")
    subprocess.Popen(
        [binary, f"--remote-debugging-port={CDP_PORT}"],
        env=_gui_env(), stdout=log, stderr=log, stdin=subprocess.DEVNULL,
        start_new_session=True, close_fds=True,
    )
    deadline = time.time() + wait_s
    while time.time() < deadline:
        if cdp_reachable():
            return {"running": True, "launched": True}
        time.sleep(1)
    raise DiscordError(
        f"Discord did not answer CDP on port {CDP_PORT} within {wait_s}s after launch. "
        f"See {CDP_LOG}. If Discord shows a stale SingletonLock, quit it fully and retry."
    )


def list_targets():
    return _run_node(["targets", str(CDP_PORT)])["targets"]


def resolve_page_target():
    """Pick the Discord page target at runtime. NEVER hardcode a target id."""
    if not cdp_reachable():
        raise DiscordError(
            "Discord CDP is not reachable on port 9229. Discord is either not "
            "running, or it was launched without --remote-debugging-port=9229. "
            "CDP control is opt-in (default off): run `session start` to launch "
            "Discord with CDP enabled, or launch it yourself with "
            "--remote-debugging-port=9229.")
    targets = list_targets()
    pages = [t for t in targets if t.get("type") == "page"
             and "discord.com" in (t.get("url") or "")]
    if not pages:
        raise DiscordError("No discord.com page target found on CDP. "
                           "Is Discord running with --remote-debugging-port=9229?")
    # Prefer the main app page (has a webSocketDebuggerUrl).
    pages.sort(key=lambda t: 0 if t.get("webSocketDebuggerUrl") else 1)
    return pages[0]


def evaluate(ws_url, expression, timeout=60):
    return _run_node(["eval", ws_url], stdin_text=expression, timeout=timeout)["value"]


def navigate(ws_url, url):
    return _run_node(["navigate", ws_url, url])


def open_channel(channel_id):
    """Navigate the client to a channel/DM. Returns the resolved target + URL."""
    target = resolve_page_target()
    ws_url = target["webSocketDebuggerUrl"]
    if isinstance(channel_id, str) and (channel_id.startswith("@me/") or "/" in channel_id):
        url = f"https://discord.com/channels/{channel_id.lstrip('/')}"
    else:
        # Bare snowflake: a DM channel id.
        url = f"https://discord.com/channels/@me/{channel_id}"
    navigate(ws_url, url)
    # Let the client render the channel before any DOM read.
    time.sleep(2)
    return {"target_id": target["id"], "url": url, "title": target.get("title", "")}


# --- DOM scraping (selectors from Phase 1; stable hooks first) ------------

READ_JS = """(() => {
  const items = [...document.querySelectorAll('li[id^="chat-messages-"]')];
  let lastAuthor = '';
  return items.map(li => {
    const id = li.id.split('-').pop();
    // Discord omits the author header on follow-up messages from the same
    // author, so inherit the last seen author when a row has no header.
    const nameEl = li.querySelector('span[class*="username"]');
    if (nameEl && nameEl.textContent) lastAuthor = nameEl.textContent;
    const author = lastAuthor;
    const timeEl = li.querySelector('time');
    const timestamp = timeEl?.getAttribute('datetime') || timeEl?.textContent || '';
    const content = li.querySelector('div[class*="messageContent"]')?.innerText || '';
    const attachments = [...li.querySelectorAll(
      'a[href*="cdn.discordapp.com"], a[href*="media.discordapp.net"]'
    )].map(a => a.getAttribute('href'));
    return { id, author, timestamp, content, attachments };
  });
})()"""

SERVERS_JS = """(() => {
  // Locale-proof: do not depend on the nav aria-label ("Servers" in English,
  // "Thanh bên máy chủ" in Vietnamese). The guild items carry stable
  // data-list-item-id="guildsnav___<id>" hooks in every locale.
  const items = [...document.querySelectorAll('[data-list-item-id^="guildsnav___"]')];
  if (!items.length) return { ok: false, error: 'server rail not found (no guildsnav items)' };
  return { ok: true, count: items.length,
    servers: items.map(el => ({
      id: (el.getAttribute('data-list-item-id') || '').replace('guildsnav___', ''),
      name: el.getAttribute('aria-label') || el.textContent.trim(),
    })) };
})()"""

CHANNELS_JS = """(() => {
  const links = [...document.querySelectorAll('a[href^="/channels/"]')];
  const seen = new Map();
  for (const a of links) {
    const href = a.getAttribute('href');
    if (!seen.has(href)) seen.set(href, (a.getAttribute('aria-label') || a.textContent || '').trim());
  }
  return [...seen.entries()].map(([href, name]) => ({ href, name }));
})()"""

CHANNEL_TITLE_JS = """(() => {
  const h = document.querySelector('h1');
  return { title: h ? h.textContent.trim() : '',
           url: location.pathname, composer: !!document.querySelector('div[role="textbox"][contenteditable="true"]') };
})()"""


def _wait_for(ws_url, expression, timeout=15, what="condition"):
    """Poll a Runtime.evaluate expression until truthy (channel still loading)."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            last = evaluate(ws_url, expression)
        except DiscordError:
            last = None
        if last:
            return last
        time.sleep(0.5)
    raise DiscordError(f"Timed out waiting for {what} ({timeout}s). "
                       "The channel may still be loading, or Discord changed its DOM.")


def read_messages(channel_id, limit=20):
    """Open the channel, then scrape the visible message window.

    Only the viewport window is in the DOM; `limit` caps the returned rows.
    Scrolling up loads older messages, but Discord virtualizes the list:
    scrolling away can unload the newest rows, so the scroller is always
    returned to the bottom before the final read (2026-11-24: a limit=10
    read returned zero rows until this was added).
    Returns {"channel_id", "messages": [...], "count", "truncated"}.
    """
    opened = open_channel(channel_id)
    target = resolve_page_target()
    ws_url = target["webSocketDebuggerUrl"]
    messages = []
    _wait_for(
        ws_url,
        "document.querySelectorAll('li[id^=\"chat-messages-\"]').length",
        timeout=15, what="messages to appear",
    )
    messages = evaluate(ws_url, READ_JS) or []
    # Scroll the message scroller up to load older messages (bounded).
    scroll_js = """(() => {
      const sc = document.querySelector('[class*="scroller"][class*="messages"], [class*="messagesWrapper"] [class*="scroller"]');
      if (!sc) return 0;
      sc.scrollTop = 0;
      return document.querySelectorAll('li[id^="chat-messages-"]').length;
    })()"""
    scroll_bottom_js = """(() => {
      const sc = document.querySelector('[class*="scroller"][class*="messages"], [class*="messagesWrapper"] [class*="scroller"]');
      if (!sc) return 0;
      sc.scrollTop = sc.scrollHeight;
      return 1;
    })()"""
    seen = len(messages or [])
    for _ in range(5):
        if seen >= limit:
            break
        before = seen
        evaluate(ws_url, scroll_js)
        time.sleep(1)
        after = len(evaluate(ws_url, READ_JS) or [])
        if after <= before:
            break
        seen = after
    # Always come back to the bottom: the newest messages are what callers
    # (and send read-backs) need, and a scrolled-up view may have unloaded them.
    evaluate(ws_url, scroll_bottom_js)
    time.sleep(1)
    messages = evaluate(ws_url, READ_JS) or []
    if not messages:
        _wait_for(
            ws_url,
            "document.querySelectorAll('li[id^=\"chat-messages-\"]').length",
            timeout=10, what="messages to reappear after scroll",
        )
        messages = evaluate(ws_url, READ_JS) or []
    if not messages:
        raise DiscordError(f"No messages found in the DOM for channel {channel_id}. "
                           "The channel may still be loading, or Discord changed its DOM.")
    truncated = len(messages) > limit
    return {
        "channel_id": str(channel_id), "url": opened["url"],
        "messages": messages[-limit:] if limit else messages,
        "count": min(len(messages), limit) if limit else len(messages),
        "truncated": truncated,
        "total_visible": len(messages),
    }


def list_servers():
    target = resolve_page_target()
    value = evaluate(target["webSocketDebuggerUrl"], SERVERS_JS)
    if isinstance(value, dict) and not value.get("ok", True):
        raise DiscordError(value.get("error", "server rail not found"))
    return value


def list_channels():
    target = resolve_page_target()
    links = evaluate(target["webSocketDebuggerUrl"], CHANNELS_JS) or []
    dms, guild_channels = [], []
    for link in links:
        href = link.get("href", "")
        if href.startswith("/channels/@me/"):
            dms.append(link)
        elif href.startswith("/channels/"):
            guild_channels.append(link)
    return {"dms": dms, "guild_channels": guild_channels,
            "dm_count": len(dms), "guild_channel_count": len(guild_channels)}


def current_channel():
    target = resolve_page_target()
    value = evaluate(target["webSocketDebuggerUrl"], CHANNEL_TITLE_JS) or {}
    return {"target_id": target["id"], "title": target.get("title", ""),
            "url": value.get("url", target.get("url", "")),
            "channel_title": value.get("title", ""),
            "composer_present": value.get("composer", False)}


def send_message(channel_id, text):
    """Focus the composer, insert text, press Enter. Returns CDP send result."""
    opened = open_channel(channel_id)
    target = resolve_page_target()
    ws_url = target["webSocketDebuggerUrl"]
    # The channel view may still be rendering after navigation (observed
    # 2026-11-24: "composer not found" right after a slow read). Wait for it.
    _wait_for(ws_url,
              "!!document.querySelector('div[role=\"textbox\"][contenteditable=\"true\"]')",
              timeout=15, what="composer")
    result = _run_node(["send", ws_url, text])
    result["channel_id"] = str(channel_id)
    result["url"] = opened["url"]
    return result


def send_file(channel_id, file_path, text=""):
    """Upload a file via the composer's file input, optional caption, Enter to send."""
    path = Path(file_path).expanduser()
    if not path.is_file():
        raise DiscordError(f"File not found: {file_path}")
    opened = open_channel(channel_id)
    target = resolve_page_target()
    ws_url = target["webSocketDebuggerUrl"]
    _wait_for(ws_url, "!!document.querySelector('input[type=file]')",
              timeout=15, what="file input")
    args = ["sendfile", ws_url, str(path)]
    if text:
        args.append(text)
    result = _run_node(args)
    result["channel_id"] = str(channel_id)
    result["url"] = opened["url"]
    return result


def status():
    """Read-only status: process, CDP, target, current channel."""
    running = cdp_reachable()
    info = {"discord_running": running, "cdp_port": CDP_PORT,
            "cdp_url": f"http://127.0.0.1:{CDP_PORT}/json/version"}
    if not running:
        return info
    try:
        version = _http_json("/json/version")
        info.update({"browser": version.get("Browser"), "protocol": version.get("Protocol-Version")})
    except Exception:
        pass
    try:
        target = resolve_page_target()
        info.update({"target_id": target["id"], "target_title": target.get("title"),
                     "target_url": target.get("url")})
        info.update(current_channel())
    except DiscordError as e:
        info["target_error"] = str(e)
    return info
