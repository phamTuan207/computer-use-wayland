"""Persist the re-observe requirement across commands in one guarded session.

Call mutations and the final pre-input check while holding the caller's desktop lock.
"""
import json
import os
import re
import tempfile


def marker_path(state, token):
    if not token:
        return None
    if not re.fullmatch(r'[0-9a-f]{32}', token):
        raise RuntimeError('invalid automation session token')
    return state / ('session-reobserve-' + token + '.json')


def read_marker(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, 'rb') as stream:
        raw = stream.read(4097)
    if len(raw) > 4096:
        raise RuntimeError('invalid re-observe marker')
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        raise RuntimeError('invalid re-observe marker') from None
    if (not isinstance(value, dict) or set(value) != {'observation'} or
            value['observation'] is not None and
            (not isinstance(value['observation'], str) or not value['observation'] or
             len(value['observation'].encode('utf-8')) > 4096)):
        raise RuntimeError('invalid re-observe marker')
    return value


def write_marker(state, path, observation):
    raw = json.dumps({'observation': observation}, ensure_ascii=False).encode('utf-8')
    if len(raw) > 4096:
        raise RuntimeError('invalid re-observe marker')
    fd, temporary = tempfile.mkstemp(prefix='.reobserve-', dir=state)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def record_refusal(state, token):
    path = marker_path(state, token)
    if path is not None:
        read_marker(path)  # A corrupt existing requirement must remain fail-closed.
        write_marker(state, path, None)


def record_observation(state, token, result):
    path = marker_path(state, token)
    if path is None or read_marker(path) is None:
        return
    observation = result.get('observation') if isinstance(result, dict) else None
    if (not isinstance(observation, str) or not observation or
            len(observation.encode('utf-8')) > 4096 or result.get('ok') is False):
        raise RuntimeError('fresh desktop observation required')
    write_marker(state, path, observation)


def require_observation(state, token, observation=None):
    path = marker_path(state, token)
    marker = read_marker(path) if path is not None else None
    if marker is None:
        return
    fresh = marker['observation']
    if fresh is None or observation is not None and observation != fresh:
        raise RuntimeError('fresh desktop observation required after transient refusal')


def complete_requirement(state, token):
    """Consume a validated requirement only after a successful input batch."""
    path = marker_path(state, token)
    if path is not None and read_marker(path) is not None:
        path.unlink()
