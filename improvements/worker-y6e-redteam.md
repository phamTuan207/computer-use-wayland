# Redteam paper: Worker Y6e risk review of hyprglass commit 03a57c4

- Reviewer: redteam (reviewer only). Date: 2026-11-21, 21:33 +07.
- Subject: fetched commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd (upstream v1.1.1) from https://github.com/hyprnux/hyprglass.git, as the gate for a rebuild with scripts/build-glass.py --local-optics and a nested-only load test.
- Method: read Y6e's log in full first; read Makefile-pin, Makefile-diff.txt, hyprpm-pin.toml, workflows-diff.txt, hyprland-version-pin, scan-added.txt, scan-removed.txt, scripts/build-glass.py; ran my own greps over the full 10,070 line diff (improvements/y6e-evidence/diff-99f30ca-03a57c4.txt, md5 71ee7ccaef91e73bc61dd1cbebd8e521, verified locally, 54 files); read the four new source files in full; independently ran `git ls-remote --tags` against the public GitHub URL from /tmp (reads refs only).
- Scope compliance: no commit, no checkout, no build, no load of the fetched commit; no git command inside the vendor repo. The only git command run was the read-only ls-remote above.
- Verdicts used: PROVEN (the attack works, with evidence), PLAUSIBLE (the attack could work, not yet proven or refuted), REFUTED (evidence kills the attack).

## 1. Supply chain

### A1. Fetch tampering: the fetched object differs from upstream v1.1.1
REFUTED. Git object IDs are content hashes, the fetch ran over https, and the build gate itself (build-glass.py) requires HEAD to equal the full SHA 03a57c4451b4abee38feda2ffb725f55ecc0f2fd. In-transit substitution would need a SHA-1 collision against git's hardened collision detection. The diff I reviewed is the artifact the build would consume, and its md5 matches the value in Y6e's log.

### A2. No tags fetched locally, so the v1.1.1 tag binding is unproven
REFUTED (closed during this review). The evidence file ls-remote-tags.txt lists `03a57c4451b4abee38feda2ffb725f55ecc0f2fd refs/tags/v1.1.1`. I independently ran live `git ls-remote --tags` from this VM and got the identical line. The tag is lightweight (no `^{}` deref line) and points directly at the pinned commit. Two independent sources now agree on the binding.

### A3. Release-bot authorship proves nothing about code safety
PROVEN as a statement, REFUTED as a bypass of this gate. The commit author github-actions[bot] with message "chore(release): v1.1.1 [skip ci]" proves only that the repo's release automation produced the commit. A compromised upstream account or automation could publish malicious code under the same author. The defense here does not rest on authorship; it rests on the hash binding (A1, A2) plus this line-level review of the diff. Upstream compromise is outside what any fetch-time check can catch, and is accepted on that basis.

### A4. Shallow-clone verification gaps
PLAUSIBLE in theory, REFUTED for this build. A shallow fetch does not verify ancestry, but ancestry is irrelevant: the build consumes the tree at one hash, and that hash is verified. The history-coherence note in Y6e's log (v0.9.1 to v1.1.1, issue refs #98/#99/#100/#102) is supporting color only, not a control. One verification genuinely missing: no `git verify-commit` record exists for 03a57c4. Release-please bot commits are typically unsigned, so the check would likely return "no signature", but the absence was never recorded as a known fact. See AMEND item 2.

### A5. Diff evidence integrity
REFUTED as a bypass. The diff was generated on the laptop and pulled in chunks with md5 verification. If the laptop vendor repo were tampered with, the diff would reflect the tamper, but this review reads the diff content line by line, so tamper would have to survive this review to reach the build. Boundary: the diff covers only 99f30ca..03a57c4. Code unchanged since v0.9.1 is not in the diff and was not reviewed here (see B5).

## 2. Hidden execution in the diff

### B1. system/popen/fork/exec/socket/curl/wget in added lines
REFUTED. My own grep over the full diff for `system\(|popen|execl|execv|posix_spawn|QProcess|fork\(|socket\(|curl|wget|getaddrinfo|/bin/sh|/dev/tcp|base64|LD_PRELOAD|setuid|chmod\(|setenv|putenv|environ|mktemp|tmpnam` returned zero code hits. Y6e's token scan (73 matches, scan-added.txt) agrees: all hits are CHANGELOG/README doc links, hyprctl usage examples, or legitimate Hyprland API calls.

### B2. __attribute__((constructor)) / static initializers running at dlopen
REFUTED for added code. No `__attribute__`, `atexit`, `__asm__`, or `\x` hex escapes in any added line. Namespace-scope statics in the new files are trivial (`static bool s_instanceActive = false`, main.cpp diff line 9773; constexpr arrays in Contour.cpp). No global C++ object with a non-trivial constructor exists in added code. Caveat: unchanged v0.9.1 code was not scanned (see B5).

### B3. Shell-outs via other spellings (execlp, std::system with a variable, backticks)
REFUTED for added lines. Covered by the B1 greps. Backtick appears only in README docs. The README warning about `io.popen`/`os.execute` (diff line 940) concerns the user's own hyprland.lua, not plugin behavior.

### B4. The nm invocation in findFunctionsByName
REFUTED as plugin-controlled execution. The `nm` fork lives in Hyprland's own PluginAPI.cpp, not in plugin code (comment, diff lines 9750-9752 and 9993-9995). The plugin calls HyprlandAPI::findFunctionsByName with fixed literals only: "renderLayer" (diff line 9975) and "CRenderPass3add" (diff line 10012). No config value, client input, or environment value reaches the search string, so no injection is possible from the plugin side. Worst case at load: a forked nm slows nested startup. The fallback runs only if the dlsym path fails, and the dlsym path is guarded by a dladdr same-object check (diff lines 9754-9759).

### B5. The item-helper C code and the protocol XML
PLAUSIBLE, OPEN. Neither src/item-helper/helper.c nor protocols/hyprglass-item-v1.xml is in the 99f30ca..03a57c4 diff (both unchanged since v0.9.1), so this review has no evidence of their content, yet the build compiles helper.c and the nest loads it. Partial evidence arrived after Y6e's log snapshot: item-helper-blob-pin.txt shows ItemHelperBlob.S (`.incbin "src/item-helper/hyprglass-item-helper.so"`, written to a memfd and dlopen'd from there at PLUGIN_INIT per the ItemHints.cpp comment) and the helper.c head (depends only on libwayland-server, no Hyprland headers, no C++). The helper BODY (request handlers, handling of client-supplied preset and shape values) and the protocol XML are still unread. This is the load-bearing open item. See AMEND item 1.

### B6. Shader strings escaping into code
REFUTED. Shaders are embedded GLSL string constants in Shaders.hpp (diff lines 8181-8934), compiled by the GL driver through Hyprland's createProgram, never executed as host code. Compile failure is handled: notification plus glass off until reload (ShaderManager.cpp, diff lines 7780-7846). loadShaderSource is called with fixed literals only ("liquidglass.frag", "contourseed.frag", "contouredt.frag", "contoursmooth.frag", "contourfield.frag"). Its body is unchanged v0.9.1 code, in the B5 bucket.

### B7. Makefile $(shell ...) calls
REFUTED as a fetched-code risk, with one environmental note. The calls are pkg-config (hyprland, pixman-1, libdrm, wayland-server), `$(CXX) --version | grep`, and the git describe branch (skipped, see C4). All resolve through PATH. A poisoned PATH could substitute pkg-config, wayland-scanner, or g++, but that requires prior compromise of the build environment, not of the fetched commit. Accepted as an environmental assumption; record it.

### B8. The four new files, read in full
REFUTED. LoadGuard.cpp (diff lines 6076-6155), Frost.cpp (2067-2150), Contour.cpp (1234-1555), GlassSnapshotElement.cpp (5020-5198) contain no file IO, no process creation, no network, and no environment access. They are GL render math, region math, and counters. The only environment read in the whole added codebase is LoadGuard::skipRequested getenv at diff line 6134; the only dlsym is LoadGuard::otherActiveCopyPath at diff line 6126. Boundary: this verdict covers added and changed lines only. Unchanged v0.9.1 code (ItemHints.cpp memfd/dlopen site, loadShaderSource body, PLUGIN_INIT helper wiring, the hyprctl handler body) also executes at build and load time and was not re-verified here. That is the B5 AMEND item, not a separate finding.

## 3. Build-script assumptions (scripts/build-glass.py)

### C1. Dirty-tree check bypass via ignored files
PROVEN gap in the gate. `git status --porcelain --untracked-files=all` does not list .gitignore'd files (nor .git/info/exclude nor global excludes). A prebuilt .o/.so or a dropped .hpp under src/ that is ignored would be invisible to the check. Practical exposure is limited to worktree reuse: in a fresh worktree nothing pre-exists. Mitigations already present: `make -B` rebuilds every target unconditionally, and the link line is explicit (no wildcards), so a stale ignored .o cannot survive into the link. The check as written still cannot see ignored files at all. See AMEND item 3.

### C2. git apply runs something
REFUTED. git apply executes no hooks and no commands. The two patches are our own repo files, read in full by Y6e: local-optics (2,229 B, two C++ hunks) and shayxo-legacy (23,419 B, GLSL only in Shaders.hpp). No vendor-controlled content passes through git apply.

### C3. make -B with the fetched Makefile
REFUTED as an escape. I read Makefile-pin in full (94 lines). Recipes are compile, link, wayland-scanner codegen, and `clean` (rm -f of build artifacts only). No curl, wget, install, cp, network, or writes outside the tree, and no absolute paths. `$(wildcard src/*.hpp)` affects rebuild triggers only (headers are prerequisites, not linked content).

### C4. HYPRGLASS_VERSION injection via the git describe branch
REFUTED. build-glass.py passes HYPRGLASS_VERSION=1.1.1-cu.1 on the make command line. Command-line variables override Makefile assignments and satisfy `ifndef`, so the `git describe` branch is skipped. The branch is also sanitized (`tr -cd 'A-Za-z0-9._+-'`) as defense in depth. Even if the branch ran, its output is confined to a -D string macro.

### C5. The worktree shares the vendor repo's .git
REFUTED as a write path into the vendor checkout. No make recipe touches .git. git apply writes worktree files and the worktree's own index (stored under .git/worktrees/<name>/), not the vendor checkout's index or files. The vendor checkout stays untouched.

### C6. hyprpm.toml commit_pins gap and .hyprland-version 0.57.0 vs running 0.57.2
REFUTED as safety issues. hyprpm is not used by this build. The runtime version identity does not come from .hyprland-version: GIT_TAG and GIT_COMMIT_HASH come from the installed Hyprland headers (/usr/include/hyprland/src/version.h, confirmed by the release.yml check in workflows-diff.txt). LoadGuard compares release lines via HyprlandIdentity::compare (diff lines 5949-6076): 0.57 built vs 0.57 running is a Match, and the dependency-suffix check compares installed libs to running libs, identical on the same machine. BUILT_FOR_HYPRLAND_GIT is false at this pin (BuildChannel.hpp, diff lines 1174-1185), so the commit-only path does not apply. The load is expected to Match, not pause. If it pauses, that is a stop-and-investigate signal, not a cue to set the skip variable.

## 4. Load-test containment (nested only)

### D1. Helper .so with RTLD_NODELETE persists after the nest dies
REFUTED. RTLD_NODELETE only prevents dlclose inside the process lifetime. The helper is written to a memfd and dlopen'd from there (ItemHelperBlob.S comment, item-helper-blob-pin.txt), so there is no on-disk copy at all, and the mapping dies with the nested Hyprland process. The memfd/dlopen call site itself is in unchanged ItemHints.cpp; see B5 for the read-to-close.

### D2. LoadGuard duplicate-copy path touches the live session
REFUTED. It only iterates Hyprland's in-process plugin list via g_pPluginSystem and dlsym's a symbol in the nested process (LoadGuard.cpp, diff lines 6116-6131). No files, no IPC.

### D3. Config, cache, or state files written by the plugin
REFUTED for added code: zero file-IO calls in added lines (B8). The plugin's only persistent surface is the user's own config (the test's conf copy), which is user-authored Lua. No state survives the nest.

### D4. HYPRGLASS_SKIP_VERSION_CHECK env var bypasses the version gate
PLAUSIBLE procedural hole. The var is read from the nested compositor's own environment (LoadGuard.cpp, diff line 6134). If it is set in the ambient environment when the nest launches, the version gate is silently bypassed and the load test proves nothing about the gate. If exported broadly it could also affect a future live load. See AMEND item 4.

### D5. Live-session touch paths from inside the nest
Mostly REFUTED, one accepted residual. The nested compositor is a separate process with its own Wayland display; the plugin registers its hyprctl command and protocol global inside the nest only. Remaining shared resources: the GPU and XDG_RUNTIME_DIR. No plugin socket code exists in added lines. The residual: a GL fault in the nest could stall the shared GPU and freeze live rendering. Shader compile failures are handled in code (B6), and the shaders are the released v1.1.1 set, so this is accepted as negligible for a nested-only test. No live work depends on the nest, and killing the nest is the recovery.

### D6. Conf mix-up: the rebuilt .so path lands in the live config
PLAUSIBLE procedural hole, not a code hole. If the rebuilt path ever enters the live config, live Hyprland (PID 1515) would load it. See AMEND item 5.

## AMEND checklist (all must close before GO)

1. Pull into the evidence pack and read, at the pin: src/item-helper/helper.c (full body), protocols/hyprglass-item-v1.xml, the src/ItemHints.cpp memfd/dlopen site, and the src/ShaderManager.cpp loadShaderSource body. Record file hashes and the read verdict. This closes B5 and B8's boundary, and is the load-bearing item: the build compiles and the nest loads this code.
2. Record the outcome of `git verify-commit 03a57c4` (expect unsigned or signed; either way record it as a known fact, not an unasked question). This closes A4.
3. Before build, assert the fresh worktree shows nothing under `git status --porcelain --ignored --untracked-files=all` (or `git clean -ndx` empty) and record the output. This closes C1.
4. At nest launch: show `env | grep HYPRGLASS` empty, launch with the var explicitly unset, and record the LoadGuard verdict from the nested `hyprctl hyprglass status` or plugin list (expect match). This closes D4.
5. Before and after the test: verify the live config contains no hyprglass path and live Hyprland (PID 1515) plugin list is unchanged; record both. This closes D6.

## Notes (not blocking)

- Upstream has a newer tag, v1.2.0 (56714382e7ee6a46826bc8586f6d68b662c60c8a), confirmed by the same live ls-remote. The pin is not latest; that is a freshness note, not a safety matter.
- The workflows diff is CI-only (build-channel checks, release-tag check, forward-merge handling). `make` never runs it. No safety content.
- The hyprpm.toml commit_pins end at Hyprland 0.56.2 to v0.11.0 with no pin for any 0.57.x line. Irrelevant to this manual build; noted only.

## Verdict: AMEND

No blocking fact was found in the reviewed diff. Every attack is refuted except the five closable items above, of which item 1 (unread unchanged code that the build compiles and the nest loads) is the load-bearing one. Close all five, record the evidence, then GO. Any BLOCK from council on any item means NO BUILD.
