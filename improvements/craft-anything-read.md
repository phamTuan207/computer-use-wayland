# craft-anything: relevance read for a Python to Rust port

Evaluator: Luna 6 Max (W2, TRACK 1). Owner: Pham Tuan.
Repo read: `~/workspace/craft-anything` (storytold/craft-anything), HEAD `9c9f5a1`, dated 2026-11-18.
Version: `0.6.1`, workspace edition 2024, rust-version 1.97 (`Cargo.toml`, lines 1-9).
Port target for context: `~/workspace/computer-use-wayland` holds 123 `.py` files and 0 `.rs` files (counted 21:32), so the port input is Python source, not a compiled binary.

## Work log (Asia/Ho_Chi_Minh)

- 21:31:22 started. Listed repo, read `Cargo.toml`, `README.md`, `AGENTS.md`, `CLAUDE.md`.
- 21:31:28 counted layout: 13 crates under `crates/`, 3 apps under `apps/`, 806 `.rs` files.
- 21:32 searched for port, transpile, Python handling. Read `crates/ai/src/rebuild/study.rs` and `brief.rs`.
- 21:34 read `python_tools.rs`, `rust_tools.rs`, `pyc.rs` headers; checked own-project mode.
- 21:35 read `docs/ROADMAP.md` line 1935 context, `docs/tool-status.md` summary, `docs/STATUS.md`.
- 21:36 checked `own_project()` definition, Codex adapter status, tool registration, test counts.
- 21:37 confirmed no TUI deps, checked `text_tools.rs`, `evidence` crate, `agent.rs` loop.
- 21:32:23 counted port target files (123 Python, 0 Rust). Wrote this file.

## What it actually does

Craft Anything is a pure-Rust "study any app, then have AI build your own version" engine, in its own words: "See how any website, app or game works, then have AI build your own version; an open-source, clean-room engine in pure Rust" (`README.md`, lines 28-31). Its workflow is Study, Build, Check, Ready (`README.md`, lines 84-92):

1. Study: inspect the target with real tools (screenshots and layout for a website, triage and disassembly for a program).
2. Build: an external coding agent builds a NEW project in `app/`, in the stack the request names.
3. Check: compare the build with the original (page screenshots at three widths, a game self-test, an app run).
4. Ready: open, play, preview, or refine.

Two modes govern what may be read. Clean room (default) reads nothing inside the original, only what a visitor sees. Deep mode reads code and files with built-in engines, plus Ghidra when installed (`README.md`, lines 124-140; `AGENTS.md`, lines 25-28). It ships 320 tools, each one a CLI command and an MCP tool (`README.md`, lines 89 and 190-191). The workspace layers are: `evidence` (L0), `formats` (L0), `disasm` (L1), `js` (L1), `analysis` (L2), `platform` (L2), `engines` (L3), `engine` (L4), `ai` (L5), `mcp` (L5), `setup` (L5), `ui-egui` (L6) (`AGENTS.md`, lines 11-21). The UI is an egui desktop app plus a web viewer; there is no terminal UI (see below).

## Check 1: does it analyse a codebase and produce a port?

No. There is no porting or transpiling component anywhere in the repo.

- A grep for `transpil` and for port-a-code phrasing across `crates/`, `apps/`, `docs/`, `README.md` and `AGENTS.md` returns zero hits for any transpiler or code-port feature. The only "port" hits are unrelated words (portable, transport, support, import).
- The rebuild path is generation from evidence, not transformation of source. The builder brief orders: "Rebuild the layout, styling and behaviour yourself from the evidence" and "Change files only inside app/. Everything else in the workspace is read-only evidence" (`crates/ai/src/rebuild/brief.rs`, lines 8-13). The builder never reads the original source to convert it line by line; in Clean room it is forbidden to, and in Deep mode it reads binaries and bundles to describe behaviour, then writes fresh code.
- The closest mode, own-project editing, still does not port. `Manifest::own_project()` is true only when "their files are the app, edited in place, with nothing to recreate" (`crates/engine/src/workspace.rs`, lines 483-487). That mode hands an existing project to an external coding agent for edits, and its check just runs the project's own build and tests (`crates/ai/src/rebuild/check.rs`, lines 56-67). There is no step that maps Python constructs to Rust constructs, no AST-to-AST translation, no symbol table carried across languages.
- Python handling is limited to three shallow things, none of which reads Python source semantics:
  - `crates/formats/src/pyc.rs` (1,089 lines) reads compiled `.pyc` headers and code objects: names, argument counts, constants. The tool states its own limit: "Bytecode isn't decoded: this shows what functions exist and what they name, not what they do" (`crates/engine/src/tools/python_tools.rs`, lines 80-84). We have the `.py` source, so even this inventory is redundant.
  - `crates/formats/src/pyinstaller.rs` (779 lines) extracts files from PyInstaller bundles. Our target is not a PyInstaller bundle.
  - `crates/engine/src/toolchains.rs` and `crates/ai/src/rebuild/stacks.rs` know how to launch a Python project (`python3 main.py`, `.venv/bin/python`, `python -m <name>`), i.e. how to RUN Python, not how to convert it.
- There is no Python source parser in the dependency tree: no `tree-sitter`, no `rustpython`, no `pyo3` in `Cargo.toml` or any crate `Cargo.toml`. The JavaScript crate uses `oxc_parser` 0.153 (`Cargo.toml`, lines 74-80), which parses JavaScript only. In `crates/analysis/src/js_source.rs` (lines 275-276), `"py"` is only a language label (`"py" => "python"`) for a source-tree summary, not a parser.
- The analysis crate covers native binaries (`native.rs`), JavaScript bundles (`js_*.rs`), websites and packet captures. Nothing in `crates/analysis/src/` parses Python, and nothing in `crates/formats/src/` parses `.py` source files.

## Check 2: is any reusable component useful for this port?

Almost nothing, and nothing worth vendoring. The honest list, strongest first:

- Design reference only: the rebuild loop. `crates/ai/src/rebuild/study.rs` (study before building), `brief.rs` (prompt construction, stack steps, per-kind briefs), `check.rs` (run the toolchain build and test, compare against the original) and `self_check.rs` (stop rules, good-enough reporting) form a coherent study, build, check, refine loop with an external agent doing the writing. If our port harness needs a loop shape, reading these four files (about 30 minutes) is a reasonable reference. Importing `crates/ai` is not: it drags the whole engine, the MCP server, the agent adapters and the workspace layering rules with it, and its builder is an external CLI agent, not a library call.
- Pattern reference only: bounded process execution. `crates/platform/src/process.rs` (2,118 lines) wraps child processes with wall-clock and idle timeouts, capped output (8 MB stdout cap in `check.rs`, lines 22-26), stdin closed, and kill on timeout, cancel or drop (`AGENTS.md`, lines 44-51, rule 10). This is good practice our port harness should copy as an idea, but computer-use-wayland already has its own relay and process handling, and vendoring the crate would pull in the platform crate's other concerns.
- Smallest crate, still not needed: `crates/evidence/src/` (`lib.rs` defines `Confidence` at line 27, `Evidence` at line 203, `EvidenceBuilder` at line 380; `error.rs` defines `ToolError` at line 98). It is a tidy model for typed, confidence-graded results with limitations and coverage. Useful as a design example for structured port reports, not as a dependency; the port does not need an evidence ledger to translate Python to Rust.
- Not reusable for this job:
  - `crates/js` (oxc-based JS parsing, bundle graphs, source maps): JavaScript only, zero Python relevance.
  - `crates/disasm` and `crates/formats` (ELF, PE, Mach-O, WASM, DEX, APK, .NET, Go): binary forensics. Our input is Python source, so there is nothing to disassemble.
  - `crates/ui-egui` (3.0 MB): an egui desktop GUI. A grep for `ratatui` and `crossterm` in every `Cargo.toml` returns zero hits, so there is no TUI component to reuse either.
  - `crates/ai/src/agent.rs` (`AgentLoop` at line 381, `ApiConversation` at line 977) plus `cli_agents/adapters/`: an agent harness that shells out to Claude Code (first, verified), Codex, Copilot, Grok, opencode and others. The README states the Codex adapter "exists but hasn't been verified on a real install yet" (`README.md`, lines 163-165). It orchestrates agents; it does not port code, and our port already has its own agent setup.
  - `core_text_read` (`crates/engine/src/tools/text_tools.rs`, line 15): paged plain-text file reading. Any port harness can read files in a few lines; this is not a reason to adopt the engine.

## Check 3: maturity

Early alpha, by its own badge and docs. Evidence:

- `README.md` line 35 carries a "Status: early alpha" badge, and the Status section says "Craft Anything is in early alpha" (`README.md`, lines 197-205).
- Version `0.6.1` (`Cargo.toml`, line 5). `docs/STATUS.md` was last updated 2026-11-09, with a baseline audit of 923 tests passing on 2026-10-23. A grep count today finds 4,919 `#[test]` markers and 40 `#[ignore]` markers across `crates/` and `apps/` (grep count, not a test run; no build was attempted in this read).
- `docs/ROADMAP.md` still has 164 open `- [ ]` items (grep count). The Status section lists as only "Partly there": building with API keys and other coding agents (built, not yet run live), behaviour checks for apps and games, and engine tools tested only against stand-ins (`README.md`, lines 205-207).
- `docs/tool-status.md` (functional audit 2026-10-16) records unverified toolsets: Android device 23 unverified (no device attached), Frida 9 unverified (not installed), runtime 5 unverified (runs foreign code, not executed in the audit). Known partials remain, e.g. `native_function_pseudocode` showing only arguments set in the calling block for imports outside the arity table.
- A live bug illustrates the alpha state: a Rust project rewritten in Python is still checked with Cargo until the old manifest is moved out (`docs/ROADMAP.md`, lines 1932-1935). Stack detection is manifest-based and stale, which is exactly the kind of edge a port harness cannot rely on.

## Verdict: irrelevant, skip it

Craft Anything does not port code. It clones apps by observing behaviour and having an external coding agent write a fresh implementation from that evidence. That is the opposite direction from our job, which is a faithful source-to-source port of an existing Python codebase whose logic, not its appearance, must survive. No crate or module in it analyses Python source, maps it to Rust, or verifies semantic equivalence between a Python original and a Rust rewrite. The shallow Python pieces it does have (`.pyc` name inventory, PyInstaller extraction, Python launch recipes) are all useless when the `.py` source is in hand.

Recommendation: do not install it, do not vendor any crate, do not route port work through its rebuild loop. The only action worth taking is a 30-minute skim of `crates/ai/src/rebuild/check.rs` and `crates/platform/src/process.rs` as design references for our own build, check and timeout handling, if whoever builds the port harness wants a worked example of that loop shape. Everything else in the repo is out of scope for this port.
