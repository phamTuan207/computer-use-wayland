#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int &x : a) cin >> x;

    for (int pass = 0; pass < n - 1; ++pass) {
        for (int i = 0; i + 1 < n; ++i) {
            if (a[i] > a[i + 1]) swap(a[i], a[i + 1]);
        }
        for (int i = 0; i < n; ++i) {
            if (i) cout << ' ';
            cout << a[i];
        }
        cout << '\n';
    }
}
