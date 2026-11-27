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
        map<int, int> freq;
        for (int i = 0, id; i < n; ++i) {
            cin >> id;
            ++freq[id];
        }

        int leastId = -1, mostId = -1;
        int leastCount = INT_MAX, mostCount = 0;
        for (auto [id, count] : freq) {
            if (count < leastCount) {
                leastCount = count;
                leastId = id;
            }
            if (count > mostCount) {
                mostCount = count;
                mostId = id;
            }
        }
        cout << leastId << ' ' << mostId << '\n';
    }
}
