# Đo cải thiện overhead

BASELINE / AFTER

Chạy cùng `tests/performance.py:24`, 40 mẫu mỗi phép đo, Python mới cho
import/help/status; `perf_counter` tính toàn thời gian subprocess, gồm tạo tiến
trình (`tests/performance.py:36`). Bảng này đo help qua `cu.main()` trực tiếp
(`tests/performance.py:44`), tránh lỗi entry point của phiên bản trước biến
SystemExit của --help thành exit 1. Lỗi đó đã sửa tại `scripts/cu.py:585`;
giữ cách đo cũ để so sánh với baseline. Không phát input, không khởi động session thật.
Ảnh giả lập RGB 1920×1200, resize 1280×800; subprocess chụp/monitors được thay
bằng dữ liệu trong RAM (`tests/performance.py:47`). Gate này đo xử lý Python/PIL,
KHÔNG đo capture/compositor hay khởi động sau đổi zoom.

| Phép đo | Trước median/p95 ms | Sau median/p95 ms | Giảm median ms |
|---|---:|---:|---:|
| Python pass | 8.903 / 10.874 | 8.937 / 10.850 | -0.034 |
| Python + import cu | 39.855 / 45.332 | 25.903 / 32.779 | 13.952 |
| Help qua main | 50.695 / 57.570 | 36.913 / 42.117 | 13.782 |
| Status qua main | 59.550 / 64.300 | 36.359 / 43.386 | 23.191 |
| Gate ảnh tĩnh, capture giả lập | 73.245 / 74.767 | 68.344 / 71.442 | 4.901 |
| Gate ảnh đổi, capture giả lập | 70.998 / 72.312 | 71.107 / 72.637 | -0.109 |
| So ảnh đầy đủ, không đổi | 3.735 / 3.824 | 3.738 / 3.837 | -0.003 |

Lặp lại bằng `python3 tests/performance.py --scripts scripts --samples 40`.
Bản trước là bản sao hai file scripts chưa sửa trong thư mục tạm; dùng cùng
lệnh với `--scripts <thư-mục-bản-trước>`. Các số là hai lượt liên tiếp trên môi
trường chạy hiện tại, không khẳng định độ trễ desktop của máy người dùng.

CHANGES

- `scripts/cu.py:471`: tải urllib khi browser start, base64 khi có ảnh CDP
  (`scripts/cu.py:564`); giảm import tổng 13.952 ms, help 13.782 ms.
- `scripts/cu.py:514`: chỉ tìm môi trường compositor ở lệnh dùng nó. Status
  giảm tổng 23.191 ms gồm cả import; phần tăng thêm so với help là 9.409 ms,
  không phải phép đo độc lập chỉ của environment.
- `scripts/cursor_session.py:160`: bỏ tính histogram nếu diff giống nhau.
  Giảm gate tĩnh giả lập 4.901 ms. Gate ảnh đổi 70.998 → 71.107 ms
  (+0.109 ms); không tuyên bố cải thiện ảnh đổi. Vẫn 4 grim + 4 hyprctl
  mỗi mẫu tĩnh, vẫn ba cặp giống nhau (`scripts/cursor_session.py:166`).

REJECTED

- Cache bytes RGB: gate tĩnh lần thử 73.432 → 63.993 ms, nhưng phép đo
  bổ sung ảnh đen/trắng đổi liên tục, 4 captures, 40 mẫu, median/p95
  71.930/74.789 → 82.058/83.905 ms. Chậm +10.128 ms median;
  đã bỏ. Cách còn lại tại `scripts/cursor_session.py:157` giữ diff.
- Chỉ so patch 49×49: median/p95 0.049/0.052 ms, tiết kiệm khoảng 3.689 ms
  so với phép so đầy đủ sau sửa. Sai: full guard trả true, patch guard false
  khi vùng lớn ở ngoài điểm click đổi (`tests/performance.py:72`). Đây chỉ là
  chi phí so ảnh; tiết kiệm capture thật OPEN. Giữ whole-image stale guard
  (`scripts/cu.py:254`), không nới ngưỡng.
- Thêm daemon: OPEN, chưa thử vì không đo được round trip compositor để
  chứng minh lợi ích; chưa thêm.
- Gộp Enter vào nhóm gõ: không thử phát input; giữ ranh giới đổi focus/IME
  tại `scripts/cu.py:290`, kiểm thử tại `tests/test_core.py:123`.

LEFT / OPEN

- Compositor: pgrep quickshell/Hyprland/waybar/kitty không thấy tiến trình;
  hyprctl -j monitors exit 2. Không lấy được socket bằng cách người dùng đưa.
  Observe thật, pre-capture, startup sau zoom, phân bố 26 captures,
  click+type+Enter, DOM/a11y typing: OPEN. Không chạy act, kể cả wait:0.
- Mọi call site hyprctl: desktop query helper `scripts/cu.py:100`, focus
  dispatch `scripts/cu.py:117`, guardian command `scripts/cursor_session.py:26`,
  startup monitors `scripts/cursor_session.py:138`, hotkey eval/device query
  `scripts/cancel_hotkey.py:16` và `scripts/cancel_hotkey.py:24`.
- Click+type+Enter ở window đã focus có 32 truy vấn theo đếm mã:
  focus 1 (`scripts/cu.py:116`), guard ban đầu 3 (`scripts/cu.py:376`),
  observe trước 3 (`scripts/cu.py:190`), click guard+cursor 4
  (`scripts/cu.py:413`, `scripts/cu.py:399`), type 9 + Enter 9
  (`scripts/cu.py:413`, `scripts/cu.py:419`, `scripts/cu.py:420`),
  observe sau 3 (`scripts/cu.py:457`). Thời gian thật OPEN. Không cache qua
  hành động hay bỏ kiểm tra sau capture vì trạng thái có thể đổi.
- Pointer vẫn tạo khi chỉ gõ (`scripts/cu.py:394`); tiết kiệm nếu tạo khi cần:
  OPEN. Không thay khi chưa đo native device.
- cmd được hỏi hai lần trước sửa, cả hai exit 6: API không kết nối được.
  Hai agent thay thế rà soát chỉ đọc; không sửa chung.

VALIDATION

Lượt trước: 40 kiểm thử Python qua. Sau sửa CLI: 42 kiểm thử Python qua
(16.248 s); capture/adapter, CDP keyboard và validation qua; git diff --check sạch.

Kiểm thử đổi một pixel riêng mỗi kênh RGB, bố trí/scale/transform, tên/thêm
màn hình reset gate tại `tests/test_cursor_session.py:319`; ảnh tĩnh vẫn cần
4 captures tại `tests/test_cursor_session.py:346`. Local state/CDP không tìm
môi trường compositor: `tests/test_core.py:52`.

CLI EXIT FIX

- Trước sửa, chạy `python3 scripts/cu.py --help` trả exit 1 và thêm JSON
  lỗi `error: "0"`. Handler nay giữ SystemExit của argparse: help exit 0,
  không yêu cầu dừng phiên; đối số sai exit 2 và vẫn dừng phiên
  (`scripts/cu.py:585`). Các ngoại lệ khác vẫn dùng handler lỗi
  (`scripts/cu.py:590`).
- Kiểm thử entry point trong tiến trình riêng qua `runpy`, thay toàn bộ
  `cursor_session.request_stop` bằng Mock để không tác động phiên thật
  (`tests/test_core.py:13`). Help chính/browser/session không gọi cleanup
  (`tests/test_core.py:33`); thiếu lệnh/lệnh lạ/observe thiếu đích gọi cleanup
  một lần và giữ exit 2 (`tests/test_core.py:42`).
- Không đo lại hiệu năng sau sửa exit handler: tác động thời gian OPEN.

Không add/commit/push; không sửa bản cài đặt live; không để tiến trình nền.
