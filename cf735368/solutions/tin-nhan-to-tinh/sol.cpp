#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    if (!(cin >> s)) return 0;

    int bestStart = 0, bestLength = 1;
    for (int i = 0; i < static_cast<int>(s.size()); ) {
        int j = i + 1;
        while (j < static_cast<int>(s.size()) && s[j] == s[i]) ++j;
        if (j - i > bestLength) {
            bestStart = i;
            bestLength = j - i;
        }
        i = j;
    }

    cout << bestLength << '\n' << s.substr(bestStart, bestLength) << '\n';
}
