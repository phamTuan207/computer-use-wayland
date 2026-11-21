# Desktop control landscape, agent-desktop, linux-use, kde-desktop-mcp, CUA on Hyprland, 2026-11-21

By clone2. Question: what can this repo learn from four newer
desktop control projects, and which parts apply on Wayland and
Hyprland. Short answer: all four converge on the same observation
channel, the AT-SPI accessibility tree over D-Bus, and they differ
in input delivery. Semantic AT-SPI actions are the low risk win.
Direct Hyprland socket window operations and honest input delivery
reporting are cheap to copy. A compositor plugin, the CUA route,
is the only one that gives true background control, at a real
pinned version and per app qualification cost. None of the four
replaces the browser protocol channels, CDP and BiDi and
Marionette still give DOM access no accessibility tree matches.

Two of the four were downloaded and run on this machine during
this research, timed results in section 6. Access date for all web
sources: 2026-11-21. Documented facts are stated plainly,
inferences are marked as inference.

## 1. Vercel agent-desktop

Identity: vercel-labs/agent-desktop on GitHub, a Vercel Labs
project, Apache-2.0, created 2026-02-19, about 25,851 stars and 51
releases at crawl time. Source:
https://github.com/vercel-labs/agent-desktop

What it is: computer use through the OS accessibility tree, no
screenshots or pixel matching as the primary method. It reads the
tree and returns JSON with a ref for every actionable element, the
agent clicks or types on a ref, then re-reads the UI to verify.
There is no model inside, the loop lives in the agent. It ships as
a CLI and a C library over a PlatformAdapter that talks to the OS
accessibility API, and running it as an MCP server exposes every
command as an MCP tool over stdio. Its command set, 61 names,
covers observe (snapshot, find, get, is, screenshot,
list-surfaces), ref actions (click, double-click, right-click,
type, set-value, clear, focus, select, toggle, check, uncheck,
expand, collapse, scroll), apps and windows (launch, close-app,
list-apps, list-windows, focus-window, resize, move, minimize,
maximize, restore), plus keyboard, mouse, clipboard,
notifications, wait, sessions and sandboxes. Source: the repo
above, and the installed binary help output quoted in section 6.

Platforms: macOS 13 or later via the AX API, Windows 10 1809 or
later via UI Automation, Linux Ubuntu 24.04 or later, x86-64 or
aarch64, X11 or Wayland, with AT-SPI. It does not require KDE or
GNOME by name. Linux needs a graphical session of the signed-in
user and a running AT-SPI bus, a TTY or SSH shell without session
variables sees no apps. Source:
https://skillsafe.ai/skill/@vercel-labs/agent-desktop-linux/

Wayland behaviour, documented in the same Linux guide: observation
and semantic actions work on X11 and Wayland through AT-SPI.
Wheel scroll is physical input, X11 and headed mode only. Pointer
gestures such as double-click, triple-click, hover and drag are
headed X11 only and refuse on Wayland with ACTION_NOT_SUPPORTED.
Press and text keys work on X11 and on capability detected Mutter
Wayland sessions. The Linux adapter pull request reported native
Wayland pass counts of GTK3 33 passed and 3 failed, GTK4 21 passed
and 9 failed, Qt 35 passed and 4 failed. Source:
https://github.com/vercel-labs/agent-desktop/pull/298

Hyprland: not named as a measured target in the sources read.
Inference: semantic AT-SPI actions should behave as on other
Wayland sessions, but the Mutter specific keyboard note means
Hyprland cannot be assumed equal to GNOME Wayland.

Install: npm install -g agent-desktop, Homebrew, or release
archives. Verified locally, section 6.

Applicable here: the ref based loop itself, snapshot with refs,
act on a ref, re-read to verify, and a PlatformAdapter split where
each capability fails separately with a clear code such as
ACTION_NOT_SUPPORTED instead of a silent fallback.

## 2. linux-use

Disambiguation first, three projects share this name space:

- javimosch/linux-use, the exact name match, an agent-first CLI
  by Javi Mosch, MIT. This section is about this one. Repo facts
  checked through the GitHub API on 2026-11-21: license MIT, last
  push 2026-10-04, 0 stars, so a small personal project. Detailed
  behaviour below comes from secondary summaries, marked as such:
  https://www.techbytes.app/posts/linux-use-agent-first-gui-control-for-linux/
- wtyler2505/Linux-Use, a port of Windows-Use to Linux targeting
  Mint Cinnamon, AT-SPI2 tree navigation plus python-xlib, wmctrl
  and xdotool, screenshots with pyautogui, and its own summary
  says actual GUI interaction was untested. Source:
  https://github.com/wtyler2505/linux-use/blob/HEAD/COMPLETION_SUMMARY.md
- agent-sh/computer-use-linux, not named linux-use but often
  confused with it: a Rust MCP server and CLI with semantic AT-SPI
  trees, bounded screenshots, compositor aware window targeting
  across GNOME, KDE and KWin, Hyprland, niri, COSMIC, i3, Sway,
  labwc and X11, Wayland input through the RemoteDesktop portal
  with a uinput fallback, Hyprland targeting via hyprctl, and a
  doctor command returning a JSON readiness report. Worth its own
  study if broad compositor coverage becomes a goal. Source:
  https://pi.dev/packages/@agent-sh/computer-use-linux

javimosch/linux-use, per the secondary summaries: a small static
binary, no LLM code inside. It enumerates apps, reads an app tree
with state, and acts with an act command taking an element
reference string, so the widget accessible action fires directly,
with no focus, no pointer move, and success even when the window
is occluded. It also streams AT-SPI events with a watch command as
newline delimited JSON. Element entries carry a reference path,
role, name, center coordinates and an action. The author reported
walking 28 interactive elements in gnome-calculator in 48 ms.
Changed or missing elements exit with code 83 and a fix
suggestion. Testing was manual only, Ubuntu 22.04.3, GNOME 42.9,
X11, six GTK apps verified and some Qt menus. Chromium and Edge
need --force-renderer-accessibility. On Wayland the accessibility
read paths work but synthetic input is broken, so full automation
is X11 only today, per that summary. Build needs libatspi2.0-dev,
libxtst-dev, libx11-dev, libglib2.0-dev, and
org.gnome.desktop.interface toolkit-accessibility set to true.

Applicable here: act by element reference on an occluded window is
directly relevant to Hyprland workspaces, where the target window
is often not focused. The watch event stream as newline delimited
JSON is a clean way to wait for UI changes instead of polling
screenshots. The distinct stale element exit code with a fix
suggestion is a small copyable reliability feature.

Not run here: building it needs X11 development libraries and its
full automation is documented as X11 only, so a headless Wayland
oriented run would not test anything its author claims.

## 3. kde-desktop-mcp

Identity: ahmetadakli/kde-desktop-mcp, a screenshot free desktop
control MCP server for KDE Plasma on Wayland, Hyprland, and
Windows, written in Rust as a single executable. Latest release
checked through the GitHub API on 2026-11-21: v0.17.0, with a
prebuilt x86-64 Linux tarball. README content read through the
Glama mirror, crawled 2026-11-21:
https://glama.ai/mcp/servers/ahmetadakli/kde-desktop-mcp
It is not kwin-mcp or kwin-mcp-server, those are separate projects
that run apps in isolated virtual KWin sessions.

Architecture, per backend, from the README:

- Reading: AT-SPI over D-Bus on both Linux backends, talked to
  directly without libatspi, with pipelined requests. Element
  actions are AT-SPI actions and EditableText.
- Keyboard: /dev/uinput on both Linux backends. Mouse: an
  absolute uinput pointer on KDE, Hyprland movecursor plus uinput
  buttons on Hyprland.
- Typing: on KDE, direct AT-SPI insertion into Qt multi-line
  fields, otherwise clipboard plus Ctrl+V with the previous
  clipboard restored. On Hyprland, wtype, otherwise the same
  clipboard path.
- Window operations: KWin scripting over D-Bus on KDE. On
  Hyprland, the Hyprland socket, with clients, monitors and
  dispatchers batched in one request, explicitly not hyprctl
  processes.
- Screenshot fallback: KWin ScreenShot2 or spectacle on KDE,
  grim on Hyprland.
- Backend selection is automatic: Hyprland when
  HYPRLAND_INSTANCE_SIGNATURE is set, otherwise KDE, override with
  DESKTOP_MCP_BACKEND. On Hyprland the active window is matched
  to its AT-SPI application by pid.

So yes, parts work without KDE by design: the Hyprland backend
replaces KWin scripting with the Hyprland socket, spectacle with
grim, and the KDE typing path with wtype, while AT-SPI reading
and uinput keyboard stay shared. It was verified on a real KDE
Plasma desktop, and Hyprland was verified in a nested session
inside KDE, per the README.

Speed design worth noting: tree output is compacted, examples
show a Dolphin plus Kate tree going from 15,182 to 7,092
characters and a Firefox page from 5,943 to 1,421. A tree read can
be reused while the app provably did not change and the read is
under 2 s old, one Firefox get_text example goes from 8.7 ms to
1.1 ms with that reuse. An AT-SPI call waits at most 2 s. Its own
benchmark section states that tool calls take milliseconds and
task time is dominated by model turns and by the size of what the
model reads. It ships tools/mcp_bench.py, which measures servers
with the same calls and prints median ms.

Tools include apps, tree, find, get_text with pagination, set_text
with verified readback, act with verified actions, click, key,
type_text, focus, drag, window operations, launch, clipboard,
wait_for, wait_idle, screenshot, doctor, and batch. Batch runs
several tools in one call, checked before anything runs, stops at
the first error, supports step references, conditions and repeat
until. Input replies state whether input was sent, maybe sent, or
nothing sent.

Coexistence design: a per app allowlist file with tiers view,
click and full, re-read on every call, input tools pause when the
user used keyboard or pointer in the last 1.5 s, a stop shortcut,
takeover detection, and an on-screen indicator on wlr-layer-shell.

Requirements: on Hyprland, a Hyprland session with the movecursor
dispatcher, at-spi2-core and wl-clipboard, recommended wtype and
grim, a working AT-SPI bus in the session, Qt apps may need
QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1, write access on /dev/uinput,
and the MCP client started from inside the Hyprland session so
the session variables reach the server.

Run here: section 6. It starts only as far as its session checks,
exactly as its requirements predict.

## 4. CUA, TryCua, Hyprland native

Identity: Cua from TryCua, repo trycua/cua, open core computer
use infrastructure, MIT for the driver, a background driver for
macOS, Windows and Linux over CLI and MCP, plus cloud sandboxes
and Cua-Bench. The repo page itself did not open in this research
pass, so its star count is not claimed. Sources:
https://www.rl-list.com/vendors/cua and
https://www.starryhope.com/linux/omarchy-cua-driver/

Linux driver: released for Linux on 2026-06-18 in version 0.5.7
for X11 and XWayland, native Wayland in preview, using AT-SPI2
over D-Bus for the tree and XTEST for input, tested on Debian 12,
Ubuntu 22.04 and 24.04, Rocky 9 and Fedora 41. Cua itself never
calls a model, the driving agent does the thinking, and there is
no Cua account. Sources as above.

Hyprland native background mode: a compositor plugin loaded into
Hyprland itself. The plugin is optional, the driver works without
it, and installing the package does not load the plugin or enable
input. The module installs at
/usr/lib/cua/hyprland/cua-hyprland-plugin.so, is loaded with
hyprctl plugin load, status is read with hyprctl -j cua:status,
and loading alone does not enable input. Background admission
requires the exact XKB keymap rules evdev, model pc105, layout us
with empty variant, options and file, the plugin enabled in the
Hyprland input config, a config reload, and the driver started
with CUA_DRIVER_RS_ENABLE_WAYLAND=1. In practice the agent then
gets a second pointer and keyboard of its own, a compositor
native synthetic cursor lets it operate a background window while
the user keeps their own pointer, and the user pointer never
moves in background mode. Multi monitor Hyprland support was
reported in cua-driver-rs v0.33.4. Sources:
https://github.com/danwahlin/omarchy-pkgs/blob/HEAD/pkgbuilds/cua-hyprland-plugin/README.md
and the independent guide above, run on 2026-10-16 on Omarchy
Edge with Hyprland 0.56.2-4.

Session variables matter in practice: without WAYLAND_DISPLAY,
XDG_RUNTIME_DIR, HYPRLAND_INSTANCE_SIGNATURE,
DBUS_SESSION_BUS_ADDRESS, XDG_SESSION_TYPE, XDG_CURRENT_DESKTOP
and DISPLAY passed to it, the driver reports not a Wayland
session and finds no windows.

Qualification scope, the part most summaries skip: the Omarchy
package profile pins Hyprland 0.56.2 and qualifies native Wayland
Inkscape 1.4.4 with the canonical US keymap. A retained canonical
run recorded all 128 required cells with 87 deliveries and 41
expected refusals and no failures. Outside that profile sit
current LibreOffice Calc, Chromium and Electron raw background
input, XWayland, Unicode and IME, non-US layouts and modified
pointer gestures. A background refusal never authorizes a hidden
foreground fallback. The independent guide found Inkscape was the
only installable app taking background input, and a background
click in Chromium was refused with background_unavailable and
client_not_qualified. Foreground actions on Hyprland change focus
and the pointer and do not restore them, and a foreground step is
refused while a physical key or button is held. While the plugin
is installed, an Omarchy update that moves Hyprland or the pinned
packages fails. Telemetry is on by default and is disabled with
cua-driver telemetry disable.

Speed: no published millisecond benchmark for the Hyprland plugin
was found, and none is invented here. The only hard numbers in
the sources are task level results including agent reasoning, a
foreground Chromium task at 58 s and a background Inkscape task
at 1 m 46 s, plus a documented 25 ms per character pacing for
type_text into native GTK clients from a driver pull request, so
bursts are not dropped.

Not run here: the Hyprland mode needs a running Hyprland
compositor to load the plugin into, which this headless VM does
not have. Its documented failure mode without session variables,
not a Wayland session and no windows, matches what the other
tools showed in section 6.

## 5. Comparison against the repo current methods

Repo today, from the repo own docs: screenshot plus pointer as
the general desktop path, Chromium over CDP, Firefox and Zen over
WebDriver BiDi through scripts/zen_cli.py, and Marionette through
Selenium as measured in the earlier clone2 report.

| Aspect | Repo today | agent-desktop | linux-use | kde-desktop-mcp | CUA Hyprland |
| --- | --- | --- | --- | --- | --- |
| Observation | screenshot, DOM or BiDi tree for browsers | AT-SPI tree with refs | AT-SPI tree with ref paths | AT-SPI tree, compacted, cached 2 s | AT-SPI tree |
| Primary action | coordinates, DOM calls | semantic action on a ref | semantic action on a ref, works occluded | semantic action, uinput fallback | semantic action, plugin background input |
| Window ops | Hyprland tools in repo | own window commands | minimal | Hyprland socket batched, or KWin scripts | hyprctl plugin status, compositor native |
| Input fallback | pointer and keyboard paths | physical input X11 headed only | XTest, X11 only | uinput, wtype, clipboard paste | plugin seat, own XKB state per lane |
| Works on Hyprland | yes, it is the target | semantic actions yes, gestures limited, untested on Hyprland per sources | reads yes, input X11 only per summary | yes, dedicated backend | yes, that is its purpose, pinned versions |
| Background work while user types | no | no | occluded windows yes, same seat | no, it pauses on user activity by design | yes, separate agent seat, qualified apps only |
| Needs a live session | yes for desktop path | yes, AT-SPI bus | yes | yes, plus /dev/uinput | yes, plus plugin and exact keymap |
| Browser pages | strong, DOM level | tree level only, Chromium needs the renderer flag | tree level only | tree level only | tree level, background input refused for Chromium |

Inference from the table: the four projects do not compete with
the repo browser work, they compete with its screenshot plus
pointer desktop path, and on that path they are ahead in one
specific way, semantic actions on named elements, with
verification by re-reading state instead of by looking at pixels.

## 6. Run results on this machine, 2026-11-21

This machine is a headless VM, no display, no session bus, no
at-spi2-core installed. Both runnable tools were installed
outside the repo and run with wall clock and elapsed timing.

agent-desktop, installed with npm into a tools folder, elapsed
for the install itself about 7 s including downloads:

- agent-desktop --version: prints agent-desktop 1.3.1. Its help
  confirms the design in section 1, snapshot captures the
  accessibility tree as structured JSON with @ref IDs, click is
  described as click element via accessibility press action.
- list-apps, wall clock 2026-11-21T09:30:52Z: exit 1, elapsed
  0.0056 s, error code PLATFORM_NOT_SUPPORTED, the AT-SPI
  accessibility bus is not available in this session, no D-Bus
  session bus reachable, with the suggestion to run inside a
  desktop session or under dbus-run-session.
- list-apps under dbus-run-session: exit 1, elapsed 0.0142 s,
  error changes to AT-SPI is not installed or not visible to
  this process, install the at-spi2-core package.
- snapshot under dbus-run-session: exit 1, elapsed 0.0094 s,
  PERM_DENIED with the same AT-SPI missing suggestion.

kde-desktop-mcp, prebuilt desktop-mcp v0.17.0 binary from the
project GitHub releases:

- Started as an MCP stdio server with an initialize request,
  wall clock 2026-11-21T09:31:05Z: exit 1, elapsed 0.0027 s,
  session bus connection failure, no such file for the session
  bus address. It checks the session before serving any tool.
- Under dbus-run-session, wall clock 2026-11-21T09:31:08Z:
  exit 1, elapsed 0.0154 s, accessibility bus unavailable,
  org.a11y.Bus was not provided by any service files, because
  at-spi2-core is not installed here.

Reading of these results: both tools install and start cleanly
and fail fast, in milliseconds, with precise staged errors that
name the missing layer, session bus first, then the AT-SPI bus.
That failure quality is itself a feature worth copying, and it
confirms on real runs the documented requirement chain. Nothing
about their in-session behaviour is verified by these runs, that
needs the laptop session, same as the AT-SPI prototype in the
companion document.

## 7. Recommendations for this repo

In order of value against risk:

1. Adopt the shared pattern now: AT-SPI tree reading with
   compact output, ref based semantic actions, re-read to verify.
   The AT-SPI prototype from this batch is the seed. agent-desktop
   is the reference implementation to compare against, and it is
   one npm install away on the laptop.
2. Copy kde-desktop-mcp Hyprland specifics: window operations
   over the Hyprland socket batched in one request instead of
   hyprctl subprocesses, tree caching only while the app provably
   did not change, input replies of sent, maybe sent, or not
   sent, and its batch tool, since its own benchmark notes say
   model turns and read size dominate task time, not call latency.
3. Copy the coexistence features before any always-on agent:
   per app allowlist tiers, pause on recent user input, a stop
   shortcut, and a layer shell indicator. kde-desktop-mcp has all
   four designed for exactly this compositor.
4. Treat CUA as the research direction for true background
   control, not as a dependency yet: the gain is real, an agent
   seat that never moves the user pointer, but the documented
   cost is pinned Hyprland and app versions, a US keymap
   requirement, per app qualification, and updates blocked while
   the plugin is installed. A qualification matrix like theirs,
   pinned versions plus a canonical run with deliveries and
   expected refusals counted, is worth adopting as a testing
   pattern either way.
5. Keep the browser channels primary for Zen and Chromium. Every
   project here reads browsers only at tree level, and Chromium
   background input is explicitly refused in the CUA profile.
6. Add a doctor style readiness report to the repo CLI: session
   variables present, session bus reachable, AT-SPI bus answers,
   toolkit switches, uinput access, each as its own line with a
   fix suggestion. Both runnable projects here show how much
   debugging time that saves.
