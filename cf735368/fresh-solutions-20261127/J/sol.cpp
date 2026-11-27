#include <bits/stdc++.h>
using namespace std;
using i128 = __int128_t;
using i64 = long long;

i64 mulmod(i64 a, i64 b, i64 mod) {
    return (i64)((i128)a * b % mod);
}
i64 powmod(i64 a, i64 d, i64 mod) {
    i64 r = 1 % mod;
    a %= mod;
    while (d > 0) {
        if (d & 1) r = mulmod(r, a, mod);
        a = mulmod(a, a, mod);
        d >>= 1;
    }
    return r;
}
i64 egcd(i64 a, i64 b, i64 &x, i64 &y) {
    if (b == 0) { x = 1; y = 0; return a; }
    i64 x1, y1;
    i64 g = egcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - y1 * (a / b);
    return g;
}
i64 modinv(i64 a, i64 mod) {
    i64 x, y;
    egcd(a, mod, x, y);
    x %= mod;
    if (x < 0) x += mod;
    return x;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    const int LIM = 1000000;
    vector<int> primes;
    vector<bool> is_composite(LIM + 1, false);
    for (int i = 2; i <= LIM; i++) {
        if (!is_composite[i]) {
            primes.push_back(i);
            if ((long long)i * i <= LIM)
                for (long long j = 1LL * i * i; j <= LIM; j += i) is_composite[(int)j] = true;
        }
    }
    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        i64 n, e, c;
        cin >> n >> e >> c;
        i64 p = -1;
        for (int pr : primes) {
            if ((i64)pr * pr > n) break;
            if (n % pr == 0) { p = pr; break; }
        }
        i64 q = n / p;
        i64 phi = (p - 1) * (q - 1);
        i64 d = modinv(e, phi);
        i64 m = powmod(c, d, n);
        cout << m << "\n";
    }
    return 0;
}
