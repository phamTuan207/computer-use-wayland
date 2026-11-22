#!/usr/bin/env python3
"""Live Zen runner: q04 re-run (fixed fixture) + fcc-k f01-f10 (Worker U, 21/11/2026).

Runs against the LIVE Zen on the laptop via geckodriver --connect-existing
(Marionette 2828), reusing the proven driver from tests/realistic/run_live.py
(Worker P) and the helpers from tests/realistic/run_agyq.py (Worker R):
- explicit tab switch after window/new, 1s settle after navigation,
  0.5s after switch, no maximize, one WebDriver session per test,
  always deleted in a finally block,
- end states verified by reading the DOM directly. The fixtures'
  window.__fcckVerify() / __agyVerify() hooks are NEVER used as oracles.

q04: the fixture bug R proved (double-escaped regexes in renderPreview)
is fixed (commit on todolist-push: single backslashes in the three
regexes, plus the same fix in INITIAL_NOTES bodies, the snippet regex,
and the __agyVerify hook body). This run clicks the RENDERED wiki link
in Preview (spec steps 9-10) instead of working around via the sidebar.

f01-f10: Worker S fixed all fixtures (DOM-only checkers, missing UI
added, jsdom-verified 10/10). This is the first LIVE Zen run of the
fixed fixtures.

Usage (on the laptop, from /tmp/worker-u-server):
  LIVE_SERVER_ROOT=/tmp/worker-u-server LIVE_SERVER_PORT=8767 \
  LIVE_LOG=/tmp/worker-u-live.jsonl WD_PORT=4447 \
  python3 run_fcck.py q04
  python3 run_fcck.py all
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, Runner, start_server  # noqa: E402


def select_option(d, css, value):
    """Set a <select> value and fire change."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def clear_search(d, css):
    """Clear an input and fire input so the filter re-renders."""
    return d.eval(
        "const el=document.querySelector(arguments[0]); el.value='';"
        "el.dispatchEvent(new Event('input',{bubbles:true})); return 'cleared';",
        [css])


def norm(s):
    """Collapse all whitespace so multi-line renders compare sanely."""
    return " ".join((s or "").split())


def append_text(d, css, text):
    """Type without clearing: focus, caret to end, send keys."""
    d.eval(
        "const el=document.querySelector(arguments[0]); el.focus();"
        "el.setSelectionRange(el.value.length, el.value.length);",
        [css])
    el = d.find(css)
    d._wd("POST", d._s(f"/element/{el}/value"), {"text": text})
    return "appended"


def type_contenteditable(d, css, text):
    """Type into a contenteditable cell via the browser editing commands.

    Marionette element/value only works for input/textarea/select, so for
    contenteditable cells use focus + selectAll + insertText, which is the
    user-equivalent input path (not a direct state write).
    """
    return d.eval(
        "const el=document.querySelector(arguments[0]); el.focus();"
        "document.execCommand('selectAll', false, null);"
        "document.execCommand('insertText', false, arguments[1]);"
        "return el.textContent;", [css, text])


def click_note_by_title(d, title):
    """Click a q04 sidebar note by its TITLE text only."""
    return d.eval(
        "const items=[...document.querySelectorAll('#notes-list-scroll .note-item')];"
        "const it=items.find(e=>{const t=e.querySelector('.note-item-title');"
        "return t && t.textContent.replace(/\\uD83D\\uDCCC/g,'').trim()===arguments[0];});"
        "if(!it) return 'NOT-FOUND'; it.click();"
        "return 'clicked: '+arguments[0];", [title])


def note_titles(d):
    return d.eval(
        "return [...document.querySelectorAll('#notes-list-scroll .note-item .note-item-title')]"
        ".map(e=>e.textContent.replace(/\\uD83D\\uDCCC/g,'').trim())")


def body_visible(d):
    """Guard against the hidden-body Marionette incident (R, 21/11):
    new tabs once rendered with document.body visibility hidden."""
    return d.eval(
        "return getComputedStyle(document.body).visibility")


# ---------------- q04 re-run (fixed fixture) ----------------

def run_q04(r, d):
    url = r.base + "/agy-q/fixtures/test-04-notes-app.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible (no hidden-body incident)", vis == "visible", vis)
    notes0 = r.step("read sidebar notes", "eval",
                    lambda: d.eval(
                        "return [...document.querySelectorAll('#notes-list-scroll .note-item .note-item-title')]"
                        ".map(e=>e.textContent.trim())"))
    r.details["initialNotes"] = notes0
    r.check("3 initial notes", len(notes0) == 3, str(notes0))
    r.check("initial notes are the 3 expected",
            sorted(notes0) == ["Security Model", "Storage Engine",
                               "System Architecture"], str(notes0))
    r.step("click New Note", "click", lambda: d.click("#btn-new-note"))
    r.step("type note title", "type",
           lambda: d.type_text("#input-note-title", "Memory Tiering RFC"))
    r.step("type note tags", "type",
           lambda: d.type_text("#input-note-tags", "rfc, performance, memory"))
    body = ("# Memory Tiering Architecture\n\n"
            "This proposal integrates tiered RAM and CXL memory.\n\n"
            "Related: [[Storage Engine]] and [[Security Model]].")
    r.step("type note body", "type",
           lambda: d.type_text("#textarea-note-body", body))
    r.step("click Save Note", "click", lambda: d.click("#btn-save-note"))
    notes1 = r.step("read sidebar after create", "eval",
                    lambda: d.eval(
                        "return [...document.querySelectorAll('#notes-list-scroll .note-item')]"
                        ".map(e=>e.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["notesAfterCreate"] = notes1
    r.check("Memory Tiering RFC in sidebar",
            any("Memory Tiering RFC" in n for n in notes1), str(notes1))
    r.check("new note shows tags rfc, performance, memory",
            any("rfc" in n and "performance" in n and "memory" in n
                for n in notes1), str(notes1))
    # Spec steps 9-10, the part that could NOT run before the fix:
    # switch to Preview, the wiki link must now RENDER as <a>, and a real
    # Marionette click on it must navigate to Storage Engine.
    r.step("switch to Preview tab", "click", lambda: d.click("#tab-preview-mode"))
    preview_html = r.step("read preview HTML", "eval",
                          lambda: d.eval(
                              "return document.querySelector('#rendered-markdown-content').innerHTML"))
    r.details["previewHtml"] = preview_html
    link_present = r.step("check wiki link rendered", "eval",
                          lambda: d.eval(
                              "return !!document.querySelector('[id=\"link-note-Storage Engine\"]')"))
    r.details["wikiLinkRendered"] = link_present
    r.check("wiki link renders in preview after fix", link_present is True,
            preview_html[:300])
    r.check("no raw [[...]] markup survives in preview",
            "[[Storage Engine]]" not in preview_html, preview_html[:300])
    r.check("paragraph breaks render as </p><p>",
            "</p><p>" in preview_html, preview_html[:300])
    r.step("click rendered wiki link", "click",
           lambda: d.click('[id="link-note-Storage Engine"]'))
    title = r.step("read current note title after link click", "value",
                   lambda: d.value("#input-note-title"))
    r.details["titleAfterLinkClick"] = title
    r.check("wiki link navigates to Storage Engine", title == "Storage Engine",
            str(title))
    bl = r.step("read backlinks box", "text", lambda: d.text("#box-backlinks"))
    r.details["backlinksStorageEngine"] = bl
    r.check("backlink shows Memory Tiering RFC", "Memory Tiering RFC" in bl, bl)
    r.step("switch to Edit tab", "click", lambda: d.click("#tab-edit-mode"))
    r.step("append reciprocal link", "append",
           lambda: append_text(d, "#textarea-note-body",
                               "\n\nReference: [[Memory Tiering RFC]]."))
    r.step("click Save Note again", "click", lambda: d.click("#btn-save-note"))
    r.step("click Pin Note", "click", lambda: d.click("#btn-pin-note"))
    pinned_ok = r.step("check PINNED section content", "eval",
                       lambda: d.eval(
                           "const t=document.querySelector('#sidebar').innerText;"
                           "const p=t.indexOf('PINNED'); const a=t.indexOf('ALL NOTES');"
                           "return p>=0 ? t.slice(p,a) : 'NO-PINNED-SECTION'"))
    r.details["pinnedSection"] = pinned_ok
    r.check("PINNED section lists Storage Engine",
            "Storage Engine" in str(pinned_ok), str(pinned_ok))
    r.step("search #performance", "type",
           lambda: d.type_text("#input-notes-search", "#performance"))
    perf = r.step("read filtered notes", "eval", lambda: note_titles(d))
    r.details["performanceSearch"] = perf
    r.check("tag search matches exactly 2 notes", len(perf) == 2, str(perf))
    r.check("matches are Storage Engine + Memory Tiering RFC",
            sorted(perf) == ["Memory Tiering RFC", "Storage Engine"], str(perf))
    r.step("clear search", "eval",
           lambda: clear_search(d, "#input-notes-search"))
    r.step("open Security Model note", "click_js",
           lambda: click_note_by_title(d, "Security Model"))
    title2 = r.step("read current title before archive", "value",
                    lambda: d.value("#input-note-title"))
    r.check("Security Model opened", title2 == "Security Model", str(title2))
    r.step("click Archive Note", "click", lambda: d.click("#btn-archive-note"))
    notes2 = r.step("read sidebar after archive", "eval", lambda: note_titles(d))
    r.details["notesAfterArchive"] = notes2
    r.check("Security Model removed from active list",
            "Security Model" not in notes2, str(notes2))
    r.step("open Archived view", "click", lambda: d.click("#tab-view-archived"))
    arch = r.step("read archived list", "eval", lambda: note_titles(d))
    r.details["archivedList"] = arch
    r.check("Security Model in archived list", "Security Model" in arch, str(arch))
    r.step("return to All Notes view", "click", lambda: d.click("#tab-view-all"))
    count = r.step("read active count badge", "text", lambda: d.text("#count-active"))
    r.details["activeCount"] = count
    r.check("active count badge is 3", count.strip() == "3", count)
    r.step("click Export Notes Manifest", "click", lambda: d.click("#btn-export-notes"))
    summary = r.step("read export summary", "text",
                     lambda: d.text("#export-summary-text"))
    r.details["exportSummary"] = summary
    r.check("manifest says Active: 3, Archived: 1, Pinned: 1",
            "Active: 3, Archived: 1, Pinned: 1" in summary, summary)
    r.step("dismiss export modal", "click", lambda: d.click("#btn-dismiss-export-modal"))
    r.step("re-open Memory Tiering RFC", "click_js",
           lambda: click_note_by_title(d, "Memory Tiering RFC"))
    bl2 = r.step("read backlinks of new note", "text", lambda: d.text("#box-backlinks"))
    r.details["backlinksNewNote"] = bl2
    r.check("reciprocal backlink shows Storage Engine",
            "Storage Engine" in bl2, bl2)

# ---------------- fcc-k tests (fixed fixtures, Worker S) ----------------

def _fcc_cell_btn(cell_id):
    # The spreadsheet fixture selects a cell ONLY via the buttons below
    # the table (onclick=clickCell('a2')). Clicking the <td> does nothing
    # (P's trap check, kept here as a regression check).
    return f"button[onclick=\"clickCell('{cell_id}')\"]"


def _click_button_by_text(d, text):
    return d.eval(
        "const b=[...document.querySelectorAll('button')]"
        ".find(x=>x.textContent.trim()===arguments[0]);"
        "if(!b) return 'NOT-FOUND'; b.click(); return 'clicked: '+arguments[0];",
        [text])


def run_f01(r, d):
    url = r.base + "/fcc-k/fixtures/test-01-spreadsheet.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    headers = r.step("read headers", "eval",
                     lambda: d.eval("return [...document.querySelectorAll('#sheet th')].map(e => e.textContent).join(',')"))
    r.check("headers Date Item Units Price Total",
            headers == ",Date,Item,Units,Price,Total", headers)
    r.step("TRAP: click td#a2 directly", "click_js",
           lambda: d.click_js("document.querySelector('#a2')"))
    sel = r.step("check td click selected nothing", "eval",
                 lambda: d.eval("return document.querySelector('#a2').classList.contains('sel')"))
    r.details["tdClickSelects"] = sel
    r.check("td click does NOT select (fixture trap)", sel is False, str(sel))
    rows = [("a2", "2026-11-16"), ("b2", "Widget"), ("c2", "12"),
            ("d2", "45000"), ("e2", "=C2*D2"),
            ("a3", "2026-11-17"), ("b3", "Gadget"), ("c3", "7"),
            ("d3", "82000"), ("e3", "=C3*D3"),
            ("a4", "2026-11-18"), ("b4", "Tool"), ("c4", "5"),
            ("d4", "150000"), ("e4", "=C4*D4"),
            ("e5", "=SUM(E2:E4)"), ("e6", "=AVERAGE(E2:E4)"),
            ("e7", "=COUNT(E2:E4)")]
    for cell, val in rows:
        r.step(f"select {cell.upper()}", "click",
               lambda c=cell: d.click(_fcc_cell_btn(c)))
        r.step(f"type {val} into {cell.upper()}", "type",
               lambda v=val: d.type_text("#typed", v))
        r.step(f"press type for {cell.upper()}", "click",
               lambda: _click_button_by_text(d, "type"))
        if val.startswith("="):
            r.step(f"press Enter for {cell.upper()}", "click",
                   lambda: _click_button_by_text(d, "Enter"))
    e7 = r.step("read E7 after wrong formula", "text", lambda: d.text("#e7"))
    r.details["e7AfterCount"] = e7
    r.check("E7 shows COUNT text after wrong formula", e7 == "COUNT text", e7)
    r.step("select E7", "click", lambda: d.click(_fcc_cell_btn("e7")))
    r.step("type corrected formula", "type",
           lambda: d.type_text("#typed", "=COUNTA(E2:E4)"))
    r.step("press type for correction", "click",
           lambda: _click_button_by_text(d, "type"))
    r.step("press Enter for correction", "click",
           lambda: _click_button_by_text(d, "Enter"))
    vals = r.step("read all result cells", "eval",
                  lambda: d.eval("return {e2: document.querySelector('#e2').textContent,"
                                 "e3: document.querySelector('#e3').textContent,"
                                 "e4: document.querySelector('#e4').textContent,"
                                 "e5: document.querySelector('#e5').textContent,"
                                 "e6: document.querySelector('#e6').textContent,"
                                 "e7: document.querySelector('#e7').textContent,"
                                 "c2: document.querySelector('#c2').textContent,"
                                 "c3: document.querySelector('#c3').textContent,"
                                 "c4: document.querySelector('#c4').textContent}"))
    r.details["endState"] = vals
    for k, v in [("e2", "540000"), ("e3", "574000"), ("e4", "750000"),
                 ("e5", "1864000"), ("e6", "621333"), ("e7", "3")]:
        r.check(f"{k.upper()} == {v}", vals[k] == v, f"{k}={vals[k]}")


def run_f02(r, d):
    url = r.base + "/fcc-k/fixtures/test-02-email.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    count = r.step("count inbox rows", "eval",
                   lambda: d.eval("return document.querySelectorAll('#inbox li').length"))
    r.details["inboxCount"] = count
    r.check("inbox shows 6 messages", count == 6, str(count))
    r.step("open message 1", "click", lambda: d.click("#msg1"))
    body1 = r.step("read message 1 body", "text", lambda: d.text("#msg"))
    r.details["msg1"] = body1
    r.check("message 1 quotes price 45000", "45000" in body1, body1)
    r.step("mark message 1 read", "click", lambda: d.click("#markReadBtn"))
    m1 = r.step("read msg1 row after read", "text", lambda: d.text("#msg1"))
    r.check("message 1 shows (read)", "(read)" in m1, m1)
    r.step("open message 2", "click", lambda: d.click("#msg2"))
    body2 = r.step("read message 2 body", "text", lambda: d.text("#msg"))
    r.details["msg2"] = body2
    r.check("message 2 is the complaint", "damaged" in body2, body2)
    r.step("flag message 2", "click", lambda: d.click("#flagBtn"))
    flag2 = r.step("check msg2 flagged class", "eval",
                   lambda: d.eval("return document.querySelector('#msg2').classList.contains('flagged')"))
    r.check("message 2 flagged", flag2 is True, str(flag2))
    r.step("open message 3", "click", lambda: d.click("#msg3"))
    body3 = r.step("read message 3 body", "text", lambda: d.text("#msg"))
    r.details["msg3"] = body3
    r.check("message 3 has meeting time 10:00", "10:00" in body3, body3)
    r.step("mark message 3 read", "click", lambda: d.click("#markReadBtn"))
    r.step("open message 4", "click", lambda: d.click("#msg4"))
    body4 = r.step("read message 4 subject", "text", lambda: d.text("#msg"))
    r.details["msg4"] = body4
    r.check("message 4 is Newsletter A", "Newsletter A" in body4, body4)
    r.step("archive message 4", "click", lambda: d.click("#archiveBtn"))
    ids4 = r.step("read inbox ids after archive 4", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#inbox li')].map(li=>li.id)"))
    r.check("message 4 gone from inbox", "msg4" not in ids4, str(ids4))
    r.step("open message 5", "click", lambda: d.click("#msg5"))
    r.step("archive message 5", "click", lambda: d.click("#archiveBtn"))
    ids5 = r.step("read inbox ids after archive 5", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#inbox li')].map(li=>li.id)"))
    r.check("message 5 gone from inbox", "msg5" not in ids5, str(ids5))
    r.step("open message 6", "click", lambda: d.click("#msg6"))
    r.step("mark message 6 read", "click", lambda: d.click("#markReadBtn"))
    r.step("star message 6", "click", lambda: d.click("#flagBtn"))
    m6 = r.step("read msg6 row", "eval",
                lambda: d.eval("return {text: document.querySelector('#msg6').textContent,"
                               "flagged: document.querySelector('#msg6').classList.contains('flagged')}"))
    r.details["msg6"] = m6
    r.check("message 6 read", "(read)" in m6["text"], str(m6))
    r.check("message 6 starred", m6["flagged"] is True, str(m6))
    r.step("click Compose", "click", lambda: d.click("#composeBtn"))
    r.step("type To vendor", "type",
           lambda: d.type_text("#toInput", "vendor@example.com"))
    r.step("type Subject", "type",
           lambda: d.type_text("#subjectInput", "Re: vendor quote - price correction"))
    r.step("type body paragraph", "type",
           lambda: d.type_text("#bodyInput",
                               "The original quote was 45000 per unit for 12 units. "
                               "Please correct the price to 42000 per unit. "
                               "The total should be recalculated accordingly."))
    r.step("click Send", "click", lambda: d.click("#sendBtn"))
    sent_msg = r.step("read send confirmation", "text", lambda: d.text("#msg"))
    r.check("send confirms Message sent", "Message sent" in sent_msg, sent_msg)
    r.step("open Sent folder", "click", lambda: d.click("#sentBtn"))
    sent = r.step("read Sent folder", "text", lambda: d.text("#sent"))
    r.details["sentFolder"] = sent
    r.check("Sent has corrected subject",
            "Re: vendor quote - price correction" in sent, sent)
    r.check("Sent To is vendor", "vendor@example.com" in sent, sent)
    r.check("Sent body has both prices",
            "45000" in sent and "42000" in sent, sent)
    r.step("return to Inbox", "click", lambda: d.click("#inboxBtn"))
    ids = r.step("read final inbox ids", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#inbox li')].map(li=>li.id)"))
    r.details["finalInbox"] = ids
    r.check("inbox holds only 1,2,3,6", ids == ["msg1", "msg2", "msg3", "msg6"],
            str(ids))
    flag2b = r.step("re-check msg2 flagged", "eval",
                    lambda: d.eval("return document.querySelector('#msg2').classList.contains('flagged')"))
    r.check("message 2 still flagged", flag2b is True, str(flag2b))
    m1b = r.step("re-check msg1 read", "text", lambda: d.text("#msg1"))
    r.check("message 1 still read", "(read)" in m1b, m1b)


def run_f03(r, d):
    url = r.base + "/fcc-k/fixtures/test-03-calendar.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    days = r.step("read day headers", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#grid .hour')].slice(1,6).map(e=>e.textContent.trim()).join(',')"))
    r.details["days"] = days
    r.check("week shows Tue-Sat", days == "Tue,Wed,Thu,Fri,Sat", days)
    busy = r.step("read busy slots", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#grid .slot.busy')].map(e=>e.dataset.day+' '+e.dataset.hour+':00')"))
    r.details["busySlots"] = busy
    r.check("Tue busy at 9:00 and 13:00",
            "Tue 9:00" in busy and "Tue 13:00" in busy, str(busy))
    # Bonus conflict check (S verified in jsdom): a busy slot refuses.
    r.step("click busy Tue 9:00 slot", "click",
           lambda: d.click('.slot[data-day="Tue"][data-hour="9"]'))
    grid_msg = r.step("read grid message", "text", lambda: d.text("#gridMsg"))
    r.details["busyClickMsg"] = grid_msg
    r.check("busy slot refuses with message", "busy" in grid_msg.lower(), grid_msg)
    dlg_vis = r.step("dialog stays hidden after busy click", "eval",
                     lambda: d.eval("return document.querySelector('#dialog').style.display"))
    r.check("no dialog on busy click", dlg_vis == "none", str(dlg_vis))
    r.step("click free Tue 10:00 slot", "click",
           lambda: d.click('.slot[data-day="Tue"][data-hour="10"]'))
    dlg = r.step("dialog visible after free click", "visible",
                 lambda: d.visible("#dialog"))
    r.check("dialog opens on free slot", dlg, str(dlg))
    dlg_day = r.step("read dialog day", "text", lambda: d.text("#dlgDay"))
    r.check("dialog day is Tue", dlg_day == "Tue", dlg_day)
    dlg_hour = r.step("read dialog hour", "text", lambda: d.text("#dlgHour"))
    r.check("dialog hour is 10:00", dlg_hour == "10:00", dlg_hour)
    r.step("set title", "type", lambda: d.type_text("#dlgTitle", "Project sync"))
    r.step("set date Tue", "select", lambda: select_option(d, "#dlgDate", "Tue"))
    r.step("set start 10:00", "type", lambda: d.type_text("#dlgStart", "10:00"))
    r.step("set duration 30", "select", lambda: select_option(d, "#dlgDur", "30"))
    r.step("set attendee 1", "type",
           lambda: d.type_text("#dlgAtt1", "teammate1@example.com"))
    r.step("set attendee 2", "type",
           lambda: d.type_text("#dlgAtt2", "teammate2@example.com"))
    r.step("set reminder 10", "select", lambda: select_option(d, "#dlgRem", "10"))
    r.step("click Save", "click", lambda: d.click("#dlgSave"))
    new_cell = r.step("read new event cell", "eval",
                      lambda: d.eval("const c=document.querySelector('#grid .slot.new');"
                                     "return c ? {day: c.dataset.day, hour: c.dataset.hour, text: c.textContent} : null"))
    r.details["newCell"] = new_cell
    r.check("exactly one new event cell", new_cell is not None, str(new_cell))
    if new_cell:
        r.check("event on Tue", new_cell["day"] == "Tue", str(new_cell))
        r.check("event at 10:00", new_cell["hour"] == "10", str(new_cell))
        r.check("cell shows Project sync", "Project sync" in new_cell["text"],
                str(new_cell))
    detail = r.step("read event detail", "text", lambda: d.text("#eventDetail"))
    r.details["eventDetail"] = detail
    r.check("detail has title", "Project sync" in detail, detail)
    r.check("detail duration 30 minutes", "Duration: 30 minutes" in detail, detail)
    r.check("detail reminder 10 minutes", "Reminder: 10 minutes before" in detail,
            detail)
    r.check("detail has 2 attendees", detail.count("@") >= 2, detail)
    r.check("event not on any other day",
            d.eval("return document.querySelectorAll('#grid .slot.new').length") == 1,
            "new cells count")


def run_f04(r, d):
    url = r.base + "/fcc-k/fixtures/test-04-research.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    n0 = r.step("verify notes empty", "value", lambda: d.value("#notesInput"))
    r.check("notes start empty", n0.strip() == "", n0)
    cards = r.step("count source cards", "eval",
                   lambda: d.eval("return document.querySelectorAll('#sources .card').length"))
    r.check("3 source cards", cards == 3, str(cards))
    facts = {}
    for src in ("A", "B", "C"):
        r.step(f"open source {src}", "click", lambda s=src: d.click(f"#src{s}"))
        det = r.step(f"read source {src} detail", "text", lambda: d.text("#detail"))
        r.details[f"source{src}"] = det
        facts[src] = det
        r.check(f"source {src} detail has name", f"Source {src}:" in det, det)
        r.check(f"source {src} detail has price", "Monthly price:" in det, det)
    notes_text = ("Source A: Alpha Service\nSource A: $12/mo\n"
                  "Source B: Beta Service\nSource B: $19/mo\n"
                  "Source C: Gamma Service\nSource C: $9/mo")
    r.step("type 6 fact lines", "type",
           lambda: d.type_text("#notesInput", notes_text))
    summary = "Alpha $12/mo vs Beta $19/mo vs Gamma $9/mo, all differ."
    r.step("type summary", "type", lambda: d.type_text("#summary", summary))
    lines = r.step("count fact lines", "eval",
                   lambda: d.eval("return document.querySelector('#notesInput').value.split('\\n').map(l=>l.trim()).filter(l=>l)"))
    r.details["factLines"] = lines
    r.check("6 fact lines present", len(lines) == 6, str(lines))
    for src in ("A", "B", "C"):
        r.check(f"2 facts with Source {src}",
                sum(1 for l in lines if f"Source {src}" in l) == 2, str(lines))
    r.step("click Save notes", "click", lambda: d.click("#saveBtn"))
    saved = r.step("read saved snapshot", "text", lambda: d.text("#savedNotes"))
    r.details["savedNotes"] = saved
    r.check("saved snapshot present", "Saved notes:" in saved, saved)
    r.check("saved snapshot has summary", summary[:20] in saved, saved)
    r.check("saved snapshot has all 6 facts",
            all(l in saved for l in lines), saved)
    notes_after = r.step("re-read notes after save", "value",
                         lambda: d.value("#notesInput"))
    r.check("notes survive save", notes_after.strip() == notes_text.strip(),
            notes_after)


def run_f05(r, d):
    url = r.base + "/fcc-k/fixtures/test-05-image.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    dl0 = r.step("list downloads", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#dl .file')].map(e=>e.textContent.trim())"))
    r.details["downloadsStart"] = dl0
    r.check("8 files in downloads", len(dl0) == 8, str(dl0))
    r.step("type folder name Organized", "type",
           lambda: d.type_text("#folderName", "Organized"))
    r.step("click New Folder", "click", lambda: d.click("#newFolderBtn"))
    org_vis = r.step("Organized column visible", "visible",
                     lambda: d.visible("#orgCol"))
    r.check("Organized folder created", org_vis, str(org_vis))
    pairs = [("img_01.jpg", "trip-01.jpg"), ("screenshot.png", "trip-02.png"),
             ("photo from web.jpg", "trip-03.jpg"), ("img_04.jpg", "trip-04.jpg"),
             ("img_05.jpg", "trip-05.jpg"), ("img_06.png", "trip-06.png"),
             ("img_07.jpg", "trip-07.jpg"), ("img_08.jpg", "trip-08.jpg")]
    for orig, new in pairs:
        r.step(f"move {orig} to Organized", "click_js",
               lambda: d.click_js("document.querySelector('#dl .file')"))
        dl_now = r.step(f"downloads after moving {orig}", "eval",
                        lambda: d.eval("return [...document.querySelectorAll('#dl .file')].map(e=>e.textContent.trim())"))
        r.check(f"{orig} left downloads", orig not in dl_now, str(dl_now))
        r.step(f"select {orig} in Organized", "click",
               lambda o=orig: d.click(f'#org .file[data-name="{o}"]'))
        sel = r.step(f"read selected file", "text", lambda: d.text("#selected"))
        r.check(f"selected is {orig}", sel == orig, sel)
        r.step(f"type new name {new}", "type",
               lambda n=new: d.type_text("#renameInput", n))
        r.step(f"click Rename for {new}", "click", lambda: d.click("#renameBtn"))
        org_now = r.step(f"Organized after rename to {new}", "eval",
                         lambda: d.eval("return [...document.querySelectorAll('#org .file')].map(e=>e.textContent.trim())"))
        r.check(f"{new} in Organized", new in org_now, str(org_now))
        r.check(f"{orig} gone from Organized", orig not in org_now, str(org_now))
    org = r.step("list Organized final", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#org .file')].map(e=>e.textContent.trim())"))
    r.details["organizedFinal"] = org
    expected = [n for _, n in pairs]
    r.check("Organized has exactly the 8 trip names", sorted(org) == sorted(expected),
            str(org))
    dl1 = r.step("list downloads final", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#dl .file')].map(e=>e.textContent.trim())"))
    r.check("downloads empty", len(dl1) == 0, str(dl1))
    index_text = "\n".join(f"{o} -> {n}" for o, n in pairs)
    r.step("type index.txt 8 lines", "type",
           lambda: d.type_text("#indexInput", index_text))
    r.step("click Save index.txt", "click", lambda: d.click("#saveIndexBtn"))
    saved_idx = r.step("read saved index", "text", lambda: d.text("#indexSaved"))
    r.details["savedIndex"] = saved_idx
    idx_lines = [l for l in saved_idx.split("\n") if l.strip()]
    r.check("index has 8 lines", len(idx_lines) == 8, saved_idx)
    for o, n in pairs:
        r.check(f"index maps {o} -> {n}", f"{o} -> {n}" in saved_idx, saved_idx)
    dl2 = r.step("re-check downloads empty", "eval",
                 lambda: d.eval("return document.querySelectorAll('#dl .file').length"))
    r.check("downloads still empty at end", dl2 == 0, str(dl2))

def run_f06(r, d):
    url = r.base + "/fcc-k/fixtures/test-06-settings.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    ns0 = r.step("read Notes font size", "text", lambda: d.text("#notesSettings"))
    r.check("Notes font starts 14", "14" in ns0, ns0)
    rs0 = r.step("read Reader zoom", "text", lambda: d.text("#readerSettings"))
    r.check("Reader zoom starts 100", "100" in rs0, rs0)
    r.step("open Notes Settings", "click", lambda: d.click("#notesSettingsBtn"))
    r.step("set Notes font to 18", "type",
           lambda: d.type_text("#notesFontInput", "18"))
    r.step("click Notes Apply", "click", lambda: d.click("#notesApply"))
    ns1 = r.step("re-read Notes font size", "text", lambda: d.text("#notesSettings"))
    r.details["notesSettingsAfter"] = ns1
    r.check("Notes font size now 18", ns1.strip() == "font_size: 18", ns1)
    r.step("close Notes settings", "click", lambda: d.click("#notesClose"))
    r.step("open Notes app", "click", lambda: d.click("#notesOpen"))
    ndoc_vis = r.step("Notes sample doc visible", "visible",
                      lambda: d.visible("#notesDoc"))
    r.check("Notes sample doc opens", ndoc_vis, str(ndoc_vis))
    nfont = r.step("read Notes doc font size", "eval",
                   lambda: d.eval("return getComputedStyle(document.querySelector('#notesDocText')).fontSize"))
    r.details["notesDocFont"] = nfont
    r.check("Notes doc renders at 18px", nfont == "18px", str(nfont))
    nlabel = r.step("read Notes doc label", "text", lambda: d.text("#notesDocLabel"))
    r.check("Notes doc label mentions 18", "18" in nlabel, nlabel)
    r.step("open Reader Settings", "click", lambda: d.click("#readerSettingsBtn"))
    r.step("set Reader zoom to 150", "type",
           lambda: d.type_text("#readerZoomInput", "150"))
    r.step("click Reader Apply", "click", lambda: d.click("#readerApply"))
    rs1 = r.step("re-read Reader zoom", "text", lambda: d.text("#readerSettings"))
    r.details["readerSettingsAfter"] = rs1
    r.check("Reader zoom now 150", rs1.strip() == "zoom: 150", rs1)
    r.step("close Reader settings", "click", lambda: d.click("#readerClose"))
    r.step("open Reader app", "click", lambda: d.click("#readerOpen"))
    rdoc_vis = r.step("Reader sample doc visible", "visible",
                      lambda: d.visible("#readerDoc"))
    r.check("Reader sample doc opens", rdoc_vis, str(rdoc_vis))
    rfont = r.step("read Reader doc font size", "eval",
                   lambda: d.eval("return getComputedStyle(document.querySelector('#readerDocText')).fontSize"))
    r.details["readerDocFont"] = rfont
    r.check("Reader doc renders at 24px (150% of 16px)", rfont == "24px", str(rfont))
    rlabel = r.step("read Reader doc label", "text", lambda: d.text("#readerDocLabel"))
    r.check("Reader doc label mentions 150", "150" in rlabel, rlabel)
    ns2 = r.step("re-read Notes setting at end", "text",
                 lambda: d.text("#notesSettings"))
    r.check("Notes font still 18 at end", ns2.strip() == "font_size: 18", ns2)
    rs2 = r.step("re-read Reader setting at end", "text",
                 lambda: d.text("#readerSettings"))
    r.check("Reader zoom still 150 at end", rs2.strip() == "zoom: 150", rs2)
    ndoc2 = r.step("Notes doc still open at end", "visible",
                   lambda: d.visible("#notesDoc"))
    r.check("Notes doc remains open", ndoc2, str(ndoc2))
    rdoc2 = r.step("Reader doc still open at end", "visible",
                   lambda: d.visible("#readerDoc"))
    r.check("Reader doc remains open", rdoc2, str(rdoc2))


def run_f07(r, d):
    url = r.base + "/fcc-k/fixtures/test-07-bug.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    steps = r.step("read written repro steps", "text", lambda: d.text("#reproSteps"))
    r.details["reproSteps"] = steps
    r.check("repro steps mention Toggle", "Toggle" in steps, steps)
    before = r.step("record before value", "text", lambda: d.text("#settingVal"))
    r.details["before"] = before
    r.check("before is enabled", before == "enabled", before)
    r.step("click Toggle setting", "click", lambda: d.click("#toggle"))
    r.step("click Save immediately", "click", lambda: d.click("#save"))
    after = r.step("read after value", "text", lambda: d.text("#settingVal"))
    r.details["after"] = after
    r.check("after reverted to enabled (bug reproduced)", after == "enabled", after)
    r.check("before and after differ from toggled value",
            before == "enabled" and after == "enabled", f"before={before} after={after}")
    r.step("click Save again deliberately", "click", lambda: d.click("#save"))
    after2 = r.step("read after2 value", "text", lambda: d.text("#settingVal"))
    r.details["after2"] = after2
    r.check("after2 is disabled (toggled value sticks)", after2 == "disabled", after2)
    after2b = r.step("re-read setting before typing note", "text",
                     lambda: d.text("#settingVal"))
    r.check("fresh re-read still disabled", after2b == "disabled", after2b)
    note = ("Bug: setting reverts on immediate save. "
            "Before enabled After enabled After2 disabled. "
            "Conclusion: reproduced.")
    r.step("type bug note", "type", lambda: d.type_text("#bugNote", note))
    r.step("click Save note", "click", lambda: d.click("#saveNote"))
    saved = r.step("read saved note", "text", lambda: d.text("#noteSaved"))
    r.details["savedNote"] = saved
    r.check("note saved and present", "No note saved yet" not in saved, saved)
    r.check("note has Before label", "Before" in saved, saved)
    r.check("note has After label", "After" in saved, saved)
    r.check("note has After2 label", "After2" in saved, saved)
    r.check("note mentions before value enabled", "enabled" in saved, saved)
    r.check("note mentions toggled value disabled", "disabled" in saved, saved)
    r.check("note conclusion is reproduced",
            "reproduced" in saved.lower() and "not reproduced" not in saved.lower(),
            saved)
    final = r.step("read final setting value", "text", lambda: d.text("#settingVal"))
    r.check("final setting is disabled", final == "disabled", final)


def run_f08(r, d):
    url = r.base + "/fcc-k/fixtures/test-08-form.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    r.step("type full name", "type", lambda: d.type_text("#fullName", "the owner"))
    r.step("type short password", "type", lambda: d.type_text("#pw", "abcd"))
    r.step("type mismatched confirm", "type", lambda: d.type_text("#pw2", "wxyz"))
    r.step("click Submit (first)", "click", lambda: d.click("#submit"))
    errs1 = r.step("read first-submit errors", "text", lambda: d.text("#errors"))
    r.details["firstErrors"] = errs1
    r.check("first submit shows exactly 3 errors",
            errs1.count("Password") + errs1.count("Email") == 3, errs1)
    r.check("error: Email is required", "Email is required" in errs1, errs1)
    r.check("error: password too short",
            "Password must be at least 8 characters" in errs1, errs1)
    r.check("error: passwords do not match", "Passwords do not match" in errs1,
            errs1)
    r.step("fix Email", "type",
           lambda: d.type_text("#email", "user@example.com"))
    r.step("fix Password to 12 chars", "type",
           lambda: d.type_text("#pw", "password1234"))
    r.step("fix Confirm to match", "type",
           lambda: d.type_text("#pw2", "password1234"))
    r.step("click Submit (second)", "click", lambda: d.click("#submit"))
    errs2 = r.step("read remaining errors", "text", lambda: d.text("#errors"))
    r.details["remainingErrors"] = errs2
    r.check("zero errors remain", errs2.strip() == "", errs2)
    ok = r.step("read success message", "text", lambda: d.text("#ok"))
    r.details["success"] = ok
    r.check("success message shown", "successful" in ok, ok)
    ok_vis = r.step("success message visible", "visible", lambda: d.visible("#ok"))
    r.check("success block visible", ok_vis, str(ok_vis))
    vals = r.step("read back final field values", "eval",
                  lambda: d.eval("return {name: document.querySelector('#fullName').value,"
                                 "email: document.querySelector('#email').value,"
                                 "pwLen: document.querySelector('#pw').value.length,"
                                 "match: document.querySelector('#pw').value === document.querySelector('#pw2').value}"))
    r.details["finalValues"] = vals
    r.check("final name filled", vals["name"] == "the owner", str(vals))
    r.check("final email valid", vals["email"] == "user@example.com", str(vals))
    r.check("final password >= 8 chars", vals["pwLen"] >= 8, str(vals))
    r.check("final passwords match", vals["match"] is True, str(vals))


def run_f09(r, d):
    url = r.base + "/fcc-k/fixtures/test-09-convert.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    header = r.step("read App A header", "eval",
                    lambda: d.eval("return [...document.querySelectorAll('#srcTable tr:first-child th')].map(e=>e.textContent.trim()).join(',')"))
    r.details["header"] = header
    r.check("header is Item, Units, Price", header == "Item,Units,Price", header)
    rows = r.step("read all 4 App A rows", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#srcTable tr')].slice(1).map(tr=>[...tr.querySelectorAll('td')].map(td=>td.textContent.trim()))"))
    r.details["sourceRows"] = rows
    r.check("4 source rows", len(rows) == 4, str(rows))
    r.check("row 1 is Widget 12 45000", rows[0] == ["Widget", "12", "45000"],
            str(rows))
    r.check("row 4 is Cable 20 12000", rows[3] == ["Cable", "20", "12000"],
            str(rows))
    ref = r.step("read reference block", "text", lambda: d.text("#reference"))
    r.details["reference"] = ref
    ref_lines = [l.strip() for l in ref.split("\n") if l.strip()]
    r.check("reference has 4 lines", len(ref_lines) == 4, ref)
    converted = "\n".join(ref_lines)
    r.step("type 4 converted lines into App B", "type",
           lambda: d.type_text("#tgtInput", converted))
    r.step("click Convert / Apply", "click", lambda: d.click("#convert"))
    out = r.step("read converted output", "text", lambda: d.text("#tgt"))
    r.details["convertedOutput"] = out
    out_lines = [l.strip() for l in out.split("\n") if l.strip()]
    r.check("output has exactly 4 lines", len(out_lines) == 4, out)
    for i, line in enumerate(ref_lines):
        r.check(f"line {i + 1} matches reference",
                i < len(out_lines) and out_lines[i] == line,
                f"got={out_lines[i] if i < len(out_lines) else '(missing)'} exp={line}")
    r.check("no extra lines", len(out_lines) == len(ref_lines), out)


def run_f10(r, d):
    url = r.base + "/fcc-k/fixtures/test-10-document.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    vis = r.step("check body visible", "eval", lambda: body_visible(d))
    r.check("body renders visible", vis == "visible", vis)
    secs = r.step("count document sections", "eval",
                  lambda: d.eval("return document.querySelectorAll('#doc section').length"))
    r.check("document has 3 sections", secs == 3, str(secs))
    toc0 = r.step("read TOC count", "text", lambda: d.text("#tocCount"))
    r.check("TOC starts at Tables: 0", "0" in toc0, toc0)
    r.step("open Find/Replace", "click", lambda: d.click("#find"))
    panel = r.step("find panel visible", "visible", lambda: d.visible("#findPanel"))
    r.check("find panel opens", panel, str(panel))
    r.step("type search term old vendor", "type",
           lambda: d.type_text("#findInput", "old vendor"))
    r.step("click Search", "click", lambda: d.click("#searchBtn"))
    mc1 = r.step("read match count", "text", lambda: d.text("#matchCount"))
    r.details["matchCountBefore"] = mc1
    r.check("search finds 3 matches", mc1.startswith("3 matches"), mc1)
    r.step("type replacement new vendor", "type",
           lambda: d.type_text("#replaceInput", "new vendor"))
    r.step("click Replace all", "click", lambda: d.click("#replaceAll"))
    mc2 = r.step("read match count after replace", "text",
                 lambda: d.text("#matchCount"))
    r.details["matchCountAfter"] = mc2
    r.check("0 matches remain after replace", "0 matches" in mc2, mc2)
    r.step("close Find/Replace", "click", lambda: d.click("#findClose"))
    old_left = r.step("verify no old vendor in doc", "eval",
                      lambda: d.eval("return document.getElementById('doc').textContent.includes('old vendor')"))
    r.check("no old vendor remains in document", old_left is False, str(old_left))
    new_present = r.step("verify new vendor in doc", "eval",
                         lambda: d.eval("return document.getElementById('doc').textContent.includes('new vendor')"))
    r.check("new vendor present in document", new_present is True, str(new_present))
    r.step("click Add table", "click", lambda: d.click("#addTable"))
    tbl = r.step("table exists", "eval",
                 lambda: d.eval("return !!document.getElementById('insTable')"))
    r.check("table inserted under Summary", tbl is True, str(tbl))
    for j, h in enumerate(["Column A", "Column B", "Column C"], start=1):
        r.step(f"fill header {h}", "eval",
               lambda jj=j, hh=h: type_contenteditable(
                   d, f"#insTable tr:nth-child(1) th:nth-child({jj})", hh))
    body_vals = [["Widget", "12", "45000"], ["Gadget", "7", "82000"]]
    for i, row in enumerate(body_vals, start=2):
        for j, v in enumerate(row, start=1):
            r.step(f"fill table row {i - 1} col {j}", "eval",
                   lambda ii=i, jj=j, vv=v: type_contenteditable(
                       d, f"#insTable tr:nth-child({ii}) td:nth-child({jj})", vv))
    header = r.step("read table header", "eval",
                    lambda: d.eval("return [...document.querySelectorAll('#insTable tr')[0].querySelectorAll('th')].map(c=>c.textContent.trim())"))
    r.details["tableHeader"] = header
    r.check("header is Column A/B/C", header == ["Column A", "Column B", "Column C"],
            str(header))
    body_rows = r.step("read table body rows", "eval",
                       lambda: d.eval("return [...document.querySelectorAll('#insTable tr')].slice(1).map(tr=>[...tr.querySelectorAll('td')].map(c=>c.textContent.trim()))"))
    r.details["tableBody"] = body_rows
    r.check("2 body rows", len(body_rows) == 2, str(body_rows))
    r.check("body rows non-empty",
            all(c for row in body_rows for c in row), str(body_rows))
    toc1 = r.step("read TOC count after table", "text", lambda: d.text("#tocCount"))
    r.details["tocAfterTable"] = toc1
    r.check("TOC count now Tables: 1", "Tables: 1" in toc1, toc1)
    r.step("click Save", "click", lambda: d.click("#save"))
    saved = r.step("read saved state", "text", lambda: d.text("#savedState"))
    r.check("document saved", "Saved." in saved, saved)
    r.step("click Export", "click", lambda: d.click("#export"))
    exp = r.step("read export view", "text", lambda: d.text("#exportView"))
    r.details["exportView"] = exp
    r.check("export filename is report-export.md",
            "Filename: report-export.md" in exp, exp)
    r.check("export contains new vendor", "new vendor" in exp, exp)
    r.check("export has no old vendor", "old vendor" not in exp, exp)
    r.check("export contains table headers", "Column A" in exp, exp)
    r.check("export contains table rows",
            "Widget" in exp and "Gadget" in exp, exp)


TESTS = {
    "q04": run_q04,
    "f01": run_f01, "f02": run_f02, "f03": run_f03, "f04": run_f04,
    "f05": run_f05, "f06": run_f06, "f07": run_f07, "f08": run_f08,
    "f09": run_f09, "f10": run_f10,
}


def run_one(test_id, base_url):
    fn = TESTS[test_id]
    r = Runner(test_id, base_url)
    try:
        with WD() as d:
            fn(r, d)
    except Exception as exc:
        r.failures.append(f"RUNNER ERROR: {type(exc).__name__}: {exc}")
        print(f"[{test_id}] RUNNER ERROR {exc}", flush=True)
    s = r.summary()
    print("RESULT " + json.dumps(s, ensure_ascii=False), flush=True)
    return s


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: run_fcck.py <q04 | f01..f10 | all>", flush=True)
        return 2
    wanted = list(TESTS) if args == ["all"] else args
    for t in wanted:
        if t not in TESTS:
            print(f"unknown test {t}", flush=True)
            return 2
    httpd, base_url = start_server()
    print(f"serving at {base_url}", flush=True)
    results = []
    try:
        for t in wanted:
            results.append(run_one(t, base_url))
    finally:
        if httpd is not None:
            httpd.shutdown()
    passed = sum(1 for x in results if x["pass"])
    print(f"SUMMARY {passed}/{len(results)} passed, "
          f"total_ms={sum(x['elapsed_ms'] for x in results)}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
