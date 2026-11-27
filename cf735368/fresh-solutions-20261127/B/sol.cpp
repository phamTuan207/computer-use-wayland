#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n)) return 0;
    long long cnt = 0, pen = 0;
    for (int i = 0; i < n; i++) {
        long long x, y;
        cin >> x >> y;
        if (x > 0) {
            cnt++;
            pen += x + 20 * y;
        }
    }
    cout << cnt << ' ' << pen << "\n";
    return 0;
}
