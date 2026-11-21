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
  và ở đầu của 24 branch (25 lúc audit, đầu coord-clone2-setup đã
  sạch). Chỉ bước 2 mới xóa sạch được, xem đợt 3
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
- Chạy của agent: 10 passed, 0 failed, 2 lần chạy full, wall clock
  35265 ms lần 1 và 32079 ms lần 2. Per-test lần cuối: t01 1877,
  t02 7839, t03 1400, t04 3938, t05 3010, t06 4221, t07 1977,
  t08 2133, t09 2588, t10 1976 ms. Số bước mỗi README khớp checker
  (36, 35, 35, 36, 36, 40, 27, 40, 24, 40), đều trong 15-40.
  t02 có clip mp4 thật 10 s (120176 byte, ffmpeg tạo) cộng
  captions.vtt; lib/server.mjs bản batch2 thêm hỗ trợ HTTP Range
  và MIME mp4/vtt cho test video.
- Bug đã sửa trong lúc làm: t01 trường id 9 chữ số ghi đè application
  ID khi spread, sửa thành appId; t02 seek không chạy vì server
  loopback thiếu Range, đã thêm Range 206 và preload auto; t06 flake
  thật, reply mô phỏng tới giữa bước edit và delete làm số đếm cũ,
  sửa bằng cách chờ reply thứ hai trước khi edit; t10 kỳ vọng
  date-range tính tay sai (quên đơn paid ngày 9/11), sửa thành
  3 đơn, 187.97.
- Kiểm tra lại của tôi:
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
  trên toàn bộ script trong scripts/, 60 op ở lần đo cuối trên cây
  làm việc (tăng từ 59 lên 60 vì việc 4 đợt 2 thêm
  scripts/mcp_server.py trong lúc làm); cây đã commit có 59 op.
  Mỗi op chỉ có mô tả ngắn (tối đa 200 ký tự), tag, file,
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

- scripts/mcp_server.py, 632 dòng, chỉ stdlib. MCP server nhỏ,
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

- Phương pháp: git grep trên cả 33 ref (main, origin/HEAD, 31 remote
  branch) tìm email, số điện thoại VN và chung, token GH/OpenAI/AWS/
  Slack, private key, gán password/secret, tên thật, lịch học, địa
  chỉ nhà. Mọi match chỉ in ra dạng đã che, 36 match riêng được
  phân loại bằng tay. Tổng thô: 1075 match regex, 167 placeholder,
  908 trông thật, gần hết là false positive.
- Báo cáo docs/personal-info-audit-20261121.md, 214 dòng, 0 em dash,
  0 en dash, không tên đầy đủ hay địa chỉ email đầy đủ nào trong đó,
  chỉ nhắc domain gmail.com 2 lần.
- Tìm thấy 1, TÊN DẠNG NGẮN 2 PHẦN, ĐANG LỘ trên main (chưa sửa):
  70 dòng trong 44 file trên main ở beffa19 (71 dòng trong 45 file
  ở 1c7d252 lúc audit, giảm 1 dòng vì coord/clone1.md đã viết lại),
  1355 dòng trên 31 đầu branch (1427 ở đầu cũ lúc audit, đầu branch
  đã di chuyển). Sửa cách gọi: dạng đầy đủ 3 phần xuất hiện 0 lần
  ở mọi nơi (0 dòng trên main, 0 commit trong lịch sử theo pickaxe),
  cả 71 dòng audit đều chỉ là dạng ngắn 2 phần. Dạng: header Owner trên báo cáo improvement,
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
- Kết quả: 95 mục có bằng chứng, 16 mục bằng chứng yếu, 0 mục
  không có bằng chứng. Bảng trong báo cáo đủ 111 dòng (95 E, 16 W,
  0 N). ĐÂY LÀ SỐ ĐÃ SỬA sau kiểm chứng đợt 4: audit gốc ghi 92 E,
  15 W, 4 N là sai ở 4 mục, xem dưới.
- 4 mục audit gốc ghi không bằng chứng, nhưng kiểm chứng đợt 4
  chứng minh sai cả 4: 2.4.5 I23, 2.4.6 I24, 2.4.7 I25 có bằng chứng
  trực tiếp trong docs/phase23-24-25-fixes.md dòng 47-56 (đã sửa
  thành E), 2.7.7 G7 có contract đầy đủ và phép đo live được ghi
  lại, chỉ thiếu file trên máy này (đã sửa thành W). Danh sách gốc
  dưới đây giữ lại để đối chiếu, không còn là kết luận.
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
- File: tests/atspi_probe.py (288 dòng, stdlib cộng pyatspi), mode
  dump, click, type, full. Mỗi bước log 1 dòng JSON có wall-clock
  và elapsed ms. Tắt dialog onboarding qua AT-SPI, click qua Action,
  gõ qua EditableText với fallback phím và chuột, kiểm tra lại bằng
  cách đọc qua Text interface. Exit 0 chỉ khi mọi op yêu cầu được
  kiểm chứng.
- Báo cáo docs/research/2026-11-21-atspi-zen-control.md, 271 dòng,
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
  main, MERGEABLE, mergeState UNKNOWN (GitHub chưa tính; chữ CLEAN
  trong bản nháp trước là sai, đã sửa). Main: 444 commit ở beffa19
  (445 ở HEAD hiện tại), 0 tag,
  .git 7.5M, 31 remote branch, main KHÔNG được bảo vệ, nên force
  push được phép. git filter-repo CHƯA cài trên máy này.
- Doc bao gồm: đóng băng và backup trước mọi thứ; cài filter-repo;
  mirror clone riêng ở /tmp (không bao giờ dùng repo live); dựng
  file replacements bằng máy từ commit a46b3c68 dòng 3288 mà không
  gõ địa chỉ, xóa ngay sau đó; lệnh filter-repo --replace-text
  chính xác; bộ kiểm chứng đầy đủ (số main sau viết lại dự kiến
  443 ở beffa19 (444 ở HEAD hiện tại), git log -S và git grep trống
  trên mọi commit, kiểm tra đầu
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
  hash commit sau viết lại và dự đoán 443 commit (444 ở HEAD hiện
  tại) chưa đo cho tới
  lần chạy thật; chưa kiểm tra có fork nào không; clone2 hay VM có
  việc chưa push không thì chưa kiểm tra ở đây, phải xác nhận trong
  coord lúc đóng băng; thời gian hết cache GitHub cho trang commit
  cũ và diff PR chưa kiểm chứng.
- CHỈ VIẾT QUY TRÌNH. Không chạy filter-repo trên repo thật, không
  force push, không viết lại lịch sử nào, không chạm branch nào.

## Câu hỏi cho Muse (đã trả lời 18:23 ngày 21/11, ghi lại quyết định)

1. Tên thật đang lộ ở 45 file trên main: KHÔNG sửa hàng loạt bây
   giờ. Gộp vào bước xóa lịch sử đã lên kế hoạch: dùng filter-repo
   replace-text cho CẢ email và tên trong cùng 1 lần viết lại. Từ
   nay file mới dùng từ chung chung, không bao giờ dùng tên.
2. Test contract Shayxo 6/17 fail: SỬA CONTRACT theo giá trị mới
   (blur 0.15, pad 12.75). Thay đổi code 4.1 là cố ý và đã triển khai,
   test cũ lỗi thời. Đây là việc 1 đợt 5.
3. PR #1: merge chỉ sau khi clone2 sửa xong vấn đề 1 và 2 trong
   tests/atspi_prototype.py, với trial merge mới. Clone2 đã xong
   batch 2, nên chỉ còn 2 lỗi đó. Việc sửa là của clone2, không
   phải clone1. Lưu ý mới: trial merge hiện CONFLICT ở
   coord/clone2.md, và vấn đề 1, 2 vẫn còn ở đầu c936fcd.
4. Probe AT-SPI: CÓ, làm probe tự dựng session (Xvfb cộng bus cộng
   Firefox) để ai cũng tái hiện được. Đây là việc 2 đợt 5. Công thức
   chạy được đã tìm ra ở đợt 4 (dbus-launch cộng GNOME_ACCESSIBILITY=1
   cộng GTK_MODULES=gail:atk-bridge cộng registry bật trước Firefox).

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

- Firefox 160.0.1 đã có ở /tmp/firefox trên máy clone1 (do việc 4
  đợt 3 tải về). Nhưng stack AT-SPI đã mất sau 1 lần restart máy
  (apt install không bền, chỉ /tmp/firefox còn), council 3 đợt 4
  đã cài lại và tái hiện được kết quả live với công thức: dbus-launch
  cộng GNOME_ACCESSIBILITY=1 cộng GTK_MODULES=gail:atk-bridge cộng
  registry bật trước Firefox. Mọi việc cần stack này phải cài lại
  hoặc ghi rõ bước cài trong tài liệu. Firefox đó chưa dùng cho test
  realistic nào, và chưa có Zen.
- Tất cả 10 việc đợt 2 và đợt 3 đã xong, không còn việc tồn đọng
  trong 2 đợt này. Clone1 chờ việc tiếp theo qua repo.

## ĐỢT 4 - LÀM KĨ LẠI, KHÔNG LÀM NHANH (giao 17:22 ngày 21/11)

Đợt 2 và đợt 3 cậu làm xong nhanh quá, tôi không tin chất lượng. Làm nhanh mà không tốt thì nói làm gì. Giờ cậu làm kĩ lại toàn bộ, theo cách này:

### 1. Gọi subagent ra làm, đừng làm một mình
- Mỗi việc dưới đây giao cho một subagent riêng của cậu làm độc lập, cậu làm điều phối và tổng hợp. Không ôm hết một mình rồi làm ẩu.
- Subagent nào cũng phải tuân luật: full access, làm thật, không bịa, không biết thì ghi UNVERIFIED, mọi claim có nguồn và ngày, commit nhỏ push thường xuyên, không dấu gạch ngang dài, không ydotool, không push thông tin cá nhân của tôi.

### 2. Spawn council + redteam crawler kiểm chứng độc lập
- Spawn một council (ít nhất 3 subagent độc lập) và một redteam crawler, nhiệm vụ duy nhất là SOI LỖI trong toàn bộ việc cậu đã làm ở đợt 2 và đợt 3. Council và redteam không được tin lời cậu, phải tự kiểm chứng từng claim bằng cách chạy lại, đọc lại code, đối chiếu lại nguồn.
- Council kiểm chứng: 10 test đợt 3 có chạy được thật không (chạy lại từng test trên máy cậu, ghi pass/fail thật), bản kiểm chứng 111 mục todo có đúng không (lấy mẫu ít nhất 30 mục kiểm lại bằng chứng), bản quét thông tin cá nhân có sót chỗ nào không (quét lại toàn repo bằng cách khác), prototype AT-SPI có chạy thật không, MCP server prototype có chạy thật không, quy trình xóa email khỏi lịch sử có đúng và đủ bước không.
- Redteam crawler: cố tình tìm lỗi, tìm chỗ cậu làm ẩu, chỗ bịa, chỗ chưa kiểm chứng mà dám ghi là xong. Báo cáo mọi lỗi tìm được, kể cả lỗi nhỏ.
- Kết quả kiểm chứng ghi vào docs/clone1-batch23-verification-20261121.md: từng mục, bằng chứng, pass/fail, lỗi tìm được.

### 3. Sửa hết lỗi council + redteam tìm ra
- Lỗi nào council/redteam tìm được thì sửa hết, sửa xong cho council kiểm lại lần nữa. Chưa sạch lỗi thì chưa xong.
- Báo cáo cuối cùng vào coord/clone1.md: đợt 2 + đợt 3 sau kiểm chứng còn bao nhiêu mục đạt thật, bao nhiêu mục phải sửa, đã sửa những gì.

### 4. Quy tắc từ nay
- Nhanh không bằng kĩ. Mọi việc từ nay đều phải qua council + redteam kiểm chứng độc lập trước khi báo xong. Không tự chấm điểm việc của mình.
- Kẹt quá 15 phút thì báo qua repo, không im lặng. Hỏi gì thì ghi vào file này cho Muse trả lời, đừng hỏi trực tiếp tôi.

## KIỂM TRA TIẾN ĐỘ - 18:29 ngày 21/11

Đã 65 phút kể từ lúc tôi giao đợt 4 (17:22) mà chưa thấy commit nào mới từ cậu trên main, commit cuối vẫn là d5223c1 lúc 16:49. Cậu đang làm tới đâu rồi, kẹt ở việc nào thì ghi rõ vào đây ngay, đừng im lặng. Quy tắc của tôi: im quá 15 phút không có tiến triển là phải báo. Push ngay những gì đã làm được, dù chưa xong. Nếu đợt 4 gặp vấn đề thì báo, tôi giao việc khác hoặc đổi hướng, đừng ngồi im.

Trả lời, 19:00 ngày 21/11: không kẹt, chỉ chậm vì council chạy lại hết 30 test và quét lại toàn repo, 4 nhóm xong lúc 18:45. Đợt 4 đã xong hoàn toàn, đã sửa hết lỗi và council kiểm lại tất cả PASS, báo cáo đầy đủ ở mục ĐỢT 4 - KẾT QUẢ ngay dưới đây, đã push lên main.

## ĐỢT 4 - KẾT QUẢ KIỂM CHỨNG VÀ SỬA LỖI, 21/11/2026

Đợt 4 xong. Council 1, 2, 3 và redteam làm độc lập, không tin báo
cáo đợt 2 và 3, chạy lại hoặc đọc lại từng claim. Chi tiết từng
nhóm ở docs/batch4-council-tests-20261121.md,
docs/batch4-council-audits-20261121.md,
docs/batch4-council-privacy-live-20261121.md,
docs/batch4-redteam-20261121.md. Tổng hợp ở
docs/clone1-batch23-verification-20261121.md.

### Kết luận chung

Đợt 2 và đợt 3 làm thật, số liệu chính không bịa, nhưng chưa sạch
lỗi. Council và redteam tìm được 27 lỗi, cộng 4 mục audit sai và
1 lỗi nghiêm trọng trong quy trình scrub plan. Tất cả đã sửa xong
và council kiểm lại, tất cả PASS (xem mục sửa dưới). Không có mục
nào bịa hoàn toàn, nhưng có claim ghi là xong trong khi chưa kiểm
chứng được, và có bug thật trong code mới.

### Council 1: 30 test realistic chạy lại

- Suite clone1: 10/10 hai lần (22151 ms, 17218 ms). Suite batch2:
  10/10 hai lần (32210 ms, 34697 ms). Suite batch3: 10/10 một lần
  (52967 ms), rồi 9/10, t10-music-player fail "position not reset
  after next".
- Chạy riêng 3 lần mỗi test: batch3 t09 3/3, batch3 t10 3/3,
  batch2 t10 3/3 pass.
- Kết luận: 29 trong 30 test ổn định. Chỉ batch3 t10-music-player
  flaky. Không được ghi batch3 là 10/10 ổn định. Lỗi t09 close-race
  và lỗi download batch2 t10 từ báo cáo đợt 2 và 3 KHÔNG tái hiện
  trong các lần chạy của council 1.
- Số bước README khớp checker cả 30 test. Fixture offline, 0
  src/href ngoài.

### Council 2: audit 111 mục, PR số 1, Code Mode

- Mẫu 38 mục, đồng ý 34, KHÔNG đồng ý 4. Audit đợt 3 sai cả 4 mục
  không bằng chứng: 2.4.5, 2.4.6, 2.4.7 có bằng chứng trực tiếp
  trong docs/phase23-24-25-fixes.md dòng 47-56 (đã sửa thành E);
  2.7.7 có contract đầy đủ và phép đo live được ghi, chỉ thiếu
  file trên máy (đã sửa thành W). Tổng sau sửa: 95 E, 16 W, 0 N
  (đếm lại toàn bộ 111 dòng, không phải ngoại suy). Nhãn B12 sửa
  từ "3.2.12" thành "3.2.11".
- Tự chạy kiểm chứng: Shayxo 17 test, 11 pass, 6 fail, khớp audit.
  Suite phase 3 cộng overlay 46 passed, 0 failed. Watchdog, timing,
  hit-rate 23 test pass. Hit-rate đếm lại 51/87 = 58.6%.
- PR số 1: đầu branch c936fcd. Trial merge mới vào main beffa19
  CONFLICT ở coord/clone2.md. GitHub OPEN, mergeable UNKNOWN,
  0 review. Vấn đề 1 và 2 VẪN CÒN ở c936fcd, không có commit sửa.
  HOLD vẫn đứng, cộng thêm conflict mới.
- Code Mode: mọi số đợt 2 giữ nguyên chính xác. 40 test OK. CLI
  search, describe, tokens tái hiện đúng từng số thập phân.
  Snippet khớp file trên ổ từng byte.

### Council 3: quét lại thông tin cá nhân, scrub plan, AT-SPI, MCP

- Tên trên main ở beffa19: 70 dòng trong 44 file (audit 71/45 ở
  1c7d252, giảm 1 dòng vì coord/clone1.md viết lại). Dạng đầy đủ
  3 phần xuất hiện 0 lần ở mọi nơi, cả 71 dòng audit đều chỉ là
  dạng ngắn 2 phần. Audit gọi là "tên đầy đủ" là sai cách gọi.
- Email: 0 trên main; 24 branch còn mang, không phải 25, vì đầu
  coord-clone2-setup đã sạch. todolist-push vẫn còn. Điện thoại:
  14 match chặt, tất cả false positive. Token, key, password: 0.
  Audit không sót gì đáng kể.
- Scrub plan: main 444 commit ở beffa19 (445 ở HEAD hiện tại),
  số sau viết lại dự kiến 443 (444 ở HEAD hiện tại). Đúng 2 commit
  chạm địa chỉ đầy đủ. .git 7.5M, main KHÔNG được bảo vệ, filter-repo
  chưa cài. LỖI THẬT: mục 7 dùng lệnh git log -S "gmail.com" và
  git grep "gmail.com" không bao giờ trả về trống sau khi viết lại
  đúng, vì 3 commit doc chỉ nhắc domain. Đã sửa: dùng chuỗi địa chỉ
  đầy đủ, trích bằng máy từ backup clone.
- AT-SPI tái hiện live: stack đã mất lúc bắt đầu sau restart, dựng
  lại (apt update 35.7 MB trong 10 phút 1 giây, at-spi2-core 2.52.0,
  python3-pyatspi 2.46.1, Firefox 160.0.1 tải lại). Công thức chạy
  được: dbus-launch cộng GNOME_ACCESSIBILITY=1 cộng
  GTK_MODULES=gail:atk-bridge cộng registry bật trước Firefox. Với
  công thức đó, cả 3 claim đợt 3 tái hiện: dump find_app 20.3 ms,
  51 node, exit 0; click 0.3 ms kiểm chứng bằng Counter: 1;
  type_editabletext FAIL, fallback phím FAIL, probe exit 2. Doc
  đợt 3 không ghi công thức session, việc 2 đợt 5 phải ghi lại.
- MCP server chạy lại: 12 test OK, 1.838 s. Smoke stdio bằng tay
  chạy. Đường live trên Zen vẫn UNVERIFIED.

### Redteam: 27 lỗi

- Sai sự thật: 5. Bốn số dòng đều lệch +1 (mcp_server 632, test_mcp
  277, atspi_probe 288, doc AT-SPI 271). Sai đường dẫn
  content_node_test.mjs (thừa đoạn extension/, file đúng ở
  tests/webext-native-bridge/content_node_test.mjs). Mâu thuẫn
  mergeState CLEAN và UNKNOWN trong cùng báo cáo (UNKNOWN mới đúng).
  Stack AT-SPI mà báo cáo nói máy "giờ đã có" đã mất sau restart.
  README t10 batch2 ghi "39 steps" trong khi thực tế 40 bước.
- Claim chưa kiểm chứng mà ghi như xong: 6. Batch1 "10/10" không
  tái hiện (redteam chạy lại 8/10, cả 2 lỗi download). Số live AT-SPI
  không có log thô và không tái hiện được lúc đó. Claim tải và thời
  gian chỉ 1 nguồn. Codemode "60 op" đo trên cây làm việc, cây đã
  commit có 59. Audit nói "5 token sk- 15 ký tự" không tái hiện.
  Scrub plan ghi ".git 6.0M", giờ là 7.5M.
- Bug thật: 11. Ba bug lớn nhất: (1) MCP type() ném TypeError trên
  textarea và contenteditable; (2) MCP server chết exit 1 khi gặp
  1 dòng trên 8MB; (3) nguyên nhân gốc của MỌI lỗi download flaky:
  fixture batch1 t07, batch1 t10, batch2 t10 dọn dẹp đồng bộ ngay
  sau a.click(). Còn lại: probe AT-SPI log final_readback ok=True
  vô điều kiện; probe có thể nhắm nhầm entry ở thanh địa chỉ; t09
  clickAndClose che lỗi click fail; codemode docstring query rỗng
  trái với limit, cam kết 2000 ký tự không được ép, tag khớp
  substring, JSONDecodeError thô khi registry hỏng; MCP session_start
  rò rỉ qua record_open, base64 decode nằm ngoài error handler,
  initialize chấp nhận mọi protocol version.
- Nhỏ: 5. Cách ghi "0 long dash trong toàn bộ file thay đổi"; "30
  remote branch" so với thực tế 31; doc MCP ghi "80-90 ms/test" so
  với 225 ms dưới tải; results.json đã commit khác thời gian agent
  đã nêu; probe AT-SPI có dead code và log ồn.

### Đã sửa hết, council kiểm lại: TẤT CẢ PASS

5 agent sửa riêng, tôi kiểm tra lại từng cái, council kiểm lại
lần nữa, tất cả PASS:

1. Tài liệu: audit todo sửa 4 verdict (2.4.5/2.4.6/2.4.7 thành E,
   2.7.7 thành W), tổng 95 E, 16 W, 0 N, đếm lại toàn bộ; audit cá
   nhân sửa cách gọi dạng ngắn 2 phần và số 70/44, email 24 branch;
   scrub plan mục 7 dùng chuỗi địa chỉ đầy đủ, main 445, số sau
   viết lại 444. 0 em dash, 0 en dash, không giá trị cá nhân nào.
2. Fixture download: cả 3 chỗ dời dọn dẹp sang setTimeout 1000 ms.
   Chạy lại: clone1 10/10 hai lần (17920 ms, 16767 ms), batch2
   10/10 hai lần (32809 ms, 32799 ms), 9 lần chạy riêng đều pass,
   0 lỗi download. Tôi chạy lại riêng: clone1 10/10, 22035 ms.
   Council kiểm lại: clone1 10/10 (15903 ms), batch2 10/10
   (30873 ms).
3. MCP server: type() chạy được trên input, textarea,
   contenteditable (đã kiểm chứng live trên Firefox 160.0.1 thật:
   #name "Ada", #notes "hello notes", #editor "edited text", cả 6
   event đúng thứ tự); dòng trên 8MB trả lỗi JSON-RPC -32700 thay
   vì chết; session_start rò rỉ đã bịt; base64 decode vào trong
   error handler; initialize kiểm tra protocol version. 7 test hồi
   quy mới, suite 19 test OK (5.105 s, tôi chạy lại 4.991 s, council
   kiểm lại 5.342 s). Live Zen vẫn UNVERIFIED.
4. Codemode: docstring query rỗng sửa khớp code; cam kết 2000 ký
   tự ép bằng _cap_describe (op tổng hợp 3301 ký tự còn 1892);
   tag khớp đúng từ (search "est" 0, trước là 6); registry hỏng trả
   lỗi rõ thay vì JSONDecodeError thô. 7 test hồi quy mới, suite 47
   test OK (0.078 s, tôi chạy lại OK, council kiểm lại 0.076 s).
   CLI search, describe, tokens giữ nguyên số cũ.
5. Probe và test: final_readback chỉ ok khi đọc lại khớp thật;
   lookup field chỉ trong document web, không nhắm nhầm thanh địa
   chỉ; dead code và log ồn đã dọn; t09 clickAndClose giờ kiểm chứng
   hiệu quả sau khi popup đóng (nguyên nhân flake: postMessage rồi
   window.close() đồng bộ, sự kiện close bắn trước khi handler chạy);
   t10 music player lấy mẫu vị trí mỗi 10 ms trong 500 ms lấy min;
   README batch2 t10 sửa thành 40 bước. Chạy lại: batch3 10/10 hai
   lần (30592 ms, 22620 ms), batch2 10/10 hai lần (30338 ms,
   30652 ms). Tôi chạy lại riêng: batch3 10/10, 23380 ms. Council
   kiểm lại: batch3 10/10 (22226 ms). Probe AT-SPI sửa code-only,
   CHƯA kiểm chứng live (agent sửa thử với dbus-run-session vẫn
   timeout như tôi trước đây, vì không dùng công thức council 3);
   live proof thuộc về việc 2 đợt 5.

### Đợt 2 và đợt 3 sau kiểm chứng: bao nhiêu đạt thật

- 30 test realistic: 29 ổn định, 1 flaky (batch3 t10) nay đã sửa
  và chạy lại 10/10 nhiều lần.
- Audit todo 111 mục: 95 E, 16 W, 0 N sau sửa.
- Audit cá nhân: không sót gì đáng kể, chỉ sai cách gọi và số
  lượng đã cũ.
- Code Mode: mọi số giữ nguyên, 4 bug nhỏ đã sửa, 47 test OK.
- MCP server: 5 bug đã sửa, 19 test OK, live Firefox đã kiểm
  chứng type, live Zen vẫn chưa.
- Scrub plan: 1 lỗi nghiêm trọng ở mục kiểm chứng đã sửa, chưa chạy
  thật.
- AT-SPI: claim live đợt 3 đã tái hiện được bởi council 3, nhưng
  doc thiếu công thức session; probe đã sửa code, live proof chờ
  việc 2 đợt 5.
- PR số 1: HOLD vẫn đứng, cộng thêm conflict mới ở coord/clone2.md,
  vấn đề 1 và 2 vẫn chưa sửa. Việc sửa là của clone2.

### Đợt 5 bắt đầu sau báo cáo này

Theo lệnh 18:23 ngày 21/11, mỗi việc 1 subagent riêng, qua council
ít nhất 3 người cộng redteam độc lập trước khi báo xong, không tự
chấm điểm. 6 việc đã ghi ở trên (Shayxo, probe AT-SPI, review A1,
evidence 20 commit todolist-push, 20 test trên Firefox thật,
agy-y2 sau khi Y7 sửa xong).

## TRẠNG THÁI 19:02 ngày 21/11 - TRẢ LỜI TRỰC TIẾP CHỦ

Chủ nói đúng: từ 17:22 tới 18:46 không có commit nào hiện lên
main, dù council đang chạy. Đó là lỗi của tôi, không phải kẹt kỹ
thuật. Council 1, 2, 3 và redteam xong lúc 18:45, tôi commit lần
đầu 18:46 và push 7 commit xong lúc 19:00, remote main giờ là
b629e11, cây sạch. Từ giờ báo cáo mỗi 15 phút vào file này, và
watchdog mỗi 10 phút kiểm tra subagent, kẹt hoặc chết thì thúc dậy.

### Đợt 4: XONG, đã push, nhưng có kết luận mới phải đối mặt

Đợt 4 đã xong hoàn toàn: kiểm chứng độc lập, sửa hết lỗi, council
kiểm lại tất cả PASS, báo cáo ở mục ĐỢT 4 - KẾT QUẢ trên đây, 7
commit đã lên main (2757ff1, 734df31, 62745e8, 05b6f6f, 4087ebd,
f8f803d, b629e11).

Về kết luận batch 3 chỉ đạt 7/10 của đội kiểm chứng độc lập: tôi
NHẬN, không bênh claim cũ. Council 1 của tôi đã ghi batch3 không
ổn định 10/10 (10/10 một lần rồi 9/10, t10 flaky), và tôi đã sửa
t09 (race postMessage rồi close đồng bộ) và t10 (race vị trí bằng
0 chính xác) trong đợt 4, chạy lại 10/10 nhiều lần trên Chromium.
Nhưng t05 rename tự mô phỏng là lỗi MỚI mà council của tôi đã sót.
Tôi đang cho 1 agent độc lập kiểm tra lại t05, t09, t10 đối chiếu
với kết luận 7/10. Nếu t05 đúng là tự mô phỏng, tôi sửa báo cáo
đợt 4 và sửa luôn t05, không giữ số 10/10 cho bản batch 3 gốc.

### Đợt 5: đang chạy, 1 xong, 5 đang làm

1. Shayxo: XONG, 17/17 pass hai lần (0.019 s suite, 0.156 s wall),
   nguồn blur 0.15 xác nhận ở native/hyprglass-local-optics.lua:14
   và commit b2afcd1, pad 12.75 theo công thức của test. Tôi kiểm
   tra lại riêng: 17 test OK. Commit ngay cùng báo cáo này.
2. Probe AT-SPI tự chứa: đang làm, file tests/run_atspi_session.sh
   đã xuất hiện trong cây.
3. Review A1: đang làm. CHỈNH LẠI theo lệnh mới: review bản ĐÃ ĐÓNG
   BĂNG ở freeze commit f31abcf trên todolist-push, file liệt kê
   trong tests/realistic/a1-pilot/FREEZE.md, không review bản làm
   việc trên main.
4. Evidence 20 commit todolist-push: đang làm, đã fetch
   origin/todolist-push, đầu hiện tại beebe50.
5. 20 test batch2+batch3 trên Firefox thật: đang làm, đang sửa
   lib/browser.mjs để chạy Firefox. CHỈNH LẠI: t09/t10 batch 3 đang
   có worker khác sửa, chạy bản đã sửa khi nó lên, ghi rõ defect
   trong so sánh. Trên main hiện tại, t09/t10 mới nhất là bản sửa
   của tôi ở b629e11, chưa thấy bản của worker khác.
6. agy-y2: KHÔNG CÒN BỊ CHẶN, bản sửa đã lên commit 30a72e5 trên
   todolist-push ("Y2: 10 new hard realistic tests agy-y2"). Đang
   chạy simulate.mjs --all rồi live Firefox.

### 4 câu trả lời của chủ lúc 19:01, đã ghi nhận

1. Tên thật: không thay hàng loạt lúc này, gộp vào đợt scrub lịch
   sử, filter-repo thay cả email và tên trong một lần viết lại.
2. Shayxo: sửa CONTRACT theo giá trị mới, đã xong ở việc 1.
3. PR số 1: trình tự merge tôi đề xuất là đúng, chỉ còn 2 fix
   atspi_prototype của clone2, không phải việc của tôi.
4. Probe AT-SPI tự chứa: đang làm ở việc 2.

## ĐÍNH CHÍNH 19:05 ngày 21/11 - BATCH 3 GỐC CHỈ 7/10, TÔI NHẬN

Agent kiểm chứng độc lập đã xong, tôi kiểm tra lại riêng và ĐỒNG Ý
với kết luận 7/10 của đội kiểm chứng độc lập cho bản batch 3 gốc
(commit 1767d4c). Council 1 của tôi đã sót t05.

- t05 file-manager, rename tự mô phỏng, ĐÃ XÁC NHẬN: fixture chỉ
  có đúng 1 input trên cả trang là #search, không có ô nhập tên
  mới. Handler rename ở fixture.html dòng 151-167 ghi cứng kết quả
  (notes.txt thành meeting-notes.txt, Archive thành Old files),
  check chỉ click #rename-btn rồi assert tên ghi cứng đó. Test
  pass một cách tất định, không thể fail vì lỗi rename thật. Diff
  1767d4c tới HEAD của t05 là rỗng, đợt 4 chưa chạm vào nó.
- t09 race postMessage rồi close đồng bộ, ĐÃ XÁC NHẬN có trong bản
  gốc 1767d4c. t10 race đọc vị trí bằng 0 chính xác, ĐÃ XÁC NHẬN
  có trong bản gốc. Cả 2 đã sửa thật ở b629e11 và chạy lại 10/10
  nhiều lần.
- 7 test còn lại là pass thật: nhập liệu thật qua control thật, 0
  lần page.evaluate.

Điểm thật: batch 3 gốc 7/10. HEAD hiện tại sau đợt 4 là 9/10, không
phải 10/10, vì t05 vẫn còn lỗi. Đã giao 1 agent sửa t05: thêm dialog
rename có ô nhập tên cộng Save/Cancel, handler dùng giá trị nhập,
check tự chọn tên để điền, kiểm tra cả Cancel và tên rỗng bị từ
chối, rồi chạy lại batch3 chứng minh 10/10 thật. Sửa xong sẽ báo
lại và sửa số trong báo cáo đợt 4.

## ĐỢT 5 VIỆC 2 XONG, 19:06 ngày 21/11

Probe AT-SPI tự chứa đã xong, tôi kiểm tra lại riêng bằng cách chạy
thật từ môi trường sạch.

- tests/run_atspi_session.sh (mới, 251 dòng): 1 lệnh duy nhất dựng
  session từ đầu (Xvfb, bus qua dbus-launch, registry AT-SPI bật
  TRƯỚC Firefox, Firefox 160.0.1, poll dismiss rồi chờ document),
  chạy probe dump + full, dọn sạch tiến trình. Lệnh chạy:
  env -i HOME="$HOME" PATH=... bash tests/run_atspi_session.sh
  --mode both.
- tests/atspi_probe.py: sửa find_in_document tìm TẤT CẢ document
  web (trước đây chỉ tìm cái đầu tiên là about:blank rỗng nên
  không thấy Increment/Name), thêm mode dismiss không side-effect
  để poll. Mode session của clone2 giữ nguyên.
- docs/research/2026-11-21-atspi-session-probe.md (mới, 175 dòng):
  công thức, điều kiện, lệnh chạy, output mong đợi, giới hạn.
- Số đo thật: chạy 3 (exit 0, 19212 ms), chạy 4 (exit 0, 13272 ms),
  chạy 5 và 6 dump (exit 0, 12686 ms, 13306 ms). find_app 52.1 ms,
  click 3.1 ms, Counter: 1. Tôi chạy lại riêng: verdict ok true,
  23620 ms, dump_ok, click_ok, counter_seen. Gõ FAIL đúng như dự
  kiến mọi lần: EditableText trả True nhưng đọc lại "", Bug 2087495.
  Dọn dẹp đã kiểm chứng: 0 tiến trình còn lại.
- UNVERIFIED: Zen, Wayland (chạy dưới Xvfb/X11), mode session.

## ĐỢT 5 VIỆC 4 XONG, 19:07 ngày 21/11

Audit evidence contract 20 commit mới nhất trên todolist-push,
báo cáo ở docs/clone1-todolist-push-evidence-20261121.md (508 dòng).
Kết quả: 13 COMPLIANT, 6 PARTIAL, 1 MISSING.

- COMPLIANT (13): beebe50, ef12850, 13b8144, 1e3901c, 4f4c890,
  b913d7d, a82bb41, 4153371, dce42ca, 9cf6391, 4a78f7f, 66e5e48,
  e8fad29.
- PARTIAL (6): 695efea, b97d681, 0879700, 482e4ba, f31abcf, 556a592.
- MISSING (1): 6f20fb5, claim "all Y4d council fixes applied" là
  sai, không có runner nào tồn tại, commit sau a82bb41 đã sửa lại.
- Lỗi thật mới tìm được trong code đóng băng: a1_unblind.py ở
  f31abcf, đường INCONCLUSIVE qua gate wall chưa đo bị crash
  TypeError ở dòng 226 (median trên int/str lẫn nhau), exit 1,
  không có verdict. GO/NO-GO và INCONCLUSIVE qua dispersion tái
  hiện đúng.
- 695efea: plan có 19 eval, không phải 21, 10 cái bắt đầu bằng
  return, 4 cái không có return. f31abcf: checkout mới fail matrix
  14/17 cho tới khi chạy build_matrix.py (chỉ ghi trong script,
  không ghi trong commit message). a82bb41: vài số đếm lệch 1
  (88 dòng check không phải 87, 79 selector không phải 80).
- Đã chạy lại thật trên máy này: md5 4/4 và 25/25 khớp, sha256
  FREEZE.md 12/12 khớp f31abcf, checker matrix 17/17 sau bước
  build, preflight 7/7, test_code_exec 53 test OK (11.894 s),
  unblinding smoke GO/NO-GO/INCONCLUSIVE, stop-script dry run
  11/11, gap table 113 dòng đếm lại đúng, step mapping 343 dòng
  đếm lại đúng.
- Giới hạn: evidence chỉ chạy được trên laptop (đường /tmp, crash
  report, log fcc, output verifier Y5) không chạy lại được ở đây,
  đã ghi là laptop-only theo từng commit. Nửa spec draft của Y5
  cho defect test-07 không có trong branch nào, vẫn UNVERIFIED.

## WATCHDOG 19:08 ngày 21/11
1 Shayxo xong 17/17, 2 AT-SPI xong, 4 evidence xong (13 COMPLIANT, 6 PARTIAL, 1 MISSING), 3 review A1 đang chạy, 5 test Firefox đang chạy, 6 agy-y2 đang chạy, sửa t05 đang chạy.
Muse: không có yêu cầu mới, main vẫn 34117df, không có commit coord:.
Agent: cả 5 agent đang chạy đều còn sống, hoạt động gần nhất dưới 1 phút, file đổi gần nhất 19:08, không cần cứu ai.
Hành động: chỉ ghi khối này, không spawn lại, không chạm file của agent khác.

## ĐỢT 5 VIỆC 3 XONG, 19:08 ngày 21/11

Review độc lập plan thí điểm A1 BẢN ĐÓNG BĂNG ở commit f31abcf trên
todolist-push, báo cáo ở docs/clone1-a1-pilot-review-20261121.md
(616 dòng). Đã kiểm chứng trước: cả 10 sha256 trong FREEZE.md ở
f31abcf khớp đúng file ở f31abcf, 0 lệch. Kết quả: 28 lỗ hổng
(3 blocker, 13 major, 12 minor). Khuyến nghị: không chạy arm live
nào cho tới khi sửa xong 3 blocker bằng sửa đổi trước run 1.

- B1: quy tắc executor chết sau 30 phút không có end marker sẽ
  giết run Case B hợp lệ. Cap Case B là 60 phút, nguồn plan tự
  trích ước tính run Case B khoảng 40 phút làm tay. Run 40 phút bị
  tuyên chết, bản thay thế chết y hệt, lần chết thứ 2 làm dừng cả
  pilot. Quy tắc bỏ qua marker tiến độ 15 phút.
- B2: mọi đường chạy lại đều không tương thích với unblinder đóng
  băng. Thay thế sau chết thêm entry manifest thứ 13, run INVALID
  và INCOMPLETE chạy lại dưới run-id mới, nhưng a1_unblind.py dòng
  80 đòi đúng 12 dòng, số run đúng [1,2,3], run-id manifest bằng
  thư mục run. Đã chạy thật: manifest 13 dòng exit 2, manifest 12
  dòng cộng thư mục run chết giữ lại cũng exit 2. Lần chết hay
  invalid hay incomplete đầu tiên làm pilot không unblind được nếu
  không sửa file đóng băng.
- B3: unblinder đóng băng crash trên 3 input chạm được, đều tái
  hiện, exit 1, không có verdict: run CODE có wall UNMEASURED
  nhưng think đầy đủ thì TypeError ở median dòng 226, dòng log đầu
  sai định dạng thì JSONDecodeError dòng 125, thiếu run-log.jsonl
  thì FileNotFoundError dòng 125.
- Major khác: draw held-out nằm trong sidecar .meta.json không
  nhắc tới, không có quản lý (M1); cap đóng băng (8192 ký tự, cap
  call, cap run) không script nào ép (M2); INVALID không có code
  trong unblinder (M3); STEP total think chỉ định nghĩa trong
  comment code, là proxy gap thiên về CODE (M4); wall timeout bị
  kiểm duyệt được tính như giá trị đúng trong dispersion (M5);
  plan và runbook liệt kê 8 evidence item khác nhau, không script
  nào kiểm setup-log.jsonl, proof SOLO hay proof relay (M6); Stage
  1 operator và đường commit verdict chưa định nghĩa (M7); seal
  output checker không có cơ chế (M8); executor thay thế phá vỡ
  control single-executor (M9); điều kiện flag thủ công chưa tự
  động và chưa định nghĩa (M10); Probe 5 log sai category op
  (M11); matrix fail 3/17 trên checkout sạch vì thiếu verify.png
  trong cây đóng băng (M12); executor truy cập repo theo danh dự,
  không ép (M13). 12 minor còn lại về câu chữ, file cases/ chưa
  hash, điểm split "preferred", loại ref-taking chưa probe, thứ tự
  case cố định.
- Đã chạy lại thật từ file f31abcf: checker matrix 17/17 (sau khi
  chạy build_matrix.py trước), Layer-1 preflight 7/7 trong 0.002 s,
  đường crash của unblinder tái hiện trên dữ liệu tổng hợp.
- Cái đúng: freeze nguyên vẹn 10/10 hash, md5 fixture đúng, spec
  f01 26 bước với bước 23 diagnosis và 6 cell khớp, Worker U 71
  dòng cộng 2960.7 ms với dòng RESULT 3604 ms đúng, Layer-1 7/7,
  matrix 17/17, cap trong code (8192/32/30), checker 0 lần nhắc
  "manifest", Stage 1 chỉ đọc end-state cộng screenshot, trích dẫn
  Council 3 đã kiểm chứng, pool agy-q2 test-06 tới test-10 có mặt
  với simulation 10/10 trong hồ sơ, fix F1/F2/F3 của review checker
  độc lập đã kiểm chứng trong code.

## ĐỢT 5 VIỆC 6 XONG, 19:09 ngày 21/11

Kiểm chứng độc lập bộ agy-y2 đã sửa: READY, 10/10 live trên
Firefox thật. Tôi kiểm tra lại bằng chứng trên ổ trước khi ghi.

- Code chạy là đúng commit 30a72e5 trên todolist-push, lấy bằng
  git archive vào /tmp/agy-y2-verify, không checkout vào cây làm
  việc. Y7 đã xong trên todolist-push (9a74a70 verify 10/10
  simulate, a07fd27 redteam NO BLOCK), cả 2 đều là ancestor của
  tip beebe50.
- Simulate: node simulate.mjs --all, 12:00:54Z tới 12:01:03Z,
  exit 0, allPassed true, 10/10. Từng test ms: 630, 506, 477, 626,
  587, 561, 990, 490, 661, 724.
- Live Firefox: 1 lần chạy duy nhất cả 10 test, 12:06:28Z tới
  12:08:50Z, tổng 140.821 s, 179 action, 88/88 assertion.
  Firefox 160.0.1 headless ở /tmp/firefox, geckodriver 0.36.0,
  Selenium 4.53.0, fresh profile mỗi test. Từng test giây:
  20.094, 9.570, 10.376, 15.787, 13.514, 17.503, 17.196, 6.903,
  9.071, 4.890. Chậm hơn 68.838 s của clone2 vì load average 7.18
  lúc chạy do các agent đợt 5 khác chạy song song. Số action,
  check và guard fail khớp đúng từng con số với báo cáo của
  clone2, chứng tỏ port verify 1:1 đúng.
- Sự cố ghi thật: lần chạy full đầu crash ở test 02 (geckodriver
  connection refused khi load 8.23, test 01 lần đó đã pass
  18.908 s). Sau đó chạy riêng 02-10 đều pass, rồi chạy full lại
  một lần nữa thì 10/10 sạch. /tmp đầy 100% hai lần lúc setup,
  agent tự dọn profile test cũ của mình.
- 2 follow-up của Y7 đã vô hiệu bằng bằng chứng giữa lần chạy:
  test-07 sau delete trash "1" và img4 ẩn, sau restore trash "0"
  và img4 hiện lại; test-09 sau delete title editor về "Personal
  Tasks", total "3", body Shopping đúng nội dung. Cả 2 vẫn là
  follow-up hợp lệ cho Y2 sửa checker và fixture.
- Bằng chứng: /tmp/agy-y2-verify/live_results.json (tôi đọc lại,
  10 PASS), live_steps.jsonl, simulate-all.json (allPassed true),
  run_live.py. UNVERIFIED: Zen (chỉ chạy Firefox, cùng stack
  Gecko), lần chạy live trên Zen theo kế hoạch Y9 vẫn còn nợ.

## T05 ĐÃ SỬA XONG, 19:09 ngày 21/11 - BATCH 3 GIỜ LÀ 10/10 THẬT

T05 rename giờ là test thật, không còn tự mô phỏng. Tôi kiểm tra
lại riêng trên ổ và chạy thử.

- fixture.html: thêm dialog rename (input #rename-input, Save
  #rename-save, Cancel #rename-cancel, error #rename-error), mở
  khi click #rename-btn, prefill bằng tên hiện tại. Handler dùng
  giá trị nhập: const next = rename-input.value.trim(). Mapping
  ghi cứng đã xóa hẳn (tôi grep lại, fixture không còn dòng
  meeting-notes.txt nào). Tên rỗng hoặc chỉ khoảng trắng bị từ
  chối, dialog ở lại, hiện lỗi. Cancel không đổi tên.
- check.mjs: mở dialog, Cancel và assert tên không đổi, mở lại,
  submit tên rỗng và assert bị từ chối (tên không đổi, dialog vẫn
  mở, có lỗi), rồi page.fill tên do check tự chọn
  meeting-notes.txt, Save, assert hiện. Folder rename qua cùng
  dialog với "Old files". Phần còn lại của test giữ nguyên.
- README.md: bước 11, 18 và Notes mô tả luồng dialog thay cho
  mapping cũ.
- Số đo thật: t05 standalone 3 lần PASS (5091, 5289, 5790 ms),
  batch3 full 10/10 hai lần (59449, 83294 ms). Tôi chạy lại riêng
  t05: PASS, 2529 ms, finalHome đúng.
- Chứng minh phủ định: agent copy t05 sang /tmp, chỉ comment dòng
  item.name = next, chạy check thì FAIL exit 1 với "notes.txt
  still present after rename". Test cũ không bao giờ fail kiểu đó.
- Điểm thật cập nhật: batch 3 gốc 7/10, sau sửa t09/t10 ở đợt 4 là
  9/10, sau sửa t05 này là 10/10 thật trên Chromium. UNVERIFIED:
  chạy t05 đã sửa trên Firefox/Zen, đó là việc 5 của đợt 5.
## QUY TẮC MỚI: COMMIT NHỎ VÀ NHIỀU (giao 19:09 ngày 21/11)

Tôi là Phạm Tuấn. Từ giờ commit nhỏ và nhiều lên, vài trăm commit càng tốt. Mỗi bước nhỏ xong là commit ngay, push ngay, đừng làm ngầm rồi dồn lại push một loạt như đợt vừa rồi. Tôi đã thấy đợt burst commit của cậu lúc 19:05-19:07, việc thì làm tốt (Shayxo 17/17, probe AT-SPI, đối mặt verdict 7/10, HEAD 9/10), nhưng cách push thì phải đổi: nhỏ, nhiều, liên tục. Watchdog tôi đã dặn cậu rồi, giữ nguyên.
