#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n)) return 0;
    long long g = 0, sum = 0;
    for (int i = 0; i < n; i++) {
        long long a;
        cin >> a;
        g = std::gcd(g, a);
        sum += a;
    }
    cout << g << ' ' << sum / g << "\n";
    return 0;
}
