"""Hyprland command builders (pure, no desktop access).

Exact hyprctl dispatch strings for the operations agents need most.
Workspace focus was verified live on the owner's machine 2026-11-21
(ws1 <-> ws2 in ~1s); the rest use the same proven hl.dsp object form
(Hyprland 0.57.2 Lua). Runners and cron bodies should use these builders
(or copy their exact strings) instead of hand-writing dispatch forms.

Rules baked in here (do not bypass):
- NEVER the string dispatcher form (hyprctl dispatch workspace N): broken.
- NEVER hl.dsp.workspace.goto: goto is a Lua reserved word.
- Signature discovery: ls /run/user/1000/hypr/ (NOT hyprland/, which is empty).
- focus_app / launch-or-focus mirror the omarchy scripts of the same
  names (same match order, same hl.dsp focus form); the omarchy
  `focuswindow address:...` string-dispatch fallback is NOT emitted
  (broken on this Hyprland, KB proved rc=7).
"""
import os
import re

HYPR_RUNTIME_DIR = "/run/user/1000"
HYPR_SIGNATURE_DIR = "/run/user/1000/hypr"
WAYLAND_DISPLAY = "wayland-1"
AGENT_WINDOW_CLASS = "org.omarchy.agent"
_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")

_DIRECTIONS = ("l", "r", "u", "d")


def dispatch_argv(lua):
    """hyprctl argv for one hl.dsp Lua expression."""
    if not isinstance(lua, str) or not lua.strip():
        raise ValueError("dispatch needs a non-empty hl.dsp expression")
    if not lua.strip().startswith("hl.dsp."):
        raise ValueError("dispatch takes hl.dsp.* only, got: %r" % lua)
    if "workspace.goto" in lua:
        raise ValueError(
            "hl.dsp.workspace.goto is unusable: goto is a Lua reserved "
            "word; use hl.dsp.focus({ workspace = N }) instead")
    return ["hyprctl", "dispatch", lua]


def focus_workspace(n):
    """Switch to workspace N (int 1..10). Proven live 2026-11-21."""
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 10:
        raise ValueError("workspace must be an int 1..10, got: %r" % (n,))
    return dispatch_argv("hl.dsp.focus({ workspace = %d })" % n)


def focus_next_workspace():
    return dispatch_argv('hl.dsp.focus({ workspace = "m+1" })')


def focus_prev_workspace():
    return dispatch_argv('hl.dsp.focus({ workspace = "m-1" })')


def focus_former_workspace():
    return dispatch_argv(
        'hl.dsp.focus({ workspace = "previous_per_monitor" })')


def focus_direction(d):
    """Focus the window left/right/up/down of the active one."""
    if d not in _DIRECTIONS:
        raise ValueError("direction must be one of l/r/u/d, got: %r" % (d,))
    return dispatch_argv('hl.dsp.focus({ direction = "%s" })' % d)


def close_window():
    return dispatch_argv("hl.dsp.window.close()")


def focus_app_clients_argv():
    """hyprctl argv listing clients as JSON (input to pick_focus_address)."""
    return ["hyprctl", "clients", "-j"]


def _compile_pattern(pattern):
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("pattern must be a non-empty string")
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError("pattern is not a valid regex: %r (%s)"
                         % (pattern, exc)) from None


def _sorted_by_focus(clients):
    """Clients ordered most-recently-focused first (lowest focusHistoryID)."""
    def key(client):
        history = client.get("focusHistoryID")
        if isinstance(history, bool) or not isinstance(history, int):
            return 1 << 62
        return history
    return sorted(clients, key=key)


def _address_of(client):
    address = client.get("address")
    if isinstance(address, str) and _ADDRESS_RE.fullmatch(address):
        return address
    return None


def pick_focus_address(clients, pattern):
    """Pick a window address to focus, mirroring omarchy-hyprland-focus-app.

    clients is the parsed `hyprctl clients -j` list. Match by class regex
    first, then fall back to the launch-time title of agent windows
    (class org.omarchy.agent, whose terminal name lives only in
    initialTitle). Among matches take the most recently focused one.
    Returns the address string, or None when nothing matches.
    """
    if not isinstance(clients, list):
        raise ValueError("clients must be a list (parsed hyprctl -j)")
    regex = _compile_pattern(pattern)
    ordered = _sorted_by_focus(clients)
    for client in ordered:
        if not isinstance(client, dict):
            continue
        if regex.search(client.get("class") or ""):
            address = _address_of(client)
            if address:
                return address
    for client in ordered:
        if not isinstance(client, dict):
            continue
        if (client.get("initialClass") == AGENT_WINDOW_CLASS
                and regex.search(client.get("initialTitle") or "")):
            address = _address_of(client)
            if address:
                return address
    return None


def focus_window_argv(address):
    """Focus one window by address (hl.dsp form, proven live 2026-11-21).

    The omarchy script falls back to `hyprctl dispatch focuswindow
    address:...`, but that string-dispatcher form is broken on Hyprland
    0.57.2 Lua (KB proved rc=7), so it is deliberately NOT emitted here.
    """
    if not isinstance(address, str) or not _ADDRESS_RE.fullmatch(address):
        raise ValueError("address must look like 0x..., got: %r"
                         % (address,))
    return dispatch_argv('hl.dsp.focus({ window = "address:%s" })' % address)


def pick_launch_or_focus_address(clients, pattern):
    """Pick a window address for launch-or-focus, mirroring omarchy.

    The pattern is a plain app name, matched as a whole word
    (case-insensitive) against class or title, first match in clients
    order. Unlike pick_focus_address there is no focus-history sort:
    omarchy takes the first match (head -n1). Returns the address or
    None when nothing matches.
    """
    if not isinstance(clients, list):
        raise ValueError("clients must be a list (parsed hyprctl -j)")
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("pattern must be a non-empty string")
    regex = re.compile(r"\b%s\b" % re.escape(pattern), re.IGNORECASE)
    for client in clients:
        if not isinstance(client, dict):
            continue
        if (regex.search(client.get("class") or "")
                or regex.search(client.get("title") or "")):
            address = _address_of(client)
            if address:
                return address
    return None


def launch_or_focus_cmd(pattern, launch_cmd=None):
    """Shell command to run when launch-or-focus finds no window.

    Default is `uwsm-app -- <pattern>`, as in the omarchy script. The
    caller runs this (via setsid) only when pick_launch_or_focus_address
    returns None; when it returns an address, use focus_window_argv.
    """
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("pattern must be a non-empty string")
    if launch_cmd is None:
        return "uwsm-app -- %s" % pattern
    if not isinstance(launch_cmd, str) or not launch_cmd:
        raise ValueError("launch_cmd must be a non-empty string")
    return launch_cmd


def desktop_env(signature=None, signature_dir=HYPR_SIGNATURE_DIR):
    """Env mapping for GUI commands over SSH.

    Prefers an explicit signature, then the live
    HYPRLAND_INSTANCE_SIGNATURE, then the first directory under
    /run/user/1000/hypr/. Fails closed when no signature can be found.
    """
    sig = signature or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if sig is None:
        try:
            names = sorted(os.listdir(signature_dir))
        except OSError as exc:
            raise ValueError(
                "cannot list Hyprland signature dir %s: %s"
                % (signature_dir, exc))
        if not names:
            raise ValueError(
                "no Hyprland instance signature under %s "
                "(hyprland/ is empty; use hypr/)" % signature_dir)
        sig = names[0]
    return {
        "XDG_RUNTIME_DIR": HYPR_RUNTIME_DIR,
        "WAYLAND_DISPLAY": WAYLAND_DISPLAY,
        "HYPRLAND_INSTANCE_SIGNATURE": sig,
    }
