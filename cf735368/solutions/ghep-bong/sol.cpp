#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    if (!(cin >> n >> q)) return 0;

    int yellow = 0, orange = 0;
    long long red = 0;
    vector<int> count(n + 1);

    for (int i = 1; i <= n; ++i) {
        int color;
        cin >> color;
        if (color == 1) {
            if (++yellow == 2) {
                yellow = 0;
                if (++orange == 2) {
                    orange = 0;
                    ++red;
                }
            }
        } else if (color == 2) {
            if (++orange == 2) {
                orange = 0;
                ++red;
            }
        } else {
            ++red;
        }
        count[i] = yellow + orange + red;
    }

    while (q--) {
        int i;
        cin >> i;
        cout << count[i] << (q ? ' ' : '\n');
    }
    return 0;
}
