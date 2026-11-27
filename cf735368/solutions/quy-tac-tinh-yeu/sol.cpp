#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (int &x : a) cin >> x;

    int m = 37 * n / 100;
    int max_score = -1;
    for (int i = 0; i < m; ++i) max_score = max(max_score, a[i]);

    for (int i = m; i < n; ++i) {
        if (a[i] > max_score) {
            cout << i + 1 << '\n';
            return 0;
        }
    }
    cout << n << '\n';
}
