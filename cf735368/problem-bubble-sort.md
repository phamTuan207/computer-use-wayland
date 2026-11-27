# Bubble Sort

- Category (Drive folder): Nhan biet
- Source: Plan B Drive extraction (folder "2. Cuoi khoa"), 27/11/2026. Codeforces contest 735368 access failed (anonymous session); contest membership of this problem is NOT confirmed (see task report).
- Test set: 60 files, Polygon inputs+answers (.a). Test files are NOT in this repo (VM scratch only); setter solution.c also held in scratch for reference-output generation, not shown to solver lanes.

## Statement (verbatim from Drive doc)

BUBBLE SORT
Giới hạn thời gian:10sGiới hạn bộ nhớ: 256MB

Bạn Tùng đang tham gia khóa học Coding Fundamentals của CLB NITC. Buổi học ngày hôm nay, Tùng đang học đến thuật toán sắp xếp nổi bọt. Vì tính tò mò của mình, Tùng muốn thấy rõ từng giai đoạn của quá trình sắp xếp. Hãy giúp Tùng thực hiện điều đó bằng cách in ra mảng sau mỗi lượt duyệt của thuật toán.

Hãy cùng nhắc lại cách thức hoạt động của thuật toán sắp xếp nổi bọt. Thuật toán bao gồm  lượt duyệt. Trong lượt duyệt thứ , chúng ta duyệt qua tất cả các phần tử trong mảng từ trái sang phải. Mỗi khi phát hiện hai phần tử liền kề không nằm đúng thứ tự (phần tử bên trái lớn hơn phần tử bên phải), chúng ta sẽ hoán đổi vị trí của chúng.

Input

Dòng đầu tiên chứa một số nguyên duy nhất N (1 ≤ N ≤ 2000), là độ dài của mảng. Dòng thứ hai chứa N số nguyên A0,A1,…,An-1, (0≤Ai<N) là mảng cần sắp xếp. Tất cả các
giá trị Ai đều khác nhau.

Output

Xuất ra đúng N−1 dòng. Dòng thứ i phải chứa N số nguyên, biểu thị mảng sau lần lặp thứ i của thuật toán sắp xếp nổi bọt (bubble sort).

Ví dụ


Input
Output
6
4 2 1 3 5 0


2 1 3 4 0 5 
1 2 3 0 4 5 
1 2 0 3 4 5 
1 0 2 3 4 5 
0 1 2 3 4 5 

## Formula recovery note (coordinator, 27/11/2026)

Recovered by PDF export: the two blanks in the recap paragraph are "n - 1"
(number of passes) and "i" (pass index). The statement is otherwise complete;
the recap-symbol loss was an extraction artifact, not a statement defect.
Note the array is a permutation of 0..N-1 (0 <= Ai < N, all distinct).




