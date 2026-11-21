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

## Appendix A - last30days follow-up (owner order 02:09, run 2026-11-22 02:12-02:24 +07)

Owner order: the whole team uses last30days-skill (https://github.com/mvanhorn/last30days-skill) to crawl REAL data for the improvement research. Install with `npx skills add mvanhorn/last30days-skill -g`. HARD RULE: do NOT use old stale datasets. Only fresh real data from the last 30 days. Every crawled claim must carry its source and date. This appendix records the install, the engine run, the fresh findings, the new candidate they add, and the recency audit for every source in this log.

### A1. Install record (02:12-02:19 +07, t+7-14m)

- 02:12:29 +07: ran `npx skills add mvanhorn/last30days-skill -g`. The command produced zero output for over 5 minutes and was backgrounded by the runtime (session proc_c78dabc2e9ea).
- 02:18 +07: process inspection showed THREE concurrent `npx skills add mvanhorn/last30days-skill -g` processes (started 19:10, 19:12, 19:13 UTC), one with `-y`. These are almost certainly sibling workers installing the same skill at the same time; the npx cache path was shared (~/.npm/_npx/ac0ed6aa23b37c1e). I did not touch the other two.
- 02:19 +07: killed my own npx session only (process.kill, SIGTERM, exitSignal 15; my 19:12 process gone after, the 19:10 wrapper still listed). The npx install itself never confirmed complete in this run; record it as NOT VERIFIED, not as done.
- Working path used instead: the skill repo was already present as a git clone at ~/workspace/last30days-skill (v4.4.0, commit bb2f1ed2, "chore(release): bump version to 4.4.0 (#1539)"), with skills/last30days/SKILL.md and scripts/last30days.py in place, and ~/.config/last30days/.env already contained SETUP_COMPLETE=true. I bound SKILL_DIR to ~/workspace/last30days-skill/skills/last30days and ran the engine from the clone. The SKILL.md fetched live from main during this run is v4.5.0, so the clone is one minor version behind main; no behavior difference was observed for this run.
- Preflight: /usr/bin/python3 is 3.12.3, satisfying the 3.12+ gate. Diagnose (`--diagnose --include-research-backend`, 02:19 +07) reported available sources: reddit, hackernews, polymarket, github, grounding; local_mode true; gh available; has_scrapecreators false; bird (X) not authenticated; yt-dlp missing; no API keys present except GitHub via gh auth.
- Doctor (`doctor --cached --json`, 02:19 +07) ran a live probe instead of serving cache (from_cache false, mode probe, generated 2026-11-21T19:18:36Z). Per-source probe statuses were not fully extracted in this run; the engine run below reports the per-source outcomes that matter.

### A2. Engine run (02:20 +07, t+15m, 39.8s, exit 0)

Command: LAST30DAYS_NATIVE_SEARCH=1 python3 scripts/last30days.py "DOM accessibility tree grounding for browser and desktop agents" --emit=compact --save-dir=/tmp/crawl-doma11y/last30days --save-suffix=v3 --plan - (plan JSON via quoted heredoc, 4 subqueries: primary browser-agent a11y grounding; Playwright ariaSnapshot bounding box; AT-SPI pyatspi desktop grounding; BiDi locateNodes accessibility locator). Intent how_to; I set freshness_mode strict_recent in the plan to honor the owner 30-day rule, and the engine normalized it to evergreen_ok in its planner line ([Planner] Plan: intent=how_to, freshness=evergreen_ok, cluster_mode=workflow). That override is recorded, not hidden: the date window still enforced was Oct 22 to Nov 21, 2026, and every item below carries its date.

Engine output: badge "last30days - DOM accessibility tree grounding for browser and desktop... - Oct 22 to Nov 21, 2026 - v4.4.0". Sources: 1 active (Hacker News). Total evidence: 23 items across 1 source. Freshness warning: only 6 of 23 dated items are from the last 7 days. Warning: top evidence highly concentrated in one source. Follow-up cache ID: 3c4d04a4f2404acfa3ea6907c008d833. Raw output saved to /tmp/crawl-doma11y/last30days/dom-accessibility-tree-grounding-for-browser-and-desktop-agents-raw-v3.md.

Partial coverage (engine's own words): "Reddit unreachable: no path served; search skipped-cached; brave down; ddg throttled; startpage throttled (run doctor for fixes)." GitHub: 0 items (all found results dropped as not about the topic). X/Twitter not enabled; YouTube missing (yt-dlp not installed). A failed source is not evidence of no discussion. The Reddit and YouTube gaps mean this sweep is HN-led; the browser.search supplements in A3 partly cover the gap (they found the Playwright, BiDi, Tarsier, and browser-use material the engine missed).

### A3. Fresh findings (all dated, all within the 30-day window Oct 23 to Nov 22, 2026 unless marked otherwise)

F1. Playwright 1.60 ariaSnapshot with boxes (fresh, docs last crawled 1 day before 2026-11-22). Source: https://playwright.dev/docs/api/class-locator (Playwright docs, "Locator", accessed via browser.search 2026-11-22). locator.ariaSnapshot({ boxes: true }) "appends each element's bounding box as [box=x,y,width,height] to the snapshot. Coordinates are relative to the viewport, in CSS pixels, as returned by Element.getBoundingClientRect()." Added in v1.60. ariaSnapshotJSON added in v1.63, same box option. page.ariaSnapshot() gives the full-page version. This is the ideal single-call representation for our goal: role + name + state + rect in one snapshot, no separate rect call per element. It upgrades C7 from "design to copy" to "exact API shape to copy" and gives C1 a concrete output format to mimic in our own harvest.

F2. Mantis, numbered-text grounding with measured wins over the full accessibility tree (fresh: Show HN 2026-11-06, 4pts; README fetched 2026-11-22). Sources: https://github.com/perzianhq/mantis (Mantis repo, README, accessed 2026-11-22) and the engine cluster 5. "Lets AI agents browse the web as short, numbered text instead of screenshots." Mechanism: "Agent sends open/click to Mantis; Mantis reads the page in Chromium, numbers each control and returns only what changed." Measured results (vendor-run benchmark, medians, disclosed in README): long tasks, Luna model, Mantis 35/42 correct vs a11y tree 34/42, input tokens 244k vs 345k, tool calls 17 vs 24, time 42s vs 66s; Haiku 40/42 both, tokens 268k vs 506k, calls 19 vs 30, time 54s vs 85s. Versus the tree: "accuracy within one run, 29-47% fewer input tokens, 29-37% fewer calls, about a third less time." Versus screenshots: Luna screenshots score 2 runs higher but use more tokens and time. Caveats disclosed in the README: short-task times compare a newer Mantis build with the earlier tree/screenshot run; screenshot baseline is the project's own tool; a few tasks swapped after results; two long iframe/tab tasks left out of long-task counts. Becomes candidate C14 below.

F3. Browser-use 1.0 ultrafast mode + Playwright MCP + Stagehand v4 (fresh: 2026-11-11 to 2026-11-20). Source: https://changegamer.ai/articles/agentic-browsing-in-production (published 2026-11-11, updated 2026-11-20, accessed via browser.search 2026-11-22): "As of 13 November 2026 Playwright MCP works from accessibility snapshots with no vision model, browser-use 1.0 has the model write Python against raw CDP (its ultrafast mode acts on accessibility-tree ids), and Stagehand v4 exposes act, observe and extract primitives." Companion, context only (72 days old, outside window): https://thegeocommunity.com/blogs/generative-engine-optimization/browser-use-pi-agent-browser-architecture/ (Browser Use Pi): the model "might locate a button in an accessibility snapshot, scroll its node into view, retrieve its box model, calculate coordinates, dispatch CDP mouse input, and inspect the result", and page.snapshot() "calls Chrome's Accessibility.getFullAXTree". This is independent confirmation that the C2 + C3 combination (AX tree for identity, box model for geometry, CDP input for action) is the pattern real agent browsers use now.

F4. BiDi locateNodes locator types RESOLVED (closes open item 1 from the main log). Sources: https://www.irurueta.com/web/e2e-testing/selenium/webdriver-bidi.html (Selenium WebDriver BiDi guide, written against Selenium 4.51.0 released 9 Oct 2026, checked 25 Oct 2026, accessed via browser.search 2026-11-22): "browsingContext.locateNodes - Find nodes by CSS, XPath, inner text or accessibility locator without a classic element reference", and "Chrome and Firefox are the browsers with a complete BiDi implementation." Companion: https://mdn.hxlab.ir/en-US/docs/Web/WebDriver/Reference/BiDi/Modules/browsingContext/locateNodes (MDN mirror, crawled 6 days before 2026-11-22): locateNodes takes a locator with "one of five criteria" and "turns a locator, such as a CSS selector or XPath expression, into node references (with sharedId and optionally handle)". Companion, context only (Firefox 146 newsletter page last updated 347 days ago, outside window): https://fxdx.dev/firefox-webdriver-newsletter-146/ - Firefox 146 "added support for the context locator to the browsingContext.locateNodes command, which allows to retrieve the container of non-top-level browsing contexts, such as iframe elements." Companion, context only (June 2026 review, outside window): https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/01-webdriver-bidi-standards.md - "WebDriver BiDi is now the only cross-engine bidirectional automation protocol with real momentum", Firefox CDP "completely removed in Firefox 141 (released 22 July 2025)", "--remote-debugging-port now serves only a WebDriver BiDi WebSocket", and the CDP to BiDi gap still missing "accessibility tree, coverage/profiling, screencast" as of June 2026. Consequence for us: C6's locator question is answered (accessibility locator exists), but BiDi has no a11y-tree module, so C6 cannot replace C3; and the Firefox CDP removal confirms Zen must be driven via Marionette/BiDi, never CDP.

F5. AT-SPI-first grounding, fresh corroboration (fresh part: Tarsier listing updated Nov 2, 2026, within window). Sources: https://pypi.org/project/tarsier-ai/ (Tarsier-AI on PyPI, accessed via browser.search 2026-11-22): Linux via "Assistive Technology Service Provider Interface (AT-SPI) via pyatspi", "extracts the exact semantic structure", serializes to "highly token-efficient YAML ARIA-Snapshot", vendor claims "69.6% Token Reduction" and "100% Deterministic: No hallucinated XY coordinates or missed clicks". Vendor claims, not independent benchmarks; treat the numbers as the vendor's, not as proven. Companion: https://bestmcp.it/app-automation/tarsier/ (last updated November 2, 2026): Tarsier MCP server, 21 tools, "reads native accessibility trees instead of screenshots". Companion, context only (Aug 22, 2026, 91 days old, outside window): https://www.jocheojeda.com/2026/08/22/at-spi-first-grounding/ ("Stop Guessing Pixels: AT-SPI-First Grounding for Desktop Agents"): walk the tree, filter to actionable + visible (states showing, enabled, sensitive), build a labeled list of name + role + exact bbox via Component get_extents() in real pixels, "click the exact center of that widget's box", "verify by re-reading states". That flow is the same shape as C9 + C5 and is now corroborated by two independent authors plus a shipping tool. Companion, context only (41 days old, outside window): https://tessl.io/registry/testland/at-spi-linux/1.2.11 - for Chromium/Electron, set "--force-renderer-accessibility" on launch, or "--enable-blink-features=AccessibilityAriaVirtualContent" for newer surfaces; for Qt, QT_ACCESSIBILITY=1. The Chromium flag is a concrete Brave launch flag to test for C3/C9.

F6. Accessibility-tree grounding is now the consensus direction, with a Nov 2026 explainer (fresh). Source: https://kindatechnical.com/advanced-llm-topics/lesson-55-browser-automation-and-computer-use-agents.html ("Computer Use and Browser Agents", updated Nov 2026, last updated 5 days before 2026-11-22): "the accessibility tree reduces the page to roles (button, link, textbox, checkbox, heading), accessible names and states... Actions then target elements semantically rather than by coordinates. This is usually far cheaper in tokens than a screenshot, robust to layout and styling changes, and lets the harness verify that a target exists and is unique before acting." Grounding failures named: coordinate drift, scaling mismatches (model sees downscaled screenshot, harness applies native coordinates), stale state. Its recommended pattern: Playwright ARIA snapshot, get_by_role with exact name. This independently describes our C1 + C5 shape and names the scaling-mismatch failure that C12 exists to prevent.

F7. Engine clusters with no grounding mechanism (recorded, not used as candidates). Agweb: https://github.com/paul-nameless/agweb (Show HN 2026-11-14, 109pts, 37cmt; README fetched 2026-11-22): "A browser for coding agents on macOS, built on WebKit... agents drive it from the shell with agweb... one window that never takes focus", idle tabs suspended, five idle pages 590 MB vs Playwright Chrome 1.6 GB. macOS-only, WebKit, no rect/grounding method shown; becomes candidate C15 with a skip verdict. Other clusters off-topic for this crawl: Emacs Is My Browser (2026-11-15, 241pts), Cloudflare Turnstile solver (2026-10-28, 317pts), StarSling CI (2026-11-17, 89pts), AgentMall groceries (2026-11-19, 21pts), easi.run secure sessions (2026-11-09, 4pts). GoogleChrome/modern-web-guidance (2026-11-10, 449pts, 146cmt) is about agent-facing web guidance, not grounding; noted, not a candidate.

### A4. New candidates from the 30-day sweep

#### C14. Numbered compact text + diff-only updates (Mantis pattern)

What it is: render the page (or app) as short numbered text lines, one per control (role + name + ref number), and let the agent act by number. After each action, return ONLY what changed, not a fresh full snapshot. Numbers replace coordinates in the agent's view; the harness maps number to exact rect at action time. This is the representation optimization on top of C1/C3: the snapshot the model reads is smaller and the re-read after each action is a diff.

Source: https://github.com/perzianhq/mantis (Mantis README, accessed 2026-11-22; Show HN 2026-11-06 via last30days engine run 2026-11-22, window Oct 22 to Nov 21, 2026). Numbers in F2 above; all vendor-run with disclosed caveats.

Goal-bar mapping: total time and token cost, directly. Same accuracy as the full a11y tree (within one run on long tasks), 29-47% fewer input tokens, 29-37% fewer calls, about a third less time. One snapshot still drives many actions, and the diff-only update keeps re-verification cheap instead of re-reading the whole tree.

Applicability to our stack: apply to the C1 harvest output format and to the C9 AT-SPI harvest: assign stable ref numbers to each harvested element, emit one compact line per element (ref, role, name, center), and after each real-mouse click re-harvest and emit only added/removed/changed lines plus a focused-state line (C5). No new transport needed; it is a formatting + diffing layer over harvests we already plan to build. Watch the caveat: Mantis numbers come from its own benchmark on public sites with two models; our Messenger web app and Zen must be measured live, not assumed equal.

Measured numbers: yes, vendor-run, see F2 (long tasks Luna 35/42 vs tree 34/42, tokens 244k vs 345k, calls 17 vs 24, time 42s vs 66s; Haiku 40/42 both, tokens 268k vs 506k, time 54s vs 85s). Treat as vendor evidence, not independent proof.

Verdict: promising. Rank 3 in the updated list below, right after C1 and C12.

#### C15. Agweb agent browser (macOS WebKit, never takes focus)

What it is: a macOS-only browser built on WebKit for coding agents; one window that never takes focus, agents drive it from the shell, idle tabs suspended.

Source: https://github.com/paul-nameless/agweb (README fetched 2026-11-22; Show HN 2026-11-14, 109pts, 37cmt, via last30days engine run 2026-11-22).

Goal-bar mapping: none for our stack. It solves focus theft and idle CPU, not grounding; no rect or a11y method is shown.

Applicability to our stack: none. macOS-only, WebKit (our browsers are Zen/Brave on Linux), and our live-driving lane already handles focus by rule. The "never takes focus" idea is a design note for any future agent-browser work, not a candidate now.

Measured numbers: memory only (five idle pages 590 MB vs Playwright Chrome 1.6 GB); no grounding numbers.

Verdict: skip. Wrong platform, no grounding method.

### A5. Recency audit (every source in this log)

Window: last 30 days = Oct 23 to Nov 22, 2026. "Fresh" means dated inside the window or a living doc fetched live on 2026-11-22 with current content. "Mechanism only" means the source is cited for how a protocol or API works, not for a recent event; protocol definitions do not go stale in 30 days, but they must still be verified against the installed browser at test time.

Fresh, inside the window:
- last30days engine run 2026-11-22 (window Oct 22 to Nov 21, 2026), HN clusters F7 + Mantis + Agweb.
- Mantis README, fetched 2026-11-22; Show HN 2026-11-06.
- Agweb README, fetched 2026-11-22; Show HN 2026-11-14.
- Playwright docs ariaSnapshot boxes (v1.60), docs crawled 1 day before 2026-11-22.
- kindatechnical.com grounding lesson, updated Nov 2026 (5 days before 2026-11-22).
- changegamer.ai agentic browsing guide, published 2026-11-11, updated 2026-11-20.
- Selenium BiDi guide, checked 25 Oct 2026 (Selenium 4.51.0 released 9 Oct 2026).
- MDN locateNodes mirror, crawled 6 days before 2026-11-22.
- Tarsier bestmcp.it listing, updated Nov 2, 2026; PyPI tarsier-ai, crawled 1-2 days before 2026-11-22.
- GoogleChrome/modern-web-guidance HN 2026-11-10 (449pts).
- All other HN clusters in F7, dated 2026-10-28 to 2026-11-19.

Older than 30 days, still cited, mechanism or context only:
- CDP browser_protocol.json v1.3 (undated living spec): mechanism only, verified by direct grep.
- MDN getBoundingClientRect (undated reference): mechanism only.
- W3C WebDriver spec and W3C BiDi spec (living standards): mechanism only.
- Playwright boundingBox + locators docs (living docs): mechanism only; fresh F1 supplements them.
- Selenium elements/information docs (versioned v4.0 page): mechanism only.
- AT-SPI docs.gtk.org, pyatspi2 GitLab, Dogtail docs/PyPI, LDTP tutorial 2014-03-29: mechanism only (LDTP already verdict skip).
- Hyprland IPC wiki, Chrome DevTools a11y reference, Firefox Marionette docs, Firefox remote docs (living docs): mechanism only.
- Praman 1.3 release notes, May 2026 (179 days): context only, shows Playwright 1.60 ARIA grounding adoption.
- browxai BiDi standards review, June 2026: context only, BiDi momentum + missing a11y tree module.
- Firefox 146 newsletter page, last updated 347 days ago: context only, locateNodes context locator.
- jocheojeda AT-SPI-first post, Aug 22, 2026 (91 days): context only, corroborates C9 + C5 shape.
- tessl at-spi-linux 1.2.11, 41 days: context only, Chromium --force-renderer-accessibility flag.
- searchenginejournal.com (223 days), dev.to (220 days), theagentecosystem.com (90 days), thegeocommunity.com Browser Use Pi (72 days): context only, consensus direction + rtrvr.ai numbers as article-reported, not verified.
- Repo-internal sources (zen_dom.py, a11y.py, cdp.mjs, hypr_cmd.py, docs/zen-dom-control-comparison.md, worker3 redteam note): current in-repo facts as of Nov 2026, not external claims.

Not usable as sources (recorded, not cited for claims):
- MDN GetElementRect page: 404 on 2026-11-22 (W3C spec used instead).
- Brave support page and GNOME AT-SPI wiki: 403 on 2026-11-22 (content recovered from other sources).
- GitLab dogtail page: sign-in wall in stripped text (content recovered via PyPI + docs search).
- Hyprland hyprctl wiki page: 404 on 2026-11-22 (IPC wiki page used instead).
- Reddit (engine): unreachable, 0 items. X/Twitter: not enabled. YouTube: missing (yt-dlp not installed). GitHub (engine): 0 items after relevance filtering.

### A6. Updated ranked list (15 candidates)

1. C1 - One-shot bulk DOM rect harvest. Unchanged at the top.
2. C12 - Coordinate conversion layer + AT-SPI cross-check. Unchanged; required by every DOM candidate.
3. C14 - Numbered compact text + diff-only updates (Mantis pattern). NEW, from the 30-day sweep. Representation layer over C1/C9.
4. C9 - Raw AT-SPI via pyatspi. Unchanged; fresh F5 corroboration strengthens it.
5. C2 - Native CDP DOM domain. Unchanged; fresh F3 confirms the pattern is what agent browsers use now.
6. C3 - CDP Accessibility tree. Unchanged; F1 gives it a concrete output format to mimic (aria snapshot with boxes).
7. C5 - Focus-then-verify loop (Zen side). Unchanged.
8. C4 - W3C Get Element Rect + Computed Role/Label. Unchanged.
9. C7 - Playwright boundingBox design (copy the API shape). Strengthened by F1: ariaSnapshot({ boxes: true }) is the exact single-call shape to copy.
10. C13 - Accerciser (dev-time inspection). Unchanged.
11. C10 - Dogtail idiom (copy, do not adopt). Unchanged.
12. C6 - BiDi locateNodes. Locator types now RESOLVED (accessibility locator exists, F4); verdict stays maybe because BiDi has no a11y-tree module and Marionette paths cover the same ground with less risk. Open item 1 from the main log is CLOSED.
13. C8 - Selenium get_rect (fallback only). Unchanged.
14. C11 - LDTP2 (skip; take only wait-for-object polling). Unchanged.
15. C15 - Agweb agent browser (skip; macOS-only, no grounding method). NEW, considered and skipped.

Suggested build order is unchanged: C12 first (with the AT-SPI cross-check), then C1 + C5 on the Zen side and C2 + C3 on the Brave side, with C9 bulk harvest as the parallel screen-truth path, and C14 as the output-format layer over the harvests. The 2-vision benchmark then proves the combination.

### A7. Appendix files and evidence

- Engine raw output: /tmp/crawl-doma11y/last30days/dom-accessibility-tree-grounding-for-browser-and-desktop-agents-raw-v3.md (31,555 bytes, saved by the engine).
- Engine follow-up cache ID: 3c4d04a4f2404acfa3ea6907c008d833.
- Skill spec + references fetched live: /tmp/crawl-doma11y/last30days-SKILL.md (v4.5.0), /tmp/crawl-doma11y/references_research-runbook.md, /tmp/crawl-doma11y/references_runtime.md, /tmp/crawl-doma11y/references_synthesis.md.
- Fresh source texts: /tmp/crawl-doma11y/mantis-readme.txt, /tmp/crawl-doma11y/agweb-master.txt.
- Skill install: npx path NOT VERIFIED (stalled, see A1); engine run from the git clone at ~/workspace/last30days-skill (v4.4.0, commit bb2f1ed2).
- No implementation, no live tests, no browser tasks in this follow-up either.

## Appendix end

Appendix written: 2026-11-22 02:24 +07 (t+19m from the original 02:05:29 start). Total for both runs: first crawl about 6 minutes, follow-up about 12 minutes. 15 candidates total, 24 Scrapling fetches in run 1 plus 6 more in run 2, 1 last30days engine run (39.8s, exit 0, HN-led with Reddit/GitHub/X/YouTube gaps honestly reported), 9 browser.search calls total. Next step belongs to council + redteam review, then live testing of the ranked candidates, then the 2-vision benchmark.
