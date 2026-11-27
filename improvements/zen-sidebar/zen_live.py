#!/usr/bin/env python3
"""Live Zen Browser sidebar control via Marionette chrome-context JS.

Zen folders, workspaces and pinned tabs have no public API, but Zen's
chrome exposes them as per-window globals, reachable by running
JavaScript in Marionette's chrome context (system principal) on the
Marionette listener Zen already exposes (127.0.0.1:2828):

  gZenWorkspaces        src/zen/spaces/ZenSpaceManager.mjs
  gZenFolders           src/zen/folders/ZenFolders.mjs
  gZenPinnedTabManager  src/zen/tabs/ZenPinnedTabManager.mjs

Operations (tabs are selected by URL substring, resolved inside the
page of chrome JS so tab indexes never go stale between calls):

  introspect     report which managers/methods this Zen build exposes
  list           workspaces, folders, tabs with workspace/folder/pin state
  switch-workspace --to SPACE_UUID
  move-workspace   --tab-url PART --to SPACE_UUID
  create-folder    --label NAME --tab-url PART [--tab-url PART ...]
  move-folder      --tab-url PART --to FOLDER_ID     (folder.addTabs)
  leave-folder     --tab-url PART                    (gBrowser.ungroupTab)
  move-folder-space --folder FOLDER_ID --to SPACE_UUID
  pin / unpin      --tab-url PART
  move-tab         --tab-url PART --index N          (pinned reorder)

Every payload feature-detects the Zen API it needs and returns
{error: ...} instead of guessing when a build differs; Zen renames
these internals between versions. Start with `introspect`.

Transport: a minimal stdlib Marionette wire-protocol client (no pip
dependency). The same payloads run unchanged under Mozilla's
marionette_driver package (set_context("chrome") +
execute_async_script(js, script_args=[...], sandbox="system")) if the
raw command names ever drift; the namespaced protocol-3 names used
here (WebDriver:NewSession, Marionette:SetContext,
WebDriver:ExecuteAsyncScript, WebDriver:DeleteSession) are the first
thing `introspect` end-to-end verifies on a new machine. The greeting
is a length-prefixed frame like every other message, and async
completion is signalled by calling the callback Marionette appends as
the last script argument.

Launch gate: chrome-context (system principal) work requires Zen to
be launched with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 in its environment;
without it setContext fails with "System access is required". On a
bare VM Zen also needs a D-Bus session bus (dbus-run-session) or
startup stalls before the Marionette listener opens. After the
2026-11-27 RDP switch, the owner's live Zen no longer opens a
Marionette listener at all; this tool targets throwaway profiles
launched with --marionette (see
improvements/zen-r17-continuation-20261127.md).

WARNING: a Marionette session is full system-principal control of the
browser profile. Keep the listener on localhost only, and test on a
throwaway profile before touching a live one.
"""

import argparse
import json
import socket
import sys

# ---------- JS payloads (chrome context, system principal) ----------

_PRELUDE = """
const done = (v) => { try { arguments[arguments.length - 1](v); } catch (e) {} };
const fail = (msg) => done({ error: String(msg) });
const pickTab = (part) => {
  const hits = gBrowser.tabs.filter(
    (t) => ((t.linkedBrowser && t.linkedBrowser.currentURI && t.linkedBrowser.currentURI.spec) || "").includes(part)
  );
  if (hits.length !== 1) throw new Error(`tab selector matched ${hits.length} tabs`);
  return hits[0];
};
const need = (name) => {
  if (typeof window[name] === "undefined") throw new Error(`${name} is not exposed in this Zen build`);
};
"""

JS_INTROSPECT = _PRELUDE + """
(async () => {
  try {
    const proto = (o) => { try { return Object.getOwnPropertyNames(Object.getPrototypeOf(o)); } catch (e) { return []; } };
    done({
      userAgent: navigator.userAgent,
      hasGZenWorkspaces: typeof gZenWorkspaces !== "undefined",
      hasGZenFolders: typeof gZenFolders !== "undefined",
      hasGZenPinnedTabManager: typeof gZenPinnedTabManager !== "undefined",
      workspacesMethods: typeof gZenWorkspaces !== "undefined" ? proto(gZenWorkspaces) : [],
      foldersMethods: typeof gZenFolders !== "undefined" ? proto(gZenFolders) : [],
      pinnedMethods: typeof gZenPinnedTabManager !== "undefined" ? proto(gZenPinnedTabManager) : [],
      moveTabToWorkspace: typeof gZenWorkspaces !== "undefined" ? typeof gZenWorkspaces.moveTabToWorkspace : "n/a",
      moveTabToExistingGroup: typeof gBrowser.moveTabToExistingGroup,
      moveTabToGroup: typeof gBrowser.moveTabToGroup,
      activeWorkspace: typeof gZenWorkspaces !== "undefined" ? gZenWorkspaces.activeWorkspace : null,
    });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_LIST = _PRELUDE + """
(async () => {
  try {
    need("gZenWorkspaces"); need("gZenFolders");
    const folders = gBrowser.tabGroups.filter((g) => g.isZenFolder).map((g) => ({
      id: g.id, label: g.label, collapsed: g.collapsed,
      workspace: g.getAttribute("zen-workspace-id"),
      tabCount: g.tabs ? g.tabs.length : null,
    }));
    const tabs = gBrowser.tabs.map((t, i) => ({
      index: i,
      url: (t.linkedBrowser && t.linkedBrowser.currentURI && t.linkedBrowser.currentURI.spec) || "",
      pinned: !!t.pinned,
      essential: t.hasAttribute("zen-essential"),
      workspace: t.getAttribute("zen-workspace-id"),
      folder: t.group && t.group.isZenFolder ? t.group.id : null,
    }));
    done({
      activeWorkspace: gZenWorkspaces.activeWorkspace,
      workspaces: [...gZenWorkspaces.getWorkspaces()].map((w) => ({ uuid: w.uuid, containerTabId: w.containerTabId })),
      folders, tabs,
    });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_SWITCH_WORKSPACE = _PRELUDE + """
(async () => {
  try {
    need("gZenWorkspaces");
    await gZenWorkspaces.changeWorkspaceWithID(arguments[0]);
    done({ activeWorkspace: gZenWorkspaces.activeWorkspace });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_MOVE_WORKSPACE = _PRELUDE + """
(async () => {
  try {
    need("gZenWorkspaces");
    if (typeof gZenWorkspaces.moveTabToWorkspace !== "function") {
      return fail("gZenWorkspaces.moveTabToWorkspace is not a function in this build; run introspect and check the build's method list before using any fallback");
    }
    const tab = pickTab(arguments[0]);
    await gZenWorkspaces.moveTabToWorkspace(tab, arguments[1]);
    done({ url: tab.linkedBrowser.currentURI.spec, workspace: tab.getAttribute("zen-workspace-id") });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_CREATE_FOLDER = _PRELUDE + """
(async () => {
  try {
    need("gZenFolders");
    const [label, ...parts] = arguments[0];
    const tabs = parts.map((p) => pickTab(p));
    const folder = gZenFolders.createFolder(tabs, { label });
    done({ folderId: folder.id, label: folder.label });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_MOVE_FOLDER = _PRELUDE + """
(async () => {
  try {
    const tab = pickTab(arguments[0]);
    const folder = gBrowser.tabGroups.find((g) => g.id === arguments[1] && g.isZenFolder);
    if (!folder) return fail(`no Zen folder with id ${arguments[1]} (see list)`);
    folder.addTabs([tab]);
    done({ url: tab.linkedBrowser.currentURI.spec, folder: tab.group ? tab.group.id : null });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_LEAVE_FOLDER = _PRELUDE + """
(async () => {
  try {
    const tab = pickTab(arguments[0]);
    gBrowser.ungroupTab(tab);
    done({ url: tab.linkedBrowser.currentURI.spec, folder: tab.group ? tab.group.id : null,
           note: "raw ungroupTab; verify Zen folder bookkeeping followed (see research report)" });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_MOVE_FOLDER_SPACE = _PRELUDE + """
(async () => {
  try {
    need("gZenFolders");
    const folder = gBrowser.tabGroups.find((g) => g.id === arguments[0] && g.isZenFolder);
    if (!folder) return fail(`no Zen folder with id ${arguments[0]} (see list)`);
    await gZenFolders.changeFolderToSpace(folder, arguments[1]);
    done({ folderId: folder.id, workspace: folder.getAttribute("zen-workspace-id") });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_PIN = _PRELUDE + """
(async () => {
  try {
    const tab = pickTab(arguments[0]);
    if (arguments[1]) { gBrowser.pinTab(tab); } else { gBrowser.unpinTab(tab); }
    done({ url: tab.linkedBrowser.currentURI.spec, pinned: !!tab.pinned });
  } catch (e) { fail(e && e.stack || e); }
})();
"""

JS_MOVE_TAB = _PRELUDE + """
(async () => {
  try {
    const tab = pickTab(arguments[0]);
    gBrowser.moveTabTo(tab, { tabIndex: arguments[1] });
    done({ url: tab.linkedBrowser.currentURI.spec, index: gBrowser.tabs.indexOf(tab) });
  } catch (e) { fail(e && e.stack || e); }
})();
"""


# ---------- minimal Marionette wire client (stdlib only) ----------

class MarionetteError(Exception):
    pass


class Marionette:
    """Marionette protocol 3: greeting JSON, then length-prefixed frames
    of [type, messageId, name, params] / [type, messageId, error, result]."""

    def __init__(self, host="127.0.0.1", port=2828, timeout=30):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.msgid = 0
        self.greeting = self._read_greeting()

    def _fill(self):
        chunk = self.sock.recv(65536)
        if not chunk:
            raise MarionetteError("connection closed by server")
        self.buf += chunk

    def _read_greeting(self):
        # The greeting is a length-prefixed frame like every other
        # message: b'50:{"applicationType":"gecko","marionetteProtocol":3}'.
        # Parsing it as bare JSON reads the "50" as a number and leaves
        # ":{...}" in the buffer, which then breaks the first frame read.
        return self._read_frame()

    def _read_frame(self):
        while b":" not in self.buf:
            self._fill()
        size_raw, _, rest = self.buf.partition(b":")
        size = int(size_raw)
        while len(rest) < size:
            self._fill()
            _, _, rest = self.buf.partition(b":")
        self.buf = rest[size:]
        return json.loads(rest[:size].decode("utf-8"))

    def command(self, name, params=None):
        self.msgid += 1
        payload = json.dumps([0, self.msgid, name, params or {}]).encode("utf-8")
        self.sock.sendall(str(len(payload)).encode("ascii") + b":" + payload)
        msg = self._read_frame()
        if not isinstance(msg, list) or len(msg) < 4:
            raise MarionetteError(f"malformed response to {name}: {msg!r}")
        if msg[1] != self.msgid:
            raise MarionetteError(
                f"response id {msg[1]} does not match request id {self.msgid} for {name}")
        _, _, error, result = msg[:4]
        if error:
            raise MarionetteError(f"{name} failed: {error}")
        return result

    def new_session(self):
        return self.command("WebDriver:NewSession", {"capabilities": {}})

    def set_context(self, context):
        return self.command("Marionette:SetContext", {"value": context})

    def execute_async(self, script, args=()):
        # sandbox="system" asks Marionette for a system-principal sandbox,
        # the documented privilege mechanism for chrome-context work.
        result = self.command("WebDriver:ExecuteAsyncScript",
                              {"script": script, "args": list(args), "sandbox": "system"})
        # WebDriver wraps script results as {"value": ...}; unwrap so
        # callers see the payload's own return shape.
        if isinstance(result, dict) and set(result) == {"value"}:
            return result["value"]
        return result

    def close(self):
        try:
            self.command("WebDriver:DeleteSession")
        except Exception:
            pass
        self.sock.close()


# ---------- CLI ----------

def run_op(client, args):
    client.new_session()
    client.set_context("chrome")
    # Lazy: only the chosen subcommand's arguments are dereferenced.
    # argparse defines --to/--tab-url/--label/... only for the
    # subcommand actually chosen, so an eager table crashes on
    # unrelated attributes.
    ops = {
        "introspect": lambda: (JS_INTROSPECT, ()),
        "list": lambda: (JS_LIST, ()),
        "switch-workspace": lambda: (JS_SWITCH_WORKSPACE, (args.to,)),
        "move-workspace": lambda: (JS_MOVE_WORKSPACE, (args.tab_url, args.to)),
        "create-folder": lambda: (JS_CREATE_FOLDER, ([args.label] + list(args.tab_url_multi),)),
        "move-folder": lambda: (JS_MOVE_FOLDER, (args.tab_url, args.to)),
        "leave-folder": lambda: (JS_LEAVE_FOLDER, (args.tab_url,)),
        "move-folder-space": lambda: (JS_MOVE_FOLDER_SPACE, (args.folder, args.to)),
        "pin": lambda: (JS_PIN, (args.tab_url, True)),
        "unpin": lambda: (JS_PIN, (args.tab_url, False)),
        "move-tab": lambda: (JS_MOVE_TAB, (args.tab_url, args.index)),
    }
    script, script_args = ops[args.cmd]()
    return client.execute_async(script, script_args)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2828)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("introspect")
    sub.add_parser("list")
    for name in ("switch-workspace", "move-workspace", "move-folder"):
        p = sub.add_parser(name)
        p.add_argument("--to", required=True)
        if name != "switch-workspace":
            p.add_argument("--tab-url", required=True)
    p = sub.add_parser("create-folder")
    p.add_argument("--label", required=True)
    p.add_argument("--tab-url", dest="tab_url_multi", action="append", required=True)
    p = sub.add_parser("leave-folder")
    p.add_argument("--tab-url", required=True)
    p = sub.add_parser("move-folder-space")
    p.add_argument("--folder", required=True)
    p.add_argument("--to", required=True)
    for name in ("pin", "unpin"):
        p = sub.add_parser(name)
        p.add_argument("--tab-url", required=True)
    p = sub.add_parser("move-tab")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--index", type=int, required=True)

    args = ap.parse_args(argv)
    client = Marionette(args.host, args.port)
    try:
        result = run_op(client, args)
    finally:
        client.close()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if isinstance(result, dict) and result.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
