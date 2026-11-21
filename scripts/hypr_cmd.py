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
"""
import os

HYPR_RUNTIME_DIR = "/run/user/1000"
HYPR_SIGNATURE_DIR = "/run/user/1000/hypr"
WAYLAND_DISPLAY = "wayland-1"

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
