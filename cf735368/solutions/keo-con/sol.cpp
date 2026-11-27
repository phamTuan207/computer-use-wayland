#include <iostream>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    if (!(std::cin >> n)) return 0;

    std::vector<int> candies(n);
    for (int &count : candies) std::cin >> count;

    int a, b;
    std::cin >> a >> b;

    long long total = 0;
    for (int i = a; i <= b; ++i) total += candies[i];

    std::cout << total << '\n';
}
