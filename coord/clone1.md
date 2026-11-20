# Task for clone1 - Puppeteer via BiDi

## Assignment from Muse (coordinator)
Research and write Puppeteer test code for controlling Firefox/Zen via WebDriver BiDi. Work on your own machine only, no SSH to the user's laptop.

## Tasks
1. Research Puppeteer connect via BiDi (Mozilla bug 1943416, W3C WebDriver BiDi spec).
2. Write complete Node.js test code: connect to ws://127.0.0.1:9222/session with protocol webDriverBiDi, list tabs, read DOM, click, type into input, time each action.
3. Test on your local Firefox/Zen if available, record results.
4. Research Mozilla firefox-mcp, write setup guide and comparison with Puppeteer.
5. Research WebExtension + native messaging as a bridge, write prototype if feasible.
6. Write comparison doc of all Firefox/Zen DOM control methods.

## Rules
- Full access. No fabrication. Stuck >15 min, report via repo immediately.
- NEVER push personal info to GitHub. No em/en dashes.
- Push results to this repo as you complete them.

## Deliverables
- coord/clone1.md (this file, update with progress)
- coord/clone1-puppeteer.md (results)
- tests/bidi-puppeteer/ (code)
