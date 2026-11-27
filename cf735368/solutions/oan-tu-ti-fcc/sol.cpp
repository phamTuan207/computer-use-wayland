#include <bits/stdc++.h>
using namespace std;

int main(){
    int t;
    if(scanf("%d",&t)!=1) return 0;
    while(t--){
        int x,y,z;
        if(scanf("%d %d %d",&x,&y,&z)!=3) break;
        int n=x+y+z;
        int bestV=-1000000000;
        int bestA=0,bestB=0,bestC=n;
        for(int a=0;a<=n;a++){
            for(int b=0;b<=n-a;b++){
                int c=n-a-b;
                int G=min(x,b)+min(y,c)+min(z,a);
                int r=max(0,x-b);
                int s=max(0,y-c);
                int p=max(0,z-a);
                int A=max(0,a-z);
                int B=max(0,b-x);
                int C=max(0,c-y);
                int left=r+s+p;
                int draws=min(r,A)+min(s,B)+min(p,C);
                int V=-G+left-draws;
                if(V>bestV){
                    bestV=V;
                    bestA=a;
                    bestB=b;
                    bestC=c;
                }
            }
        }
        string out;
        out.append(bestA,'R');
        out.append(bestB,'S');
        out.append(bestC,'P');
        printf("%s\n", out.c_str());
    }
    return 0;
}
