# Báo cáo phân công Maximum MacShell glass

Bản công khai rút gọn. Log lệnh, ảnh, bản export và thông tin môi trường được lưu riêng; không chứa đường dẫn cá nhân, mã tiến trình hoặc thông tin xác thực.

## Phân công

| Vai trò | Công việc | Giới hạn |
|---|---|---|
| Điều phối chính (root) | Quyết định shader, review nguồn/helper, vận hành GUI, xem ảnh, **viết gate `ROOT-REVIEWED.json`**, integration/acceptance, quyết định công bố | Chỉ root điều khiển GUI và **ghi gate**; root sở hữu commit/push. |
| Worker harness/build | Tạo và sửa wrapper cho compositor mới, build riêng, cài immutable theo hash | Không ghi đè thư viện đang được desktop dùng; không hot-swap. |
| Worker native (AGY) | Sửa comment source cuối và build `reference-final` | Backend được chấp nhận chỉ đọc; không thay ABI/protocol/pin; **không** viết gate. |
| Reviewer độc lập | Review correctness và đánh giá hình ảnh so với ảnh tham chiếu thật | Kết luận của reviewer không thay cho người dùng duyệt thẩm mỹ. |
| Worker tài liệu/verification (CommandCode) | Chuẩn bị bản chụp repo riêng, chạy các lệnh đã review, tổng hợp bằng chứng thật | Không sửa test/data để đạt kết quả xanh. |

## Tiến triển đã có bằng chứng

- Phase1 transparency đã commit 77737df và push riêng (clean bisect point, tách khỏi candidate native): brightness trung tính, không adaptive dim.
- Các bước 1–5 đã triển khai trong candidate: Snell, normal SDF, ba IOR, ánh sáng rim/meniscus có hướng, blur 24 taps và mipchain riêng.
- Calibration dựa trên ảnh tham chiếu thật đổi thickness 12 → 15 logical px, radius 3 → 3.6 logical px tại blur_strength 0.42, tăng gain ánh sáng có hướng và giảm outline chữ xuống 1 px / alpha 0.30. Phiên live private nested: shader `ready` / `versionCheck match`, năm capture 1920×1200, cleanup exit 0; log GPU radius 3.600 / calcLOD 0.381 (suy từ công thức, không phải đo thời gian GPU). Root xem đủ năm ảnh; judge độc lập mở crop của calibration, phase3 và client B rồi chọn calibration để tích hợp, chờ người dùng duyệt.
- Native cuối `reference-final`: patch `0e108b69…`, library `21553b5b…`; delta so calibration chỉ **comment** ở bốn file source; indicator source **không đổi** (`e4fe670e…`). Gate `reports/reference-final/ROOT-REVIEWED.json` do **root** viết (`success: true`); AGY chỉ build `reference-final`, **không** viết gate.
- Phiên live cuối `final-live-01`: shader `ready` / `versionCheck match`, năm capture 1920×1200, session và compositor exit 0, library `21553b5b…`; năm crop **byte-identical** với calibration (`reports/reference-final/crop-byte-comparison.json`), root mở đủ năm ảnh nên verdict của judge độc lập áp dụng nguyên; residual vẫn còn: chữ trắng yếu trên nền sáng, trung tâm phẳng/sắc hơn MacShell, crop wallpaper là nền đen có lưới.
- Sự cố report-shell: formatter báo cáo của worker đặt backtick markdown trong dấu nháy kép nên shell chạy `indicator` đứng riêng; root đã dừng **đúng** shell/indicator đó và ngắt lượt AGY sau khi build xong; plugin native **không** reload, artifact build **không** đổi (`reports/reference-final/report-shell-incident.json`). Claim ghost/perf bị bác; không có bằng chứng ghost hay perf.
- Điều phối chính bổ sung điều kiện phục hồi EGL theo display, context và cả read/draw surfaces. Cumulative patch bao gồm thay đổi này.

## Verification calibration

Native build và immutable install đã hoàn tất, exit 0; indicator compile với `-Wall -Wextra -Werror -O2` exit 0. Năm module focused chạy trên bản chụp commit riêng: 57 tests, 57 pass, 0 skip, exit 0 (0.083 s). Snapshot chứa cumulative patch và indicator cuối; backend kiểm tra đúng pin. Hash file được bảo vệ khớp trước và sau. Capture calibration live: năm ảnh 1920×1200, shader `ready` / `versionCheck match`, cleanup exit 0. Đây là focused checks, chưa phải full acceptance. Phê duyệt thẩm mỹ của người dùng còn chờ.

## Acceptance prepush (đã thực chạy)

Full9 prepush acceptance đã chạy trên candidate private bằng wrapper đã review (exit từng lệnh và tên test fail nằm trong log private):

- `unittest discover` exit 1: **2 failure** ở `test_indicator_material` — `test_fixed_white_ink_and_no_dark_inner_rim` (đếm `cairo_set_source_rgb(cr,.98,.99,1)` là 4 thay vì 2 sau thay outline) và `test_parsed_constants_are_meaningful` (liquid alpha `0.18` không còn, giá trị đã chọn là `0.06`). Hai assertion hardcode cũ này mâu thuẫn với thay đổi hình ảnh **có chủ đích** của candidate; đây **không** phải phê duyệt thẩm mỹ của người dùng.
- `check-perf-evidence.py` (thường và `-O`) cùng `test_perf_evidence`: lỗi truy vấn Git object lịch sử (R5) vì cây private giữ bởi `git archive` thiếu lịch sử. Đã sửa **môi trường** bằng fetch read-only lịch sử main vào repo private (không checkout/reset/merge; byte tracked không đổi) — đây là bổ sung bối cảnh kiểm chứng, **không** sửa test/data/checker để né.
- `focused` (5 module optics): 57/57, 0 skip, exit 0; cả 5 node suite exit 0.

Candidate **không** đạt toàn bộ test không đổi; **không** có tuyên bố green hay full acceptance. Quyết định công bố thuộc root.

## Giới hạn còn mở

Nếu mip allocation/generation thất bại, fallback vẫn lấy mẫu full resolution; không giữ nguyên downscale hoặc chi phí baseline. Chưa có runtime proof cho 10-bit/FP16. Không suy từ build thành kết luận shader đã chạy đúng ở mọi format. Judge độc lập ghi residual so với MacShell: trung tâm kính phẳng/sắc hơn, chữ trắng yếu trên nền sáng, crop wallpaper là nền đen có lưới. Main desktop vẫn dùng thư viện cũ cho đến fresh login; không logout, reload/unload hoặc hot-swap plugin trong mission này.

## Artifact (đường dẫn tương đối)

- Build + focused calibration: `reports/reference-calibration/result.json`, `reports/reference-calibration/raw-01/`.
- Build native cuối (AGY) + gate: `reports/reference-final/result.json`, `reports/reference-final/result.md`, `reports/reference-final/ROOT-REVIEWED.json`, `reports/reference-final/raw/`.
- So crop byte final vs calibration: `reports/reference-final/crop-byte-comparison.json`.
- Sự cố report-shell: `reports/reference-final/report-shell-incident.json`.
- Phiên live cuối: `final-live-01/` (run.json, stage1-*.meta.json, compositor.stdout).
- Phiên calibration live: `calibration-live-01/` (run.json, stage1-*.meta.json, compositor.stdout).
- Đánh giá nguồn/ảnh độc lập: `reports/final-source-review.md`, `reports/reference-visual-calibration.md`.
- Probe mip GPU STEP5: `step5-probe-01/mip-gpu-evidence.json`.
- Acceptance prepush: `reports/commandcode-final/prepush-01/`, `reports/commandcode-final/prepush-02/`, `reports/commandcode-final/acceptance-result.json`, `reports/commandcode-final/preserve/`.
- Brief + raw CLI: `cmd-final-review-brief.md`, `cmd-acceptance-brief.md`, `cmd-acceptance-failure-followup.md`, `agy-final-build-brief.md`, `opencode-*-brief.md`; output thô `opencode-*.stdout/stderr`.

## Model và quyền sở hữu

- Các lượt OpenCode trước bị rate limit; export model chỉ xác nhận được một số worker, không phủ hết model, mức reasoning hoặc chi phí. Không suy phần còn thiếu.
- Lượt AGY calibration/final chạy qua CLI có banner **Gemini 3.8 Flash medium** (fallback). Đây là banner CLI; model thực chưa được xác minh.
- Lượt CommandCode (audit docs + chuẩn bị acceptance) báo banner CLI **Command Code 1.82.3**, model **DeepSeek v4.1 Flash, high effort** (theo yêu cầu/quan sát). Đây là banner khai báo; provider billing chưa xác minh; không tuyên bố token.
- Các lượt Codex helper/review/judge kế thừa: model thực **chưa xác minh**; không tự gán model.
- Quyền sở hữu: root viết gate `ROOT-REVIEWED.json`, giữ commit/push/integration, GUI và quyết định công bố; AGY sở hữu `source-work/` + build `reference-final/` (comment native) nhưng **không** ghi gate; CommandCode chỉ audit docs công khai, chuẩn bị candidate và chạy acceptance sau gate. Không có tuyên bố tiết kiệm token/chi phí nào khi không có số đo.

## Chốt bản theo phản hồi người dùng

Người dùng đã duyệt vòng hiệu chỉnh 5 sau demo 45.027 giây. Root sở hữu các thay đổi chính xác trong hai file native qua năm vòng; AGY hết quota nên không được khởi chạy lại liên tục. CommandCode làm bulk build trong snapshot commit riêng bằng wrapper đã review, không sửa nguồn hoặc điều khiển GUI. Root mở đủ năm ảnh mỗi vòng; reviewer hình ảnh độc lập so với vòng trước và ảnh người dùng. Các ảnh/log giữ riêng.

Bản chốt: lớp trắng 2 px ít đục; vùng khúc xạ 6 px, thickness 21 px; blur mép 3 px, lòng 2.5 px. Native patch SHA256 `f7fd86cc3e4c6f9b83f217841e0c15d10a140d3e72a3545efcb85a82b8ad8028`; indicator giữ nguyên outline nhẹ. Native build/install exit 0, phiên thử mới shader ready/match và cleanup 0. Judge ghi nhận trong hơn, mép mềm hơn nhẹ; không thấy artifact mới rõ.

Bằng chứng cuối: `reports/user-tune-05/`, `user-tune-05-live-01/`; brief bulk `cmd-user-tune-05-brief.md`, raw output và build-record trong artifact tương ứng. Acceptance chốt dùng wrapper/run-checks đã review, chạy trước push và trên exact pushed tree; bằng chứng lưu `reports/approved-final/`. Root giữ integration, commit/push và cài manifest fresh-login; không thay plugin đang chạy. Những báo cáo trước nói chờ người dùng duyệt là trạng thái lịch sử, được thay bằng phê duyệt hiện tại. Hai assertion test material lịch sử vẫn được báo trung thực nếu còn fail; không có tuyên bố toàn bộ test xanh.
