# R8 — đo hiệu năng trên máy Hyprland thật

Đo trên R7 `65078ce7aa04bbfdacb86cd2b3fa7fa15aa1d316`. Không sửa production,
API, skill, ABI hoặc benchmark R5/R6/R7. Không có thay đổi đạt điều kiện
**lợi ích đã đo + bảo toàn tính đúng** để triển khai trong vòng này.

Số liệu từng mẫu, từng lượt provider và nguồn hash:
[r8_measurements.json](benchmarks/r8_measurements.json).
`R8/MEASUREMENT-REPORT.md` trong gói bàn giao là bản sao báo cáo này;
`R8/FAN-OUT-REPORT.md` mô tả đầy đủ phân công, lỗi và đính chính.
Raw logs, nguồn bộ đo và ảnh fixture được giữ riêng trong gói R8 cho reviewer.
Hash trong JSON chỉ liên kết artifacts, không phải chứng thực độc lập.

## Máy và cách đo

- Hyprland **0.56.2**, commit `efb50993780079460b0cbed1363e2166a2de1d9f`;
  màn hình 1920×1200, scale 1, khoảng 144 Hz. CPU Core 5 210H, 12 logical CPUs;
  Linux 7.2.5-3-omarchy, Python 3.14.8, Node v26.7.0.
- Ứng dụng GTK4 thật, hai cửa sổ riêng, nội dung giả lập/local, không tài khoản,
  mạng hay chỉnh setting. Chỉ một người điều khiển GUI tại một thời điểm.
  Đây không phải khảo sát mọi ứng dụng thường dùng của người dùng.
- Một session production có guardian, indicator và Esc; driver riêng gọi nguyên
  `session_driver.execute`. Không sao chép token hay bỏ guard. Các wrapper chỉ
  đo và chuyển tiếp lời gọi. Không build/load plugin, không sync bản cài.
- Năm task agent thật: agent đọc observation rồi chọn ref; không tự động ánh xạ
  tên sang ref và act trong cùng script. Một bộ replay có kiểm chứng riêng so
  sánh hai **đường đã tồn tại**: desktop và a11y. Replay không đo model thinking.
- Mỗi task reset riêng ngoài timer. Timer từ start đến sau xác nhận trạng thái
  ứng dụng. Click a11y có thể ACK trước callback GTK; phải đợi counter, không chỉ
  tin `ok`/`completed`. P95 dùng nearest-rank; n=5 thì P95 là mẫu lớn nhất.
  Không chạy test suite cùng lúc đo live.

## Item 1 — (b) Đã đo: agent hiện tại đã bỏ PNG trên bộ task này

| Task agent thật | Wall ms | CLI tổng ms | Skeleton / drill / act calls | PNG lưu / ảnh đưa model | Backend reply bytes |
|---|---:|---:|---|---|---:|
| Click-type, có tiếng Việt | 14340.084 | 244.390 | 1 / 0 / 1 | 0 / 0 | 8581 |
| Form ba field | 8296.169 | 233.259 | 1 / 0 / 1 | 0 / 0 | 8581 |
| Mở panel rồi bấm | 15680.709 | 540.050 | 2 / 1 / 2 | 0 / 0 | 18990 |
| Qua hai cửa sổ | 23498.674 | 703.194 | 2 / 1 / 3 | 0 / 0 | 25268 |
| Chọn row 7 trong danh sách | 14508.723 | 446.510 | 1 / 2 / 1 | 0 / 0 | 13790 |

Exact text/counter đều được kiểm bằng state riêng của ứng dụng, sau callback.
Row 7 được kích hoạt qua AT-SPI dù nằm ngoài phần nhìn thấy; không gọi đây là
kiểm chứng cuộn vật lý. T1 có lỗi `KeyError` trong script kiểm chứng do đọc
counter sớm; chỉ đọc lại, không gửi lại input; thời gian lỗi vẫn nằm trong wall.
Model ID và usage token của native worker: **UNVERIFIED**.

Không có baseline screenshot giả để tuyên bố tiết kiệm: baseline tự nhiên hiện
đã là `[0,0,0,0,0]`. Không sửa hướng dẫn chỉ để tạo một con số before/after.
Token ảnh góp vào năm task này bằng 0; **tổng token native chưa đo được**.
Reply bytes là JSON backend trước bộ lọc stdout của agent, không phải lượng
text chắc chắn đã vào model. Chia bytes/4 chỉ là proxy text: lần lượt khoảng
2145 / 2145 / 4748 / 6317 / 3448 token, không phải billing.

Bộ replay riêng, 5 block đầy đủ × 5 task × 2 route = **50 task đúng**;
đảo thứ tự route theo block. Desktop dùng tọa độ fixture đã đối chiếu ảnh,
không phải agent reasoning. Cả hai route vẫn giữ guard và verifier.

| Task replay | Desktop median / P95 ms | A11y median / P95 ms | Framebuffer captures desktop | PNG lưu desktop | A11y captures / PNG |
|---|---|---|---:|---:|---|
| Click-type | 483.1 / 504.6 | 447.6 / 454.4 | 3 | 2 | 0 / 0 |
| Form | 624.8 / 633.5 | 455.4 / 461.9 | 3 | 2 | 0 / 0 |
| Panel | 728.0 / 735.5 | 918.0 / 929.2 | 6 | 4 | 0 / 0 |
| Hai cửa sổ | 1549.8 / 1582.6 | 1068.0 / 1075.9 | 12 | 8 | 0 / 0 |
| Danh sách | 1209.8 / 1213.9 | 650.0 / 667.6 | 11 | 4 | 0 / 0 |

Capture dùng PPM trong production; chỉ một số được mã hóa/lưu PNG.
Không gộp capture preflight không lưu, PNG lưu và ảnh model đã đọc thành một số.
Desktop replay tạo **100 PNG**, median **46627 B**, range **39343–49407 B**,
P95 **49360 B**, kích thước toàn cửa sổ khoảng 924/925×1176.
Ước lượng 117 KB/ảnh không khớp fixture đơn giản này; không ngoại suy sang ảnh/web.
Byte nén PNG không quy đổi được thành vision tokens. Giá/token mỗi PNG trên
model thực tế **UNVERIFIED**. Hai ảnh setup root đã xem nằm ngoài năm task trên;
ảnh replay/chẩn đoán không đưa vào model.

## Item 2 — (c) Rebuttal: pixel đứng yên chưa chứng minh paint hoàn tất

Thử riêng hook tại vị trí sleep 80 ms trong `desktop_act`, không sửa file
production. Ba mode, 8 block, ba độ trễ GTK 0/30/60 ms = **72 mẫu**:

1. `fixed80`: sleep thật 80 ms rồi capture cuối nguyên bản.
2. `adaptive`: poll vùng canvas qua capture production, hai hash không đổi trong
   ít nhất 10 ms thì dừng, deadline kiểm giữa các poll là 80 ms; vẫn giữ capture
   cuối nguyên bản. Không cache geometry/focus, không thay guard.
3. `diagnostic80`: tiếp tục poll đến deadline để đo phân bố, không early-return.

Mỗi mẫu đúng khi RGB ảnh after khớp ảnh tham chiếu sau 250 ms, màu tham chiếu
xanh và counter paint đúng 1. Tham chiếu ngoài timer act. Mỗi lần reset hủy timer
paint cũ. Thời điểm callback draw không được gọi là thời điểm compositor present.

| Trễ GTK ms | Fixed80: act median ms / đúng | Adaptive: act median ms / đúng | Adaptive hook median ms |
|---:|---|---|---:|
| 0 | 210.96 / 8 trên 8 | 195.02 / 8 trên 8 | 69.18 |
| 30 | 210.36 / 8 trên 8 | 229.24 / 8 trên 8 | 99.19 |
| 60 | 202.14 / 8 trên 8 | 198.75 / 8 trên 8 | 71.11 |

Trung bình act, trọng số bằng nhau cho ba workload: **209.118 → 206.156 ms**.
Lợi 2.962 ms (khoảng 1.4%), nhưng paired-block bootstrap 95% **[-1.147, 6.979] ms**
(seed 0, 10000 draws, 8 block). Đây chưa là lợi ích ổn định; workload 30 ms chậm hơn.
Không đặt một ngưỡng thắng tùy ý sau đo và không gọi CI này là bảo đảm.

Quan trọng hơn: trong **cả 8 mẫu adaptive delay60**, hai poll đã chấp nhận
màu cũ `[37,63,151]`; after cuối mới xanh `[37,138,63]`. Prototype chỉ đúng nhờ
capture cuối còn giữ nguyên và tốn thêm thời gian. Nếu trả thẳng frame “stable”
để tiết kiệm capture, các frame thực đã đo đó đều chưa phải kết quả paint.
Đây là bằng chứng mới trên máy về quyết định early-stable sai; **không** gọi
prototype after là thất bại — cả 24 after của nó vẫn đúng trong thử nghiệm này.

Phân bố upper bound lần đầu poll nhìn thấy xanh (`diagnostic80`, n=8 mỗi hàng):

| Trễ GTK ms | Min / median / max ms tính từ hook |
|---:|---|
| 0 | 33.79 / 34.95 / 40.78 |
| 30 | 61.39 / 69.05 / 76.84 |
| 60 | 98.35 / 104.62 / 111.76 |

Đây là thời gian **quan sát được** gồm capture/fence/IPC/giải mã, không phải
settle time chính xác. JSON giữ từng interval chuyển màu và timestamp callback.
Capture đang chạy không bị cắt ở deadline: hook diagnostic median khoảng
101–105 ms dù budget 80 ms. Không trình bày đây là deadline cứng 80 ms.
Phân bố chỉ gồm ba paint workload có delay kiểm soát, không phải mọi real app.

Giữ fixed80. Case delayed60 trên đường production vẫn **8/8 đúng**; checker
vẫn phải giữ counterexample R5. Không tuyên bố sleep80 bảo đảm arbitrary delay.
`scripts/cu.py:839–849` đã cho phép bỏ after khi có verifier độc lập;
không cần giảm safety wait cho task cần ảnh cuối.

Raw: `raw/settle-rows.json`, `settle-statistics.json`, ảnh after/reference.
Client timeout 60 s **sau khi đã ghi đủ 72 mẫu**; response cuối gặp BrokenPipe.
Wrapper exit1 được giữ trong `raw/settle.stderr`/`live5-failure.txt`.
Không gọi wrapper này xanh; 72 mẫu được đếm từ records đã hoàn chỉnh, không từ exit.

## Item 3 — (b) Đo IPC: chưa có cache an toàn đáng triển khai

Đo đúng UNIX socket read-only hiện có trong `cu.hypr`, không dùng subprocess
`hyprctl` để thổi phồng latency. Microbenchmark: 120 mẫu/query, 480 tổng,
median clients / monitors / activewindow / cursorpos =
**0.0543 / 0.0293 / 0.0266 / 0.0177 ms** khi đọc liên tiếp ngoài thao tác input.

Trong task live desktop, thời gian operation được chốt **trước** khi hash kết quả
cho trace. Chi phí hash riêng không được tính thành IPC thật. Bản campaign đầu
chưa tách chi phí đó được giữ riêng, không dùng cho bảng này.

| Desktop workload | IPC/task median | IPC tổng median ms | Trần tỷ lệ wall nếu bỏ toàn bộ IPC |
|---|---:|---:|---:|
| Click-type | 60 (range 58–60) | 13.40 | 2.79% |
| Form | 108 | 12.26 | 1.97% |
| Panel | 68 | 15.55 | 2.15% |
| Hai cửa sổ | 150 | 37.07 | 2.39% |
| Danh sách | 87 | 18.41 | 1.52% |

Năm task native-a11y thật: **0 Hypr query trong task**, không tính setup/guardian.
Queries giống kết quả có thật: ví dụ form 89–90/108, multi-window 116–118/150
lặp lại hash cùng query. JSON có latency/query/task và số lần lặp từng mẫu.
Không coi “kết quả đã giống nhau” là cho phép bỏ kiểm tra ở lần sau.

Guard trước/sau capture và qua input/IME/wait cần dữ liệu mới (`cu.py:333–365`,
`739–746`, `819–829`). Trong một guard, mỗi loại query chỉ được đọc một lần.
TTL xuyên các ranh giới đó đổi behavior an toàn. Không nghiên cứu/chạy lại
finding cache R5 đã đóng, không cache activewindow/cursorpos. Con số bỏ mọi IPC
là **trần lý thuyết**, không phải mức cache có thể đạt an toàn.

## Item 4 — (b) Payload đã đo; chưa triển khai dirty-subtree protocol

Native task thực có **75210 B** reply backend cộng lại, zero ảnh. Theo từng lượt:

- Skeleton: 22–23 elements, **2962–3049 B** reply.
- Drill panel: 5 elements, **1082 B**; drill scroll/list: 13/25 elements,
  **1413/3796 B**.
- Automatic after a11y: 41–45 elements, **5618–6279 B** reply.

Đây là trước agent lọc stdout; không gọi toàn bộ số này là model input.
Field values bị redacted; cây không thay đổi không chứng minh text/action đúng.

Một phép chiếu diff offline trên snapshots thật, cùng task nhiều lượt:
T3 reveal và T4 reveal đều cho **6902 B** items đầy đủ có path so với
**4685 B** diff envelope (23 item đổi, 18 path xóa). Sau T4 panel-action,
items không đổi: **6902 → 56 B** envelope giả định. Đây là serialized projection,
**không phải API chạy được hay token/time savings đã đạt**. Các cặp qua reset/task
khác cũng có trong JSON nhưng không dùng để tuyên bố tiết kiệm multi-round.

Dirty protocol cần base ID, ref/snapshot binding, strict bounded patch validation,
resync khi mất base và kiểm chứng app riêng. Không bỏ các semantics đó để giảm
bytes. Chưa có phép đo end-to-end của protocol bảo toàn hành vi, nên không triển
khai chỉ dựa trên projection. Có cơ hội giảm output ở app lớn; bộ nhỏ này chưa
chứng minh lợi tổng đủ để thêm protocol.

Usage provider thực từ hai lần OpenCode PARTIAL (không tính là 5 task thành công):

| Invocation | Assistant messages có usage | Input | Cache read | Output | Reasoning |
|---|---:|---:|---:|---:|---:|
| Stage2 | 20 | 51540 | 6386132 | 4154 | 1817 |
| Stage3 | 9 | 8021 | 2972409 | 2397 | 554 |

Từng tool round giữ trong `opencode_usage.*.rounds`, gồm usage, bytes và gap.
JSONL có 19/8 tool rounds; export khớp message IDs bổ sung final text-only
messages thành 20/9. `complete_export_usage` giữ từng message cùng usage thực.
Đây là fields provider báo; không cộng reasoning với output khi chưa biết
chúng có chồng nhau không. Final text-only usage lấy từ assistant messages tương ứng trong export,
không từ cumulative session totals. Bảng không bao gồm native hay các
invocation khác và không được gọi là toàn bộ chi phí dự án. OpenCode báo cost0 trên model miễn phí; chi phí native
không có telemetry, **UNVERIFIED**, không suy ra tổng USD bằng 0.

Inherited context khoảng 300k+ tokens mỗi round lớn hơn nhiều reply vài KB.
Cache read 6.39M là history/provider accounting, không phải tree mới.
Không có decomposition provider chính xác cho system/history/tree/ảnh; backend
bytes và provider totals là hai phép đo khác nhau, không ép chúng cộng thành
một biểu đồ 100%. Tỷ lệ token giảm tổng hoặc token mỗi PNG vẫn UNVERIFIED.

## Item 5 — (b) Profile hoàn chỉnh; đầu vào định lượng cho vòng tiếp

Bảng item1 là breakdown task agent thật: observe/act theo từng CLI có trong JSON,
CLI chỉ khoảng 233–703 ms trong wall 8.30–23.50 s. Phần còn lại gồm model,
tool orchestration, scheduling, verification và lỗi script; **không gắn nhãn
“model think” cho phần dư**. Native không có inference telemetry riêng.
Trong replay, sleep80, encode/persist, capture, pointer, IME và IPC có trace riêng;
chúng lồng nhau, không cộng các duration inclusive như các phần rời nhau.

Ba time sinks khác ảnh/tree/IPC/history, xếp theo độ lớn quan sát được:

1. **Các lượt model/tool qua lại.** Stage2 có gap giữa finish lượt trước và
   start lượt sau: median **4360.5 ms**, tổng **109816 ms** cho 18 gap.
   Gap gồm provider/queue/transport/model, không phải inference thuần; stage2
   là run lỗi nên không dùng làm SLA. Ưu tiên batch các quyết định độc lập sau
   một observation, giữ điểm dừng khi layout đổi. Ước tính mỗi lượt thật sự bỏ
   được có thể tránh cỡ một gap đo được, không bảo đảm 4.36 s/task.
2. **Callback GTK sau ACK a11y.** Replay semantic nằm ngoài CLI khoảng
   **207–219 ms** ở click-type/form/list và **418–419 ms** ở panel/multi-window
   (median), gồm polling/RPC và callback. Core act báo 1–6 ms không bao gồm
   phần này. Không bỏ verification để lấy số đẹp. Có thể gộp các action độc lập
   để overlap callback; lợi còn lại **chưa đo**, không sửa ứng dụng của người dùng.
3. **Khởi tạo process/GI cho adapter.** Microbenchmark mới, 15 mẫu/mode:
   Python pass **8.13 ms**, imports `cu`+GI/AT-SPI **68.65 ms**; environment
   refresh riêng **15.14 ms**. Đây là read-only process/import test sau GUI,
   không phải warm-worker A/B. Worker a11y sống theo session là hướng có thể thử;
   khoảng 68.65 ms/call là trần tham khảo, không phải gain đã đạt. Phải tách
   entrypoint stdin hiện tại, bảo toàn timeout/cancel và snapshot mới mỗi lệnh.

Ba token sinks ngoài ảnh/tree/history, theo magnitude quan sát/proxy Stage2:

1. **Reasoning model:** provider báo **1817 tokens**. Có thể thử brief/task hẹp
   và command schema đúng; mức tiết kiệm chưa đo và không được hy sinh quyết định
   an toàn. Output/reasoning có thể chồng nhau.
2. **Tool code sinh lại:** 17 shell commands, **6023 UTF-8 B**, proxy khoảng
   **1506 text tokens**. Client có command schema rõ có thể giảm Python lặp lại;
   gain tương lai tối đa bị chặn bởi phần code có thể bỏ, không phải toàn bộ usage.
3. **Nội dung report sinh trong write:** **2357 UTF-8 B**, proxy khoảng
   **589 text tokens**. Dùng template artifact ngắn cho task thường có thể giảm
   phần này; báo cáo audit R8 vẫn bắt buộc nên không cắt chứng cứ ở vòng này.

Các proxy text /4 không là tokenizer chính xác hay phần bill độc lập; không cộng
chúng vào reasoning để tuyên bố total saving. Commentary thêm 904 B, không nằm
trong top3. Tool schemas/system overhead không được đo riêng: UNVERIFIED.

## Lỗi, mẫu loại và giới hạn phải giữ

- Fixture đầu lỗi GTK `update_property` gọi scalar thay vì sequence: chưa có
  input task. Root sửa scaffold riêng; log `pilot-fixture.stderr` còn nguyên.
- OpenCode stage2 sai `--ref`; stage3 dùng đường dẫn `PLACEHOLDER`; session
  production dừng đúng. Wrapper cả hai exit0 không nghĩa là task hoàn thành.
  T2 stage2 kết thúc trước callback; T2 stage3 tự resolve refs trong script.
  Không tính chúng vào năm task model-controlled/verified ở item1.
- Replay pilot thứ nhất không verify được panel action do layout fixture cũ;
  pilot thứ hai thiếu drill cấp list. Giữ `pilot-*`/`pilot2-*`, không trộn kết quả.
- Campaign replay đầu hoàn chỉnh 60 task có timer IPC bao gồm hash overhead.
  Giữ `inclusive-*`, không dùng làm latency IPC. Campaign timer đã sửa dự kiến
  60: hoàn chỉnh **57 markers**, task tiếp theo bị ngắt; chỉ giữ **50** từ block0–4.
  Loại toàn block5, kể cả 7 task đã hoàn chỉnh, vì root chạy micro probe quá sớm.
- Probe phụ bị treo vì root `import a11y` đọc stdin ở entrypoint module,
  **không phải bằng chứng AT-SPI deadlock**. Hai client timeout; root yêu cầu
  `finish`; guardian dừng process. Không resume/replay. Không có kết quả warm-worker
  để báo. Micro import timings cuối dùng các imports thành phần, không import
  entrypoint đọc stdin. Log lỗi, exit1 và traceback giữ nguyên.
- Root sửa cách phân tích telemetry: union các tool intervals khi song song;
  step_start→finish không bao trọn inference, nên thêm inter-round gap;
  đính chính report worker nhầm T1 flag với T2 premature end. Original report
  và `analysis/root-errata.md` đều được giữ.
- Bộ đo có overhead wrapper/hash/RPC, không phải production SLA. Snapshot full
  bytes không phải model input sau filtering. Không đo CPU utilization, giá vision,
  native provider totals hay thời gian present chính xác.

## Bảo toàn và kiểm thử

Không đổi tracked file production nào so với R7. File riêng
`tests/session_quiet_live.py` không stage/commit; SHA256 phải vẫn
`aa5af4d1cf3ad53ca28681ea25edaa9b2191b40f0a936b6825d0e9d62a4f3c63`.
Session/fixture đã dọn; focus/workspace ban đầu được trả lại khi không có cancel;
IME kiểm lại là bamboo, state2. Không xóa cancellation để chạy tiếp.

Kết quả prepush và pushed-tree acceptance sẽ ghi trong artifacts riêng, gồm
commands/exits, pass/skip thực, hash tracked trước/sau và exact commit.
Báo cáo này không lấy test R7 làm test R8 và không gọi kiểm trước push là
pushed verification. Không thay samples/evidence cũ để làm test xanh.
