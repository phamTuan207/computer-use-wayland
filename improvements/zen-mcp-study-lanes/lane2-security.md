# Lane 2: Security audit of spaxe-dev/zen-mcp

Scope and method: read-only audit. No code from the repo was installed or
executed. Evidence is from a shallow clone read at the **v0.6.0 tag**
(the version named in the assignment; `git archive v0.6.0` extracted to a
scratch copy for line-numbered reading) plus the clone HEAD (0.6.3) where a
difference matters and is flagged as such. Access date for all sources:
**2026-11-27**.

Version note that matters for the verdict: the assignment targets v0.6.0.
The repo has since released up to 0.6.3, and 0.6.3 adds an install-time
behaviour v0.6.0 does not have (see section 2.3). The verdict in section 6
is for **v0.6.0 as audited**; the conditions there cover later versions.

---

## 1. Outbound data flow

### 1.1 Every external endpoint the project's own code can reach

Exactly one, in v0.6.0:

| Endpoint | File and line | What is sent | When |
|---|---|---|---|
| `https://registry.npmjs.org/@spaxe-dev%2Fzen-mcp/latest` (GET) | `src/zen/updates.ts:9-11` (constant `REGISTRY_URL`), `:125-131` (the fetch) | No body. Headers only: `accept: application/json`, `user-agent: zen-mcp/<version>`. No browser data, no identifiers, no machine data. | Once per server start (`src/cli.ts:200` calls `runtime.checkForUpdates()`; `src/zen/runtime.ts:220-224`), and on `zen-mcp doctor` / `zen-mcp update` (`src/cli.ts:307,317`). Disable with `ZEN_MCP_NO_UPDATE_CHECK=1` (`src/zen/runtime.ts:221`). Timeout 2 s default, failure is a normal result (`updates.ts:104-159`). |

That is the complete list of non-local endpoints in the project's own code.
Everything else network-shaped is local:

- Marionette client: TCP to `127.0.0.1:2828` by default
  (`src/zen/marionette.ts:12-13,125,212`; host overridable only by the
  operator's own `ZEN_MCP_MARIONETTE_HOST` env var, `marionette.ts:125`).
- Bridge WebSocket server: bound to `127.0.0.1`, ephemeral port (`port: 0`),
  `src/bridge/host.ts:357-362` (start method), URL built as
  `ws://127.0.0.1:<port>` at `host.ts:384`; non-loopback connections are
  rejected at connection time (`host.ts:398-405`, `isLoopback` check).
- Bridge client inside Zen: `new WebSocket(config.url)` to that loopback
  URL only (`src/bridge/entry.ts:409-411`).
- Port probe: `net.connect({ host: "127.0.0.1", port })`
  (`src/zen/launcher.ts:134-136`).
- Dev/test scripts only (`scripts/probe-mcp.ts`, `probe-smoke.ts`,
  `benchmark-surfaces.mjs`, `agent-eval.mjs`): local `node:http` servers on
  `127.0.0.1` for test pages. These are not in the published package
  (`package.json` `files` at v0.6.0 is only `dist`, `README.md`, `LICENSE`).

URLs that appear as string literals but are **not** contacted by the server:
the template start pages in `src/zen/templates.ts:127-179` (Wikipedia,
arXiv, GitHub, MDN, etc.) are URLs the browser itself opens if a user
applies a built-in template; the server code never fetches them.
`https://github.com/spaxe-dev/zen-mcp` in `src/mcp/server.ts:231` is a
metadata string in the MCP server info, not a request.

### 1.2 Patterns searched, and scope

Whole tree at v0.6.0 (148 files: `src/`, `scripts/`, `test/`, `docs/`,
root configs, `package.json`, `package-lock.json`), searched for:
`fetch(`, `axios`, `http.request`/`https.request`, `new WebSocket`,
`WebSocketServer`, imports of `node:http`, `node:https`, `node:net`,
`node:tls`, `node:dns`, `dns.`, `lookup(`, `createConnection`, and the
telemetry/error-reporting names `telemetry`, `analytics`, `sentry`,
`posthog`, `mixpanel`, `segment`, `amplitude`, `bugsnag`, `rollbar`,
`gtag`, `track(`. Result: the only `fetch` call site in the whole tree is
`updates.ts:125`; no telemetry or error-reporting code or dependency
exists in the project's own code (see also section 3).

One indirect outbound path exists **by design, not by this code**: page
text and other tool results are returned over MCP stdio to the MCP client,
and the client sends them to whatever model provider the user configured.
The project states this itself: "Page text read by the agent is sent to
whatever model provider the MCP client uses" (`docs/security.md:151`).
In an isolated test with no signed-in pages, what flows there is only the
content of pages the test itself opens.

### 1.3 The update-install path (outbound plus execution, user-gated)

If a newer release exists, the browser banner offers an **Update** button.
Clicking it (an authenticated in-browser user click; "no MCP tool can call
it", `src/zen/runtime.ts` comment above `installUpdate`) runs the detected
package manager's global install of `@spaxe-dev/zen-mcp@latest`:
`src/zen/updates.ts:173-188` (`updateCommand`: `npm install -g`,
`pnpm add -g`, `yarn global add`, `bun add -g`) and `:256-299`
(`runInstaller`, `spawn`). On Windows it deliberately resolves the
installer outside the working directory first, to stop a repo-local
`npm.cmd` hijack (`updates.ts:205-250`). This downloads code from npm at
click time; it does not run automatically.

---

## 2. Install-time and run-time code execution surface

### 2.1 package.json lifecycle scripts at v0.6.0

`package.json` (v0.6.0) scripts, complete list: `build`, `dev`, `start`,
`typecheck`, `test`, `test:zen`, `check:skill`, `context:budget`,
`context:check`, `prepack` (`node scripts/build.mjs`).

- **No `preinstall`, no `install`, no `postinstall`, no `prepare` script
  exists at v0.6.0.** Installing the published package runs no project
  code at install time. (`files` ships only `dist`, `README.md`,
  `LICENSE`, so no `scripts/` directory is even in the tarball.)
- `prepack` runs only when the maintainer packs/publishes; it runs
  `scripts/build.mjs`, which is a plain esbuild bundle of `src/cli.ts`
  and `src/bridge/entry.ts` plus a `chmod 0755` on the output
  (`scripts/build.mjs:1-39`). No network, no shelling out.
- `bin`: `zen-mcp` -> `dist/cli.js` (the bundled server/CLI).

Dependency install scripts are a separate matter and are covered in
section 3.3: only `esbuild` and `fsevents`, both dev-only, have them.

### 2.2 What the running server process can do (OS level)

The server is an ordinary Node process running with the user's full OS
privileges. There is no sandbox. Concretely, in the code:

- Spawn Zen Browser: `spawn(executable, args, ...)`
  (`src/zen/launcher.ts:247`), with `-marionette`, `-no-remote`, the
  chosen profile, and `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1` in the child
  environment only (`docs/security.md:30`, `docs/architecture.md:23`).
- Kill processes it launched, and detect Zen processes:
  `tasklist`/`taskkill` on Windows, `pgrep -x` on POSIX
  (`src/zen/launcher.ts:163-181,296,385-386`).
- Spawn a package manager for the user-clicked update (section 1.3).
- Write files: its own config (`src/config.ts:328`), its data directory
  (sessions `src/zen/sessions.ts`, templates `src/zen/templates.ts`,
  audit log `src/mcp/guard.ts`, update state `src/zen/updates.ts:328-337`),
  with owner-only atomic writes and symlink refusal
  (`src/utils/safe-file.ts`).
- Write **other applications' config files during onboarding**:
  `zen-mcp onboard` merges a `zen-mcp` entry into the config files of up
  to 28 MCP clients (`src/onboard/clients.ts:645-672`,
  `atomicWritePrivate` at `:654,663,672`). This is an explicit user-run
  command, not something `serve` does.
- No general shell tool, no arbitrary command execution API: every
  `spawn`/`execFileSync` call site in `src/` is one of the above, with
  fixed argument lists (search: `child_process` across `src/` returns
  only `updates.ts`, `launcher.ts`). No `exec` with a shell string in
  `src/`.

### 2.3 Changed in 0.6.3 (not in the audited version, flagged for safety)

At HEAD (0.6.3), `package.json` gains
`"postinstall": "node scripts/postinstall.mjs"`, and
`scripts/postinstall.mjs` spawns the built `dist/skill-offer.js`, which
offers to run `npx skills add spaxe-dev/zen-mcp --skill zen-mcp --global
--yes` (a network fetch plus a global install of a skill from GitHub) when
the user answers yes at the install-time prompt. It exits quietly when
`dist` is absent and is skipped in non-interactive sessions per the
README at HEAD. Anyone pinning the audited behaviour should install
**0.6.0 exactly**, not `@latest`.

### 2.4 Arbitrary JavaScript: the sharp edge, and its guardrail

Internally, the server **does** execute JavaScript in both browser
contexts, and this is the most powerful capability in the design:

- Chrome context: `Marionette.executeChrome` / `executeAsyncScript` with
  `setContext("chrome")` (`src/zen/marionette.ts:282,434,465,479,548-576`),
  used to inject the bridge (`src/bridge/host.ts:1973`) and to read back
  the launch nonce.
- Content context: fixed read/evidence/wait scripts
  (`src/shared/read-script.ts`, `src/shared/evidence-script.ts`), and in
  the bridge, `MarionetteCommandsParent:executeScript` call sites
  (`src/bridge/ops.ts:840,1225,1301,1402,1913,2328,2623`).

The guardrail, verified in the catalog and server code: **no MCP tool
accepts JavaScript from the model.** All 55 tools take structured
arguments only; every script body is a fixed string built by the server.
`docs/security.md:26,80` states this and the tool list in
`src/mcp/catalog.ts` confirms there is no eval/execute tool among the 55.
So arbitrary JS is a capability of the *server binary itself* (as with
any browser harness), not a capability handed to the agent or to page
content. A compromised or malicious MCP *client* driving the tools still
cannot inject script; it can only call the 55 fixed operations.

---

## 3. Dependency audit

### 3.1 Direct dependencies (package.json, v0.6.0)

Runtime (4): `@modelcontextprotocol/sdk ^1.32.2`, `commander ^14.0.3`,
`ws ^8.22.0`, `zod ^4.6.7`.
Dev (5): `@types/node ^22.18.0`, `@types/ws ^8.18.1`, `esbuild ^0.28.2`,
`tsx ^4.20.6`, `typescript ^5.9.3`.
All are canonical, widely used packages under their expected names and
scopes; no name resembles a typosquat of a popular package.

### 3.2 Transitive dependencies (package-lock.json, lockfileVersion 3)

130 `node_modules` entries, 126 unique package names. The bulk is the MCP
SDK's server stack (`express 5.3.0`, `hono 4.13.18`,
`@hono/node-server 2.1.8`, `ajv`, `jose`, `cors`, `eventsource`, etc.)
plus the dev toolchain. Full resolved list (name, version) was extracted
from the lockfile during this audit; the notable entries:

- Telemetry/analytics/error-reporting packages: **none.** No Sentry,
  PostHog, Mixpanel, Segment, Amplitude, or similar name appears anywhere
  in the lockfile.
- Packages pulling native binaries: the `@esbuild/*` platform packages
  (26 platform variants, version 0.28.2) and `fsevents 2.3.3` (macOS).
  Both are **dev-only** (`"dev": true` in the lockfile); neither is in the
  published package, whose `files` list ships a prebuilt `dist` only.
- Packages with their own install scripts (`hasInstallScript: true` in
  the lockfile, exactly 2): `esbuild 0.28.2` (line 840 of the lockfile;
  its postinstall validates/selects the platform binary, standard for
  esbuild) and `fsevents 2.3.3` (line 1054; node-gyp build on macOS,
  standard for fsevents). Both dev-only.
- Abandoned-looking packages: a few old-but-stable utilities in the
  express stack (`ee-first 1.1.1`, `unpipe 1.0.0`, `vary 1.1.2`,
  `once 1.4.0`) are unmaintained in the sense of being finished, tiny,
  and ubiquitous; none is a known-compromised or renamed package.
- The project itself fixed a transitive issue in its history:
  commit `9ecaa3a` (2026-11-13) "fix: update hono and @hono/node-server",
  which is dependency hygiene happening in the open.

Sub-point marked **UNVERIFIED**: the *internal* network behaviour of
transitive dependencies was not line-audited (130 packages). What was
checked: names/versions against known telemetry packages (none), install
scripts (2, both standard), and the fact that the server's own code only
exercises the SDK's stdio transport path in normal use. A full transitive
audit would need a per-package source review, which is out of proportion
here; the settling check, if ever required, is an egress-blocked run
(section 6) which makes the question moot in practice.

Also **UNVERIFIED**: that the published npm tarball for 0.6.0 is
byte-identical to a build of the git tag. Checking that requires
downloading and building, which the read-only rule for this lane
excluded. The release workflow (`.github/workflows/release.yml`) builds
from the tag with `npm ci`, typecheck, unit tests, `npm pack` with
SHA256SUMS, and OIDC trusted publishing with provenance, which is the
right shape, but shape is not proof.

### 3.3 CI (dependency-relevant)

`.github/workflows/ci.yml`: matrix Windows/Ubuntu/macOS x Node 22/24,
runs `npm ci`, typecheck, build, `context:check`, and unit tests. The
live Zen suite is explicitly excluded from CI and release (needs a real
desktop Zen).

---

## 4. Permissions: the complete demand list

| Demand | Evidence | Exposure |
|---|---|---|
| Browser extension | **None.** No extension, no `manifest.json`, no native-messaging manifest anywhere in the tree (searched `manifest`, `nativeMessaging`, `<all_urls>`, `webRequest`). README at HEAD and v0.6.0: "Nothing is installed into Zen itself; the bridge is injected at runtime." Injection is via Marionette chrome JS at runtime (`src/bridge/host.ts:1973`). | Nothing persists inside Zen after the owned browser quits. |
| Debug/control port | Marionette, Zen's own listener, on **127.0.0.1:2828** by default (`src/zen/marionette.ts:12-13`; `src/config.ts:32,59`). Zen is launched with `-marionette` by zen-mcp itself; no Zen preference is changed, so a normal Zen launch opens no port (`docs/security.md:30`). After ownership proof the server closes other Marionette sessions and calls `setAcceptConnections(false)`, so the port then refuses new connections (`docs/security.md:36-38`). | Loopback only in the project's code. Short unauthenticated race window between Zen start and lockdown, which the project discloses (`docs/security.md:133,149`): a same-user local process could race for a Marionette session; the server detects a competing session and aborts. Whether Zen's Marionette listener itself binds only loopback inside the browser is Firefox behaviour, **UNVERIFIED** from this repo alone. |
| Bridge port | WebSocket server on **127.0.0.1, ephemeral port**, loopback-only check plus mutual HMAC-SHA256 with a per-session 256-bit key and fresh nonce per connection (`src/bridge/host.ts:357-362,398-456`; `docs/security.md:42-46`). | Loopback, authenticated. |
| MCP transport | stdio only in normal use (client launches `zen-mcp serve`). No HTTP listener is opened by the project's own server code. | Local process boundary only. |
| Profile directory | The Node process does **not** parse profile files on disk: no reads of `cookies.sqlite`, `logins.json`, `key4.db`, `places.sqlite`, or session files exist in `src/` (searched `cookies`, `logins.json`, `key4.db`, `places.sqlite`, `sessionstore`). On-disk profile touches are: creating the dedicated profile dir (`src/zen/launcher.ts:232-234`) and reading the profile **lock** (`parent.lock` / POSIX lock symlink PID, `launcher.ts:341-376`). History and bookmarks are read *inside* the browser via the Places API (section 5), not from files. Default profile is a dedicated agent profile under zen-mcp's data dir (`launcher.ts:37-42`); the user's normal profile is used only on explicit opt-in (`useDefaultProfile`, `src/config.ts:18-21`). | Default: isolated profile with no user cookies, logins, or history. Opt-in normal profile is the dangerous mode (section 5). |
| OS access | Run as the user: spawn/kill processes, write zen-mcp config and data dirs, write MCP client configs on `onboard`, read `PATH`, `APPDATA`, `XDG_CONFIG_HOME`, `ProgramFiles`, `LOCALAPPDATA` for discovery (env reads enumerated from `src/`: only path/config/feature-flag variables, no credential-shaped variables). | Full user-level access, as with any local MCP server. No elevation, no sudo, no registry writes found (searched `winreg`/`registry` in code paths; the only "registry" in `src/` is the npm registry URL and in-memory registries). |
| Consent gate | `requireConsent` defaults to true (`src/config.ts`, `DEFAULT_CONFIG`); first tool use shows an in-Zen approval card; nothing is read or changed before approval (`docs/security.md:48-52`). Consent is per server process and there are no per-action cards after that. | One broad approval covers the session; Pause and read-only mode are the finer controls. |

---

## 5. Data exposure inventory (what the tools can read)

Tool names are the 55 in `src/mcp/catalog.ts`. "Can read" means a code
path exists in v0.6.0.

| Browser data | Can the tools read it? | Tool(s) and code path |
|---|---|---|
| Page content (text, Markdown, links, tables, outline, PDF text) | **Yes** | `zen_read_page`, `zen_read_pages`, `zen_find_text`, `zen_search_tabs`. Fixed read script in the bridge; http(s) pages only, background tabs included (`docs/security.md:70-74`). |
| Page structure / interactive controls, snapshot, semantic model | **Yes** | Same read tools with snapshot/semantic formats (`src/shared/read-script.ts`, `src/shared/semantic.ts`). Semantic model never carries field values (`docs/security.md:76`). |
| Form field values | **Mostly no, by design** | Sensitive fields (password, file, email, tel, payment, OTP, and hint-matched fields) are classified in `src/shared/sensitive.ts:7-55` and their values are withheld; snapshot reports only whether a non-empty value exists for sensitive fields (`src/shared/protocol.ts:740-751`); post-action effect probes return **hashes** of non-password form values, never the values (`docs/security.md:86`). `zen_type` reports a character count, not the text, and typing into a password field returns a limitation instead of echoing (`docs/security.md:84`). Non-sensitive field values can appear in interactive reads as part of control state; treat page reads as able to see ordinary form contents. |
| Browsing history | **Yes** | `zen_history_search`: SQL over `moz_places` inside the browser (url, title, last_visit_date, visit_count), `src/bridge/ops.ts:3966-4011`. **Not filtered by the domain allowlist** ("Metadata only; not filtered by the domain allowlist", `src/mcp/descriptions.ts:49-50`). In the default dedicated profile this is only the agent profile's own history; in normal-profile mode it is the user's real history. |
| Bookmarks | **Yes** | `zen_bookmarks_search`: SQL over `moz_bookmarks` join `moz_places` (title, url, dateAdded), `src/bridge/ops.ts:4014-4047`. |
| Recently closed tabs | **Yes** | `zen_history_recently_closed`: `SessionStore.getClosedTabData`, titles/URLs, http(s) only, `src/bridge/ops.ts:4049` onward. |
| Open tabs, spaces, folders, pins, essentials, containers | **Yes** | `zen_tabs_list`, `zen_spaces_list`, `zen_folders_list`, `zen_containers_list`, etc. Session save also stores the full layout of URLs locally (`zen_session_save`). |
| Cookies | **No tool, no code path found.** Searched `cookie`/`document.cookie`/`CookieManager` across `src/`: the only hits are the unrelated `cookie` npm package in the lockfile (an MCP SDK transitive dep) and URL-policy text. No tool returns cookies, and no bridge op reads them. | Absence verified by catalog plus full-tree search. |
| Saved credentials / logins | **No tool, no code path found.** No `logins.json`, Login Manager, or credential API use in `src/`. Password *fields on pages* are value-redacted as above. | Same basis as cookies. |
| localStorage / sessionStorage / IndexedDB | **No tool, no code path found.** Searched `localStorage`, `sessionStorage`, `indexedDB` across `src/`: zero hits in project code. | Same basis as cookies. |
| Clipboard | **Write only** | `zen_clipboard_write` writes text up to 1 MB (`src/bridge/ops.ts:4121-4156`). No clipboard read tool exists. |
| Browser events | Titles/URLs of allowed pages only | `zen_events`: tab/navigation/dialog events; never page text, form values, or dialog text; off-allowlist URLs are dropped and counted (`docs/security.md:88-103`). |
| Audit log (local file) | n/a (persistence, not exposure) | `audit.jsonl` in the data dir, owner-only, 5 MB rotation; URLs stripped to scheme/host/path, sensitive args replaced by length plus SHA-256 digest; a bounded preview of summarized args can remain, which the project discloses (`docs/security.md:113-123`). Nothing in the log is transmitted anywhere by the code. |
| Screenshots, downloads, uploads | **Not present** | README (v0.6.0): "there is no page screenshot, file upload, download handling". A click can still *trigger* a download in the browser as a page-level side effect (`docs/tools.md:92`). |

### Riskiest capabilities (ranked)

1. **`zen_click` + `zen_type`** (`src/mcp/guard.ts:70-71` lists them as
   the mutating page-input tools): real input events. A click can submit
   a form, make a purchase, or start a download; the allowlist checks
   URLs before and after but cannot predict page scripts
   (`docs/security.md:82,154`). Blocked in read-only mode and by Pause.
2. **Normal-profile mode** (`--use-default-profile`): turns every "yes"
   in the table above into the user's *real* signed-in pages, history,
   and bookmarks, and that text then flows to the MCP client's model
   provider. This is a configuration choice, not a defect, and it is the
   single decision that changes the risk class.
3. **`zen_tabs_open` / session restore / template apply**: can open
   arbitrary http(s) (and `about:` for tabs) URLs into the owned browser,
   subject to the domain allowlist when one is configured; the default
   allowlist is empty, meaning all domains allowed
   (`src/config.ts` `DEFAULT_CONFIG`, `docs/security.md:66-68`).
4. **`zen_clipboard_write`**: silent overwrite of the user's clipboard
   with agent-chosen text (up to 1 MB).
5. **Destructive organisation tools**: `zen_space_delete`,
   `zen_session_delete`, `zen_template_delete`, `zen_tabs_close`,
   folder/pin/essential mutation: can destroy browser organisation state
   inside the owned profile.
6. **The update-install path** (section 1.3): user-click-gated global
   install of `@latest` from npm; supply-chain trust in npm at click
   time.

What is **not** there matters equally: no agent-supplied JS eval, no
cookie or credential reader, no screenshot, no file upload/download
handling, no shell tool, no telemetry.

---

## 6. Code quality: the "vibe coded" claim, checked

The Reddit claim has two parts: (a) AI-generated-looking code, (b) only
tested on Windows. Part (b) is verified separately in section 7. For (a),
the honest finding is mixed, and the strongest signals cut against the
dismissive version of the claim.

Evidence **for** the vibe-code suspicion:

- Extremely compressed history: 69 commits from 2026-10-31 to 2026-11-21
  for v0.6.0 (80 commits to HEAD), 68 of 69 by a single author ("Spaxe",
  one external contributor commit), with 26 commits on 2026-11-01 alone,
  each landing very large feature blocks (v0.2 in a day: bridge, policy,
  sessions, UI). That velocity is consistent with heavy AI assistance.
- Very large files: `src/bridge/ops.ts` 4,247 lines,
  `src/shared/read-script.ts` 3,561, `src/mcp/server.ts` 3,323,
  `src/zen/runtime.ts` 2,297, `src/bridge/host.ts` 2,274 (of ~47,086
  total lines including tests). Generated-code workflows often produce
  such monoliths.
- Type-safety erosion exactly where the browser's untyped internals are
  touched: 47 `: any` / `as any` uses, concentrated in
  `src/bridge/ops.ts` and `src/bridge/chrome-globals.d.ts` (`Services:
  any`, `Components: any`). Some of this is forced by Zen/Firefox
  internals having no types, but the density is real.
- Pre-1.0 churn: README states the public API, tools, and configuration
  keys can still change between minor releases.

Evidence **against** the sloppy-vibe-code reading:

- Test mass: 42 test files, ~14,185 lines of tests, 542 `test(`/`it(`
  declarations counted in `test/unit` plus `test/integration`, including
  a dedicated `test/integration/security.e2e.test.ts`. Unit tests run in
  CI on three OSes and two Node versions; typecheck and build gate every
  push (`.github/workflows/ci.yml`). README concedes the limits honestly:
  "Unit tests are broad but not exhaustive. On Windows, `npm test` runs
  the full unit suite and skips five POSIX-specific tests. The live suite
  has 34 declarations across three files" (README, v0.6.0).
- Zero `TODO`/`FIXME`/`HACK` markers in `src/`, `test/`, `scripts/`
  (counted: 0). Whatever else it is, it is not littered with deferred
  stubs.
- Error handling is dense and deliberate: 319 `catch` occurrences and
  244 `throw new` in `src/`, with typed error classes
  (`src/shared/errors.ts`) and bounded, redacting audit summaries.
- Security engineering that vibe code rarely produces unprompted:
  symlink-refusing atomic owner-only writes (`src/utils/safe-file.ts`),
  an installer PATH-hijack defence with a written rationale
  (`src/zen/updates.ts:205-250`), mutual HMAC bridge auth with replay
  separation by direction (`docs/security.md:44`), launch-nonce ownership
  proof before recording a PID (`docs/security.md:32`), and a security
  document that lists residual risks against itself
  (`docs/security.md:147-156`), including admitting the Marionette race
  is "detected, not eliminated".
- Commit messages are conventional and specific (`fix:`, `feat:`,
  `test:`, `docs:`, `chore:` prefixes with concrete subjects throughout
  the log), and several commits are narrow audit-response fixes
  (e.g. `49fd208` "fix: close config, read-only, and input-cap
  audit gaps").

Verdict on this sub-point: **AI-assisted, very probably; sloppy, no.**
The fair label is "single-author, AI-accelerated, unusually
security-conscious pre-1.0 project". The residual risk is not code
sloppiness; it is bus-factor and the un-audited-by-third-parties nature
of a three-week-old project. Whether a specific Reddit commenter used
the exact phrase "vibe coded" is **UNVERIFIED**: the r/zen_browser
thread dated 2026-11-22 named in the assignment was not retrieved in
this lane's searches; the claims attributed to it were checked against
the repo directly instead.

---

## 7. Platform support: the "only tested on Windows" claim

**The claim is true, and the project says so itself.**

- README (v0.6.0), status line: "Windows is the only platform with a
  live-tested Zen launch."
- README platform table (v0.6.0): Windows "Verified live: launch,
  consent, evidence, shutdown", Zen 1.24b, evidence date 2026-11-02;
  macOS "Unverified live; code paths and CI only"; Linux "Unverified
  live; distro, Flatpak, and Snap paths pass CI only". And: "Treat
  macOS and Linux as untested until a live launch, the consent card,
  and a clean shutdown have passed on that platform."
- `docs/troubleshooting.md` known limitations repeats it.

But "only tested on Windows" does not mean "Windows-only code". The
cross-platform work is real:

- CI matrix runs typecheck, build, and unit tests on
  `windows-latest`, `ubuntu-latest`, `macos-latest` x Node 22/24
  (`.github/workflows/ci.yml`).
- Zen discovery has explicit branches per OS
  (`src/zen/launcher.ts:91-132`): Windows `ProgramFiles`/`LOCALAPPDATA`
  `zen.exe` paths; macOS `/Applications/Zen Browser.app/...`; Linux
  `/usr/bin/zen`, `/opt/zen/zen`, Flatpak exports
  (`app.zen_browser.zen`), and `/snap/bin/zen-browser`.
- Process handling is per-OS: `tasklist`/`taskkill` on win32,
  `pgrep -x` with a multi-name list (`zen`, `zen-bin`, `zen-browser`,
  `zen_browser`, `zenbrowser`) on POSIX (`launcher.ts:149-181`), and a
  POSIX profile-lock PID parser (`launcher.ts:371-376`) beside the
  Windows `parent.lock` check (`launcher.ts:341-360`). Commit `09c909d`
  (2026-11-02) is literally "fix: cover POSIX Zen process names and
  platform status".
- Config paths branch correctly: `%APPDATA%` on Windows,
  `$XDG_CONFIG_HOME` or `~/.config` elsewhere (`src/config.ts:74-76`;
  `src/onboard/clients.ts:1487-1513` handles the same split for 28
  client configs).
- Windows-specific hardening exists where Windows is genuinely
  different (installer resolution, `updates.ts:210-299`), not as the
  only path.

Platform verdict: **live behaviour is proven only on Windows; macOS and
Linux are engineered-for and CI-tested but live-unproven.** On this
team's Linux machines, a first live run is itself an experiment, which
is exactly what an isolated test environment is for.

---

## 8. VERDICT

### SAFE — for installation in an isolated test environment, at v0.6.0, under the conditions below.

Evidence chain, in one pass:

1. **No exfiltration channel in the project's own code.** The single
   outbound request is a version check to the npm registry carrying
   only a `zen-mcp/<version>` user-agent (section 1.1), and it can be
   switched off. No telemetry, analytics, or error-reporting code or
   dependency exists (sections 1.2, 3.2). All browser control traffic
   is loopback (Marionette `127.0.0.1:2828`, authenticated bridge
   WebSocket on an ephemeral `127.0.0.1` port) (section 4).
2. **Nothing runs at install time at v0.6.0.** No preinstall, install,
   postinstall, or prepare script in the package; the tarball ships a
   prebuilt `dist` only (section 2.1). The only dependency install
   scripts in the lockfile are esbuild's and fsevents', both dev-only
   and standard (section 3.2).
3. **The dangerous data is not reachable.** No tool or code path reads
   cookies, saved credentials, or web storage (section 5). The default
   profile is a dedicated, empty agent profile; the user's real profile
   is touched only on explicit opt-in (section 4).
4. **The agent-facing surface is fixed operations, not code.** 55
   structured tools, no agent-supplied JavaScript, no shell tool, no
   screenshot/upload/download handling (sections 2.4, 5). The powerful
   chrome-context execution is internal to the server binary and gated
   by a one-time in-browser consent card by default (section 4).
5. **Dependencies are mainstream.** 4 direct runtime deps (MCP SDK,
   commander, ws, zod), 130 lockfile entries, no telemetry packages, no
   typosquat-shaped names (section 3).

Conditions the verdict depends on (all of them are the test setup, not
hopes):

- **Pin version 0.6.0** (`@spaxe-dev/zen-mcp@0.6.0`), not `@latest`:
  0.6.3 adds a postinstall skill offer that can fetch and globally
  install a skill from GitHub on a yes answer (section 2.3). That does
  not make 0.6.3 malicious, but it is a different install-time surface
  than the one audited here.
- **Use the default dedicated agent profile.** Never
  `--use-default-profile`, never point `profilePath` at a real profile.
  With the normal profile the verdict flips for data exposure: real
  history, bookmarks, and signed-in page content become readable and
  flow to the MCP client's model provider (sections 4, 5).
- **Set `ZEN_MCP_NO_UPDATE_CHECK=1`** if the test wants zero outbound
  traffic from the server itself; otherwise accept exactly one npm
  registry GET per start (section 1.1). Blocking egress entirely is
  the belt-and-braces option and also settles the UNVERIFIED transitive
  dependency question (section 3.2) by construction.
- **Run it as a throwaway OS user / VM** as "isolated test environment"
  implies: the server process inherently has full user-level OS access
  (spawn, kill, file writes, onboarding writes to client configs)
  (section 2.2). That is normal for a local MCP server and is the main
  reason the verdict is scoped to an isolated environment rather than
  a daily-driver account.
- **Treat Linux as unproven live** (section 7): expect possible launch
  or lifecycle bugs on Linux; in an isolated environment those are
  reliability risks, not security ones.
- Do not run `zen-mcp onboard` or `zen-mcp update` in the test unless
  testing them specifically: onboard writes other tools' config files,
  and update replaces the installed code with `@latest` (sections 1.3,
  2.2).

What would change the verdict to NOT SAFE: a finding of any outbound
channel carrying browser data (none found), any install-time execution
in the pinned version (none at 0.6.0), a cookie/credential reader (none
found), or a requirement to use the real profile for the test (that is
a different test, and this verdict does not cover it).

UNVERIFIED sub-points, restated: (a) npm tarball identical to the git
tag build; settling check: download the tarball and a local tag build
and compare hashes, in the install step itself. (b) Transitive deps'
internal network behaviour; settled by egress blocking. (c) Zen's own
Marionette bind address inside the browser; settled by a socket listing
during a live test run. (d) The exact wording of the 2026-11-22 Reddit
thread; not needed for the verdict, which rests on the code.

---

## Sources (all accessed 2026-11-27)

- Repo, v0.6.0 tag and HEAD: https://github.com/spaxe-dev/zen-mcp
- README (v0.6.0, platform table and maturity section, in-repo):
  https://github.com/spaxe-dev/zen-mcp/blob/main/README.md
- Security model (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/docs/security.md
- Architecture (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/docs/architecture.md
- Security policy (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/SECURITY.md
- Tools reference (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/docs/tools.md
- Troubleshooting / known limitations (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/docs/troubleshooting.md
- CI workflow (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/.github/workflows/ci.yml
- Release workflow (in-repo): https://github.com/spaxe-dev/zen-mcp/blob/main/.github/workflows/release.yml
- npm package page (version listing only): https://www.npmjs.com/package/@spaxe-dev/zen-mcp
- All file:line citations above are to the v0.6.0 tag unless marked HEAD.
