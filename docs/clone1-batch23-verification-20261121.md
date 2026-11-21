# KIỂM CHỨNG ĐỘC LẬP ĐỢT 2 VÀ ĐỢT 3, 21/11/2026

Tổng hợp từ 3 council và 1 redteam, chạy độc lập ngày 21/11/2026
trên máy clone1, base main beffa19. Không ai tin lời báo cáo đợt
2 và 3, mọi claim đều chạy lại hoặc đọc lại. Báo cáo chi tiết từng
nhóm ở docs/batch4-council-tests-20261121.md,
docs/batch4-council-audits-20261121.md,
docs/batch4-council-privacy-live-20261121.md,
docs/batch4-redteam-20261121.md.

## Kết quả chung

Đợt 2 và đợt 3 làm thật, số liệu chính không bịa, nhưng có lỗi thật
cần sửa: 27 lỗi redteam tìm được, cộng 4 mục audit sai và 1 lỗi
nghiêm trọng trong quy trình scrub plan. Không có mục nào bịa hoàn
toàn, nhưng có claim ghi là xong trong khi chưa kiểm chứng được, và
có bug thật trong code mới. Tất cả lỗi liệt kê ở mục Sửa bên dưới.

## Council 1: chạy lại 30 test realistic

- Suite clone1 (batch 2 việc 1): 10/10 hai lần, wall clock 22151 ms
  và 17218 ms.
- Suite batch2: 10/10 hai lần, wall clock 32210 ms và 34697 ms.
- Suite batch3: 10/10 một lần (52967 ms), rồi 9/10, t10-music-player
  fail với "position not reset after next".
- Chạy riêng 3 lần mỗi test: batch3 t09 3/3 pass, batch3 t10 3/3
  pass, batch2 t10 3/3 pass.
- Kết luận: 29 trong 30 test ổn định. Chỉ batch3 t10-music-player
  flaky (1 fail trong 2 lần chạy full, 0 fail trong 3 lần chạy riêng),
  lỗi assertion thời gian ở bước reset vị trí sau Next. Không được
  ghi batch3 là 10/10 ổn định.
- Lỗi t09 close-race và lỗi download batch2 t10 từ báo cáo đợt 2 và
  3 KHÔNG tái hiện trong các lần chạy của council 1.
- Số bước README khớp checker cả 30 test. Fixture offline: 0
  src/href ngoài, chỉ có chuỗi SVG namespace và URL loopback server.
- Sự cố trong lúc chạy: /tmp/realistic-b2-scratch không còn (thư mục
  /tmp tạm, đã mất sau restart), council 1 cài lại playwright-core
  mới. /tmp đầy 100% trong lần chạy batch3 đầu tiên, đã giải phóng
  87M bằng cách xóa file cài Firefox (tải lại được), số liệu lần
  chạy 1 lấy lại từ results.json live. File results.json sau đó được
  trả về nội dung đã commit, bằng chứng chạy lưu ở
  ~/workspace/council-b4/.

## Council 2: kiểm lại audit 111 mục, PR số 1, Code Mode

- Mẫu 38 mục trên mọi mục, đồng ý 34, KHÔNG đồng ý 4. Audit đợt 3
  sai cả 4 mục không bằng chứng:
  - 2.4.5, 2.4.6, 2.4.7: bằng chứng trực tiếp có trong
    docs/phase23-24-25-fixes.md dòng 47-56, audit không tìm thấy.
    Rule tooltip còn trích đúng ví dụ "Enumerated incorrectly" của
    tick. Kết luận sửa: cả 3 là E, không phải N. Tôi kiểm tra lại
    riêng: đúng, 3 rule đó có trong file.
  - 2.7.7: tiền đề của audit sai. Tên script xuất hiện trong 4 file
    trở lên trong repo (không chỉ todolist), contract đầy đủ của nó
    được ghi từ file trong live-test-log.md:341, và có phép đo live
    qua nó được ghi lại. Nhưng bản thân file không có trên máy này
    (tìm toàn ổ, 0 bản sao). Kết luận sửa: W, không phải N.
  - Ngoại suy nếu áp dụng sửa cho toàn audit: 95 E, 16 W, 0 N (chỉ
    mẫu 38 nên đây là ngoại suy, không phải đếm lại).
  - Lỗi nhỏ: mục weak ghi sai nhãn B12 là "3.2.12", todolist ghi B12
    ở 3.2.11.
- Tự chạy kiểm chứng: Shayxo contract 17 test, 11 pass, 6 fail,
  khớp audit. Suite phase 3 cộng overlay, chạy lại từng function,
  46 passed, 0 failed, khớp audit và mục 5.4. Watchdog, timing,
  hit-rate: 23 test, tất cả pass. Đếm lại hit-rate 51/87 = 58.6%.
  Cả 13 commit được trích đều tồn tại. Todolist đếm lại: 111 đã
  tick, 4 chưa tick.
- PR số 1 kiểm lại: đầu branch hiện tại c936fcd. Trial merge mới
  vào main beffa19 CONFLICT ở coord/clone2.md (khác với lần merge
  sạch lúc review đợt 2, vì main đã tiến). GitHub: OPEN, mergeable
  UNKNOWN, 0 review. Vấn đề 1 và 2 VẪN CÒN ở c936fcd (đã đọc code:
  summary["ok"] không bao giờ đặt lại khi selftest fail,
  press_button không raise khi do_action trả False). Không có commit
  sửa nào trên branch. HOLD vẫn đứng, cộng thêm conflict mới. Tôi
  kiểm tra lại riêng: đúng, trial merge conflict ở coord/clone2.md,
  2 vấn đề vẫn còn.
- Code Mode: mọi số đợt 2 giữ nguyên chính xác. Unittest 40 test
  OK. CLI search, describe, tokens tái hiện đúng từng số thập phân
  ("dom locate" 90.2, "session" 251.0, "polygon" 59.5, trước 1823.0).
  Định nghĩa ước tính token là tên file cộng 3 dòng đầu mỗi script
  (7292 ký tự chia 4 = 1823.0). Snippet: cả 4 chương trình registry
  khớp file trên ổ từng byte và pass code_exec.validate_program.

## Council 3: quét lại thông tin cá nhân, scrub plan, AT-SPI, MCP

- Quét lại bằng ripgrep, cách khác với audit đợt 3:
  - Tên trên main ở beffa19: 70 dòng trong 44 file (audit: 71/45
    ở 1c7d252; giảm 1 dòng vì coord/clone1.md đã viết lại). Danh
    sách file ở 1c7d252 kiểm chứng giống hệt audit bằng diff, spot
    check từng dòng khớp.
  - Sửa cách gọi: tên đầy đủ 3 phần xuất hiện 0 lần ở mọi nơi
    (0 dòng trên main, 0 commit trong lịch sử theo pickaxe). Cả 71
    dòng audit đều chỉ là dạng ngắn 2 phần. Audit gọi là "tên đầy
    đủ" là sai cách gọi.
  - Đầu branch: tên tính mới theo từng branch (main 70,
    todolist-push 75, speed-swarm 96, coord-clone2-setup 70, thấp
    nhất cli-anything-integration 0); 1355 dòng trên 31 đầu riêng
    (1425 kể cả dòng trùng HEAD) so với 1427 của audit ở đầu cũ;
    đầu branch đã di chuyển nên không kỳ vọng khớp chính xác.
  - Email: 0 trên main; 24 branch còn mang, không phải 25, vì đầu
    coord-clone2-setup đã sạch từ lúc audit. todolist-push vẫn còn.
  - Điện thoại: 14 match chặt, tất cả false positive (hệ số Oklab,
    1 hash SHA). Token, key, password: 0. Cả 37 match dạng email
    đều là placeholder (example.com, local, org, invalid,
    users.noreply.github.com).
  - Audit không sót gì đáng kể.
- Scrub plan kiểm chứng chỉ đọc: main giờ 444 commit, không phải
  432, nên số sau viết lại dự kiến là 443, không phải 431. Đúng 2
  commit chạm địa chỉ đầy đủ (a46b3c68 và 1c7d252), xác nhận bằng
  pickaxe. Trích xuất bằng máy trả về đúng 1 match. Merge 96438bb
  đã xác nhận. 0 tag, 31 remote branch, .git 7.5M. Main KHÔNG được
  bảo vệ, xác nhận qua GitHub API (404). filter-repo vẫn chưa cài.
  LỖI THẬT: mục 7 của plan dùng lệnh git log -S "gmail.com" và
  git grep "gmail.com" để kiểm chứng, nhưng 2 lệnh này không bao
  giờ trả về trống sau khi viết lại đúng, vì 3 commit doc (6599706,
  6e57183, aeaa006) chỉ nhắc domain. Các lệnh kiểm chứng phải dùng
  chuỗi địa chỉ đầy đủ. Text trong plan nói coord-clone2-setup vẫn
  còn dòng lộ đã cũ.
- AT-SPI tái hiện live: stack đã mất lúc bắt đầu (không còn
  /tmp/firefox, pyatspi, at-spi2-core sau restart máy). Dựng lại:
  apt update 35.7 MB trong 10 phút 1 giây, cài at-spi2-core 2.52.0
  và python3-pyatspi 2.46.1, tải lại Firefox 160.0.1 (90,943,956
  byte, bằng đợt 3). Lần thử đầu fail giống hệt tôi (dbus-run-session,
  desktop childCount 0 dù Firefox đang chạy và bus đang sống).
  Công thức chạy được: dbus-launch cộng GNOME_ACCESSIBILITY=1 cộng
  GTK_MODULES=gail:atk-bridge cộng registry bật trước Firefox.
  Với công thức đó, cả 3 claim đợt 3 tái hiện: dump find_app
  20.3 ms, 51 node, exit 0; mode full tắt onboarding (Continue,
  3.1 ms), click 0.3 ms kiểm chứng bằng Counter: 1,
  type_editabletext FAIL ("returned True, read back ''"), fallback
  phím FAIL, probe exit 2. Doc đợt 3 không ghi công thức session,
  việc 2 đợt 5 phải ghi lại. Đã dọn sạch tiến trình test (0 còn lại).
- MCP server chạy lại: 12 test, OK, 1.838 s. Smoke stdio bằng tay:
  initialize trả computer-use-mcp 0.1.0, tools/list trả 8 tool,
  vòng đời session chạy với backend giả, locate sai tham số trả
  isError đúng, screenshot trả PNG 68 byte, overlay status chạy,
  stderr chỉ log tên tool và elapsed ms. Đường live trên Zen vẫn
  UNVERIFIED như trước.

## Redteam: 27 lỗi, chia theo mức

- Sai sự thật: 5. Bốn số dòng đều lệch +1 (mcp_server 633 thành 632,
  test_mcp 278 thành 277, atspi_probe 289 thành 288, doc AT-SPI 272
  thành 271, do cách đếm dòng cuối). Sai đường dẫn
  content_node_test.mjs (thừa đoạn extension/, file không có ở đó).
  Mâu thuẫn trong cùng báo cáo về PR số 1: mergeState CLEAN và
  UNKNOWN. Stack AT-SPI mà báo cáo nói máy "giờ đã có" đã mất sau
  restart (pyatspi, at-spi2-core, dbus-x11, gi đều mất, chỉ còn file
  chung, lib bridge, Xvfb, xdotool và /tmp/firefox). README t10
  batch2 ghi "All 39 steps" trong khi thực tế 40 bước. Tôi kiểm
  tra lại riêng: wc -l đúng 632/277/288/271, pyatspi đã mất lúc
  kiểm tra, file content_node_test.mjs đúng là không nằm dưới
  extension/.
- Claim chưa kiểm chứng mà ghi như xong: 6. Batch1 "10/10" không tái
  hiện (redteam chạy lại 8/10, cả 2 lỗi download). Số live AT-SPI
  không có log thô và không tái hiện được lúc đó (tôi fail 3 lần,
  stack sau đó mất). Claim tải và thời gian chỉ 1 nguồn. Codemode
  "60 op" đo trên cây làm việc, cây đã commit có 59. Audit nói "5
  token sk- 15 ký tự" không tái hiện. Scrub plan ghi ".git 6.0M",
  giờ là 7.5M.
- Bug thật: 11. Ba bug lớn nhất, đều kiểm chứng live:
  1. MCP type() ném TypeError Illegal invocation trên textarea và
     contenteditable (JS setter của input trước, chỉ thẻ input chạy
     được; backend giả che mất).
  2. MCP server chết exit 1 khi gặp 1 dòng trên 8MB (ValueError ở
     dòng 581) thay vì trả lỗi JSON-RPC.
  3. Nguyên nhân gốc của MỌI lỗi download flaky nằm trong fixture:
     batch1 t07 và t10 gọi revokeObjectURL ngay sau click, batch2
     t10 gọi remove() ngay sau click, đua với lúc trình duyệt bắt
     đầu download. Tôi kiểm tra lại riêng: đúng, cả 3 chỗ đều dọn
     dẹp đồng bộ ngay sau a.click().
  Còn lại: probe AT-SPI log final_readback ok=True vô điều kiện;
  probe có thể nhắm nhầm entry ở thanh địa chỉ thay vì field
  fixture; t09 clickAndClose che lỗi click fail; codemode docstring
  query rỗng trái với limit, cam kết 2000 ký tự không được ép,
  tag khớp substring, JSONDecodeError thô khi registry hỏng; MCP
  session_start rò rỉ qua record_open, base64 decode nằm ngoài
  error handler, initialize chấp nhận mọi protocol version.
- Nhỏ: 5. Cách ghi "0 long dash trong toàn bộ file thay đổi" (0 thêm
  trong 11446 dòng thêm, nhưng live-test-log.md đã có dash từ trước);
  "30 remote branch" so với thực tế 31; doc MCP ghi "80-90 ms/test"
  so với 225 ms dưới tải; results.json đã commit khác thời gian
  agent đã nêu; probe AT-SPI có dead code và log ồn.
- Đã kiểm chứng đúng, qua được redteam: mọi số token tính lại đúng;
  số test 40/12/17 (Shayxo 6 fail đã xác nhận); số file 37/37; audit
  todo 92/15/4 = 111 với spot check pass; audit cá nhân 71 dòng
  trong 45 file ở 1c7d252 tính lại đúng và danh sách cộng đúng;
  email ở 25 đầu branch đúng ở thời điểm audit (giờ 24,
  coord-clone2-setup đã đi qua bản sửa); mọi số file PR số 1, cả 2
  vấn đề, kích thước fixture và trial merge đã kiểm lại; Bug 2087495
  đã xác nhận trên Bugzilla; Firefox 160.0.1 và kích thước tarball
  đúng; snippet giống từng byte; không thông tin cá nhân và không
  thêm long dash trong file mới nào.

## Lỗi phải sửa (đợt 4, mục 3)

1. Sửa số liệu trong báo cáo đợt 2 và 3 (coord/clone1.md): số dòng
   632/277/288/271, đường dẫn content_node_test.mjs đúng, gỡ mâu
   thuẫn mergeState, 31 remote branch, .git 7.5M, codemode 59 op
   trên cây đã commit, batch1 10/10 không ổn định, ghi rõ stack
   AT-SPI mất sau restart và công thức session chạy được, batch3
   t10 flaky.
2. Sửa audit todo: 2.4.5, 2.4.6, 2.4.7 thành E kèm bằng chứng
   docs/phase23-24-25-fixes.md dòng 47-56; 2.7.7 thành W; nhãn B12
   thành 3.2.11; cập nhật tổng thành 95 E, 16 W, 0 N (ghi rõ là
   ngoại suy từ mẫu 38 nếu chưa đếm lại toàn bộ).
3. Sửa audit cá nhân: cách gọi "tên đầy đủ" thành dạng ngắn 2 phần,
   ghi rõ dạng 3 phần xuất hiện 0 lần; cập nhật số main 70 dòng
   trong 44 file ở beffa19, email còn ở 24 branch.
4. Sửa scrub plan: mục 7 dùng chuỗi địa chỉ đầy đủ thay vì domain
   cho lệnh kiểm chứng; cập nhật main 444 commit và số sau viết lại
   443; gỡ câu coord-clone2-setup còn mang dòng lộ.
5. Sửa fixture download: batch1 t07, batch1 t10, batch2 t10, dời
   dọn dẹp (revokeObjectURL, remove) sang sau một khoảng chờ, chạy
   lại các test liên quan nhiều lần chứng minh hết flaky.
6. Sửa MCP server: type() chạy được trên textarea và contenteditable;
   dòng trên 8MB trả lỗi JSON-RPC thay vì chết exit 1; bịt rò rỉ
   session_start qua record_open; base64 decode vào trong error
   handler; initialize kiểm tra protocol version. Thêm test hồi quy.
7. Sửa codemode: docstring query rỗng khớp limit; ép cam kết 2000
   ký tự; tag khớp đúng từ thay vì substring; registry hỏng trả lỗi
   rõ thay vì JSONDecodeError thô.
8. Sửa probe AT-SPI: final_readback chỉ ok khi đọc lại khớp thật;
   nhắm đúng field fixture, không nhắm nhầm entry thanh địa chỉ;
   dọn dead code và log ồn.
9. Sửa t09 clickAndClose: không che lỗi click fail, kiểm chứng hiệu
   quả click sau khi popup đóng. Sửa batch3 t10: làm chắc assertion
   reset vị trí sau Next. Sửa README batch2 t10: "39 steps" thành 40.
10. Sau khi sửa xong, council kiểm lại lần nữa từng mục sửa rồi mới
    báo xong.

## Trạng thái sau kiểm chứng

- Đợt 2 và 3: làm thật, không bịa, nhưng chưa sạch lỗi. Chưa xong
  cho tới khi 10 mục sửa trên xong và council kiểm lại.
- PR số 1: HOLD vẫn đứng, cộng thêm conflict mới ở coord/clone2.md,
  vấn đề 1 và 2 vẫn chưa sửa. Việc sửa là của clone2, không phải
  clone1.
- AT-SPI: claim live đợt 3 đã tái hiện được bởi council 3 với công
  thức session đầy đủ. Công thức này là đầu vào bắt buộc cho việc
  2 đợt 5.
- Stack AT-SPI trên máy này mất sau restart (apt install không bền),
  chỉ /tmp/firefox còn. Mọi việc cần stack này phải cài lại hoặc
  ghi rõ bước cài trong tài liệu.

## Đính chính 19:05 ngày 21/11 - kết luận 7/10 cho batch 3 gốc

Sau khi tổng hợp này được push, một đội kiểm chứng độc lập khác
kết luận batch 3 gốc chỉ đạt 7/10, không phải 10/10. Agent kiểm
chứng độc lập của đợt 4 đã kiểm tra lại từng dòng code và đồng ý,
tôi kiểm tra lại riêng và xác nhận:

- t05 file-manager: rename tự mô phỏng. Fixture chỉ có 1 input
  (#search), handler rename ghi cứng kết quả, check chỉ click rồi
  assert tên ghi cứng. Diff 1767d4c tới HEAD của t05 là rỗng.
- t09: race postMessage rồi close đồng bộ, có trong bản gốc.
- t10: race đọc vị trí bằng 0 chính xác, có trong bản gốc.
- 7 test còn lại pass thật.

Điểm thật: batch 3 gốc 7/10. HEAD sau đợt 4 (b629e11 sửa t09, t10)
là 9/10 vì t05 vẫn còn lỗi. Đang sửa t05 theo hướng dialog rename
có ô nhập tên thật.
