# Keo Con

- Category (Drive folder): Nhan biet
- Source: Plan B Drive extraction (folder "2. Cuoi khoa"), 27/11/2026. Codeforces contest 735368 access failed (anonymous session); contest membership of this problem is NOT confirmed (see task report).
- Test set: 60 files, Polygon inputs+answers (.a). Test files are NOT in this repo (VM scratch only); setter solution.c also held in scratch for reference-output generation, not shown to solver lanes.

## Statement (verbatim from Drive doc)

KẸO CON
Giới hạn thời gian: 5s
Giới hạn bộ nhớ: 256MB

Các bạn học viên tham gia khóa học Coding Fundamentals của CLB NITC đã đi học và làm bài tập đầy đủ. Thế nên vào buổi cuối, các bạn đứng lớp quyết định tặng mỗi bạn một số kẹo nhất định dựa vào mức độ tình yêu của các bạn dành cho NITC. Để dễ phân phát, các bạn học viên ngồi thành một hàng và được đánh số từ 0 đến N-1 từ trái sang phải. Bạn được đánh số i sẽ nhận được Ci  số kẹo (0 ≤i <N). 

Đang phát kẹo giữa chừng thì bạn Đoan quên mất mình đã phát bao nhiêu cây kẹo. Hãy giúp bạn Đoan tính tổng số kẹo đã phát từ vị trí A đến vị trí B (bao gồm cả A và B) nhé!

Input

Dòng đầu tiên chứa một số nguyên N (1 ≤ N ≤ 1000000) – số lượng học viên. Dòng thứ hai chứa N số nguyên C0, C1, …, CN-1 (1 ≤ Ci   ≤ 1000), trong đó số thứ i cho biết bạn học viên thứ i đang giữ Ci viên kẹo. Dòng thứ ba và cũng là dòng cuối cùng chứa hai số nguyên A và B (0 ≤ A ≤ B < N) – các giới hạn của khoảng trong truy vấn của bạn Đoan.

Output

Xuất ra một số duy nhất – tổng số kẹo mà các em nhỏ đang giữ giữa vị trí A và B
(bao gồm cả hai vị trí này), tức là CA+CA+1+…+CB.

Ví dụ


Input
Output
5
4 5 9 10 2
1 3


24




Input
Output
2
2 3
1 1


3




Input
Output
7
1 2 3 3 3 1 3
0 6


16



Giải thích

Trong test case 1, vị trí A là 1 và vị trí B là 3. Nên tổng số kẹo là 5 + 9 + 10 = 24

