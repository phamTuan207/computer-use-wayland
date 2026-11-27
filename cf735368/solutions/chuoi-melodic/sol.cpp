#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        vector<int> a(n);
        for (int &x : a) cin >> x;

        int most_kept = 1;
        for (int p : a) {
            int kept = 0;
            for (int x : a) {
                if (x % p == 0) ++kept;
            }
            most_kept = max(most_kept, kept);
        }
        cout << n - most_kept << '\n';
    }
    return 0;
}
