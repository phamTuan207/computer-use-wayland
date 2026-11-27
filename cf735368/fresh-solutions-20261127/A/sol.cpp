#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long n, m;
    if (!(cin >> n >> m)) return 0;
    long long per = n / m;
    long long rem = n % m;
    long long need = (m - rem) % m;
    cout << per << "\n" << rem << "\n" << need << "\n";
    return 0;
}
