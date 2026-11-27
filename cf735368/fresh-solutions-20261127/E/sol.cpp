#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long N;
    if (!(cin >> N)) return 0;
    long long best = 1;
    for (int k = 0; k < 61; k++) {
        __int128 p2 = (__int128)1 << k;
        if (p2 <= N) best = max(best, (long long)p2);
        __int128 v = 3 * p2;
        if (v <= N) best = max(best, (long long)v);
    }
    cout << (N - best) << "\n";
    return 0;
}
