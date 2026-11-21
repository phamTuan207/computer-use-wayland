# AT-SPI for desktop control without screenshots, 2026-11-21

By clone2. Question: can an agent operate native desktop apps by
reading the accessibility widget tree and pressing widgets by name,
instead of taking screenshots and clicking coordinates. Short
answer: yes for GTK and Qt apps in a session where accessibility is
enabled, and the mechanism is display server independent because it
runs over D-Bus. The hard limits are per toolkit enablement, apps
that expose no tree, and the fact that under Wayland AT-SPI gives
semantic actions but not global coordinates or raw input injection.
Prototype: tests/atspi_prototype.py, measured results in section 6.

Access date for all web sources: 2026-11-21.

## 1. Architecture

AT-SPI is the Assistive Technology Service Provider Interface.
AT-SPI2 moved the transport from CORBA to D-Bus. The protocol is a
set of D-Bus interfaces in the org.a11y.atspi namespace that an
application implements, and clients consume through libatspi or its
Python binding pyatspi2. Source:
https://github.com/gnome/at-spi2-core/blob/HEAD/devel-docs/architecture.rst

There is a dedicated accessibility bus, separate from the session
bus. at-spi-bus-launcher owns org.a11y.Bus on the session bus,
starts a private bus for accessibility traffic, and answers
org.a11y.Bus.GetAddress. at-spi2-registryd keeps the desktop root
object whose children are the registered applications and forwards
events. A client starts at that root and walks down. Sources:
https://gnome.pages.gitlab.gnome.org/at-spi2-core/coverage/bus/at-spi-bus-launcher.c.html
and https://dogtail.gitlab.io/qecore/doc_basic_automation.html

How an app exposes its tree depends on toolkit generation. GTK2,
GTK3, Firefox, Chromium, LibreOffice and Java Swing implement the
ATK interfaces, and atk-bridge translates ATK into the AT-SPI
D-Bus interfaces. GTK4, Qt5 and Qt6, and WebKit skip ATK and call
the AT-SPI D-Bus APIs directly. Every accessible object offers the
same base vocabulary: children, name, role, states, and for
interactive widgets a list of actions plus a way to run one. A
button may present an action named click or press. Optional
interfaces add Text, EditableText, Value, Selection, Component and
Table. EditableText.SetTextContents replaces the full text of an
entry and returns a success boolean. Sources: the architecture
document above and
https://gnome.pages.gitlab.gnome.org/at-spi2-core/devel-docs/doc-org.a11y.atspi.EditableText.html

## 2. Toolkit support, who exposes a tree and who does not

Supported, per the architecture document and the references below:
GTK3 and GTK4, Qt5 and Qt6 through the Qt accessibility bridge,
Firefox through ATK, LibreOffice, Java Swing, WebKit apps.

Gated, tree empty until switched on:

- Qt: the bridge loads only when accessibility is requested.
  QT_ACCESSIBILITY=1 for the Qt4 era, QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
  named for Qt5. Sources: http://www.chiark.greenend.org.uk/doc/qt-at-spi/README
  and https://www.mail-archive.com/debian-accessibility@lists.debian.org/msg07791.html
- Chromium and Electron: the browser frame registers, but the web
  content tree is empty unless the browser was launched with
  --force-renderer-accessibility, or a real screen reader is
  detected. Source: https://github.com/william-long-ii/watson/issues/66
- Firefox: its accessibility service must not be force disabled,
  and the tree can be lazy, first queries can return empty.
  Source: same issue as above.

Expected to expose little or nothing, inference from the toolkit
model: apps drawn with SDL, OpenGL, Vulkan or a custom canvas,
most games, image and video editor canvas areas, and terminal
emulators that draw their own text grid. A field census on a
Hyprland machine supports this for terminals, see section 5.

## 3. Python control with pyatspi2

Essentials, from the pyatspi2 source and docs:

- desktop = pyatspi.Registry.getDesktop(0), iterate it for
  applications. Every accessible has .name, .childCount,
  .getChildAtIndex(i), .parent, and iteration yields children.
- Roles and states: obj.getRoleName() returns strings such as
  push button, entry, frame. obj.getState() is tested with
  .contains(pyatspi.STATE_VISIBLE), STATE_ENABLED, STATE_EDITABLE,
  STATE_CHECKED and similar constants.
- Actions: action = obj.queryAction(), action.nActions,
  action.getName(i), action.doAction(i) returns a boolean.
  Source: https://github.com/GNOME/pyatspi2/blob/master/pyatspi/action.py
- Text: text = obj.queryText(), text.characterCount,
  text.getText(start, end). For buttons and labels the visible
  text is usually just .name.
- Writing: editable = obj.queryEditableText(),
  editable.setTextContents(value) replaces all text,
  editable.insertText(position, value, length) inserts.
- Values: value = obj.queryValue(), value.currentValue is
  readable and writable for sliders, spin buttons, progress bars.
- Events: pyatspi.Registry.registerEventListener(callback,
  "window:activate", "object:state-changed:focused",
  "document:load-complete") then Registry.start() runs the loop.
- Probing an interface an object does not implement raises, so
  wrap queryAction, queryText and similar calls in try and except.
  Held references go stale when widgets are destroyed, re walk
  from the app root after any action that changes the UI.

Dogtail is a maintained higher level wrapper over the same stack:
from dogtail.tree import root, then root.application(name) and
child(name, role).click(). Source:
https://dogtail.gitlab.io/qecore/doc_basic_automation.html

## 4. Wayland behaviour, what works and what breaks

Tree traversal, roles, names, states, actions and text work under
Wayland, because all of it travels over D-Bus, not over the
display protocol. A Wayland feasibility study for another
automation framework lists as working: full tree traversal, roles,
names, states, actions, text, selection and value queries.
Source: https://github.com/d-biehl/robotframework-platynui/blob/HEAD/dev-docs/platform-linux-wayland.md

Why a press needs no coordinates: the action call is a D-Bus
method on the accessible object inside the target process, and the
toolkit performs the activation itself, the same path as keyboard
activation of a focused widget. No pointer position and no
compositor permission are involved. The flip side: if a widget
exposes no action, AT-SPI offers no fallback click at its location
under Wayland.

What breaks under Wayland, documented:

- Global coordinates. Component GetExtents with SCREEN returns
  0, 0, because Wayland clients do not know their absolute screen
  position. WINDOW relative extents still work. GNOME states the
  same in project terms: parts of the ATK model that assume global
  coordinates cannot be implemented under Wayland, and UI tests
  are majorly affected by the lack of global positions and the
  inability to inject input events. Sources: the PlatynUI study
  above and https://wiki.gnome.org/Projects(2f)GTK(2f)Accessibility.html
- Raw input. Synthetic keyboard and mouse under Wayland need a
  compositor granted channel, libei on GNOME and KDE, or the
  wlroots virtual pointer and virtual keyboard protocols. Typing
  into a control that has no EditableText interface therefore
  needs a second mechanism next to AT-SPI. Source: the PlatynUI
  study above.
- Window management stays compositor specific, there is no EWMH
  equivalent. On Hyprland that half belongs to Hyprland IPC.

Hyprland inference: the semantic half of AT-SPI is compositor
independent and should work on Hyprland for apps that join the
bus. The Dogtail Wayland input path depends on a GNOME daemon
using Shell introspection and Mutter portals, so it should not be
expected on Hyprland. No Hyprland project documentation stating an
official AT-SPI position was found in this pass.

## 5. Hyprland field evidence, third party measurement

A live census on a Hyprland machine, at-spi2-core 2.60.4,
registryd running and org.a11y.Status.IsEnabled true, found 13
registered apps, mostly shell applets, one Chrome window exposing
zero children, and five open terminal windows not appearing in the
registry at all. The same note measured walking a small applet
tree at 87 elements in about 20 ms, roughly 0.22 to 0.24 ms per
element for name and role fetches. Source:
https://github.com/ilyaskhallouki/hyprsay/blob/HEAD/docs/research/vision/prior-art.md
This is a third party measurement, not a Hyprland project claim,
and not re measured by clone2.

## 6. Prototype and measured results on this machine

tests/atspi_prototype.py implements one shared node interface with
two backends. The live backend wraps pyatspi objects. The selftest
backend is an in-memory fake editor, entry, Save button, Cancel
button, status label, where the Save action copies the entry text
into the status label, so a press is verified by reading real
state back. Both backends run the same list windows, find widget,
set text, press and verify logic, each step timed with wall clock
and a monotonic elapsed clock, JSON log with --log-json.

This machine is a headless VM: no pyatspi, no gi, no session bus,
no display, no at-spi daemons. Measured run, 2026-11-21,
wall clock 2026-11-21T09:29:45Z, auto mode, exit code 0:

- live_import_and_list_applications: FAIL in 0.0001 s,
  ModuleNotFoundError, No module named pyatspi. Recorded in the
  log, not hidden. Live desktop control is UNVERIFIED on this
  machine and needs a graphical session.
- selftest, all steps ok, total elapsed 0.0004 s for the whole
  auto run: build fake tree 7 objects, list windows found the
  Fake Editor frame, find entry, set entry text, find Save button
  by name and role, press via its click action, verify status
  label read back "saved:clone2 atspi test".

Honest reading of these numbers: the selftest times the logic in
memory, it is not a D-Bus measurement and must not be compared
with live timings. The only live AT-SPI timing available today is
the third party census in section 5, about 0.22 to 0.24 ms per
element walked, and a single doAction is one D-Bus round trip
after the search.

Run it on the laptop, inside the graphical session:

    gsettings set org.gnome.desktop.interface toolkit-accessibility true
    python3 tests/atspi_prototype.py --mode live --app "Text Editor" --button Save --log-json /tmp/atspi-live.json

Adjust the app fragment and button name to an open GTK app.
Check first with Accerciser that the app appears in the tree.

## 7. Speed, semantic press against screenshot plus coordinates

A semantic press costs one tree search plus one D-Bus round trip.
The search is the variable part: the census rate above implies a
few hundred elements cost tens of milliseconds. A screenshot path
costs a capture, a locate step, in this repo a model round trip at
seconds scale, a pointer move and click, and usually a second
capture to verify. AT-SPI also verifies by reading state back,
which is another cheap tree read, not another image. Where an app
exposes a good tree, AT-SPI should be the primary method for that
app and screenshots the fallback. Where it exposes nothing,
canvas, games, terminals, AT-SPI contributes nothing and the
screenshot path, or the app own protocol such as BiDi for
browsers, stays primary. Numbers for the repo own methods are in
the batch speed comparison document.

## 8. Failure modes checklist

- App node missing or zero children: accessibility off for that
  toolkit, Qt variable missing, Chromium flag missing, or the app
  has no accessible toolkit.
- Sandboxed apps: the a11y bus has no access control and all
  clients see each other, which historically blocked simply
  giving sandboxed apps the bus. A short term fix later let Orca
  work with sandboxed apps. Sources: the GNOME GTK accessibility
  page above and https://lwn.net/Articles/971541/
- Stale accessibles: calls on destroyed widgets fail with IPC
  errors, treat exceptions during a walk as normal and re walk.
- Big trees: the protocol is chatty by design, walking a large
  browser or office tree with several thousand nodes, fetching
  name, role, states and actions per node, can cost seconds and
  stall on a busy app. Prefer targeted searches, prune subtrees,
  and wait on events instead of polling the whole tree. Sources:
  the architecture document above and the LWN article above.
- Wrong session: a script run from SSH, cron or a service with a
  different DBUS_SESSION_BUS_ADDRESS sees an empty desktop. Run
  inside the graphical session or export that session address and
  XDG_RUNTIME_DIR.
- Enablement quick checks: NO_AT_BRIDGE=1 disables the bridge,
  so check it is not set. Confirm at-spi-bus-launcher and
  at-spi2-registryd run as the session user, and that
  org.a11y.Bus.GetAddress answers on the session bus.

## 9. What this means for the repo

1. Add an AT-SPI backend for native apps next to the browser
   backends: list apps and windows, snapshot a subtree as name,
   role, states and actions, press by name and role, set entry
   text. The prototype in tests/atspi_prototype.py is the seed,
   its node interface is the seam.
2. Use it as primary for GTK and Qt apps, keep screenshots as
   fallback for canvas and tree less apps, and keep BiDi primary
   for Zen, where the DOM is richer than the accessible tree.
3. Pair it with a wlroots virtual keyboard channel only for
   controls with no EditableText, never as the first path.
4. On the laptop, run the live mode against one GTK app and one
   Qt app and record real per step timings before deciding how
   much of the desktop workflow moves to AT-SPI.
