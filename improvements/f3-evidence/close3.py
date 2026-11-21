import sys, json
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession
from cleanup_full import list_tabs_full
with ZenSession() as z:
    new = z._wd("POST", f"/session/{z.session}/window/new", {"type": "tab"})
    sac = new["value"]["handle"]
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    tabs = list_tabs_full(z)
    print("BEFORE", len(tabs))
    doomed = [t for t in tabs if t["handle"] != sac and ((t["title"] == "Example Domain" and t["url"] == "https://example.com/") or (t["title"] == "" and t["url"] == "about:blank"))]
    print("DOOMED", len(doomed), [(t["title"], t["url"]) for t in doomed])
    for tab in doomed:
        z._wd("POST", f"/session/{z.session}/window", {"handle": tab["handle"]})
        z._wd("DELETE", f"/session/{z.session}/window", {})
        print("CLOSED", tab["title"], tab["url"])
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    after = list_tabs_full(z)
    print("AFTER", len(after), [t["title"] for t in after])
    print("END on sacrificial")
