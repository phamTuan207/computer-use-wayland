# Workflow Lauren Tan: tổng thể điều phối đa agent

Tổng hợp ngày 22/11/2026 từ talk gốc, clip TikTok, các phân tích độc lập và 2 file nội bộ của team. Đây là bản quy trình rõ ràng cho team làm theo, không chỉ vụ review code mà tổng thể workflow điều phối đa agent.

## 1. Cô là ai, nguồn nào

- Lauren Tan, handle @poteto (clip TikTok gọi là "chị Khoai Tây"). Học tài chính kế toán, chuyển sang code. 4 năm Netflix, 6 năm Meta (React Core team, làm React Compiler, staff engineer/EM), rồi Cursor (Member of Technical Staff), nay là Principal Engineer tại SpaceX (trước là xAI), team Grok Bot.
- Talk gốc: "All Code Is Slop (Except Mine)", AI Engineer Code Summit, video đăng 14/11/2026, dài 17:32, 1,39 triệu lượt xem. Link: https://www.youtube.com/watch?v=O_zcc6Xl12g
- Clip TikTok team đã crawl: https://www.tiktok.com/@anythingai39/video/7710239842663288071, @anythingai39 đăng 20/11/2026, dài 222 giây, 61.792 plays. Đây là bản tóm tắt tiếng Việt của talk, không phải chính cô nói.
- Cô open-source pstack, plugin cho Cursor (Markdown skills + subagent poteto-agent + scripts, MIT). Chữ P trong pstack là Process: playbook để agent làm engineering nghiêm túc. Repo: https://github.com/cursor/plugins/tree/main/pstack
- File nội bộ: improvements/worker-w-crawl-clip-20261121.md (transcript + đối chiếu nguồn) và improvements/working-structure-redesign-20261121.md (đề xuất tái thiết đã duyệt 21/11).

## 2. Nguyên tắc nền: kim tự tháp tin tưởng

Khi agent mắc lỗi, sửa theo thứ tự từ trên xuống, càng rộng càng đầu tư nhiều. Human review là đỉnh nhọn đắt nhất, để dưới cùng.

1. Codebase: API design, kiến trúc, refactor, sao cho lựa chọn sai không thể viết ra được.
2. Check xác định: lint, types, compiler, tests, không phụ thuộc phán đoán của model.
3. Validation: runtime validation (agent tự chạy code) và formal verification (TLA+, Lean, property-based UI testing).
4. Text rules: AGENTS.md, rules files, skills, chỉ cho thứ cần phán đoán và không mã hóa thành check được.

Khi sửa lỗi, hỏi 2 câu trước: có biến thành check xác định chặn lỗi ngay lúc viết không? Tốt hơn nữa, có đổi thiết kế để lựa chọn sai không thể viết ra không? Chỉ khi cả hai đều không được mới đưa vào rules file.

Ví dụ thật trong talk: ở Cursor, agent từng import code main-process vào renderer process. Cách sửa: tách thành 2 thư mục top-level tên rõ ràng, dùng dependency analysis + lint cấm cross-import. Agent từng dùng setTimeout/requestAnimationFrame vá khoảng trống rồi viết comment biện hộ. Cách sửa: cấm khoảng 99% comment, thay bằng lint rule mà error message bảo agent sửa root cause.

## 3. Xây môi trường trước, rồi mới scale

Cô mất khoảng 6 tháng chỉnh môi trường làm việc của agent trước khi đạt tốc độ cao, và 6 tháng đó đến trước mọi kiểu tự động hóa "software factory". Thứ tự setup:

1. Cài pstack, chạy /setup-pstack, chọn model theo vai: model lớn làm coordinator, model hiệu quả làm coding workhorse.
2. Bắt đầu với 0 skill, quan sát agent fail ở đâu rồi mới kéo skill vào, và đo xem skill có thật sự làm agent thông minh hơn không.
3. Chạy /create-verification-skill cho từng app. Nó viết skill gồm Launch, Doctor, Drive, Evidence, Cleanup, cộng feature map. Trước khi bàn giao, nó tự chứng minh end-to-end một lần.
4. Xây CLI nhỏ thân thiện với agent cho app: subcommand composable, --dry-run cho mọi thứ destructive, error mô tả rõ, --help đầy đủ, output JSON machine-readable.
5. Thêm feature map: index markdown tìm được của mọi feature, cách tới được nó và kết quả nào chứng minh nó chạy đúng. Cô gọi là "materialized memory".
6. Lên lịch /maintain-verification-skill hàng ngày. Kết quả chỉ là clean, changed (1 PR giới hạn trong thư mục của skill) hoặc blocked, và không bao giờ sửa product code.
7. Cloud agent làm mặc định: mỗi agent có máy riêng nên chạy được app, quay video, chụp screenshot, lái UI. Đó là lý do cô tin output.
8. Gom việc vào Cursor Projects, chạy 10+ Projects song song.

## 4. Điều phối: coordinator gom việc, chia việc, không tự code

- Bots là manager, không phải coder. Cô bảo bot spawn cloud agent thay vì tự làm, để có 1 coordinator và nhiều agent.
- Hệ phân cấp: cô nói với chief of staff, chief of staff nói với eng lead bot. Eng lead break task, delegate và supervise thay vì tự làm.
- Coordinator gom việc: 30 complaint hiệu năng thành 1 investigation vào root cause chung, không phải 30 agent sửa triệu chứng.
- Local coordinator, cloud subagents. 1 coordinator local spawn cloud subagent; /swarm 10+ agent fuzz PR trên autopilot.
- Projects là inner loop, Grok Bot là outer loop. Bug report ở Slack/Linear/X không nối vào inner loop; Grok Bot gom context bên ngoài rồi nhắn vào Projects.
- Vòng ngoài bắt đầu từ goal, không phải process: brain-dump cách mình làm việc bằng giọng nói, để bot restate lại, để bot phỏng vấn mình về phần còn thiếu, cho bot nguồn feedback riêng, rồi mới thêm trigger.

## 5. Vòng trong: /poteto-mode

Router /poteto-mode làm 4 việc:

1. Load principles: khoảng 2 chục skill một-nguyên-tắc, ví dụ Laziness Protocol (thay đổi nhỏ nhất giải quyết vấn đề) và Prove It Works (kiểm tra artifact thật).
2. Chọn playbook theo loại việc: bug report đi Bug fix, hành vi mới đi Feature, câu hỏi read-only đi Investigation. Việc lớn hoặc không khớp đi figure-it-out, tự thiết kế playbook.
3. Copy từng bước của playbook vào todo list. Bước bỏ qua vẫn hiển thị dạng skip: lý do, không gì biến mất lặng lẽ.
4. Gọi skill hỗ trợ khi cần.

23 playbooks có tên, trong đó: Investigation, Bug fix, Perf issue, Hillclimb, Runtime forensics, Feature, Refactoring, Prototype, Visual parity, Babysit, Shipping, Autonomous run, Orchestrate, Session pickup, Pause safely, Worktree cleanup, Opening a PR.

Trust boundary trong delegation: lead agent không tự viết code. Nó giao cho background subagent (poteto-agent), subagent này đọc cùng principles trước. Mỗi vai có thể dùng model khác. Điểm quan trọng: lead agent tự review diff, tự viết summary thay vì lặp lại claim của subagent, vì agent có thể tưởng mình xong trong khi chưa xong.

Lập kế hoạch qua code: prompt cô dùng nhiều nhất: "restate in your own words what you think my goals are and what the problem I'm trying to solve is." Plan bằng prototype và architecture arena: nhiều thiết kế ứng viên song song, thường từ model family khác nhau, cross-judge bằng model khác chấm, và scrap toàn bộ thiết kế nếu sai. Không review adversarially plan trừu tượng (agent bịa risk lý thuyết); plan commit cho project lớn thì xóa khi xong.

An toàn: tiến hành không hỏi với mọi thứ reversible. Dừng và hỏi trước one-way door: force-push shared branch, deploy, xóa data, nhắn customer.

## 6. Evidence contract: "done" không có nghĩa gì nếu không có bằng chứng chạy được

Đây là phần khớp nhất với evidence contract của team mình.

- Nêu finish condition trước: check cụ thể agent chạy được, không phải "làm tốt hơn". Reply tự tin mà không có evidence là red flag; "inconclusive" là câu trả lời trung thực, và inconclusive không phải pass.
- Match check với change: đổi CLI thì chạy command thật; đổi UI thì đi flow trong app đang chạy; migration thì replay saved input; perf thì so profile; storage thì đọc lại giá trị.
- Verify trên cùng bề mặt vấn đề xuất hiện. Bug báo ở UI thì reproduce ở UI, không phải "unit test pass". Agent phải reproduce bug trước khi sửa và reproduce lại sau khi sửa.
- Agent tự verify bằng cách chạy app thật: chạy code và đọc output thật, lái app (Playwright hoặc CDP qua CLI nhỏ), chụp screenshot và so sánh. Không có verification, mọi vòng lặp agent đều kết thúc bằng human kiểm tra; có verification, agent tự hill-climb: thử, đo, điều chỉnh.
- Verifier swarm: spawn /swarm agent "fuzz" mọi stack PR. Agent chấm change không bao giờ là agent viết change đó.
- Overnight contract: goal, finish condition, permissions, escape hatch, /loop, decision log. Plateau nghĩa là pivot, và finish condition không bao giờ lặng lẽ nới lỏng.
- PR nhỏ, có thứ tự, evidence trong mô tả. 5 PR hẹp hơn 1 PR béo. /poteto-mode babysit this pr xử lý blocker theo thứ tự (conflict, rồi review thread, rồi CI) và dừng ở merge-ready.
- Review comment được triage với nghi ngờ, không chấp nhận wholesale. /interrogate tách catch thật khỏi noise.
- Review của human đổi hình dạng: cô nói review thu hẹp thành xem artifact validation agent giao: video, screenshot, chart, kết quả formal verification. Agent tương tác app đang chạy qua CDP.

## 7. Merge và review sau khi land

- Khi đủ trust, agent merge PR của chính mình, cô review những gì đã land trong lúc cô vắng mặt hoặc ngủ. Một số project tự merge PR, cô review sau.
- Làm việc ngược từ "agent merge code của chính nó". Cô gọi đây là unlock lớn để đạt 2.000+ PR. Gỡ bỏ từng bước human theo mức trust tăng lên, biến mỗi bước thành agent.
- Pipeline auto-merge đã xác nhận đang chạy: sau mỗi release, một Cursor project vận hành toàn bộ build như user thật, mở fix PR khi thấy bug và tự merge.
- Review bằng sampling: cô không đọc mọi PR. Cô đọc mẫu, tìm pattern xấu, rồi sửa môi trường sinh ra chúng.
- Code owners PR được auto-approve; codebase và lint rule làm việc enforce.

## 8. Vòng lặp cải tiến: biến mọi sửa chữa thành luật

Thói quen mà clip TikTok nhấn mạnh và là phần team mình cần học nhất.

- Mỗi lần can thiệp sửa agent, nghĩ cách loại bỏ nó hoàn toàn. Thứ tự giá trị: (1) loại bỏ vấn đề bằng kiến trúc hoặc data structure tốt hơn; (2) biến thành lint rule hoặc test để CI bắt; (3) biến thành skill hoặc rule; (4) dựa vào human review, cô gắn nhãn "ngmi".
- Người làm vườn (gardener): có người lặng lẽ xem dòng PR chảy vào codebase, để ý mùi: helper isRecord thứ ba trong tuần, lint suppression lan như dây leo. "Every weed you pull becomes a rule, so it can't grow back."
- Khi viết lint rule chặn pattern xấu, quay lại dọn các ví dụ cũ để agent sau không copy chúng.
- Dr Eggbot daily friction routine: quét chat tìm correction và đề xuất skill, bot hoặc routine. Routine health check flag routine không dùng hoặc đắt (mặc định hàng tuần).
- /automate-me và /reflect, đào transcript cũ tìm correction mình cứ lặp lại. Trong nội bộ cô gọi là /lauren-mode, trong pstack là /poteto-mode.
- Evals là unit test cho skill: eval playbook dùng coordinator tạo rubric, spawn nhiều subagent trong thư mục riêng biệt, ngăn chúng phát hiện mình đang bị eval, hill-climb tới khi đạt target (ví dụ 10/10), dùng judge agent (có thể model khác) để giảm bias. Eval thay đổi skill trước khi tin nó.
- Đừng viết SKILL.md freehand. Đi qua authoring playbook để được validate. Skill chỉ chạy khi được invoke (cô set disable-model-invocation: true trên mọi skill pstack), không load sẵn như AGENTS.md khổng lồ.
- Ba đức tính khi dùng Grok Bot: Laziness, Impatience, Hubris. Hubris nghĩa là chịu trách nhiệm outcome dù tay mình không làm.
- Không để agent viết thay mình. Writing là thinking; viết rõ tạo ra instruction rõ.

## 9. Đối chiếu với team mình

File improvements/working-structure-redesign-20261121.md đã áp dụng Lauren Tan hẹp, và đã duyệt:

- Evidence contract: không report nào tính là done nếu thiếu evidence chạy được (exact test command + output/log, commit hash, run log có thời gian, screenshot/video cho task máy). "Done" trơ trụi bị trả lại không đọc. Generator không bao giờ tự chạy test của mình; chỉ evidence của runner khác mới tính cho change đã land. Khớp với mục 6 của cô.
- "Twice means a rule, and the rule lives in a lint, a test, or a template." Một dòng trong spawn-brief template. Khớp với mục 8 của cô.
- Coordinator duy nhất, repo-mediated, không peer-to-peer. Anthropic "Worse Together" (11/11/2026, MEASURED, 77 scenario): 1 coordinator thắng team peer-to-peer 4/4 môi trường, hơn 10-45 điểm. Khớp với coordinator của cô.
- Two-lane spawn cap. Khác cô ở quy mô: cô chạy 10+ Projects song song vì có cloud agent + token free; team mình cap 2 lane vì token và chất lượng đã đo được (parallelism hiệu quả chỉ 1,21-1,82x; subagent làm solve rate rơi 83% xuống 59% trong benchmark 2.124 run). Không copy số lane của cô.
- Cô auto-merge, mình acceptance gate. Đúng vị trí trên trust curve: cô mất 6 tháng xây verification mới dám auto-merge; team mình đang ở giai đoạn rung 1-3, gate là đúng, không nhảy bước.

## 10. Caveat: cái gì chưa kiểm chứng được

- Mọi con số PR và revert rate đều là self-reported của SpaceX/xAI, không có kiểm chứng độc lập. Talk kết thúc bằng pitch cho Grok Bot.
- Điều kiện của cô: setup đốt khoảng 15 tỉ token/ngày, plan thường không chịu nổi; tác giả clip trả lời comment rằng điều kiện là làm ở SpaceX và được cấp token Grok free. Phương pháp chuyển giao được, con số thì không.
- Claim viral "cô build team Grok Bot Chief of Staff, Managers, Workers" là HYPE. The Independent AI kiểm tra 8/11/2026: video 56 phút là talk thật của cô ở Cursor (khoảng tháng 8/2026) nhưng bị ghép intro/outro giả giọng khác và chữ "SpaceXAI"; talk thật không hề build team đó, nội dung là verification skills, feature maps, evals và CI guardrails.
- Không có nguồn nào đo riêng phần điều phối đa agent của cô bằng số liệu độc lập (ví dụ: bao nhiêu agent song song thì hiệu quả). Phần coordination ở trên là mô tả từ chính cô và người phân tích, không phải benchmark.
- Ngày talk: paulkuo.tw ghi 11/11/2026, video đăng 14/11/2026. Chưa khớp hẳn, có thể talk ngày 11/11 và video đăng ngày 14/11.

## 11. Nguồn chính

- Talk gốc: https://www.youtube.com/watch?v=O_zcc6Xl12g ("All Code Is Slop (Except Mine)", AI Engineer, 14/11/2026, 17:32)
- Clip TikTok: https://www.tiktok.com/@anythingai39/video/7710239842663288071 (@anythingai39, 20/11/2026, 222 giây)
- Phân tích trust pyramid: https://paulkuo.tw/en/articles/agent-mistakes-into-checks/ (Paul Kuo, 19/11/2026)
- Hướng dẫn thực hành: https://thoughtfulbits.ai/how-to-be-like-poteto
- Giải phẫu pstack: https://fairusss.vercel.app/writing/pstack-ai-agent-workflow
- Tóm tắt transcript talk: https://ainotes.us/summary/all-code-is-slop-except-mine-lauren-tan-spacexsi
- Kiểm chứng hype: https://theindependentai.com/hype-or-fact/spacexai-lauren-tan-grok-bot-team-repost (kiểm tra 8/11/2026)
- pstack upstream: https://github.com/cursor/plugins/tree/main/pstack
- X của cô: https://x.com/poteto ; GitHub: https://github.com/poteto
- Nội bộ: improvements/worker-w-crawl-clip-20261121.md, improvements/working-structure-redesign-20261121.md

## 12. Kết luận một câu

Workflow của cô không phải "review code giỏi hơn" mà là "xây môi trường để agent tự chứng minh việc của mình, coordinator chỉ gom việc và sửa môi trường, và mỗi lần sửa tay đều biến thành luật để lần sau không cần mình nữa".
