/* Y13g verify: argv-ignoring sleeper for the A4 live probe.
   Ignores every argv token and sleeps 180s, so a dummy process
   can carry an exact target cmdline (e.g. "python3 -m
   run_codex_y5") while staying alive. Built with:
   gcc -O2 -o sleeper sleeper.c
*/
#include <unistd.h>
int main(void) { sleep(180); return 0; }
