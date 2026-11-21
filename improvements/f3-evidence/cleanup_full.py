"""Full cleanup redo (owner 22:49): close the 39 resurrected fixture tabs
+ the 15 definitely-unused tabs (13 about:blank, httpbin, BiDi fixture
40301). Keep the 13 real tabs incl. Free Claude Code Admin 127.0.0.1:8082.

Safety: sacrificial tab opened FIRST; the sacrificial handle is EXCLUDED
from the doomed set (cleanup2.py would have closed its own sacrificial
tab: a fresh about:blank tab matches title "" + about:blank). Session
ends focused on the sacrificial tab.
"""
import json, sys, time
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession

FIXTURE_TITLES = {
    "Browser IDE & Debugger", "Cloud Notes Sync App",
    "Browser DevTools Simulator", "File Manager Web Portal",
    "Video Conference Client", "Cloud Spreadsheet Studio",
    "Corporate Webmail Client", "Photo Studio Pro",
    "Calibration Grid E2",
}
BIDI_FIXTURE_URL = "http://127.0.0.1:40301/fixture"
HTTPBIN_URL = "https://httpbin.org/forms/post"

def is_doomed(tab):
    title, url = tab["title"], tab["url"]
    if title == "New Tab":
        return True
    if title in FIXTURE_TITLES:
        return True
    if url.startswith("http://127.0.0.1:876") or url.startswith("http://127.0.0.1:444"):
        return True
    if url.startswith("http://localhost:876") or url.startswith("http://localhost:444"):
        return True
    if url.startswith("file://"):
        return True
    if title == "" and url == "about:blank":
        return True
    if title == "" and url == HTTPBIN_URL:
        return True
    if title == "BiDi fixture" and url == BIDI_FIXTURE_URL:
        return True
    return False

def list_tabs_full(z):
    handles = z._wd("GET", f"/session/{z.session}/window/handles")["value"]
    current = z._wd("GET", f"/session/{z.session}/window")["value"]
    tabs = []
    for handle in handles:
        try:
            z._wd("POST", f"/session/{z.session}/window", {"handle": handle})
        except Exception as exc:
            tabs.append({"handle": handle, "title": f"<switch failed: {exc}>", "url": ""})
            continue
        try:
            title = z._wd("GET", f"/session/{z.session}/title")["value"]
        except Exception as exc:
            title = f"<title failed: {exc}>"
        try:
            url = z._wd("GET", f"/session/{z.session}/url")["value"]
        except Exception as exc:
            url = f"<url failed: {exc}>"
        tabs.append({"handle": handle, "title": title, "url": url})
    z._wd("POST", f"/session/{z.session}/window", {"handle": current})
    return tabs

def main():
    t0 = time.time()
    result = {"before": [], "closed": [], "after": [], "errors": []}
    with ZenSession() as z:
        new = z._wd("POST", f"/session/{z.session}/window/new", {"type": "tab"})
        sac = new["value"]["handle"]
        z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
        print("SACRIFICIAL opened first", sac, flush=True)
        tabs = list_tabs_full(z)
        result["before"] = [{"title": t["title"], "url": t["url"]} for t in tabs]
        print("BEFORE", len(tabs), "tabs", flush=True)
        doomed = [t for t in tabs if t["handle"] != sac and is_doomed(t)]
        print("DOOMED", len(doomed), json.dumps([t["title"] for t in doomed], ensure_ascii=False), flush=True)
        for tab in doomed:
            try:
                z._wd("POST", f"/session/{z.session}/window", {"handle": tab["handle"]})
                z._wd("DELETE", f"/session/{z.session}/window", {})
                result["closed"].append(tab["title"] + " | " + tab["url"])
                print("CLOSED", tab["title"], tab["url"], flush=True)
            except Exception as exc:
                result["errors"].append(f"{tab['title']}: {exc}")
                print("ERROR closing", tab["title"], exc, flush=True)
        z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
        after = list_tabs_full(z)
        result["after"] = [{"title": t["title"], "url": t["url"]} for t in after]
        print("AFTER", len(after), "tabs", flush=True)
        print("AFTER-TITLES", json.dumps([t["title"] for t in after], ensure_ascii=False), flush=True)
        z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
        print("END on sacrificial tab", flush=True)
    with open("/tmp/zen_tab_cleanup/result_full.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"DONE closed {len(result['closed'])} errors {len(result['errors'])} elapsed {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
