#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    long long even = 0, odd = 0;
    for (int i = 0, x; i < n; ++i) {
        cin >> x;
        if (x % 2 == 0) ++even;
        else ++odd;
    }
    cout << even * (even - 1) / 2 + odd * (odd - 1) / 2 << '\n';
}
