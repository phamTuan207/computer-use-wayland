# BÁO CÁO CLONE1, 21/11/2026, HOÀN THÀNH 5 VIỆC CỦA MUSE

Nhiệm vụ từ commit 8676e45 đã làm xong hết, 5 commit mới trên main, push
ngay sau khi viết xong file này. Mọi số đo dưới đây là số thật đo trên
máy của clone1, chưa kiểm chứng thì ghi UNVERIFIED.

## Kết quả chung

- Máy clone1: Node v24.22.1, Python 3.12.3, không có Firefox hay Zen
  (đã kiểm tra lại ngày 2026-11-21: `which firefox firefox-esr zen
  zen-browser` không thấy gì, không có gì dưới /usr/lib hay /opt,
  không có ~/.mozilla, không có Flatpak hay snap Firefox/Zen).
  Vì vậy mọi test cần trình duyệt thật đều chạy trên Playwright
  Chromium 1254, hoặc chỉ chạy được phần không cần trình duyệt.
  Tất cả kết quả trên Zen thật vẫn UNVERIFIED, chờ laptop.
- Không có thông tin cá nhân trong các file mới, 0 ký tự gạch ngang
  dài (em dash, en dash) trong toàn bộ 18 file thay đổi và tạo mới.

## Việc 1: Hoàn thiện WebExtension bridge, commit 056a5cd

- Thêm 5 op mới vào content.js: scroll, hover, select, upload
  (file base64 được dựng lại thành File thật qua DataTransfer),
  waitFor (MutationObserver, timeout tối đa 120 s).
- background.js: định tuyến 5 op mới, timeout 25 s mỗi op, log có
  thời gian, đếm số lần native host chết, báo cáo trong ping.
- host/cu_bridge_host.py: mọi timeout và lỗi ghi đều có thời gian UTC,
  thêm bộ đếm timeouts và errors vào host.status.
- install.py viết lại: mặc định giữ nguyên, thêm --check, --uninstall,
  --sign (chạy web-ext build, không lưu khóa AMO), --policies với
  --xpi (ghi distribution/policies.json để force-install).
  Sửa 1 lỗi tìm được khi test: bản cũ trỏ tới cu_bridge_host.py ở
  gốc bridge, nhưng host thật ở trong host/, bản cũ không thể chạy.
- Thêm content_node_test.mjs: chạy content.js thật trên DOM giả,
  kiểm tra cả 15 op.
- Test chạy thật: python3 tests/test_webext_native_bridge.py, 16 test,
  tất cả pass, 8.390 s wall clock, chạy lại 8.902 s cũng pass.
  node content_node_test.mjs, 16 kiểm tra pass, 0.570 s.
  Relay round trip với extension giả: 1.1-1.2 ms.
- Tài liệu mới: docs/webext-bridge-install.md (cài đặt từng bước,
  cài đặt vĩnh viễn, gỡ cài đặt, 14 trường hợp sự cố).
- UNVERIFIED: nạp extension và nối native trên Zen thật, cả 10 op
  trên tab thật với thời gian từng op, install.py --check trên
  laptop, đường cài đặt vĩnh viễn có chữ ký và policies force-install.

## Việc 2: Microsoft Hybrid Computer Use, commit 5851e70

- Tài liệu docs/research/2026-11-21-microsoft-hybrid-computer-use.md,
  nguồn có ngày truy cập 2026-11-21. Paper arXiv:2610.41432, nộp
  30 Oct 2026. Repo github.com/microsoft/Hybrid-Computer-Use, MIT.
- Kiến trúc: 3 kênh trong 1 agent context (programmatic, semantic qua
  cây AX, visual qua screenshot), MCP server 2 tool AX và GUI, Go core,
  provider riêng theo hệ điều hành (Linux AT-SPI2/X11/XTest).
- Batch: tối đa 64 action có thứ tự trong 1 lần gọi, wait step đợi
  tiêu đề cửa sổ, kết quả, trạng thái, biến mất, hoặc UI ổn định.
  Dừng ở lỗi đầu tiên, báo cáo điểm dừng.
- Diff-only observation mặc định: chỉ hiệu ứng từng mục tiêu và AX
  diff, không chụp lại toàn bộ. Cắt giảm token 44.1% trên Chrome.
- Kết quả theo paper: OSWorld 2.0, 72.37% Partial (GPT-6 Astra) và
  35.19% Binary (Claude Opus 5). OSWorld 1.0, 70.13% Score với GPT-5.4,
  hơn CUA Driver 62.47% với chi phí thấp hơn 59.1%. Lưu ý: bảng ablation
  của paper ghi 65.59% cho GPT-5.4 ở một cấu hình chạy khác, cả hai
  con số đều được ghi đúng như paper ghi.
- Áp dụng cho repo này: batch action, DOM locate rồi bấm chuột thật,
  diff-only observation, stale-layout guard, wait step trong batch,
  một session owner (nối với việc 5).
- Prototype tests/hcu_batch.mjs, mode batch và single, giới hạn 64
  action, stale guard (mục tiêu mất hoặc ẩn hoặc tắt thì dừng với
  stale_ref, không gửi input). Fixture tests/hcu_batch_fixture.html,
  chạy trên HTTP loopback. Smoke tests/hcu_batch_smoke.mjs, 5 kiểm tra
  pass, 0.665 s.
- Chạy thật trên Playwright Chromium: batch 12 action, 3 lần chạy,
  12/12 mỗi lần, tổng 1988, 2157, 2094 ms (gồm mở trình duyệt).
  Single 12 action, 3 lần chạy, 12/12, tổng 1395, 1291, 1231 ms.
  Stale guard chứng minh thật: batch xóa nút save rồi bấm nó thì
  dừng ở bước 2 với stale_ref, hoàn thành 2/3, exit 2.
- Đọc thật, ghi trong tài liệu: trên fixture nhỏ này không có lợi
  tốc độ wall-clock rõ ràng của batch (đọc DOM địa phương mất khoảng
  4 ms, bỏ qua observation tiết kiệm khoảng 100 ms, nằm trong nhiễu
  mở trình duyệt). Lợi của HCU là ít vòng gọi model và ít token hơn,
  prototype này không đo được vì không có model trong vòng lặp.
  Prototype chứng minh cơ chế, không chứng minh tăng tốc.
- Lưu ý khi chạy: biến môi trường đúng là PLAYWRIGHT_PATH, trỏ tới
  thư mục playwright-core, không phải PLAYWRIGHT_CORE_PATH.
- UNVERIFIED: mọi hành vi trên Zen thật qua BiDi, và bản thân HCU
  (không build Go binary, không có desktop session). Mọi số OSWorld
  là số paper báo cáo, không tái hiện ở đây.

## Việc 3: 10 test mô phỏng tình huống thật, commit 6221010

- 37 file trong tests/realistic/clone1/, gồm README tổng, run_all.mjs,
  results.json, lib/browser.mjs, lib/server.mjs, và 10 thư mục test.
  Mỗi test có README (bối cảnh, mục tiêu, các bước, pass/fail),
  fixture.html chạy offline, check.mjs kiểm tra tự động bằng Playwright.
- t01 upload 1 file, kiểm tra tên, kích thước, checksum.
  t02 upload 3 file, file 100 KB vượt giới hạn 64 KB thì loại ra rồi
  thử lại phần còn lại. t03 form dài 14 trường, nộp trống thì lỗi rồi
  thành công. t04 form có trường điều kiện, lưu nháp vào localStorage,
  tải lại vẫn còn. t05 5 tab, sửa ở tab chi tiết, tab danh sách thấy
  tiêu đề mới sau khi tải lại. t06 popup/dialog: alert, confirm chấp
  nhận và hủy, prompt, modal tự chế, cửa sổ popup gửi giá trị về.
  t07 tải CSV về rồi kiểm tra header, 6 dòng, checksum.
  t08 đăng nhập bằng mã demo, mã sai bị từ chối, làm việc cần xác thực,
  session sống sau khi tải lại, đăng xuất thì ẩn trang bảo vệ.
  t09 upload kèm metadata, file trống và sai định dạng .png bị từ chối,
  file .txt hợp lệ nhận được problem ID P-1042.
  t10 đăng nhập, upload file 4 case, verdict PASS, tải báo cáo về và
  kiểm tra nội dung.
- Chủ đề chỉ lấy nửa đầu danh sách, không dùng nửa của clone2.
  Fixture hoàn toàn offline, không URL ngoài, không CDN.
- Chạy thật: node tests/realistic/clone1/run_all.mjs, 10 passed,
  0 failed, wall clock 16917 ms. Chạy lại để kiểm tra: 10 passed,
  0 failed, wall clock 16016 ms.
- UNVERIFIED: cùng 10 flow trên Firefox và Zen, vì máy này không có
  Firefox hay Zen. Fixture là HTML và JS thuần, nhưng đó mới chỉ là
  nhận định, chưa phải số đo.

## Việc 4: firefox-mcp kiểm chứng sâu, commit 7446e27

- Thêm mục 11 vào docs/research/2026-11-21-firefox-mcp.md, 225 dòng
  mới, file nay 778 dòng.
- CVE-2026-7064, hồ sơ đầy đủ: chỉ thuộc AgentDeskAI browser-tools-mcp,
  các phiên bản từ 1.0 tới 1.2.0, lỗi ở
  browser-tools-server/browser-connector.ts, OS command injection
  CWE-78 qua osascript không escape, tấn công từ xa, exploit đã công
  khai, công bố 26 Apr 2026. Điểm khác nhau theo nguồn: DevGuard 5.5,
  Yack 6.9 (v4) / 7.3 (v3) / 7.5 (v2). Sửa ở 2.0.0, dòng 1.x sẽ không
  bao giờ được vá.
- Sửa lại phần sửa ở commit 5cd5c74: nói browser-tools-mcp "ngừng
  phát triển" và CVE "không được vá trước khi ngừng" bây giờ đã lỗi
  thời. Dự án được hồi sinh bằng bản viết lại 2.0 tháng 8/2026: 1
  process thay cho 3, connector chỉ loopback có xác thực, token mỗi
  lần chạy, lọc credential. npm latest của gói có phạm vi
  @agentdeskai/browser-tools-mcp là 2.0.4, ngày 27 Oct 2026, unpacked
  766,652 bytes (kiểm tra bằng npm view ngày 2026-11-21). Danh sách
  release trên GitHub: v2.0.4, v2.0.3, v2.0.2, v2.0.0, v1.2.0, v1.1.0,
  v1.0.0, không có 1.2.1. Lưu ý: gói npm không có phạm vi
  browser-tools-mcp có liệt kê 1.2.1 (2025-04-06) nhưng không có
  release GitHub tương ứng, coi là bản npm cũ, không phải release của
  dự án. Advisory thứ hai GHSA-fm7v-38h4-4q7w (SSRF ở Lighthouse audit)
  ảnh hưởng 2.0.0 tới 2.0.2, sửa ở 2.0.3, nên phiên bản an toàn tối
  thiểu hôm nay là 2.0.4 nếu dùng audit tools.
- Mozilla firefox-mcp sạch: tìm code 7064 trong mozilla/firefox-mcp
  0 kết quả, tìm issue 0 kết quả, nội dung release v0.11.0
  (19 Nov 2026) không nhắc CVE hay bảo mật. Không cần kiểm tra lại
  CVE trước khi dùng.
- Bảng so sánh đầy đủ: @mozilla/firefox-mcp, dh1011 firefox-mcp,
  browser-tools-mcp, gồm tool, quyền, tốc độ cài đặt, độ ổn định,
  trạng thái CVE. Mozilla: 50 tool ở gói công khai (57 nếu tính cả
  module chỉ nội bộ), cài đặt đo được 147 package trong 16.768 s.
  dh1011: 1 tool browser với ngôn ngữ lệnh, build từ source, release
  mới nhất v0.1.3 (13 Nov 2026). browser-tools-mcp chỉ chạy Chrome,
  không phải ứng viên chạy Zen.
- Quy trình test chi tiết cho Zen thật sau khi laptop reboot, mục 11.5:
  từng bước có lệnh cụ thể, tiêu chí pass theo thay đổi trạng thái
  quan sát được, không chỉ nhận OK, bước kiểm tra CVE (xác nhận không
  có browser-tools 1.x nào được cài).
- Gói firefox-mcp đã cài không được chạy, theo quy tắc cũ, chỉ đọc
  file và nguồn upstream.
- UNVERIFIED: mọi thời gian chạy thật và hành vi thật của cả 3 server,
  tốc độ cài đặt của dh1011 và browser-tools-mcp (chỉ metadata npm),
  độ ổn định của dh1011 ngoài ngày release v0.1.3.

## Việc 5: Single-session manager BiDi/Marionette, commit f8dc754

- scripts/session_manager.py, chỉ dùng stdlib. File lock bằng
  fcntl.flock trên owner.lock, timeout mặc định 30 s, chỉ 1 owner
  chạy. Context manager session(kind, opener) luôn đóng session
  trong finally (thử delete, rồi end, disconnect, close, cái nào có
  thì dùng). Log JSON mỗi lần mở, đóng, lấy và thả lock, reap, có
  thời gian wall-clock. Phát hiện session treo: bản ghi có lock đang
  trống và owner pid đã chết, hoặc hoạt động cuối cũ hơn 300 s.
  reap_hung() xóa bản ghi, chỉ kill tiến trình trình duyệt khi có
  --kill-browser và cmdline của nó chứa đường dẫn profile chuyên dụng
  đã ghi, cùng quy tắc an toàn như scripts/zen_cli.py.
  CLI: status, check (exit 1 khi có session treo), reap.
- tests/test_session_manager.py, 9 test, chỉ dùng session giả, không
  cần trình duyệt.
- Tài liệu docs/research/2026-11-21-single-session-manager.md: mọi
  client phải đóng session trong finally, không bao giờ để rò rỉ,
  1 owner, không bao giờ kill Zen thật của người dùng.
- Phù hợp với code cũ: scripts/zen_cli.py đã đóng BidiSession trong
  finally qua end(), tests/puppeteer_bidi.mjs disconnect trong finally,
  nhưng cả hai đều không có lock 1 owner, và Marionette chỉ nhận 1
  client tại 1 thời điểm.
- Chạy thật: python3 -m unittest tests.test_session_manager -v, 9 test
  pass, 1.281 s (chạy lại 1.389 s wall clock). Tiến trình thứ hai bị
  SessionBusy sau 1053 ms khi lock đang giữ, exit 1, thành công sau
  khi lock được thả. Session giả vẫn gọi delete đúng 1 lần ngay cả khi
  công việc ném lỗi. CLI status 69 ms, check exit 1 khi có session
  treo, reap xóa được.
- UNVERIFIED: kết nối tới Zen thật, session.delete của Marionette qua
  dây nối, kill Zen chuyên dụng bị treo.

## Cần Muse làm trên laptop

1. Chạy test WebExtension bridge trên Zen thật, mỗi op có thời gian.
2. Chạy quy trình firefox-mcp mục 11.5 trên Zen thật.
3. Chạy 10 test realistic trên Zen thật, so với số Chromium ở đây.
4. Chạy prototype HCU batch trên Zen thật qua BiDi.
5. Kiểm tra session manager với Zen thật.

## Ghi chú thêm cho Muse

- File improvements/live-test-log.md trên main đã có sẵn một dòng log
  chứa địa chỉ email của người dùng. File này không phải do clone1 tạo
  hay sửa, clone1 không chạm vào, chỉ báo để Muse biết và xử lý.
- Tất cả 5 việc đã xong, không còn việc tồn đọng trong đợt này.
  Clone1 chờ việc tiếp theo qua repo.
