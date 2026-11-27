#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    if (!(cin >> s)) return 0;
    for (char &c : s) {
        if (c == 'A') c = 'U';
        else if (c == 'T') c = 'A';
        else if (c == 'C') c = 'G';
        else if (c == 'G') c = 'C';
    }
    unordered_map<string, string> table = {
        {"UCU","Ser"},{"UCC","Ser"},{"UCA","Ser"},{"UCG","Ser"},
        {"ACU","Thr"},{"ACC","Thr"},{"ACA","Thr"},{"ACG","Thr"},
        {"CGU","Arg"},{"CGC","Arg"},{"CGA","Arg"},{"CGG","Arg"},
        {"GGU","Gly"},{"GGC","Gly"},{"GGA","Gly"},{"GGG","Gly"},
        {"CCU","Pro"},{"CCC","Pro"},{"CCA","Pro"},{"CCG","Pro"},
        {"UAU","Tyr"},{"UAC","Tyr"},
        {"CAU","His"},{"CAC","His"}
    };
    vector<string> out;
    for (size_t i = 0; i + 3 <= s.size(); i += 3) {
        string codon = s.substr(i, 3);
        auto it = table.find(codon);
        out.push_back(it == table.end() ? "Unk" : it->second);
    }
    for (size_t i = 0; i < out.size(); i++) {
        if (i) cout << '-';
        cout << out[i];
    }
    cout << "\n";
    return 0;
}
