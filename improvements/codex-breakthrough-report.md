# Báo cáo kiểm toán độc lập: hướng đột phá cho computer-use-wayland

## Phạm vi kiểm tra

Đọc trực tiếp docs/zen-error-fix-todolist-20261121.md, toàn bộ /tmp/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md, scripts/cu.py, các adapter browser/accessibility, broker/session driver và mã act-now đã cài trên laptop. Tôi không mở hay điều khiển cửa sổ, tab hoặc phiên trình duyệt. Phép đo mới duy nhất là tổng hợp JSONL đã có sẵn của act-now.

## 1. Verdict

Hướng hiện tại không vững nếu tiếp tục lấy một ảnh rồi bắt model chọn càng nhiều tọa độ càng tốt làm vòng điều khiển chính. Driver có một số nền tảng tốt: ánh xạ tọa độ từ vùng ảnh, kiểm tra con trỏ, khóa session, overlay và không phát lại batch khi kết quả có thể đã chạy. Nhưng hợp đồng chính vẫn là gửi x/y rồi coi driver nhận đủ input là thành công; nó không chứng minh nút nào nhận click hay ứng dụng đạt mục tiêu. Cần đổi trọng tâm sang một executor cục bộ hiểu tên và trạng thái điều khiển, thực hiện thao tác chuột hoặc bàn phím thật, kiểm tra điều kiện trước và sau, rồi chỉ gọi model hoặc dùng ảnh khi cấu trúc UI không đủ. Giữ screenshot làm đường dự phòng, giữ an toàn của session, và gộp các backend đang rời rạc vào một luồng thực thi có bằng chứng.

## 2. Weaknesses found

### 2.1 Báo thành công khi mới gửi được input

scripts/cu.py:1541-1549 tự ghi rõ kiểm tra desktop chỉ biết vị trí con trỏ, không biết phần tử UI nhận sự kiện. scripts/cu.py:1580-1592 từ chối nếu con trỏ lệch hơn 3 px so với tọa độ được yêu cầu, nhưng điều đó chỉ kiểm tra khâu di chuyển chuột. scripts/cu.py:1806-1809 so hash pixel và giải thích rằng ảnh thay đổi, kể cả do animation, không xác nhận hành động thành công. Với AT-SPI, scripts/a11y.py:204-219 coi do_action trả true là click hoàn tất; không kiểm tra trạng thái sau click.

Mã act-now đã cài trên laptop biến kết quả này thành ok=true khi cu.py báo ok hoặc đủ số action hoàn tất: /home/james/.local/share/agent-computer-use/scripts/first_action.py:422-439. Vì vậy click đúng pixel nhưng vào khoảng trống vẫn có thể thành công theo hợp đồng của tool. Lỗi chat Brave được ghi tại /tmp/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md:302-313 cho thấy chính trường hợp đó: các batch báo xong nhưng tin không được gửi; lần kiểm tra sau tìm thấy điểm click cao hơn ô nhập 64-75 px. Đây là lỗ hổng xác minh, không chỉ là lỗi vision.

Mỗi kết quả cần tách ít nhất ba điều: input đã gửi, đúng mục tiêu nhận input, và trạng thái sau đó đã được xác nhận. Hiện hai trạng thái sau chưa được desktop backend chứng minh.

### 2.2 Scope của observation đổi giữa các bước

desktop_act chỉ cho phép key và type khi observation thuộc một cửa sổ, không phải toàn màn hình: scripts/cu.py:1473-1475. Tuy nhiên first_action.py luôn chụp after bằng observe_screen, kể cả khi batch đầu vào dùng window observation: /home/james/.local/share/agent-computer-use/scripts/first_action.py:480-485. Nếu model dùng ảnh after đó cho bước gõ tiếp theo, bước mới bị từ chối theo đúng luật hiện có.

Lỗi thứ hai nằm trong _fresh_observation: khi observation thiếu, lỗi hoặc quá cũ, wrapper chụp toàn màn hình rồi vẫn đưa nguyên action list cho executor: first_action.py:289-315. Wrapper ghi source=captured trong envelope, nhưng không chuyển tọa độ theo frame mà agent đã dùng và không dừng để xin target mới. Sự cố J40 ghi nhận chính hậu quả này: điểm lấy từ ảnh cửa sổ bị dùng trên ảnh toàn màn hình và hụt nút khoảng (+45,+12) px, trong khi lệnh vẫn trả ok: /tmp/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md:848-852. J35 ghi nhận observation cửa sổ 1863x1176 và after toàn màn hình 1920x1200: dòng 822-826 cùng file.

Cần coi scope là một phần bắt buộc của dữ liệu hành động. Observation mới khác scope phải làm dừng batch, không được tự đổi frame rồi tiếp tục.

### 2.3 Vision sai, nhưng scale màn hình không giải thích hết

E2 đo 17/29 lần tìm điểm trúng ngay từ đầu, tức 58.6%; cả 29 lần con trỏ tới điểm được yêu cầu với sai số 0.5-0.9 px: docs/calibration-e2-report.md:31-59 và docs/final-report-20261121.md:63-64. Tôi tính khoảng Wilson 95% cho tỷ lệ 17/29 là 40.7%-74.5%. Mẫu này cho thấy vision grounding kém trên grid đó, nhưng còn nhỏ và không phải tập held-out của app mới. G30 là một ví dụ độc lập có giá trị hơn cho nguyên nhân đọc ảnh: điểm nhìn thấy ô nhập thấp hơn thực tế 64-75 px.

Ngược lại, dữ liệu geometry ghi màn hình 1920x1200, scale 1; scripts/cu.py:973-977 ánh xạ pixel ảnh qua vùng capture rồi sang pixel compositor. Đây là bằng chứng không ủng hộ chẩn đoán chung rằng thiếu một hệ số scale toàn cục là nguyên nhân duy nhất. Có ít nhất hai loại lỗi: model chọn sai mục tiêu trong ảnh, và orchestration đưa ảnh hoặc tọa độ thuộc frame khác nhau vào cùng hành động.

Đầu vào ảnh cũng không đồng nhất. observe mặc định giới hạn 960 px chiều rộng: scripts/cu.py:2303. save_observation lưu JPEG q90: scripts/cu.py:807-863. Ngược lại, act-now tự capture ảnh mới ở max_width=1920: first_action.py:313. Vì vậy kích thước và độ nén của ảnh model thấy thay đổi theo đường đi. Mã ánh xạ có thể bù scale số học, nhưng model vẫn phải nhận ra mục tiêu từ ảnh có độ phân giải và chi tiết khác nhau.

Một vấn đề phụ đã có bằng chứng: preflight so ảnh JPEG đã giải mã với capture mới chưa nén; scripts/cu.py:979-1000 dùng ngưỡng patch 6. J37 báo patch quanh con trỏ khác 6.627 và gây từ chối không ổn định: file lỗi dòng 832-837. Đây là khả năng false refusal do codec, cần tách khỏi việc màn hình thực sự đổi.

### 2.4 Tối đa hóa hành động trên một ảnh là mục tiêu sai

Desktop và code-exec đều nhận tối đa 32 actions một lần: scripts/cu.py:1013-1019, scripts/code_exec.py:187-192. Batch desktop kiểm tra focus, cửa sổ, geometry và màn hình trước hành động, rồi có thể chạy nhiều thao tác trên cùng một observation. Các guard đó không kiểm tra rằng click đầu đã mở đúng trang, focus đúng ô, hoặc bước trước không làm các tọa độ sau lỗi thời. After capture chỉ diễn ra ở cuối batch.

Nếu hit rate mỗi click là 90%, xác suất cả 20 click đều đúng lần đầu chỉ khoảng 12.2% khi giả sử lỗi độc lập và không retry; với 32 click là 3.4%. Lỗi thật có tương quan nên đây chỉ là minh họa, nhưng nó đủ chỉ ra rằng 90% per-click không có nghĩa 90% task thành công. Batch nên tăng khi executor chứng minh các bước kế tiếp vẫn hợp lệ, không phải vì có thể nhét thêm tọa độ vào cùng ảnh.

### 2.5 Có nhiều backend, nhưng chưa có một executor chung

Repo có desktop act, Chromium CDP, AT-SPI, Zen Marionette/BiDi và code-exec. Nhưng đường đi của act-now chỉ gọi desktop_act, không route mục tiêu web sang DOM hoặc AT-SPI: first_action.py:403-405, 457-460. code-exec có DOM actions và assertions, nhưng định nghĩa cửa sổ DOM là chromium và chỉ bật khi CU_CODE_EXEC=1: scripts/code_exec.py:41-53, 69-77, 92-103. Zen helper nằm riêng.

scripts/zen_dom.py:81-115 khởi chạy geckodriver và tạo một WebDriver session cho mỗi invocation. CLI của nó thực hiện một list, eval hoặc locate rồi đóng session: lines 221-245. locate chỉ querySelector một CSS selector và lấy getBoundingClientRect: lines 172-185. Nó không xác nhận phần tử đang hiện, có thể tương tác, không bị che, đang đứng yên, hoặc selector chọn đúng trong nhiều phần tử. Hình chữ nhật chính xác trong CSS không đồng nghĩa mục tiêu đúng hoặc điểm đó nhận click.

Zen helper còn có eval chạy JavaScript không giới hạn trong tab hiện tại: lines 151-155, 221-245. Giao diện agent bình thường không nên có lệnh tùy ý sửa trang như một primitive mặc định; nên chỉ lộ API đọc/truy vấn có giới hạn và giữ eval cho chế độ phát triển có chủ ý.

AT-SPI cũng chỉ là một nguồn một phần: scripts/a11y.py:83-104 duyệt tối đa 500 node hoặc 2 giây, trả tối đa 80 item và đặt cờ truncated; query bị khóa sau fastpath flag ở lines 118-139. Đây không phải lý do bỏ accessibility, mà là lý do backend cần trả rõ độ bao phủ rồi chuyển sang DOM hoặc ảnh khi cây không đủ.

Kết quả nghiên cứu Zen đã chứng minh DOM đọc nhanh và tọa độ rect hữu ích, nhưng chính record cũng nói BiDi pointer click thất bại, Marionette có giới hạn viewport và click không tương đương chuột thật: docs/zen-dom-control-comparison.md:67-120. Đường đúng là semantic locate + input thật khi cần hover/trusted event + xác minh trạng thái, không phải DOM click cho mọi control.

### 2.6 act-now không dùng session driver dài hạn

Repo có session_remote broker và JSON-lines session-driver: scripts/session_remote.py:460-520 và scripts/session_driver.py:59-75. Broker giữ một driver chạy lâu và tuần tự hóa request. Nhưng act-now dựng lệnh cu.py session cho từng invocation: first_action.py:172-178, 403-405. Như vậy wrapper mới không dùng đường session bền vững đã có; mỗi batch có lại startup/teardown. zen_dom cũng mở và đóng session cho mỗi lệnh.

Điều này làm nhiều lớp safety và lifecycle phải được duy trì song song. Cần một owner duy nhất của pointer, overlay và session Firefox, với hàng đợi tuần tự. Không mở BiDi và Marionette từ các client cạnh tranh vì bản ghi cho thấy hai giao thức dùng chung một slot của Zen.

### 2.7 Bộ đo latency không đo đúng lời hứa

first_action.py ghi order_to_overlay_ms từ lúc Python wrapper bắt đầu, không phải từ lúc người dùng ra lệnh trên VM: lines 339-400. Mã không ghi timestamp first pointer action. target_breached lại so tổng thời lượng của cả batch với ngưỡng 30 giây: lines 495-498. Vì vậy cờ này không đo first-action latency. Ghi chú cùng file lines 40-48 thừa nhận thời gian không gồm model decision và phần observation trước khi gọi tool.

Tổng hợp read-only log sẵn có tại /home/james/.cache/agent-computer-use/first-action-20261122.jsonl: 199 dòng, p50 order-to-overlay 337.5 ms, lớn nhất 368.4 ms; p50 tổng wrapper 2.288 giây, lớn nhất 6.95 giây; 195 đường session, 4 fallback, 0 timeout. Có 167 envelope ok=true và 32 ok=false. Những số này đo thời gian và trạng thái executor, không phải click hit rate hay task success. Năm lần dùng observation source=captured. Các lỗi log gồm screen changed, key/type trên screen scope, Ctrl+T, tọa độ ngoài ảnh, focus/geometry. Đây là các refusal hữu ích, nhưng log không có target element hay postcondition để xác định ok=true có đúng mục tiêu không.

Không tìm thấy record hỗ trợ chính xác giả thuyết 11.6 giây trên 12.26 giây là SSH dispatch. Log act-now bắt đầu sau khi lệnh đã tới laptop nên không đo SSH. Một kết quả khác ghi service 11.611 giây và gap 1208.942 giây cho nhiều task, nhưng đó là số đo khác, không chứng minh hay bác bỏ tỷ lệ SSH 95%: improvements/speed-proto-pick4-summary.md:38. Cần đo riêng VM-to-laptop dispatch với cùng workload, fresh SSH và connection reuse.

### 2.8 Bằng chứng nhanh chưa đại diện cho task thực

Fixture form chạy trong Zen thật đạt 0.64 giây và 15 bước theo docs/final-report-20261121.md:160-176. Nhưng trang là fixture mô phỏng quy trình Polygon, không phải task upload trên trang Polygon; báo cáo tự ghi không có baseline cùng task ở lines 178-194. Bản ghi 13/13 verified action không thể biến thành cam kết 90% cho app khác. Todolist còn ghi held-out app mới và agent độc lập là PARTIAL ở dòng 38; J10 nói think-time thật vẫn OPEN tại file lỗi dòng 717.

Todolist đánh dấu nhiều mục DONE theo hướng đã xác định hoặc có fixture, nhưng các mục đó không đồng nghĩa đã chứng minh trên app thật. Cần xem DONE là trạng thái của một bằng chứng cụ thể, không phải trạng thái chung của tính năng.

### 2.9 Mã đã cài không được checkout hiện tại tái tạo

Checkout hiện là branch todolist-push, HEAD 4500a18, local remote-tracking ref báo behind 622 commit. scripts/first_action.py không có trong repo và không được git track; bản đọc được nằm ở /home/james/.local/share/agent-computer-use/scripts/first_action.py. Installed cu.py có hai nhánh act-now bổ sung so với scripts/cu.py của checkout. Có các file untracked trong repo từ trước; tôi không sửa chúng.

Điều này cản trở review, test và deploy có thể lặp lại. Một hành vi đang chạy trên laptop phụ thuộc wrapper không có trong source checkout và một ref remote cũ. Trước khi dùng các benchmark này làm chuẩn release, phải khóa source commit, artifact đã cài và log của cùng build vào một manifest.

### 2.10 Overlay và suy nghĩ model còn hai câu hỏi khác nhau

Todolist ghi overlay idle có 0 repaint và 0 event trong các lần đo, nhưng test nền LIQUID không chạy vì plugin không được load: docs/zen-error-fix-todolist-20261121.md:42-45. Vì vậy chưa có bằng chứng rằng tình trạng nhấp nháy lúc ban đầu đã được tái tạo hoặc sửa. Cùng lúc, phần think-time không được đo bởi act-now và J10 đánh dấu H2 còn mở. Không nên quy hai vấn đề này về SSH hay screenshot khi chưa có số đo ở các pha riêng.

## 3. Breakthrough proposal

### Xây một semantic transaction executor cục bộ

Thay action JSON thông thường từ tọa độ sang một yêu cầu có ý nghĩa:

- Target: role và tên mục tiêu, hoặc selector/ref đã đọc từ snapshot mới.
- Scope: cửa sổ hoặc tab cụ thể, frame ảnh/DOM, và ID của observation.
- Preconditions: mục tiêu duy nhất, nhìn thấy, bật, đúng cửa sổ; geometry và focus chưa đổi.
- Input: chuột thật, bàn phím thật, hoặc API/DOM action đã được xác nhận phù hợp với control.
- Postcondition: ví dụ dialog đóng, URL đổi, ô đã có giá trị, trạng thái checked đổi, hoặc text mới xuất hiện.
- Retry policy: chỉ retry khi executor biết chắc chưa gửi input; kiểm tra trạng thái trước khi phát lại hành động có thể gửi hoặc xóa dữ liệu.

Executor resolve target ngay trên laptop bằng backend phù hợp: DOM/BiDi cho trang web, AT-SPI cho control desktop, và screenshot crop cho canvas, nội dung ảnh hoặc control không được expose. Khi cần hover thật như Browse, đọc DOM để tìm đúng control rồi dùng chuột thật. Sau mỗi bước có khả năng đổi trang hoặc focus, executor đợi một postcondition tại máy và trả về diff nhỏ. Chỉ yêu cầu model xem ảnh mới nếu điều kiện không giải được bằng dữ liệu cấu trúc.

Model nên quyết định mục tiêu và nhánh khó. Executor nên làm các bước ổn định như tìm, điền, đợi trang sẵn sàng, đọc lại field và kiểm tra kết quả. Một form có thể chạy nhiều bước trong một lần gọi, nhưng Submit hoặc click có thể gây side effect phải có precondition và postcondition riêng. Đây là cách giảm vòng model mà không đặt cược toàn bộ task vào một ảnh cũ.

### Dùng lại nền tảng, gộp đường đi

- Đưa session owner, overlay, desktop input và browser session vào một broker cục bộ duy nhất. Route act-now qua session-driver thay vì tạo session mới cho mỗi batch. Giữ fallback chỉ khi log xác nhận session chưa chạy action; timeout tiếp tục không replay.
- Thêm adapter Zen vào cùng hợp đồng với Chromium và AT-SPI. Dùng một remote-session owner duy nhất cho Zen, có timeout và đóng session trong finally. Thêm xử lý visibility, hit-test, element chuyển động, CSS transforms, iframe offsets và target không duy nhất.
- Mỗi target ref phải gắn với snapshot ID và scope. Observation hết hạn hoặc đổi scope thì từ chối, không âm thầm thay bằng screen capture khác.
- Giữ desktop_act cho chuột/keyboard thật, nhưng đổi ok thành input_sent; chỉ đặt verified=true khi có postcondition. Dùng PNG hoặc ảnh lossless crop cho các trường hợp vision fallback và giữ ảnh cấu trúc thấp nhất cần thiết.
- Bỏ kỳ vọng rằng một ảnh phải lái tối đa actions. Bỏ generic x/y làm đầu vào thường ngày của model. Giữ tọa độ như chi tiết nội bộ của adapter pointer.
- Gỡ unrestricted zen_dom eval khỏi giao diện agent mặc định; giữ nó trong chế độ debug có chủ ý.

### Độ khó, rủi ro, và cách chứng minh

Một prototype cho Zen với semantic target, chuột thật, precondition và postcondition cần khoảng 2-3 ngày nếu dùng fixture riêng và một số task web ít rủi ro. Hợp nhất broker, thêm desktop AT-SPI và xử lý các giới hạn Firefox có thể cần 1-2 tuần cho một kỹ sư. Bộ benchmark độc lập cần thêm vài ngày. Đây là ước lượng, chưa phải kế hoạch được thực thi.

Rủi ro chính: Zen chỉ có một remote session slot và session bị treo có thể chặn mọi client; một số control cần sự kiện chuột thật; iframe, shadow DOM, canvas, native file picker và Wayland extent có thể thiếu dữ liệu; DOM fill có thể không tạo cùng hiệu ứng như gõ phím thật; UI đổi giữa lúc đọc và click. Giảm rủi ro bằng một session owner, không retry input không xác định, đọc lại target sát thời điểm click và giữ vision/native input làm fallback.

Đo trên 100 task held-out có cả browser và app desktop, nội dung và bố cục mới. Ghi riêng:

- Tỷ lệ đúng mục tiêu ngay lần đầu, không tính retry là pass.
- Tỷ lệ task thành công end-to-end, số side effect sai và số hành động cần phục hồi.
- P50/P90 thời gian của model, SSH, broker, observe, act và verify.
- Số lần gọi model, ảnh full screen, crop, DOM/a11y query và lần retry.
- Độ chính xác của postcondition và số false success.

Định nghĩa trước 90% là click hit rate hay task success. Nếu mục tiêu là task success ít nhất 90% với độ tin cậy 95%, một mẫu 100 task cần khoảng 96 pass trở lên theo Wilson, với giả định mẫu độc lập và đại diện. Không gộp 13/13 trên fixture với 90% task thật. So sánh screenshot-only, DOM+chuột, AT-SPI+chuột và executor đề xuất trên cùng tập task, xen kẽ thứ tự để giảm ảnh hưởng thời gian hoặc thay đổi UI.

## 4. Anything I could not verify

- Không tìm thấy bằng chứng cục bộ cho tuyên bố sweep 66 element và 5/5 click từ cùng một snapshot. Có bằng chứng fixture 13/13 và công cụ zen_dom trả một rect cho selector, nhưng không đủ để xác nhận tuyên bố 66/5.
- Không xác minh được SSH chiếm 95% của 12.26 giây. Log cục bộ không bao gồm thời gian trước khi lệnh đến laptop.
- Không thử lại click trong browser, BiDi, Marionette, AT-SPI, overlay hoặc compositor. Không mở, đóng hay đổi tab/cửa sổ.
- Không xác minh overlay flicker trong chế độ LIQUID vì record nói plugin không được load; cũng không đo model think time trên một task agent-driven mới.
- Chưa chứng minh 90% task success trên held-out app. Các số 17/29 và 13/13 chỉ áp dụng cho hai phép thử cụ thể được mô tả.
- Không fetch origin, nên trạng thái behind 622 là theo remote-tracking ref có sẵn trong checkout. Không thể khẳng định checkout đó là source chính xác của mọi artifact đã cài.
- Không chạy test suite. Chỉ đọc mã, tài liệu và tổng hợp log hiện có. Repo không bị sửa; chỉ tạo báo cáo này.

