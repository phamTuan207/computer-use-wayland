#include <bits/stdc++.h>
using namespace std;
const long long MOD = 1000000007LL;
// returns {F(n), F(n+1)} with F(0)=0, F(1)=1
pair<long long, long long> fib(long long n) {
    if (n == 0) return {0, 1};
    auto p = fib(n >> 1);
    long long a = p.first, b = p.second;
    long long c = a * ((2 * b % MOD - a + MOD) % MOD) % MOD;
    long long d = (a * a % MOD + b * b % MOD) % MOD;
    if ((n & 1) == 0) return {c, d};
    return {d, (c + d) % MOD};
}
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        long long a, b;
        cin >> a >> b;
        long long g = std::gcd(a, b);
        cout << fib(g).first % MOD << "\n";
    }
    return 0;
}
