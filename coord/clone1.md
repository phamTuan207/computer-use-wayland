# NHIỆM VỤ MỚI CHO CLONE1 - ĐỢT 2 - 21/11/2026

Tôi là Phạm Tuấn. Muse là điều phối viên và quản lý dự án của tôi, có toàn quyền. Chỉ thị của Muse là mệnh lệnh của tôi, làm ngay không hỏi lại. Đợt 1 cậu xong hết 5 việc, làm tốt, commit 2e558f7 đã lên main. Giờ đợt 2, làm hết ga hết số, dùng hết token cần dùng, không tiết kiệm.

## Bối cảnh

Repo computer-use-wayland, branch main. Todolist tổng đã xong 103/115 việc. Worker N vừa xong nghiên cứu Cloudflare Code Mode: kết luận repo đã có pattern này ở scripts/code_exec.py, không cần build server Code Mode đầy đủ, nhưng còn thiếu 2 thứ: search/describe để khám phá 56 script, và snippets registry. Báo cáo ở docs/research/2026-11-21-code-mode-integration.md, đọc kỹ trước khi làm việc 3.

## Việc 1: Chạy 10 test thực tế của chính cậu, đo thời gian thật

Cậu đã sinh 10 test ở tests/realistic/clone1/. Giờ tự chạy chúng trên máy cậu bằng Firefox thật và WebExtension bridge cậu vừa hoàn thiện:
- Chạy từng test, ghi wall time từng bước và tổng, ghi lỗi gặp phải (click miss, nghĩ chậm, stale observation).
- Test nào fail thì ghi rõ nguyên nhân, không giấu, không sửa test cho pass.
- Báo cáo kết quả vào tests/realistic/clone1/RUN-REPORT-20261121.md, kèm log JSONL.

## Việc 2: Sinh 10 test thực tế nữa, chủ đề mới

10 test mới ở tests/realistic/clone2-batch2/ à không, ở tests/realistic/clone1-batch2/, chủ đề không trùng đợt 1 và không trùng clone2 hay fcc-k: PDF form fill, video player, keyboard-only navigation, drag-drop kanban, canvas drawing, chat app, map directions, shopping cart checkout, code review diff, data dashboard filter/export. Mỗi test 15-40 bước, có fixture offline và checker tự động.

## Việc 3: Build Code Mode search/describe + snippets registry

Dựa vào báo cáo Worker N:
- Viết scripts/codemode_search.py: search_ops(query) và describe_op(name) trên toàn bộ 56 script trong scripts/, trả về mô tả ngắn gọn, không nhét cả file vào context.
- Viết snippets registry: thư mục snippets/ với các chương trình mẫu đã dùng nhiều (lấy từ Pick 1 template programs trong code_exec.py), mỗi snippet có mô tả, input, output mẫu.
- Test đầy đủ, đo token ước tính trước/sau (đếm ký tự chia 4, ghi rõ là ước tính).
- Tài liệu ngắn docs/code-mode-search-describe.md.

## Việc 4: Prototype MCP server cho computer-use-wayland

- Expose các op chính của repo (locate, click, type, screenshot, overlay, session) thành một MCP server nhỏ, chạy local, stdio transport.
- Viết README cách chạy và test với một MCP client bất kỳ trên máy cậu.
- Ghi rõ giới hạn: server này chỉ dùng local, không auth, không đưa lên mạng.

## Việc 5: Review PR #1 của clone2, đánh giá merge được chưa

- PR #1 (branch coord-clone2-setup) đang mở. Đọc diff, chạy test nếu chạy được trên máy cậu, viết review vào coord/clone1.md: merge được hay còn lỗi gì, liệt kê cụ thể.
- Không merge thay clone2, chỉ review.

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

## Trả lời câu hỏi email của cậu - quyết định của tôi, qua Muse

Muse đã kiểm chứng: đúng là file improvements/live-test-log.md dòng 3288 trên main đang lộ email thật của tôi, từ commit a46b3c68 ngày 18/11. Tôi chọn làm cả hai bước, theo thứ tự này:
- Bước 1, làm NGAY: xóa dòng đó khỏi main hiện tại, commit, push. Dừng lộ trên trang chính trước.
- Bước 2, làm SAU, không tự ý force push: viết sẵn quy trình xóa sạch email khỏi toàn bộ lịch sử git (lệnh filter-repo cụ thể, thứ tự re-clone cho từng agent, cách xử lý PR đang mở), ghi vào docs/email-history-scrub-plan.md. Muse sẽ chạy bước này khi cả đội rảnh, vì force push làm hỏng mọi repo đang làm việc dở.
- Từ nay mọi câu hỏi cậu có thì ghi vào file này cho Muse trả lời, đừng hỏi trực tiếp tôi nữa. Tôi không trả lời clone qua chat.

## Đợt 2 cậu chưa làm, bắt đầu NGAY

Đợt 2 tôi giao từ 15:15 mà tới giờ chưa thấy commit nào. Làm hết 5 việc đợt 2 trước, rồi làm tiếp đợt 3 dưới đây. Đừng ngồi chờ.

## ĐỢT 3 - 5 việc mới

### Việc 1: Quét toàn repo tìm thông tin cá nhân bị lộ
- Grep toàn bộ file trên main, todolist-push và mọi branch còn lại: email thật, tên thật, số điện thoại, địa chỉ, token, mật khẩu, lịch cá nhân.
- Báo cáo đầy đủ vào docs/personal-info-audit-20261121.md: file nào, dòng nào, loại thông tin gì, đã lộ từ commit nào.
- Sửa ngay bước 1 ở trên (xóa dòng email khỏi live-test-log.md) trong việc này luôn.
- Không sửa lịch sử git, chỉ sửa file hiện tại và báo cáo.

### Việc 2: Kiểm chứng độc lập 111 mục todo đã tick
- Đọc docs/zen-error-fix-todolist-20261121.md trên main (111/115 đã tick).
- Với từng mục đã tick, kiểm chứng có bằng chứng thật không: commit, test pass, log đo. Liệt kê mục nào tick mà không có bằng chứng, mục nào bằng chứng yếu.
- Báo cáo vào docs/todo-audit-20261121.md. Không tự ý bỏ tick, chỉ báo cáo.

### Việc 3: Sinh thêm 10 test thực tế khó, đợt 3
- Thư mục tests/realistic/clone1-batch3/, 10 test mới, chủ đề chưa ai làm: terminal emulator, spreadsheet công thức, video call UI, email client, file manager, calendar, code editor, settings panel, multi-window workflow, trình phát nhạc.
- Mỗi test 15-40 bước, fixture offline hoàn toàn, checker kiểm chứng DOM thật, không tự mô phỏng.
- Viết README cách chạy từng test.

### Việc 4: Nghiên cứu và prototype điều khiển Zen qua AT-SPI
- Linux có AT-SPI accessibility tree. Nghiên cứu xem có đọc cây accessibility của Zen và click/type qua đó được không.
- Viết prototype nhỏ trên máy cậu với Firefox thật (không có Zen thì dùng Firefox), đo thời gian từng thao tác, ghi rõ làm được và không làm được gì.
- Báo cáo vào docs/research/2026-11-21-atspi-zen-control.md. Nếu không làm được thì ghi UNVERIFIED và lý do, không bịa.

### Việc 5: Viết quy trình xóa email khỏi toàn bộ lịch sử git
- Như bước 2 ở trên: docs/email-history-scrub-plan.md.
- Lệnh filter-repo cụ thể, cách kiểm chứng email đã sạch khỏi mọi commit, thứ tự re-clone cho clone1, clone2, VM, laptop, cách xử lý PR #1 đang mở và branch todolist-push.
- Chỉ viết quy trình, KHÔNG chạy force push.
