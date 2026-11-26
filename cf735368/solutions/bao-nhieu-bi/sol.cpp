#include <iostream>
#include <vector>
using namespace std;

int main() {
    int m, n;
    if (!(cin >> m >> n)) return 0;

    vector<vector<long long>> a(m, vector<long long>(n));
    for (auto& row : a)
        for (auto& value : row)
            cin >> value;

    int i, j;
    cin >> i >> j;

    for (const auto& row : a) {
        for (int col = 0; col < n; ++col) {
            if (col) cout << ' ';
            cout << row[col];
        }
        cout << '\n';
    }
    cout << a[i - 1][j - 1] << '\n';
}
