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
