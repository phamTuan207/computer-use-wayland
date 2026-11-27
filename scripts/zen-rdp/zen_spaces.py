#!/usr/bin/env python3
"""Typed Spaces/Folders list+create wrappers over the RDP parent target.

Adoption item P4 (improvements/zen-mcp-adoption-decision-20261127.md):
one audited implementation of the gZenWorkspaces / gZenFolders calls
instead of hand-written chrome JS per callsite. Call knowledge ported
from improvements/zen-sidebar/zen_live.py (JS_LIST / JS_CREATE_FOLDER)
and verified live against the Zen build on 2026-11-27; the Marionette
transport is NOT ported. Every wrapper goes through
RDPClient.parent_evaluate, so the existing parent-context gate
(allow_parent / --allow-parent) and the drive-report audit
(parent_evaluates + action counts) apply unchanged. This module owns
the JS strings; callers pass typed arguments only.

Scope is list + create ONLY (4 wrappers). Move/switch mutate visible
owner state and are a separate later decision. Removal operations are
rejected by charter, permanently, and are absent by construction:
no wrapper and no JS string for them exists in this module. The
pinned method set below is the whole surface; rdp_smoke asserts it
on every run so a Zen update that renames an internal fails loud.

createAndSaveWorkspace is async and RDP evaluateJSAsync does not
await promises (verified live: it returns a Promise grip), so
create_space fires the call, stores the outcome on a token-keyed
global slot, and polls that slot with a bounded timeout. It passes
dontChange=true: creating a space never switches the visible space.

Stdlib only. Sends no OS input; ydotool is banned and not used.
"""
import json
import secrets
import time

from rdp_client import RDPError

# The whole P4 surface. Smoke asserts each is a function on the
# parent target; anything beyond this set is out of scope by design.
PINNED_METHODS = (
    "gZenWorkspaces.getWorkspaces",
    "gZenWorkspaces.createAndSaveWorkspace",
    "gZenFolders.createFolder",
)

_JS_LIST_SPACES = (
    "JSON.stringify({"
    "activeWorkspace: gZenWorkspaces.activeWorkspace, "
    "spaces: [...gZenWorkspaces.getWorkspaces()].map(w => ({"
    "uuid: w.uuid, name: w.name, containerTabId: w.containerTabId}))})"
)

_JS_LIST_FOLDERS = (
    "JSON.stringify({folders: gBrowser.tabGroups"
    ".filter(g => g.isZenFolder).map(g => ({"
    "id: g.id, label: g.label, collapsed: g.collapsed, "
    "workspace: g.getAttribute('zen-workspace-id'), "
    "tabCount: g.tabs ? g.tabs.length : null}))})"
)

# Tabs are selected by URL substring, resolved inside the chrome JS
# so tab indexes never go stale between calls (zen_live.py pattern).
# Exactly one match per part is required; anything else throws.
_JS_CREATE_FOLDER = (
    "JSON.stringify((() => {"
    "const parts = %s; const label = %s;"
    "const tabs = parts.map(p => {"
    "const hits = gBrowser.tabs.filter(t => "
    "((t.linkedBrowser && t.linkedBrowser.currentURI && "
    "t.linkedBrowser.currentURI.spec) || '').includes(p));"
    "if (hits.length !== 1) throw new Error("
    "'tab selector matched ' + hits.length + ' tabs for ' + "
    "JSON.stringify(p));"
    "return hits[0];});"
    "const f = gZenFolders.createFolder(tabs, {label});"
    "return {id: f.id, label: f.label};"
    "})())"
)


def _parse_json_result(raw, what):
    """parent_evaluate returns the JSON string our JS produced.
    Anything else (grip dict, non-JSON) is a loud failure."""
    if not isinstance(raw, str):
        raise RDPError(f"{what}: unexpected parent evaluate result "
                       f"{type(raw).__name__}: {str(raw)[:200]}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RDPError(f"{what}: parent evaluate returned non-JSON: "
                       f"{raw[:200]!r} ({e})")


def _require_nonempty_str(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string, "
                         f"got {value!r}")
    return value


def list_spaces(client):
    """{"activeWorkspace": uuid, "spaces": [{uuid, name,
    containerTabId}]}. Read-only; still parent-gated + audited."""
    return _parse_json_result(client.parent_evaluate(_JS_LIST_SPACES),
                              "list_spaces")


def list_folders(client):
    """{"folders": [{id, label, collapsed, workspace, tabCount}]}."""
    return _parse_json_result(client.parent_evaluate(_JS_LIST_FOLDERS),
                              "list_folders")


def create_space(client, name="Space", timeout=10.0):
    """Create a space without switching to it (dontChange=true).
    Returns {"uuid": ..., "name": ...}. Raises RDPError on JS
    failure or when the async create does not settle in time."""
    _require_nonempty_str(name, "name")
    if not (isinstance(timeout, (int, float)) and timeout > 0):
        raise ValueError(f"timeout must be > 0, got {timeout!r}")
    slot_key = secrets.token_hex(8)
    slot = f"globalThis.__zenSpacesPending[{json.dumps(slot_key)}]"
    fire = (
        "globalThis.__zenSpacesPending = "
        "globalThis.__zenSpacesPending || {};"
        f"{slot} = {{done: false}};"
        f"gZenWorkspaces.createAndSaveWorkspace("
        f"{json.dumps(name)}, undefined, true)"
        f".then(w => {{ {slot} = {{done: true, ok: !!w, "
        "uuid: w ? w.uuid : null, name: w ? w.name : null}; })"
        f".catch(e => {{ {slot} = {{done: true, ok: false, "
        "error: String(e)}; });"
        f"{json.dumps(slot_key)}"
    )
    client.parent_evaluate(fire)
    poll = f"JSON.stringify({slot} || null)"
    deadline = time.monotonic() + timeout
    while True:
        state = _parse_json_result(client.parent_evaluate(poll),
                                   "create_space poll")
        if isinstance(state, dict) and state.get("done"):
            break
        if time.monotonic() >= deadline:
            raise RDPError(
                f"create_space: createAndSaveWorkspace did not settle "
                f"within {timeout}s (name={name!r})")
        time.sleep(0.05)
    try:
        client.parent_evaluate(f"{slot} = undefined; true")
    except Exception:
        pass  # slot cleanup is best-effort; the create already settled
    if not state.get("ok"):
        raise RDPError(
            f"create_space: createAndSaveWorkspace failed: "
            f"{state.get('error') or 'returned no workspace'}")
    return {"uuid": state.get("uuid"), "name": state.get("name")}


def create_folder(client, label, tab_urls):
    """Create a folder holding the tabs matched by URL substrings
    (exactly one tab per part). Returns {"id": ..., "label": ...}.
    Note: Zen's createFolder pins the tabs it groups."""
    _require_nonempty_str(label, "label")
    if not isinstance(tab_urls, (list, tuple)) or not tab_urls:
        raise ValueError("tab_urls must be a non-empty list of URL "
                         f"substrings, got {tab_urls!r}")
    for part in tab_urls:
        _require_nonempty_str(part, "tab_urls entry")
    expr = _JS_CREATE_FOLDER % (json.dumps(list(tab_urls)),
                                json.dumps(label))
    return _parse_json_result(client.parent_evaluate(expr),
                              "create_folder")


def pinned_method_types(client):
    """{pinned method: typeof} read live from the parent target."""
    expr = "JSON.stringify({" + ", ".join(
        f"{json.dumps(m)}: typeof {m}" for m in PINNED_METHODS) + "})"
    return _parse_json_result(client.parent_evaluate(expr),
                              "pinned_method_types")


def assert_pinned_methods(client):
    """Fail loud unless every pinned method is a function. Returns
    the type map. Used by rdp_smoke after every Zen update."""
    types = pinned_method_types(client)
    bad = {k: v for k, v in types.items() if v != "function"}
    if bad or set(types) != set(PINNED_METHODS):
        raise RDPError(f"pinned Spaces/Folders methods not all "
                       f"functions: {types}")
    return types
