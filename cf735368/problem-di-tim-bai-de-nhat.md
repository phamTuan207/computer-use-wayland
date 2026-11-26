# Di tim bai de nhat

- Category (Drive folder): Nhan biet
- Source: Plan B Drive extraction (folder "2. Cuoi khoa"), 27/11/2026. Codeforces contest 735368 access failed (anonymous session); contest membership of this problem is NOT confirmed (see task report).
- Test set: 60 files, Polygon inputs+answers (.a). Test files are NOT in this repo (VM scratch only); setter solution.c also held in scratch for reference-output generation, not shown to solver lanes.

## Statement (verbatim from Drive doc)

ĐI TÌM BÀI DỄ NHẤT!
Giới hạn thời gian: 1s
Giới hạn bộ nhớ: 256MB

Khi chuẩn bị bài thi cuối kì, bạn Hiếu muốn bài đầu tiên phải là bài thật thật dễ để tất cả các bạn học viên tham gia đều có thể làm được. Vì nếu không làm được thì các bạn sẽ buồn. Thế nên bạn Hiếu đã chọn ra một vài bài và hỏi n bạn khác để xin ý kiến. Mỗi bạn sẽ trả lời rằng bài đấy dễ hay khó.

Nếu ít nhất 1 trong n người trả lời rằng bài đấy khó, bạn Hiếu sẽ thay đổi bài đấy ngay lập tức! Sau khi thu nhập đủ ý kiến, bạn Hiếu sẽ quyết định bài đó khó hay dễ. Hãy giúp bạn Hiếu nhé.

Input

Dòng đầu tiên chứa một số nguyên duy nhất n (1≤n≤100) - số lượng người được hỏi ý kiến.
Dòng thứ hai chứa n số nguyên, mỗi số nguyên có giá trị là 0 hoặc 1. Nếu số nguyên thứ i
là 0, thì người thứ i cho rằng bài toán này dễ; nếu là 1, thì người thứ i cho rằng bài toán này khó.

Output

In ra một từ: "EASY" nếu bài toán được coi là dễ theo tất cả các phản hồi, hoặc "HARD" nếu có ít nhất một người cho rằng bài toán đó khó.

Giải thích


Input
Output
3
0 0 1


HARD




Input
Output
1
0

EASY



Giải thích
Trong ví dụ thứ nhất, người thứ ba cho rằng đó là một vấn đề khó, vì vậy nó cần được thay thế.

Trong ví dụ thứ hai, vấn đề đó lại dễ đối với người duy nhất có liên quan, nên không cần phải thay thế nó.


