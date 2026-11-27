#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int x, y, z;
        cin >> x >> y >> z;
        char move = z >= y ? 'R' : (x >= z ? 'S' : 'P');
        cout << string(x + y + z, move) << '\n';
    }
}
