#include <array>
#include <iostream>
#include <string>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int n, m;
        string p, q;
        cin >> n >> m >> p >> q;

        array<int, 26> count{};
        for (char c : p) ++count[c - 'a'];
        for (char c : q) --count[c - 'a'];

        bool possible = true;
        for (int i = 0; i < 26; ++i) {
            int expected = (i == ('s' - 'a') || i == ('i' - 'a') || i == ('x' - 'a')) ? 1 : 0;
            if (count[i] != expected) possible = false;
        }
        cout << (possible ? "YES" : "NO") << '\n';
    }
    return 0;
}
