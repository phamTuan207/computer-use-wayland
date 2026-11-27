#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    if (!(cin >> n >> k)) return 0;
    vector<int> a(n);
    for (int &x : a) cin >> x;

    auto bad = [k](int x, int y) { return abs(x - y) > k; };
    int total = 0;
    for (int i = 1; i < n; ++i) total += bad(a[i - 1], a[i]);

    unordered_map<int, int> change;
    for (int i = 0; i < n;) {
        int j = i + 1;
        while (j < n && a[j] == a[i]) ++j;

        if (i > 0) change[a[i]] -= bad(a[i - 1], a[i]);
        if (j < n) change[a[i]] -= bad(a[j - 1], a[j]);
        if (i > 0 && j < n) change[a[i]] += bad(a[i - 1], a[j]);
        i = j;
    }

    int answer = *min_element(a.begin(), a.end());
    int best = INT_MAX;
    for (const auto &[x, delta] : change) {
        int boredom = total + delta;
        if (boredom < best || (boredom == best && x < answer)) {
            best = boredom;
            answer = x;
        }
    }
    cout << answer << '\n';
}
