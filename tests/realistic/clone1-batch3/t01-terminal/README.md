# t01-terminal: terminal emulator session

## Context

A web terminal emulator with a small virtual file system. The user
runs shell-like commands: help, echo, pwd, ls, cd, cat, history,
clear, and ArrowUp to recall the previous command. Unknown commands
print an error instead of crashing.

## Goal

Run a realistic terminal session: inspect the file system, move
between directories, read files, trigger errors for bad paths, recall
a command from history, clear the screen, and confirm the terminal
still works afterwards.

## Steps

1. Open the fixture page, check the prompt shows `/home/demo`.
2. Run `help`, check the command list appears.
3. Run `echo hello world`, check the text is printed.
4. Run `ls`, check readme.txt, notes.txt, and docs are listed.
5. Run `pwd`, check it prints `/home/demo`.
6. Run `cd docs`, check the prompt changes to `/home/demo/docs`.
7. Run `ls`, check guide.txt is listed.
8. Run `cat guide.txt`, check the file text appears.
9. Run `cat missing.txt`, check the "No such file" error.
10. Run `cd ..`, check the prompt returns to `/home/demo`.
11. Run `cd nowhere`, check the "No such directory" error.
12. Run `cat docs`, check the "is a directory" error.
13. Run `history`, check earlier commands are listed.
14. Press ArrowUp, check the input recalls `history`.
15. Press Enter, check the recalled command runs again.
16. Run `frobnicate`, check the "command not found" error.
17. Run `clear`, check the output area is empty.
18. Run `pwd`, check it still prints `/home/demo`.
19. Check the prompt is still `/home/demo`.
20. Run `echo final check`, check the text is printed.

## Pass conditions

- Every command above prints the expected output or error.
- The prompt follows the current directory after cd.
- ArrowUp recalls the last command.
- clear empties the output and the terminal keeps working.

## Fail conditions

- Any expected output, error, or prompt change is missing.
- ArrowUp recalls the wrong command.
- The terminal stops responding after an error or after clear.

## Notes

The file system is virtual and lives in the page. No real shell is
run and no data leaves the machine. The browser run is Playwright
Chromium; the same flow on Firefox or Zen is UNVERIFIED.
