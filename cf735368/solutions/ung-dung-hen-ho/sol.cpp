#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long k;
    if (!(cin >> n >> k)) return 0;

    unordered_map<long long, long long> count;
    long long answer = 0;
    for (int i = 0; i < n; ++i) {
        long long a;
        cin >> a;
        long long r = a % k;
        long long need = (k - r) % k;
        answer += count[need];
        ++count[r];
    }

    cout << answer << '\n';
    return 0;
}
