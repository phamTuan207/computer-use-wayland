#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n)) return 0;
    vector<int> a(n + 1);
    for (int i = 1; i <= n; i++) cin >> a[i];
    const int INF = 1e9;
    vector<int> maxgap(n + 1, INF);
    for (int v = 1; v <= n; v++) {
        int prev = 0, mg = 0;
        for (int i = 1; i <= n; i++) {
            if (a[i] == v) {
                mg = max(mg, i - prev);
                prev = i;
            }
        }
        mg = max(mg, (n + 1) - prev);
        maxgap[v] = mg;
    }
    for (int k = 1; k <= n; k++) {
        int ans = -1;
        for (int v = 1; v <= n; v++) {
            if (maxgap[v] <= k) { ans = v; break; }
        }
        if (k > 1) cout << ' ';
        cout << ans;
    }
    cout << "\n";
    return 0;
}
