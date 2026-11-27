#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    if (!(cin >> s)) return 0;
    long long freq[26] = {0};
    for (char c : s) freq[c - 'a']++;
    long long odd = 0;
    for (int i = 0; i < 26; i++) if (freq[i] % 2 == 1) odd++;
    cout << odd / 2 << "\n";
    return 0;
}
