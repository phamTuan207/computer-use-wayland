# Council review, Voice 1 (realism): Zen ordinary-user tests

- File reviewed: `improvements/zen-ordinary-user-tests-20261121.md` (447 lines, branch todolist-push)
- Reviewer: Council Voice 1, realism
- Date: 2026-11-21, 22:30 Asia/Ho_Chi_Minh
- Verdict: **AMEND**
- Note: I did not modify the scenario file. ZT-06 must not run as written (see R1). The other scenarios may run only after their listed fixes.

## What is genuinely realistic

- ZT-01 (Wikipedia search and read), ZT-02 (Ctrl+F in a long article), ZT-10 (sidebar tab switching and collapse) are things an ordinary user actually does. ZT-10 is the strongest scenario in the file: it re-tests the owner-reported F-001 sidebar failure directly.
- ZT-05 (workspace switch and back) is real user behaviour on this Hyprland machine and a fair re-test of owner-reported F-002, even though it tests the window manager, not the browser.
- Wikipedia (`en.wikipedia.org`, Ho Chi Minh City article) is a good choice: public, stable, login-free, and a real reading task. The file's Purpose claim holds for Wikipedia and example.com only.

## Site check (live, from this VM, 2026-11-21 about 22:30 +07)

| Site | Result | Realism verdict |
|---|---|---|
| example.com | 200 | Stable and login-free, but no ordinary user navigates here repeatedly. It is a placeholder, not a destination. Used in ZT-00, ZT-01, ZT-03, ZT-04, ZT-05, ZT-08, ZT-09, ZT-10. |
| en.wikipedia.org | 200 | Real, stable, login-free. Keep. |
| httpbin.org/forms/post | 200 at check time | Public and login-free, but it is a developer test service, not a site any ordinary user visits. Fragile: one volunteer-run service underpins ZT-07, ZT-08 and ZT-09, so one outage fails three scenarios for a non-Zen reason. |
| w3.org dummy PDF | **404** (GET and HEAD, checked twice) | Dead. The URL in ZT-06 is a W3C test-suite resource, not a document a user would download, and it no longer resolves. ZT-06 cannot pass as written. |

## Per-scenario verdicts

- ZT-01: AMEND (steps 1 and 6)
- ZT-02: AMEND, minor (step 5)
- ZT-03: AMEND (step 3 fallback)
- ZT-04: AMEND (bookmark target and lookup method)
- ZT-05: GO, with the relabel in R9
- ZT-06: BLOCKED as written, do not run (dead URL, R1)
- ZT-07: AMEND, major (wrong site, R2)
- ZT-08: AMEND (arbitrary chain plus httpbin leg)
- ZT-09: AMEND (mechanical counting plus httpbin leg)
- ZT-10: GO

## Required changes

R1. ZT-06, L261-L265 and L271-L272. Replace the dead PDF URL. `https://www.w3.org/WAI/ER/tests/xhtml/testsuite/resources/pdf/dummy.pdf` returned 404 on 2026-11-21. Do not run ZT-06 until the replacement URL is in the file, verified HTTP 200 with Content-Type application/pdf before the run, and steps 2, 5 and 7 updated to the replacement filename. Pick a PDF a real user would actually download (a manual, a timetable, a public report), not another test-suite dummy file.

R2. ZT-07, L295, L297-L299, L300-L311. Replace httpbin.org/forms/post with a real login-free form an ordinary user actually fills, or drop the submit-and-echo assertion. No ordinary user has ever opened httpbin to type `custname` / `custtel` / `size` / `comments`. The values `Test User` and `0123456789` (L300-L304, L310) are test data, not user input. If no suitable real form is found, reframe ZT-07 as fill-only on a real page and say so in the goal, rather than keeping a developer echo service as the user goal.

R3. ZT-07 knock-on, ZT-08 L331 and ZT-09 L365-L366. Remove the httpbin leg from ZT-08 and ZT-09 as part of R2. Replace it with a second Wikipedia article so a httpbin outage cannot fail three scenarios at once.

R4. ZT-01, L115-L117. Name the link. "Click the first link inside the article lead section" has no user goal: the first link changes when the article is edited, and no user clicks a link because it is first. State the exact link text (for example a named link in the Ho Chi Minh City lead) and its expected destination title and URL.

R5. ZT-03, L166-L168. Remove the conditional fallback. "Middle-click, or right-click and choose Open Link in New Tab, on the Wikipedia wordmark link if present; if no such link exists, press Ctrl+T and type example.com" is harness branching, not user behaviour. Give one deterministic action: Ctrl+click (or middle-click) one named link, with its exact text and expected new-tab title.

R6. ZT-01, L103-L104. Pick one input method. No user presses Ctrl+L and then clicks the address bar. Use Ctrl+L then type, or click the bar then type, not both.

R7. ZT-04, L194 and L202-L204. Bookmark a page worth bookmarking. Nobody bookmarks example.com. Bookmark the Ho Chi Minh City Wikipedia article instead and update the expected title, URL, star state and library steps to match.

R8. ZT-04, L202-L203 and L207-L209. Do not verify a bookmark through Ctrl+Shift+O (the bookmark library). An ordinary user checks the filled star or the bookmarks sidebar/menu. Keep the library check only as a separate verification note, not as a user step.

R9. ZT-02, L141-L144 (step 5). Delete the mouse click on the highlighted find match. A user who finds a word with Ctrl+F reads it where it is highlighted; they do not click the match. Pass is: match count shown, match highlighted and scrolled into view.

R10. ZT-06, L268 and L274. Remove the OR-branches. "Click the download button (or press Ctrl+S)" and "click the downloaded file in the download panel, or open it from ~/Downloads in a new tab" are two different tests in one step. Choose one path and write it as the only path.

R11. ZT-07, L312-L314 (step 8). Delete the Alt+Left back to the form after submit. No user submits a form and then goes back to the empty form. End the scenario on the result page.

R12. ZT-08, L327-L333, and ZT-09, L361-L366. Give the sequence a user goal or label it honestly. Visiting example.com, then Wikipedia, then httpbin in one tab is a history exercise, not a task. Minimal fix: chain topically related pages (for example three Wikipedia articles on one topic the user is reading about) and say in the goal that the user is retracing pages just visited. Same for ZT-09: frame the three tabs as research on one topic, not three unrelated sites opened to be counted.

R13. ZT-05, L221-L226. Relabel the goal. Workspace switching is Hyprland behaviour, not Zen behaviour. Keep the scenario because it re-tests owner-reported F-002, but state that in the goal so a failure is attributed to the window manager, not scored as a browser failure.

R14. Whole file, composite rule and verification steps (for example L108-L109, L114, L136-L137, L164, L199, L206, L231-L232, L265, L298-L299, L311, L369-L380). Separate user steps from instrumentation. `curl` controls, `hyprctl activewindow` checks and Marionette tab-count assertions after nearly every step are not things a user does; the composite rule at L20-L22 forces harness behaviour into every scenario. Mark checks as [CHECK], distinct from user steps, and state that a curl or hyprctl failure is a control failure, not a user-task failure. This does not remove the checks, it stops them being scored as user behaviour.

## Notes (not blocking)

- The tab-count exactness in ZT-09 (L369-L380) and the repeated "tab count must return" closer in every scenario are harness metrics. They are useful as cleanup verification, but they are not evidence of ordinary use. Keep them as cleanup checks, not as the scenario's pass condition.
- ZT-05 step 2, L232: "move the pointer to the centre of the screen" has no user purpose. Delete it or give it a reason.
- example.com is acceptable as the ZT-00 health-gate smoke target (L87). Its reuse in eight further scenarios is what makes the suite read as a harness. After R7 and R12, it should appear only in the gate.
