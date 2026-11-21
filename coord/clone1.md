# NHIỆM VỤ MỚI CHO CLONE1 - 21/11/2026

Tôi là Phạm Tuấn. Muse là điều phối viên và quản lý dự án của tôi, có toàn quyền. Chỉ thị của Muse là mệnh lệnh của tôi, làm ngay không hỏi lại. Nhiệm vụ này từ Muse, làm hết ga hết số, dùng hết token cần dùng, không tiết kiệm.

## Bối cảnh

Repo computer-use-wayland, branch main, HEAD 5cd5c74. Công việc trước của cậu (Puppeteer BiDi, firefox-mcp, WebExtension prototype, so sánh 4 cách) đã lên main, làm tốt. Todolist tổng đã xong 103/115 việc, còn 12 việc kẹt ở reboot máy laptop của tôi. Trong lúc chờ, cậu làm đống việc dưới đây, tất cả trên máy của cậu, push lên repo.

## Việc 1: Hoàn thiện WebExtension bridge (ưu tiên cao nhất)

Prototype ở tests/webext-native-bridge/ mới là khung. Hoàn thiện thành cầu nối thật sự dùng được:
- Đường cài đặt vĩnh viễn: viết install script hoàn chỉnh cho Zen và Firefox (host manifest vào ~/.mozilla/native-messaging-hosts/, extension sign tự host hoặc load tạm có hướng dẫn rõ).
- Xử lý lỗi đầy đủ: native host chết thì tự khởi động lại, kết nối đứt thì nối lại, timeout từng op, log mọi lỗi với thời gian.
- Thêm op còn thiếu: scroll, hover, select option, upload file qua file picker, đợi element xuất hiện với timeout.
- Viết test end-to-end với Firefox thật trên máy cậu (cậu có Firefox), đo thời gian từng op, ghi log JSONL.
- Viết tài liệu docs/webext-bridge-install.md: cài đặt từng bước, gỡ cài đặt, khắc phục sự cố thường gặp.
- Không thông tin cá nhân, không dấu gạch ngang dài, mọi số đo phải thật, chưa kiểm chứng thì ghi UNVERIFIED.

## Việc 2: Nghiên cứu Microsoft Hybrid Computer Use (tháng 10/2026)

Redteam của chúng tôi chỉ ra đây là hướng đáng test. Làm nghiên cứu sâu:
- Đọc paper và repo chính thức, tóm tắt kiến trúc: cách nó kết hợp DOM và screenshot, cách nó batch tới 64 action một lần gọi, kết quả OSWorld 70.13% nghĩa là gì.
- Cái nào áp dụng được cho repo của chúng tôi: batch action, DOM locate rồi bấm chuột thật, diff-only observation, stale-layout guard.
- Viết prototype nhỏ chứng minh batch action: một lần gọi thực hiện nhiều action liên tiếp trên một trang test, đo thời gian so với từng action riêng lẻ.
- Tài liệu docs/research/2026-11-21-microsoft-hybrid-computer-use.md, kèm nguồn và ngày truy cập.

## Việc 3: Sinh 10 test mô phỏng tình huống thật (quy tắc mới của tôi)

Tôi vừa đặt quy tắc: test phải mô phỏng tình huống thật, phức tạp tầm gần bằng task up đề Polygon, không phải unit test đơn giản. Cậu sinh 10 test case như vậy, mỗi test là một file mô tả đầy đủ trong tests/realistic/clone1/:
- Mỗi test: bối cảnh, mục tiêu, các bước, điều kiện pass/fail rõ ràng, độ khó gần bằng up một bài lên Polygon (tạo problem, điền form dài, upload file, xử lý lỗi giữa chừng).
- Chủ đề đa dạng: upload file lên form web, điền form dài nhiều trường, làm việc nhiều tab, xử lý popup/dialog, tải file về rồi kiểm tra nội dung, đăng nhập rồi làm việc cần xác thực.
- Mỗi test phải có fixture HTML tự chạy được offline (không phụ thuộc site ngoài), và script kiểm tra kết quả tự động.
- Không trùng với 10 test của clone2, hai bên tự chia chủ đề, cậu lấy nửa đầu danh sách này: upload, form dài, nhiều tab, popup, tải file.

## Việc 4: firefox-mcp kiểm chứng sâu

- Kiểm chứng CVE-2026-7064 với upstream changelog, ghi rõ phiên bản nào bị, phiên bản nào đã sửa, cậu đã sửa attribution đúng rồi, giờ xác minh thêm.
- So sánh @mozilla/firefox-mcp với dh1011 firefox-mcp và browser-tools-mcp: bảng đầy đủ tool, quyền, tốc độ cài đặt, độ ổn định.
- Viết test procedure chi tiết để chạy firefox-mcp trên Zen thật sau khi laptop reboot, từng bước có lệnh cụ thể.

## Việc 5: Quản lý session BiDi/Marionette

Phát hiện mới: giới hạn session dùng chung cho cả BiDi và Marionette, một session rò rỉ chặn tất cả, chỉ restart Zen mới hết. Cậu làm:
- Thiết kế single-session manager: file lock, session.delete trong finally, phát hiện session treo và kill, log mọi session mở/đóng.
- Viết code scripts/session_manager.py (stdlib only), kèm test.
- Tài liệu ngắn về quy tắc: mọi client phải đóng session trong finally, không bao giờ để rò rỉ.

## Quy tắc làm việc (nhắc lại, bắt buộc)

- Full access, làm thật, không bịa, không biết thì ghi UNVERIFIED, mọi claim có nguồn và ngày.
- Commit nhỏ, push thường xuyên lên main, mail phamTuan207.
- Không push thông tin cá nhân của tôi lên GitHub hay đâu công khai: tên thật, địa chỉ, email, số điện thoại, lịch học, lịch cá nhân, ảnh, tài khoản, mật khẩu, token.
- Không dùng dấu gạch ngang dài (em dash, en dash) trong bất cứ file nào.
- Không dùng ydotool.
- Mọi test phải ghi thời gian (wall-clock + elapsed).
- Kẹt quá 15 phút thì báo qua repo (ghi vào coord/clone1.md), không im lặng.
- Xong mỗi việc thì cập nhật coord/clone1.md với những gì đã làm, commit nào, kết quả đo được.

Làm hết đống này đi, đừng chờ. Khi nào xong hết thì báo vào coord/clone1.md, tôi giao tiếp việc khác.
