#!/usr/bin/env python3
"""Live Zen runner: agy-q2 test-01..10 (Worker Y4, 21/11/2026).

Runs tests/realistic/agy-q2/test-01..10 against the LIVE Zen on the
laptop via geckodriver --connect-existing (Marionette 2828), reusing
the proven driver from tests/realistic/run_live.py (Worker P) and the
helpers from tests/realistic/run_agyq.py (Worker R) / run_fcck.py
(Worker U):
- explicit tab switch after window/new, 1s settle after navigation,
  0.5s after switch, no maximize, one WebDriver session per test,
  always deleted in a finally block,
- end states verified by reading the DOM directly. The fixtures'
  window.__agyVerify() hooks are NEVER used as oracles.
- selects set via JS value + change event; date inputs via JS value +
  change (Marionette keystrokes into a Firefox date input are
  locale-dependent); everything else driven through real Marionette
  clicks / keystrokes.
- ONE shared test tab for the whole suite (bootstrap_tab): tabs
  created by window/new intermittently open with body
  visibility:hidden (21/11 17:52-17:57, self-cleared ~17:59), which
  makes Marionette refuse every click/type. A pre-existing tab
  navigated with goto stays visible, so all tests share one reused
  tab; each test still gets a fresh WebDriver session, clears
  storage, and reloads the fixture. The tab is returned to
  about:blank at the end.

Each test opens its fixture in a fresh tab, clears localStorage /
sessionStorage, reloads, then follows the spec step by step with
per-step wall timing. A step that raises aborts that test; a failed
CHECK is recorded and the test continues. Per-test JSON summary lines
go to stdout; per-step JSONL goes to LIVE_LOG.

Usage (on the laptop, from /tmp/worker-y4-server):
  LIVE_SERVER_ROOT=/tmp/worker-y4-server LIVE_SERVER_PORT=8768 \\
  LIVE_LOG=/tmp/worker-y4-live.jsonl WD_PORT=4448 \\
  python3 run_agyq2.py all
  python3 run_agyq2.py q01 q02
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import (  # noqa: E402
    SERVER_PORT, WD, Runner,
    start_server as _rl_start_server,
)


def start_server():
    """Reuse a server already listening on our port (e.g. the persistent
    python3 -m http.server started for probing), else start a fresh one.

    run_live.start_server only reuses when the clone1 fixture answers,
    so on this port it would try to bind 8768 twice and die with
    EADDRINUSE. Probe our own fixture first.
    """
    probe = (f"http://127.0.0.1:{SERVER_PORT}/agy-q2/fixtures/"
             "test-01-whiteboard.html")
    try:
        with urllib.request.urlopen(probe, timeout=2) as resp:
            if resp.status == 200:
                print(f"reusing live server at http://127.0.0.1:{SERVER_PORT}",
                      flush=True)
                return None, f"http://127.0.0.1:{SERVER_PORT}"
    except Exception:
        pass
    try:
        return _rl_start_server()
    except OSError as exc:
        raise RuntimeError(
            f"could not start or reuse a server on port {SERVER_PORT} "
            f"(is a stale server holding the port with the wrong root?): {exc}"
        )


def select_option(d, css, value):
    """Set a <select> value and fire change."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def select_by_text(d, css, text):
    """Select the <option> whose visible text matches, by its value."""
    return d.eval(
        "const sel=document.querySelector(arguments[0]);"
        "const opt=[...sel.options].find(o=>o.textContent.trim()===arguments[1]);"
        "if(!opt) return 'NOT-FOUND'; sel.value=opt.value;"
        "sel.dispatchEvent(new Event('change',{bubbles:true}));"
        "return sel.value;", [css, text])


def clear_input(d, css):
    """Clear an input and fire input so filters re-render."""
    return d.eval(
        "const el=document.querySelector(arguments[0]); el.value='';"
        "el.dispatchEvent(new Event('input',{bubbles:true})); return 'cleared';",
        [css])


def set_date(d, css, value):
    """Set a date input value and fire change (deterministic)."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def txt(d, css):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? el.textContent : null;", [css])


def count(d, css):
    return d.eval(
        "return document.querySelectorAll(arguments[0]).length;", [css])


def has_class(d, css, cls):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? el.classList.contains(arguments[1]) : false;",
        [css, cls])


def is_checked(d, css):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? !!el.checked : false;", [css])


def norm(s):
    """Collapse all whitespace so multi-line renders compare sanely."""
    return " ".join((s or "").split())


def ensure_visible(d, r, label="test tab"):
    """Body must be visible before Marionette can click/type.

    Window/new tabs intermittently open with body visibility:hidden
    (observed 17:52-17:57 on 21/11: every new tab hidden, all 22
    existing tabs visible, window.focus() did not help; the state
    cleared by itself ~17:59 after a real click in a reused tab).
    Recovery: switch away and back, window.focus, wait, re-check.
    Returns True if visible, False if still hidden after recovery.
    """
    if d.visible("body"):
        return True
    print(f"[{r.test}] body hidden on {label}, attempting recovery",
          flush=True)
    # switch away to a different tab and back to the test tab
    try:
        test_tab = getattr(r, "tab", None)
        away = None
        for h in d.handles():
            if h != test_tab:
                try:
                    d.switch(h)
                    away = h
                    break
                except Exception:
                    continue
        if away is not None and test_tab is not None:
            d.switch(test_tab)
            d.eval("window.focus(); return 'focused';")
            time.sleep(2)
    except Exception as exc:
        print(f"[{r.test}] recovery switch failed: {exc}", flush=True)
    return d.visible("body")


def open_fixture(r, d, fname):
    url = r.base + "/agy-q2/fixtures/" + fname
    # Shared visible test tab (r.tab), NOT window/new: new tabs
    # intermittently open with body visibility:hidden (see
    # ensure_visible). The tab is shared across tests; each test
    # clears storage and reloads, so state stays isolated.
    d.switch(r.tab)
    r.step("open fixture", "goto", lambda: d.goto(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear(); sessionStorage.clear();"
                           "return 'cleared';"), d.refresh()))
    if not ensure_visible(d, r):
        raise RuntimeError(
            "test tab body still hidden after recovery; cannot drive "
            "(Marionette refuses clicks on visibility:hidden content)")
    r.step("check body visible", "check", lambda: d.visible("body"))
    r.check("body renders visible (no hidden-body incident)",
            d.visible("body"), "visible")


# ---------------- q01 whiteboard ----------------

def run_q01(r, d):
    open_fixture(r, d, "test-01-whiteboard.html")
    r.check("canvas visible", d.visible("#whiteboard-canvas"), "visible")
    r.check("objects count starts 0", txt(d, "#objects-count") == "0",
            txt(d, "#objects-count"))
    r.step("type board title", "type",
           lambda: d.type_text("#input-board-title", "Architecture Sprint 2026"))
    r.step("click rect tool", "click", lambda: d.click("#tool-rect"))
    r.step("click blue swatch", "click", lambda: d.click("#color-blue"))
    r.step("set coords 100,80,180,120", "type", lambda: (
        d.type_text("#input-coord-x", "100"),
        d.type_text("#input-coord-y", "80"),
        d.type_text("#input-coord-w", "180"),
        d.type_text("#input-coord-h", "120")))
    r.step("place shape", "click", lambda: d.click("#btn-add-shape"))
    r.check("1 object after rect", txt(d, "#objects-count") == "1",
            txt(d, "#objects-count"))
    rows = r.step("read objects table", "text",
                  lambda: txt(d, "#object-list-body"))
    r.check("row 1 is blue rect", "rect" in norm(rows).lower()
            and "Blue" in rows, norm(rows))
    r.step("click circle tool", "click", lambda: d.click("#tool-circle"))
    r.step("click green swatch", "click", lambda: d.click("#color-green"))
    r.step("set coords 400,150,r50", "type", lambda: (
        d.type_text("#input-coord-x", "400"),
        d.type_text("#input-coord-y", "150"),
        d.type_text("#input-coord-w", "50")))
    r.step("place circle", "click", lambda: d.click("#btn-add-shape"))
    r.check("2 objects after circle", txt(d, "#objects-count") == "2",
            txt(d, "#objects-count"))
    rows = r.step("read objects table 2", "text",
                  lambda: txt(d, "#object-list-body"))
    r.check("row 2 is green circle r=50", "circle" in norm(rows).lower()
            and "Green" in rows and "r=50" in rows, norm(rows))
    r.step("click text tool", "click", lambda: d.click("#tool-text"))
    r.step("click blue swatch again", "click", lambda: d.click("#color-blue"))
    r.step("type API Gateway", "type",
           lambda: d.type_text("#input-canvas-text", "API Gateway"))
    r.step("set coords 120,130", "type", lambda: (
        d.type_text("#input-coord-x", "120"),
        d.type_text("#input-coord-y", "130")))
    r.step("place text", "click", lambda: d.click("#btn-add-shape"))
    r.check("3 objects after text", txt(d, "#objects-count") == "3",
            txt(d, "#objects-count"))
    r.step("click line tool", "click", lambda: d.click("#tool-line"))
    r.step("click red swatch", "click", lambda: d.click("#color-red"))
    r.step("place accidental line", "click", lambda: d.click("#btn-add-shape"))
    r.check("4 objects after accidental line",
            txt(d, "#objects-count") == "4", txt(d, "#objects-count"))
    r.step("click undo", "click", lambda: d.click("#btn-undo"))
    r.check("back to 3 objects after undo",
            txt(d, "#objects-count") == "3", txt(d, "#objects-count"))
    rows = r.step("read objects table 3", "text",
                  lambda: txt(d, "#object-list-body"))
    r.check("red line gone after undo", "Red" not in rows, norm(rows))
    r.step("click rect tool again", "click", lambda: d.click("#tool-rect"))
    r.step("click yellow swatch", "click", lambda: d.click("#color-yellow"))
    r.step("set coords 400,300,200,100", "type", lambda: (
        d.type_text("#input-coord-x", "400"),
        d.type_text("#input-coord-y", "300"),
        d.type_text("#input-coord-w", "200"),
        d.type_text("#input-coord-h", "100")))
    r.step("place yellow rect", "click", lambda: d.click("#btn-add-shape"))
    r.step("click text tool again", "click", lambda: d.click("#tool-text"))
    r.step("type Database Cluster", "type",
           lambda: d.type_text("#input-canvas-text", "Database Cluster"))
    r.step("set coords 420,340", "type", lambda: (
        d.type_text("#input-coord-x", "420"),
        d.type_text("#input-coord-y", "340")))
    r.step("place text 2", "click", lambda: d.click("#btn-add-shape"))
    r.check("5 objects total", txt(d, "#objects-count") == "5",
            txt(d, "#objects-count"))
    r.step("click save board", "click", lambda: d.click("#btn-save-board"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#status-banner"))
    r.check("save banner confirms 5 objects",
            "Board 'Architecture Sprint 2026' saved with 5 objects" in norm(banner),
            norm(banner))


# ---------------- q02 recipe app ----------------

def run_q02(r, d):
    open_fixture(r, d, "test-02-recipe-app.html")
    r.check("catalog starts 12", txt(d, "#catalog-count") == "12",
            txt(d, "#catalog-count"))
    r.check("planner starts 0", txt(d, "#planner-count") == "0",
            txt(d, "#planner-count"))
    r.step("type plan name", "type",
           lambda: d.type_text("#input-plan-name", "Weekly Health Plan"))
    r.step("select category dinner", "select",
           lambda: select_option(d, "#filter-category", "dinner"))
    r.check("catalog drops to 4", txt(d, "#catalog-count") == "4",
            txt(d, "#catalog-count"))
    r.step("check gluten-free", "click", lambda: d.click("#filter-diet-gf"))
    r.check("catalog narrows to 2", txt(d, "#catalog-count") == "2",
            txt(d, "#catalog-count"))
    r.step("view salmon recipe", "click", lambda: d.click("#btn-view-salmon"))
    r.check("modal opens",
            d.eval("return document.getElementById('recipe-modal')"
                   ".style.display;") == "flex",
            d.eval("return document.getElementById('recipe-modal')"
                   ".style.display;"))
    r.check("servings start 2", txt(d, "#servings-count") == "2",
            txt(d, "#servings-count"))
    r.step("inc servings to 3", "click", lambda: d.click("#btn-inc-servings"))
    r.step("inc servings to 4", "click", lambda: d.click("#btn-inc-servings"))
    r.check("servings now 4", txt(d, "#servings-count") == "4",
            txt(d, "#servings-count"))
    ing = r.step("read modal ingredients", "text",
                 lambda: txt(d, "#modal-ingredients-list"))
    r.check("ingredients scale to 4 fillets", "4 fillets" in norm(ing),
            norm(ing))
    r.check("ingredients scale to 4 tbsp olive oil",
            "4 tbsp olive oil" in norm(ing), norm(ing))
    r.step("add salmon to plan", "click",
           lambda: d.click("#btn-modal-add-plan"))
    r.check("planner count 1", txt(d, "#planner-count") == "1",
            txt(d, "#planner-count"))
    r.step("reset category to all", "select",
           lambda: select_option(d, "#filter-category", "all"))
    r.step("uncheck gluten-free", "click", lambda: d.click("#filter-diet-gf"))
    r.step("search Pancakes", "type",
           lambda: d.type_text("#recipe-search", "Pancakes"))
    r.check("only pancakes visible", count(d, ".recipe-card") == 1,
            count(d, ".recipe-card"))
    r.check("visible card is pancakes",
            "Fluffy Banana Oat Pancakes" in norm(txt(d, "#recipe-grid")),
            norm(txt(d, "#recipe-grid")))
    r.step("add pancakes to plan", "click",
           lambda: d.click("#btn-plan-pancakes"))
    r.step("search Smoothie", "type",
           lambda: d.type_text("#recipe-search", "Smoothie"))
    r.step("add smoothie to plan", "click",
           lambda: d.click("#btn-plan-smoothie"))
    r.step("search Tacos", "type",
           lambda: d.type_text("#recipe-search", "Tacos"))
    r.step("add tacos by mistake", "click",
           lambda: d.click("#btn-plan-tacos"))
    r.check("planner count 4 after mistake",
            txt(d, "#planner-count") == "4", txt(d, "#planner-count"))
    r.step("remove tacos from planner", "click",
           lambda: d.click("#btn-remove-plan-tacos"))
    r.check("planner back to 3", txt(d, "#planner-count") == "3",
            txt(d, "#planner-count"))
    r.step("generate shopping list", "click",
           lambda: d.click("#btn-generate-shopping-list"))
    n_items = r.step("count shopping items", "count",
                     lambda: count(d, "#shopping-list-output .shopping-item"))
    r.check("shopping list has at least 5 items", n_items >= 5, n_items)
    r.step("save meal plan", "click", lambda: d.click("#btn-save-plan"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#recipe-status-banner"))
    r.check("save banner confirms plan",
            "Meal plan 'Weekly Health Plan' saved with 3 recipes and shopping list"
            in norm(banner), norm(banner))


# ---------------- q03 habit tracker ----------------

def run_q03(r, d):
    open_fixture(r, d, "test-03-habit-tracker.html")
    r.check("4 habits initially", txt(d, "#stat-total-habits") == "4",
            txt(d, "#stat-total-habits"))
    r.check("adherence starts 57%", txt(d, "#stat-adherence-rate") == "57%",
            txt(d, "#stat-adherence-rate"))
    r.step("type habit name", "type",
           lambda: d.type_text("#input-habit-name", "Deep Work Sprint"))
    r.step("select category Productivity", "select",
           lambda: select_option(d, "#select-habit-category", "Productivity"))
    r.step("set target days 5", "type",
           lambda: d.type_text("#input-target-days", "5"))
    r.step("click add habit", "click", lambda: d.click("#btn-add-habit"))
    r.check("5 rows after add", count(d, "#habits-tbody tr") == 5,
            count(d, "#habits-tbody tr"))
    for day in ("mon", "tue", "wed", "thu", "fri"):
        r.step(f"check deep work {day}", "click",
               lambda day=day: d.click(f"#check-habit-deep-work-sprint-{day}"))
    r.check("deep work streak 5d",
            txt(d, "#streak-deep-work-sprint") == "5d",
            txt(d, "#streak-deep-work-sprint"))
    r.step("type accidental habit", "type",
           lambda: d.type_text("#input-habit-name", "Social Media Browsing"))
    r.step("select category Mindset", "select",
           lambda: select_option(d, "#select-habit-category", "Mindset"))
    r.step("add accidental habit", "click", lambda: d.click("#btn-add-habit"))
    r.check("6 rows after accidental add",
            count(d, "#habits-tbody tr") == 6, count(d, "#habits-tbody tr"))
    r.step("delete accidental habit", "click",
           lambda: d.click("#btn-del-habit-social-media-browsing"))
    r.check("back to 5 rows", count(d, "#habits-tbody tr") == 5,
            count(d, "#habits-tbody tr"))
    r.check("accidental habit gone",
            "Social Media Browsing" not in norm(txt(d, "#habits-tbody")),
            norm(txt(d, "#habits-tbody")))
    r.step("check water sat", "click",
           lambda: d.click("#check-habit-water-sat"))
    r.step("check water sun", "click",
           lambda: d.click("#check-habit-water-sun"))
    r.check("water streak 7d", txt(d, "#streak-water") == "7d",
            txt(d, "#streak-water"))
    r.step("filter Productivity", "select",
           lambda: select_option(d, "#filter-category", "Productivity"))
    r.check("filtered view shows 1 row",
            count(d, "#habits-tbody tr") == 1, count(d, "#habits-tbody tr"))
    r.check("filtered row is deep work",
            "Deep Work Sprint" in norm(txt(d, "#habits-tbody")),
            norm(txt(d, "#habits-tbody")))
    r.step("reset filter to all", "select",
           lambda: select_option(d, "#filter-category", "all"))
    r.check("all 5 habits visible", count(d, "#habits-tbody tr") == 5,
            count(d, "#habits-tbody tr"))
    r.check("adherence now 66%", txt(d, "#stat-adherence-rate") == "66%",
            txt(d, "#stat-adherence-rate"))
    r.step("save tracking log", "click", lambda: d.click("#btn-save-habits"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#habit-status-banner"))
    r.check("save banner confirms 5 habits 23 checks",
            "Habit log saved successfully for 5 habits (23 completed checks)"
            in norm(banner), norm(banner))


# ---------------- q04 budget tracker ----------------

def add_expense(r, d, desc, amount, category, date):
    r.step(f"type desc {desc}", "type",
           lambda: d.type_text("#input-expense-desc", desc))
    r.step(f"type amount {amount}", "type",
           lambda: d.type_text("#input-expense-amount", amount))
    r.step(f"select category {category}", "select",
           lambda: select_option(d, "#select-expense-category", category))
    r.step(f"set date {date}", "date",
           lambda: set_date(d, "#input-expense-date", date))
    r.step("click add expense", "click", lambda: d.click("#btn-add-expense"))


def run_q04(r, d):
    open_fixture(r, d, "test-04-budget-tracker.html")
    r.check("4 initial rows", count(d, "#expenses-tbody tr") == 4,
            count(d, "#expenses-tbody tr"))
    r.check("total spent starts $1475.50",
            txt(d, "#stat-total-spent") == "$1475.50", txt(d, "#stat-total-spent"))
    r.check("budget starts $2500.00",
            txt(d, "#stat-budget-limit") == "$2500.00",
            txt(d, "#stat-budget-limit"))
    r.step("set budget 3000", "type",
           lambda: d.type_text("#input-monthly-budget", "3000"))
    r.step("click set budget", "click", lambda: d.click("#btn-set-budget"))
    r.check("budget limit now $3000.00",
            txt(d, "#stat-budget-limit") == "$3000.00",
            txt(d, "#stat-budget-limit"))
    add_expense(r, d, "Cloud Server Hosting", "85.00", "Tech", "2026-11-12")
    r.check("5 rows after first expense",
            count(d, "#expenses-tbody tr") == 5, count(d, "#expenses-tbody tr"))
    add_expense(r, d, "Weekly Groceries", "112.50", "Groceries", "2026-11-15")
    r.check("6 rows after second expense",
            count(d, "#expenses-tbody tr") == 6, count(d, "#expenses-tbody tr"))
    add_expense(r, d, "Luxury Watch", "1500.00", "Tech", "2026-11-16")
    r.check("status turns Over Budget",
            txt(d, "#stat-budget-status") == "Over Budget",
            txt(d, "#stat-budget-status"))
    r.step("delete luxury watch", "click",
           lambda: d.click("#btn-del-expense-luxury-watch"))
    r.check("status back to Safe", txt(d, "#stat-budget-status") == "Safe",
            txt(d, "#stat-budget-status"))
    r.check("remaining $1327.00",
            txt(d, "#stat-remaining-budget") == "$1327.00",
            txt(d, "#stat-remaining-budget"))
    r.check("total spent $1673.00",
            txt(d, "#stat-total-spent") == "$1673.00",
            txt(d, "#stat-total-spent"))
    r.step("filter Groceries", "select",
           lambda: select_option(d, "#filter-expense-category", "Groceries"))
    r.check("exactly 2 rows filtered",
            count(d, "#expenses-tbody tr") == 2, count(d, "#expenses-tbody tr"))
    r.step("reset filter to all", "select",
           lambda: select_option(d, "#filter-expense-category", "all"))
    r.check("all 6 rows visible", count(d, "#expenses-tbody tr") == 6,
            count(d, "#expenses-tbody tr"))
    r.step("save budget report", "click", lambda: d.click("#btn-save-budget"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#budget-status-banner"))
    r.check("save banner confirms report",
            "Budget report saved: 6 expenses totaling $1673.00 (Remaining: $1327.00)"
            in norm(banner), norm(banner))


# ---------------- q05 contact book ----------------

def run_q05(r, d):
    open_fixture(r, d, "test-05-contact-book.html")
    r.check("6 contacts initially", txt(d, "#contacts-count") == "6",
            txt(d, "#contacts-count"))
    r.check("6 cards initially", count(d, ".contact-card") == 6,
            count(d, ".contact-card"))
    r.step("open new contact modal", "click",
           lambda: d.click("#btn-new-contact"))
    r.check("modal opens",
            d.eval("return document.getElementById('contact-modal')"
                   ".style.display;") == "flex",
            d.eval("return document.getElementById('contact-modal')"
                   ".style.display;"))
    r.step("type first name Frank", "type",
           lambda: d.type_text("#input-contact-first", "Frank"))
    r.step("type last name Sinatra", "type",
           lambda: d.type_text("#input-contact-last", "Sinatra"))
    r.step("type email", "type",
           lambda: d.type_text("#input-contact-email", "frank.s@example.com"))
    r.step("type phone", "type",
           lambda: d.type_text("#input-contact-phone", "+1-555-0106"))
    r.step("select department Engineering", "select",
           lambda: select_option(d, "#select-contact-group", "Engineering"))
    r.step("type notes", "type",
           lambda: d.type_text("#input-contact-notes", "Vocal Architect"))
    r.step("save new contact", "click",
           lambda: d.click("#btn-modal-save-contact"))
    r.check("count 7 after add", txt(d, "#contacts-count") == "7",
            txt(d, "#contacts-count"))
    r.step("edit bob martin", "click",
           lambda: d.click("#btn-edit-contact-bob-martin"))
    r.step("change bob phone", "type",
           lambda: d.type_text("#input-contact-phone", "+1-555-9999"))
    r.step("save edited contact", "click",
           lambda: d.click("#btn-modal-save-contact"))
    r.check("bob phone updated", txt(d, "#phone-bob-martin") == "+1-555-9999",
            txt(d, "#phone-bob-martin"))
    r.step("star david kim", "click",
           lambda: d.click("#btn-fav-contact-david-kim"))
    r.check("david kim star active",
            has_class(d, "#btn-fav-contact-david-kim", "active"),
            d.eval("return document.getElementById('btn-fav-contact-david-kim')"
                   ".className;"))
    r.step("delete spam bot", "click",
           lambda: d.click("#btn-del-contact-spam-bot"))
    r.check("count 6 after delete", txt(d, "#contacts-count") == "6",
            txt(d, "#contacts-count"))
    r.step("search Kim", "type",
           lambda: d.type_text("#contact-search", "Kim"))
    r.check("only 1 card after search Kim", count(d, ".contact-card") == 1,
            count(d, ".contact-card"))
    r.check("visible card is david kim",
            "David Kim" in norm(txt(d, "#contacts-list")),
            norm(txt(d, "#contacts-list")))
    r.step("clear search", "clear", lambda: clear_input(d, "#contact-search"))
    r.step("filter Engineering", "select",
           lambda: select_option(d, "#filter-contact-group", "Engineering"))
    r.check("exactly 3 engineering cards", count(d, ".contact-card") == 3,
            count(d, ".contact-card"))
    r.step("reset filter to all", "select",
           lambda: select_option(d, "#filter-contact-group", "all"))
    r.check("all 6 cards visible", count(d, ".contact-card") == 6,
            count(d, ".contact-card"))
    r.step("save directory", "click", lambda: d.click("#btn-save-directory"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#contact-status-banner"))
    r.check("save banner confirms 6 contacts 1 favorite",
            "Directory saved: 6 contacts (1 favorite)" in norm(banner),
            norm(banner))


# ---------------- q06 file converter ----------------

def run_q06(r, d):
    open_fixture(r, d, "test-06-file-converter.html")
    r.check("queue starts 0", txt(d, "#queue-count") == "0",
            txt(d, "#queue-count"))
    r.step("select source sample-data.csv", "select",
           lambda: select_option(d, "#select-source-file", "sample-data.csv"))
    r.step("select target JSON", "select",
           lambda: select_option(d, "#select-target-format", "JSON"))
    r.step("select compression High", "select",
           lambda: select_option(d, "#select-compression", "High"))
    r.step("check preserve metadata", "click",
           lambda: d.click("#check-preserve-meta"))
    r.check("preserve metadata checked",
            is_checked(d, "#check-preserve-meta"), "checked")
    r.step("add csv to queue", "click", lambda: d.click("#btn-add-queue"))
    r.check("queue 1 row", count(d, "#queue-table-body tr") == 1,
            count(d, "#queue-table-body tr"))
    r.check("row target is JSON",
            "JSON" in norm(txt(d, "#queue-table-body")),
            norm(txt(d, "#queue-table-body")))
    r.step("select source photo.png", "select",
           lambda: select_option(d, "#select-source-file", "photo.png"))
    r.step("select target WEBP", "select",
           lambda: select_option(d, "#select-target-format", "WEBP"))
    r.step("add png to queue", "click", lambda: d.click("#btn-add-queue"))
    r.check("queue 2 rows", count(d, "#queue-table-body tr") == 2,
            count(d, "#queue-table-body tr"))
    r.step("select source corrupted.bin", "select",
           lambda: select_option(d, "#select-source-file", "corrupted.bin"))
    r.step("add corrupted to queue", "click", lambda: d.click("#btn-add-queue"))
    r.check("queue 3 rows", count(d, "#queue-table-body tr") == 3,
            count(d, "#queue-table-body tr"))
    r.check("corrupted badge Invalid format",
            txt(d, "#status-corrupted-bin") == "Invalid format",
            txt(d, "#status-corrupted-bin"))
    r.step("remove corrupted row", "click",
           lambda: d.click("#btn-remove-queue-corrupted-bin"))
    r.check("queue back to 2 rows", count(d, "#queue-table-body tr") == 2,
            count(d, "#queue-table-body tr"))
    r.step("convert all", "click", lambda: d.click("#btn-convert-all"))
    r.check("status Conversion complete",
            txt(d, "#queue-status-text") == "Conversion complete",
            txt(d, "#queue-status-text"))
    r.check("output count 2", txt(d, "#output-count") == "2",
            txt(d, "#output-count"))
    r.step("download sample-data.json", "click",
           lambda: d.click("#btn-download-sample-data-csv"))
    r.check("csv badge Downloaded",
            txt(d, "#badge-download-sample-data-csv") == "Downloaded",
            txt(d, "#badge-download-sample-data-csv"))
    r.step("download photo.webp", "click",
           lambda: d.click("#btn-download-photo-png"))
    r.check("png badge Downloaded",
            txt(d, "#badge-download-photo-png") == "Downloaded",
            txt(d, "#badge-download-photo-png"))
    r.step("save session", "click", lambda: d.click("#btn-save-session"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#converter-status-banner"))
    r.check("save banner confirms batch",
            "Batch complete: 2 files converted and 2 downloaded" in norm(banner),
            norm(banner))


# ---------------- q07 weather dashboard ----------------

def run_q07(r, d):
    open_fixture(r, d, "test-07-weather-dashboard.html")
    r.check("3 city cards initially", count(d, ".city-card") == 3,
            count(d, ".city-card"))
    r.check("city count starts 3", txt(d, "#stat-city-count") == "3",
            txt(d, "#stat-city-count"))
    r.check("celsius toggle active",
            has_class(d, "#btn-unit-c", "active"),
            d.eval("return document.getElementById('btn-unit-c').className;"))
    r.check("tokyo 18C", txt(d, "#temp-tokyo") == "18°C", txt(d, "#temp-tokyo"))
    r.step("switch to fahrenheit", "click", lambda: d.click("#btn-unit-f"))
    r.check("tokyo 64F", txt(d, "#temp-tokyo") == "64°F", txt(d, "#temp-tokyo"))
    r.check("london 54F", txt(d, "#temp-london") == "54°F",
            txt(d, "#temp-london"))
    r.step("switch back to celsius", "click", lambda: d.click("#btn-unit-c"))
    r.check("tokyo back to 18C", txt(d, "#temp-tokyo") == "18°C",
            txt(d, "#temp-tokyo"))
    r.step("select ho chi minh city", "select",
           lambda: select_option(d, "#select-add-city", "ho-chi-minh-city"))
    r.step("add city", "click", lambda: d.click("#btn-add-city"))
    r.check("hcmc card created", d.visible("#card-city-ho-chi-minh-city"),
            "visible")
    r.check("hcmc 32C", txt(d, "#temp-ho-chi-minh-city") == "32°C",
            txt(d, "#temp-ho-chi-minh-city"))
    r.step("select reykjavik", "select",
           lambda: select_option(d, "#select-add-city", "reykjavik"))
    r.step("add reykjavik by mistake", "click",
           lambda: d.click("#btn-add-city"))
    r.check("reykjavik card appears",
            d.visible("#card-city-reykjavik"), "visible")
    r.check("reykjavik snow showers",
            "Snow Showers" in norm(txt(d, "#card-city-reykjavik")),
            norm(txt(d, "#card-city-reykjavik")))
    r.check("city count 5", txt(d, "#stat-city-count") == "5",
            txt(d, "#stat-city-count"))
    r.step("remove reykjavik", "click",
           lambda: d.click("#btn-remove-city-reykjavik"))
    r.check("reykjavik card gone from DOM",
            count(d, "#card-city-reykjavik") == 0,
            count(d, "#card-city-reykjavik"))
    r.check("city count back to 4", txt(d, "#stat-city-count") == "4",
            txt(d, "#stat-city-count"))
    r.step("set hcmc primary", "click",
           lambda: d.click("#btn-primary-city-ho-chi-minh-city"))
    r.check("hcmc card has primary-city class",
            has_class(d, "#card-city-ho-chi-minh-city", "primary-city"),
            d.eval("return document.getElementById"
                   "('card-city-ho-chi-minh-city').className;"))
    r.check("primary badge exists",
            count(d, "#badge-primary-ho-chi-minh-city") == 1,
            count(d, "#badge-primary-ho-chi-minh-city"))
    r.step("switch to fahrenheit for handover", "click",
           lambda: d.click("#btn-unit-f"))
    r.check("active unit indicator F",
            txt(d, "#active-unit-indicator") == "°F",
            txt(d, "#active-unit-indicator"))
    r.check("hcmc 90F", txt(d, "#temp-ho-chi-minh-city") == "90°F",
            txt(d, "#temp-ho-chi-minh-city"))
    r.step("save dashboard", "click", lambda: d.click("#btn-save-weather"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#weather-status-banner"))
    r.check("save banner confirms dashboard",
            "Dashboard saved: 4 cities monitored in °F (Primary: Ho Chi Minh City)"
            in norm(banner), norm(banner))


# ---------------- q08 quiz app ----------------

def run_q08(r, d):
    open_fixture(r, d, "test-08-quiz-app.html")
    r.check("question 1 visible",
            "Which HTTP status code represents 'Created'?" in norm(txt(d, "#question-text")),
            norm(txt(d, "#question-text")))
    r.check("progress 1 of 5", txt(d, "#progress-text") == "Question 1 of 5",
            txt(d, "#progress-text"))
    r.step("answer q1 201 Created", "click", lambda: d.click("#opt-q1-201"))
    r.step("next to q2", "click", lambda: d.click("#btn-next-question"))
    r.check("question 2 visible",
            "What is the primary role of the Wayland compositor?" in norm(txt(d, "#question-text")),
            norm(txt(d, "#question-text")))
    r.step("answer q2 compositor", "click",
           lambda: d.click("#opt-q2-compositor"))
    r.step("next to q3", "click", lambda: d.click("#btn-next-question"))
    r.check("question 3 visible",
            "Which data structure provides O(1) average time complexity for lookup?"
            in norm(txt(d, "#question-text")), norm(txt(d, "#question-text")))
    r.step("accidentally pick linked list", "click",
           lambda: d.click("#opt-q3-linked-list"))
    r.step("correct to hash table", "click",
           lambda: d.click("#opt-q3-hash-table"))
    r.check("hash table selected", is_checked(d, "#opt-q3-hash-table"),
            "checked")
    r.check("linked list no longer selected",
            not is_checked(d, "#opt-q3-linked-list"), "unchecked")
    r.step("next to q4", "click", lambda: d.click("#btn-next-question"))
    r.check("question 4 visible",
            "Which CSS declaration promotes an element to a GPU compositing layer?"
            in norm(txt(d, "#question-text")), norm(txt(d, "#question-text")))
    r.step("answer q4 will-change", "click",
           lambda: d.click("#opt-q4-will-change"))
    r.step("next to q5", "click", lambda: d.click("#btn-next-question"))
    r.check("question 5 visible",
            "Which signal is dispatched by 'kill -9' in Unix?"
            in norm(txt(d, "#question-text")), norm(txt(d, "#question-text")))
    r.step("answer q5 sigkill", "click", lambda: d.click("#opt-q5-sigkill"))
    r.step("back to q4", "click", lambda: d.click("#btn-prev-question"))
    r.check("q4 still shows after back",
            "Which CSS declaration promotes an element to a GPU compositing layer?"
            in norm(txt(d, "#question-text")), norm(txt(d, "#question-text")))
    r.check("q4 answer retained", is_checked(d, "#opt-q4-will-change"),
            "checked")
    r.step("forward to q5", "click", lambda: d.click("#btn-next-question"))
    r.check("q5 still shows after forward",
            "Which signal is dispatched by 'kill -9' in Unix?"
            in norm(txt(d, "#question-text")), norm(txt(d, "#question-text")))
    r.check("q5 answer retained", is_checked(d, "#opt-q5-sigkill"), "checked")
    r.check("submit button visible", d.visible("#btn-submit-quiz"), "visible")
    r.step("submit quiz", "click", lambda: d.click("#btn-submit-quiz"))
    r.check("results card displayed", d.visible("#quiz-results-card"),
            "visible")
    r.check("final score 5 / 5", txt(d, "#stat-final-score") == "5 / 5",
            txt(d, "#stat-final-score"))
    r.check("percent 100%", txt(d, "#stat-score-percent") == "100%",
            txt(d, "#stat-score-percent"))
    r.step("save quiz results", "click", lambda: d.click("#btn-save-quiz"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#quiz-status-banner"))
    r.check("save banner confirms 5/5 100%",
            "Quiz completed: 5/5 score (100%) - Results verified and saved"
            in norm(banner), norm(banner))


# ---------------- q09 pomodoro timer ----------------

def run_q09(r, d):
    open_fixture(r, d, "test-09-pomodoro-timer.html")
    r.check("focus mode active initially",
            has_class(d, "#btn-mode-work", "active"),
            d.eval("return document.getElementById('btn-mode-work').className;"))
    r.check("clock starts 25:00", txt(d, "#timer-display") == "25:00",
            txt(d, "#timer-display"))
    r.step("open settings", "click", lambda: d.click("#btn-open-settings"))
    r.check("settings modal opens",
            d.eval("return document.getElementById('settings-modal')"
                   ".style.display;") == "flex",
            d.eval("return document.getElementById('settings-modal')"
                   ".style.display;"))
    r.step("set work duration 30", "type",
           lambda: d.type_text("#input-work-duration", "30"))
    r.step("set break duration 6", "type",
           lambda: d.type_text("#input-break-duration", "6"))
    r.step("check auto-break", "click", lambda: d.click("#check-auto-break"))
    r.check("auto-break checked", is_checked(d, "#check-auto-break"),
            "checked")
    r.step("save settings", "click", lambda: d.click("#btn-save-settings"))
    r.check("settings modal closed",
            d.eval("return document.getElementById('settings-modal')"
                   ".style.display;") == "none",
            d.eval("return document.getElementById('settings-modal')"
                   ".style.display;"))
    r.check("clock now 30:00", txt(d, "#timer-display") == "30:00",
            txt(d, "#timer-display"))
    r.step("start first focus", "click", lambda: d.click("#btn-start-pause"))
    r.check("button label Pause", txt(d, "#btn-start-pause") == "Pause",
            txt(d, "#btn-start-pause"))
    r.step("complete focus cycle 1", "click",
           lambda: d.click("#btn-complete-cycle"))
    hist = r.step("read history", "text", lambda: txt(d, "#history-list"))
    r.check("history logs session 1 focus",
            "Session 1: Focus (30m, Focus)" in norm(hist), norm(hist))
    r.check("break mode active after focus",
            has_class(d, "#btn-mode-short-break", "active"),
            d.eval("return document.getElementById('btn-mode-short-break')"
                   ".className;"))
    r.check("clock 06:00 in break", txt(d, "#timer-display") == "06:00",
            txt(d, "#timer-display"))
    r.step("complete break cycle", "click",
           lambda: d.click("#btn-complete-cycle"))
    hist = r.step("read history 2", "text", lambda: txt(d, "#history-list"))
    r.check("history logs session 2 break",
            "Session 2: Short Break (6m, Break)" in norm(hist), norm(hist))
    r.check("work mode active again",
            has_class(d, "#btn-mode-work", "active"),
            d.eval("return document.getElementById('btn-mode-work').className;"))
    r.check("clock back to 30:00", txt(d, "#timer-display") == "30:00",
            txt(d, "#timer-display"))
    r.step("start second focus", "click", lambda: d.click("#btn-start-pause"))
    r.step("accidental reset", "click", lambda: d.click("#btn-reset-timer"))
    r.check("button label Start after reset",
            txt(d, "#btn-start-pause") == "Start", txt(d, "#btn-start-pause"))
    r.check("clock reset to 30:00", txt(d, "#timer-display") == "30:00",
            txt(d, "#timer-display"))
    r.check("no incomplete session appended",
            count(d, "#history-list .history-row") == 2,
            count(d, "#history-list .history-row"))
    r.step("complete focus cycle 2", "click",
           lambda: d.click("#btn-complete-cycle"))
    hist = r.step("read history 3", "text", lambda: txt(d, "#history-list"))
    r.check("history logs session 3 focus",
            "Session 3: Focus (30m, Focus)" in norm(hist), norm(hist))
    r.check("completed cycles 2", txt(d, "#stat-completed-cycles") == "2",
            txt(d, "#stat-completed-cycles"))
    r.check("total focus 60 min", txt(d, "#stat-total-focus") == "60 min",
            txt(d, "#stat-total-focus"))
    r.step("save session log", "click", lambda: d.click("#btn-save-session"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#pomodoro-status-banner"))
    r.check("save banner confirms 2 cycles 60 min",
            "Session log saved: 2 focus cycles completed (60 min total focus)"
            in norm(banner), norm(banner))


# ---------------- q10 markdown editor ----------------

def run_q10(r, d):
    open_fixture(r, d, "test-10-markdown-editor.html")
    r.check("initial preview shows empty message",
            "Live preview will appear here..." in norm(txt(d, "#markdown-preview")),
            norm(txt(d, "#markdown-preview")))
    r.step("type doc title", "type",
           lambda: d.type_text("#input-doc-title", "Release Notes v2.3.0"))
    md = ""
    md += "# Architecture Overview"
    r.step("type h1", "type", lambda: d.type_text("#markdown-source", md))
    r.check("preview renders h1",
            d.eval("return document.querySelector('#markdown-preview h1')"
                   " ? document.querySelector('#markdown-preview h1')"
                   ".textContent : null;") == "Architecture Overview",
            d.eval("return document.querySelector('#markdown-preview h1')"
                   " ? document.querySelector('#markdown-preview h1')"
                   ".textContent : null;"))
    md += "\n## Core Changes"
    r.step("type h2", "type", lambda: d.type_text("#markdown-source", md))
    r.check("preview renders h2",
            d.eval("return document.querySelector('#markdown-preview h2')"
                   " ? document.querySelector('#markdown-preview h2')"
                   ".textContent : null;") == "Core Changes",
            d.eval("return document.querySelector('#markdown-preview h2')"
                   " ? document.querySelector('#markdown-preview h2')"
                   ".textContent : null;"))
    md += "\n- Replaced X11 with native Wayland compositor"
    r.step("type list item 1", "type",
           lambda: d.type_text("#markdown-source", md))
    md += "\n- Added offline test validation suite"
    r.step("type list item 2", "type",
           lambda: d.type_text("#markdown-source", md))
    r.check("preview renders 2 list items",
            count(d, "#markdown-preview li") == 2,
            count(d, "#markdown-preview li"))
    md += "\n- Broken experimental feature (deprecated)"
    r.step("type accidental list item", "type",
           lambda: d.type_text("#markdown-source", md))
    r.check("preview shows 3 list items",
            count(d, "#markdown-preview li") == 3,
            count(d, "#markdown-preview li"))
    md = md.replace("\n- Broken experimental feature (deprecated)", "")
    r.step("remove accidental line", "type",
           lambda: d.type_text("#markdown-source", md))
    r.check("preview back to 2 list items",
            count(d, "#markdown-preview li") == 2,
            count(d, "#markdown-preview li"))
    md += "\n**Zero regressions** observed in test suite."
    r.step("type strong note", "type",
           lambda: d.type_text("#markdown-source", md))
    r.check("preview renders strong tag",
            d.eval("return document.querySelector('#markdown-preview strong')"
                   " ? document.querySelector('#markdown-preview strong')"
                   ".textContent : null;") == "Zero regressions",
            d.eval("return document.querySelector('#markdown-preview strong')"
                   " ? document.querySelector('#markdown-preview strong')"
                   ".textContent : null;"))
    wc = r.step("read word count", "text", lambda: txt(d, "#stat-word-count"))
    r.check("word count non-zero", int(wc) > 0, wc)
    r.step("export html", "click", lambda: d.click("#btn-export-html"))
    r.check("export badge visible", d.visible("#export-status-tag"), "visible")
    r.check("export badge text",
            txt(d, "#export-status-tag") == "HTML Exported",
            txt(d, "#export-status-tag"))
    r.step("save document", "click", lambda: d.click("#btn-save-doc"))
    banner = r.step("read status banner", "text",
                    lambda: txt(d, "#editor-status-banner"))
    r.check("save banner confirms document",
            "Document saved: 'Release Notes v2.3.0' (HTML exported, 0 errors)"
            in norm(banner), norm(banner))


TESTS = {
    "q01": run_q01, "q02": run_q02, "q03": run_q03, "q04": run_q04,
    "q05": run_q05, "q06": run_q06, "q07": run_q07, "q08": run_q08,
    "q09": run_q09, "q10": run_q10,
}


def bootstrap_tab(base):
    """Find or create ONE visible test tab, shared by all tests.

    Preference order: an about:blank tab, then any tab already on our
    test origin (leftovers from probes are fine, they hold no user
    content). Only if neither exists, create one with window/new and
    verify it is visible (with the ensure_visible recovery). The tab
    is kept out of opened_tabs so session cleanup never closes it.
    Returns the tab handle.
    """
    wd = WD()
    d = wd.__enter__()
    try:
        for h in d.handles():
            try:
                d.switch(h)
                url = d.eval("return document.URL")
            except Exception:
                continue  # alert tab etc: never touch it
            if url == "about:blank" or url.startswith(base):
                print(f"reusing test tab {h[:8]} url={url[:60]}",
                      flush=True)
                return h
        h = d.new_tab(base + "/agy-q2/fixtures/test-01-whiteboard.html")
        r = Runner("bootstrap", base)
        r.tab = h
        if not ensure_visible(d, r, "new test tab"):
            raise RuntimeError(
                "new test tab body hidden after recovery; cannot drive")
        d.opened_tabs.remove(h)
        print(f"created test tab {h[:8]}", flush=True)
        return h
    finally:
        wd.__exit__()


def main():
    args = sys.argv[1:]
    selected = list(TESTS) if not args or args == ["all"] else args
    unknown = [a for a in selected if a not in TESTS]
    if unknown:
        print(f"unknown tests: {unknown}", file=sys.stderr)
        return 2
    _, base = start_server()
    print(f"serving at {base}", flush=True)
    try:
        tab = bootstrap_tab(base)
    except Exception as exc:
        print(f"BOOTSTRAP FAILED {type(exc).__name__}: {exc}", flush=True)
        return 2
    results = []
    wd_failures = 0
    for tid in selected:
        r = Runner(tid, base)
        r.tab = tab
        try:
            wd = WD()
            d = wd.__enter__()
        except Exception as exc:
            # Only a failure to CREATE the session counts toward the
            # abort threshold. A step failure inside a test contains
            # "/session/<id>/..." in its URL and must never count here
            # (that bug aborted the first Y4 run after 2 tests).
            r.failures.append(f"session: {type(exc).__name__}: {exc}")
            print(f"[{tid}] SESSION ERROR {type(exc).__name__}: {exc}",
                  flush=True)
            wd_failures += 1
            results.append(r.summary())
            print(json.dumps(results[-1], ensure_ascii=False), flush=True)
            if wd_failures >= 2:
                print("two consecutive session-creation failures, aborting run",
                      flush=True)
                break
            continue
        try:
            TESTS[tid](r, d)
        except Exception as exc:
            r.failures.append(f"runner: {type(exc).__name__}: {exc}")
            print(f"[{tid}] RUNNER ERROR {type(exc).__name__}: {exc}",
                  flush=True)
        finally:
            wd.__exit__()
        wd_failures = 0
        summary = r.summary()
        results.append(summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    passed = sum(1 for s in results if s["pass"])
    total_ms = sum(s["elapsed_ms"] for s in results)
    print(json.dumps({"suite": "agy-q2", "passed": passed,
                      "total": len(results), "total_ms": total_ms},
                     ensure_ascii=False), flush=True)
    # Leave the shared test tab clean (about:blank) for the next runner.
    try:
        with WD() as d:
            d.switch(tab)
            d.goto("about:blank")
            print("test tab returned to about:blank", flush=True)
    except Exception as exc:
        print(f"tab cleanup failed (harmless): {exc}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
