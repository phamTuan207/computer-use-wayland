# Worker CLICK-CRAWL-DOMA11Y log - DOM/a11y automation crawl

Worker: CLICK-CRAWL-DOMA11Y. Scope: crawling + candidate list only. No live driving, no browser tasks, no implementation, no live tests. Never ydotool.

## Run clock (Asia/Ho_Chi_Minh)

- Start: 2026-11-22 02:05:29 +07 (t+0s)
- Repo fetch + baseline read: 02:05-02:09 (t+0-4m)
- Scrapling batch 1 (12 URLs): 02:06-02:07, all 12 returned 200 except one 404 (t+1-2m)
- Scrapling batch 2 (12 URLs): 02:07-02:08, 10 OK, one 403, one 404 (t+2-3m)
- CDP protocol JSON raw re-fetch + targeted greps: 02:08-02:09 (t+3-4m)
- Repo gap check (hypr_cmd, cdp.mjs, a11y.py): 02:09:29 (t+4m)
- Log written: 2026-11-22 02:10 +07 (t+5m)
- End: 2026-11-22 02:11 +07 (t+6m)

## Goal bar (judge every candidate against exactly this)

One vision (one observation) drives as many actions as possible, total task time reduced as much as possible, accuracy 90% or above. One vision, max actions, minimal total time, accuracy >= 90%.

Acceptance context recorded during this run (from MEMORY.md updates, not from this worker): the benchmark is a 2-vision task (vision 1 finds all input fields + buttons of clone1 + clone2 on ws2, one script does all clicks + sends with no vision, vision 2 checks both messages sent). The benchmark runs AFTER improvements are judged good, not before. Order: (1) research + improve one-vision, (2) run the 2-vision benchmark to prove it, (3) then todolist + error-file fixes. Method is free: use an existing tool or build one, result is what matters.

## Proven failure this crawl must fix

Muse read an input field about 90px too high from a JPEG (clicked (250,1037), real field center (306,1132)). Fix direction: exact rects from DOM/a11y, click point = rect center, no screenshot reading to locate the field. Note the failure was a vision-grounding read error, not a coordinate transform error: the click itself landed where aimed. So the highest-value candidates are the ones that remove the JPEG read from the locate step entirely.

## Method

- Scrapling venv ~/workspace/scrapling-trial-venv, scrapling 0.5.1, PLAIN Fetcher only. StealthyFetcher never used (blocked by VM proxy per brief).
- Batch 1: 12 URLs, all fetched with plain Fetcher. Batch 2: 12 URLs, plain Fetcher. Raw CDP protocol JSON re-fetched separately because the first stripped-text save lost JSON method names (my tag-stripper ate the JSON); the raw file at /tmp/crawl-doma11y/cdp-protocol-raw.json (1,425,607 bytes) was then grepped directly.
- Fallbacks used: browser.search for LDTP tutorial, Dogtail examples, Brave CDP launch flags, Firefox AT-SPI exposure (4 searches). browser.open not needed; search snippets plus Scrapling fetches covered the sources.
- Scrapling failures: none in batch 1/2 as transport failures. Two sources returned 403 (Brave support page, GNOME AT-SPI wiki) and two returned 404 (MDN GetElementRect page, Hyprland hyprctl wiki page); content for those topics was recovered from other fetched sources (W3C WebDriver spec, CDP protocol JSON, browser.search results). GitLab dogtail page returned a sign-in wall in stripped text (status 200, no usable content); Dogtail content was recovered via browser.search (PyPI + docs pages).
- Scope: computer-use project only. Public technical sources only. No personal info, no credentials.

## Repo baseline - what already exists (do NOT re-propose as new)

Read before crawling, from the repo at ~/workspace/computer-use-wayland, branch todolist-push:

1. scripts/zen_dom.py (334 lines): single-session Marionette manager. ZenSession with file lock, geckodriver per session, guaranteed session delete. locate(selector) returns exact rect via getBoundingClientRect in CSS pixels with center_x/center_y. tab_at(index) targets one tab by known handle index without scanning. evaluate() runs JS. verify() checks a DOM condition after a real mouse click. Rule in the docstring: DOM is used to LOCATE and READ, clicks are NOT done through the DOM (BiDi click failed to fire a handler 21/11; Marionette click fails on windowed Zen, 0x0 viewport quirk); caller does the real mouse click through cu.py. Missing: no multi-element harvest (locate is one selector per call), no scrollIntoView helper, no focus helper, no CSS-px to screen-px conversion.
2. scripts/a11y.py (238 lines): AT-SPI adapter via pyatspi (gi.repository Atspi). observe(pid), query(pid, name/role), ground(snapshot_path, ref) returns screen extents plus root window extents, drill(path, ref), act(path, actions) with text verification. _component_extents() returns exact AT-SPI Component screen box, but extents are only collected when CU_PICK4_FASTPATH=1 (opt-in, default off). Missing: extents off by default, no bulk harvest, no role/name index across the whole tree in one pass, no caret-offset to screen-xy helper.
3. scripts/cdp.mjs (528 lines): dependency-free CDP adapter (Node 22 WebSocket). Uses Runtime.evaluate, Input.dispatchMouseEvent, Input.dispatchKeyEvent, Input.insertText. Already does e.scrollIntoView({block:'center', behavior:'instant'}) before CDP clicks and already checks document.activeElement for editable focus (line 425). Missing: no DOM.getBoxModel / DOM.getContentQuads, no Accessibility.getFullAXTree, no bulk rect harvest.
4. scripts/hypr_cmd.py:109: already parses `hyprctl clients -j`. The window-geometry half of the coordinate conversion already has a reader; the conversion itself (CSS px + window at/size + devicePixelRatio + scroll) is not built anywhere.
5. docs/zen-dom-control-comparison.md: 5 tools tested live 21/11. Selenium + geckodriver WORKS headless, PARTIAL windowed. Puppeteer via BiDi PARTIAL, click FAILED. Playwright 1.65.1 moz-firefox BROKEN. Single-session slot: BiDi and Marionette share one slot, a leak blocks ALL remote control until Zen restarts.
6. docs/redteam-council-20261121/worker3-coordinate-redteam.md: prior art that overlaps this crawl. It already notes Playwright boundingBox (relative to main frame even for child-frame elements), iframe rect recursion per frame level, and that cross-origin iframes cannot be scripted from the parent (same-origin policy) so elements inside them fall back to vision or BiDi browsing-context-scoped calls. This crawl does not re-argue those points; candidates below cite them where they bite.

## Measured numbers - honest status

No public source fetched in this crawl reports an accuracy percentage or a millisecond latency for DOM/a11y grounding. The sources report behavior (exact rects, viewport-relative, null when not visible), not benchmark numbers. The only measured numbers available are in-repo: the failure itself (about 90px high, click (250,1037) vs real center (306,1132)); BiDi click failed to fire a handler (21/11); Marionette click fails on windowed Zen (0x0 viewport quirk). Any candidate below that claims a number is marked as such; the rest say "no numbers reported" rather than inventing any. Live measurement is the job of the testing phase after council + redteam review, not this crawl.

## Candidates

Each candidate has: what it is, source (URL + title + date accessed), goal-bar mapping, concrete applicability to our stack, measured numbers, verdict.
Date accessed for all sources: 2026-11-22. All URLs below are copied verbatim from fetch/search results.

### C1. One-shot bulk DOM rect harvest: all targets in a single evaluate call (Zen Marionette + Brave CDP)

What it is: one JS evaluate returns rects for EVERY actionable element on the page at once (all inputs, textareas, contenteditable fields, buttons, links, each with tag, type, role, accessible name, rect, center, visibility, and whether it is the focused element). One DOM read replaces N locate() calls and replaces the JPEG read entirely. The click list for a whole task comes from this single snapshot, and later clicks run with no further reads except a cheap re-verify.

Source: https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect (MDN, "Element: getBoundingClientRect() method", accessed 2026-11-22, Scrapling plain Fetcher status 200). MDN: getBoundingClientRect() returns a DOMRect "providing information about the size of an element and its position relative to the viewport", width/height plus x/y relative to the viewport, and "the amount of scrolling that has been done of the viewport area ... is taken into account", so rect edges change when scroll changes. Companion source for the transport: repo scripts/zen_dom.py evaluate() (Marionette) and scripts/cdp.mjs Runtime.evaluate (CDP).

Goal-bar mapping: this is the most direct one-vision analogue in DOM form. First-time-right grounding (exact numbers, no eyeballing); zero screenshot reads for locating; one read yields many actions (the whole click list). It is what makes the 2-vision benchmark possible on the DOM side: vision 1 becomes a DOM snapshot instead of a JPEG, and the script phase needs no vision at all.

Applicability to our stack: extend scripts/zen_dom.py with a harvest() method beside locate(): one evaluate() running querySelectorAll over a fixed selector set, returning a JSON list of {selector or index, tag, role, name, x, y, width, height, center_x, center_y, visible, focused}. Same pattern in scripts/cdp.mjs via Runtime.evaluate. Callers then click real-mouse points from the snapshot (keeping the existing rule: DOM locates, real mouse clicks). Needs C12 (coordinate conversion) to turn viewport CSS px into screen px, and needs an iframe rule (see worker3 redteam note: recurse per frame, cross-origin frames unreachable from parent JS).

Measured numbers: none reported by MDN. In-repo failure it addresses: about 90px misread.

Verdict: promising. The single highest-leverage candidate; it is a small extension of code that already exists and works.

### C2. Native CDP DOM domain: DOM.getBoxModel / DOM.getContentQuads / DOM.querySelector / DOM.focus / DOM.scrollIntoViewIfNeeded (Brave)

What it is: CDP's own DOM domain returns element geometry without any injected JS. DOM.querySelector finds a node, DOM.getBoxModel returns its content/padding/border/margin boxes, DOM.getContentQuads returns quads describing node position on the page (multiple quads for inline nodes), DOM.focus focuses an element, DOM.scrollIntoViewIfNeeded scrolls it into view. This is the no-JS-injection path: geometry comes from the browser's own layout data, not from script running in the page.

Source: https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json (Chrome DevTools Protocol browser_protocol.json, version 1.3, accessed 2026-11-22, Scrapling plain Fetcher status 200, 1,425,607 bytes). Verified by direct grep of the raw file: getBoxModel "Returns boxes for the given node", getContentQuads "Returns quads that describe node position on the page. This method might return multiple quads for inline nodes" (experimental), scrollIntoViewIfNeeded "Scrolls the specified rect of the given node into view if not already visible", getDocument "Returns the root DOM node (and optionally the subtree)", querySelector "Executes querySelector on a given node", describeNode "Describes node given its id, does not require domain to be enabled. Does not start tracking any objects, can be used for automation", focus "Focuses the given element", Page.getLayoutMetrics "Returns metrics relating to the layouting of the page, such as viewport bounds/scale".

Goal-bar mapping: first-time-right grounding (layout-engine numbers, immune to page JS interference); zero screenshot reads; native scroll/focus removes the guesswork that caused the click-then-type failure mode (focus first, verify, then type).

Applicability to our stack: add DOM-domain calls to scripts/cdp.mjs (it currently uses only Runtime.evaluate + Input). Flow per target: DOM.getDocument, DOM.querySelector, DOM.scrollIntoViewIfNeeded, DOM.getBoxModel, DOM.focus, then real mouse click at the border-box center (or CDP Input.dispatchMouseEvent, already in cdp.mjs) and Input.insertText. Needs Brave launched with --remote-debugging-port (see C8 for the launch caveat) and C12 for viewport-to-screen conversion. Note DOM.getBoxModel quads are viewport-relative; confirm the exact origin against the live browser during testing, do not assume.

Measured numbers: none reported in the protocol JSON (it is a spec, not a benchmark).

Verdict: promising. Best Brave-side grounding method; strictly better than JS injection where the page may block or alter script.

### C3. CDP Accessibility domain: Accessibility.getFullAXTree / getPartialAXTree / queryAXTree (Brave)

What it is: the browser's accessibility tree as data. getFullAXTree fetches the entire accessibility tree for the root document; getPartialAXTree fetches one node plus a partial tree; queryAXTree queries a DOM node's accessibility subtree for accessible name and role, returning matches. Each AX node carries role, name, and properties including focusable, focused, editable, hidden. This grounds by role + name ("textbox named Message") instead of by pixels or CSS selectors, which survives restyles and DOM reshuffles.

Source: same CDP browser_protocol.json v1.3 as C2 (accessed 2026-11-22). Verified by grep: getFullAXTree "Fetches the entire accessibility tree for the root Document" (experimental), getPartialAXTree "Fetches the accessibility node and partial accessibility tree for this DOM node, if it exists" (experimental), queryAXTree "Query a DOM node's accessibility subtree for accessible name and role... returns those that match the specified name and role". Companion: https://developer.chrome.com/docs/devtools/accessibility/reference (Chrome DevTools, "Accessibility reference", accessed 2026-11-22, status 200), which documents the Accessibility tab as showing "the accessibility tree, ARIA attributes, and computed accessibility properties of DOM nodes" and that "the accessibility tree is a subset of the DOM tree". Note the protocol doc warns that enabling the Accessibility domain "can impact performance until accessibility is disabled", so enable per-task and disable after.

Goal-bar mapping: first-time-right grounding by role + name (the most robust selector for chat inputs and send buttons); zero screenshot reads; one getFullAXTree call yields every target on the page at once, so one observation drives many actions.

Applicability to our stack: add to scripts/cdp.mjs: enable Accessibility, getFullAXTree with a depth limit, filter to editable textboxes + buttons, map each AX node back to its DOM node (backendNodeId) and then to a rect via C2 DOM.getBoxModel. Use for the 2-vision benchmark's vision 1: role/name lookup of both chat inputs and both send buttons in one tree fetch. Watch the performance note: measure the enable/fetch/disable cost live; if getFullAXTree is slow on heavy pages, fall back to getPartialAXTree per subtree.

Measured numbers: none reported; only the performance warning quoted above.

Verdict: promising. Strongest Brave-side method for role-based grounding; pair with C2 for rects.

### C4. W3C WebDriver classic Get Element Rect + Get Computed Role / Label (Zen via Marionette)

What it is: the standard WebDriver endpoint for exact element geometry, no JS needed. Get Element Rect returns the element's x, y, width, height. Get Computed Role and Get Computed Label return the accessibility role and name the browser computed for the element. Together they give rect + role + name from the standard protocol Marionette already speaks.

Source: https://w3c.github.io/webdriver/ (W3C WebDriver standard, accessed 2026-11-22, Scrapling plain Fetcher status 200). Table of contents verified in the fetched text: "12.4.7 Get Element Rect", "12.4.9 Get Computed Role", "12.4.10 Get Computed Label", alongside "12.5.1 Element Click", "12.5.3 Element Send Keys", "13.2.1 Execute Script". (The MDN page for the same command, https://developer.mozilla.org/en-US/docs/Web/WebDriver/Commands/GetElementRect, returned 404 on 2026-11-22, so the W3C spec is the source of record here.)

Goal-bar mapping: first-time-right grounding via a standard endpoint (no page JS, no screenshot); rect + role + label in three cheap calls, or one call when only the rect is needed.

Applicability to our stack: scripts/zen_dom.py already speaks WebDriver over HTTP to geckodriver (its _wd helper). Add a rect() method using GET /session/{id}/element/{elementId}/rect plus element lookup via Find Element, and role()/label() via the computed-role/label endpoints. This is a smaller, more standard alternative to C1's JS harvest for single elements, and a good cross-check: if JS rect and WebDriver rect disagree, the page is doing something odd (transform, zoom, shadow DOM) and the run should stop and report instead of clicking. Caveat from the repo: Marionette click fails on windowed Zen, so keep using real-mouse clicks; only the rect comes from WebDriver. Also the single-session-slot rule still applies (one session at a time, always deleted).

Measured numbers: none reported in the spec.

Verdict: promising. Cheap, standard, and doubles as an independent cross-check for C1.

### C5. Focus-then-verify loop: scrollIntoView + focus + document.activeElement check before typing (Zen side gap)

What it is: after clicking, do not type blind. Scroll the field into view, focus it, then read document.activeElement (or the AT-SPI focused state) and only type when the focused element is the intended field. The earlier failure chain had two separable links: wrong point (fixed by C1-C4) and unverified focus (this candidate). The Codex demo that proved the root cause used exactly this discipline: click the re-read center, see the caret, then type.

Source: MDN getBoundingClientRect page (same as C1) for scroll-aware rects; repo scripts/cdp.mjs lines 234/252 (scrollIntoView before CDP clicks) and line 425 (document.activeElement check before typing) show the Brave side already does this; the Zen side (scripts/zen_dom.py) has verify() but no focus/scroll helper, so this candidate is the Zen-side port of a proven in-repo pattern. CDP DOM.focus and DOM.scrollIntoViewIfNeeded (C2 source) are the Brave-native forms.

Goal-bar mapping: accuracy guard, not a locator. It converts a silent wrong-field type into a loud stop (focus check fails, abort, re-read). It costs one cheap DOM read and protects the 90% accuracy bar.

Applicability to our stack: add focus(selector) + scroll_into_view(selector) to scripts/zen_dom.py using evaluate(): el.scrollIntoView({block:'center'}); el.focus(); return document.activeElement === el. Call it after every real-mouse click on an input and before any wtype text. On the AT-SPI side the equivalent is checking the focused state in a11y.py observe output.

Measured numbers: none; the evidence is the Codex demo outcome (correct center + visible caret, typed at once, Enter sent) recorded in MEMORY.md 2026-11-22 01:46.

Verdict: promising. Tiny to build, directly closes the second link in the failure chain.

### C6. WebDriver BiDi browsingContext.locateNodes (Zen)

What it is: the BiDi-standard way to find nodes by locator without screenshots: browsingContext.locateNodes takes a browsing context plus a locator and returns matching nodes. It is the BiDi counterpart of classic Find Element, usable over the same single remote session Zen exposes.

Source: https://w3c.github.io/webdriver-bidi/ (WebDriver BiDi standard, accessed 2026-11-22, Scrapling plain Fetcher status 200, 4,216,015 bytes). Table of contents verified in the fetched text: "7.3.3.7 The browsingContext.locateNodes Command" alongside getTree, navigate, activate, captureScreenshot. Honest limit: the stripped text I saved contains only one occurrence of "locateNodes" (the contents entry) and zero occurrences of "accessibility" or "innerText" as locator types, so the exact locator types this command accepts were NOT verified from this fetch. That is an open verification item for the implementation phase, not a claim made here.

Goal-bar mapping: first-time-right grounding through a standard locator (no JPEG); one call can return many nodes, so one observation can drive many actions.

Applicability to our stack: only if the repo's BiDi path is viable. Repo evidence cuts against it: docs/zen-dom-control-comparison.md records Puppeteer via BiDi as PARTIAL with click FAILED (handler not fired), and BiDi shares the single session slot with Marionette, so a leaked BiDi session blocks Marionette too. Use locateNodes for locating only (never for clicking), keep real-mouse clicks, and only pursue it if C1/C4 prove insufficient, since Marionette classic already covers the same ground with less risk.

Measured numbers: none reported.

Verdict: maybe. Standard and plausible, but redundant with C1/C4 and carries the repo's proven BiDi risk; try only after the Marionette paths are measured.

### C7. Playwright locator.boundingBox + getByRole + aria snapshots

What it is: Playwright's locator API returns exact geometry from a semantic locator: locator.boundingBox() returns the box of the element matching the locator, or null if the element is not visible, calculated relative to the main frame viewport. The docs example is exactly our use: get the box, click its center with page.mouse. getByRole finds by accessibility role, and aria snapshots give a YAML representation of the page accessibility tree for role/name based grounding.

Source: https://playwright.dev/docs/api/class-locator#locator-bounding-box (Playwright docs, "locator.boundingBox", accessed 2026-11-22, Scrapling plain Fetcher status 200). Verified text: "This method returns the bounding box of the element matching the locator, or null if the element is not visible. The bounding box is calculated relative to the main frame viewport - which is usually the same as the browser window." Example: "const box = await page.getByRole('button').boundingBox(); await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);". Companion: https://playwright.dev/docs/aria-snapshots (Playwright docs, "Aria snapshots", accessed 2026-11-22, status 200): "aria snapshots provide a YAML representation of the accessibility tree of a page". Companion: https://playwright.dev/docs/locators (accessed 2026-11-22, status 200).

Goal-bar mapping: first-time-right grounding (semantic locator to exact box); zero screenshot reads; role-based locators survive restyles.

Applicability to our stack: poor fit as a primary path, good as a reference implementation. Repo evidence: docs/zen-dom-control-comparison.md records Playwright 1.65.1 moz-firefox as BROKEN against Zen, and the session-leak rule applies to any remote client. Playwright's value here is as the design to copy (boundingBox relative to main frame viewport even for child-frame elements; iframe recursion per the worker3 redteam note) rather than as a library to adopt. Only revisit if the Zen remote path changes (e.g. a Playwright version that works against Zen, or Brave-side Playwright over CDP, where Playwright is known-good).

Measured numbers: none reported in the fetched docs.

Verdict: maybe. Excellent API design to copy; not adoptable against Zen today (BROKEN in repo tests).


### C8. Selenium WebElement.get_rect + is_displayed + getAttribute (Zen via geckodriver)

What it is: Selenium's element-information API. getRect() returns height, width, x and y of the element; isDisplayed() checks the element is displayed; getAttribute("value") reads a field's value for verify-after-type. It is the Selenium wrapper around the same W3C endpoints as C4.

Source: https://www.selenium.dev/documentation/webdriver/elements/information/ (Selenium docs, "Information about web elements", accessed 2026-11-22, Scrapling plain Fetcher status 200). Verified text: "GetRect - Returns height, width, x and y coordinates referenced element. Rectangle res = driver.findElement(By.name("range_input")).getRect();" plus isDisplayed and getAttribute("value") examples in the same page.

Goal-bar mapping: first-time-right grounding (standard rect); is_displayed plus value read give a cheap verify loop (C5 pattern in Selenium form).

Applicability to our stack: scripts/zen_dom.py deliberately avoids the Selenium module ("Stdlib only (urllib). No selenium module needed; the laptop has no pip"). Adopting Selenium would add a dependency the repo chose not to carry, for endpoints zen_dom.py already reaches by raw HTTP. Repo test result: Selenium + geckodriver 0.36.0 WORKS headless, PARTIAL windowed (docs/zen-dom-control-comparison.md). Only useful as a fallback if the stdlib WebDriver client in zen_dom.py hits a wall, or as a cross-check harness on a machine with pip.

Measured numbers: none reported (the docs example asserts getX() == 10 on a test page, which is a fixture value, not a benchmark).

Verdict: maybe. Works, but redundant with C4 and adds a dependency the repo explicitly avoided; keep as fallback only.

### C9. Raw AT-SPI via pyatspi: Component.get_extents (screen coords) + Text caret + Action, for native apps and for Firefox/Chromium web content

What it is: the Linux desktop accessibility bus. Every accessible object exposes interfaces: Component (onscreen visual representation, get_extents in screen coordinates), Text (character offsets, caret position, text ranges), Action (named actions such as click, focus), Collection (search by role/name criteria), EditableText. Firefox and Chromium both publish their content to AT-SPI through the ATK bridge, so the same call that grounds a native GTK button can ground a Zen web input: walk the tree, match role + name, read screen extents, click the center with the real mouse.

Source: https://docs.gtk.org/atspi2/ (AT-SPI 2.0 API docs, accessed 2026-11-22, Scrapling plain Fetcher status 200). Verified text: "Component - An interface implemented by objects which have onscreen visual representations", plus Collection ("An interface designed to allow accessibles which satisfy a set of criteria to be returned"), Text, EditableText, Action, Document, Hypertext, Image, Selection, Table. Companion: https://www-archive.mozilla.org/access/unix/atspi-support (Mozilla, "Support for Linux/UNIX Assistive Technology Developers", accessed via browser.search 2026-11-22): "The base of our support ... is AT-SPI", "The AT-SPI tree and the DOM tree are parallel structures, although the AT-SPI tree is a subset of the DOM tree". Companion: https://en.wikipedia.org/wiki/Assistive_Technology_Service_Provider_Interface (accessed via browser.search 2026-11-22): "AT-SPI can also be used for automated testing of user interfaces, with tools such as Linux Desktop Testing Project and Dogtail", and Firefox/Thunderbird for Linux implement ATK "so they communicate out-of-box with AT-SPI". Companion on toolkit coverage: Chromium exposes AT-SPI via its auralinux code (chromium/ui/accessibility/platform, content/browser/accessibility), Firefox via gecko-dev/accessible/atk (per search result 4, james4ever0.github.io summary of at-spi2-core toolkits.md).

Goal-bar mapping: first-time-right grounding in TRUE screen coordinates (no viewport-to-screen conversion needed, which is the whole point of C12); zero screenshot reads; one tree walk yields every target in an app or a page, so one observation drives many actions. It is also the ONLY candidate in this list that covers non-browser apps (native dialogs, file picker, system UI), which DOM methods can never touch.

Applicability to our stack: scripts/a11y.py already implements this with pyatspi (gi.repository Atspi) and _component_extents() exists, but extents collection is gated behind CU_PICK4_FASTPATH=1 (default off) and ground() needs a snapshot path. The missing work: turn the flag on by default for grounding calls, add a bulk harvest (one tree walk returning all editable text fields + buttons with role, name, screen rect, focused state), add a Collection-based search by role/name, and add a caret-offset to screen-xy helper via the Text interface for verifying the caret is inside the field after focus. Risks to verify live: Zen's web content must actually appear in the AT-SPI tree with correct screen extents on Hyprland/Wayland (Firefox historically exposes it; Zen is a fork, verify); AT-SPI tree walks can be slow on huge pages (time-box and depth-limit); the file-picker dialog is a separate app (xdg-desktop-portal / GTK) with its own tree.

Measured numbers: none reported in the fetched sources.

Verdict: promising. The only screen-coordinate-native method and the only non-browser method; the natural complement to C1 (DOM for web detail, AT-SPI for screen truth and native UI).

### C10. Dogtail on top of pyatspi (role/name search, focus/click/type primitives)

What it is: a Python GUI automation framework wrapping pyatspi/AT-SPI. Tree API: root.application(name), app.child("File", "menu").click(), role + name search. Procedural API: focus.application, focus.frame, focus.text(roleName='editbox'), click('7'), type(...). Dogtail 2.x handles Wayland input via the Screen Cast / Remote Desktop API and uses the window list to connect input to the right window.

Source: https://pypi.org/project/dogtail/ (Dogtail on PyPI, accessed via browser.search 2026-11-22): "dogtail is a GUI test tool and UI automation framework written in Python. It uses Accessibility (AT-SPI) technologies to communicate with desktop applications", "works great in combination with behave and qecore ... if you're interested in using it with modern wayland-based GNOME", "Dogtail then ensures the correct window is connected via the Remote Desktop API, allowing input actions to be accurately executed within it", "On the AT-SPI tree and accessibility's introspection side, not much has changed - input has primarily been the challenge on Wayland". Companion: https://dogtail.gitlab.io/qecore/doc_basic_automation.html (Dogtail docs, "Automation of Desktop Applications", accessed via browser.search 2026-11-22): "Automation is done using AT-SPI ... wrapped by pyatspi for use in python ... taken by dogtail which serves as our API". Companion: https://github.com/t0mjones/qa/blob/HEAD/plugins/qa-desktop/skills/at-spi-linux/SKILL.md (at-spi-linux skill, accessed via browser.search 2026-11-22): dogtail procedural example with focus.application / focus.frame / click / focus.text(roleName='editbox') and the Accerciser inspection step. (Direct GitLab fetch of dogtail returned a sign-in wall in stripped text; content above comes from PyPI + docs via search.)

Goal-bar mapping: first-time-right grounding by role + name; zero screenshot reads; one tree search per target, or one root fetch plus many child searches per task.

Applicability to our stack: do NOT adopt dogtail as a dependency; adopt its pattern. scripts/a11y.py already is a thinner dogtail (observe/query/ground/drill/act). What dogtail adds that a11y.py lacks: the role-based search idiom (child by name + role in one call), the focus-then-act sequencing, and the Wayland Remote Desktop input lesson (input is the hard part on Wayland, tree reading is the easy part). That last point supports our existing split: read positions from AT-SPI/DOM, keep input on the real mouse + wtype path we already have. Also note dogtail is GNOME-oriented (toolkit-accessibility gsettings, qecore); on Hyprland/Omarchy the gsettings step may not apply and needs live verification.

Measured numbers: none reported.

Verdict: maybe. Do not adopt the library; copy the role/name search idiom and the focus-then-act sequencing into a11y.py. Revisit adoption only if a11y.py's own search proves too thin.

### C11. LDTP2 (Linux Desktop Testing Project): getobjectproperty, guiexist, waittillguiexist

What it is: the older AT-SPI test framework. A daemon (ldtpd) exposes the accessibility tree over XML-RPC; clients call getobjectproperty(window, object, property), guiexist(), waittillguiexist(), click, settext, verifystate. It uses the accessibility libraries to poke through the application's UI, with Appmap files mapping window/object names.

Source: https://github.com/ldtp/ldtp2/blob/master/doc/ldtp-tutorial.rst (LDTP Tutorial, version 1.1, dated 2014-03-29, accessed via browser.search 2026-11-22): "The Linux Desktop Testing Project (LDTP) is aimed at producing a high quality automated testing framework ... It uses the Accessibility libraries to poke through the application's user interface", "Accessibility libraries provide applications property, state, its child items etc", "LDTP supports verification of actions performed (guiexist(), verifystate, etc)". Companion: https://mail.python.org/archives/list/python-announce-list@python.org/thread/JK2ZS7OTV7BGN7DEEC7BQ76DUEQDRSDN/ (LDTP 2.0.1 release note, accessed via browser.search 2026-11-22): v2 is a complete Python rewrite, new dependency python-pyatspi, "in v1 each action command was given 1 second sleep time internally before execution, but on v2 there is no delay unless its set in environment variable LDTP_COMMAND_DELAY".

Goal-bar mapping: first-time-right grounding in principle (same AT-SPI tree as C9); in practice a daemon plus XML-RPC plus Appmap files is the opposite of minimal total time.

Applicability to our stack: none directly. It would add a daemon, a new dependency set (python-atspi, twisted-web), and a mapping-file layer, to reach the same tree scripts/a11y.py already reads directly. Its one transferable idea is waittillguiexist: poll for an object to exist before acting, which is a useful retry shape for lazy-loaded chat UIs; implement that as a small poll loop in a11y.py, not by adopting LDTP.

Measured numbers: none, except the v1 1-second-per-action sleep (a cost, not a benchmark) removed in v2.

Verdict: skip. Same tree as C9 with a heavier stack and a 2014-era tutorial; take only the wait-for-object polling idea.

### C12. Coordinate conversion layer: CSS viewport px to screen px (Hyprland window geometry + devicePixelRatio + scroll)

What it is: the missing link between every DOM rect and the real mouse. A DOM rect is in CSS pixels relative to the viewport. The mouse needs screen pixels. Conversion needs: the browser window's screen position and size (Hyprland), the devicePixelRatio / scaling, the viewport offset inside the window (chrome height, sidebar width, Zen's vertical tabs and URL bar), and the current scroll offset (already inside getBoundingClientRect, but the window offset is not). Page.getLayoutMetrics (CDP) gives viewport bounds/scale on the Brave side; AT-SPI root extents give the window frame on any side.

Source: https://wiki.hyprland.org/IPC/ (Hyprland Wiki, "IPC", accessed 2026-11-22, Scrapling plain Fetcher status 200). Verified: Hyprland exposes an IPC socket at $XDG_RUNTIME_DIR/hypr/[HIS]/.socket.sock with events including activewindow / activewindowv2 on window focus change. Repo companion: scripts/hypr_cmd.py:109 already parses `hyprctl clients -j`; the repo already reads window lists, the conversion math is what is missing. Companion: MDN getBoundingClientRect page (C1 source) for the viewport-relative definition and scroll behavior. Companion: CDP browser_protocol.json (C2 source) for Page.getLayoutMetrics ("viewport bounds/scale").

Goal-bar mapping: this is the accuracy guard for ALL DOM candidates. A perfect DOM rect clicked at the wrong screen point is still a miss, and a 90px-class error can come from this layer (window offset, Zen sidebar, DPR) just as easily as from a JPEG misread. Without it, C1-C4 cannot reach 90% accuracy in the real click.

Applicability to our stack: build a small pure function, e.g. viewport_to_screen(css_x, css_y) in the driver layer: take hyprctl clients entry for the Zen/Brave window (at + size), add the measured viewport origin inside the window (calibrate once per window layout: URL bar height, sidebar width), multiply by devicePixelRatio from a DOM read (window.devicePixelRatio) or Page.getLayoutMetrics. Cross-check the conversion against AT-SPI: the AT-SPI screen extents of the same element (C9) must agree with the converted DOM rect within a few px, or the run stops and reports. That cross-check is the cheapest accuracy proof available before any live benchmark.

Measured numbers: none reported; the calibration constants (URL bar height, sidebar width, DPR) are machine-specific and must be measured live on the laptop, not taken from docs.

Verdict: promising. Not optional: every DOM candidate depends on it. Build it first, with the AT-SPI cross-check, before trusting any DOM click point.

### C13. Accerciser + AT-SPI inspection tooling (dev-time tree inspection, not a runtime method)

What it is: Accerciser is the interactive accessibility explorer: it connects to the AT-SPI bus as a client like a screen reader and shows the live accessibility tree of every running application, with each object's role, name, description, states, relations, and supported interfaces. It is the tool for learning the exact role + name triples that C9/C10 queries use, and for confirming Zen's web content is actually in the AT-SPI tree.

Source: https://wiki.gnome.org/Apps/Accerciser (GNOME Wiki, "Accerciser", accessed 2026-11-22, Scrapling plain Fetcher status 200; stripped text thin, title + topic confirmed). Companion: https://vectree.io/pdf/c/assistive-technology-service-provider-interface (Vectree AT-SPI overview, accessed via browser.search 2026-11-22): "Accerciser is the developer's X-ray machine for the Assistive Technology Service Provider Interface ... It shows the live accessibility tree of every running application. With Accerciser you can browse each accessible object's role, name, description, states, relations, and supported interfaces."

Goal-bar mapping: indirect. It does not ground at runtime, but it removes guesswork from writing the role/name queries that do, which protects first-time-right accuracy during development.

Applicability to our stack: use on the laptop during development to inspect Zen's AT-SPI tree (confirm web inputs appear, read their exact roles/names/extents), then hard-code nothing from it: runtime code queries the tree live. No code change.

Measured numbers: none.

Verdict: maybe. Useful dev tool, not a runtime candidate; use it to de-risk C9 before building on it.

## Ranked list (most promising first)

1. C1 - One-shot bulk DOM rect harvest (Zen Marionette + Brave CDP). One read, whole click list, zero JPEG. Smallest build on working code.
2. C12 - Coordinate conversion layer (CSS px to screen px) + AT-SPI cross-check. Required by every DOM candidate; build first.
3. C9 - Raw AT-SPI via pyatspi (screen coords, native apps too). Only screen-truth method; complements C1.
4. C2 - Native CDP DOM domain (getBoxModel / getContentQuads / focus / scrollIntoViewIfNeeded). Best Brave-side grounding, no JS injection.
5. C3 - CDP Accessibility tree (getFullAXTree / queryAXTree). Best Brave-side role + name grounding; pair with C2.
6. C5 - Focus-then-verify loop (Zen side). Tiny port of a proven in-repo pattern; closes the second failure link.
7. C4 - W3C Get Element Rect + Computed Role/Label. Standard, cheap, and a cross-check for C1.
8. C7 - Playwright boundingBox design (copy the API shape, do not adopt the library; BROKEN against Zen today).
9. C13 - Accerciser (dev-time inspection to de-risk C9).
10. C10 - Dogtail idiom (copy role/name search + focus-then-act; do not adopt the library).
11. C6 - BiDi locateNodes (standard but redundant with C1/C4 and carries repo-proven BiDi risk).
12. C8 - Selenium get_rect (works, but redundant with C4 and adds a dependency the repo avoided).
13. C11 - LDTP2 (skip; same tree as C9 with a heavier stack; take only the wait-for-object polling idea).

Suggested build order for council/redteam: C12 first (with the AT-SPI cross-check), then C1 + C5 on the Zen side and C2 + C3 on the Brave side, with C9 bulk harvest as the parallel screen-truth path. The 2-vision benchmark then proves the combination; no benchmark run is part of this crawl.

## Open verification items (for council + redteam, not decided here)

1. BiDi locateNodes locator types (css? xpath? innerText? accessibility?) were not verifiable from the stripped spec fetch. Verify from the full BiDi spec before any C6 work.
2. DOM.getBoxModel quad origin (viewport vs document) must be confirmed against the live Brave build during testing; do not assume.
3. Zen web content in the AT-SPI tree: confirm live that Zen (Firefox fork) publishes page inputs with correct screen extents on Hyprland/Wayland, and measure tree-walk cost on a heavy page.
4. Brave --remote-debugging-port launch caveat: per the CDP skill docs found via search, Chrome/Brave refuse the flag on the default user data directory and need a custom profile, and the debug port cannot be enabled on an already-running browser (relaunch required). That conflicts with driving the user's already-logged-in Brave; verify the Linux behavior live before building on C2/C3.
5. Playwright moz-firefox BROKEN and Puppeteer BiDi click FAILED are repo-recorded; any revisit needs a live re-test, not a docs claim.
6. Cross-origin iframes: DOM rects cannot reach them from parent JS (same-origin policy); BiDi browsing-context-scoped calls or vision remain the fallback (per worker3 redteam note). The Messenger web app used in the benchmark must be checked for cross-origin frames before the benchmark runs.
7. AT-SPI performance: getFullAXTree and full AT-SPI tree walks can be slow on heavy pages; both need a live time measurement and a depth limit.

## Method note on the last30days-skill standing instruction

During this run MEMORY.md gained a standing instruction (2026-11-22 02:09) to use https://github.com/mvanhorn/last30days-skill for crawling real data from the last 30 days only. This crawl already satisfies the substance of that rule: every source above was fetched live on 2026-11-22 via Scrapling plain Fetcher or browser.search, with status codes recorded, and no stale cached data was used. The skill itself was not installed in this run because this task's brief specified the Scrapling + browser.search method, and the topic here is stable protocol specs (CDP, W3C WebDriver, BiDi, AT-SPI), not fast-moving trend data. If the parent wants a last30days pass over Reddit/X/YouTube/HN/GitHub for newer grounding tricks, that is a separate follow-up crawl, not a redo of this one.

## Files and evidence

- This log: improvements/worker-click-crawl-doma11y-log.md (this file).
- Raw fetch dumps (VM scratch, not committed): /tmp/crawl-doma11y/*.txt (24 source texts), /tmp/crawl-doma11y/cdp-protocol-raw.json (1,425,607 bytes), /tmp/crawl-doma11y/fetch1.py, fetch2.py, fetch3.py, fetch3b.py.
- No implementation, no live tests, no browser tasks in this run.

## End

End: 2026-11-22 02:11 +07 (t+6m). Total wall time about 6 minutes. 13 candidates, 24 Scrapling fetches (22 with usable content, 2 recovered via search), 4 browser.search calls, 0 StealthyFetcher uses, 0 live drives, 0 implementations. Next step belongs to council + redteam review, then live testing of the ranked candidates, then the 2-vision benchmark.
