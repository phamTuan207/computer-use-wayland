# Phân tích shader kính: trạng thái hiện tại

Tài liệu này thay cho bảng khoảng cách trước triển khai. Các bước 1–5 đã có trong candidate; điều đó không đồng nghĩa người dùng đã duyệt hình ảnh hoặc desktop chính đã chạy native mới.

| Bước | Kỹ thuật đã triển khai | Phạm vi và giới hạn |
|---|---|---|
| 1 | Khúc xạ Snell với IOR cơ sở 1.5 | Dịch tọa độ lấy mẫu theo tia khúc xạ và độ dày kính. |
| 2 | Normal giải tích từ SDF rounded-box và profile quartic | Dùng vùng kính thực, tách khỏi padding trong suốt; không đổi hình bao thành squircle để giả độ cong. |
| 3 | Dispersion qua ba lần `refract` với ba IOR | R/G/B có tia riêng; khác cách nhân một offset chung trong reference. |
| 4 | Rim có hướng và meniscus Gaussian | Nhánh indicator thay chồng bevel/Fresnel/specular cũ, bỏ term tối cứng bên trong; lớp wash/rim của client vẫn là phần riêng. |
| 5 | Disk blur 24 điểm có trọng số Gaussian, bán kính theo khoảng cách mép, mipmap riêng | Copy nguồn sắc trước preblur; tạo đủ mip, chọn LOD theo mật độ texel thực, giữ sample đã blur làm fallback. |

Nhánh mới chỉ dành cho namespace indicator có protocol region và glass box hợp lệ. Mỗi lần ghi sample tăng serial và vô hiệu hóa mip cũ; cache hit tái sử dụng chain phù hợp. Copy bằng shader áp swizzle nguồn, không ép mọi format thành RGBA8. Allocation bảo toàn READ/DRAW framebuffer; copy và draw phục hồi các binding đã chạm. Cleanup chỉ xóa GL objects khi render context hợp lệ, đồng thời phục hồi EGL context/surfaces trước đó.

Bằng chứng GPU của checkpoint STEP5 trước calibration: nguồn **XRGB8888**, internal **RGBA8**, sample **406×158**, **9 mip levels**, level 1 **203×79**, level cuối **1×1**, **GL error 0**. Log này chứng minh allocation/generation trên cấu hình đó. LOD khoảng **0.118** tại radius 3 px, scale 1 là giá trị suy từ công thức shader, không phải phép đo LOD hay thời gian GPU. Chưa có xác minh runtime cho 10-bit hoặc FP16.

Caveat fallback: nếu format được nhận nhưng allocation/generation mip thất bại, sample vẫn dùng full resolution. Đường fallback còn hoạt động, nhưng không giữ nguyên downscale hoặc chi phí của baseline. Chưa có số đo hiệu năng để kết luận chi phí 24×3 lần đọc texture mỗi pixel.

Calibration đã chạy trong compositor thử mới (private nested) với thickness **15 logical px** trước hệ số refraction, radius interior **3.6 logical px** tại `blur_strength=0.42`, gain ánh sáng có hướng và text outline **1 px / alpha 0.30**. Log GPU thật của phiên đó in ra sample **406×158**, **9 mip levels**, level 1 **203×79**, level cuối **1×1**, `interiorRadiusPx(scale1) 3.600`, `lod(density1) 0.381`, **GL error 0**; năm capture **1920×1200**, shader status `ready`, `versionCheck match`, cleanup exit 0. Giá trị LOD **0.381** của calibration là suy từ công thức shader theo mật độ texel; không phải phép đo LOD hay thời gian GPU. Đây là phiên compositor thử, không phải kích hoạt desktop chính.

Mục tiêu hình ảnh là gần reference nhưng hơi ít blur hơn; cần kiểm tra trong tương tác thật, không chỉ ảnh tĩnh. Không tuyên bố tương đương hoàn toàn với reference, runtime mip của reference, hay padding an toàn cho mọi scale/tham số. Đánh giá ảnh độc lập ghi nhận residual so với MacShell: phần giữa kính còn phẳng/sắc hơn, chữ trắng vẫn yếu trên nền sáng, và crop wallpaper là nền đen có lưới nên không đủ bằng chứng độ mềm nền tự nhiên. Phê duyệt thẩm mỹ của người dùng còn chờ; native mới trên desktop chính còn chờ phiên đăng nhập mới. Grain giữ 0; không có kết luận mới về grain hoặc shadow.

Calibration đã build/cài riêng thành công (exit 0), indicator compile exit 0. Năm module focused chạy trên snapshot commit riêng: 57 tests pass, 0 skip, exit 0. Năm capture calibration **1920×1200** đã có (shader `ready`, `versionCheck match`, cleanup exit 0) và root đã xem. Năm capture `final-live-01` **1920×1200** trùng byte với calibration (shader `ready`/`versionCheck match`, cleanup exit 0); gate `ROOT-REVIEWED.json` do root viết. Full9 prepush đã chạy thật trên candidate private: 2 failure `test_indicator_material` mâu thuẫn thay đổi hình ảnh có chủ đích, lỗi Git object lịch sử R5 đã sửa bằng fetch read-only (không sửa test/data); candidate không đạt toàn bộ test không đổi. Release cần full prepush acceptance rồi kiểm tra trên đúng cây đã push, log bằng chứng lưu riêng theo từng lần chạy, và còn chờ người dùng duyệt hình ảnh.
