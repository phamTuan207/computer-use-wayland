# Phân tích shader kính: trạng thái hiện tại

Tài liệu này thay cho bảng khoảng cách trước triển khai. Các bước 1–5 đã triển khai. Người dùng đã duyệt hình ảnh bản hiệu chỉnh cuối; desktop chính cần đăng nhập mới để nạp thư viện mới.

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

## Bản hiệu chỉnh được người dùng duyệt

Sau các vòng demo, người dùng chọn bản có lớp trắng mỏng **2 logical px**, giảm độ đục và bỏ lớp trắng sữa phủ rộng. Vùng khúc xạ theo SDF rộng **6 logical px**, thickness **21 logical px** trước hệ số refraction 0.7. Ánh sáng phản chiếu có hướng dùng cùng normal quartic với tia Snell; các dải phản sáng trong vẫn nằm trong vùng mép.

Ở profile trung tính `blur_strength=0.42`, bán kính blur mép **3 logical px**, lòng kính **2.5 logical px**; chuyển mềm ở độ sâu 4.8–6 px. Bán kính mép theo knob và chặn ở 6 logical px để giữ giới hạn lấy mẫu đã review. Lớp trắng chính kết thúc ở 2 px; phản xạ phụ có hướng vẫn trải trong vùng khúc xạ 6 px. Đây là kích thước theo công thức shader, không phải phép đo từ ảnh. Giữ nguyên profile trung tính, grain 0, client B và outline chữ 1 px / alpha 0.30.

Năm capture mới trên dark/light/window/wallpaper/optical đều từ compositor riêng: shader `ready`, `versionCheck match`, session/compositor exit 0. Root mở đủ năm ảnh; judge độc lập thấy lớp trắng mỏng, trong hơn và mép mềm hơn chút, không thấy lỗi mới rõ. Demo tương tác chạy thực 45.027 giây, sau đó người dùng duyệt. Không suy từ ảnh tĩnh rằng độ bẻ cong đã tăng rõ bằng mắt hoặc mọi format đều được hỗ trợ.

## Giới hạn và kiểm chứng

Chữ trắng vẫn yếu trên nền rất sáng; hiệu ứng mép chưa phong phú hoàn toàn như ảnh tham chiếu. Chưa có runtime proof 10-bit/FP16, số đo hiệu năng, hoặc kiểm chứng dài hạn. Fallback mip còn caveat ở trên. Không thêm grain hoặc shadow mới khi chưa có bằng chứng hình ảnh.

Calibration lịch sử có 57/57 focused checks pass. Lần acceptance của bản công bố trước chạy 673 tests, có hai assertion material cũ không khớp thay đổi có chủ đích (đếm lệnh màu chữ và alpha wash); các suite còn lại pass. Không sửa test để đạt xanh. Bản được duyệt phải chạy lại full acceptance trước push và trên đúng cây đã push; kết quả thật, lệnh và exit được lưu riêng theo commit. Việc người dùng duyệt hình ảnh không thay cho kết quả test.

Cài đặt desktop dùng thư viện bất biến theo hash và manifest cho fresh login; không reload/unload/hot-swap plugin hiện tại. Trạng thái đã nạp trên desktop chính chỉ được xác nhận sau đăng nhập mới.
