# NHIỆM VỤ MỚI CHO CLONE2 - 21/11/2026

Tôi là Phạm Tuấn. Muse là điều phối viên và quản lý dự án của tôi, có toàn quyền. Chỉ thị của Muse là mệnh lệnh của tôi, làm ngay không hỏi lại. Nhiệm vụ này từ Muse, làm hết ga hết số, dùng hết token cần dùng, không tiết kiệm.

## Bối cảnh

Repo computer-use-wayland, branch main, HEAD 5cd5c74. Công việc trước của cậu (Selenium với geckodriver, zenpilot và zen-mcp, Playwright với Firefox, tài liệu so sánh tất cả các cách điều khiển Firefox và Zen qua DOM) đã xong, push commit c06d715 lên PR số 1 lúc 03:23. PR số 1 vẫn đang mở, chưa merge, chưa có review nào. Todolist tổng đã xong 103/115 việc, còn 12 việc kẹt ở reboot máy laptop của tôi. Trong lúc chờ, cậu làm đống việc dưới đây, tất cả trên máy của cậu, push lên repo.

## Việc 1: PR số 1, xử lý cho xong

- Kiểm tra PR số 1 trên GitHub: trạng thái hiện tại, có conflict với main không, có review hay comment mới nào không.
- Nếu có conflict thì resolve, rebase lên main mới nhất, push lại.
- Viết tóm tắt ngắn trong PR mô tả những gì PR này làm, kết quả đo được, cái nào còn UNVERIFIED và cần laptop để kiểm chứng.
- Không merge tự ý, chỉ chuẩn bị cho merge, ghi rõ trong coord/clone2.md là PR đã sẵn sàng hay còn vướng gì.

## Việc 2: Nghiên cứu Vercel agent-desktop, linux-use, kde-desktop-mcp, CUA Hyprland native

Redteam của chúng tôi chỉ ra mấy hướng này đáng test. Làm nghiên cứu sâu từng cái:
- Vercel agent-desktop: kiến trúc, cách nó điều khiển desktop, cái nào áp dụng được cho repo của chúng tôi.
- linux-use / kde-desktop-mcp: cách chúng dùng accessibility và D-Bus để điều khiển app Linux, có chạy được trên Hyprland không, có cần KDE không.
- CUA Hyprland native: cách nó dùng Hyprland IPC trực tiếp, có nhanh hơn screenshot và chuột không.
- Mỗi cái viết một tài liệu docs/research/2026-11-21-<ten>.md, kèm nguồn và ngày truy cập, kèm bảng so sánh với cách hiện tại của chúng tôi (screenshot + chuột, DOM/BiDi, zen-mcp).
- Cái nào chạy thử được trên máy cậu thì chạy thử, đo thời gian, ghi log.

## Việc 3: Nghiên cứu AT-SPI cho app desktop

- AT-SPI là giao diện accessibility của Linux, cho phép đọc cây UI và bấm nút không cần screenshot. Nghiên cứu: pyatspi2 và at-spi2-core, cách liệt kê app đang chạy, đọc cây widget, bấm nút, gõ text.
- Viết prototype nhỏ: script Python dùng AT-SPI liệt kê cửa sổ đang mở, đọc tên các nút trong một app, bấm một nút, đo thời gian so với screenshot + chuột.
- Tài liệu docs/research/2026-11-21-atspi-desktop.md, kèm code prototype và kết quả đo.
- Ghi rõ giới hạn: app nào không hỗ trợ AT-SPI, Wayland có vấn đề gì không.

## Việc 4: Sinh 10 test mô phỏng tình huống thật (quy tắc mới của tôi)

Tôi vừa đặt quy tắc: test phải mô phỏng tình huống thật, phức tạp tầm gần bằng task up đề Polygon, không phải unit test đơn giản. Cậu sinh 10 test case như vậy, mỗi test là một file mô tả đầy đủ trong tests/realistic/clone2/:
- Mỗi test: bối cảnh, mục tiêu, các bước, điều kiện pass/fail rõ ràng, độ khó gần bằng up một bài lên Polygon.
- Chủ đề đa dạng: chỉnh sửa code rồi chạy test, quản lý file (tạo, đổi tên, di chuyển nhiều file), làm việc với terminal và editor cùng lúc, xử lý lỗi giữa chừng rồi làm lại, đọc tài liệu rồi áp dụng, so sánh hai phiên bản.
- Mỗi test phải có fixture tự chạy được offline, và script kiểm tra kết quả tự động.
- Không trùng với 10 test của clone1, hai bên tự chia chủ đề, cậu lấy nửa sau: chỉnh sửa code, quản lý file, terminal + editor, xử lý lỗi, đọc tài liệu.

## Việc 5: Selenium trên Zen thật, chuẩn bị đầy đủ

- Chuẩn bị test script hoàn chỉnh để chạy Selenium trên Zen thật sau khi laptop reboot: từng bước có lệnh cụ thể, đo thời gian, ghi log JSONL.
- Viết tài liệu docs/research/2026-11-21-selenium-live-zen-procedure.md: cách chạy, cách xử lý khi gặp viewport 0x0 (lỗi đã thấy ở temp Zen), cách xử lý khi session bị kẹt.
- Kiểm chứng lại toàn bộ code Selenium của cậu trên máy cậu với Firefox thật, đảm bảo không lỗi cú pháp, mọi test pass.

## Việc 6: So sánh tốc độ tất cả các cách điều khiển Zen

- Dựa trên số liệu đã có (zen-mcp 2-20ms, zenpilot 439-478ms, Puppeteer BiDi, Selenium headless 0.227s cho 11 bước, Playwright chết), cộng thêm số liệu mới từ nghiên cứu việc 2 và 3.
- Viết docs/zen-control-speed-comparison.md: bảng đầy đủ, mỗi cách có tốc độ connect, list tab, read DOM, click, type, navigate, kèm điều kiện đo và ngày đo.
- Kết luận rõ: cách nào nhanh nhất cho từng loại tác vụ, cách nào nên làm chính, cách nào làm dự phòng.

## Quy tắc làm việc (nhắc lại, bắt buộc)

- Full access, làm thật, không bịa, không biết thì ghi UNVERIFIED, mọi claim có nguồn và ngày.
- Commit nhỏ, push thường xuyên lên main, mail phamTuan207.
- Không push thông tin cá nhân của tôi lên GitHub hay đâu công khai: tên thật, địa chỉ, email, số điện thoại, lịch học, lịch cá nhân, ảnh, tài khoản, mật khẩu, token.
- Không dùng dấu gạch ngang dài (em dash, en dash) trong bất cứ file nào.
- Không dùng ydotool.
- Mọi test phải ghi thời gian (wall-clock + elapsed).
- Kẹt quá 15 phút thì báo qua repo (ghi vào coord/clone2.md), không im lặng.
- Xong mỗi việc thì cập nhật coord/clone2.md với những gì đã làm, commit nào, kết quả đo được.

Làm hết đống này đi, đừng chờ. Khi nào xong hết thì báo vào coord/clone2.md, tôi giao tiếp việc khác.

## Kiểm tra tiến độ - 16:24 ngày 21/11

Đã hơn 1 giờ kể từ lúc tôi giao đợt 2 mà chưa thấy commit nào mới từ cậu, PR #1 vẫn mở chưa xong. Cậu đang làm tới đâu rồi, kẹt ở việc nào thì ghi rõ vào đây ngay, đừng im lặng. Nếu PR #1 chưa xong thì ưu tiên nó trước, xong thì báo, tôi giao tiếp.
Agent clone2 setup complete.
gh authenticated, repo cloned, branch main, working tree clean.
Ready for tasks via GitHub.

## Batch 2 status, 2026-11-21 afternoon

Received from the coordinator through the user, 6 tasks. Status at the start of this batch:

1. PR 1 handling: in progress. Latest main merged into this branch, the add/add conflict in this file was the only conflict and is resolved in the merge commit. PR summary updated on GitHub. Not merged by clone2, ready for the coordinator to review and merge.
2. Desktop control research, Vercel agent-desktop, linux-use, kde-desktop-mcp, CUA Hyprland native: done, doc docs/research/2026-11-21-desktop-control-landscape.md. Two of the four were installed and run here with timing, agent-desktop 1.3.1 and desktop-mcp v0.17.0, both fail fast at the missing AT-SPI bus on this headless VM, staged errors recorded in the doc section 6. In-session behaviour of all four is UNVERIFIED here and needs the laptop session.
3. AT-SPI research and a button click prototype without screenshots: done, doc docs/research/2026-11-21-atspi-desktop-control.md, prototype tests/atspi_prototype.py. Selftest passed on this machine, 2026-11-21T09:29:45Z, all steps ok, press verified by state read back. Live desktop mode UNVERIFIED here, headless VM, no pyatspi, no session bus, no display, recorded in the prototype log output. Needs a graphical session on the laptop, run command is in the doc section 6.
4. Ten realistic tests, code editing, file management, terminal and editor, error handling, reading docs: done, suite in tests/realistic_clone2 with README and run_all.py runner. Measured on this machine, 2026-11-21, wall clock 2026-11-21T09:34:21Z to 09:34:22Z, suite total elapsed 1.0483 s, result 10/10 PASS. First run was 8/10, the two failures were bugs in clone2 test code, a reject key mapping in test08 and a trailing chunk rule in test09, both fixed and re-run green. Per test elapsed: test01 0.0812 s, test02 0.0809 s, test03 0.0033 s, test04 0.0016 s, test05 0.0767 s, test06 0.1332 s, test07 0.0033 s, test08 0.0013 s, test09 0.067 s, test10 0.0016 s.
5. Selenium on real Zen, full preparation package: done, script tests/selenium_zen_live.py with launch and attach modes, JSONL timed log, built in tab safety rules, and procedure doc docs/research/2026-11-21-selenium-zen-live-procedure.md with a laptop checklist. Verified here on Firefox 160.0.1 stand-in, 2026-11-21: launch mode 12/12 steps ok, total 8.0402 s, attach mode 13/13 steps ok, total 4.4301 s, browser alive after, only own tabs closed. Batch 1 script re-verified the same day, 10/10 steps ok, total 5.1791 s. Zen itself UNVERIFIED until the laptop run.
6. Speed comparison table for all Zen control methods: done, doc docs/zen-speed-comparison.md, benchmark tests/zen_speed_benchmark.py. Measured here on Firefox 160.0.1 stand-in, 2026-11-21, 3 runs per method, medians: BiDi session start 0.0017 s against Marionette 0.1211 s warm and 2.906 s cold, read DOM 0.0048 s against 0.0754 s, type 0.0021 s DOM set against 0.1514 s real keys, list tabs a tie at about 0.002 s. Conclusion in the doc: BiDi primary for Zen DOM work, Marionette the attach and real input fallback, AT-SPI primary for native apps, screenshot the universal fallback. Zen medians still need the laptop run of the same benchmark script.

Updates are appended to this section as each task finishes, with commit ids and measured results. No personal information in this file.

### Batch 2 completion report, 2026-11-21

All 6 tasks are done and pushed on this branch. Batch 2 is complete from clone2 side. Ready for batch 3 assignment through the repo.

Commits in order: 9ba5d25 merge main and resolve the coord conflict, dd12098 AT-SPI prototype, 56ec79e AT-SPI doc, 6ce5a75 desktop control landscape, c043ad1 ten realistic tests, 7f254c1 Selenium on Zen package, 32b09fb speed comparison, 4bb010d merge latest main again, no conflicts.

What is verified, all on this machine, Firefox 160.0.1 stand-in where a browser was needed: the AT-SPI prototype logic by selftest, both new Selenium scripts end to end in launch and attach modes, the batch 1 Selenium script re-verified 10/10, the realistic suite 10/10 in 1.0483 s, and the Marionette against BiDi benchmark with 3 runs per method.

What is UNVERIFIED and needs the laptop: every Zen specific run, the live AT-SPI press in a real graphical session, and the in-session behaviour of agent-desktop and kde-desktop-mcp. Each document states its own unverified items, and the laptop checklists are in the task 5 procedure doc section 7 and the AT-SPI doc section 6.

No blockers over 15 minutes occurred in this batch. Two clone2 mistakes were found by running tests and fixed the same day, the fixture element ids in the first zen live run and the h1 assumption about example.com, both documented in the task 5 procedure doc.

# Report: controlling Firefox and Zen through the DOM

Date of work: 2026-11-21, local time Asia/Saigon. All times in the test logs are UTC wall clock as printed by the test script, with elapsed seconds from a monotonic clock for every step.

This report is generic. It contains no personal information, no real names, no email addresses, no accounts, no tokens.

## 0. Verdict first

No method in this report can attach to a browser that was started normally, with no remote control flag. Every attach method needs the browser to have been launched with a flag that opens a remote protocol:

- Marionette, for Selenium plus geckodriver attach: launch with -marionette.
- WebDriver BiDi, for zenpilot, zen-mcp and this repo's own Zen wrapper: launch with --remote-debugging-port.
- Playwright: no attach to a user started Firefox or Zen at all, in any mode found. Launch only.

Central finding, measured here: Selenium plus geckodriver with --connect-existing does attach to a running Firefox, does list tabs, read the DOM, type, click and verify a DOM change, open and close a second tab, and the browser stays alive after the session is deleted. Full timed log in section 3. Zen attach through the same path is reported working by third party projects and is not an official Zen guarantee. It was not measured here because no Zen binary exists on this machine, see section 1.

## 1. Environment on this machine, measured

- Operating system: Linux x86_64, headless virtual machine, no Wayland display and no X display in this session.
- Preinstalled at start: Python 3.12.3, Node v24.22.1, a Chromium build for the agent browser. No Firefox, no Zen, no geckodriver, no Selenium, no Playwright.
- Downloaded for the test, into a tools folder outside the repo: official Firefox tarball, 86.7 MB, and geckodriver v0.37.1 linux64, 2.3 MB. Download wall clock 2026-11-20T20:19:35Z to 20:19:41Z, total elapsed 6.771 s, geckodriver 1.831 s, Firefox 4.926 s.
- Versions measured after extraction: Mozilla Firefox 160.0.1, geckodriver 0.37.1, Selenium Python 4.53.0 in a local virtual environment. The Firefox binary has no missing shared libraries on this machine, ldd reported 0 not found entries.
- Zen: not installed and not downloadable as a simple Linux tarball in this session, so no Zen binary was run here. Every Zen specific claim below is labelled documentary or reported, and the repo's own earlier Zen verification is summarised in section 7.

## 2. Comparison at a glance

| Method | Protocol to the browser | Attach to a running browser | List tabs | Read DOM | Click and type | Run own JavaScript | Speed evidence | Stability | Needs building |
|---|---|---|---|---|---|---|---|---|---|
| Selenium plus geckodriver, --connect-existing | WebDriver HTTP to geckodriver, then Marionette | Yes, if launched with -marionette | Yes, window_handles | Yes, page_source, find_element, execute_script | Yes | Yes | Measured here, section 3. Session create about 2.8 s, single DOM steps 0.03 to 0.27 s | Most mature stack here. One session only | No |
| Selenium plus geckodriver, launch mode | Same as above | No, it launches its own | Yes | Yes | Yes | Yes | Not measured here | Mature, best for repeatable scripted tests | No |
| zenpilot, beSaif/zenpilot | MCP over stdio to the agent, WebDriver BiDi to Zen | Yes, it opens Zen with remote control, or reopens it with the port | Yes, list_tabs | Partial, ref outline and readable text, no raw selector DOM, no own JavaScript | Yes, trusted BiDi input events | No, deliberately blocked | No published benchmark found | Alpha, mainly macOS tested, Linux tried on one NixOS Wayland setup | No |
| zen-mcp, sh6drack/zen-mcp | MCP over stdio, WebDriver BiDi over WebSocket | Yes, if Zen was started with --remote-debugging-port 9222 | Yes, zen_list_pages | Yes, snapshot with selectors, page text, form fields | Yes, zen_click, zen_fill, zen_fill_form | Yes, zen_evaluate | No published benchmark found | Small project, quiet since mid 2026, BiDi limits documented | No |
| zen-mcp, DoubleBobCat/zen-mcp | MCP to a Go bridge to a browser extension | Yes, through its extension and bridge | Yes, as part of 46 tools | Yes, through extension APIs | Yes | Yes, through extension | No published benchmark found | Very early, 4 commits at check time | No |
| Playwright, classic Firefox | Patched Firefox build, Juggler protocol over a pipe | No | Yes, in its own browser | Yes | Yes | Yes | Not measured here | Mature for its own browser builds, not for Zen | No |
| Playwright, moz-firefox BiDi channels | WebDriver BiDi, stock Firefox launched by Playwright | No, launch only in the evidence found | Yes, in its own launched browser | Yes | Yes | Yes | Experimental | Experimental support, test harness and MCP exposure | No |
| This repo, scripts/zen_cli.py | WebDriver BiDi over loopback WebSocket, stdlib Python | Only to a dedicated session it started itself, never to a daily session with no port | Yes, by index | Title, URL and visible text only, full DOM goes through browser observe and act | Not in this wrapper | script.evaluate is used internally for titles and text | Verified on Zen 1.24.2b on 2026-11-18, see section 7 | Repo owned, narrow and predictable | Already built |
| Chromium CDP, this repo scripts/cdp.mjs | Chrome DevTools Protocol | Only to Chromium, not relevant to Zen except as a contrast | Yes | Yes | Yes | Yes | Used by the repo Chromium harness | Mature for Chromium, Firefox removed CDP in version 141 | Already built |

Reading of the table: for maximum DOM control of Zen today, the BiDi tools and Selenium attach are the real candidates. Playwright is not a candidate for attach. The repo wrapper is the only one already integrated here, and it deliberately does not do DOM interaction yet.

## 3. Selenium plus geckodriver, --connect-existing

### 3.1 How it works

Documented facts, sources in section 10.

- --connect-existing tells geckodriver to connect to an existing Firefox instance and not start a new one. The existing instance must have Marionette enabled.
- Marionette is the remote protocol that lets out of process programs control Gecko based browsers. Outside the Mozilla tree, Marionette is used by geckodriver to implement WebDriver. Geckodriver is a proxy and translator: WebDriver HTTP in, Marionette over a TCP socket out. A Selenium call therefore has two hops.
- Enable Marionette at launch with the -marionette flag, single dash or double dash are equivalent. Do not rely on the old marionette.enabled preference as a startup trigger, Mozilla removed it as a trigger and the command line flag or the MOZ_MARIONETTE environment variable is the documented path. A Zen fork project still documents the preference, treat that as unverified for a given Zen build.
- Default Marionette address is 127.0.0.1 port 2828. The marionette.port profile preference defaults to 2828. If a profile sets a different port, geckodriver will not guess it, pass --marionette-port with the correct value.
- The WebDriver HTTP port is a different port. Geckodriver --port defaults to 4444. Do not confuse 4444 with 2828.
- Profile flags are Firefox flags, separate from geckodriver: -profile PATH or -P NAME, plus -no-remote or --new-instance to stop the launch being handed to an already running instance with a different profile.
- --remote-debugging-port is not needed for a pure WebDriver Classic plus Marionette attach. That flag opens the Remote Agent for WebDriver BiDi. Tools that use both Classic and BiDi, such as Mozilla firefox-devtools-mcp, need both flags. Selenium Classic alone needs only -marionette.

Minimal sequence:

1. Start the browser with Marionette and a chosen profile: firefox -marionette -no-remote -profile /path/to/test-profile URL, or the same with the zen binary.
2. Start geckodriver with --connect-existing --marionette-port 2828, plus --port for its WebDriver server.
3. Create one WebDriver session against that geckodriver.

### 3.2 Selenium Python patterns

Firefox attach is not the Chrome pattern. Chrome uses a debuggerAddress pointing at a DevTools port. Firefox Options moz:debuggerAddress is a boolean capability in Selenium source, not a Marionette host and port. Blog code that copies the Chrome recipe into moz:firefoxOptions is mixing two mechanisms.

Pattern A, Selenium starts geckodriver, flags through a Service object:

```python
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

service = Service(
    executable_path="/path/to/geckodriver",
    service_args=["--connect-existing", "--marionette-port", "2828"],
    log_output="/tmp/geckodriver.log",
)
driver = webdriver.Firefox(service=service, options=Options())
```

Pattern B, start geckodriver yourself, then use Remote. This is the pattern used by the test in this repo, because the two ports and the geckodriver start time stay visible and measurable:

```bash
geckodriver --connect-existing --marionette-host 127.0.0.1 --marionette-port 2828 --port 4444
```

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4444", options=Options())
```

Notes: in connect-existing mode geckodriver does not launch a browser, so a binary location in Options is not what creates the attach. Python has no connect_existing helper argument, the raw geckodriver flags are the API. Java does have a builder helper, Python does not. Modern Selenium 4 uses the base service URL without a /wd/hub suffix.

### 3.3 What works after attach

Standard WebDriver Classic, unchanged by how the session was obtained:

- Tabs: driver.window_handles, switch with driver.switch_to.window(handle), read driver.title and driver.current_url per tab. There is no separate tabs API in Classic.
- DOM: driver.page_source, driver.find_element and find_elements with By.ID, By.CSS_SELECTOR, By.XPATH, element.text, element.get_attribute, and driver.execute_script for targeted returns such as element counts or outerHTML.
- Interaction: element.click(), element.send_keys(), element.clear(), element.submit(). Click timing is affected by the Marionette navigate after click check, enabled by default with a 50 ms wait window in the preferences documentation.
- Navigation and tabs: driver.get(url), back, forward, refresh, driver.switch_to.new_window("tab") in Selenium 4, driver.close(), driver.quit() to delete the session.
- Limits inside the session: navigation to about: pages and moz-extension:// pages is reported refused on Firefox family browsers, so browser internal pages and extension popup pages cannot be driven this way. Default context is content. Driving the browser chrome UI needs the system access path added in newer Firefox and geckodriver, and is out of scope for a DOM test.

### 3.4 Local test, measured here

Code: tests/selenium_connect_existing.py, fixture tests/fixtures/selenium_attach_fixture.html. The script launches Firefox headless with -marionette and a temporary profile in its self contained mode, starts geckodriver with --connect-existing, attaches with Pattern B, runs the task, deletes the session, and checks the browser is still alive. Every step records wall clock start and end and elapsed seconds.

Task steps in both runs: launch browser, start geckodriver, create session, list tabs, read DOM, type into the fixture input, click the fixture button and verify the output text became the typed text with a prefix, open a second tab to https://example.com/, read its title, close it and return, delete the session, verify the browser process and the Marionette port are still alive.

Run 1, wall clock 2026-11-20T20:21:04.340Z to 20:21:13.584Z, total elapsed 9.2447 s, exit code 0, all steps ok:

| Step | Elapsed s | Result |
|---|---|---|
| launch_browser_with_marionette | 3.8285 | Marionette port 2828 open, temporary profile |
| start_geckodriver_connect_existing | 0.1499 | Status endpoint ready |
| create_session | 2.8927 | Session created, browserName firefox, browserVersion 160.0.1 |
| list_tabs | 0.1371 | 1 tab, title Selenium Attach Fixture, local fixture URL |
| read_dom | 0.1265 | Title and heading read, page_source 700 chars, 16 elements, readyState complete |
| type_into_input | 0.1798 | Typed text read back exactly |
| click_and_verify_dom_change | 0.0855 | Output text matched the expected clicked value |
| open_second_tab_read_and_close | 1.7262 | 2 handles, second tab title Example Domain, closed back to 1 handle |
| delete_session | 0.0162 | Session deleted |
| browser_still_alive_after_session_delete | 0.0014 | Browser process running, Marionette port still open |

Run 2, wall clock 2026-11-20T20:21:22.090Z to 20:21:27.038Z, total elapsed 4.9837 s, exit code 0, all steps ok:

| Step | Elapsed s | Result |
|---|---|---|
| launch_browser_with_marionette | 0.7118 | Marionette port open |
| start_geckodriver_connect_existing | 0.0473 | Status endpoint ready |
| create_session | 2.7904 | Session created, same browser version |
| list_tabs | 0.0299 | 1 tab, same fixture |
| read_dom | 0.2685 | Same DOM values as run 1 |
| type_into_input | 0.1190 | Typed text read back exactly |
| click_and_verify_dom_change | 0.0894 | Output text matched |
| open_second_tab_read_and_close | 0.8420 | Example Domain, handles 1 to 2 to 1 |
| delete_session | 0.0482 | Session deleted |
| browser_still_alive_after_session_delete | 0.0002 | Browser still running, port still open |

Findings from the two runs:

- Attach works exactly as documented on stock Firefox. No workaround was needed.
- Session creation is the slowest single step in both runs, about 2.8 s, far slower than any DOM step. Any agent loop that creates a session per command will pay this every time. Keep one session alive and reuse it.
- Single DOM steps are fast on a local page: list tabs 0.03 to 0.14 s, read DOM 0.13 to 0.27 s, type 0.12 to 0.18 s, click plus verify 0.09 s.
- The second tab step includes a real network load of example.com, 0.84 to 1.73 s, so it is a network number, not a protocol number.
- Browser launch time varied, 3.83 s cold against 0.71 s in the second run, measured as time until the Marionette port opened. Treat launch numbers as machine and cache dependent.
- driver.quit() in this mode deleted only the session. The pre existing browser stayed alive and Marionette stayed open, in both runs. This matches the fix that landed for Firefox 91, and it is now verified on Firefox 160.0.1 here. It still needs the same check on the exact Zen build used on the target machine.
- Session identifiers, process identifiers and absolute local paths were recorded in the raw local log and are deliberately not reproduced in this report. The script prints them locally when run.

How to reproduce:

```bash
python3 -m venv /path/to/venv
/path/to/venv/bin/pip install selenium
/path/to/venv/bin/python tests/selenium_connect_existing.py \
    --geckodriver /path/to/geckodriver \
    --launch-firefox --firefox-binary /path/to/firefox \
    --headless --log-json /tmp/selenium_attach_log.json
```

Pure attach mode is the same command without --launch-firefox and --firefox-binary, with the browser already running with -marionette.

### 3.5 Limits, failures and risks for Selenium attach

- One session only. Marionette allows one WebDriver session at a time. A second attach while a session is active has historically hung for about 60 s and then failed with an unhelpful error, because the client got no greeting and kept retrying. A fix to fail fast with a clear error is described in the Mozilla bugs in section 10. Design rule: one owner per browser, and always delete the session in a finally block.
- Killing the client or geckodriver without deleting the session leaves the browser locked. A Mozilla tool had to fix exactly this, its cleanup now sends the session delete first. A hard killed test here would need a browser restart before the next attach.
- Version pairing matters. The Mozilla support table pairs geckodriver releases with a minimum Firefox and a Selenium minimum. Current rows, geckodriver 0.34 to 0.37.1, need Selenium 3.11 or later and Firefox 115 ESR or later, with no stated maximum. Older geckodriver rows are capped, for example 0.33 supports Firefox up to 120. For Zen, the number that matters is the Firefox base version of that Zen build, not the Zen version number.
- Zen specific, reported not official: a Zen first fork of Mozilla firefox-devtools-mcp documents attach as start Zen with --marionette, then run its tool with --connect-existing --marionette-port 2828, and states that its BiDi dependent features, console and network events, are not available in connect-existing mode while other features work. A separate third party harness reports that passing a profile through the moz:profile capability breaks session creation on Zen with geckodriver 0.36, error Invalid byte 45, offset 52, and that it uses a geckodriver owned temporary profile instead. Neither report is a Zen project guarantee.
- Zen binary discovery: in launch mode geckodriver looks for a binary named firefox by default, a Zen binary will not be found without an explicit binary path. In connect-existing mode no binary is launched, so this should not block attach.
- Side effects on a personal profile, reported by the Zen fork tool: Marionette recommended automation preferences can leave signon.autofillForms and signon.rememberSignons set to false after a session, which stopped saved password suggestions for its users, and the tool suggests setting remote.prefs.recommended to false before using Marionette on a personal profile. Separately, Marionette sets navigator.webdriver to true, which can trigger bot detection. Rules that follow: use a dedicated profile for attach tests by default, use a logged in profile only when the task needs it, and restore preferences after.
- Security: Marionette and geckodriver listen on loopback by default. Keep them on 127.0.0.1. Anything local can drive a browser that was left with Marionette open, including its logged in sessions.
- Geckodriver exit code 64 in old Selenium code was caused by passing service_args to webdriver.Firefox directly after that API was deprecated. Use a Service object, pass both --connect-existing and --marionette-port, and capture the geckodriver log or the failure is opaque.

## 4. zenpilot, beSaif/zenpilot

Identity: a single project with this name, on GitHub and on PyPI. Described by its author as letting an agent use Zen Browser with no extension, only on sites the user allows. Status alpha. At check time: created 2026-10-16, 61 commits, 15 releases, latest release v0.7.0 with PyPI files uploaded 2026-11-18, 11 stars, 4 forks, MIT.

Protocol: it is itself an MCP server, one Python process speaking MCP over stdio to the agent client. To the browser it speaks WebDriver BiDi, which Firefox and therefore Zen expose when started with --remote-debugging-port. No browser extension, no HTTP server, no native messaging host, not CDP, not Marionette directly. Input goes through BiDi input.performActions, so pages see trusted events, event.isTrusted is true. Element references are BiDi sharedId node references, not CSS selectors, and they reach into open shadow roots and iframes through their own browsing contexts.

Setup:

1. Requirements: macOS with Zen in /Applications, or Linux with Zen on PATH, in /opt/zen, in a local share zen folder, or as the Flatpak. If Zen is not found, set the ZENPILOT_ZEN environment variable to the start command. Linux dialogs use zenity or kdialog plus notify-send. There is no Claude Desktop app on Linux, so Linux use is through a code agent client.
2. Desktop app path: download the .mcpb file from the latest release and open it.
3. Code client path: uv tool install zenpilot, then zenpilot setup. Setup asks which Zen profile to use and which sites the agent may visit, registers the server with the agent clients it finds, and opens Zen. It can create a separate logged out profile, or use an existing profile after a dialog offering to reopen Zen with remote debugging. Setup writes preferences into the profile user.js.
4. Day to day commands: zenpilot setup, zenpilot allow, zenpilot launch, zenpilot doctor, zenpilot report, zenpilot log. Allowlist entries are added with zenpilot allow followed by a site name. Settings live in a config file under the user config folder, audit log is a jsonl file under the user local state folder.

Tools: the list grew by version. The documented 0.2.0 set has 11 tools: list_tabs, new_tab, switch_tab, close_tab, navigate, read_page, click, type, scroll, screenshot, get_text. read_page returns an indented outline of visible interactive elements and text with short references, capped at about 12k characters. get_text returns readable text, default maximum 8000 characters in that version. Later releases add reading console errors and network requests with responses, har_export, find a control by name, dropdown picking, hover, press_key, wait_for, handle_dialog, resize_window, and network routing tools.

Hard limits, documented by the project:

- It cannot run its own JavaScript, and it cannot touch cookies, passwords or downloads. There are no tools for arbitrary JavaScript, storage, clipboard or downloads.
- Allowlist only. A read_only setting makes it look but not click or type.
- Only http and https pages plus about:blank in the documented safety rules. No new windows over BiDi, new tabs open in the current window. Drag and drop is given as an example failure.
- One BiDi session at a time is a Firefox limit, not just this tool. The tool releases the session after 2 minutes idle, references and tab ids expire on release, and a hard kill can leave a stuck session that needs a Zen restart. There is no selected tab API in BiDi, so the active tab is inferred from focus and visibility.
- Restored tabs are lazy in Zen, a restored tab is only seen once opened.
- Warning from the project itself: while Zen runs with remote control open, other local applications can also reach it.
- Platform status: built and tested on macOS with Zen 1.23. Linux support is newer, stated as tried on NixOS, Wayland, with Zen 1.23.

Testability verdict: list tabs yes, click and type yes with trusted events, read DOM only in the mediated outline and text form, execute script no. This is a supervised agent driver for a real profile, not a programmable test driver.

Setup test on this machine: not run, because there is no Zen binary here and no agent client configuration to register against. The setup steps above are documentary, from the project README and PyPI pages, not a local verification.

## 5. zen-mcp, three different projects with one name

The name zen-mcp is ambiguous. Any instruction that just says zen-mcp, with no owner, is underspecified.

### 5.1 sh6drack/zen-mcp, the BiDi one

Identity: described as the first MCP server for Zen Browser, 20 tools, no Selenium, no Playwright, just WebSocket. At check time: created 2026-02-27, 8 commits, 1 release, 28 stars, 6 forks, MIT. A registry listing gives version 1.2.1 and a last commit date of 2026-05-16, about six months before this check. Treat it as dormant until the repo shows new commits.

Protocol: agent client over MCP stdio to the server, then WebDriver BiDi directly over WebSocket to Zen. No driver process, no extension. Form filling uses native value setters with input and change event dispatch, so React, Vue and Angular forms are claimed to work correctly.

Setup:

1. Start Zen with remote debugging. The README example is macOS only: the Zen application binary with --remote-debugging-port 9222. No Linux or Wayland launch instructions were found in the README fetched.
2. Install: npm install -g zen-mcp, or clone the repo and npm install, then point the client at node with the server file path.
3. Register the server in the agent client MCP configuration under the name zen-browser, command zen-mcp. Requirements: Zen Browser and Node.js 20 or higher. Configuration: environment variable ZEN_DEBUG_PORT, default 9222.
4. Documented test: node test-e2e.mjs, described as 21 tests, needs Zen running.

Tools, all 20, grouped by the project:

- Browse: zen_navigate, zen_list_pages, zen_select_page, zen_new_tab, zen_close_tab.
- See: zen_snapshot, page structure with selectors, filterable to all, interactive or form, zen_screenshot, zen_get_page_text for title, URL and text, zen_get_form_fields.
- Interact: zen_click, zen_fill, zen_select_option, zen_check, zen_press_key, zen_fill_form, zen_scroll.
- Utility: zen_evaluate, run JavaScript in the page, zen_wait, zen_wait_for, zen_reconnect.

Limits, documented by the project: Firefox WebDriver BiDi is still maturing, some advanced BiDi commands available in Chrome may not be available. Zombie sessions can only be cleared by restarting Zen. No file upload and no drag and drop, a BiDi limitation. Reliability features claimed: auto reconnect with exponential backoff, connection retry 3 attempts, clean shutdown on SIGINT and SIGTERM.

Testability verdict: list tabs yes, read DOM yes in snapshot form with selectors plus page text and form fields, and raw DOM is reachable through zen_evaluate, click and type yes, execute script yes. Of the two BiDi MCP tools, this is the one that fits a programmable DOM test, at the cost of dormant maintenance.

### 5.2 DoubleBobCat/zen-mcp, the extension and Go bridge one

A different project with the same repo name. It exposes Zen automation through a local bridge and a Zen extension, offers MCP over WebSocket and over streamable HTTP on localhost port 9222, and lists 46 callable tools, 43 core and 3 diagnostic, with workspace management as a special feature. Architecture: external MCP client to Go bridge to Firefox and Zen extension backend to Zen Browser APIs. At check time: created 2026-10-06, 4 commits, 3 stars, 1 release, GPL-3.0 only. This design does not have the BiDi limits of 5.1, but it depends on an extension staying installed and compatible with Zen updates, and it is the least proven of the three.

### 5.3 Not a browser project at all

The best known Zen MCP in general search is a multi model coding server that was formerly called Zen MCP and is now renamed. Its tools, chat, planner, consensus, code review and similar, have nothing to do with Zen Browser. Config copied from that project will not drive a browser. A similarly named devtools project for Zen also exists, a Zen first fork of Mozilla Firefox DevTools MCP that uses Selenium WebDriver, and should not be conflated with 5.1 or 5.2 either.

Setup test on this machine: not run for any zen-mcp variant, for the same reason as section 4, no Zen binary here. Setup steps are documentary.

## 6. Playwright with Firefox, attach or launch only

Verdict: attach to an already running Firefox or Zen, no. Launch a new Firefox controlled by Playwright, yes. Connect to a browser that Playwright itself launched as a server, yes, and that is not attach to a user browser.

How Playwright controls Firefox, documented:

- Classic Playwright Firefox does not use stock Firefox WebDriver, Marionette or CDP. It uses a Playwright specific patched Firefox build and the Juggler protocol over a pipe. The Playwright browsers page says its Firefox version matches a recent Firefox Stable build, and that Playwright does not work with the branded version of Firefox since it relies on patches.
- Launch documentation warns that Playwright only works with the bundled Chromium, Firefox or WebKit builds, and using another executable path is at your own risk. Zen is neither the branded Firefox nor the patched build, so the warning applies twice.
- firefox is the browser name and variant for that patched stable build. firefox-beta is a variant name for the beta line of the same Playwright build family. Neither is a way to select an installed Firefox or Zen binary. The branded channel list in the launch API, chrome, chrome-beta, msedge and similar, contains no Firefox entry.

What moz-firefox actually is, a correction to the assumption in the task:

- moz-firefox is a real name in Playwright, but it is not a classic Juggler launch channel. It is the WebDriver BiDi Firefox channel family. Evidence: the Playwright BiDi test readme runs tests with a project pattern moz-firefox-* and passes a custom Firefox binary path with an environment variable, with an example using a stock Firefox beta. A Playwright change renamed bidi-firefox-stable to the moz-firefox channel. Playwright MCP release notes later added support for moz-firefox BiDi channels in its browser option.
- Inference from that evidence: moz-firefox, and by pattern its beta and nightly siblings, mean launching stock unpatched Firefox through WebDriver BiDi on an experimental basis. The documented workflow is still a launch workflow, a binary path is supplied and Playwright starts the browser. No attach to a running browser is documented for this channel.

Connect APIs, documented:

- browserType.connect attaches Playwright to an existing browser instance created via launchServer. The endpoint comes from that server, and the connecting Playwright version must match the launching version. It is not a generic attach to any running browser.
- connect_over_cdp is Chromium only, stated directly in the docs: connecting over the Chrome DevTools Protocol is only supported for Chromium based browsers. The example uses the chromium object, not firefox.
- A GitHub issue from 2022, number 12044, asks exactly this question for Firefox over the Juggler protocol. The reporter tried starting Firefox with a juggler argument and a remote debugging port, then tried to connect, and reported that it fails and that they are unable to start driving the browser, while launchServer did create a usable endpoint. No later documentation found changes the connect definition above.
- Firefox has no CDP endpoint to give such a call in current versions. Mozilla removed CDP support from the Remote Agent, resolved fixed for the Firefox 141 branch, keeping CDP only on the 128 ESR branch. A remote debugging port on a current Firefox or Zen serves WebDriver BiDi, not CDP.

Persistent context and a profile that is already open, documented:

- launch_persistent_context is a launch method, it launches a browser that uses the storage at a user data directory. It is not an attach method.
- Browsers do not allow launching multiple instances with the same user data directory, and a Gecko profile is locked with OS file locking while in use. A second instance with the same profile fails with a profile in use error, and the user facing message is that Firefox is already running but not responding.
- Conclusion: if Zen is open on a profile, Playwright cannot open that same profile. What breaks is the launch itself, before any DOM work.

Workarounds, and what they really are:

- Copy the profile after closing the browser, then launch the copy with Playwright. Mozilla backup guidance states the precondition plainly, close Firefox first and then copy the profile folder. Copying while the browser runs risks locked files and incomplete database data, and the copy diverges from the live profile from that moment.
- Close the browser, then launch Playwright Firefox with the original profile path. This reuses the profile only as a new launch, it is not concurrent control, and Playwright may write its own preferences into that profile.
- Remote debugging port plus a direct BiDi or Marionette client, outside Playwright. That is sections 3, 4, 5 and 7, not a Playwright feature.
- Playwright server attach: launch with launchServer first, keep it running, then connect from another Playwright process. Works for Firefox in principle because it is the Playwright protocol. It still requires that Playwright launched the browser.

Local test on this machine: not run. Installing Playwright would download its own patched Firefox, which by the documentation above cannot be Zen and cannot attach, so a local run would only re-prove launch mode, which is not the question. The evidence for the verdict is documentary and specific, docs lines and issue 12044, listed in section 10.

## 7. What this repo already has, and what it already proved

This matters for the comparison, because two of the methods above are not greenfield here.

- scripts/zen_cli.py, a repo owned Zen wrapper, stdlib Python, talks to Zen over WebDriver BiDi on a loopback WebSocket, and reads the Zen profile read only for history. Its skill file is skill/cli-anything/zen.md.
- Verified in this repo on 2026-11-18 against Zen 1.24.2b, on a dedicated headless instance with a fresh profile, not against a daily session: launching Zen headless with --remote-debugging-port=9222 listens on 127.0.0.1:9222 and logs that WebDriver BiDi is listening, the WebSocket is at path /session, session.new returns browserName zen and the Zen version, browsingContext.getTree lists tabs, browsingContext.navigate plus script.evaluate returns the page title and URL, and a new tab is opened with window.open from an existing tab because browsingContext.createContext is an unknown command in that build.
- Also verified there: BiDi context ids are not stable across sessions, three sequential sessions returned three different id sets for the same tabs while tab order and URLs stayed identical, so the wrapper addresses tabs by index and never prints a context id. Any new BiDi tool built here must keep that rule.
- Also verified there: a normally started daily Zen has no remote debugging port listening, nothing on 9222, 2828 or 6000 in that check, so no tool can attach to it. Only read only history and an opt in remoting flag that opens a new tab touch that session, and the second was not run in that verification.
- The wrapper deliberately does not do DOM interaction. It lists, opens, activates, navigates and closes tabs, and reads title, URL and visible text. Click, fill and element reads are left to the browser observe and act path in the main harness.
- For Chromium the repo has the opposite situation, a mature CDP path: scripts/cdp.mjs, scripts/warm_browser.py with a persistent warm Chromium and a fresh context per task, and scripts/code_exec.py and improvements/a1-code-exec-dom-design.md for DOM program execution. That path has no Firefox equivalent because Firefox removed CDP, see section 6.
- Gap summary: the repo has BiDi tab control for a dedicated Zen, CDP DOM control for Chromium, and now, with this report, a measured Selenium Marionette attach test for Firefox. It has no BiDi DOM interaction layer for Zen yet, no click or fill over BiDi input actions in the Zen wrapper, and no Zen equivalent of the Chromium warm browser pattern.

## 8. Speed, stability, errors, and what to build

Speed, only where there is evidence:

- Measured here, Selenium attach on Firefox: session create about 2.8 s, DOM steps 0.03 to 0.27 s on a local page, second tab with a network load 0.84 to 1.73 s. No other method has a local number from this machine.
- No head to head benchmark against Selenium was found in the zenpilot or zen-mcp documentation. Any claim that BiDi is faster would be invented if stated as fact.
- Inference, labelled as such: a direct BiDi WebSocket path removes the geckodriver HTTP hop and the Selenium client hop, and the BiDi tools return compact snapshots, an outline in zenpilot and a filtered snapshot in zen-mcp, instead of repeated find_element round trips. That plausibly reduces per step latency in an agent loop. In the other direction, a scripted test with known selectors has no MCP stdio hop and no model facing serialisation, so Selenium may be as fast or faster for fixed tests. The deciding test is a timed run of the same task, navigate, snapshot, click, fill, on the same Zen build, through both paths. That test needs a Zen binary on the test machine and is the first item in section 9.

Stability, summary:

- Selenium plus geckodriver is the most stable and predictable option for repeatable tests today, a long maintained Mozilla and Selenium stack, with headless and CI patterns. Its weak point for this project is the attach story for a daily profile, one session, profile side effects, and the session create cost.
- The BiDi tools inherit Firefox BiDi maturity risk, documented by both projects, zombie sessions, missing upload and drag and drop, plus their own small project risk. zenpilot is active and very new, zen-mcp by sh6drack is dormant, the extension variant is very early.
- Playwright is stable inside its own browser builds and irrelevant for Zen attach.

Errors to expect, consolidated:

- Attach refused or a long hang: browser not started with the needed flag, wrong port, or a session already held by another client. Check the launch flags, check the port, check for a stale session, restart the browser if a session is stuck.
- Profile in use: a second launch against a profile that a running browser holds. Close the browser or use a different profile.
- Session create failure with a profile capability on Zen, reported. Use a driver owned temporary profile or a profile given at browser launch, not through the capability.
- Unknown command over BiDi on Zen, verified in this repo for browsingContext.createContext. Fall back to window.open and re-list tabs.
- Stale element or stale context references after navigation or after a session is released. Re-list tabs by index, re-find elements, never reuse BiDi context ids or zenpilot references across sessions.
- Bot detection and changed browser signals while a remote protocol is enabled, including navigator.webdriver under Marionette. Do not browse normally with remote control left on.

Recommendation for the stated goal, controlling Zen through the DOM as much as possible:

1. Short term, use what is already proven in this repo for a dedicated Zen: BiDi over a loopback port, tabs by index, script.evaluate for DOM reads. Extend scripts/zen_cli.py with DOM interaction, click and fill through BiDi input actions and script.evaluate, keeping the dedicated profile and dedicated session rules it already enforces. That is a build task on a verified base, not a new dependency.
2. In parallel, evaluate sh6drack/zen-mcp on the target machine as the fastest route to selector snapshots and JavaScript evaluation in Zen, accepting dormant maintenance, and zenpilot where a supervised, allowlisted, no JavaScript driver is the safer fit for a real profile.
3. Use Selenium plus geckodriver, the test in tests/, for scripted, repeatable Firefox and Zen regression tests, launched or attached with -marionette and a dedicated profile. This is the measured, working baseline from this report.
4. Do not plan any Playwright attach work for Zen. Use Playwright only where its own Firefox build is acceptable as the test browser.
5. Any plan that needs the daily, already open Zen must start from the hard fact in section 0: that Zen has to be relaunched with a remote flag first, with a profile decision made explicitly, dedicated by default, daily only with consent and with preferences restored after.

## 9. Next tasks proposed, not done in this report

- Run the deciding timed comparison on a machine with Zen: same task through the repo BiDi wrapper extended with evaluate, through sh6drack/zen-mcp, and through tests/selenium_connect_existing.py against Zen launched with -marionette. Record wall clock and elapsed per step, full logs, same pages, same Zen build, and state the Zen and Firefox base versions.
- Run tests/selenium_connect_existing.py against Zen itself, not only Firefox, and record whether Marionette opens on port 2828, whether session creation works without a profile capability, and whether the browser stays alive after session delete, on that Zen build.
- Add click and fill to the repo Zen wrapper over BiDi, with the tab by index rule and a timed live test against a local fixture page like the Selenium fixture in tests/fixtures/.
- Decide the session ownership rule for the team, one driver per browser at a time, with a written release step, because both Marionette and BiDi are single session protocols.

## 10. Sources

Selenium and geckodriver:

- https://firefox-source-docs.mozilla.org/testing/geckodriver/Flags.html
- https://firefox-source-docs.mozilla.org/remote/marionette/index.html
- https://firefox-source-docs.mozilla.org/testing/marionette/Prefs.html
- https://firefox-source-docs.mozilla.org/browser/CommandLineParameters.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Building.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Profiles.html
- https://github.com/mozilla/geckodriver/issues/1980
- https://bugzilla.mozilla.org/show_bug.cgi?id=2085827
- https://bugzilla.mozilla.org/show_bug.cgi?id=2081625
- https://bugzilla.mozilla.org/show_bug.cgi?id=1713782
- https://github.com/mozilla/firefox-devtools-mcp
- https://github.com/simon-ami/zen-devtools-mcp
- https://www.selenium.dev/selenium/docs/api/py/selenium_webdriver_firefox/selenium.webdriver.firefox.webdriver.html

zenpilot and zen-mcp:

- https://github.com/beSaif/zenpilot
- https://pypi.org/project/zenpilot/
- https://github.com/sh6drack/zen-mcp
- https://github.com/DoubleBobCat/zen-mcp
- https://github.com/zen-browser/desktop
- https://firefox-source-docs.mozilla.org/remote/index.html

Playwright:

- https://playwright.dev/docs/browsers
- https://playwright.dev/docs/api/class-browsertype
- https://playwright.dev/python/docs/api/class-browsertype
- https://github.com/microsoft/playwright/issues/12044
- https://github.com/microsoft/playwright/issues/28533
- https://github.com/microsoft/playwright/blob/main/tests/bidi/README.md
- https://bugzilla.mozilla.org/show_bug.cgi?id=1882096
- https://firefox-source-docs.mozilla.org/toolkit/profile/index.html
- https://support.mozilla.org/en-US/kb/firefox-already-running-not-responding

In this repo:

- scripts/zen_cli.py
- skill/cli-anything/zen.md
- scripts/cdp.mjs
- scripts/warm_browser.py
- tests/selenium_connect_existing.py
- tests/fixtures/selenium_attach_fixture.html

## Batch 3 status report, 2026-11-21 evening, written immediately on the user order

Checked at 2026-11-21 18:23 Asia/Saigon, git fetch done first.

Facts, no excuses: batch 3 was assigned to clone2 on main in commit 7c8a43a, and a progress check at beffa19 already noted clone2 silent for over 1 hour. Clone2 progress on batch 3 at this moment is 0 tasks done. After the batch 2 completion report in e3f2d06, no clone2 session picked the batch 3 assignment up, so nothing was started, nothing is half done, and there are no clone2 batch 3 commits. That silence was wrong and it is recorded here as the user ordered, in the open.

Action from this minute: clone2 reads the batch 3 assignment from main now, assigns each batch 3 task to its own subagent, coordinates and synthesizes, then puts the work through a council of at least 3 reviewers plus an independent redteam check before reporting any task done, per the user process order of 2026-11-21 18:23. Batch 4, given by the user in chat today, starts only after batch 3 is finished, with its stated prerequisites checked first, files on todolist-push verified before any dependent task runs.

Status updates for batch 3 will be appended to this file per task, with commits, as they land. No blocker over 15 minutes will stay silent.

## ĐỢT 3 - 10 test thực tế khó (giao 17:00 ngày 21/11)

Làm sau khi xong đợt 2. Việc này vốn giao cho fcc nhưng nó chết 2 lần không ra file nào, nên tôi chuyển sang cho cậu.

Tạo tests/realistic/clone2-batch3/, 10 test mới, mỗi test 15-40 bước, fixture offline hoàn toàn, checker kiểm chứng DOM thật, không tự mô phỏng. Chủ đề, mỗi test một cái:
1. PDF form fill (điền form PDF, validate, submit)
2. Video player (play/pause/seek/volume/subtitle/playlist)
3. Keyboard-only navigation (chỉ dùng bàn phím đi hết flow, không chuột)
4. Drag-drop kanban (kéo thả thẻ qua các cột, lưu trạng thái)
5. Canvas drawing (vẽ, chọn màu, undo, lưu ảnh)
6. Chat app (gửi/nhận tin, typing indicator, search tin nhắn)
7. Map directions (tìm đường, đổi phương tiện, ước tính thời gian)
8. Shopping cart checkout (thêm hàng, mã giảm giá, thanh toán)
9. Code review diff (xem diff, comment từng dòng, approve/request changes)
10. Data dashboard (bảng số liệu, lọc, sort, export CSV)

Mỗi test: file .md spec (bước, kết quả mong đợi, thời gian), fixture HTML offline dưới fixtures/, README cách chạy. Commit nhỏ, push thường xuyên lên main. Xong thì báo vào file này, tôi giao tiếp.

## KIỂM TRA TIẾN ĐỘ - 18:05 ngày 21/11

Đã hơn 1 giờ kể từ lúc tôi giao đợt 3 (17:00) mà chưa thấy commit nào mới từ cậu trên main. Cậu đang làm tới đâu rồi, kẹt ở việc nào thì ghi rõ vào file này ngay, đừng im lặng. Quy tắc của tôi: im quá 15 phút không có tiến triển là phải báo. Nếu kẹt thì báo kẹt, tôi giao việc khác hoặc đổi hướng, đừng ngồi im. Push ngay những gì đã làm được, dù chưa xong.

## Clone2 bao cao dot 3, 2026-11-21 18:30

Trang thai that, khong che giau: dot 3 duoc giao luc 17:00, den 18:23 clone2 moi kiem tra va thay minh chua bat dau viec nao cua dot 3, 0 commit, 0 file. Sau bao cao dot 2 luc chieu, khong co phien clone2 nao nhan viec dot 3, nen clone2 im lang hon 1 gio. Loi nay la cua clone2, da ghi lai day du trong coord o PR 1, commit c936fcd.

Tu 18:30 clone2 bat dau dot 3 ngay: 10 test kho o tests/realistic/clone2-batch3, moi test giao mot subagent rieng lam doc lap, clone2 dieu phoi va tong hop, va truoc khi bao xong se qua council it nhat 3 nguoi cong redteam kiem chung doc lap, theo lenh moi cua chu du an. Xong dot 3 moi lam dot 4. Cap nhat tung test se ghi tiep vao file nay kem commit.

Tien do dot 3, cap nhat 18:40 ngay 21/11: xong 5/10 test, moi test mot subagent rieng, da commit len main tung test.
- test01 PDF form fill: PASS, 19 buoc, 32 check, 23.6972 s, commit 0b7a6a7.
- test02 video player: PASS 2 lan chay, 21 buoc, 32 check, 28.2941 s va 31.1248 s, commit 7088472.
- test03 keyboard only navigation: PASS, 21 buoc, 36 check, 14.978 s, khong dung chuot, commit 49f1a0d.
- test04 kanban drag drop: PASS 2 lan, 20 buoc, 17 check, 29.1275 s va 15.7999 s, commit 5035bc2. Luu y that: ActionChains drag that khong keo duoc the trong Firefox headless, 0/3, the duoc keo bang co che dispatch event cua fixture qua dung handler cua board, da ghi ro trong spec, khong che giau.
- test05 canvas drawing: PASS 2 lan, 26 buoc, 17 check, 8.8376 s, kiem chung pixel that, commit 91baf2a.
5 test con lai, chat, map, shopping, code review, dashboard, dang chay song song. Xong se chay lai toan bo bang run_all, roi qua council 3 nguoi va redteam truoc khi bao xong dot 3.

BAO CAO HOAN THANH DOT 3, clone2, 21/11, sau council va redteam.

Ket qua: tests/realistic/clone2-batch3 co 10 test kho, moi test mot subagent rieng lam doc lap, clone2 dieu phoi va tong hop. Tong 231 buoc. Chay toan bo bang run_all.py: 10/10 PASS. Lan chay tong hop cua clone2: 73.1844 s, wall 2026-11-21T11:31:53Z den 11:33:07Z. Sau cac sua chua cua council, chay lai toan bo: 10/10 PASS, 74.1993 s, wall 11:37:35Z den 11:38:49Z.
- test01 PDF form fill: 19 buoc, 32 check, commit 0b7a6a7.
- test02 video player: 21 buoc, 32 check, commit 7088472, sua tuong tac that o commit 7ee546e.
- test03 keyboard only navigation: 21 buoc, 36 check, commit 49f1a0d.
- test04 kanban drag drop: 20 buoc, 17 check, commit 5035bc2.
- test05 canvas drawing: 26 buoc, 17 check, commit 91baf2a.
- test06 chat app: 19 buoc, 42 check, commit 36a76ff.
- test07 map directions: 26 buoc, 17 check, commit d25a1bf.
- test08 shopping checkout: 27 buoc, 19 check, commit 46be5e1.
- test09 code review diff: 29 buoc, 16 check, commit 64309c8.
- test10 data dashboard: 23 buoc, 36 check sau khi them check CSV toan bo, commit ff90883.

Council 3 nguoi kiem chung doc lap: ca 3 deu chay lai phan duoc giao va ket luan SOUND hoac PASS cho ca 10 test, so buoc va so check khop chinh xac voi spec. Redteam doc lap: thu pha bang fixture gia sabotage, test08 FAIL dung nhu phai the khi SAVE10 bi lam hong, chung to checker bat duoc loi that. Ket luan redteam: khang dinh cua dot dung ve co ban, co 3 diem yeu da xu ly.

Da sua theo council va redteam truoc khi bao xong:
- test02: truoc day dat seek, volume, speed, subtitle bang script, chua khai trong spec. Da doi sang tuong tac that, Select class cho select va phim mui ten cho slider, test khong con execute_script, commit 7ee546e, chay lai 3 lan deu PASS.
- test01: ngay sinh dat bang script vi go phim vao date input headless phu thuoc locale, da khai ro trong spec, commit 48b1300. test05 sua so lieu data URL 3478 thanh 3474. test06 them method notes ve typing indicator va viec xoa o tim kiem.
- run_all.py: truoc day chi tin RESULT tu bao, nay bat buoc ca exit code 0, timeout ghi fail va chay tiep, commit 5a1f46d. test08 va test09: exception ngoai step nay lam fail test thay vi bi nuot. test10: check CSV so khop toan bo cac dong voi bang hien tai.

Gioi han con lai, khai that:
- test04: ActionChains drag that khong keo duoc the trong Firefox headless, 0/3, the keo bang dispatch event cua fixture qua handler cua board. Bang chung chi den muc xu ly event drag cua board, chua chung minh duoc keo tha bang con tro that. Da ghi ro trong spec.
- test05: undo va redo kiem chung bang bo dem stroke, chua lay mau pixel cho rieng hai thao tac nay.
- test06: typing indicator kiem chung qua bo dem cua fixture, da khai trong spec.
- test08: nhanh FREESHIP va nguong mien phi ship chua duoc kich hoat trong test. test09: file diff thu 3 va nhanh chan request changes khi khong co comment lan summary chua duoc test.
- Thoi gian trong spec la luc may ban song song nen cao hon luc chay ranh, redteam da xac nhan cung bac do lon va so buoc, so check khop tuyet doi.

Dot 3 xong. Dot 4 se lam tiep theo thu tu da giao.

Tien do dot 4, cap nhat 18:55 ngay 21/11: xong 5/6 task, da commit len main tung task, council 3 nguoi va redteam dang kiem chung.
- Task 2 agy-y2 live Firefox: 10/10 PASS, 179 action, 88/88 assertion, 68.838 s, commit 80c548a, bao cao docs/research/2026-11-21-agy-y2-live-firefox-run.md. Dieu kien Y7 da kiem tra truoc, co tren todolist-push o 9a74a70 va a07fd27.
- Task 3 fcc-k live Firefox: 10/10 PASS, 0 fail, tong 72,932.9 ms trong do khoi dong browser 37,763.3 ms, thoi gian thao tac thuan 29,672.2 ms so voi so tham chieu Zen cua Worker U la 28,613 ms, 383 buoc, 0 fail, commit dd59fb7.
- Task 4 Marionette raw: chung minh quy tac mot session, session thu hai bi loi session not created, ket noi TCP thu hai bi dong ngay khong handshake khi dang co session, xoa session xong tao lai duoc, commit f7de515, docs/firefox-multi-session-proof-20261121.md.
- Task 5 AT-SPI probe mo rong: ket qua am tinh va ghi that, may nay khong co daemon at-spi o bat cu dau, pyatspi khong cai duoc tu pip (404) hay apt (khong co candidate), Xvfb va bus rieng khoi dong duoc nhung khong doc duoc cay va khong an duoc nut that, commit bc88646.
- Task 6 evidence batch actions: 10 nguon moi, commit eb090c3, docs/research/2026-11-21-batch-actions-evidence.md.
- Task 1 chua xong: subagent bi co an toan cua he thong chan o ban clone phu dung de sua nhanh PR 1, chua dung gi vao code. Clone2 da hoi nguoi dung chon cach di tiep ngay trong chat, dang cho tra loi. Chan doan 2 loi da xong tu code doc duoc.

Bao cao dot 4, phan da xong, 21/11: task 2 den 6 da qua council 3 nguoi va redteam, task 1 con cho nguoi dung chon cach di tiep.
- Council nguoi 1: task 2 va 3 VERIFIED, moi con so trong hai bao cao khop chinh xac voi file ket qua tho, chay lai diem test03 agy-y2 va test08 fcc-k deu tai lap dung ket qua, negative control co that trong code.
- Council nguoi 2: task 4 va 5 VERIFIED, chay lai script Marionette tai lap ca 11 ket qua, chay lai probe AT-SPI tai lap tung stage voi thoi gian gan nhu trung khop.
- Council nguoi 3: task 6 VERIFIED, doi chieu truc tiep 7 tren 10 nguon, moi con so khop voi nguon goc, quet ve sinh sach, khong dau gach dai, khong thong tin ca nhan. Mot luu y nho: bai Beyond Browsing ghim so lieu ban v1, ban moi nhat v3 co so khac, doc dung cho ban da ghim.
- Redteam: khang dinh task 2, 3 va 4 dung nguyen. Task 5 co mot sua chua quan trong da ghi vao doc: cau "apt khong co candidate" chi dung voi apt lists rong cua may nay, mirror azure.archive.ubuntu.com that ra co day du at-spi2-core 2.52.0, python3-pyatspi 2.46.1, python3-gi va gir1.2-atspi. Cho chan duy nhat la hoan tat apt-get update, can phe duyet ma hai lan het thoi gian cho, va cai dat. Duong mo khoa da co bang chung, ghi o commit sua chua cua doc AT-SPI.
- Task 1 van cho: can nguoi dung chon cho phep xu ly ban clone phu bi co an toan, hoac lam ngay trong repo chinh. Chan doan 2 loi da xong. Khi co lua chon, clone2 lam not task 1 va bao cao rieng.


## NHIỆM VỤ MỚI: WATCHDOG 10 PHÚT + TIẾP TỤC DỰ ÁN (giao 19:09 ngày 21/11)

Tôi là Phạm Tuấn. Thêm một nhiệm vụ chạy song song với việc dự án của cậu, không thay thế việc đó.

### Watchdog: canh tất cả subagent mỗi 10 phút

Cứ mỗi 10 phút, cậu kiểm tra một vòng:
1. Tất cả subagent còn sống không: subagent của chính cậu, và các lane khác nhìn được qua GitHub (commit mới trên todolist-push là các worker Muse của tôi, commit mới trên main là clone1 và cậu, PR và issue mới). Cậu không nhìn được danh sách subagent trong máy của Muse tổng, nên cậu canh bằng dấu vết để lại trên GitHub, đó là cách duy nhất của cậu, ghi rõ giới hạn này trong báo cáo.
2. Muse tổng (Muse điều phối, chính là ông Muse chính) có nhắn gì mới không: kiểm tra coord/clone2.md và coord/clone1.md có commit mới nào từ Muse không, có issue mới không. Có chỉ thị mới thì làm ngay, báo lại vào file này là đã nhận.
3. Lane nào im hơn 30 phút trong khi việc chưa xong thì ghi cờ STALL vào file này, kèm bằng chứng: lane nào, commit cuối lúc nào, việc gì đang dở. Không cần chờ đủ 1 giờ mới báo như trước nữa.

Ghi kết quả mỗi lần kiểm tra vào file này hoặc một file log riêng docs/clone2-watchdog-log.md, ngắn gọn: giờ kiểm tra, lane nào sống, lane nào im, có chỉ thị mới nào không.

Clone1 cũng đã nhận nhiệm vụ watchdog này từ chính tôi rồi. Hai đứa cùng canh, đừng ỷ lại nhau.

### Tiếp tục dự án

Goal, todolist, quy trình Lauren Tan, final test đều đã có hết rồi, cứ làm hết đi là thành công, không cần hỏi lại. Goal quan trọng nhất: fix hết tất cả lỗi trong file tổng hợp lỗi để các Muse dùng computer-use hầu như không trượt, nghĩ nhanh, tổng thời gian task rút gọn vài lần, overlay không nhấp nháy nữa. Todolist đang 112/115. Thí điểm A1 đã đóng băng, chờ lệnh chạy. Final test (tự tạo contest riêng trên nick Codeforces của tôi, up 5 đề) chạy CUỐI CÙNG, sau khi xong hết mọi việc khác.

### Quy tắc commit mới: nhỏ và NHIỀU

Từ giờ commit nhỏ và nhiều lên, vài trăm commit càng tốt. Mỗi bước nhỏ xong là commit ngay, push ngay, đừng dồn lại rồi push một cục. Làm ngầm rồi mới push một loạt là không được nữa. Quy tắc này áp cho mọi việc cậu làm từ giờ.

Task 1 dot 4 HOAN THANH, clone2 lam truc tiep sau khi nguoi dung xac nhan, 21/11:
- Loi 1 da sua, commit ba7900a tren nhanh PR 1: nhanh selftest fail trong main() nay dat summary["ok"] = False, dung hop dong docstring cua mode auto. Kiem chung hanh vi: gia lap live ok cong selftest fail cho exit code 1, live fail cong selftest ok cho exit code 0.
- Loi 2 da sua, commit 83d55ae: press_button raise RuntimeError khi do_action tra False. Kiem chung: node gia co do_action tra False thi press_button raise that, truoc day step van pass.
- Chay lai: selftest ok true, total 0.0003 s, wall 2026-11-21T15:28:42Z. Auto: live fail dung nhu thuc te may nay, ModuleNotFoundError pyatspi, selftest ok true, tong 0.0004 s.
- Trial merge PR 1 voi main moi nhat: chi xung dot 1 file coord/clone2.md, ghep noi ca hai phia la xong, cay sau merge chay selftest ok true. Trial merge khong push. Trang thai GitHub cua PR 1 hien la CONFLICTING vi chinh file coord nay, ngoai ra khong co xung dot code nao. Merge that chi can giai quyet coord/clone2.md.
- Muc 3 cua clone1 ve find_widget khop dung ten la ghi chu, khong phai loi bat buoc sua, clone2 ghi nhan chua sua.
Dot 4 nhu vay xong ca 6 task.

## Batch 5 - dot manh (22:32 21/11, toi giao)

Clone2, toi can cau dot manh token hon, viec truoc nhe qua roi. Lam 3 viec nay, chat luong tren het, council + redteam cho moi ket luan, commit nho va nhieu, push ngay khi xong tung phan. Batch 4 xong het ca 6 task roi, tot; 3 viec duoi day la rieng biet, lam tiep di.

### Task 1 - crawl lai toan bo repo tim loi sot
Doc het improvements/, docs/, todolist, file tong hop loi tren repo. Tim moi loi hay viec nao todolist chua co, doi chieu tung claim voi bang chung (file/dong). Bao cao vao docs/clone2-repo-crawl-20261121.md.

### Task 2 - chay mu cac kich ban test nguoi dung pho thong tren Zen
Khi ZT-A commit xong improvements/zen-ordinary-user-tests-20261121.md tren todolist-push, lay file do ve, chay tung kich ban tren Firefox cua cau (chay mu, khong sua de truoc khi chay). Ghi lai moi loi voi anh chup + thoi gian vao docs/clone2-zen-ordinary-user-run-20261121.md.

### Task 3 - kiem tra evidence contract doc lap
Chay full test suite tren may cau, kiem tra cac commit moi nhat tren todolist-push co du bang chung chay duoc khong (lenh test, output, commit hash, log thoi gian). Vi pham nao ghi ro commit/file/dong vao docs/clone2-evidence-check-20261121.md.

Luat nhu cu: khong dua thong tin ca nhan nao cua toi len repo, khong dau gach ngang dai, khong ydotool, test nao cung ghi thoi gian. Ket qua bao cao vao file nay.

## Da nhan batch 5, 22:39 ngay 21/11
Clone2 da nhan batch 5 (commit c77e8a1): task 1 crawl repo tim loi sot, task 2 chay mu kich ban Zen nguoi dung pho thong, task 3 kiem tra evidence contract. File ZT-A improvements/zen-ordinary-user-tests-20261121.md da co tren todolist-push. Clone2 se lam ngay, council + redteam cho moi ket luan, commit nho va push ngay tung phan.

## Bao cao clone2: E1 (3.4.1) va G14 (2.1.10) HOAN THANH, 21/11

Ca hai muc todolist con mo ma may clone2 lam duoc da xong, qua council 3 nguoi va redteam:

- 3.4.1 E1, commit d1e1054, f9f796c, a1dbcf3, 6c15501, 4c59744, doc docs/research/2026-11-21-e1-planning-vs-execution.md, code tests/exp341/. Ba arm chay that tren Firefox, 6 task, checker chung. Ket qua da sua theo council va redteam: arm A nhu da viet can 9 retry, arm B 0 retry nhung executor khong co duong retry va plan doc tu source fixture, arm A-prime (agent xen ke doc quan sat day du, gom gia tri field va data-action cua nut) dat 18/18 sach, 0 retry, 29 action, hoa B ve do chinh xac. Ket luan dung: doc toan bo DOM truoc khi ra tay moi chua loi truot, o ca hai kien truc; plan thang that o so lan quan sat, 18 so voi 36 cua A-prime, quan trong khi moi lan quan sat ton mot lan goi mo hinh. Kien nghi lai: plan tu mot lan doc DOM giau, thuc thi theo lo checkpoint thua, giu hoi phuc theo quan sat. Loi harness run_all ghi crash thanh 0 da sua, 36 lan chay ghi lai khong bi anh huong.
- 2.1.10 G14, commit 4b798c3 va 9568a49, doc docs/research/2026-11-21-g14-heldout-real-app.md, code tests/heldout_g14/. App that chua tung dung trong repo: Swag Labs tren saucedemo.com, agent moi doc lap, dinh vi bang ngu nghia DOM, khong toa do. Cap so trung thuc: lan cham dau tien 0.8636 (38/44, loi o nut Continue vi app render bang input submit), sua locator tong quat mot lan roi chay lai toan bo dat 5/5 task, 43/43 action, hit rate 1.000, tong 74.181 s. Council 3 nguoi SOUND ca ba, redteam tai lap duoc ca che loi lan 1 va xac nhan harness khong an gian miss.
- Hai muc con mo con lai khong nam o may clone2: 2.1.7 can file video goc tren may nguoi dung, 2.2.3 can may nguoi dung de nap plugin vao Hyprland dang chay. Clone2 ghi ro de Muse tong quyet, khong im lang bo qua.
- Batch 5 dang chay: 3 task, moi task mot subagent rieng, bao cao rieng khi xong.
Pham Tuan: them mot luu y: graph GitHub cua toi hom nay moi co 136 contribution, can cham 240 truoc khi het ngay (tinh theo ngay UTC, het luc 07:00 sang mai gio VN). Commit NHIEU hon nua va NHO hon nua: moi buoc nho la mot commit rieng, push ngay khi xong, dung don lai. Ap dung cho moi viec dang lam.

## Da nhan luu y commit nho va nhieu, 22:58 ngay 21/11
Clone2 da nhan luu y graph 136 can cham 240 truoc 07:00 sang mai gio VN (commit e37a3bf): commit nho va nhieu hon nua, moi buoc nho la mot commit rieng, push ngay khi xong, dung don lai. Clone2 ap dung cho batch 5 dang chay va moi viec sau nay.

## Bao cao clone2: Batch 5 HOAN THANH, 21/11

Ca 3 task xong, moi task qua council 3 nguoi va redteam doc lap, commit nho push rieng tung phan.

- Task 1, crawl repo tim loi sot, commit fe93a87, doc docs/clone2-repo-crawl-20261121.md. 16 finding, 2 HIGH. F1: pilot A1 dong bang van co 3 blocker, 13 loi lon, 12 loi nho, self-test in 17/17 trong khi cay chi co 16 case, redteam tai lap duoc ca 3 crash cua unblinder. F2: full suite chay 1494 test, 14 roi 21 failure tuy lan chay, 73 error on dinh; discovery dem 1525 test nhung 31 khong chay, 29 giai thich duoc do 2 class loi o setUpClass, 2 con lai chua tach rieng, 1525 tru 31 bang 1494. Council va redteam khong be duoc finding lon nao, cac sua so da ap dung truoc khi commit.
- Task 2, chay mu kich ban Zen nguoi dung pho thong, commit 3ba12bf (bao cao) va de0d3cb (51 anh chup, force-add vi .gitignore chan *.png), doc docs/clone2-zen-ordinary-user-run-20261121.md. Chay tren Firefox dung thay Zen, 22:46 den 23:22, 10 kich ban chay, 6 pass (4 sach, 2 co dieu kien), 4 fail, 1 khong ap dung (ZT-05 doi workspace, may nay khong co Hyprland). F-003 (selector Wikipedia doi dang), F-005 (size la radio chu khong phai select), F-006 (nut submit khong co type) deu xac nhan lai tren trang live. F-004 (click muc download khong mo tab moi) GIU NGUYEN la loi trinh duyet: redteam bao khong co toa do click nen phai ha xuong khong ket luan, nhung council 2 chung minh runlog co day du toa do, ca hai click (1390,108) va (1385,107) deu roi dung hang muc, bao cao da viet lai dung trinh tu nay va bo tu "double-click". F-001 (sidebar Zen) xoa mot phan: tab hien du ten va click doi tab duoc, nua con lai (nut thu gon) doi chay tren laptop. F-002 van mo. Segfault Firefox cu khong tai lap: khong crash, khong minidump, nhung trigger cua loi cu khong co trong tai lieu nen chi ghi "khong thay crash khi mo dong tab".
- Task 3, kiem tra evidence contract, commit f2ca7e1, doc docs/clone2-evidence-check-20261121.md. Full suite tren may nay: Ran 1494 test, 16 failure, 73 error, 17 skipped, 1388 pass. Tim duoc 2 bug that tren main: tests/test_cursor_session.py loi SyntaxError o dong 566 lam ca module khong import duoc (van con tren main, clone2 tu kiem tra lai bang py_compile), va scripts/cu.py bien cuc bo run che ham run() nen doctor ime probe luon fail (da duoc sua tren main boi commit 22b0fa3). 20 commit moi nhat tren todolist-push: 19 COMPLIANT, 1 PARTIAL. Claim "vi pham nang nhat" ban dau la SAI va da sua: file log F2 da co tren todolist-push chi 81 giay sau luc agent fetch, so lieu khop dung. Bao cao can sua 6 cho theo council va redteam, da sua het truoc khi commit.
- Hai bug tren main la ung vien sua tiep theo cho Muse tong quyet, sua chung khong nam trong batch 5.
- Watchdog 10 phut van chay, log o docs/clone2-watchdog-log.md. Clone1 STALL tu 22:41, batch 6 chua co commit nao, da bao len chat luc 23:18 va nhac trong coord/clone1.md.
## Batch 6 - kiem tra 2 bug + review F1/F2/F3b + go conflict PR #1 (00:01 22/11, toi giao)

Clone2, batch 5 xong roi, tot. Bay gio lam batch 6.

### Task 1 - kiem tra 2 bug tren main roi moi sua
- Bug 1: SyntaxError trong tests/test_cursor_file.py (bao cao f2ca7e1 noi la bug that tren main). Toi vua kiem tra tren main fd77c0d: py_compile OK, khong co loi. Cau kiem tra lai: loi cau thay o file nao, dong nao, commit nao; neu tai hien duoc thi sua, neu khong thi ghi ro la da het hoac bao cao sai.
- Bug 2: shadow-run trong scripts/cu.py. Fix 22b0fa3 da co tren main roi, cau xac nhan lai va dong muc nay.
Bao cao vao docs/clone2-batch6-bugfix-20261122.md, ghi ro tung bug: con loi hay da het, bang chung, commit fix neu co.

### Task 2 - review doc lap diff F1/F2/F3b
Doc ky diff cua F1 (guardian fix), F2 (act-now), F3b (slot heal) tren todolist-push, council + redteam, ghi nhan xet vao docs/clone2-f-team-review-20261122.md.

### Task 3 - go conflict PR #1
coord/clone2.md dang conflict tren PR #1, go cho sach.

Luat nhu cu: khong dua thong tin ca nhan nao cua toi len repo, khong dau gach ngang dai, khong ydotool, test nao cung ghi thoi gian. Ket qua bao cao vao file nay.

## Da nhan batch 6, 00:49 ngay 22/11
Clone2 da nhan batch 6 (commit 41e09a6): task 1 kiem tra 2 bug tren main roi moi sua, task 2 review doc lap diff F1/F2/F3b, task 3 go conflict PR #1. Clone2 lam ngay, council + redteam cho moi ket luan, commit nho va push ngay tung phan.

## Bao cao clone2: Batch 6 HOAN THANH, 22/11

Ca 3 task xong, moi task qua council 3 nguoi va redteam doc lap, commit nho push rieng tung phan.

- Task 1, kiem tra 2 bug, commit fix 9171773 va bao cao cf3f6de, doc docs/clone2-batch6-bugfix-20261122.md. Bug 1: Muse tong kiem tra nham file, test_cursor_file.py thi py_compile OK that, loi that nam o test_cursor_session.py dong 570, van con tren main luc kiem tra. Nguyen nhan do duoc: CPython 3.12 gioi han 20 block long nhau, method test_cleanup_exceptions_cannot_skip_restore long 21 (for 1 + outer with 18 item + inner with 2 item). Sua toi thieu bang cach tach inner with ra helper _guardian_case_with_native_indicator, giu nguyen thu tu patch va assertion, ca module chay lai 34 test OK (skipped 1). Bug 2: da sua tu truoc boi 22b0fa3, kiem tra lai truoc/sau: truoc sua 5 loi dung kieu 'ArgumentParser' object is not callable, sau sua 13/13 pass. Dong muc. Council 3 nguoi SOUND ca ba, redteam pha 3 lan khong pha duoc, chi co 2 ghi chu trinh bay nho (thu tu thoi gian truoc/sau) da sua truoc khi commit.
- Task 2, review doc lap F1/F2/F3b, commit f99ac12, doc docs/clone2-f-team-review-20261122.md (407 dong). Ket luan: F1 SOUND, F2 SOUND, F2b SOUND, F3b SOUND (chi bang chung), khong gi BROKEN. Tu chay lai: F1 test_cursor_theme 35 OK, test_cursor_session 36 OK, wrapper 3 OK, sync 9 OK; F2 test_first_action 46 OK, test_overlay 12 OK; F2b 12.262 s, 5/5 action; full suite tren tip todolist-push 8bdd5aa: Ran 1634 test, 4 failure, 68 error (giam tu 14-16 xuong 4, phan lon do thieu binary wtype). Loi BLOCK D1 da sua o 1c6344e/4c32fc4, re-review GO. File ban dau bi cat cut giua chung o dong 229 va thieu muc coverage, council va redteam deu chan lai, da sua xong truoc khi commit: viet lai duoi F3b tu log goc, them muc coverage, sua dong "still broken on main" thanh da sua boi 9171773. Crawl F1 HIGH (pilot A1) khong ai dung toi, van mo.
- Task 3, go conflict PR #1, merge commit 1d25d2e tren nhanh coord-clone2-setup. Chi xung dot coord/clone2.md, go bang hop ca hai phia, khong xoa gi, selftest AT-SPI van pass. Sau do Muse tong da merge PR #1 luc 01:06, commit d322cd7.
- Watchdog 10 phut van chay, log o docs/clone2-watchdog-log.md. Clone1 STALL tu 22:41 ngay 21/11, batch 6 chua co commit nao, da nhac trong coord/clone1.md va bao len chat.

## Batch 7 - kiem tra 13 vi pham + grounding DOM/a11y nhanh (02:08 22/11, toi giao)

Clone2, batch 6 xong roi, tot. Bay gio lam batch 7, 3 viec. Goal chung cho moi viec: mot vision lam duoc nhieu thao tac nhat, tong thoi gian giam toi da, do chinh xac tu 90% tro len. Council 3 nguoi + redteam cho moi ket luan, commit nho va nhieu, push ngay khi xong tung phan.

### Task 1 - kiem tra doc lap 13 vi pham cua clone1
Clone1 tu audit thay 13 vi pham (docs/clone1-evidence-audit-full-20261121.md, commit 581736e 01:45 22/11): 3 HIGH (V1 thieu file gate H3, V2 F3 dan 9 log khong ton tai, V3 thieu bang chung cham 130/130), 5 MEDIUM, 5 LOW. Cau kiem tra doc lap tung vi pham mot: dung hay sai, bang chung file/dong. Bao cao vao docs/clone2-violation-verify-20261122.md, ghi ro tung vi pham: giu nguyen / bac bo, ly do, bang chung.

### Task 2 - nghien cuu grounding DOM/a11y nhanh cho Firefox/Zen
Tim cach lay toa do chinh xac tu DOM/a11y thay vi doc anh JPEG: BiDi/CDP/AT-SPI, rect chinh xac, mot observation cho nhieu action, verify re khong can observe lai. Bao cao vao docs/clone2-dom-grounding-20261122.md, kem so do duoc tren may cau neu co (thoi gian, do chinh xac). Day la y kien doc lap thu hai, ben canh dan crawl cua Muse tong. Cai last30days-skill (npx skills add mvanhorn/last30days-skill -g) tren may cau va dung no de research, chi dung data that 30 ngay gan nhat, moi claim ghi nguon + ngay.

### Task 3 - sua cac vi pham HIGH da xac nhan
Sua cac vi pham HIGH ma Task 1 xac nhan la dung. Neu khong co HIGH nao dung, lam G29 thay the: click vao thanh dia chi Zen roi dung diem nhung khong focus, tim nguyen nhan va sua, test live tren Firefox cua cau. Bao cao + commit sua, council + redteam.

Luat nhu cu: khong dua thong tin ca nhan nao cua toi len repo, khong dau gach ngang dai, khong ydotool, test nao cung ghi thoi gian. Ket qua bao cao vao file nay.

## Bao cao clone2: Batch 7 HOAN THANH, 22/11

Ca 3 task xong, moi task qua council 3 nguoi va redteam doc lap, commit nho push rieng tung phan.

- Task 1, kiem tra doc lap 13 vi pham cua clone1, commit ebf6ec8, sua so eec3056, doc docs/clone2-violation-verify-20261122.md (194 dong). Ket qua: ca 13 UPHELD, 0 bac bo, 3 HIGH, 5 MEDIUM, 5 LOW, khop dung kiem ke cua audit. V6 manh hon audit: tai lap duoc crash B3a bang manifest gia, TypeError dung dong 226, exit 1. Council va redteam giu nguyen ca 13, chi sua 3 so nho: state.json 16 thanh 15, baseline V4 1359 thanh 1339, Y13g 51 thanh 50 o anchor.
- Task 2, nghien cuu grounding DOM/a11y nhanh, commit bench 79b75e7 va 47d5ee6, bao cao 3fd6986 va 455b6e8, doc docs/clone2-dom-grounding-20261122.md (402 dong), code tests/dom_grounding_bench.py. Do that tren Firefox 160.0.1: one-shot rect sweep 66 element, Marionette median 0.030 s, BiDi 0.006-0.054 s, khop nhau toi 5.7e-14 px; mot snapshot cho 5 click that, ca 5 trung, 3 lan chay; verify bang mot lan doc DOM 0.005-0.015 s; gioi han cung: Firefox chi cho mot session remote duy nhat tren mot trinh duyet, qua ca hai giao thuc. Council va redteam chan lai bao cao dau: so session.new BiDi 0.002-0.005 s la SAI, do that 1.51-2.77 s tren trinh duyet moi, 0.014 s khi am; "three full runs" la sai, chi co 2 full + 1 partial crash KeyError; so a11y khong co bang chung. Da sua het: them buoc do a11y vao bench, chay lai 2 run day du (run 4, run 5, log o /tmp), tinh lai bang median tu log, sua kich thuoc screenshot 1280x814 va ngay agent-desktop 27-28/10. last30days-skill KHONG cai duoc: lenh npx treo 25 phut o prompt chon agent, chay lai thi installer bao Critical Risk ca 3 scanner (Gen, Socket, Snyk) va dung o xac nhan, clone2 khong xac nhan, khong ghi gi vao may. Research thay bang web search gioi han 30 ngay, moi claim ghi nguon + ngay. Quyet dinh cai bat chap canh bao la cua Muse tong.
- Task 3, sua 3 vi pham HIGH, bao cao 5777535 tren main, doc docs/clone2-batch7-high-fixes-20261122.md. Ca 3 PARTIALLY FIXED, khong bia gi: V1 sua ho so trong repo bang append co ngay vao F1 log (05ee34d), ban ghi chap thuan H3 van thieu, chi Muse tong ghi lai duoc; V2 sua F3b log (748cc35), phat hien that ra thieu 14 log chu khong phai 9, log chi lay duoc tu laptop; V3 sua live-test-log (219720c), verdict 130/130 la UNVERIFIABLE tu bang chung trong repo, chi con tom tat inline. Council va redteam SOUND ca 4, chi sua mot khung nho (relaunch-f3b.log thuoc STEP 3, commit 177c85a).
- Watchdog 10 phut van chay, log o docs/clone2-watchdog-log.md. Clone1 song lai luc 01:39 sau 177 phut im, xong batch 6 task 2.

## Batch 8 - xay script benchmark 2-vision + mo rong bench DOM 2 cua so + thu tuc probe C12 (03:05 22/11, toi giao)

Clone2, batch 7 xong roi, tot, council + redteam deu xac nhan. Bay gio lam batch 8, 3 viec. Goal chung cho moi viec: mot vision lam duoc nhieu thao tac nhat, tong thoi gian giam toi da, do chinh xac tu 90% tro len. Council 3 nguoi + redteam cho moi ket luan, commit nho va nhieu, push ngay khi xong tung phan.

Luu y ve last30days-skill: DUNG cai bang npx skills add -g. Installer bao Critical Risk ca 3 scanner, toi dang tu doc source de quyet dinh, chua co verdict thi khong ai duoc click qua xac nhan. Viec nao can claim tu web thi dung web search gioi han 30 ngay gan nhat, moi claim ghi nguon + ngay.

### Task 1 - xay script/workflow cho benchmark 2-vision (chi xay, KHONG chay live)

Benchmark la bai kiem tra nghiem thu, chi chay sau khi cach cai tien duoc duyet xong va toi bao chay. Viec cua cau bay gio la xay san script + workflow, khong chay live.

Script lam theo thiet ke tong hop (doc improvements/worker-coord-click2-log.md tren nhanh todolist-push, muc "The combined design"): VISION 1 lay inventory bang one-shot bulk DOM harvest cho ca hai cua so clone (mot evaluate tra ve ref, role, name, rect, center, visibility, focused cho moi input + button), dinh dang numbered compact text; script chay chuoi gui cho ca hai clone (click input clone1, go, Enter, click input clone2, go, Enter) voi guard kieu HCU (kiem tra lai geometry + focus truoc khi nhap, dung o loi dau tien, phan sau bao not-executed), exactly-once intent cho moi tin (retry khong duoc gui trung), gate V12 (kiem tra bubble da gui trong DOM thread) sau moi tin, cham bang outcome (tin da vao thread hay chua), khong cham bang point-in-box. Ghi ro cac gap da biet (F5/D1-D6 trong log tong hop: bulk harvest chua xay xong, chua co ledger exactly-once, chua co gate V12, chua co co che handover BiDi/Marionette, step-6 loop hygiene chua co chu) thanh TODO trong script, se sua sau vong review.

Deliverable: script + file workflow mo ta tung buoc, cac lenh chay, cach truyen inventory vao, cach doc ket qua. Test kho tren fixture (headless Firefox neu duoc), khong dong vao laptop cua toi, khong nhan vao thread that.

### Task 2 - mo rong bench DOM sang dang 2 cua so cua benchmark

Tiep noi Task 2 batch 7 cua cau (one-shot rect sweep 66 element, Marionette median 0.030 s, BiDi 0.006-0.054 s, khop nhau toi 5.7e-14 px, 5 click tu mot snapshot deu trung). Bay gio do dang 2 cua so: hai cua so/tab headless Firefox, moi cua so mot lan one-shot harvest, do thoi gian harvest moi cua so, do chinh xac click, do thoi gian verify bang mot lan doc DOM. So sanh ground_many cua amend (3N evals) voi one-shot (1 evaluate) tren cung fixture, ghi so cu the. Giu nguyen do nghiem ngat nhu batch 7 task 2: ghi may, trinh duyet, log tho, council + redteam tu kiem tra truoc khi commit (ban nhap dau batch 7 cua cau tung bi chan lai vi so session.new BiDi sai, so run sai, thieu bang chung a11y, dung de lap lai). Bao cao vao docs/clone2-dom-bench-2win-20261122.md, kem code bench.

### Task 3 - viet thu tuc probe live cho C12 (chi viet thu tuc, khong chay live)

Council C1/C2 deu ket luan C12 CHUA xong: code amend (zen_dom.py viewport_origin) coi mozInnerScreenX/Y la toa do man hinh tuyet doi, trong khi bao cao calibration-e2 noi no la toa do tuong doi cua so (240, 8). Can mot probe live tren laptop de phan xu: doc mozInnerScreenX/Y, doc window origin tu hyprctl, click that bang dom_act. Lane live luc nay dang ban (BASELINE2 dang chay), nen cau chi viet thu tuc, khong chay.

Doc code amend (viewport_origin, dom_rect_to_image_point tren nhanh todolist-push) tren giay, roi viet file docs/clone2-c12-probe-procedure-20261122.md gom: tung buoc lenh cu the, bang ket qua ky vong cho ca hai truong hop (mozInnerScreen tuyet doi vs tuong doi cua so), luat quyet dinh (truong hop nao thi C12 xong, truong hop nao thi phai sua code the nao), va cac bien can ghi (DPR, window origin, sidebar width, URL bar height). De Muse tong hoac worker khac chay ngay khi lane ranh.

Luat nhu cu: khong dua thong tin ca nhan nao cua toi len repo, khong dau gach ngang dai, khong ydotool, test nao cung ghi thoi gian. Ket qua bao cao vao file nay.

### Task 4 - CANCELLED: review last30days da xong boi Muse tong (verdict CLEAN)

Task review nay HUY, khong lam nua. Muse tong da tu doc source xong (repo HEAD f5d0e44, SKILL.md v4.5.0), verdict CLEAN: moi outbound host deu la provider hop le co ghi trong tai lieu, khong eval/exec/os.system, khong obfuscation, khong exfiltration host, khong install hook, MCP Go code khong phone home, box_chrome_login.py khong doc cookie nao va khong in gia tri cookie, setup-keychain.sh chi macOS Keychain, doc cookie can consent rieng, skill khong post/like/sua, khong log/cache API key. Critical Risk 3 scanner la false positive tu hanh vi da ghi trong tai lieu (browser session + nhieu API key + subprocess local nhu yt-dlp).

Thay bang Task 4 moi: cai skill last30days tren may cau (git clone repo roi dung tu clone, hoac copy thu muc skill tu ban cai cua Muse tong neu lay duoc, hoac npx skills add va tra loi prompt tuong tac vi lenh npx tran se treo o prompt). Sau do chay mot sweep 30 ngay bang skill cho chu de cua Task 2 (DOM grounding), chi dung data that 30 ngay gan nhat, moi claim ghi nguon + ngay. Bao cao sweep vao docs/clone2-last30days-sweep-20261122.md. Council 3 nguoi + redteam cho ket luan.

## Da nhan batch 8, 03:10 ngay 22/11
Clone2 da nhan batch 8 (commit b8cfe92 va 9260185): task 1 xay script benchmark 2-vision (chi xay, khong chay live), task 2 mo rong bench DOM 2 cua so, task 3 viet thu tuc probe C12 (chi viet, khong chay live), task 4 review source last30days-skill lam truoc nhat, khong click qua xac nhan installer trong bat cu truong hop nao. Clone2 lam ngay, task 4 truoc, council + redteam cho moi ket luan, commit nho va push ngay tung phan.

Muse tong 03:10: Task 4 review o tren HUY roi (verdict CLEAN cua Muse tong), clone2 doc Task 4 CANCELLED va lam Task 4 moi (cai skill + sweep 30 ngay), khong lam review nua.

## Da nhan Task 4 CANCELLED, 03:20 ngay 22/11
Clone2 da nhan lenh huy Task 4 review (commit 07a4a27, 03:16): review last30days-skill da co verdict CLEAN cua Muse tong, khong lam review nua. Task 4 moi la cai skill last30days tren may clone2 roi chay sweep 30 ngay cho chu de DOM grounding, bao cao vao docs/clone2-last30days-sweep-20261122.md, council + redteam. Ghi chu: agent review cu da xong va push truoc khi lenh huy toi (41af33a, verdict PROCEED, 03:19), trung voi verdict CLEAN cua Muse tong, nen chi con Task 4 moi chua lam, cho Muse tong dieu lai.

## Pham Tuan tra loi cau hoi cua clone2 ve Task 4, 03:31 ngay 22/11

Clone2, thay doi Task 4 trong batch 8 la that, do toi chi dao, khong phai gia mao. Ly do ro rang nhu sau.

Toi da ra lenh luc 03:04: doc source code repo last30days-skill, neu khong thay gi nguy hiem thi cu dung, toi khuyen khich dung. Roi luc 03:08 toi bao Muse tong lam nhanh roi tich hop luon. Muse tong da tu doc source xong (repo HEAD f5d0e44, SKILL.md v4.5.0), verdict CLEAN, skill da cai tren VM tai ~/workspace/custom-skills/last30days/, roi huy viec review lai cua cau vi review cua Muse tong da dung roi, khong can review lan nua. Viec huy Task 4 cu la lenh cua toi thong qua Muse tong, khong phai ai khac sua file.

Chinh review cua cau cung dong y voi verdict nay: cau da lam xong review, verdict PROCEED, commit 41af33a, file docs/clone2-last30days-review-20261122.md. Council va redteam cung dong y. Vay la 3 ben doc lap deu cung ket luan: skill sach, Critical Risk 3 scanner la false positive.

Task 4 moi van dung: cai skill last30days tren may cau roi chay sweep 30 ngay cho chu de DOM grounding, chi dung data that 30 ngay gan nhat, moi claim ghi nguon + ngay, bao cao vao docs/clone2-last30days-sweep-20261122.md. Cu lam tiep, khong can hoi lai.

## Da nhan xac nhan Task 4, 03:48 ngay 22/11
Clone2 da nhan xac nhan luc 03:31: thay doi Task 4 trong batch 8 la that, do Pham Tuan chi dao qua Muse tong, khong phai gia mao. Task 4 moi van dung: cai skill last30days tren may clone2 roi chay sweep 30 ngay cho chu de DOM grounding, bao cao vao docs/clone2-last30days-sweep-20261122.md, council + redteam. Ghi chu: Task 4 moi van chua co agent nao lam, cho Muse tong dieu lai.

## Bao cao clone2: Batch 8 HOAN THANH (4 task goc), 03:49 ngay 22/11

Ca 4 task goc cua batch 8 da xong, council 3 nguoi + redteam cho moi ket luan, commit nho va push ngay tung phan. Task 4 moi (cai skill + sweep 30 ngay) da duoc giao cho agent rieng luc 03:49, dang chay, se bao cao rieng khi xong.

### Task 1 - script/workflow benchmark 2-vision (chi xay, khong chay live)

Script tests/two_vision_bench.py (783 dong sau fix pass), fixture tests/two_vision_fixture.html + 3 fixture bien the (contenteditable, id-less, below-fold), driver exactly-once tests/two_vision_once_driver.py, workflow docs/two-vision-benchmark-workflow-20261122.md (379 dong). Commit: e864c5b (fixture), 072e060 (script), 9196744 (4 bug fix), f341563 (workflow), fix pass 7e81213 + 92ef65a, merge 87e5806.

Council: 1 ISSUES, 2 ISSUES, 3 SOUND. Redteam: BROKEN, 6 finding (3 critical). Tat ca da sua xong va kiem chung live tren headless Firefox 160.0.1, chi fixture local, khong chay live: (1) gate live chuyen sang kiem tra URL trong plan, khong phai flag, plan chua URL that bi tu choi exit 2, khong gui gi; (2) V1 check doc innerText cho contenteditable, value cho input thuong, fixture CE PASS 6.6076 s; (3) ref cho element khong id thanh duong CSS hop le (nth-of-type), fixture noid PASS 5.4565 s; (4) scroll truoc roi moi guard, fixture below-fold PASS 5.4953 s; (5) v12-timeout danh dau failed-unverified, lan chay sau cung intent bi chan retry, khong gui trung lan 2; (6) --instances two bi tu choi exit 2, khong ghi nhan nhu da chay. Con so 0.0026 s cho exactly-once da rut lai, thay bang driver chay lai (call 1 sent 0.5988 s, call 2 skipped-already-sent 0.0153 s, bubble van 1, PASS). Happy path chay lai PASS 8.4457 s, harvest-only 4.3510 s, stop-at-first-failure FAIL dung thiet ke 9.2775 s, live refusal van exit 2.

Su co: /tmp bi xoa giua chung khi fix pass dang chay, log fix pass dau tien mat het. Agent chay lai toan bo va luu log vao ~/workspace/tools/two_vision_fixpass/ (36 file). Log goc /tmp cho cac run truoc fix da mat, nhung council 1 va 2 da kiem chung cac so do tu log truoc khi mat.

### Task 2 - mo rong bench DOM sang 2 cua so

Bench tests/dom_bench_2win.py (7a71efc), bao cao docs/clone2-dom-bench-2win-20261122.md (e7b49ef, 325 dong), fix pass 4de8c0b (371 dong). 2 full run (22 step, 11.35 s va 11.08 s), Firefox 160.0.1 headless, 1 Marionette session, 2 cua so. One-shot harvest 66 element moi cua so: pooled median 0.0112 s. ground_many full inventory (65 selector, 200 eval): pooled median 0.5353 s, khoang 48x cham hon, 200x eval. 5 click moi cua so deu trung ca 2 run. Tim thay 2 gioi han that: ground_many strict that bai voi element duoi fold (name-input center y 1927.37 vs viewport 814), va scroll lam rect snapshot het han.

Council: 1 ISSUES (minor), 2 ISSUES (minor), 3 SOUND. Redteam: BROKEN o 1 claim, co che cua finding 2 (scroll lam het han rect) bi chung minh la khong the xay ra theo co che click cua bench. Fix pass viet lai finding 2 chi theo log quan sat, co che ghi UNKNOWN, bo han cau chuyen scroll bottom/top, giu nguyen fix re-read vi run 1 va 2 chung minh no dung. Cac sua nho khac: range per-selector 6.52 den 10.40 ms (10.48 ms thuoc run partial), verify batch 7 0.002 den 0.015 s, tham chieu section 1 va 6, ghi chu set A ban dau, trich dan day du clicked log, them ghi chu variance 2-run.

### Task 3 - viet thu tuc probe live cho C12 (chi viet, khong chay live)

Thu tuc docs/clone2-c12-probe-procedure-20261122.md (94db742, 386 dong), fix pass e51f538 (754 dong). Doc code amend tren giay truoc khi viet: viewport_origin() tra [mozInnerScreenX, mozInnerScreenY] va ghi la toa do man hinh tuyet doi, trong khi calibration-e2 noi la window-relative (240, 8).

Council: 1 SOUND, 2 ISSUES, 3 SOUND. Redteam: BROKEN, 7 finding (2 critical). Tat ca da sua xong: them Step 4b click 5 diem Case B khi Case A trượt hoac khong click duoc; muc 6 tach 2 nhanh (Branch 1 click Case A, Branch 2 hinh hoc E2 thi Case A khong click duoc, di thang Step 4b); them Outcome E; buoc 2 goi truc tiep viewport_origin() bang python3 heredoc, Outcome C viet lai; buoc 5 a11y viet lai bang lenh python3 -c day du; muc 7 nhúng driver click /tmp/c12_probe_click.py (102 dong, py_compile OK); Outcome B item (4) sua thanh suy lai fixture cho mo hinh window-relative, cam copy so E2; sua tham chieu va bookkeeping file commit.

### Task 4 (cu) - review source last30days-skill, verdict PROCEED

Bao cao docs/clone2-last30days-review-20261122.md (41af33a, 95 dong), fix pass 1678ee7 (101 dong). Review chi doc plain text, khong chay file nao, khong click qua xac nhan installer. Ket luan: Critical Risk la false positive ve y do doc hai. Khong co exfiltration, obfuscation, trom credential, hardcode secret, download-and-execute. Chay replica 50 rule CRITICAL cua Hermes cho 0 hit. Flag bat dung kha nang (doc va giai ma session cookie trinh duyet) nhung sai ve y do: tinh nang nay duoc ghi trong tai lieu, mac dinh tat, tu choi ro rang thi thang, chi doc dung 2 cookie X / 1 cookie Reddit / 1 cookie Truth Social, gia tri khong log khong luu. Phat hien them: chuoi curl pipe shell cu con sot trong CHANGELOG.md:819 (tai lieu lich su, skill dir da sach tu fix #1502). Dieu kien kem verdict: mac dinh khong bat cookie trinh duyet, dung X API chinh thuc hoac Grok CLI; verdict PROCEED khong cho phep tu cai -g, quyet dinh cai la cua Muse tong.

Council: 3x SOUND. Redteam: SOUND, PROCEED dung. Fix pass sua 9 muc nho (ghi nhan Hermes thang 07/2026 vs thang 11/2026, so module lib 130 khong phai 170, duong dan pyproject.toml o repo root, trich dan npm i -g, siet lai cach viet 0 eval / 0 secret / re.compile, them luu y luong du lieu rerank va luat Grok Bot chi kich hoat khi khai LAST30DAYS_HOST). Verdict PROCEED giu nguyen, trung voi verdict CLEAN cua Muse tong, 3 ben doc lap cung ket luan.

### Task 4 moi - cai skill + sweep 30 ngay (dang chay)

Pham Tuan xac nhan luc 03:31: thay doi Task 4 la that, do anh chi dao qua Muse tong, lam tiep khong can hoi lai. Clone2 da giao task 4 moi cho agent rieng luc 03:49: cai skill last30days tren may clone2 (uu tien git clone roi dung tu clone), chay sweep 30 ngay bang skill cho chu de DOM grounding, chi dung data that 30 ngay gan nhat, moi claim ghi nguon + ngay, bao cao vao docs/clone2-last30days-sweep-20261122.md, council + redteam. Se bao cao rieng khi xong.

### Task 4 moi - HOAN THANH, 04:05 ngay 22/11

Task 4 moi da xong: cai skill bang git clone (HEAD ef01dab, SKILL.md v4.5.0, hon ban da review f5d0e44 dung 1 commit, diff chi them tinh nang TikTok public-comments), chay 3 luot sweep cho chu de DOM grounding, bao cao docs/clone2-last30days-sweep-20261122.md (e680aad, 205 dong), council 3 nguoi + redteam xong, fix pass bd8fbdf (261 dong, merge a320a3e).

Ket qua chinh: Turbo-Browser-MCP (Show HN 2026-11-15, repo tao 2026-11-14, 136 sao) lam dung hinh dang thiet ke ket hop: snapshot chi phan thay doi, batch action kem kiem tra ket qua, co che chong gui trung bang submissionKey, chot chan submit mac dinh bat, bao cao sau moi click. Chromium/CDP only nen driver khong chuyen sang Zen, chi lay duoc 3 co che de ap vao thiet ke cua minh. So benchmark cua no UNVERIFIED o day. Xac nhan doc lap: BotCircle issue 8 (2026-10-22) ghi dung loi click mu vi grounding toa do chua kiem chung, sua bang cach giong amend cua minh, DOM va accessibility truoc, toa do sau cung.

Council: 1 ISSUES, 2 ISSUES, 3 ISSUES. Redteam: SOUND, 4 finding. Fix pass sua het: (1) run 3 GitHub status la no-results, khong phai ok, ca 2 ket qua run 3 chi tu Hacker News, Turbo-Browser-MCP dung tren HN mot minh; (2) diff them truc tiep call toi www.tiktok.com/api/comment/list/, bat mac dinh, ghi ro khong dung tu class de che, sua duong dan file, ghi ro engine co ghi state vao ~/.config/last30days; (3) run 1 thoi gian chi la agent-reported, run 2 va 3 dung 12.8 s theo engine in, 2 luot chay song song; (4) bo sung 3 item noise run 1 con thieu; (5) submissionKey chi exactly-once khi call tra ve, neu throw sau khi gui thi ledger trong va chay lai se gui trung, ledger chi o 1 may.

## Batch 9, giao 04:35 ngày 22/11 (Muse điều phối, lệnh của tôi)

Batch 8 xong hết, task 4 mới (cài skill + sweep 30 ngày) xong 04:05, báo cáo e680aad. Làm tiếp batch 9, 4 việc, mỗi việc council 3 người + redteam, commit nhỏ push ngay từng phần, làm hết ga hết số, dùng hết token cần dùng, không tiết kiệm.

### Việc 1 - Thiết kế phương pháp one-vision từ kết quả sweep của cậu

Dựa trên sweep task 4 mới của cậu: Turbo-Browser-MCP (Show HN 2026-11-15) có 3 cơ chế áp được cho thiết kế của mình (snapshot chỉ phần thay đổi, batch action kèm kiểm tra kết quả, chống gửi trùng bằng submissionKey + chặn submit mặc định + báo cáo sau mỗi click), và BotCircle issue 8 (2026-10-22) xác nhận lỗi click mù vì grounding tọa độ chưa kiểm chứng. Viết docs/clone2-one-vision-design-20261122.md: ánh xạ 3 cơ chế đó sang stack của mình (Zen/Marionette, chuỗi tọa độ window-relative theo kết luận probe C12: screen = window origin Hyprland + mozInnerScreen + rect center), kèm sketch API cụ thể và một ví dụ làm việc đầy đủ cho bài benchmark 2-vision (ô nhập của cả hai clone). Ghi rõ cái nào lấy được từ Turbo-Browser-MCP, cái nào không (nó chỉ chạy Chromium/CDP, driver không chuyển sang Zen được).

### Việc 2 - Kiểm tra sẵn sàng live cho benchmark 2-vision, KHÔNG chạy live

Kiểm tra tests/two_vision_bench.py + tests/two_vision_once_driver.py + docs/two-vision-benchmark-workflow-20261122.md còn đúng trên main không, chạy lại toàn bộ fixture suite headless trên máy cậu, và viết checklist điều kiện tiên quyết cho lần chạy live (trạng thái workspace, chat của cả hai clone, nội dung tin nhắn chính xác, tiêu chí PASS/FAIL cho từng vision, điều kiện dừng). Bài chạy live là bài nghiệm thu của điều phối, cậu chỉ chuẩn bị, không tự chạy live.

### Việc 3 - Viết nháp mục lỗi G31

Muse tổng vừa nhắn tin trực tiếp cho cậu bằng chuột computer-use lúc 03:53:30, gửi được trong 4 phút 3 giây, 1/1. Nhưng lúc đọc ảnh để xác định ô nhập, mắt nó đọc sai 45px quá cao (nó đoán (307,1085), công cụ visual_grounding cho (306,1130)), cùng kiểu lỗi như CL1-MSG trước đó; nó bắt được trước khi click nhờ công cụ grounding. Viết nháp mục lỗi docs/g31-nearmiss-draft-20261122.md từ các số này: điểm click (306,1130), con trỏ sau click (1288,1144) cách điểm click 2px, gõ xong kiểm tra chữ trong ô nhập của cậu (ô nhập clone1 vẫn trống), Enter một phát gửi, bong bóng xanh đủ chữ trong thread. Kết luận: công cụ grounding là cách sửa, đọc bằng mắt là lỗi. Council + redteam duyệt nháp này.

### Việc 4 - Crawl data mới 30 ngày về cách kiểm chứng click không cần vision thứ hai

Dùng skill last30days đã cài trên máy cậu, crawl data thật trong 30 ngày qua: các agent kiểm chứng một cú click đã trúng đích bằng cách nào mà không cần chụp ảnh lần hai (đọc trạng thái DOM, kiểm tra caret/focus, đọc kết quả session). Chỉ dùng data thật 30 ngày gần nhất, mỗi claim ghi nguồn + ngày, không dùng dataset cũ kĩ. Báo cáo vào docs/clone2-ground-verify-sweep-20261122.md, council + redteam.

Luat nhu cu: khong dua thong tin ca nhan nao cua toi len repo, khong dau gach ngang dai, khong ydotool, test nao cung ghi thoi gian. Ket qua bao cao vao file nay.
