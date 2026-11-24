"""Session state for cli-anything-discord.

JSON session file holding the CDP endpoint, resolved page target and current
channel, so one-shot subcommands share state with the REPL. Saves use the
HARNESS exclusive-lock pattern (guides/session-locking.md): open "r+",
lock, then truncate inside the lock. Never bare open("w") + json.dump().
"""

import json
import os
from pathlib import Path

DEFAULT_SESSION_PATH = Path.home() / ".cli-anything-discord" / "session.json"

DEFAULT_SESSION = {
    "cdp_port": 9229,
    "target_id": None,
    "current_channel_id": None,
    "current_channel_name": None,
    "updated_at": None,
}


def _locked_save_json(path, data, **dump_kwargs):
    """Atomically write JSON with exclusive file locking."""
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        f = open(path, "w")
    with f:
        locked = False
        try:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, **dump_kwargs)
            f.flush()
        finally:
            if locked:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def load_session(path=None):
    path = Path(path) if path else DEFAULT_SESSION_PATH
    session = dict(DEFAULT_SESSION)
    if path.is_file():
        try:
            with open(path) as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                session.update(stored)
        except (json.JSONDecodeError, OSError):
            pass
    return session


def save_session(session, path=None):
    from datetime import datetime, timezone
    path = Path(path) if path else DEFAULT_SESSION_PATH
    session = dict(session)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    _locked_save_json(str(path), session, indent=2)
    return session


def set_current_channel(channel_id, channel_name=None, path=None):
    session = load_session(path)
    session["current_channel_id"] = str(channel_id)
    if channel_name:
        session["current_channel_name"] = channel_name
    save_session(session, path)
    return session
