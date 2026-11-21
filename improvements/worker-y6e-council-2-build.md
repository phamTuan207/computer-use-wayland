# Council Voice 2 paper: build-time safety of fetched hyprglass commit 03a57c4

- Voice: Council Voice 2 (build-time safety only)
- Subject: Worker Y6e rebuild risk review, fetched commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd
- Date: 2026-11-21
- Verdict: GO (for build-time safety scope only)
- Method: reviewer only. Read the evidence files in full. No commit, no checkout, no build, no load, no git command inside the vendor repo. Every claim below cites a file and line I read myself.

## 0. Evidence read

- improvements/worker-y6e-rebuild-load-log.md, read in full.
- scripts/build-glass.py, 99 lines, read in full.
- improvements/y6e-evidence/Makefile-pin, 94 lines, read in full.
- improvements/y6e-evidence/Makefile-diff.txt, 20 lines, read in full.
- improvements/y6e-evidence/workflows-diff.txt, 79 lines, read in full.
- improvements/y6e-evidence/hyprpm-pin.toml, 31 lines, read in full.
- improvements/y6e-evidence/hyprland-version-pin, 1 line, read in full.
- improvements/y6e-evidence/scan-added.txt (73 matches) and scan-removed.txt (5 matches), read in full.
- native/hyprglass-local-optics.patch, 36 lines, read in full.
- native/hyprglass-shayxo-legacy.patch, 511 lines, read in full.
- improvements/y6e-evidence/diff-99f30ca-03a57c4.txt, 10,070 lines, read in the sections relevant to build-time safety and spot checked by grep for execution primitives (see section 5).

## 1. Build script: scripts/build-glass.py

Every external command it runs, in order:

1. `git -C <source> rev-parse --show-toplevel` (line 56)
2. `git -C <source> rev-parse HEAD` (line 59)
3. `git -C <source> status --porcelain --untracked-files=all` (lines 61 and 88, twice)
4. `pkg-config --modversion hyprland` (line 66)
5. Per patch: `git apply --reverse --check <patch>` (line 78), then `git apply --check <patch>` (line 81), then `git apply <patch>` (line 83), all with cwd set to the source tree
6. `make -j2 -B HYPRGLASS_VERSION=1.1.1-cu.1` (line 90), cwd set to the source tree, stdio inherited

Judgement per command:

- All invocations use `subprocess.run` with a list of arguments (helper `run`, lines 30-31). There is no `shell=True`, no `os.system`, no `eval`, no `exec`, no curl, no wget, no network call anywhere in the script. I grepped the script for shell, subprocess, os., eval, curl, wget, install, load: the only hits are the `import subprocess` line, the `run` helper itself, and the final print saying "not installed and not loaded".
- The only variable inputs are the operator supplied SOURCE path (resolved with `Path.resolve`, line 54) and the two patch paths, which are derived from the script's own location (`parents[1] / native/...`, lines 20-21) and therefore point at our own repo content, not at fetched content.
- The script enforces its gates before any mutation: SOURCE must be the git toplevel (lines 56-58), HEAD must equal REQUIRED_COMMIT 03a57c4... (lines 59-60), the tree must be clean unless `--allow-dirty` is passed (lines 61-64), and pkg-config hyprland must report exactly 0.57.2 (lines 66-69). Only then does it apply patches and run make.
- Writes: `git apply` writes only the two patched files inside the source tree. `make` writes build artifacts inside the source tree (.o files, the helper .so, generated protocol files, hyprglass.so). There is no write outside the source tree: no absolute output path, no write to HOME, /usr, or /etc, no install step, no load step (no hyprctl, no dlopen, no plugin load).
- `output()` builds an error string with `' '.join(args)` (line 36). That string is only printed on failure, never executed.
- Note, not a finding: `--allow-dirty` is operator opt-in and the HEAD pin is still enforced when it is used. Also, the script does not scrub the environment, so CXX, CC, and WAYLAND_SCANNER come from the operator environment if set (make `?=` does not override an environment value). That is a property of the trusted operator environment, not of the fetched commit. See the hardening suggestion in section 6.

Conclusion for the script: clean. It cannot by itself execute code from the fetched commit, reach the network, write outside the source tree, install, or load anything. The executed surface is exactly what `make` runs, which is the Makefile review in section 2.

## 2. Makefile at the pin: Makefile-pin plus Makefile-diff.txt

### 2.1 Every recipe command in Makefile-pin

- `%.o : %.cpp` rule: `$(CXX) -c $(CXXFLAGS) $(INCLUDES) $< -o $@` (compile only)
- `$(PROTOCOL_HEADER)` rule: `$(WAYLAND_SCANNER) server-header $< $@` (code generation from protocols/hyprglass-item-v1.xml)
- `$(PROTOCOL_CODE)` rule: `$(WAYLAND_SCANNER) private-code $< $@` (code generation from the same XML)
- `$(ITEM_HELPER_DIR)/%.o` rule: `$(CC) -c -fPIC -O2 -std=c11 $(WAYLAND_SERVER_CFLAGS) -I$(ITEM_HELPER_DIR) $< -o $@` (compile only)
- `$(HELPER_SO)` rule: `$(CC) -shared -fPIC -Wl,-z,noexecstack -o $@ $(HELPER_OBJ) $(WAYLAND_SERVER_LIBS)` (link only)
- `$(ITEM_HELPER_BLOB_OBJ)` rule: `$(CC) -c src/ItemHelperBlob.S -o $@` (assemble only; the .S embeds the helper .so via .incbin, see 2.4)
- `$(TARGET)` rule: `$(CXX) $(LDFLAGS) $(OBJ) $(ITEM_HELPER_BLOB_OBJ) -o $@ $(LIBS)` (link only, with `-shared -Wl,-z,noexecstack`)
- `clean` rule: `rm -f $(OBJ) $(TARGET) $(ITEM_HELPER_BLOB_OBJ) $(HELPER_OBJ) $(HELPER_SO) $(PROTOCOL_HEADER) $(PROTOCOL_CODE)` (delete only, in-tree artifact paths only)

There is no `install` target at all. There is no cp, mv, chmod, curl, wget, or system call in any recipe. All outputs are relative paths inside the source tree. `.PHONY` is only `all clean`. The `all` target is only `$(TARGET)`. Nothing in the Makefile runs, tests, or loads the built library.

### 2.2 The `git describe` version branch (Makefile-pin lines 15-22)

```
ifndef HYPRGLASS_VERSION
HYPRGLASS_VERSION := $(shell [ -e .git ] && git describe --tags --dirty 2>/dev/null | sed 's/^v//' | tr -cd 'A-Za-z0-9._+-')
endif
```

- When it runs: only when HYPRGLASS_VERSION is not passed on the make command line, and only if a `.git` entry exists. build-glass.py always passes `HYPRGLASS_VERSION=1.1.1-cu.1` (build-glass.py line 90), so in our build this branch is skipped entirely.
- Injection analysis: even if it did run, the output passes through `tr -cd 'A-Za-z0-9._+-'`, which strips every shell metacharacter (no dollar, backtick, quote, semicolon, space, slash, or newline survives). The result is then placed inside double quotes in `-DHYPRGLASS_VERSION='"$(HYPRGLASS_VERSION)"'`, so it stays one word and cannot become a separate compiler flag or a shell command. A hostile tag name in the fetched repo is neutralized by that whitelist before it reaches the compiler command line.
- The comment above the branch says the intent is to keep only characters safe in a C string. The implementation matches the comment.

### 2.3 The GCC detection condition (Makefile-diff.txt)

The diff changes the `--no-gnu-unique` guard from `ifeq ($(basename $(CXX)),g++)` to `ifneq ($(shell $(CXX) --version 2>/dev/null | grep -c 'Free Software Foundation'),0)`. The new form runs `$(CXX) --version` once at parse time through a fixed pipeline and uses only the count. It cannot inject anything into the flags except choosing whether `--no-gnu-unique` is added. No new execution surface beyond a compiler version query. The SOURCES change in the same diff adds only LoadGuard.cpp, GlassSnapshotElement.cpp, Frost.cpp, and Contour.cpp, all under src/.

### 2.4 The .incbin helper blob

- Makefile-pin lines 40-42 comment: the helper is built as its own shared library and embedded via ItemHelperBlob.S inside hyprglass.so, so it can be dlopen'd with RTLD_NODELETE and outlive a plugin reload. The rule assembles src/ItemHelperBlob.S, and the comment states the .incbin path is relative to the repo root.
- The embedded file is HELPER_SO, built in the same make run from in-tree helper.c plus the wayland-scanner generated protocol code. It is not a prebuilt binary from the vendor repo: the 54-file diff contains no .so, .o, or other binary file.
- I verified the mechanism is unchanged since v0.9.1: there is no ItemHelperBlob entry anywhere in diff-99f30ca-03a57c4.txt (grep for ItemHelperBlob and incbin returns zero lines). The log's claim that it is unchanged is confirmed.
- Residual, recorded here and not a blocker: the exact content of src/ItemHelperBlob.S is not in the evidence pack, because it is an unchanged file and therefore not in the diff. The assembler only translates directives and embeds bytes at build time; it does not execute the embedded content, so a hostile .S could at worst embed unexpected bytes, which would be a load-time matter for Council 3, not a build-time execution. See section 6 for the one-line read-only check that would close this residual.

### 2.5 The clean target

`rm -f` with make variables expanding only to in-tree artifact paths. No `rm -rf`, no wildcard, no `$(shell)` in the clean recipe. It is also not run by build-glass.py, which uses `make -B` instead. Safe.

### 2.6 `$(shell ...)` inventory for Makefile-pin

Five occurrences, all at parse time, all with fixed arguments: pkg-config --cflags hyprland pixman-1 libdrm (line 10), pkg-config --libs hyprland (line 11), the git describe branch (line 17, skipped in our build), `$(CXX) --version | grep -c` (line 25), pkg-config --cflags/--libs wayland-server (lines 49-50). None of them takes input from repo content except the git describe output, which is whitelist filtered as shown in 2.2.

## 3. The two patches, read in full

### 3.1 native/hyprglass-local-optics.patch (36 lines, 2 files, 2 hunks)

- Hunk 1, src/GlassLayerSurface.cpp at line 702: adds an indicator namespace check (`layerSurface->m_namespace == "computer-use-indicator"`), computes region extents with finite and positive guards (`std::isfinite` on x, y, w, h, and w > 0, h > 0), and assigns maskInfo.glassBoxOffsetPx, maskInfo.glassBoxSizePx, and cornerRadius. Pure C++ logic.
- Hunk 2, src/GlassRenderer.cpp at line 535: replaces the optical-box condition with a `validOpticalBox` boolean requiring finite and strictly positive glassBoxSizePx. Pure C++ logic.
- Hunk line counts reconcile with the headers (hunk 1: 6 old lines, 18 new lines, 12 added; hunk 2: 7 old, 9 new). The one empty context line in hunk 1 is a standard unified-diff context line, not a defect.
- No shell, network, file IO, process, include change, or build content in either hunk. Confirmed: the patch touches only what it claims.

### 3.2 native/hyprglass-shayxo-legacy.patch (511 lines, 1 file, 5 hunks)

- Single file: src/Shaders.hpp only. Confirmed by the file header (`diff --git i/src/Shaders.hpp w/src/Shaders.hpp`) and by grep: it is the only `diff --git` header in the file.
- All five hunk counts verified arithmetically against their headers: hunk 1, 26 old / 29 new; hunk 2, 6 / 11; hunk 3, 6 / 74; hunk 4, 31 / 48; hunk 5, 239 / 86. All exact. The file ends on a context line at line 511; the counts prove it is complete, not truncated.
- Content: SHAYXO_* GLSL constants, sampleSharp, bevelSlope, snellShift, luma, toLinearApprox, fromLinearApprox, linearToOklab, oklabToLinear, applyHighlight, toneMappedTint, and the main() refraction, tint, and highlight rework. GLSL only, inside a C++ string literal map. No C++ code, no shell, no network, no file IO, no include, no build content.
- Grep over both patches for system, popen, exec, curl, wget, socket, fopen, ofstream, and system includes: zero hits.
- Confirmed: the patch touches only what it claims.

## 4. Workflows diff is CI-only

workflows-diff.txt (79 lines) touches only .github/workflows/ci.yml, hyprland-update.yml, and release.yml:

- ci.yml adds a "Check the build channel" step that greps for `BUILT_FOR_HYPRLAND_GIT *= *true` in src/BuildChannel.hpp.
- release.yml adds a release-tag check against /usr/include/hyprland/src/version.h, a build-channel check, and forward-merge handling that restores src/BuildChannel.hpp from HEAD^1.
- hyprland-update.yml changes only the wording of a step that creates a branch and sets the version flag.

All of these are GitHub Actions `run:` steps. Local `make` never reads .github, and no workflow step runs during a local build. The only `make` mentions in the workflows are the CI build steps themselves, which run on GitHub runners, not here. Verified CI-only. The BuildChannel.hpp file the workflows reference is itself a new 6-line file in the diff (line 1174, `BUILT_FOR_HYPRLAND_GIT = false`), which is consistent with the workflow text.

## 5. Independent verification (did not trust the log blindly)

I re-checked the following myself instead of taking the log's word:

- Diff file integrity: `md5sum` of improvements/y6e-evidence/diff-99f30ca-03a57c4.txt is 71ee7ccaef91e73bc61dd1cbebd8e521, matching the log. Line count 10,070 and size 543,272 B also match.
- Diff file list: grep counts 54 `diff --git` headers, matching the log. Non-src files are exactly .github/workflows/ci.yml, hyprland-update.yml, release.yml, .hyprland-version, CHANGELOG.md, Makefile, README.md, hyprpm.toml. All other 46 files are under src/.
- Makefile token scan: my own grep over Makefile-pin for curl, wget, git, pip, npm, install, cp, mv, rm -rf, chmod, /usr/, /etc/, HOME finds only the git describe line, which is analyzed in 2.2. This confirms the log's zero-hit scan.
- Added-lines token scan: my own grep over the full diff for system(, popen, execl, execv, fork(, curl, wget, socket(, getaddrinfo, /dev/tcp, base64, constructor attribute, LD_PRELOAD, chmod, setuid, /etc/, HOME finds no hits in added code. The only added-code hits of interest are the ones the log already lists: `std::getenv("HYPRGLASS_SKIP_VERSION_CHECK")` in LoadGuard.cpp (diff line 6134), `lua_rawgeti` (diff line 7088), the registerHyprCtlCommand handler (diff line 1989), and the dlsym/nm comment block (diff lines 9750-9761).
- The nm item, read in full at diff lines 9735-9785: `resolveHyprlandFunction` tries `dlsym(RTLD_DEFAULT, mangledName)` first with a dladdr check against the Hyprland executable, and only then falls back to `HyprlandAPI::findFunctionsByName`, which per the comment runs nm on the Hyprland binary. That fork and exec of nm happens at plugin runtime, not during the build. Nothing in the build executes it. Flagged here for Council 3 (runtime behavior and containment), not a build-time finding.
- Removed-lines scan: the old HYPRGLASS_SKIP_VERSION_CHECK escape hatch was removed from main.cpp (diff lines 9804-9816) and its README line, and the getenv now lives in LoadGuard.cpp (diff line 6134). This is a move, not a disappearance, as the log says. Whether LoadGuard still enforces the check is Council 3 scope.
- hyprpm-pin.toml: `build = ["make"]`, output hyprglass.so. hyprpm is not used by build-glass.py, so this is inert for our build. The commit_pins list ends at hyprland 0.56.2, with no pin for any 0.57.x line. Noted as a functional fact for the load test, not a build-safety issue.
- .hyprland-version at the pin reads 0.57.0 while build-glass.py requires pkg-config hyprland 0.57.2. Functional note for the load test, not build safety.

## 6. Residuals and hardening suggestions (none gating)

1. ItemHelperBlob.S content is not in the evidence pack (unchanged file, not in the diff). Closing check, read-only, for Y6e before the build: add `git show 03a57c4:src/ItemHelperBlob.S` output to the evidence pack and confirm the .incbin path names the helper .so built in the same run. This does not change the verdict, because the assembler does not execute embedded bytes at build time.
2. build-glass.py does not scrub CXX, CC, or WAYLAND_SCANNER from the environment. Hardening suggestion, not a finding against the fetched commit: invoke make with explicit `CXX=g++ CC=gcc` or clear those variables in the script, so a stray environment value cannot substitute a different compiler. The fetched commit cannot set those variables itself.
3. Compiling untrusted C++ inherently runs the compiler over untrusted source. There is no build-time code execution primitive in this Makefile (no configure script, no CMake custom command, no codegen step that runs a built artifact, no post-build step). wayland-scanner only generates C from the XML protocol file. This is the normal residual of any build, not a finding against this commit.

## 7. Verdict

GO for build-time safety scope.

- scripts/build-glass.py runs only fixed git, pkg-config, and make commands with list arguments, no shell, no network, no install, no load, and no write outside the source tree.
- The Makefile at the pin contains only compile, link, wayland-scanner, assemble, and a narrow rm -f clean. No install target, no network, no post-build execution. The git describe branch is skipped in our build and is injection-proof by its character whitelist even if it ran. The .incbin blob embeds a library built in the same run, and the mechanism is unchanged since v0.9.1.
- Both patches touch only what they claim: local-optics is two C++ logic hunks, shayxo-legacy is GLSL in src/Shaders.hpp only, and neither contains build, shell, or network content.
- The workflows diff is CI-only and nothing in it runs during local make.
- I independently re-verified the diff md5, the 54-file list, the Makefile token scan, and the added-lines token scan, and I read the nm fallback block in full. The nm execution is runtime behavior for Council 3, not a build-time block.

No AMEND is open in this scope, and nothing in this scope blocks the build. Runtime behavior, load containment, and the version-check enforcement in LoadGuard are Council 3 scope and are not decided by this paper.
