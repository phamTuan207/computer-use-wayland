# Provenance and measured validation

Built and tested 2026-10-06 on this machine: Hyprland/Wayland, eDP-2 1920×1200, scale 1, transform 0. Independent temporary Chromium profiles and a GTK3 form were used; no external accounts or services were modified. Tests restore the previous focused window and stop only their own processes.

## Design sources

- [OpenAI computer use](https://developers.openai.com/api/docs/guides/tools-computer-use): code execution is recommended for Astra; keep the environment available, group short predictable actions, return observations, and assess final state. The helper provides that local execution layer, not OpenAI's desktop plugin.
- [agent-sh/computer-use-linux](https://github.com/agent-sh/computer-use-linux): semantic AT-SPI actions before pixel input, bounded trees and screenshot metadata. Studied its documented architecture; did not install its daemon or use its legacy Hyprland dispatch syntax.
- [kurojs/wayland-mcp](https://github.com/kurojs/wayland-mcp): action chaining and separation between observation and input. Studied its public interfaces; no extra VLM/model proxy installed.
- [atx/wtype](https://github.com/atx/wtype) and local `wtype(1)`: existing virtual keyboard, named XKB keys, `-M`/`-m` modifiers, `-P`/`-p` held keys and `-s` delays. ydotool was considered but is not installed and `/dev/uinput` is absent; no root/input-group changes made.
- [wlr virtual pointer](https://wayland.app/protocols/wlr-virtual-pointer-unstable-v1): absolute extents and output-bound pointer creation. Bundled protocol XML preserves its MIT copyright notice. The helper's C driver adds output binding, placement checks and persistent drag state.
- [Chromium/Electron non-BMP keyboard issue](https://github.com/electron/electron/issues/49894): independently reproduced here (`🐱` became U+F431). Browser CDP insertion and native AT-SPI setter returned correct text. Desktop keyboard rejects such strings before input.

## Tests and numbers

- Native 24×24 px target: 12/12 click handlers fired, every click trusted, screenshot resized to 960 px width. Cropped screenshot also mapped correctly.
- Native batch total median 271 ms, maximum of 12 runs 277 ms: placement checks, image preflight and final capture included; shell startup and model reasoning excluded. Previous runs on this machine were ~302–303 ms. These are observed timings, not service guarantees.
- Browser form: three actions (Unicode fill, click, final-state assertion) took 34 ms of execution inside CDP; Node startup, initial observation and model reasoning excluded.
- Native keyboard: 14 actions in one existing wtype process, 573 ms execution in the GTK fixture. Verified Ctrl+A, Home/End, Shift+Right three times, Delete, Backspace, Return, F1, PageUp/PageDown and Tab/Shift+Tab against event logs and final text.
- Semantic AT-SPI: full Vietnamese+emoji text verified and button handler fired, 4 ms mutation time; interpreter startup, DBus discovery, subsequent tree snapshot and model reasoning excluded.
- Native Chromium Ctrl+T/Ctrl+W opened and closed exactly one test tab. Browser DND handler confirmed native drag/drop.
- Root agent visually read a GTK screenshot, selected button/input coordinates, then used installed CLI for a four-action batch. App recorded exactly one click and `Codex kiểm tra bàn phím`.
- Rejections tested: invalid coordinates before any action, stale DOM refs, covered DOM button, changed desktop screenshot, bad keyboard names and non-BMP keyboard input. Unit test specifically catches a small changed target even when whole-image average barely changes.
- Both skill paths passed the skill-creator validator. Codex `skills/list` reported `computer-use` enabled; OpenCode v2 `/api/skill` listed the new skill among 34 skills. No model turn was started for discovery checks.
- CLI tabs, DOM observation with image output, doctor, accessibility discovery and managed-profile browser startup were exercised. The managed-profile test closed only its own process and restored previous focus.

## Practical limits

These tests establish the helper's input/mapping behavior in the tested apps, not model vision accuracy across arbitrary applications. Multi-monitor, fractional-scale and rotated mapping have mathematical unit tests but were not tested with physical outputs. Dynamic scenes can produce conservative image-preflight refusals. Native a11y is available only when the app exposes it; existing Chromium/Zen sessions were not reconfigured to expose accessibility. CDP collection is top-document only. Compositor/global shortcut handling, XWayland apps and all function/media keys are not universally validated.

No exact token savings measured. Bounded DOM/a11y output and fewer tool/model round trips reduce unnecessary context by design; screenshot token cost and model latency depend on the host/model. Loading skill does not grant extra sandbox permissions.

## Reproduce

```bash
python3 ~/.local/share/agent-computer-use/scripts/build.py
python3 -m unittest discover -s ~/.local/share/agent-computer-use/tests -p 'test_*.py'
python3 ~/.local/share/agent-computer-use/tests/live.py
python3 ~/.local/share/agent-computer-use/tests/keyboard_live.py
python3 ~/.local/share/agent-computer-use/tests/exact_live.py
```

Live tests take the foreground briefly; run sequentially. Results are written to `tests/latest-results.json` and `tests/keyboard-results.json` under `~/.local/share/agent-computer-use`. Before changing installed skills, backups were saved under `backups/20261006-202358`.

## Optimization pass, 2026-10-06

- Shared skill reduced from 4,728 to 2,712 characters (43%); desktop action JSON averaged 652 to 263 characters (60%). Character reductions are not measured model-token savings.
- Zen disposable profile: 12 literal-text cases with Bamboo active, English/Vietnamese/URL/leading dash; exact values checked through the local page. IME restored after every literal batch. Ctrl+Space round trip, explicit Telex `chaof ` → `chào `, compact CLI stdin actions and separate local submission verified.
- GTK regression: 14 keyboard actions across five context-preserving groups, 745 ms execution; Unicode+emoji accessibility setter and button took 6 ms. A reproduced final-keymap-slot binding failure was avoided by reserving VoidSymbol with release only; no meaningless key-down, clipboard change or extra delay. Waiting alone did not fix it. This identifies an effective workaround, not a fully proven upstream root cause.
- Zen wheel initially failed intermittently. Wheel requests now include discrete detents; a 30 ms pause after pointer motion plus a 2 px non-click motion near the intended target reestablishes pointer focus in the successful runs. Some failed runs delivered neither hover nor wheel; the exact compositor root cause is not established. Scroll outcomes are verified, not inferred from event delivery. Generic scrolling still requires observing the correct container.
- Desktop screen-change refusals return a fresh observation without another model/tool capture round. Unit tests verify IME restoration on a typing exception. Zen is absent from the current AT-SPI application list; no existing browser accessibility/preferences were changed.
- Results: `tests/optimization-results.json`, `tests/latest-results.json`, `tests/keyboard-results.json`. Benchmarks exclude model decisions and host approval overhead; no new Facebook message was sent during this pass. Backups: `backups/20261006-221242`.

- Additional focus check found GTK Shift+Tab did not actually return to the entry despite a recorded key event. The helper maps it to `ISO_Left_Tab` with Shift; tests now check actual entry focus and standalone editing outcomes. Editing-only groups also temporarily deactivate composition. User trackpad interference was confirmed during one interrupted turn; foreground tests must run without concurrent manual input.

Final successful Zen report: 12/12 literal cases, 21/21 bidirectional nested wheel cases, median native batch 438 ms (max 501 ms); explicit Telex and compact installed CLI verified. Final GTK report confirms reverse Tab focus and standalone End/Backspace/Home/Delete. All 14 unit tests and both shared skill validations pass.
