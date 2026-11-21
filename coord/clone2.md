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

