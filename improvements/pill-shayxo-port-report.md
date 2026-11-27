# Báo cáo port Shayxo Legacy cho pill

- Model: gpt-6-luna
- Reasoning effort: max
- Bắt đầu, mốc thời gian đầu tiên được ghi sau khi đọc tài liệu: 2026-11-18 14:14:34 +07
- Kết thúc: 2026-11-18 14:47:51 +07
- Plugin mới SHA-256: 199153aea84a833d86f3eee21708e186c5a722c52259397735898b52f86df07f
- Plugin cũ SHA-256: 69309243789bee75616b5d260882db7597ab7da4f928755971f813dd77b89748
- Build source: ~/computer-use-handoff/backend/hyprglass-1.1.1, upstream pin 03a57c4451b4abee38feda2ffb725f55ecc0f2fd

## Kết quả theo checklist

| Bước | Lệnh/kết quả | Mã thoát | Thời gian |
|---|---|---:|---:|
| 1 | python3 -m unittest discover -s tests -p 'test_glass_*.py' lần đầu: một expected value Fresnel sai; sửa test theo công thức, chạy lại Ran 52, OK (skipped=1). Báo cáo D2 ghi lần chạy cuối của bộ mở rộng: python3 -m unittest discover -s tests -p 'test_glass_*.py' -v, Ran 60, OK (skipped=1). | 1 rồi 0; D2: 0 | 424 s từ mốc repo check đến kết thúc Step 1; lượt test lại 0.13 s |
| 2 | git clone https://github.com/hyprnux/hyprglass.git /tmp/d3-shayxo-patchcheck.cAUdLj; git checkout --detach 03a57c4451b4abee38feda2ffb725f55ecc0f2fd; git apply --check ~/computer-use-wayland/native/hyprglass-shayxo-legacy.patch | 0 cho cả ba | 25 s theo mốc giờ; clone 1.862 s |
| 3 | git checkout -- src/Shaders.hpp; xác minh git status --short chỉ còn M src/GlassLayerSurface.cpp, M src/GlassRenderer.cpp, còn Shaders.hpp sạch. Đọc scripts/build-glass.py: PATCHES = (('local-optics', PATCH), ('shayxo Legacy', SHAYXO_PATCH)). | 0 | 33 s theo mốc giờ |
| 4 | python3 scripts/build-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1 --local-optics --allow-dirty | 0 | 45.004 s đo bằng Bash time; 101 s tính cả thời gian xử lý của bước |
| 5 | Trích 706 dòng liquidglass.frag và biến thể contour 707 dòng; glslangValidator -S frag /tmp/d3-liquidglass.frag; glslangValidator -S frag /tmp/d3-liquidglass-contour.frag | 0 cho cả hai | 66 s theo mốc giờ; mỗi lệnh validator dưới 0.01 s |
| 6 | Đọc GlassRenderer.cpp và GlassRenderer.hpp: renderer cấp SAMPLE_PADDING_PX = 60 framebuffer px mỗi phía; uvPadding = 60 / fullWidth|fullHeight. | 0 | 54 s theo mốc giờ |
| 7 | python3 scripts/install-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1/hyprglass.so ~/.local/share/agent-computer-use/plugins; xác minh bytes SHA khớp tên file | 0 | 0.021 s |
| 8 | refresh-visuals-manifest.py và check-visuals-manifest.py qua. sync-installed.py dừng với lỗi bên dưới; sync-installed.py --check không chạy sau khi bước dừng. | 0, 0, rồi 1 | sync 2.658 s; bước dừng tại lỗi |
| 9 | python3 -m unittest discover -s tests -p 'test_*.py' | 1 do đúng 5 lỗi baseline | 87.832 s |
| 10 | Các commit port đã có trên origin/main; xác minh bằng git ls-remote. Tôi đẩy commit làm rõ ghi chú công thức/tài liệu sau git fetch origin, xác nhận không bị behind và diff chỉ gồm ba file liên quan. | 0 | git push origin main: 1.746 s; kiểm tra remote: 0.541 s |
| 11 | Ghi file báo cáo và /tmp/d3-execute-report.md | 0 | Thời điểm kết thúc ở đầu báo cáo |

Bash không có /usr/bin/time: lệnh bọc ban đầu thoát 127 với /usr/bin/bash: line 1: /usr/bin/time: No such file or directory. Lệnh build thực tế sau đó chạy bằng Bash time và thành công. Đuôi log build: local-optics patch đã áp dụng sẵn; Shayxo Legacy patch được áp dụng; các file C++ biên dịch và Linking hyprglass.so... Done!.

## Kiểm thử hồi quy

Baseline tại be552a40: Ran 1109 tests in 95.579s, FAILED (failures=5, skipped=1).

Lần chạy full suite: Ran 1127 tests in 87.622s, FAILED (failures=5, skipped=1), exit code 1. Cả năm lỗi đều là lỗi Doctor CLI đã có trong baseline; không có lỗi mới:

- test_base_exception_from_probe_is_not_converted_to_ime_error (test_session_driver.DoctorCliTests)
- test_first_failure_skips_second_probe (test_session_driver.DoctorCliTests)
- test_long_crlf_probe_error_is_single_line_bounded (test_session_driver.DoctorCliTests)
- test_remote_success_keeps_schema (test_session_driver.DoctorCliTests)
- test_second_probe_failure_after_first_success (test_session_driver.DoctorCliTests)

Số test theo file:

| File | HEAD ban đầu | Sau thay đổi | Lý do |
|---|---:|---:|---|
| test_glass_optics_contract.py | 7 | 7 | Đổi mô hình capsule sang Snell Legacy |
| test_glass_lighting_contract.py | 9 | 9 | Đổi hợp đồng ánh sáng sang Schlick và các lobe Legacy |
| test_glass_dome_contract.py | 5 | 5 | Kiểm tra dome gate và wide-epsilon axis fade |
| test_glass_ripple_contract.py | 3 | 3 | Bỏ mô hình ripple cũ; khóa một trường Snell |
| test_glass_build.py | 13 | 14 | Thêm lỗi patch thứ hai phải dừng trước make |
| test_glass_shayxo_contract.py | 0 | 17 | Thêm hợp đồng số học và nguồn |
| Tổng tăng |  | +18 | 17 test mới và 1 test build mới |

Lần focused đầu của tôi có assertion Fresnel sai: AssertionError: 0.04206927312437237 != 0.063899196026 within 11 places (0.02182992290162763 difference). Tôi sửa expected value rồi focused suite chạy xanh. Không chạy full suite lần hai vì kết quả cho thấy đúng cùng năm lỗi baseline, không có dấu hiệu flaky.

## Mô hình, các phần khớp nguồn và độ lệch

Coordinator chọn task value set khi khác với preset GlassStyle.Chrome thật ở Shayxo commit f5e1fb56; vì vậy đây là port Shayxo Legacy theo giá trị task, không gọi là bản sao đúng preset Chrome.

| Tham số | Giá trị task được port | GlassStyle.Chrome thật |
|---|---:|---:|
| Dispersion | 0.07 | 0.010 |
| Specular | 0.55 | 0.50 |
| Fresnel | 0.10 | 0.08 |
| Inner shadow | 0.07 | 0.06 |
| Legibility | 0.6 | 0.90 |
| Tint | Trong suốt | Trắng, alpha 0.11 |
| Backdrop pre-blur | 0 | 14 dp |
| Mirror echo | 0 | 0.08 |

Band 14 dp, depth 9 dp, fine blur 0 và bevel 3 dp khớp preset Chrome. Mirror bị loại theo task.

Đã dịch/giữ theo công thức Shayxo: bevelSlope, Snell tangent-difference snellShift, chuẩn hóa Snell theo giá trị ở rim, outward push, guard rim 1.5 px, inner fade, wide-epsilon normal và axis fade, dispersion theo từng kênh, Schlick Fresnel, key/counter lobe, edge line 2 px, inner line và Oklab highlight. smoothstep(1.0, 0.75, e) được viết thành 1.0 - smoothstep(0.75, 1.0, e) để giữ easing trong GLSL ES 300. Sample point dùng UV remap sẵn có của Hyprglass qua sampleSharp; không thêm host uniform hay shader API mới.

Plumbing/độ lệch: Hyprglass contour SDF thay cho host Skia/Compose của Shayxo; pill này có dome weight bằng 0 nên không có dome displacement. Fine blur bằng 0 đi thẳng tới sample sharp sau offset. Không có wideTex hay bản Gaussian quarter-scale trong renderer, nên bỏ wide tone B + k(D-B) + c|D-B|; port giữ toneMappedTint và legibility term nhưng dùng sharp sample thay cho wide copy. Vì vậy tone không giống hệt nguồn Shayxo.

### Bend formula

Nội dung nghiên cứu nói “full” ở outer 75%, nhưng đó chỉ là hệ số 1 - smoothstep(0.75, 1.0, e). Tỉ số Snell và rim guard vẫn làm tổng bend thay đổi. Công thức cho các mốc e=0/0.5/0.75/1 lần lượt 0/0.188/0.086/0. Tại depth 1.5 px là 0.508922 (xấp xỉ 0.509); quét dày 0.0001 px cho cực đại khoảng 0.515247 tại 1.3983 px. Test khóa công thức, không khẳng định bend=1.

Dispersion checkpoint 0.07 × 0.8 = 0.056, hệ số đỏ/xanh 0.944/1.056. 8.1855 px (7.65 × 1.07) là giới hạn bảo thủ với bend ≤ 1, không phải độ lệch đạt được của profile thực tế. Counter power theo task là 6 × 1.6 = 9.6; f0=0.04.

## Pad và GLSL

Công thức pad của task là 9 × 1.4 + max(0,0) = 12.6 px ở scale 1. Renderer dành 60 framebuffer px mỗi phía qua SAMPLE_PADDING_PX; sampleBackground thêm 120 px vào kích thước sample box và tính uvPadding từ chính phần 60 px. sampleUVOffset/Scale ánh xạ vùng sample của layer, không giảm margin này. Dự phòng là 60 px so với 12.6 px yêu cầu. Blit bị giới hạn tại biên framebuffer màn hình.

glslangValidator có tại /usr/bin/glslangValidator; glslc cũng có. Shader trích từ Shaders.hpp bắt đầu bằng #version 300 es. Cả lệnh validator cho biến thể mặc định và HYPRGLASS_FEATURE_CONTOUR đều exit 0, không có output. Đây là kiểm tra cú pháp GLSL; build make tự nó không biên dịch shader.

## Reproducibility, manifest và cài đặt

Clone mới /tmp/d3-shayxo-patchcheck.cAUdLj checkout đúng commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd; git apply --check ~/computer-use-wayland/native/hyprglass-shayxo-legacy.patch exit 0, không output.

Artifact cài tại:
~/.local/share/agent-computer-use/plugins/hyprglass-199153aea84a833d86f3eee21708e186c5a722c52259397735898b52f86df07f.so

Refresh manifest thành công với profile_sha256=545455d372f13ff6bf1666768e36c5ae21850c6d67222d6d97a70600f9378107 và ABI 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6. check-visuals-manifest.py xác nhận profile hash.

sync-installed.py thất bại nguyên văn:
sync-installed: error: repo source changed before release verification; refusing acceptance

Nó tạo snapshot ~/.local/share/agent-computer-use/backups/sync-20261118-142702-887112-de8fcf67; transaction.json ghi status=rolled-back. So sánh evidence cho thấy HEAD chưa đổi nhưng đúng một file tracked đổi trong lúc sync: tests/test_glass_local_optics.py (ghi chú test được thêm trong lúc bộ contract đang hoàn thiện). Vì bước dừng ở lỗi, sync-installed.py --check không chạy; không ghi nhận sync thành công.

## Các commit trên origin/main

Các commit port có author/committer của the owner. Bảy commit đầu đã nằm trên remote khi bắt đầu bước push; commit cuối là ghi chú bổ sung được đẩy sau fetch/kiểm tra diff.

1. c2b52d2aeb64aa2a440266d7b74190be634d7999 — feat: add shayxo Legacy glass shader patch
2. 09a8df75b0e0b65b6abfb5d17187d03dcada277a — fix: set pill optics to shayxo Legacy Chrome params (blur 0, depth 9, band 14)
3. d6e67b30160f0d93514817cd14b66305e3330045 — build: apply local-optics then shayxo Legacy patches in build-glass.py
4. cc0e76992e78fa57a6edc6cbccc471a2fd53515 — test: cover two-patch build order in test_glass_build
5. f1cd53e2991159f5bf6e062b9e122c997a5bfd62 — docs: add shayxo recon and port-design reports
6. 3ed2d8c0e75c0146dbf80b214972a8c9daf2880e — test: add shayxo Legacy contract tests
7. 6f7315f28fabb835132b8e9ae1ed45d6fe7f28fe — test: update glass contracts to shayxo Legacy Snell model
8. ab11a646e1731c6f6007256a54b1062d6d9ae58a — docs: resolve shayxo port value and bend notes

Xác minh sau push: git ls-remote origin main trả ab11a646e1731c6f6007256a54b1062d6d9ae58a refs/heads/main; khớp git rev-parse HEAD.

Pill chưa được xem lại trong phiên compositor. Theo yêu cầu, không load plugin; lần re-test hình ảnh chờ lần đăng nhập mới tiếp theo.
