#include <iostream>

int main() {
    int n;
    std::cin >> n;

    bool hard = false;
    for (int i = 0, opinion; i < n; ++i) {
        std::cin >> opinion;
        hard |= opinion == 1;
    }

    std::cout << (hard ? "HARD" : "EASY") << '\n';
    return 0;
}
