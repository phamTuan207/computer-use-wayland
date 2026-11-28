# Pick 4 — ARM 2 (FAST PATH)

- Chủ sở hữu: the owner.
- Cờ đo: `CU_PICK4_FASTPATH=1`. Kết quả `printenv | rg '^CU_(PICK|CODE)'` chỉ có `CU_PICK4_FASTPATH=1`; không đặt `CU_CODE_EXEC` hay cờ Pick khác.
- Không tạo drop-in, không khởi động lại relay, không sửa code hoặc đổi branch.
- Brief ghi commit `5d4d512`, nhưng repo và broker thực tế đang ở `c1b7034b452b24358206009c40bbf450d575da58` trên branch `speed-swarm`. Broker status lúc kiểm tra ban đầu cũng báo `started_git_head=c1b7034b452b24358206009c40bbf450d575da58` và `loaded_code_sha256=f67d8abe5eb5d933e7f0b50c625066df074dd28dbb959ab5d2fb8f0f05c1342b`. Vì vậy các số đo này thu trên `c1b7034`, không phải commit được nêu trong brief.
- Tổng thời gian các khoảng task: **894.303 giây**. Từ lúc P1 bắt đầu đến lúc xác minh dọn dẹp D1 xong: **1107.546 giây**.
- Không chèn sleep. Không có misclick, fallback hay session death. Cả 6 phiên đều kết thúc với `driver=stopped`, `guardian=clean`.

## P1 C-03

- Owner: `pick4-fp-p1`.
- Bắt đầu: 2026-11-19 02:11:16.796 +07. Kết thúc xác minh: 2026-11-19 02:13:11.013 +07. Tổng: **114.219 giây**.
- Request: `windows=1`, `observe=1`, `act=1`, `a11y=0`, `browser=0`, `status=0`. Có 1 observation và 1 act với 1 hành động nhập liệu.
- Kết quả: **SUCCESS**. OCR ảnh sau act đọc dòng `/dev/mapper/omarchy_root ... 19G 96% /`; ảnh hiển thị cột `Avail` là **19G**.
- Lỗi cục bộ trước broker: lần gọi wrapper đầu tiên thiếu tệp `p1-windows.json` và dừng với `FileNotFoundError`; không có request desktop nào được gửi. Tạo envelope đúng rồi gọi lại thành công. Không có request bị broker từ chối.

## P2 E-04

- Owner: `pick4-fp-p2`.
- Bắt đầu: 2026-11-19 02:13:23.478 +07. Kết thúc xác minh: 2026-11-19 02:14:05.799 +07. Tổng: **42.323 giây**.
- Request: `observe=1`, `act=1`; các loại khác `0`. Có 1 observation, 1 act, 1 hành động nhập liệu.
- Kết quả: **SUCCESS**. OCR ảnh sau act hiển thị `96.0`.
- Từ chối, misclick, fallback, session death: không.

## P3 B-01

- Owner: `pick4-fp-p3`.
- Bắt đầu: 2026-11-19 02:14:18.081 +07. Kết thúc xác minh: 2026-11-19 02:14:59.243 +07. Tổng: **41.164 giây**.
- Request: `observe=1`, `act=1`; các loại khác `0`. Có 1 observation, 1 act, 1 hành động nhập liệu.
- Kết quả: **SUCCESS**. OCR ảnh sau act liệt kê `/tmp/hoc-ky-2`, `/tmp/hoc-ky-2/dsa`, `/tmp/hoc-ky-2/ktvm`, `/tmp/hoc-ky-2/oop`.
- Từ chối, misclick, fallback, session death: không.

## P4 A-01

- Owner: `pick4-fp-p4`.
- Bắt đầu: 2026-11-19 02:15:18.632 +07. Kết thúc xác minh: 2026-11-19 02:17:20.573 +07. Tổng: **121.943 giây**.
- Request: `observe=1`, `act=1`; các loại khác `0`. Có 1 observation, 1 act, 1 hành động nhập liệu.
- Kết quả: **SUCCESS**. OCR tiếng Anh của Tesseract đọc `Y tudng 1: app nhdc udng nudc`, `Y tudng 2: bot tém tat bai giang.`, `Y tudng 3: web ban dd secondhand`, và bỏ sót một số dấu. Quan sát trực tiếp cùng ảnh sau `cat` hiển thị chính xác:
  - `Ý tưởng 1: app nhắc uống nước.`
  - `Ý tưởng 2: bot tóm tắt bài giảng.`
  - `Ý tưởng 3: web bán đồ secondhand.`
- Từ chối, misclick, fallback, session death: không.

## G1 Nautilus grounding

- Owner: `pick4-fp-g1`.
- Bắt đầu: 2026-11-19 02:18:31.587 +07. Kết thúc (BLOCKED): 2026-11-19 02:23:12.838 +07. Tổng: **281.253 giây**.
- Request attempts: `windows=2`, `observe=3` (2 accepted, 1 `sequence_gap`), `act=1`, `a11y=3` (đều bị từ chối), `status=1`, `browser=0`.
- Có 2 observation ảnh được chấp nhận: quan sát terminal để mở Nautilus và quan sát Nautilus sau lỗi. Có thêm 1 observe bị từ chối với `sequence_gap`. Act duy nhất là 1 hành động nhập liệu để mở cửa sổ Nautilus mới.
- A11y calls: **3**. Ground calls: **0**. Crop observes: **0**. Full-window observes: **2 accepted**, không có cái nào dùng để ground Home; thêm 1 observe attempt bị từ chối. Vision turns dùng cho grounding: **0**. Fallbacks: **0**.
- Kết quả: **BLOCKED**. `a11y query --pid 764773 --name Home` trả nguyên văn `request_error: unsupported_command`. Sau một observe Nautilus mới, lần retry duy nhất trả cùng lỗi. Lệnh `a11y observe` dùng để làm mới cũng trả `unsupported_command`; một observe kế tiếp bị từ chối `sequence_gap`. `status` cho thấy `next_sequence=5`; sau observe mới, query retry vẫn không được hỗ trợ. Không thực hiện ground hoặc click Home.

## D1 Chromium DOM-first

- Owner: `pick4-fp-d1`.
- Bắt đầu: 2026-11-19 02:24:50.943 +07. Kết thúc (assert và kiểm tra dọn dẹp): 2026-11-19 02:29:44.342 +07. Tổng: **293.401 giây**.
- Request: `windows=2`, `observe=2`, `act=2`, `browser=4` (start, tabs, DOM observe, DOM act), `a11y=0`, `status=0`. Tổng 10 request; 3 observations (2 ảnh desktop, 1 DOM snapshot), 2 act requests, 6 actions tổng cộng.
- Browser observes có ảnh: **0**. Browser observes không ảnh: **1**. Browser acts: **1**. Asserts: **1**. Ảnh chụp: **2**, đều cần để xác nhận đúng cửa sổ/focus trước khi dùng desktop act cho thanh địa chỉ và trước khi đóng Chromium bằng Alt+F4. Browser observe và browser act không chụp ảnh.
- Kết quả: **SUCCESS**. DOM observe xác nhận URL `file:///tmp/speed-pick4-20261118/pick4-fixture.html` và ref `e2` là nút “Show result”. Browser act click `e2`, rồi assert `#result` chứa `pick4-ok`; kết quả trả `ok: true`, `completed: 2`.
- Alt+F4 qua broker đóng cửa sổ Chromium. Kết quả act báo `window no longer exists` khi cửa sổ đã đóng; request `windows` kế tiếp xác nhận địa chỉ Chromium không còn.

## Tổng request và teardown

- Request được broker chấp nhận: `windows=5`, `observe=8`, `act=7`, `a11y=0`, `browser=4`, `status=1` (**25** tổng).
- Request bị từ chối: `observe=1` (`sequence_gap`), `a11y=3` (`unsupported_command`) (**4** tổng). Lỗi wrapper P1 xảy ra trước khi gửi broker và không nằm trong các số này.
- Quan sát độc lập: 8 desktop observe được chấp nhận, 1 browser DOM observe được chấp nhận; thêm 1 desktop observe bị từ chối. Các act P1–P4 trả thêm ảnh after; browser act trả DOM after snapshot.
- Hyprland object-form close trả `ok` cho terminal kiểm tra và Nautilus. Kiểm tra `hyprctl -j clients` cuối báo `test_windows_remaining=0`; PID Chromium quản lý `767756` không còn. Quét process không còn `cu.py session`, `session-driver`, `cursor_session.py guard` hoặc `native/indicator`.
- `git status --short` cuối có 4 file tracked sửa đổi: `scripts/cu.py`, `scripts/vscode_cli.py`, `skill/cli-anything/registry.json`, `skill/cli-anything/vscode.md`. Mtime của cả 4 là 2026-11-18 23:16–23:20 +07, trước lượt chạy này; tôi không sửa chúng. `browser start` báo profile quản lý tại `~/computer-use-wayland/browser-profile`; không xóa profile để giữ trạng thái tab.

## Output analyzer
== overall ==
records (excluding status polls): 41
status polls: 18
total logged sleeps: 0.0 s in 0 entries

== task d1 ==
  act        n=2 service=0.667 s
  browser    n=4 service=0.743 s
  finish     n=1 service=0.254 s
  observe    n=2 service=0.259 s
  start      n=1 service=0.000 s
  windows    n=2 service=0.216 s
  service total: 2.139 s
  image bytes total: 39930
  start call: 0.186 s, ready: 0.851 s, polls: 3
  first request after ready: 5.978 s
  between-request gaps: n=11 total=291.334 s max=139.231 s
    gap d1-start -> d1-browser-start : 6.642 s
    gap d1-browser-start -> d1-windows : 16.468 s
    gap d1-windows -> d1-browser-tabs : 6.931 s
    gap d1-browser-tabs -> d1-desktop-observe : 7.862 s
    gap d1-desktop-observe -> d1-navigate-act : 21.555 s
    gap d1-navigate-act -> d1-browser-observe : 7.546 s
    gap d1-browser-observe -> d1-browser-act : 13.264 s
    gap d1-browser-act -> d1-close-observe : 45.876 s
    gap d1-close-observe -> d1-close-act : 14.707 s
    gap d1-close-act -> d1-windows-after-close : 11.252 s
    gap d1-windows-after-close -> d1-finish : 139.231 s
  task span (first submit to last result): 293.658 s
  gap share of span: 99.2%, service share: 0.7%
  think/prep split (DECIDE lines):
    d1-browser-start       think=5.9 s prep=0.0 s
    d1-windows             think=16.4 s prep=0.0 s
    d1-browser-tabs        think=6.9 s prep=0.0 s
    d1-desktop-observe     think=7.8 s prep=0.0 s
    d1-navigate-act        think=21.5 s prep=0.0 s
    d1-browser-observe     think=7.5 s prep=0.0 s
    d1-browser-act         think=13.2 s prep=0.0 s
    d1-close-observe       think=45.8 s prep=0.0 s
    d1-close-act           think=14.7 s prep=0.0 s
    d1-windows-after-close think=11.2 s prep=0.0 s
    d1-finish              think=139.2 s prep=0.0 s

== task g1 ==
  a11y       n=3 service=0.156 s
  act        n=1 service=0.485 s
  finish     n=1 service=0.261 s
  observe    n=3 service=0.391 s
  start      n=1 service=0.000 s
  status     n=1 service=0.054 s
  windows    n=2 service=0.209 s
  service total: 1.556 s
  image bytes total: 2640273
  start call: 0.211 s, ready: 0.873 s, polls: 3
  first request after ready: 7.094 s
  between-request gaps: n=11 total=279.749 s max=50.819 s
    gap g1-start -> g1-windows-before : 7.756 s
    gap g1-windows-before -> g1-term-observe : 24.763 s
    gap g1-term-observe -> g1-open-nautilus-act : 14.610 s
    gap g1-open-nautilus-act -> g1-windows-nautilus : 6.684 s
    gap g1-windows-nautilus -> g1-a11y-query-home : 24.189 s
    gap g1-a11y-query-home -> g1-a11y-refresh : 44.577 s
    gap g1-a11y-refresh -> g1-recovery-observe : 50.819 s
    gap g1-recovery-observe -> g1-status : 30.098 s
    gap g1-status -> g1-fresh-observe : 27.319 s
    gap g1-fresh-observe -> g1-a11y-query-retry : 13.902 s
    gap g1-a11y-query-retry -> g1-finish : 35.031 s
  task span (first submit to last result): 281.515 s
  gap share of span: 99.4%, service share: 0.6%
  think/prep split (DECIDE lines):
    g1-windows-before      think=7.1 s prep=0.0 s
    g1-term-observe        think=24.7 s prep=0.0 s
    g1-open-nautilus-act   think=14.6 s prep=0.0 s
    g1-windows-nautilus    think=6.7 s prep=0.0 s
    g1-a11y-query-home     think=24.2 s prep=0.0 s
    g1-a11y-refresh        think=44.5 s prep=0.0 s
    g1-recovery-observe    think=50.8 s prep=0.0 s
    g1-status              think=30.1 s prep=0.0 s
    g1-fresh-observe       think=27.3 s prep=0.0 s
    g1-a11y-query-retry    think=13.9 s prep=0.0 s
    g1-finish              think=35.0 s prep=0.0 s

== task p1 ==
  act        n=1 service=0.401 s
  finish     n=1 service=0.153 s
  observe    n=1 service=0.225 s
  start      n=1 service=0.000 s
  windows    n=1 service=0.108 s
  service total: 0.887 s
  image bytes total: 1790982
  start call: 0.182 s, ready: 0.849 s, polls: 3
  first request after ready: 32.150 s
  between-request gaps: n=4 total=113.307 s max=37.399 s
    gap p1-start -> p1-windows-retry : 32.817 s
    gap p1-windows-retry -> p1-observe-1 : 23.318 s
    gap p1-observe-1 -> p1-act : 19.772 s
    gap p1-act -> p1-finish : 37.399 s
  task span (first submit to last result): 114.376 s
  gap share of span: 99.1%, service share: 0.8%
  think/prep split (DECIDE lines):
    p1-windows-retry       think=32.1 s prep=0.0 s
    p1-observe-1           think=23.3 s prep=0.0 s
    p1-act                 think=19.7 s prep=0.0 s
    p1-finish              think=37.4 s prep=0.0 s

== task p2 ==
  act        n=1 service=0.486 s
  finish     n=1 service=0.256 s
  observe    n=1 service=0.189 s
  start      n=1 service=0.000 s
  service total: 0.931 s
  image bytes total: 1817548
  start call: 0.223 s, ready: 0.893 s, polls: 3
  first request after ready: 9.358 s
  between-request gaps: n=3 total=41.424 s max=15.831 s
    gap p2-start -> p2-observe-1 : 10.029 s
    gap p2-observe-1 -> p2-act : 15.831 s
    gap p2-act -> p2-finish : 15.564 s
  task span (first submit to last result): 42.577 s
  gap share of span: 97.3%, service share: 2.2%
  think/prep split (DECIDE lines):
    p2-observe-1           think=9.3 s prep=0.0 s
    p2-act                 think=15.8 s prep=0.0 s
    p2-finish              think=15.5 s prep=0.0 s

== task p3 ==
  act        n=1 service=0.755 s
  finish     n=1 service=0.156 s
  observe    n=1 service=0.187 s
  start      n=1 service=0.000 s
  service total: 1.098 s
  image bytes total: 1840243
  start call: 0.185 s, ready: 0.852 s, polls: 3
  first request after ready: 7.428 s
  between-request gaps: n=3 total=40.038 s max=18.040 s
    gap p3-start -> p3-observe-1 : 8.095 s
    gap p3-observe-1 -> p3-act : 18.040 s
    gap p3-act -> p3-finish : 13.903 s
  task span (first submit to last result): 41.321 s
  gap share of span: 96.9%, service share: 2.7%
  think/prep split (DECIDE lines):
    p3-observe-1           think=7.4 s prep=0.0 s
    p3-act                 think=18.0 s prep=0.0 s
    p3-finish              think=13.9 s prep=0.0 s

== task p4 ==
  act        n=1 service=1.068 s
  finish     n=1 service=0.153 s
  observe    n=1 service=0.179 s
  start      n=1 service=0.000 s
  service total: 1.400 s
  image bytes total: 1855419
  start call: 0.206 s, ready: 0.875 s, polls: 3
  first request after ready: 6.150 s
  between-request gaps: n=3 total=120.494 s max=76.349 s
    gap p4-start -> p4-observe-1 : 6.819 s
    gap p4-observe-1 -> p4-act : 37.326 s
    gap p4-act -> p4-finish : 76.349 s
  task span (first submit to last result): 122.100 s
  gap share of span: 98.7%, service share: 1.1%
  think/prep split (DECIDE lines):
    p4-observe-1           think=6.1 s prep=0.0 s
    p4-act                 think=37.3 s prep=0.0 s
    p4-finish              think=76.3 s prep=0.0 s

== grand totals (all tasks) ==
service total: 8.011 s, gap total: 886.347 s
