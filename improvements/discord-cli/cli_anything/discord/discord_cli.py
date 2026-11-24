"""cli-anything-discord: message read/send control for the Discord desktop client.

Subcommand CLI + REPL (HARNESS Phase 2/3). Every command supports --json.
Backend: the real Discord desktop client over CDP (utils/discord_backend.py).
"""

import json
import shlex
import sys

import click

from cli_anything.discord.core import session as session_mod
from cli_anything.discord.utils import discord_backend as backend
from cli_anything.discord.utils.repl_skin import ReplSkin

VERSION = "1.0.0"
TEST_DM_CHANNEL_ID = backend.TEST_DM_CHANNEL_ID

COMMANDS_HELP = {
    "status": "Discord process, CDP endpoint, current channel",
    "servers list": "List servers from the server rail",
    "channels list": "List DMs and guild channels",
    "channels open <id>": "Navigate the client to a channel (sets current channel)",
    "messages read [id]": "Read messages in a channel (default: current channel)",
    "messages send [id] --text ...": "Send a message (test DM only unless you know the risk)",
    "messages send-file [id] --file ...": "Send a file with optional caption",
    "session start": "Launch Discord with CDP if not running",
    "session attach": "Attach to the running Discord CDP endpoint",
    "session show": "Show the session file",
    "session stop": "Quit Discord (explicit only)",
    "repl": "Interactive REPL (also the default with no arguments)",
    "quit / exit": "Leave the REPL",
}


def _emit(ctx, data):
    """Human-readable or machine-readable output, per --json."""
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        _pretty(data)


def _pretty(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{k}:")
                click.echo(json.dumps(v, indent=2, ensure_ascii=False))
            else:
                click.echo(f"{k}: {v}")
    else:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def _fail(ctx, message):
    if ctx.obj.get("json"):
        click.echo(json.dumps({"ok": False, "error": message}, indent=2))
    else:
        click.echo(f"Error: {message}", err=True)
    raise SystemExit(1)


def _channel_or_current(ctx, channel_id):
    if channel_id:
        return channel_id
    current = session_mod.load_session().get("current_channel_id")
    if current:
        return current
    _fail(ctx, "No channel given and no current channel in session. "
               "Run `channels open <channelId>` first (test DM: 865272264831139840).")


@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, help="Machine-readable JSON output.")
@click.option("--session-file", type=click.Path(), default=None,
              help="Session file path (default ~/.cli-anything-discord/session.json).")
@click.pass_context
def cli(ctx, as_json, session_file):
    """Discord message control via the real desktop client (CDP)."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json
    ctx.obj["session_file"] = session_file
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# --- status ------------------------------------------------------------

@cli.command()
@click.pass_context
def status(ctx):
    """Show Discord process, CDP endpoint and current channel (read-only)."""
    try:
        data = backend.status()
        data["session"] = session_mod.load_session(ctx.obj.get("session_file"))
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


# --- servers -----------------------------------------------------------

@cli.group()
def servers():
    """List servers (read-only)."""


@servers.command("list")
@click.pass_context
def servers_list(ctx):
    """List servers from the server rail."""
    try:
        data = backend.list_servers()
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


# --- channels ----------------------------------------------------------

@cli.group()
def channels():
    """List and open channels/DMs."""


@channels.command("list")
@click.option("--dm", "only_dm", is_flag=True, help="Only DM channels.")
@click.option("--guild", "only_guild", is_flag=True, help="Only guild channels.")
@click.pass_context
def channels_list(ctx, only_dm, only_guild):
    """List DM and guild channels visible in the sidebar."""
    try:
        data = backend.list_channels()
        if only_dm:
            data = {"dms": data["dms"], "dm_count": data["dm_count"]}
        elif only_guild:
            data = {"guild_channels": data["guild_channels"],
                    "guild_channel_count": data["guild_channel_count"]}
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


@channels.command("open")
@click.argument("channel_id")
@click.pass_context
def channels_open(ctx, channel_id):
    """Navigate the Discord client to a channel and set it as current."""
    try:
        opened = backend.open_channel(channel_id)
        info = backend.current_channel()
        sess = session_mod.set_current_channel(channel_id, info.get("channel_title"),
                                               ctx.obj.get("session_file"))
        sess["target_id"] = opened.get("target_id")
        session_mod.save_session(sess, ctx.obj.get("session_file"))
        data = {"ok": True, **opened, "channel_title": info.get("channel_title")}
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


# --- messages ----------------------------------------------------------

@cli.group()
def messages():
    """Read and send messages."""


@messages.command("read")
@click.argument("channel_id", required=False)
@click.option("--limit", "-n", default=20, show_default=True,
              help="Max messages to return (viewport window only).")
@click.pass_context
def messages_read(ctx, channel_id, limit):
    """Read messages in a channel (default: current channel)."""
    channel_id = _channel_or_current(ctx, channel_id)
    try:
        data = backend.read_messages(channel_id, limit=limit)
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


@messages.command("send")
@click.argument("channel_id", required=False)
@click.option("--text", "-t", required=True, help="Message text to send.")
@click.pass_context
def messages_send(ctx, channel_id, text):
    """Send a message to a channel (default: current channel)."""
    channel_id = _channel_or_current(ctx, channel_id)
    try:
        data = backend.send_message(channel_id, text)
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


@messages.command("send-file")
@click.argument("channel_id", required=False)
@click.option("--file", "-f", "file_path", required=True, help="File to upload.")
@click.option("--text", "-t", default="", help="Optional caption text.")
@click.pass_context
def messages_send_file(ctx, channel_id, file_path, text):
    """Send a file to a channel (default: current channel)."""
    channel_id = _channel_or_current(ctx, channel_id)
    try:
        data = backend.send_file(channel_id, file_path, text)
        data["ok"] = True
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


# --- session -----------------------------------------------------------

@cli.group()
def session():
    """Manage the Discord session (launch / attach / stop)."""


@session.command("start")
@click.pass_context
def session_start(ctx):
    """Launch Discord with CDP on port 9229 if not already running."""
    try:
        data = backend.ensure_running()
        target = backend.resolve_page_target()
        data.update({"ok": True, "target_id": target["id"],
                     "target_url": target.get("url")})
        session_mod.save_session({**session_mod.load_session(ctx.obj.get("session_file")),
                                  "target_id": target["id"]},
                                 ctx.obj.get("session_file"))
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


@session.command("attach")
@click.pass_context
def session_attach(ctx):
    """Attach to the running Discord CDP endpoint (fails loudly if down)."""
    if not backend.cdp_reachable():
        _fail(ctx, "Discord CDP is not reachable on port 9229. "
                   "Run `session start` to launch Discord with --remote-debugging-port=9229.")
    try:
        target = backend.resolve_page_target()
        data = {"ok": True, "attached": True, "target_id": target["id"],
                "target_title": target.get("title"), "target_url": target.get("url")}
        session_mod.save_session({**session_mod.load_session(ctx.obj.get("session_file")),
                                  "target_id": target["id"]},
                                 ctx.obj.get("session_file"))
    except backend.DiscordError as e:
        _fail(ctx, str(e))
    _emit(ctx, data)


@session.command("show")
@click.pass_context
def session_show(ctx):
    """Show the session file contents."""
    _emit(ctx, {"ok": True, **session_mod.load_session(ctx.obj.get("session_file"))})


@session.command("stop")
@click.option("--force", is_flag=True, help="Actually quit the Discord client.")
@click.pass_context
def session_stop(ctx, force):
    """Quit Discord. Requires --force; never implicit."""
    if not force:
        _fail(ctx, "Refusing to quit Discord without --force. "
                   "Run `session stop --force` if you really mean it.")
    import subprocess
    # Process comm is "Discord" (capital D) on this install; `pkill -x discord`
    # matches nothing (verified 2026-11-24: pgrep -x discord rc=1, -x Discord
    # matches). Try the real name first, lowercase as a fallback.
    proc = subprocess.run(["pkill", "-x", "Discord"], capture_output=True, text=True)
    if proc.returncode != 0:
        proc = subprocess.run(["pkill", "-x", "discord"], capture_output=True, text=True)
    _emit(ctx, {"ok": proc.returncode in (0, 1),
                "message": "Discord quit (pkill discord)." if proc.returncode == 0
                else "No Discord process found."})


# --- REPL --------------------------------------------------------------

@cli.command()
@click.pass_context
def repl(ctx):
    """Interactive REPL (default when no subcommand is given)."""
    skin = ReplSkin("discord", version=VERSION)
    skin.print_banner()
    skin.warning("ToS risk: automating a user account can lead to account "
                 "termination if detected. Test DM only unless you accept the risk.")
    pt_session = skin.create_prompt_session()
    while True:
        try:
            line = skin.get_input(
                pt_session,
                context=session_mod.load_session().get("current_channel_name") or "",
            )
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line in ("quit", "exit"):
            break
        if line == "help":
            skin.help(COMMANDS_HELP)
            continue
        try:
            args = shlex.split(line)
        except ValueError as e:
            skin.error(f"Could not parse line: {e}")
            continue
        # Route through the Click group with --json off (REPL is human mode).
        try:
            cli.main(args=args, standalone_mode=False,
                     obj={"json": False, "session_file": ctx.obj.get("session_file")})
        except SystemExit as e:
            if e.code not in (0, None):
                skin.error(f"Command failed (exit {e.code}). Type 'help' for commands.")
        except Exception as e:  # noqa: BLE001 - REPL must never die on one bad line
            skin.error(str(e))
    skin.print_goodbye()


def main():
    cli()


if __name__ == "__main__":
    main()
