#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int N;
    long long X;
    if (!(cin >> N >> X)) return 0;
    vector<long long> a(N);
    long long mx = 0;
    for (int i = 0; i < N; i++) {
        cin >> a[i];
        mx = max(mx, a[i]);
    }
    long long ops = 0;
    for (long long v : a) {
        long long diff = mx - v;
        if (diff % X != 0) {
            cout << -1 << "\n";
            return 0;
        }
        ops += diff / X;
    }
    cout << ops << "\n";
    return 0;
}
