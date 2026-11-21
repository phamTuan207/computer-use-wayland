"""Omarchy CLI surfaces for agents (pure builders + usage reader).

Mirrors the stock Omarchy commands Worker OA inventoried
(improvements/omarchy-agentic-surfaces-20261121.md). Nothing here touches
the desktop: every function returns argv, or reads one local JSON file.
Runners execute the argv; the usage reader is for the watchdog.

Rules:
- OMARCHY_PATH is the fixed upstream install path. Commands that need it
  (agent usage, plugin list, omarchy-shell) crash over plain SSH without
  it; cu.environment() sets it when the directory exists. These builders
  do not set env themselves; they only build argv.
- GUI-only modes are rejected, never silently downgraded: screenshot
  region/windows/scroll need a mouse pick; menu select/input/file need a
  GUI pick; capture text needs a slurp region (only its grim + tesseract
  pipeline is reusable headless, via ocr below).
- NEVER agent prompt (wrong default agent, auto-approve), NEVER community
  MCP servers, NEVER account exec/use switching, NEVER refresh/update/
  restart. Those are excluded by the owner (OA section 6).
"""
import argparse
import json
import os
import re
import sys

OMARCHY_DEFAULT_PATH = "/usr/share/omarchy"
USAGE_STATE_DIR = os.path.expanduser("~/.local/state/omarchy/agents/usage")

_AGENT_RE = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
_GEOMETRY_RE = re.compile(r"(\d+),(\d+) (\d+)x(\d+)")
_URGENCIES = ("low", "normal", "critical")
_SCREENSHOT_MODES = ("smart", "fullscreen")
_SCREENSHOT_DESTS = ("copy", "save")
_SHELL_CALLS = {("shell", "ping"): 0, ("shell", "listPlugins"): 0,
                ("shell", "toggle"): 1}
_MENU_ACTIONS = ("toggle", "summon", "close", "refresh", "ping")
_ROUTE_RE = re.compile(r"[A-Za-z0-9_.\-]+")
_TESSERACT_ARGV = ["tesseract", "stdin", "stdout", "--oem", "1", "--psm",
                   "6", "-l", "eng", "--dpi", "300", "-c",
                   "preserve_interword_spaces=1"]


def omarchy_path(default=None):
    """The Omarchy install path, or None when this is not an Omarchy box."""
    if default is None:
        default = OMARCHY_DEFAULT_PATH
    return default if os.path.isdir(default) else None


def with_omarchy_path(env, default=None):
    """Copy env with OMARCHY_PATH set when unset and the install exists.

    Never overrides an explicit value. Returns the env unchanged on
    machines without /usr/share/omarchy. The default resolves at call
    time so tests can point it at a fixture directory.
    """
    if default is None:
        default = OMARCHY_DEFAULT_PATH
    out = dict(env)
    if not out.get("OMARCHY_PATH") and os.path.isdir(default):
        out["OMARCHY_PATH"] = default
    return out


def shell_argv(target, method, arg=None):
    """omarchy-shell IPC argv. Allowlist only: shell ping/listPlugins/toggle.

    The toggle arg must be a JSON object string (the route to toggle).
    This is the stock command route for the menu-by-command rule and the
    closest thing to an agent API in stock Omarchy.
    """
    key = (target, method)
    if key not in _SHELL_CALLS:
        raise ValueError("unsupported omarchy-shell call: %s %s" % key)
    if _SHELL_CALLS[key] == 0 and arg is not None:
        raise ValueError("omarchy-shell %s %s takes no argument" % key)
    if _SHELL_CALLS[key] == 1 and arg is None:
        raise ValueError("omarchy-shell %s %s needs a JSON object argument"
                         % key)
    argv = ["omarchy-shell", target, method]
    if arg is not None:
        try:
            parsed = json.loads(arg)
        except ValueError:
            raise ValueError("omarchy-shell toggle arg must be JSON") from None
        if not isinstance(parsed, dict):
            raise ValueError("omarchy-shell toggle arg must be a JSON object")
        argv.append(arg)
    return argv


def menu_argv(action, route=None):
    """omarchy menu argv: toggle/summon/close/refresh/ping, optional route.

    Routes look like "system" or "appearance.theme". This is the command
    form of the menu-by-command rule; never click the bar menu button.
    """
    if action not in _MENU_ACTIONS:
        raise ValueError("menu action must be one of %s, got: %r"
                         % (", ".join(_MENU_ACTIONS), action))
    argv = ["omarchy", "menu", action]
    if route is not None:
        if (not isinstance(route, str) or not _ROUTE_RE.fullmatch(route)
                or route.startswith("-")):
            raise ValueError("bad menu route: %r" % (route,))
        argv.append(route)
    return argv


def notify_argv(headline, description=None, urgency="normal", app_name=None,
                action=None, exec_cmd=None):
    """omarchy notification send argv, with optional clickable action.

    action is (label, program, [args...]); exec_cmd is (program, [args...]).
    At most one of action / exec_cmd. Urgency is low/normal/critical.
    Use for user-facing fleet alerts (blocker needs the owner, live run
    done, approval needed) with an action button, not chat alone.
    """
    if not isinstance(headline, str) or not headline or "\n" in headline:
        raise ValueError("headline must be a non-empty single line")
    if description is not None and (
            not isinstance(description, str) or "\n" in description):
        raise ValueError("description must be a single line or None")
    if urgency not in _URGENCIES:
        raise ValueError("urgency must be one of %s, got: %r"
                         % (", ".join(_URGENCIES), urgency))
    if action is not None and exec_cmd is not None:
        raise ValueError("notification takes --action or --exec, not both")
    argv = ["omarchy", "notification", "send"]
    if app_name is not None:
        if not isinstance(app_name, str) or not app_name:
            raise ValueError("app_name must be a non-empty string")
        argv += ["--app-name", app_name]
    if urgency != "normal":
        argv += ["-u", urgency]
    argv.append(headline)
    if description:
        argv.append(description)
    if action is not None:
        parts = _action_parts(action)
        argv += ["--action", parts[0], parts[1]] + parts[2:]
    if exec_cmd is not None:
        parts = _exec_parts(exec_cmd)
        argv += ["--exec", parts[0]] + parts[1:]
    return argv


def _action_parts(action):
    if (not isinstance(action, (tuple, list)) or len(action) < 2
            or not all(isinstance(p, str) and p for p in action[:2])
            or not all(isinstance(p, str) for p in action[2:])):
        raise ValueError(
            "action must be (label, program, [args...]) of non-empty strings")
    return list(action)


def _exec_parts(exec_cmd):
    if (not isinstance(exec_cmd, (tuple, list)) or len(exec_cmd) < 1
            or not all(isinstance(p, str) and p for p in exec_cmd)):
        raise ValueError("exec_cmd must be (program, [args...]) of strings")
    return list(exec_cmd)


def screenshot_argv(mode="fullscreen", dest="save"):
    """omarchy capture screenshot argv (omasnap fallback).

    Only smart/fullscreen are CLI-safe. region/windows/scroll need a GUI
    pick and are rejected here; use computer-use observe instead.
    """
    if mode not in _SCREENSHOT_MODES:
        raise ValueError(
            "screenshot mode %r needs a GUI pick; use smart or fullscreen"
            % (mode,))
    if dest not in _SCREENSHOT_DESTS:
        raise ValueError("screenshot dest must be copy or save, got: %r"
                         % (dest,))
    return ["omarchy", "capture", "screenshot", mode, dest]


def grim_argv(geometry):
    """grim argv for one region capture. Geometry is "X,Y WxH"."""
    _check_geometry(geometry)
    return ["grim", "-g", geometry, "-"]


def tesseract_argv():
    """tesseract argv matching the omarchy capture-text pipeline."""
    return list(_TESSERACT_ARGV)


def ocr_shell(geometry):
    """Shell pipeline for headless OCR of one region (no slurp pick).

    Geometry is supplied by the caller (from a DOM rect or a known
    window box), never picked with the mouse. Returns the pipeline
    string; run it through a shell.
    """
    _check_geometry(geometry)
    return ("grim -g '%s' - | tesseract stdin stdout --oem 1 --psm 6 "
            "-l eng --dpi 300 -c preserve_interword_spaces=1" % geometry)


def _check_geometry(geometry):
    if not isinstance(geometry, str):
        raise ValueError("geometry must be a string like '0,0 800x600'")
    match = _GEOMETRY_RE.fullmatch(geometry)
    if not match:
        raise ValueError("geometry must look like 'X,Y WxH', got: %r"
                         % (geometry,))
    x, y, w, h = (int(g) for g in match.groups())
    if not (0 <= x < 100000 and 0 <= y < 100000
            and 0 < w <= 100000 and 0 < h <= 100000):
        raise ValueError("geometry out of range: %r" % (geometry,))


def _as_int(value, field):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("usage field %r is not an int: %r" % (field, value))
    return value


def read_usage(agent, state_dir=None):
    """Read one agent's Omarchy usage JSON into a summary dict.

    The files live at ~/.local/state/omarchy/agents/usage/<agent>.json.
    Agent names are lowercase provider ids (codex, claude, opencode...);
    the "muse" slot tracks Meta's Muse coding agent, not this agent, and
    reads all zeros here. Raises FileNotFoundError when the file is
    absent and ValueError on a bad name or malformed content.
    """
    if not isinstance(agent, str) or not _AGENT_RE.fullmatch(agent):
        raise ValueError("bad agent name: %r" % (agent,))
    directory = state_dir or USAGE_STATE_DIR
    path = os.path.join(directory, agent + ".json")
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "no Omarchy usage file for agent %r at %s" % (agent, path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except ValueError:
        raise ValueError("malformed usage JSON at %s" % path) from None
    if not isinstance(data, dict):
        raise ValueError("usage JSON at %s is not an object" % path)
    limits = []
    for entry in data.get("limits") or []:
        if not isinstance(entry, dict):
            raise ValueError("usage limit entry is not an object: %r"
                             % (entry,))
        limits.append({"label": entry.get("label"),
                       "percent": entry.get("percent"),
                       "resets_at": entry.get("resetsAt")})
    models = data.get("todayTokensByModel") or {}
    if not isinstance(models, dict):
        raise ValueError("todayTokensByModel is not an object")
    return {
        "agent": data.get("id", agent),
        "updated_at": data.get("updatedAt"),
        "tier": data.get("tierLabel"),
        "ready": bool(data.get("ready")),
        "today_prompts": _as_int(data.get("todayPrompts", 0),
                                 "todayPrompts"),
        "today_sessions": _as_int(data.get("todaySessions", 0),
                                  "todaySessions"),
        "today_tokens": _as_int(data.get("todayTotalTokens", 0),
                                "todayTotalTokens"),
        "today_tokens_by_model": {k: _as_int(v, "todayTokensByModel")
                                  for k, v in models.items()},
        "limits": limits,
        "total_prompts": _as_int(data.get("totalPrompts", 0),
                                 "totalPrompts"),
        "total_sessions": _as_int(data.get("totalSessions", 0),
                                  "totalSessions"),
        "active_days": _as_int(data.get("activeDays", 0), "activeDays"),
    }


def usage_summary_text(summary):
    """One log line for a usage summary (watchdog-friendly)."""
    parts = ["%s: today %d prompts / %s tokens" % (
        summary["agent"], summary["today_prompts"],
        format(summary["today_tokens"], ","))]
    models = summary["today_tokens_by_model"]
    if models:
        parts.append("(%s)" % ", ".join(
            "%s %s" % (name, format(tokens, ","))
            for name, tokens in sorted(models.items())))
    for limit in summary["limits"]:
        resets = (limit["resets_at"] or "").split("T")[0]
        parts.append("%s %s%% resets %s" % (
            limit["label"], limit["percent"], resets))
    parts.append("total %d prompts / %d sessions / %d active days" % (
        summary["total_prompts"], summary["total_sessions"],
        summary["active_days"]))
    return "; ".join(parts)


def usage_cli_argv(agent, limits_only=True):
    """omarchy agent usage argv (needs OMARCHY_PATH set in the env)."""
    if not isinstance(agent, str) or not _AGENT_RE.fullmatch(agent):
        raise ValueError("bad agent name: %r" % (agent,))
    argv = ["omarchy", "agent", "usage", agent]
    if limits_only:
        argv.append("--limits-only")
    return argv


def main(argv=None):
    """CLI for the watchdog: `omarchy_cmd.py usage <agent>`.

    Reads the local usage JSON and prints the one-line summary. With
    --argv it prints the `omarchy agent usage` argv instead of reading.
    """
    parser = argparse.ArgumentParser(
        prog="omarchy_cmd.py",
        description="Read Omarchy agent usage (watchdog helper).")
    sub = parser.add_subparsers(dest="command", required=True)
    usage = sub.add_parser("usage", help="print one agent usage summary")
    usage.add_argument("agent", help="provider id, e.g. codex")
    usage.add_argument("--state-dir", default=None,
                       help="usage JSON dir (default ~/.local/state/omarchy/agents/usage)")
    usage.add_argument("--argv", action="store_true",
                       help="print the omarchy agent usage argv, do not read")
    args = parser.parse_args(argv)
    if args.command == "usage":
        if args.argv:
            print(" ".join(usage_cli_argv(args.agent)))
            return 0
        try:
            summary = read_usage(args.agent, state_dir=args.state_dir)
        except (FileNotFoundError, ValueError) as exc:
            print("usage: %s" % exc, file=sys.stderr)
            return 1
        print(usage_summary_text(summary))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
