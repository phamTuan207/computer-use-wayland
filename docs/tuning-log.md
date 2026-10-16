# Nhật ký hiệu chỉnh kính

Bản công khai rút gọn từ bằng chứng kiểm tra đã lưu riêng. Không chứa log thô hoặc thông tin môi trường cá nhân. Người dùng đã duyệt bản hiệu chỉnh cuối sau demo 45 giây.

| Checkpoint | Thay đổi | Bằng chứng và kết luận giới hạn |
|---|---|---|
| Baseline trung tính | Brightness 1, adaptive dim/boost 0, tint/noise 0 | Capture trong compositor thử mới; chữ trắng trên nền sáng còn khó đọc. |
| STEP1 | Snell, IOR 1.5 | Build riêng và phiên thử mới; shader ready, root xem đủ năm ảnh. Giữ truyền màu, thay đổi khúc xạ mép. |
| STEP2 | Normal rounded-SDF giải tích và độ dốc quartic | Phiên thử mới, năm ảnh được root xem; chưa thấy hồi quy độ trong ở các cảnh đã kiểm tra. |
| STEP3 | Ba IOR riêng cho R/G/B | Phiên thử mới, năm ảnh; dispersion nhẹ ở kích thước indicator, không kết luận từ công thức rằng hiệu ứng phải rõ bằng mắt. |
| STEP4 | Rim có hướng, meniscus; bỏ term tối cứng riêng indicator | Phiên thử mới, năm ảnh; root thấy rim dịu hơn, chữ trên nền sáng vẫn yếu. |
| STEP5 | Nguồn sắc riêng, 24 taps, mipchain thật | Phiên thử mới, shader ready, năm ảnh; root thấy optical/dark-grid sắc hơn. Đánh giá ảnh độc lập còn nhận thấy double-outline/whitewash, nên tiếp tục A/B client. |
| Probe STEP5 | Kiểm tra allocation/generation trên GPU | XRGB8888 → RGBA8; sample 406×158, 9 levels, level1 203×79, cuối 1×1, GL error 0. Radius 3 px tại scale 1 cho LOD tính toán khoảng 0.118. Không phải phép đo hiệu năng; chưa chạy xác minh 10-bit/FP16. |
| Client A/B | Giảm wash trắng và rim của client | Đã chụp đủ năm nền; judge chọn B trước khi có ảnh MacShell thật. Sau ảnh tham chiếu, judge yêu cầu mép cong và ánh sáng có hướng rõ hơn. |
| Phase3 text trước calibration | Outline 1.5 px / alpha 0.50 | Đã chụp đủ năm nền; judge thấy chữ quá đậm/rỗng, cần viền nhẹ hơn. |
| Calibration live | Thickness 15 px, radius 3.6 px tại blur_strength 0.42; gain ánh sáng có hướng; text 1 px / alpha 0.30 | Compositor thử mới (private nested), library calibration bất biến được nạp; shader `ready` / `versionCheck match`, năm capture 1920×1200, cleanup exit 0. Log GPU thật: radius 3.600, lod(density1) 0.381 (suy từ công thức mật độ texel, không phải đo thời gian GPU). Root mở đủ năm ảnh. |
| Đánh giá ảnh calibration | Judge độc lập chọn calibration để tích hợp, chờ người dùng duyệt | Judge mở 15 crop của calibration-live-01, phase3-live-01, client-b-live-01; thấy chữ đỡ rỗng hơn phase3, mép/kính dày hơn chút. Residual: trung tâm phẳng/sắc hơn MacShell, chữ trắng vẫn yếu trên nền sáng, crop wallpaper là nền đen có lưới. |
| Final live | Patch cuối `0e108b69…`, library `21553b5b…`; chỉ khác calibration ở comment source | Phiên `final-live-01`: shader `ready` / `versionCheck match`, năm capture 1920×1200, session/compositor exit 0; năm crop **byte-identical** với calibration; gate `ROOT-REVIEWED.json` do root viết (success true). Residual không đổi. |
| Acceptance prepush | Candidate private (patch cuối + indicator cuối + docs) | Full9 đã chạy: `discover` exit 1 với **2 failure** `test_indicator_material` (hardcode cũ 2/0.18 so với thay đổi có chủ đích 4/0.06); `checker`/`checker-O`/`test_perf_evidence` lỗi Git object lịch sử R5 — đã fetch read-only lịch sử main vào repo private (không sửa test/data); `focused` 57/57 và 5 node suite exit 0. Không đạt toàn bộ test không đổi; không có green/full claim. |

Các lỗi STEP5 đã được xử lý qua review: serial theo mọi lần ghi sample; không làm mất READ framebuffer khi allocation; gate theo indicator/region hợp lệ; copy nguồn sắc trước blur; hỗ trợ swizzle của XRGB qua shader copy; cleanup kiểm context và phục hồi EGL display/surfaces. Còn caveat: khi mip thất bại ở format được nhận, fallback vẫn trả chi phí full-resolution sampling.

Đích hiệu chỉnh là kính trong với khúc xạ và phản sáng có hướng. Người dùng đã duyệt bản hiệu chỉnh cuối sau demo; không tuyên bố tương đương hoàn toàn ảnh mẫu, hiệu năng hoặc hỗ trợ mọi format. Native mới trên desktop chính còn chờ phiên đăng nhập mới; các phiên thử không phải bằng chứng đã kích hoạt trên desktop chính.

Verification calibration thực chạy: native build và immutable install exit 0; indicator compile `-Wall -Wextra -Werror -O2` exit 0. Năm module focused: **57 tests, 57 pass, 0 skip, exit 0**, trên bản chụp commit riêng chứa patch và indicator cuối, backend đúng pin. Không thay test. Capture calibration live ghi shader `ready` / `versionCheck match`, năm ảnh 1920×1200, cleanup exit 0. Full9 prepush đã chạy thật trên candidate private: 2 failure `test_indicator_material` (mâu thuẫn thay đổi có chủ đích), lỗi Git object lịch sử R5 đã sửa bằng fetch read-only; candidate không đạt toàn bộ test không đổi. Release cần full prepush acceptance rồi kiểm tra trên đúng cây đã push; log bằng chứng lưu riêng theo từng lần chạy.

## Hiệu chỉnh cuối theo phản hồi người dùng

| Vòng | Thay đổi | Kết luận |
|---|---|---|
| 1–2 | Blur 2.2 rồi 2.5 px; thử dải phản sáng mảnh theo ảnh mép kính mới | Người dùng yêu cầu trắng rõ hơn và cong mạnh hơn. |
| 3–4 | Tăng thickness, dải sáng; thử lớp trắng đục và vùng mép 6 px | Người dùng yêu cầu giảm lớp trắng đục, giữ riêng vùng khúc xạ rộng. |
| 5 — được duyệt | Lớp trắng 2 px ít đục; khúc xạ 6 px, thickness 21 px; blur mép 3 px, lòng 2.5 px | Native build/install riêng exit 0; năm capture mới 1920×1200, shader ready/match, cleanup 0. Root và judge xem đủ năm ảnh. Demo thực 45.027 giây; người dùng chốt bản này. |

Patch được duyệt có SHA256 `f7fd86cc3e4c6f9b83f217841e0c15d10a140d3e72a3545efcb85a82b8ad8028`; indicator source không đổi từ bản outline nhẹ. Ánh sáng dùng normal quartic của Snell, lớp trắng và vùng khúc xạ có kích thước riêng. Mức blur là bán kính disk sampling trong shader. Không thêm dim hoặc lớp nền xám.

Giới hạn còn mở: chữ trắng trên nền rất sáng, 10-bit/FP16, hiệu năng và fallback mip. Không coi duyệt hình ảnh là full acceptance. Log acceptance mới được lưu theo commit trước push và sau push; giữ nguyên hai lỗi assertion material lịch sử nếu vẫn xuất hiện, không sửa test/fixture để xanh. Desktop chỉ nạp native mới ở fresh login.

## Xác minh desktop và cập nhật hợp đồng test

Sau khi người dùng tự đăng xuất/đăng nhập, desktop chính đã nạp đúng thư viện của bản được duyệt. Phiên điều khiển thật ghi shader `ready`, ABI `match`; root xem badge thật, lệnh chụp thành công, kết thúc session sạch và cursor guard trở về idle. Không reload/unload/hot-swap.

Theo yêu cầu xử lý hai lỗi cũ, chỉ cập nhật `test_indicator_material.py`: kiểm từng nhánh chữ trắng và outline 1 px / alpha 0.30 thay vì đếm số lệnh đặt màu; lấy vị trí/alpha wash thật từ source vào Cairo harness thay bảng cũ; giữ assertion thân trong suốt, midband bằng 0, wash nhẹ và bóng chỉ ngoài kính. Mẫu bóng được lấy trước khi vẽ wash để tách đúng thành phần. Ba material tests đã chạy và pass. Các kết quả fail phía trên là lịch sử trước lần sửa test này; full acceptance được chạy lại theo commit và lưu log riêng, không suy từ ba tests thành toàn bộ suite xanh.

Không thay đổi shader, indicator hoặc độ sáng chữ đã được người dùng duyệt. Các giới hạn 10-bit/FP16, hiệu năng và fallback mip vẫn giữ nguyên; chữ trên nền sáng được người dùng chấp nhận.

## Lựa chọn mới: khôi phục bản calibration trước các vòng giảm blur

Người dùng đánh giá lại trên desktop và yêu cầu quay về bản ngay trước vòng giảm blur đầu tiên. Trạng thái hiện tại thay thế lựa chọn tune05 ở các mục lịch sử: khôi phục nguyên patch calibration cuối đã công bố trước các vòng chỉnh viền trắng, SHA256 `0e108b69d002d2265cfb6600ded6c95b559b34f38020db825675c0fc6aa5d265`. Bán kính blur lòng kính 3.6 logical px tại profile 0.42, mép 0.45 lần bán kính đó; thickness 15 logical px và ánh sáng rim/meniscus có hướng của calibration. Không giữ các thay đổi viền trắng 2 px hoặc vùng mép 6 px từ tune05.

Tái sử dụng đúng thư viện immutable đã build và đã thử năm nền; không suy từ thay đổi hằng số ra một bản build mới. Indicator, outline chữ, profile trung tính và các kiểm tra material đã sửa giữ nguyên. Việc khôi phục desktop được chuẩn bị bằng manifest cho lần đăng nhập mới; không hot-swap hoặc tự logout. Các xác minh desktop tune05 phía trên chỉ là bằng chứng lịch sử, không phải bằng chứng bản calibration đã nạp trên desktop chính. Acceptance được chạy lại trước và sau push với log riêng theo commit. Phê duyệt hình ảnh calibration trên desktop vẫn chờ đánh giá lại của người dùng.
