"""Validate the complete Hyprland plugin list before a first-load."""
import json
import re

import indicator


FIELDS = {'name', 'author', 'handle', 'version', 'description'}
HANDLE = re.compile(r'[0-9a-fA-F]+\Z')


def parse(value):
    """Decode and structurally validate one complete `plugin list` response."""
    if isinstance(value, str):
        if len(value.encode()) > 65536:
            raise RuntimeError('plugin inventory exceeds bounds')
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError) as error:
            raise RuntimeError('invalid plugin inventory JSON') from error
    if not isinstance(value, list):
        raise RuntimeError('plugin inventory must be a list')
    names, handles = set(), set()
    for plugin in value:
        if not isinstance(plugin, dict) or set(plugin) != FIELDS:
            raise RuntimeError('malformed plugin inventory entry')
        if any(not isinstance(plugin[key], str) for key in FIELDS):
            raise RuntimeError('malformed plugin inventory entry')
        if not plugin['name'] or not plugin['author'] or not plugin['version']:
            raise RuntimeError('malformed plugin inventory entry')
        if not HANDLE.fullmatch(plugin['handle']):
            raise RuntimeError('malformed plugin handle')
        if plugin['name'] in names or plugin['handle'].lower() in handles:
            raise RuntimeError('duplicate plugin inventory entry')
        names.add(plugin['name'])
        handles.add(plugin['handle'].lower())
    return value


def _verified_hyprbars(plugin):
    return (plugin['name'] == 'hyprbars' and plugin['author'] == 'Vaxry' and
            plugin['version'] == '1.0')


def setup_baseline(value):
    """Return stable identity for no plugins or the one accepted hyprbars build.

    Hyprland assigns a new handle when a plugin is loaded in a new compositor.
    The handle is still structurally validated by parse(), but it is not part
    of the cross-startup plugin identity used by this baseline.
    """
    plugins = parse(value)
    if not plugins or (len(plugins) == 1 and _verified_hyprbars(plugins[0])):
        return [{'name':plugin['name'],'author':plugin['author'],
                 'version':plugin['version']} for plugin in plugins]
    raise RuntimeError('unsupported plugin inventory; expected none or verified hyprbars 1.0')


def setup_snapshot(value):
    """Validate the accepted setup set and retain a full same-session snapshot."""
    plugins=parse(value)
    setup_baseline(plugins)
    return plugins


def cursor_baseline(value):
    """Cursor first-load requires the accepted glass and allows known hyprbars."""
    plugins = parse(value)
    by_name = {plugin['name']: plugin for plugin in plugins}
    if set(by_name) not in ({'hyprglass'}, {'hyprglass', 'hyprbars'}):
        raise RuntimeError('cursor first-load requires accepted glass and optional verified hyprbars')
    if by_name['hyprglass']['version'] != indicator.LIQUID_VERSION:
        raise RuntimeError('cursor first-load requires the accepted glass version')
    if 'hyprbars' in by_name and not _verified_hyprbars(by_name['hyprbars']):
        raise RuntimeError('cursor first-load found unverified hyprbars')
    return plugins


def assert_glass_added(before, after):
    baseline = setup_snapshot(before)
    current = cursor_baseline(after)
    retained = [plugin for plugin in current if plugin['name'] != 'hyprglass']
    if retained != baseline:
        raise RuntimeError('plugin inventory changed during glass first-load')
    return current


def assert_guard_added(before, after):
    baseline = cursor_baseline(before)
    current = parse(after)
    by_name = {plugin['name']: plugin for plugin in current}
    guard = by_name.get('computer-use-cursor')
    if (guard is None or guard['author'] != 'computer-use-wayland' or
            guard['version'] != '1.0.0'):
        raise RuntimeError('cursor guard first-load did not publish its accepted plugin')
    retained = [plugin for plugin in current if plugin['name'] != 'computer-use-cursor']
    if retained != baseline:
        raise RuntimeError('plugin inventory changed during cursor guard first-load')
    return current
