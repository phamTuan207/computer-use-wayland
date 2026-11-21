# BÁO CÁO CLONE1, ĐỢT 2 VÀ ĐỢT 3, 21/11/2026

Đợt 2 và đợt 3 giao ở commit cdc082f đã làm xong hết, 8 commit mới
trên main (7 commit việc cộng 1 commit xóa email, xem dưới). Mọi số
đo dưới đây là số thật đo trên máy clone1, chưa kiểm chứng thì ghi
UNVERIFIED. Không có thông tin cá nhân trong các file mới, 0 ký tự
gạch ngang dài trong toàn bộ file thay đổi và tạo mới.

## Bước 1 email, làm trước tiên, commit 1c7d252

- Đã xóa dòng 3288 khỏi improvements/live-test-log.md trên main và
  push ngay. File còn 4228 dòng, grep domain còn 0 kết quả.
- Địa chỉ vẫn còn trong lịch sử git từ commit a46b3c68 ngày 18/11,
  và ở đầu của 25 branch. Chỉ bước 2 mới xóa sạch được, xem đợt 3
  việc 5.

## Đợt 2 việc 1: Chạy 10 test realistic, commit 9a2e6dc

- Chạy thật: node tests/realistic/clone1/run_all.mjs, 10 passed,
  0 failed, wall clock 41534 ms (chậm hơn lần chạy 16.0 s lúc sáng
  vì lúc chạy load average 7.68, 9 agent chạy song song).
  Per-test: t01 5365, t02 2323, t03 2225, t04 5112, t05 5051, t06 5999,
  t07 3632, t08 4718, t09 3448, t10 3624 ms.
- Không lỗi nào: failures trống cả 10 test, stderr trống. Không có
  click miss, không stale observation, không timeout.
- Báo cáo tests/realistic/clone1/RUN-REPORT-20261121.md và log
  tests/realistic/clone1/RUN-LOG-20261121.jsonl (16 dòng, JSON hợp lệ).
- Bridge kiểm tra kèm: content_node_test.mjs 16 kiểm tra pass,
  0.570 s; test_webext_native_bridge.py 16 test pass, 12.212 s.
- UNVERIFIED: chạy trên Firefox thật và Zen thật, bridge trên
  trình duyệt thật. Lúc chạy việc này máy vẫn chưa có Firefox.
  Chú ý: việc 4 đợt 3 sau đó đã cài Firefox 160.0.1 ở /tmp/firefox,
  nên từ giờ máy này đã có Firefox để chạy test thật.

## Đợt 2 việc 2: 10 test mới, commit 9e156b9

- 37 file trong tests/realistic/clone1-batch2/: t01 PDF form,
  t02 video player, t03 keyboard-only navigation, t04 kanban
  drag-drop, t05 canvas drawing, t06 chat app, t07 map directions,
  t08 shopping cart checkout, t09 code review diff, t10 data
  dashboard filter/export. Mỗi test 15-40 bước, fixture offline,
  checker tự động.
- Chạy của agent: 10 passed, 0 failed. Kiểm tra lại của tôi:
  chạy full 1 lần được 9 passed, 1 failed ở t10-dashboard, lỗi
  "download.path: canceled" ở bước export CSV. Chạy riêng t10 thì
  pass, 1947 ms, 40 bước đầy đủ. Kết luận: t10 flaky khi chạy full
  dưới tải nặng, lỗi ở khâu download, không phải ở logic test.
  Cần chạy lại trên laptop hoặc cho test export chờ download chắc
  hơn, không nên ghi 10/10 tuyệt đối.
- UNVERIFIED: cùng 10 flow trên Firefox và Zen.

## Đợt 2 việc 3: Code Mode search/describe, commit 03fbbb7

- Đã đọc docs/research/2026-11-21-code-mode-integration.md và
  scripts/code_exec.py trước khi làm.
- scripts/codemode_search.py: search_ops(query) và describe_op(name)
  trên toàn bộ script trong scripts/, 60 op ở lần đo cuối (tăng từ
  59 lên 60 vì việc 4 đợt 2 thêm scripts/mcp_server.py trong lúc
  làm). Mỗi op chỉ có mô tả ngắn (tối đa 200 ký tự), tag, file,
  kích thước. describe_op thêm tên entry point và 6 dòng đầu,
  tối đa 800 ký tự, tổng dưới 2000 ký tự. Không bao giờ trả cả file.
  Có estimate_tokens (ký tự chia 4, ghi rõ là ước tính),
  measure_tokens, list_snippets, get_snippet, CLI search, describe,
  tokens, list, snippet.
- snippets/registry.json: 4 snippet P1-P4, lấy nguyên văn từ
  improvements/pick1-program-template.md, mỗi cái có mô tả, input,
  output mẫu. Thêm 4 file .py tương ứng và README. Kiểm tra round
  trip: registry khớp file .py từng byte.
- Test: python3 -m unittest tests.test_codemode_search
  tests.test_codemode, 40 test (19 mới cộng 21 cũ), tất cả pass,
  0.393 s. CLI đã chạy thật: search "dom locate" trả zen_dom đầu
  tiên, describe zen_dom trả thông tin ngắn có entry point.
- Token ước tính (ký tự chia 4, ghi rõ là ước tính), đo với 60 op:
  catalog đầy đủ dạng rút gọn 7292 ký tự, 1823.0 token ước tính.
  Sau search, giới hạn 5: "dom locate" 90.2 (tiết kiệm 1732.8),
  "session" 251.0 (tiết kiệm 1572.0), "polygon" 59.5
  (tiết kiệm 1763.5).
- Tài liệu docs/code-mode-search-describe.md.
- UNVERIFIED: không snippet nào chạy end to end qua code_exec.py
  (máy này không có cửa sổ terminal tên speed-pick1-term và không
  có Zen sống). Output mẫu là lệnh shell bên dưới chạy trực tiếp ở
  đây, không phải chạy chương trình đầy đủ.

## Đợt 2 việc 4: MCP server prototype, commit 98edc39

- scripts/mcp_server.py, 633 dòng, chỉ stdlib. MCP server nhỏ,
  newline-delimited JSON-RPC qua stdio, protocol 2024-11-05, tên
  computer-use-mcp v0.1.0. 8 tool: session_start, session_status,
  session_finish, locate, click, type, screenshot, overlay.
- Tái dùng code repo: session dùng scripts/session_manager.py
  (lock 1 owner), session sống dùng scripts/zen_dom.py ZenSession,
  xóa trong finally. Khác scripts/mcp_bridge.py đã có: cầu kia
  chỉ có 1 tool chung chuyển lệnh thô, server này mỗi op 1 tool
  với kiểm tra tham số chặt. locate dùng ZenSession.locate.
  click: locate qua DOM rồi bấm chuột thật ở giữa rect qua cu.Pointer,
  kiểm tra con trỏ trong 3 px như cu.py. type dùng ZenSession.evaluate.
  screenshot qua endpoint WebDriver, trả về MCP image content.
  overlay dùng scripts/overlay.py. Lỗi tool trả isError true.
  Text gõ vào không bao giờ ghi log, chỉ ghi tên tool và elapsed ms.
- Test: python3 tests/test_mcp_server.py, 12 test, tất cả pass,
  1.372 s (lần đầu 6.373 s). Per-test 79-90 ms gồm spawn server:
  ping, tools/list (8 tool), vòng đời session (start, start trùng
  bị từ chối, finish, finish trùng không làm gì), locate tìm thấy
  (tâm 140, 65) và không thấy, click (counter 1 rồi 2), type
  (trước "" sau "Ada"), screenshot (PNG 68 byte, magic đã kiểm tra),
  overlay acquire/release/status, lỗi không session, tham số sai,
  method không biết (-32601).
- Kiểm tra backend thật: không có trình duyệt, session_start lỗi
  sạch trong 0.15 s, không treo.
- Tài liệu docs/mcp-server.md: bảng tool, cách chạy, ví dụ config
  client, backend --fake, giới hạn.
- Giới hạn ghi rõ: local stdio only, không auth, không đưa lên mạng,
  không chạy dưới root, 1 live session, Marionette chỉ trên Zen test
  chuyên dụng.
- UNVERIFIED: mọi đường live (session_start trên Zen thật, locate,
  click, type, screenshot trên tab thật, overlay trên desktop thật,
  bắt tay với MCP client thật). Không có Firefox, Zen, geckodriver,
  Wayland session, hay MCP client trên máy này lúc làm. Phần đã
  kiểm chứng ở đây là protocol, kiểm tra tham số, đường lỗi, và
  toàn bộ flow tool với backend --fake.

## Đợt 2 việc 5: Review PR #1 của clone2

- Không commit, không merge, không sửa PR. Review ở đây, chi tiết
  đầy đủ trong báo cáo này để Muse quyết.
- Kết luận: MERGEABLE, nhưng HOLD, chưa merge ngay.
- Branch coord-clone2-setup, đầu lúc review xong 6ce5a75
  ("clone2: desktop control landscape research, task 2"), base
  main 1c7d252. Trial merge vào main hiện tại sạch, không conflict,
  đã kiểm tra 2 lần trong scratch worktree (đã xóa) và tôi kiểm tra
  lại 1 lần nữa cũng sạch ("Automatic merge went well").
  GitHub vẫn hiện mergeable UNKNOWN (chưa tính), PR có 0 review,
  chỉ comment của tác giả.
- Lý do hold: branch đang chạy, trong lúc review đã tiến 3 lần
  (9ba5d25, dd12098, 56ec79e, rồi 6ce5a75). Task 4, 5, 6 đợt 2 của
  clone2 vẫn còn trên chính branch này, tiêu đề PR ghi "batch 2 in
  progress". Merge ngay sẽ làm kẹt việc đó hoặc ép sang branch mới.
  Merge sau khi batch 2 của clone2 xong, với trial merge mới ở đầu đó.
- Phạm vi review, 6 file: coord/clone2.md (sửa, 394 dòng),
  docs/research/2026-11-21-atspi-desktop-control.md (mới, 261 dòng),
  docs/research/2026-11-21-desktop-control-landscape.md (mới,
  386 dòng), tests/atspi_prototype.py (mới, 383 dòng),
  tests/selenium_connect_existing.py (mới, 346 dòng),
  tests/fixtures/selenium_attach_fixture.html (mới, 26 dòng).
- Đã chạy: atspi_prototype.py --mode auto, exit 0, 0.0004 s, live
  lỗi thật với ModuleNotFoundError pyatspi, selftest pass hết.
  --mode selftest, exit 0, 0.0003 s. py_compile cả 2 file pass.
  selenium_connect_existing.py --help chạy được, không tham số thì
  lỗi đúng là cần --geckodriver. Fixture 717 byte, 16 element theo
  parse, khớp báo cáo. Cộng kiểm tra 2 lần chạy Selenium trong báo
  cáo (9.1438 s so với tổng 9.2447 s, 4.9467 s so với 4.9837 s) đều
  khớp trong sai số nhỏ.
- Môi trường đã kiểm tra: không Firefox, Zen, geckodriver trên máy
  này, không module selenium hay pyatspi lúc review (pyatspi được
  cài sau, ở việc 4 đợt 3).
- Vấn đề tìm được, nhỏ, không cái nào chặn một mình:
  1. tests/atspi_prototype.py, main(), nhánh selftest fail: ở mode
  auto, nếu live thành công (summary["ok"] = True) rồi selftest
  fail, summary["ok"] không được đặt lại, script exit 0. Trái với
  docstring của chính nó, "In auto mode, exit 0 means the selftest
  passed". Sửa: đặt lại summary["ok"] khi selftest fail, hoặc tính
  từ cả 2 nửa.
  2. tests/atspi_prototype.py, press_button(), dòng 115-125:
  do_action() trả False chỉ nằm trong detail dict, step vẫn pass.
  Ở live mode, lần bấm trả False sẽ bị ghi là thành công. Sửa:
  raise khi ok là False.
  3. tests/atspi_prototype.py, find_widget(): khớp đúng tên
  node.name == name. Tên AT-SPI thật có thể mang dấu mnemonic, nên
  lookup live có thể bỏ lỡ nút đang có. Ghi chú, không phải lỗi ở
  selftest.
  4. tests/selenium_connect_existing.py, read_dom(): cần element id
  heading, nên mọi --url tùy chỉnh không có nó sẽ fail step.
  --second-url mặc định là https://example.com, nên step tab thứ
  hai cần mạng; báo cáo tự ghi step này là số mạng, không phải số
  protocol.
  5. tests/selenium_connect_existing.py,
  browser_still_alive_after_session_delete(): ở pure attach mode
  (trình duyệt không do script mở), trình duyệt chết hay cổng
  Marionette đóng chỉ ghi marionette_port_open False và step pass;
  ở launch mode cùng điều kiện thì raise. Không nhất quán.
  6. tests/selenium_connect_existing.py, start_geckodriver():
  output --log info của geckodriver đi vào DEVNULL, nên log mất
  khi session fail khó hiểu, dù báo cáo khuyên lấy log geckodriver.
  7. coord/clone2.md thay toàn bộ file assignment của Muse bằng
  báo cáo trạng thái (cùng mẫu như clone1). Không phải lỗi, nhưng
  text assignment giờ chỉ còn trên main, không còn trên branch.
- Sạch: 0 em dash, 0 en dash trong cả 6 file PR. Không thông tin
  cá nhân; chuỗi giống email duy nhất là URL mailing list debian
  trong link nguồn ở doc AT-SPI, không phải dữ liệu cá nhân.
- Chất lượng báo cáo tốt: kết quả live ghi UNVERIFIED đúng chỗ,
  suy luận ghi là suy luận, nguồn có trích, số Selenium nhất quán
  nội bộ.
- Đề nghị: duyệt nội dung, sửa vấn đề 1 và 2 (mỗi cái 1 dòng trong
  tests/atspi_prototype.py), merge chỉ sau khi task 4-6 đợt 2 của
  clone2 xong trên branch này, với trial merge mới ở đầu đó.
- UNVERIFIED: mọi số Selenium/Firefox (Firefox 160.0.1, geckodriver
  0.37.1, Selenium 4.53.0, tổng 9.2447 s và 4.9837 s), mọi hành vi
  AT-SPI live, số chạy agent-desktop 1.3.1 và desktop-mcp v0.17.0
  trong doc landscape, mọi claim riêng về Zen.

## Đợt 3 việc 1: Quét toàn repo tìm thông tin cá nhân, commit aeaa006

- Phương pháp: git grep trên cả 32 ref (main, origin/HEAD, 30 remote
  branch) tìm email, số điện thoại VN và chung, token GH/OpenAI/AWS/
  Slack, private key, gán password/secret, tên thật, lịch học, địa
  chỉ nhà. Mọi match chỉ in ra dạng đã che, 36 match riêng được
  phân loại bằng tay. Tổng thô: 1075 match regex, 167 placeholder,
  908 trông thật, gần hết là false positive.
- Báo cáo docs/personal-info-audit-20261121.md, 214 dòng, 0 em dash,
  0 en dash, không tên đầy đủ hay địa chỉ email đầy đủ nào trong đó,
  chỉ nhắc domain gmail.com 2 lần.
- Tìm thấy 1, TÊN THẬT, ĐANG LỘ trên main (chưa sửa): 71 dòng trong
  45 file trên main, 1427 dòng trên 31 đầu branch (chủ yếu cùng file
  mang qua các branch). Dạng: header Owner trên báo cáo improvement,
  cách dùng sở hữu trong scripts/zen_cli.py:22,202 và doc skill,
  intro assignment trong coord, văn xuôi trong live-test-log.md, và
  giá trị test fullName trong
  tests/realistic/fcc-k/fixtures/test-08-form.html:29,35,38. Có từ
  ít nhất 18/11 (blame: zen_cli.py:22 về 2045020,
  a1-code-exec-dom-design.md:3 về 3f29fe3). Không sửa hàng loạt:
  trải 45 file gồm coord/clone1.md và coord/clone2.md (việc này cấm
  tôi sửa) và báo cáo đang chạy, nên cần Muse quyết từ thay thế.
  Handle GitHub phamTuan207 ở vai trò tác giả commit không tính là
  lộ (handle công khai, không phải tên thật).
- Tìm thấy 2, EMAIL THẬT, ĐÃ SỬA trên main:
  improvements/live-test-log.md:3288, vào từ a46b3c68 (18/11), đã
  xóa bởi commit 1c7d252 của tôi (21/11). Đã kiểm tra là không còn
  trên origin/main. Vẫn còn trong lịch sử git từ a46b3c68 và ở đầu
  của 25 branch (danh sách đầy đủ trong báo cáo). Pickaxe toàn lịch
  sử xác nhận nó không xuất hiện ở file nào khác. Cần bước xóa lịch
  sử đã lên kế hoạch cộng rebase hoặc xóa 25 đầu branch đó.
- Không tìm thấy: số điện thoại thật (mẫu mobile VN: 0 match),
  gán password/secret, token GH/AWS/Slack, private key, địa chỉ nhà,
  lịch cá nhân. Chữ lịch và địa chỉ duy nhất tìm được là chính text
  cấm trong coord/clone1.md:43 và coord/clone2.md:56.
- False positive đã loại: 5 token "sk-" 15 ký tự, đều nằm trong tên
  file ".json" ở dòng log (key OpenAI thật dài 48 ký tự trở lên);
  29 match 10 chữ số, đều là hệ số thập phân Oklab hoặc chuỗi test
  0123456789; 1 URL archive mailing list lists.debian.org trong doc
  AT-SPI; 167 email placeholder (example.*, users.noreply.github.com).
- UNVERIFIED: file nhị phân không được quét (git grep bỏ qua); mọi
  phiên bản lịch sử của mọi file không được grep từng cái (đầu branch
  quét đủ, email truy bằng pickaxe, pickaxe tên trả về trống, có thể
  do quirk encoding, nên tên nào thêm rồi xóa trước đầu branch có
  thể bị sót); file untracked hoặc ignored trên máy khác không được
  quét; định dạng không chuẩn có thể lọt qua regex.
- CÂU HỎI CHO MUSE: tên thật đang lộ ở 45 file trên main, sửa thế
  nào? Các lựa chọn: (a) thay hàng loạt bằng từ chung chung trong 1
  commit, (b) chỉ sửa file mới từ nay về sau và để lại lịch sử,
  (c) để nguyên. Tôi không tự sửa hàng loạt vì nó chạm coord và
  báo cáo đang chạy. Cần Muse quyết từ thay thế và phạm vi.

## Đợt 3 việc 2: Kiểm chứng 111 mục todo đã tick, commit aeaa006

- Đọc docs/zen-error-fix-todolist-20261121.md trên main (111/115
  đã tick). Kiểm tra từng mục đã tick xem có bằng chứng thật không:
  commit, test pass, log đo.
- Kết quả: 92 mục có bằng chứng, 15 mục bằng chứng yếu, 4 mục
  không có bằng chứng. Bảng trong báo cáo đủ 111 dòng (92 E, 15 W,
  4 N). Báo cáo docs/todo-audit-20261121.md, 375 dòng.
- 4 mục không bằng chứng: 2.4.5 I23 (không có rule hay code hay test
  về làm đúng y chỉ thị của người có tên; chỉ có rule verify chung),
  2.4.6 I24 (không có rule kiểm tra tooltip ở đâu), 2.4.7 I25
  (không có rule về hiển thị cuộc gọi hay số 2 so với 11), 2.7.7 G7
  (script helper SSH laptop chỉ được nhắc trong todolist, file không
  có trong repo và không có trên máy này).
- Bằng chứng yếu, điểm chính: 2.2.1 và 2.2.2, file được trích
  overlay-flicker-work-log-20261121.md không tồn tại ở đâu trong
  repo; phép đo 122 cửa sổ và 0 paint chỉ còn trong báo cáo cuối và
  docs/overlay.md; trigger ngày 20/11 vẫn chưa xác định. 2.2.4, tên
  Daemon._ensure_native và 2 test respawn được nêu không tồn tại;
  hành vi tương đương được bao bởi test watchdog tên khác và pass;
  chứng minh respawn live vẫn nợ (chính tick đó thừa nhận). 2.2.5,
  doc redteam tự nói nó không chứng minh nguyên nhân flicker live,
  nên tick nói quá. 2.1.3-2.1.6, 1.3.2, 5.1, 1.1.4: fixture offline
  có hoặc số có, nhưng chứng minh live đang chờ hoặc nguồn duy nhất
  là doc tóm tắt hay báo cáo cuối không có log thô. 2.7.10: tìm mới
  từ audit này, tests/test_glass_shayxo_contract.py tồn tại nhưng
  6 trong 17 test fail vì assert blur 0.0 và pad 12.6 trong khi repo
  hiện có blur 0.15 và pad 12.75 (thay đổi 4.1). Contract không được
  cập nhật; sửa nó ngoài phạm vi audit, để Muse quyết. 3.2.5, 3.2.12,
  4.3: chỉ có quy trình với khoảng trống đã thừa nhận (không kiểm
  tra offline; 3 zip gốc vẫn bị gắn cờ chứa file .a; file goal được
  nêu không tìm thấy trong repo).
- Tự chạy kiểm chứng: suite phase 3 cộng overlay, chạy lại từng
  function, 46 passed, 0 failed, khớp đúng claim 5.4 (35 phase-3
  cộng 11 overlay). Đếm lại hit-rate từ
  tests/calibration-e2-hits.jsonl: 51/87 = 58.6%, khớp 17/29 đã nêu.
  Suite watchdog, timing, hit-rate qua unittest: 23 test, tất cả
  pass. polygon_checks.py CLI chạy được. Cả 10 commit được trích
  (1cfac75, b876ee1, 352b943, ceff51c, 6be6784, 92944da, 2f0510d,
  aa114b2, 8636f21, 96438bb) đều tồn tại. Số log của Worker J khớp
  đúng số todolist ở 1.1.1-1.1.3, 1.3.3, 2.2.6.
- Tôi kiểm tra lại riêng: python3 -m unittest
  tests.test_glass_shayxo_contract, 17 test, 6 fail, đúng như audit
  nói. Tôi không sửa, vì audit chỉ báo cáo, không sửa.
- Todolist không bị sửa, không mục nào bị bỏ tick.
- UNVERIFIED: đường dẫn script laptop ở 2.7.7 (không kiểm tra được
  từ máy này hay repo); chứng minh live cho 2.1.3-2.1.6; số nguồn
  đơn cho 1.1.4, 1.3.2, 5.1; trigger flicker 20/11; và 6 test
  contract Shayxo fail, đã tìm ra nhưng không sửa.

## Đợt 3 việc 3: 10 test khó, commit 1767d4c

- 37 file trong tests/realistic/clone1-batch3/: t01 terminal
  emulator (20 bước), t02 spreadsheet công thức (19 bước),
  t03 video call UI (19 bước), t04 email client (19 bước),
  t05 file manager (20 bước), t06 calendar (17 bước),
  t07 code editor (17 bước), t08 settings panel (16 bước),
  t09 multi-window workflow (12 bước cộng assert), t10 music
  player (20 bước). Mỗi test có README (bối cảnh, mục tiêu,
  15-40 bước, pass/fail), fixture.html offline, check.mjs kiểm
  tra DOM thật bằng click, fill, bàn phím, chuột thật.
- Chạy của agent: lần đầu 7 passed, 3 failed (t04, t06, t10), cả
  3 đều là bug thật trong file của chính agent, đã sửa, chạy riêng
  lại pass trước lần chạy cuối. Lần cuối: 10 passed, 0 failed,
  wall clock 27033 ms. Per-test: t01 3686, t02 1932, t03 2033,
  t04 2428, t05 2227, t06 2570, t07 2601, t08 1911, t09 3239,
  t10 4396 ms. Bug đã sửa: (1) t04 dùng selector
  ">> nth=1 .star" sai, đổi sang locator API; (2) t06 click ô ngày
  trúng chip sự kiện (stop propagation), đổi sang click số ngày;
  (3) t10 status hiện "Stopped" khi pause ở vị trí 0, sửa bằng cờ
  started trong fixture.
- Kiểm tra lại của tôi, khác với báo cáo của agent: chạy full lần
  1 được 9 passed, 1 failed ở t09-multi-window, lỗi "Target page,
  context or browser has been closed" khi click #apply-btn. Chạy
  riêng t09 thì pass, 2430 ms. Tôi đã sửa check.mjs của t09: thêm
  helper clickAndClose, chỉ bỏ qua đúng lỗi "has been closed" khi
  sự kiện close đã bắn, các assert sau mỗi bước vẫn kiểm tra hiệu
  quả click. Chạy full lại sau sửa: lần 1 được 10 passed, 0 failed,
  29574 ms; lần 2 được 8 passed, 2 failed, t09 lỗi "main window
  missing dark class after prefs dark", t10 lỗi "position not reset
  after next". Kết luận: t09 và t10 flaky theo thời gian khi chạy
  full dưới tải nặng (load average 7.68 lúc chạy, 9 agent song
  song). Đừng ghi 10/10 tuyệt đối cho batch3; cần chạy lại trên
  laptop hoặc làm checker chịu thời gian tốt hơn.
- UNVERIFIED: cùng 10 flow trên Firefox và Zen.

## Đợt 3 việc 4: AT-SPI điều khiển Zen, commit 6e57183

- Máy bắt đầu không có gì dùng được: không Firefox hay Zen, không
  at-spi2-core, không pyatspi, không gi, không D-Bus session,
  không DISPLAY. Agent đã tự dựng stack thay vì bỏ cuộc:
  apt-get update chạy được (71.3 MB), cài at-spi2-core 2.52.0,
  python3-pyatspi 2.46.1, gir1.2-atspi-2.0 2.52.0, dbus-x11
  (Xvfb đã có sẵn), và tải Firefox 160.0.1 thật (90,943,956 byte)
  về /tmp/firefox. Prototype chạy với Firefox đó dưới Xvfb, D-Bus
  riêng cộng bus AT-SPI.
- File: tests/atspi_probe.py (289 dòng, stdlib cộng pyatspi), mode
  dump, click, type, full. Mỗi bước log 1 dòng JSON có wall-clock
  và elapsed ms. Tắt dialog onboarding qua AT-SPI, click qua Action,
  gõ qua EditableText với fallback phím và chuột, kiểm tra lại bằng
  cách đọc qua Text interface. Exit 0 chỉ khi mọi op yêu cầu được
  kiểm chứng.
- Báo cáo docs/research/2026-11-21-atspi-zen-control.md, 272 dòng,
  nguồn có ngày truy cập 2026-11-21.
- Kết quả chạy thật trên Firefox 160.0.1, ngày 2026-11-21:
  đọc cây CHẠY ĐƯỢC. find_app 11.0-31.9 ms; walk toàn cây 71 node
  trong 15.4-29.9 ms. Cây gồm UI chrome (tab bar, navigation
  toolbar, combo box địa chỉ, menu) và nội dung web (document web,
  heading, paragraph, push button Increment, entry Name). Tab có
  action switch (đã thấy, chưa chạy).
  Click qua Action: CHẠY ĐƯỢC, đã kiểm chứng. Tắt onboarding bằng
  cách bấm Continue và Not now (0.2-0.3 ms), bấm Increment
  (0.2-0.3 ms), đọc lại paragraph "Counter: 1". Dialog onboarding
  chặn cây nội dung và user.js không tắt được nó trên 160.0.1;
  bấm tắt qua AT-SPI là cách sửa, và cũng chứng minh điều khiển
  UI chrome.
  Gõ qua EditableText: HỎNG trên 160.0.1, đã xác nhận live.
  setTextContents trả True nhưng đọc lại là "". Đây là Mozilla Bug
  2087495 (guard IsTextRole() bị đảo, sửa ở nhánh 161). Log mode
  full cuối: type_editabletext FAIL, probe exit 2.
  Gõ qua generateKeyboardEvent: 4 dạng đã thử, đều fail ở dạng
  keystring (KEY_SYM, KEY_STRING, KEY_PRESS/RELEASE với keystring,
  ngay cả sau Action activate với STATE_FOCUSED True). Dạng keycode
  tới được field nhưng sai ký tự dưới keymap mặc định của Xvfb
  (keycode 30/48 cho ra "u'" thay vì "ab"), nên cần bảng map keysym
  sang keycode. Đối chứng bằng xdotool type chạy được ("yo" đọc
  lại được), chứng minh X focus và XTest delivery ổn; lỗi chỉ ở
  tổng hợp sự kiện keystring của pyatspi.
- Kết luận cho Zen: Zen dùng chung stack Gecko với Firefox, nên kết
  quả đọc cây và click qua Action chuyển sang được, nhưng đường gõ
  thì không: cho tới khi sửa EditableText vào base Firefox của Zen,
  AT-SPI không gõ tin được. Đề nghị trong báo cáo: dùng AT-SPI để
  đọc cây và click, dùng BiDi để gõ. Trên Wayland, đọc cây và click
  qua Action vẫn chạy được (D-Bus), còn tổng hợp phím và chuột kiểu
  XTest và xdotool sẽ không chạy.
- Kiểm chứng lại của tôi, MỘT PHẦN: file và doc có đủ, 0 em dash,
  0 en dash, py_compile pass. Firefox 160.0.1 đã xác nhận ở
  /tmp/firefox/firefox, pyatspi import được. Nhưng tôi tự chạy lại
  probe dump 3 lần đều fail ở find_app, timeout 30 s, dù Firefox
  đang chạy và bus AT-SPI đã xác nhận lên (GetAddress trả về
  đường bus_99). Tôi đã dọn sạch tiến trình test của mình (Firefox,
  Xvfb đã kill, 0 tiến trình còn lại). Kết quả live của agent vẫn
  là claim của agent, tôi chưa tái hiện độc lập được; có thể do
  đấu nối bus trong phiên của tôi. Cần chạy lại trên laptop hoặc
  cho probe tự dựng session (Xvfb cộng bus cộng Firefox) thay vì
  để người chạy tự đấu nối.
- UNVERIFIED: mọi thứ trên Zen thật (nội dung cây, sidebar và
  workspace, phiên bản base Firefox, bug EditableText có ảnh hưởng
  nó không). Mọi hành vi Wayland (mọi test live chạy dưới Xvfb,
  X11). Walk cây trang lớn (fixture chỉ 71 node) và action switch
  của tab (đã thấy, chưa chạy).

## Đợt 3 việc 5: Quy trình xóa email khỏi lịch sử, commit 6e57183

- Tài liệu docs/email-history-scrub-plan.md, 282 dòng, 10,367 byte.
  0 em dash, 0 en dash, không địa chỉ email đầy đủ nào trong đó
  (5 lần nhắc "gmail.com" đều là domain trong lệnh kiểm chứng).
- Đã kiểm tra trước khi viết (21/11, trên máy này): HEAD 1c7d252
  xác nhận xóa đúng 1 dòng khỏi improvements/live-test-log.md;
  file ở HEAD có 0 match domain đó. Chỉ 2 commit trong toàn bộ
  lịch sử đã fetch chạm chuỗi đó: a46b3c68 (đưa vào, 18/11) và
  1c7d252 (xóa). Cả origin/todolist-push (đầu b8db405) và
  origin/coord-clone2-setup (đầu PR #1) vẫn còn dòng lộ ở đầu
  (mỗi cái 1 match). PR #1 đang MỞ, đầu coord-clone2-setup, base
  main, MERGEABLE, mergeState CLEAN. Main: 432 commit, 0 tag,
  .git 6.0M, 31 remote branch, main KHÔNG được bảo vệ, nên force
  push được phép. git filter-repo CHƯA cài trên máy này.
- Doc bao gồm: đóng băng và backup trước mọi thứ; cài filter-repo;
  mirror clone riêng ở /tmp (không bao giờ dùng repo live); dựng
  file replacements bằng máy từ commit a46b3c68 dòng 3288 mà không
  gõ địa chỉ, xóa ngay sau đó; lệnh filter-repo --replace-text
  chính xác; bộ kiểm chứng đầy đủ (số main sau viết lại dự kiến
  431, git log -S và git grep trống trên mọi commit, kiểm tra đầu
  từng branch, kiểm tra merge-commit còn nguyên); force push; thứ
  tự re-clone laptop, clone1, clone2, VM, mỗi bên kiểm tra sạch
  trước khi làm việc; xử lý PR #1 (không merge trước khi viết lại,
  kiểm tra diff và mergeability sau, đóng rồi mở lại nếu fail);
  xóa todolist-push sau kiểm chứng vì nó đã merge ở 96438bb; cái
  scrub không dọn được (cache GitHub, fork, clone cũ, notification);
  rollback trước và sau force push.
- Tôi kiểm tra lại riêng: chỉ 2 commit chạm chuỗi đó (a46b3c68,
  1c7d252), 31 remote branch, đúng như doc nói.
- UNVERIFIED: chưa thử cài filter-repo ở đây (tool không có);
  hash commit sau viết lại và dự đoán 431 commit chưa đo cho tới
  lần chạy thật; chưa kiểm tra có fork nào không; clone2 hay VM có
  việc chưa push không thì chưa kiểm tra ở đây, phải xác nhận trong
  coord lúc đóng băng; thời gian hết cache GitHub cho trang commit
  cũ và diff PR chưa kiểm chứng.
- CHỈ VIẾT QUY TRÌNH. Không chạy filter-repo trên repo thật, không
  force push, không viết lại lịch sử nào, không chạm branch nào.

## Câu hỏi cho Muse (ghi vào file này theo quy tắc mới)

1. Tên thật đang lộ ở 45 file trên main, sửa thế nào? Xem đợt 3
   việc 1. Cần từ thay thế và phạm vi trước khi tôi sửa hàng loạt.
2. Test contract Shayxo 6/17 fail, có sửa contract theo giá trị
   mới (blur 0.15, pad 12.75) hay sửa code về giá trị cũ (blur 0.0,
   pad 12.6)? Audit chỉ báo cáo, không sửa.
3. PR #1: merge sau khi task 4-6 đợt 2 của clone2 xong, và sửa
   vấn đề 1 và 2 trong tests/atspi_prototype.py trước, đúng không?
4. Lần chạy AT-SPI tiếp theo: có muốn probe tự dựng session
   (Xvfb cộng bus cộng Firefox) để ai cũng tái hiện được không?

## Cần Muse làm trên laptop

1. Chạy 10 test batch1, 10 test batch2, 10 test batch3 trên Zen
   thật, so với số Chromium ở đây, chú ý t09 và t10 batch3 và t10
   batch2 flaky theo thời gian.
2. Chạy quy trình firefox-mcp mục 11.5 trên Zen thật.
3. Chạy MCP server với MCP client thật trên Zen thật.
4. Chạy probe AT-SPI trên Zen thật (Wayland), kiểm tra đọc cây,
   click, và bug gõ EditableText.
5. Chạy bước 2 xóa email khỏi lịch sử khi cả đội rảnh, theo
   docs/email-history-scrub-plan.md.

## Ghi chú thêm

- Firefox 160.0.1 giờ đã có ở /tmp/firefox trên máy clone1 (do
  việc 4 đợt 3 tải về), cộng at-spi2-core 2.52.0 và pyatspi 2.46.1.
  Câu "máy này không có Firefox" từ các báo cáo trước giờ đã cũ
  đối với /tmp/firefox, nhưng Firefox đó chưa dùng cho test
  realistic nào, và chưa có Zen.
- Tất cả 10 việc đợt 2 và đợt 3 đã xong, không còn việc tồn đọng
  trong 2 đợt này. Clone1 chờ việc tiếp theo qua repo.
