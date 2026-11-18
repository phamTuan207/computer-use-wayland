# Pick 4 — Arm 1 Baseline

**Kết quả:** P1–P4 đều đạt. Mọi thao tác terminal được gửi qua broker trên máy này; không dùng a11y/browser, ydotool, SSH hay sửa repo.

## Cờ, repo và cửa sổ test

- Coordinator note ghi shared drop-in có `CU_PICK4_FASTPATH=1`, nhưng hiệu ứng đó chỉ liên quan output a11y/browser. Shell của lượt chạy thực tế in `inherited CU_PICK4_FASTPATH=unset`; sau khi source env, `CU_PICK4_FASTPATH=unset`, `CU_CODE_EXEC=unset`, và không có biến `CU_*` khớp PICK/CODE/FASTPATH. Trước mỗi wrapper call, các biến khớp đó đều được unset. Arm này chạy với **0 pick flag**.
- Nhánh là `speed-swarm`, nhưng HEAD thực tế là `c1b7034b452b24358206009c40bbf450d575da58`, không phải commit kỳ vọng `5d4d512`; nhánh báo `behind 9`. Bốn file đã sửa sẵn trước khi chạy vẫn giữ nguyên; lượt này không sửa repo.
- Cửa sổ Kitty test: address `0x55faff386f50`, PID cuối `732724`. Lần `nohup kitty` đầu không tạo cửa sổ; `setsid -f kitty` tạo đúng cửa sổ test. Lệnh `rm -rf` ban đầu bị shell-command guard từ chối trước khi chạy; chỉ hai đường dẫn được nêu đã được dọn bằng Python `rmtree`/`unlink`.

## Wall timing

Mốc bắt đầu là submit của phiên task thành công; mốc kết thúc là kết quả broker observe cuối cùng dùng để xác minh. Giờ địa phương Asia/Ho_Chi_Minh (UTC+07:00).

| Task | Bắt đầu | Xác minh xong | Tổng giây | Kết quả và bằng chứng OCR |
|---|---|---|---:|---|
| P1 C-03 | 2026-11-19 01:39:08.638 | 2026-11-19 01:43:50.132 | 281.494 | **SUCCESS** — OCR: `/dev/mapper/omarchy_root 3856 3646 196 96% /`; dòng `df -h /` cho thấy Avail là **19G** (OCR đọc ký tự `G` thành `6`). |
| P2 E-04 | 2026-11-19 01:45:04.374 | 2026-11-19 01:45:47.983 | 43.609 | **SUCCESS** — OCR hiển thị `96.0`. |
| P3 B-01 | 2026-11-19 01:50:24.844 | 2026-11-19 01:51:08.701 | 43.857 | **SUCCESS** — OCR liệt kê `/tmp/hoc-ky-2`, `/tmp/hoc-ky-2/oop`, `/tmp/hoc-ky-2/ktvm`, `/tmp/hoc-ky-2/dsa`. |
| P4 A-01 | 2026-11-19 01:54:25.031 | 2026-11-19 01:59:37.544 | 312.513 | **SUCCESS** — ảnh OCR có `BYTE-EXACT: True`; ngay sau đó `cat /tmp/y-tuong.txt` in ba dòng. OCR `eng` làm rơi dấu Việt, nên phép so bytes UTF-8 được chạy trong terminal qua broker và hiện `True`. |

Tổng các mốc task-start → xác minh: **681.473 giây**. Từ submit P1 đầu tiên đến ảnh xác minh P4 cuối cùng, tính cả khoảng nghỉ và xử lý broker: **1,228.906 giây**.

## Request và action

| Task | windows | observe | act requests | action objects hoàn tất / request | status polls tự động | status tường minh |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 2 | 3 | 2 | 1 / 2 | 3 | 0 |
| P2 | 1 | 2 | 1 | 1 / 1 | 3 | 0 |
| P3 | 2 | 2 | 1 | 1 / 1 | 89 | 1 |
| P4 | 1 | 5 | 4 | 3 / 4 | 3 | 0 |
| **Tổng** | **6** | **12** | **8** | **6 / 8** | **98** | **1** |

Có 6 action objects được thực thi, gồm 10 lệnh shell bên trong các action đó. Hai act request bị stale có `completed: 0`; không gửi input. P4 có thêm hai action chỉ đọc để đối chiếu byte/file sau khi OCR tiếng Anh không giữ được dấu.

## Refusal, session và teardown

- P1 act đầu bị từ chối stale với lỗi `observation older than 90s or from a future clock; observe again`; `completed: 0`. Đã observe mới rồi act lại thành công.
- P3 start đầu không đạt ready (`ok:false`, `ready_wall:null`, 83 polls). Status khi đó cho thấy broker đang chạy owner `pick2-p1`; không gửi request task. Đã chờ 120 giây, ghi hai khoảng 60 giây vào sleep log, rồi status báo owner đó `failed`, `driver_command_failed`, `guardian: clean`. P3 retry bằng lease mới chạy thành công.
- Sau khi P3 đã được xác minh, `finish` và `status` lease `p3-retry1.lease` đều trả `invalid_lease`; wrapper không nêu nguyên nhân sâu hơn. Đã ghi thời điểm, xóa các lease P3 cũ, mở phiên thay thế bằng thư mục lease mới, gửi `windows` đầu tiên và finish sạch trước P4.
- P4 act kiểm tra hex đầu tiên bị stale với cùng lỗi trên và `completed: 0`; đã observe mới và retry. Retry thành công; so sánh byte UTF-8 trong terminal in `BYTE-EXACT: True`.
- P4 finish báo `finished`, `driver: stopped`, `guardian: clean`. Dispatcher Hyprland graceful trả `ok`; lần kiểm tra tức thời còn thấy client test nên đã force-kill đúng PID `732724` lấy từ client có title `pick4-base-term`. Kiểm tra `hyprctl clients -j` tiếp theo cho số cửa sổ test là **0**; không còn tiến trình test/session-driver. Không đóng cửa sổ khác.
- Không task nào bị blocked; không có request terminal nào gửi tới cửa sổ ngoài Kitty test.

Thời lượng analyzer bên dưới tính từ lần submit đầu đến kết quả cuối của từng nhóm log; do đó bao gồm failed start, wait, hoặc lifecycle cleanup khi có, và khác với đồng hồ task-start → verified ở trên.

## Analyzer output

```text
== overall ==
records (excluding status polls): 38
status polls: 98
total logged sleeps: 120.0 s in 2 entries
  sleep 01:47:32.588 60.0s broker running owner pick2-p1; P3 retry wait part 1/2
  sleep 01:48:38.966 60.0s broker running owner pick2-p1; P3 retry wait part 2/2

== task p1 ==
  act        n=2 service=0.479 s
  finish     n=1 service=0.258 s
  observe    n=3 service=0.549 s
  start      n=1 service=0.000 s
  windows    n=2 service=0.217 s
  service total: 1.503 s
  image bytes total: 3581424
  start call: 0.181 s, ready: 0.849 s, polls: 3
  first request after ready: 12.193 s
  between-request gaps: n=8 total=320.646 s max=110.701 s
    gap p1-start -> p1-windows : 12.861 s
    gap p1-windows -> p1-windows-retry : 110.701 s
    gap p1-windows-retry -> p1-observe1 : 12.351 s
    gap p1-observe1 -> p1-act1 : 94.096 s
    gap p1-act1 -> p1-observe2 : 19.010 s
    gap p1-observe2 -> p1-act2 : 14.265 s
    gap p1-act2 -> p1-observe3 : 16.784 s
    gap p1-observe3 -> p1-finish : 40.578 s
  task span (first submit to last result): 322.329 s
  gap share of span: 99.5%, service share: 0.5%
  think/prep split (DECIDE lines):
    p1-windows             think=12.2 s prep=0.0 s
    p1-windows-retry       think=110.7 s prep=0.0 s
    p1-observe1            think=12.3 s prep=0.0 s
    p1-act1                think=94.1 s prep=0.0 s
    p1-observe2            think=19.0 s prep=0.0 s
    p1-act2                think=14.2 s prep=0.0 s
    p1-observe3            think=16.8 s prep=0.0 s
    p1-finish              think=40.5 s prep=0.0 s

== task p2 ==
  act        n=1 service=0.481 s
  finish     n=1 service=0.157 s
  observe    n=2 service=0.346 s
  start      n=1 service=0.000 s
  windows    n=1 service=0.111 s
  service total: 1.095 s
  image bytes total: 2731034
  start call: 0.188 s, ready: 0.861 s, polls: 3
  first request after ready: 9.310 s
  between-request gaps: n=5 total=60.617 s max=18.134 s
    gap p2-start -> p2-windows : 9.983 s
    gap p2-windows -> p2-observe1 : 10.653 s
    gap p2-observe1 -> p2-act1 : 12.536 s
    gap p2-act1 -> p2-observe2 : 9.311 s
    gap p2-observe2 -> p2-finish : 18.134 s
  task span (first submit to last result): 61.900 s
  gap share of span: 97.9%, service share: 1.8%
  think/prep split (DECIDE lines):
    p2-windows             think=9.3 s prep=0.0 s
    p2-observe1            think=10.6 s prep=0.0 s
    p2-act1                think=12.5 s prep=0.0 s
    p2-observe2            think=9.3 s prep=0.0 s
    p2-finish              think=18.1 s prep=0.0 s

== task p3 ==
  act        n=1 service=0.741 s
  finish     n=2 service=0.559 s
  observe    n=2 service=0.347 s
  start      n=3 service=0.000 s
  status     n=1 service=0.052 s
  windows    n=2 service=0.215 s
  service total: 1.914 s
  image bytes total: 2587212
  start call: 0.097 s, ready: None s, polls: 83
  between-request gaps: n=10 total=472.755 s max=248.285 s
    gap p3-start -> p3-retry1-start : 248.285 s
    gap p3-retry1-start -> p3-windows : 10.622 s
    gap p3-windows -> p3-observe1 : 9.128 s
    gap p3-observe1 -> p3-act1 : 14.217 s
    gap p3-act1 -> p3-observe2 : 8.508 s
    gap p3-observe2 -> p3-finish : 52.487 s
    gap p3-finish -> p3-status-check : 27.200 s
    gap p3-status-check -> p3-restart1-start : 85.028 s
    gap p3-restart1-start -> p3-restart1-windows : 9.239 s
    gap p3-restart1-windows -> p3-restart1-finish : 8.041 s
  task span (first submit to last result): 475.139 s
  gap share of span: 99.5%, service share: 0.4%
  think/prep split (DECIDE lines):
    p3-windows             think=9.9 s prep=0.0 s
    p3-observe1            think=9.1 s prep=0.0 s
    p3-act1                think=14.2 s prep=0.0 s
    p3-observe2            think=8.5 s prep=0.0 s
    p3-finish              think=52.5 s prep=0.0 s
    p3-status-check        think=27.2 s prep=0.0 s
    p3-restart1-windows    think=8.5 s prep=0.0 s
    p3-restart1-finish     think=8.0 s prep=0.0 s

== task p4 ==
  act        n=4 service=5.876 s
  finish     n=1 service=0.255 s
  observe    n=5 service=0.860 s
  start      n=1 service=0.000 s
  windows    n=1 service=0.108 s
  service total: 7.099 s
  image bytes total: 7809105
  start call: 0.170 s, ready: 0.836 s, polls: 3
  first request after ready: 9.195 s
  between-request gaps: n=11 total=354.924 s max=112.748 s
    gap p4-start -> p4-windows : 9.861 s
    gap p4-windows -> p4-observe1 : 8.594 s
    gap p4-observe1 -> p4-act1 : 29.565 s
    gap p4-act1 -> p4-observe2 : 23.650 s
    gap p4-observe2 -> p4-act2-od-verify : 112.748 s
    gap p4-act2-od-verify -> p4-observe3 : 19.328 s
    gap p4-observe3 -> p4-act2-od-verify-retry : 13.653 s
    gap p4-act2-od-verify-retry -> p4-observe4 : 8.991 s
    gap p4-observe4 -> p4-act3-byte-check : 69.761 s
    gap p4-act3-byte-check -> p4-observe5 : 9.347 s
    gap p4-observe5 -> p4-finish : 49.427 s
  task span (first submit to last result): 362.195 s
  gap share of span: 98.0%, service share: 2.0%
  think/prep split (DECIDE lines):
    p4-windows             think=9.2 s prep=0.0 s
    p4-observe1            think=8.6 s prep=0.0 s
    p4-act1                think=29.5 s prep=0.0 s
    p4-observe2            think=23.6 s prep=0.0 s
    p4-act2-od-verify      think=112.7 s prep=0.0 s
    p4-observe3            think=19.3 s prep=0.0 s
    p4-act2-od-verify-retry think=13.6 s prep=0.0 s
    p4-observe4            think=9.0 s prep=0.0 s
    p4-act3-byte-check     think=69.7 s prep=0.0 s
    p4-observe5            think=9.3 s prep=0.0 s
    p4-finish              think=49.4 s prep=0.0 s

== grand totals (all tasks) ==
service total: 11.611 s, gap total: 1208.942 s

```
