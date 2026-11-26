#include <algorithm>
#include <iomanip>
#include <iostream>

int main() {
    int n;
    if (!(std::cin >> n) || n < 1 || n > 10) return 0;

    double sum = 0.0, highest = 0.0;
    int passed = 0;
    for (int i = 0; i < n; ++i) {
        double score;
        std::cin >> score;
        sum += score;
        highest = std::max(highest, score);
        if (score >= 5.0) ++passed;
    }

    std::cout << std::fixed << std::setprecision(1)
              << sum / n << '\n' << highest << '\n' << passed << '\n';
}
