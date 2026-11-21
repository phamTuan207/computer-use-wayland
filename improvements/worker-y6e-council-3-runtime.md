# Council Voice 3 (runtime behavior + containment): Y6e risk review of hyprglass 03a57c4

- Reviewer: Council Voice 3, runtime behavior + containment only. Reviewer only: no commit, no checkout, no build, no load, no git commands inside the vendor repo.
- Target: fetched commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd, diff 99f30ca..03a57c4.
- Evidence: `improvements/worker-y6e-rebuild-load-log.md` (read in full), `improvements/y6e-evidence/diff-99f30ca-03a57c4.txt` (10,070 lines, md5 71ee7ccaef91e73bc61dd1cbebd8e521), `Makefile-pin`, `Makefile-diff.txt`, `hyprpm-pin.toml`, `workflows-diff.txt`, `hyprland-version-pin`, `scan-added.txt`, `scan-removed.txt`.
- Date: 2026-11-21, evening (+07).
- Line numbers below are diff-file lines unless a file name is given.

## 1. LoadGuard: what it does at load time

I read `src/LoadGuard.cpp` in full (new file, 73 lines, diff 6076-6154) and `src/LoadGuard.hpp` in full (46 lines, diff 6155-6206).

`PLUGIN_INIT` (diff 9789) does the guard first, before anything that depends on Hyprland's internal layout (comment at diff 9820): `LoadGuard::checkCompatibility(handle)` at diff 9821.

`checkCompatibility` (diff 6094) runs two checks in order:

1. Identity: `HyprlandIdentity::compare(GIT_TAG, GIT_COMMIT_HASH, running.tag, running.hash, BUILT_FOR_HYPRLAND_GIT)` (diff 6098). A `Mismatch` returns at once with reason `HyprlandVersion` and a message of the form "built for Hyprland X, running Y" (diff 6099-6104).
2. Dependencies: the ABI suffix of `__hyprland_api_get_hash()` (running) vs `__hyprland_api_get_client_hash()` (compiled in). A difference returns reason `Dependencies` with the differing libraries named (diff 6106-6115).

The identity comparison itself (`src/HyprlandIdentity.hpp`, `compare`, diff 6019) is release-line based because `BUILT_FOR_HYPRLAND_GIT` is `false` (diff 1185): `releaseLine` (diff 5978) parses only major.minor, so "v0.57.0" and "v0.57.2" are the same line (0.57) and match. The `.hyprland-version` file at the pin saying 0.57.0 while the installed compositor is 0.57.2 is therefore a non-issue for the load test: patch releases do not pause. Same commit also matches. Anything else with usable tags on both sides mismatches; with no usable tag or commit on one side the verdict is `Unknown`, not `Mismatch`, and the plugin proceeds (see the note in section 5).

The `GIT_TAG` / `GIT_COMMIT_HASH` macros on the built side describe the Hyprland the plugin was built against, not the plugin repo: the CI workflow greps exactly `#define GIT_TAG "v..."` from `/usr/include/hyprland/src/version.h` (diff line 42). The log's note that no tag points at the pin locally (shallow clone, tags not fetched) therefore does not weaken this check; the build uses the installed Hyprland 0.57.2 headers, which carry a release tag.

### Does the version check still enforce?

Yes. The old escape hatch was removed from `main.cpp` (removed lines, diff 9804-9816: the old `getenv` plus the warning-downgrade), and the `getenv` now lives in `LoadGuard::skipRequested()` (diff 6133-6136). The check moved, it did not disappear.

`skipRequested()` returns true only when `HYPRGLASS_SKIP_VERSION_CHECK` is set in Hyprland's own environment, non-empty, and not "0" (diff 6134-6135). The skip path in `PLUGIN_INIT` (diff 9823-9828):

- A failed verdict with no skip requested returns `pausedDescription(handle, verdict)` (diff 9823-9824). The copy stays listed with reason `Paused (<reason>): <message>` and draws nothing.
- A failed verdict with skip requested posts a visible 10-second notification, "check skipped (HYPRGLASS_SKIP_VERSION_CHECK), Hyprland may crash" (diff 9825-9827), and loading continues. The skip is also recorded: `g_pGlobalState->versionCheck = LoadGuard::checkResult(verdict)` (diff 9838) reports "skipped" in `hyprctl hyprglass status` (text line diff 1941, JSON field diff 1927-1930).

So the check cannot be silently skipped: skipping needs an explicit env var in the compositor's own environment (not something the plugin sets for itself, and not something a config line can smuggle in without the operator writing it), it produces an on-screen notification, and it leaves "skipped" in the status output. Nobody sets that variable in the nested load test plan, so the default path is enforce-or-pause.

### Duplicate-copy guard

`otherActiveCopyPath()` (diff 6117-6131) runs after the version verdict (diff 9831), and it is NOT skippable: the skip branch above only covers version verdicts. The README states this explicitly too (diff line 936: the variable loads hyprglass "despite the version checks above, not despite another copy").

It walks `g_pPluginSystem->getAllPlugins()`, looks for another entry named hyprglass, and `dlsym`s `hyprglass_instance_active` from that copy's handle (diff 6126). Logic:

- Symbol missing (an older copy, pre-dating the guard): treated as active, blocks.
- Symbol present and returns true: active, blocks.
- Symbol present and returns false (a newer copy that is paused): does not block.

The active flag is the file-static `s_instanceActive` (diff 9773), exported through `hyprglass_instance_active()` (diff 9776-9778), set true only after the guard passes (diff 9835) and cleared in `PLUGIN_EXIT` (diff 10043). On a duplicate load, `PLUGIN_INIT` returns `pausedDescription` with reason `Duplicate`, message "already loaded from <path>" (diff 9831-9832), and registers nothing.

A paused copy registers nothing at all: no hook, decoration, listener, config value, hyprctl command, protocol global, or GL object (LoadGuard.hpp comment, diff 6172-6174). `PLUGIN_INIT` returns before `PHANDLE` is assigned, before any listener is added, and before `Diagnostics::registerHyprCtlCommand` (diff 9942). A paused copy therefore has no `hyprctl hyprglass` command: `hyprctl hyprglass status` answers `unknown request` (README, diff line 850). `PLUGIN_EXIT` is also a no-op for a paused copy (`if (!s_instanceActive ...) return`, diff 10039-10043).

One subtlety worth recording, not a defect: a copy paused for `Duplicate` stays listed in `hyprctl plugin list` with its reason as the description, and `PLUGIN_INIT` returns normally instead of throwing, so Hyprland does not report a failed load. That is deliberate (comment diff 9781-9782).

## 2. findFunctionsByName and the nm invocation

I read `resolveHyprlandFunction` in full (diff 9750-9768) and both call sites (diff 9975, 10012).

Important correction to the log's phrasing: the `nm` invocation is not in hyprglass code. It lives in Hyprland's own `HyprlandAPI::findFunctionsByName` (Hyprland's `PluginAPI.cpp`). The diff contains only a comment describing it (diff 9750-9753) and a comment noting `nm --demangle=auto` output (diff 9742). My grep over added lines found no `nm`, `popen`, `system(`, `fork(`, or `exec` call in hyprglass code. What hyprglass does:

- `resolveHyprlandFunction` tries `dlsym(RTLD_DEFAULT, mangledName)` first, and accepts the result only if `dladdr` shows it lives in the same object as Hyprland's own `findFunctionsByName` (diff 9756-9759). That check rejects a same-named symbol from any other loaded object.
- Only if the `dlsym` path fails does it call `HyprlandAPI::findFunctionsByName(PHANDLE, fallbackSearch)` (diff 9761), which is the path where Hyprland itself forks `nm` on the Hyprland binary. The fallback match must then pass an exact predicate: the renderLayer fallback accepts only the exact demangled signature (diff 9975-9977), the renderPassAdd fallback requires the demangled name to contain `CRenderPass::add` and `IPassElement` (diff 10012-10014).

When it runs: both call sites are inside `PLUGIN_INIT` (hook setup, new main.cpp around lines 803 and 929), so at load time only, once per load, never per frame and never on demand later. There is no path or command string in hyprglass code to audit: the exact `nm` argv and the binary path it runs on are Hyprland's implementation, not in this diff, and I cannot verify them from the evidence in scope. If the council wants the exact command, read Hyprland 0.57.2's `PluginAPI.cpp`; it is outside this review.

Failure behavior if `nm` is missing or its output is unexpected: the fallback returns no match (or no acceptable match), `resolveHyprlandFunction` returns null, the hook pointer stays null, and the plugin continues with that feature degraded. Both results are null-checked before use (`renderLayerAddress != nullptr`, diff 9978; `renderPassAddAddress`, diff 10015; `renderPassAddSymbolFound` records the miss, diff 10031). The old code had the same shape (direct `findFunctionsByName` calls, removed lines diff 9961 and 10002); the new code only adds the `dlsym`-first fast path, which makes the `nm` fork less likely, not more. Worst case is a missing hook and a later notification about it, not a crash and not a hang in plugin code. The comment's own cost note stands: when the fallback does run, it forks from the compositor and slows startup (diff 9750-9751). In the nested load test that cost lands on the nested compositor only.

## 3. hyprctl commands and Lua config surface

### hyprctl

`Diagnostics::registerHyprCtlCommand` (diff 1984-2006) registers one command, `hyprglass`, prefix-matched. The diff changes the registration from the old `SHyprCtlCommand` API to the new `IPC::Socket1::SCommand` API (diff 1985-1993). Subcommands in the handler:

- Default / status: `formatStatus`, text plus JSON. New in this diff: a `versionCheck` field, "match" / "unknown" / "skipped" (diff 1927-1930, 1941).
- `stats reset`: resets the diagnostics counters only (diff 2000-2003). This is the only mutating subcommand, and it mutates in-memory counters.
- `items`: read-only listing via `formatItems` (diff 2006; the formatter itself is unchanged apart from the output-format type, diff 1797).

My grep over the whole diff found only two `rest ==` comparisons ("stats reset", "items"): no new subcommand name is added. No new hyprctl power: no config writes, no plugin load/unload, no process control, no file access from the handler. The handler only formats strings and resets counters.

### Lua config surface

The config moves to Hyprland 0.57's Lua-only config (CHANGELOG, diff lines 116, 139). The plugin's Lua-facing code only reads tables handed to its callbacks: `lua_getfield`, `lua_rawgeti`, `lua_tonumber`, with finite checks (`luaFiniteNumber`, diff 6937; `luaPresetValue`, diff 6947; the inset reader clamps and requires finite sides, diff 7080-7100). My grep over added lines found no `luaL_dofile`, `luaL_loadfile`, `lua_register`, `lua_setglobal`, `os.execute`, or `io.popen` in plugin code; the only `os.execute` / `io.popen` hits are README documentation warning operators not to block startup with them (diff 940-946). The Lua entry points the operator sees (`hl.plugin.hyprglass.config({...})`, `hyprctl eval 'hl.plugin.hyprglass.config(...)'`, window tags such as `+hyprglass_disabled`, diff 424, 443, 467, 483, 502, 524, 547, 768-770) are config setters and tags: they change glass parameters and per-window preset selection. They give no file, process, or network access beyond what Hyprland's own Lua config already provides.

New runtime surface that is not a command but is worth naming: the `hyprglass_item_v1` Wayland protocol global, offered to clients so an app can hint its own preset and shape per item (README, diff line 712). It pre-exists v0.9.1; this diff does not add it. In the nested test it is offered only on the nested display, to nested clients.

### No runtime network, shell-out, or file write

Confirmed by my own re-read (see section 5): zero `system(`, `popen`, `fork(`, `exec`, `socket(`, `getaddrinfo`, `curl`, `wget`, `ofstream`, `fopen(`, filesystem-write, `chmod`, `setenv` hits in added code lines. The plugin's runtime writes are none; its runtime reads are the Hyprland binary (nm fallback, Hyprland's code), the Lua config tables, and GPU resources through Hyprland's renderer. GL framebuffer binds in added code (diff 1439-1440, 4350-4358) are render-path operations inside the compositor, not file or device access.

## 4. Containment: nested load test

The plan is: the rebuilt plugin loads ONLY into a nested Hyprland, never the live session (PID 1515).

Blast radius if the plugin crashes, hangs, or misbehaves inside the nest:

- Crash (segfault or abort in `PLUGIN_INIT`, in a render hook, or in a render pass element): the nested compositor process dies. The live Hyprland is the parent compositor and survives; the visible effect is the nested window closing. The live session, its windows, and the live Zen keep running.
- Hang (for example the `nm` fallback fork stalling during nested startup): the nested compositor stalls at startup only. It is killable with SIGKILL from the parent shell. Nothing in the live session blocks on it.
- Misbehavior (wrong glass, runaway resamples, GL errors): contained to the nested compositor's frames and its own windows. The new snapshot/frost/contour elements allocate GPU textures and a few MB while a layer exists and free them when the last one closes (README, diff line 41 and the `CGlassSnapshotElement` cleanup in `PLUGIN_EXIT`, diff 10036-10038); a leak would cost nested-process memory, reclaimed when the nested process exits.

What kills it: nested teardown. Killing the nested Hyprland process (SIGTERM, then SIGKILL if needed) ends everything the plugin owns. `PLUGIN_EXIT` withdraws the protocol global, removes the pass elements, and clears callbacks first (diff 10039-10070), but process exit is the backstop and does not depend on the plugin cooperating.

What could escape the nest:

- The helper `.so` with `RTLD_NODELETE`: it is embedded in `hyprglass.so` and dlopen'd with `RTLD_NODELETE` so it outlives a plugin unload (Makefile-pin lines 34-52; the mechanism is unchanged from v0.9.1). `RTLD_NODELETE` only prevents `dlclose` from unloading it inside a live process. It lives in the nested process address space and dies with that process. It cannot reach the live compositor. The residual effect is inside the nest only: unloading the plugin from a still-running nested compositor leaves the helper mapped, which is the pre-existing design.
- Shared files: the plugin runs as the same UID as the user, so it inherits the user's filesystem rights, but I verified it performs no file writes at runtime (section 3). The only file writes in the picture are Hyprland's own (logs, sockets) and the operator's. There is no home-dir write path in the added code.
- DBus, GPU state, network: no DBus use, no network use in added code. The nested compositor renders through the live compositor as its backend (Wayland backend, no direct DRM master), so a GL fault in the nest cannot wedge the live compositor's DRM master. At most the nested window goes black or dies.
- The real escape route is procedural, not in the code: if the nested launch shares the live config, the live socket, or the live plugin path, the rebuilt `.so` could be loaded into the live session by mistake. The code cannot prevent the operator pointing the live config at the rebuilt file. That is the one open containment link, and it is what the AMEND below closes.

## 5. Independent verification (re-read, not trusting the log)

I re-checked two of the log's load-bearing claims directly against the diff:

- Claim: "the old HYPRGLASS_SKIP_VERSION_CHECK escape hatch was REMOVED from main.cpp and the getenv now lives in LoadGuard.cpp." Verified. Removed lines at diff 9804-9816 delete the old `getenv` plus skip logic from `main.cpp`; added lines at diff 6133-6136 add `getenv` inside `LoadGuard::skipRequested()`; `PLUGIN_INIT` calls `skipRequested()` at diff 9823. The check moved, it did not disappear.
- Claim: "NO system(, popen, execl, execv, fork(, curl, wget, socket(, getaddrinfo, /dev/tcp, base64, constructor attribute, /etc/, HOME, chmod, setuid, LD_PRELOAD hits in added code." Verified by my own grep over `^+` lines of the full diff: zero hits for `system(`, `popen`, `fork(`, `exec`, `socket(`, `getaddrinfo`, `curl`, `wget`, `ofstream`, `fopen(`, `chmod`, `setenv`, `putenv`. The only `os.execute` / `io.popen` hits are README documentation (diff 940-946).
- Additional check of my own: the `GIT_TAG` question. The log notes no tag points at the pin locally (shallow clone). I confirmed this does not weaken the version check, because the built-side macros come from Hyprland's installed `version.h` (CI grep, diff line 42), not from the plugin repo. The live check for this is the nested `hyprctl hyprglass status` showing `version check: match` (see AMEND).

## Verdict: AMEND

One item, procedural, no code change required. It gates the nested LOAD, not the build: the build step (`make` in a separate worktree, no install, no load) loads nothing and is not implicated by anything in my scope.

AMEND: before the nested load test runs, Y6e must record the exact nested launch command and the pre/post checks in the log, and satisfy all of them:

1. The nested launch uses a copied config (never the live config file) and a distinct `WAYLAND_DISPLAY` / socket dir, with the rebuilt `.so` path referenced only from that copy.
2. Before the load, `hyprctl plugin list` on the live session shows no hyprglass entry pointing at the rebuilt path; after the nested test, the same check on the live session shows the live session unchanged.
3. After the nested load, nested `hyprctl hyprglass status` shows `version check: match` (not "unknown" and not "skipped"), confirming the LoadGuard identity check is live in the actual build. If it shows "unknown", the identity half of the guard is inert in that build and the load result is weaker (dependency check only); stop and report instead of proceeding to the C2 re-run.

Close the AMEND by writing the launch command and the three check outputs into `improvements/worker-y6e-rebuild-load-log.md`, then the load may proceed.

What is NOT blocking: the version check enforces and cannot be silently skipped; the duplicate guard is not skippable and a paused copy registers nothing; the `nm` fork is Hyprland's code, load-time fallback only, with null-checked degradation; no new hyprctl or Lua power and no runtime network, shell-out, or file write in the added code; a crash or hang inside the nest kills only the nested compositor. Subject to the AMEND above, there is no runtime or containment reason to refuse the load test.
