import sys, json
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession
from cleanup_full import list_tabs_full
with ZenSession() as z:
    new = z._wd("POST", f"/session/{z.session}/window/new", {"type": "tab"})
    sac = new["value"]["handle"]
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    tabs = list_tabs_full(z)
    print("VERIFY", len(tabs), "tabs (includes 1 sacrificial)")
    for t in tabs:
        print("TAB", json.dumps(t["title"], ensure_ascii=False), t["url"])
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    print("END on sacrificial")
