#!/usr/bin/env python3
"""Live Zen runner for the 5 agy-q realistic tests (Worker R, 21/11/2026).

Runs tests/realistic/agy-q/test-01..05 against the LIVE Zen on the
laptop via geckodriver --connect-existing (Marionette 2828), reusing the
proven driver from tests/realistic/run_live.py (Worker P):
- explicit tab switch after window/new (window/new does NOT switch),
- ~1s settle after navigation, 0.5s after switch, no maximize,
- one WebDriver session per test, always deleted in a finally block,
- end states verified by reading the DOM directly. The fixtures'
  window.__agyVerify() hooks are NEVER used as oracles (same reason as
  P's fcc-k finding: a checker that can write its own expected state
  proves nothing; here they are only cross-checked after the DOM
  verdict, never trusted for it).

Selects are set via JS value + change event (same as P); everything
else is driven through real Marionette clicks / keystrokes.

Usage (on the laptop, from /tmp/worker-r-server):
  LIVE_SERVER_ROOT=/tmp/worker-r-server LIVE_SERVER_PORT=8766 \
  LIVE_LOG=/tmp/worker-r-live.jsonl WD_PORT=4446 \
  python3 run_agyq.py all
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, Runner, start_server  # noqa: E402

TEST_PREFIX = "agyq"


def click_by_text(d, scope_css, text):
    """Click the first element under scope_css whose text contains text."""
    return d.eval(
        "const els=[...document.querySelectorAll(arguments[0])];"
        "const el=els.find(e=>e.textContent.includes(arguments[1]));"
        "if(!el) return 'NOT-FOUND'; el.click();"
        "return 'clicked: '+el.textContent.trim().slice(0,60);",
        [scope_css, text])


def select_option(d, css, value):
    """Set a <select> value and fire change (same approach as P)."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def clear_search(d, css):
    """Clear a search input and fire input so the filter re-renders."""
    return d.eval(
        "const el=document.querySelector(arguments[0]); el.value='';"
        "el.dispatchEvent(new Event('input',{bubbles:true})); return 'cleared';",
        [css])


def press_enter(d, css):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));"
        "return 'enter';", [css])


def select_by_text(d, css, text):
    """Select the <option> whose visible text matches, by its real value.

    Needed when option values are ids, not display names (q02 batch
    target album: value is the album id; setting .value to the album
    NAME silently selects nothing and the batch add no-ops).
    """
    return d.eval(
        "const sel=document.querySelector(arguments[0]);"
        "const opt=[...sel.options].find(o=>o.textContent.trim()===arguments[1]);"
        "if(!opt) return 'NOT-FOUND'; sel.value=opt.value;"
        "sel.dispatchEvent(new Event('change',{bubbles:true}));"
        "return 'selected value='+opt.value;", [css, text])


def norm(s):
    """Collapse all whitespace so multi-line renders compare sanely."""
    return " ".join((s or "").split())


def click_note_by_title(d, title):
    """Click a q04 sidebar note by its TITLE text only.

    Matching the whole .note-item text is wrong: a note's body snippet
    can contain another note's title (e.g. the RFC note snippet contains
    'Security Model'), so a text-contains match picks the wrong note.
    """
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


def append_text(d, css, text):
    """Type without clearing: focus, caret to end, send keys."""
    d.eval(
        "const el=document.querySelector(arguments[0]); el.focus();"
        "el.setSelectionRange(el.value.length, el.value.length);",
        [css])
    el = d.find(css)
    d._wd("POST", d._s(f"/element/{el}/value"), {"text": text})
    return "appended"


def playlist_order(d):
    return d.eval(
        "return [...document.querySelectorAll('#playlist-table-body tr')]"
        ".map(tr=>tr.textContent.trim().replace(/\\s+/g,' '))")


def playlist_titles(d):
    return d.eval(
        "return [...document.querySelectorAll('#playlist-table-body tr td:nth-child(2) strong')]"
        ".map(td=>td.textContent.trim())")


# ---------------- agy-q tests ----------------

def run_q01(r, d):
    url = r.base + "/agy-q/fixtures/test-01-music-player.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    n = r.step("count library tracks", "eval",
               lambda: d.eval("return document.querySelectorAll('#library-table-body tr').length"))
    r.details["libraryTracks"] = n
    r.check("library shows 12 tracks", n == 12, str(n))
    side = r.step("read sidebar playlists", "text", lambda: d.text("#playlist-list"))
    r.details["sidebarPlaylists"] = side
    r.check("sidebar has Favorites", "Favorites" in side, side)
    r.check("sidebar has Recently Played", "Recently Played" in side, side)
    r.step("click New Playlist", "click", lambda: d.click("#btn-new-playlist"))
    r.step("type playlist name", "type",
           lambda: d.type_text("#input-playlist-name", "Deep Work 2026"))
    r.step("click Create", "click", lambda: d.click("#btn-create-playlist"))
    side2 = r.step("re-read sidebar", "text", lambda: d.text("#playlist-list"))
    r.check("Deep Work 2026 in sidebar", "Deep Work 2026" in side2, side2)
    active = r.step("check active playlist", "eval",
                    lambda: d.eval(
                        "const el=[...document.querySelectorAll('#playlist-list *')]"
                        ".find(e=>e.textContent.includes('Deep Work 2026'));"
                        "return el ? el.className : 'NOT-FOUND'"))
    r.details["activePlaylistClass"] = active
    r.check("new playlist is active", "active" in str(active), str(active))
    adds = [("Neon Horizon", "#add-track-1"), ("Midnight Pulse", "#add-track-3"),
            ("Coffee Beans", "#add-track-5"), ("Solar Winds", "#add-track-7")]
    for query, btn in adds:
        r.step(f"search {query}", "type",
               lambda q=query: d.type_text("#input-library-search", q))
        r.step(f"wait {query} row", "wait",
               lambda b=btn: d.wait_for(
                   f"document.querySelector('{b}')", 10, f"{b} present"))
        r.step(f"add {query}", "click", lambda b=btn: d.click(b))
    r.step("clear search", "eval",
           lambda: clear_search(d, "#input-library-search"))
    r.step("add Rainy Window by mistake", "click", lambda: d.click("#add-track-8"))
    rows = r.step("read playlist rows", "eval", lambda: playlist_titles(d))
    r.details["playlistAfterMistake"] = rows
    r.check("5 tracks after mistake add", len(rows) == 5, str(rows))
    dur = r.step("read duration summary", "text",
                 lambda: d.text("#playlist-duration-summary"))
    r.details["durationAfterMistake"] = dur
    r.check("duration shows 19:10 after mistake", "19:10" in dur, dur)
    r.step("remove Rainy Window", "click",
           lambda: d.click('[data-action="remove-8"]'))
    rows2 = r.step("read playlist after remove", "eval", lambda: playlist_titles(d))
    r.details["playlistAfterRemove"] = rows2
    r.check("4 tracks after remove", len(rows2) == 4, str(rows2))
    r.check("Rainy Window gone", "Rainy Window" not in " | ".join(rows2),
            str(rows2))
    dur2 = r.step("read duration after remove", "text",
                  lambda: d.text("#playlist-duration-summary"))
    r.details["durationAfterRemove"] = dur2
    r.check("duration shows 15:40 after remove", "15:40" in dur2, dur2)
    for i in range(3):
        r.step(f"move Solar Winds up {i + 1}/3", "click",
               lambda: d.click('[data-action="up-7"]'))
    order1 = r.step("read order after Solar up x3", "eval",
                    lambda: playlist_titles(d))
    r.details["orderAfterSolarUp"] = order1
    r.check("order Solar, Neon, Midnight, Coffee",
            order1 == ["Solar Winds", "Neon Horizon", "Midnight Pulse",
                       "Coffee Beans"], str(order1))
    r.step("move Coffee Beans up once", "click",
           lambda: d.click('[data-action="up-5"]'))
    order2 = r.step("read final order", "eval", lambda: playlist_titles(d))
    r.details["finalOrder"] = order2
    r.check("final order Solar, Neon, Coffee, Midnight",
            order2 == ["Solar Winds", "Neon Horizon", "Coffee Beans",
                       "Midnight Pulse"], str(order2))
    r.step("click Save Playlist", "click", lambda: d.click("#btn-save-playlist"))
    banner = r.step("read save banner", "text",
                    lambda: d.text("#save-status-banner"))
    r.details["saveBanner"] = banner
    r.check("banner confirms save",
            banner == "Playlist Deep Work 2026 saved successfully (4 tracks, 15:40)",
            banner)


def run_q02(r, d):
    url = r.base + "/agy-q/fixtures/test-02-photo-gallery.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    n = r.step("count gallery cards", "eval",
               lambda: d.eval("return document.querySelectorAll('#gallery-grid > *').length"))
    r.details["galleryCards"] = n
    r.check("gallery shows 12 cards", n == 12, str(n))
    side = r.step("read sidebar", "text", lambda: d.text("#sidebar"))
    r.details["sidebarStart"] = side
    r.check("sidebar shows All Photos (12)", "All Photos 12" in norm(side), side)
    r.step("click New Album", "click", lambda: d.click("#btn-new-album"))
    r.step("type album name", "type",
           lambda: d.type_text("#input-album-name", "Tokyo Architecture"))
    r.step("click Create Album", "click", lambda: d.click("#btn-confirm-album"))
    albums = r.step("read albums list", "text", lambda: d.text("#albums-list"))
    r.details["albumsAfterCreate"] = albums
    r.check("Tokyo Architecture in albums", "Tokyo Architecture" in albums, albums)
    r.check("new album count 0", "(0)" in albums, albums)
    r.step("filter location Tokyo", "select",
           lambda: select_option(d, "#select-location-filter", "Tokyo"))
    n2 = r.step("count Tokyo cards", "eval",
                lambda: d.eval("return document.querySelectorAll('#gallery-grid > *').length"))
    r.details["tokyoCards"] = n2
    r.check("6 Tokyo photos", n2 == 6, str(n2))
    tokyo_ids = r.step("read Tokyo card ids", "eval",
                       lambda: d.eval(
                           "return [...document.querySelectorAll('#gallery-grid [id^=\"chk-photo-\"]')]"
                           ".map(e=>e.id)"))
    r.details["tokyoIds"] = tokyo_ids
    r.check("Tokyo ids 101,103,104,105,107,108",
            sorted(tokyo_ids) == ["chk-photo-101", "chk-photo-103", "chk-photo-104",
                                  "chk-photo-105", "chk-photo-107", "chk-photo-108"],
            str(tokyo_ids))
    for pid in (101, 104, 108):
        r.step(f"check photo {pid}", "click", lambda p=pid: d.click(f"#chk-photo-{p}"))
    bar = r.step("read batch bar", "text", lambda: d.text("#batch-actions-bar"))
    r.details["batchBar"] = bar
    r.check("batch bar shows 3 photos selected", "3 photos selected" in bar, bar)
    r.step("select target album", "select",
           lambda: select_by_text(d, "#select-batch-target-album",
                                  "Tokyo Architecture"))
    r.step("click Add to Album", "click", lambda: d.click("#btn-batch-add-album"))
    albums2 = r.step("re-read albums list", "text", lambda: d.text("#albums-list"))
    r.details["albumsAfterAdd"] = albums2
    r.check("album count now 3", "Tokyo Architecture (3)" in norm(albums2), albums2)
    r.step("reset location filter", "select",
           lambda: select_option(d, "#select-location-filter", ""))
    r.step("open photo 108 card", "click_js",
           lambda: click_by_text(d, "#gallery-grid .photo-card", "Roppongi Tower"))
    modal = r.step("check details modal visible", "visible",
                   lambda: d.visible("#modal-photo-details"))
    r.details["detailsModalVisible"] = modal
    r.check("photo details modal opens", modal, str(modal))
    r.step("remove tag nature", "click", lambda: d.click("#btn-remove-tag-nature"))
    r.step("type new tag night", "type",
           lambda: d.type_text("#input-new-tag", "night"))
    r.step("click Add Tag", "click", lambda: d.click("#btn-add-tag"))
    tags = r.step("read modal tags", "text", lambda: d.text("#modal-tags-container"))
    r.details["tagsAfterEdit"] = tags
    r.check("tags are architecture, skyline, night",
            all(t in tags for t in ("architecture", "skyline", "night")), tags)
    r.check("nature tag gone", "nature" not in tags, tags)
    r.step("click Save & Close", "click", lambda: d.click("#btn-save-photo-details"))
    r.step("search tag night", "type",
           lambda: d.type_text("#input-tag-search", "night"))
    r.step("press Enter in tag search", "eval",
           lambda: press_enter(d, "#input-tag-search"))
    night_ids = r.step("read night search ids", "eval",
                       lambda: d.eval(
                           "return [...document.querySelectorAll('#gallery-grid [id^=\"chk-photo-\"]')]"
                           ".map(e=>e.id)"))
    r.details["nightSearchIds"] = night_ids
    r.check("night search shows exactly 3 photos", len(night_ids) == 3, str(night_ids))
    r.check("night ids are 102, 106, 108",
            sorted(night_ids) == ["chk-photo-102", "chk-photo-106", "chk-photo-108"],
            str(night_ids))
    r.step("check photo 102", "click", lambda: d.click("#chk-photo-102"))
    r.step("select target album again", "select",
           lambda: select_by_text(d, "#select-batch-target-album",
                                  "Tokyo Architecture"))
    r.step("click Add to Album again", "click", lambda: d.click("#btn-batch-add-album"))
    r.step("clear tag search", "eval",
           lambda: clear_search(d, "#input-tag-search"))
    r.step("open Tokyo Architecture album", "click_js",
           lambda: click_by_text(d, "#albums-list .nav-item", "Tokyo Architecture"))
    album_ids = r.step("read album view ids", "eval",
                       lambda: d.eval(
                           "return [...document.querySelectorAll('#gallery-grid [id^=\"chk-photo-\"]')]"
                           ".map(e=>e.id)"))
    r.details["albumViewIds"] = album_ids
    r.check("album view shows exactly 4 photos", len(album_ids) == 4, str(album_ids))
    r.check("album ids are 101, 104, 108, 102",
            sorted(album_ids) == ["chk-photo-101", "chk-photo-102", "chk-photo-104",
                                  "chk-photo-108"], str(album_ids))
    r.step("click Export Album JSON", "click", lambda: d.click("#btn-export-album"))
    banner = r.step("read export banner", "text",
                    lambda: d.text("#export-status-banner"))
    r.details["exportBanner"] = banner
    r.check("export banner confirms 4 records",
            banner == "Exported 4 photo records successfully", banner)


def run_q03(r, d):
    url = r.base + "/agy-q/fixtures/test-03-rss-reader.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    badge0 = r.step("read global unread badge", "text",
                    lambda: d.text("#badge-global-unread"))
    r.details["initialUnread"] = badge0
    r.check("initial unread badge is 6", badge0.strip() == "6", badge0)
    tree = r.step("read feed tree", "text", lambda: d.text("#feed-categories-tree"))
    r.details["feedTreeStart"] = tree
    r.check("tree has Linux Weekly", "Linux Weekly" in tree, tree)
    r.check("tree has Rust Digest", "Rust Digest" in tree, tree)
    r.step("click Subscribe", "click", lambda: d.click("#btn-add-feed"))
    r.step("type feed title", "type",
           lambda: d.type_text("#input-feed-title", "Wayland Gazette"))
    r.step("type feed url", "type",
           lambda: d.type_text("#input-feed-url", "https://wayland.local/feed.xml"))
    r.step("select category Display Servers", "select",
           lambda: select_option(d, "#select-feed-category", "Display Servers"))
    r.step("click Add Subscription", "click", lambda: d.click("#btn-confirm-feed"))
    tree2 = r.step("re-read feed tree", "text", lambda: d.text("#feed-categories-tree"))
    r.details["feedTreeAfterAdd"] = tree2
    r.check("category Display Servers exists", "Display Servers" in tree2, tree2)
    r.check("Wayland Gazette (3) in tree",
            "Wayland Gazette (3)" in norm(tree2), tree2)
    badge1 = r.step("read badge after subscribe", "text",
                    lambda: d.text("#badge-global-unread"))
    r.details["unreadAfterSubscribe"] = badge1
    r.check("badge updates to 9", badge1.strip() == "9", badge1)
    r.step("open Wayland Gazette feed", "click_js",
           lambda: click_by_text(d, "#feed-categories-tree .feed-item",
                                 "Wayland Gazette"))
    rows = r.step("read article rows", "eval",
                  lambda: d.eval(
                      "return [...document.querySelectorAll('#articles-list-container .article-row')]"
                      ".map(e=>e.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["gazetteRows"] = rows
    r.check("3 articles in feed", len(rows) == 3, str(rows))
    unread_rows = r.step("count unread rows", "eval",
                         lambda: d.eval(
                             "return document.querySelectorAll('#articles-list-container .article-row.unread').length"))
    r.check("all 3 articles unread", unread_rows == 3, str(unread_rows))
    r.step("open article 201", "click_js",
           lambda: click_by_text(d, "#articles-list-container .article-row",
                                 "Explicit Sync Lands in Mainline"))
    body = r.step("read reader pane", "text", lambda: d.text("#reader-content-body"))
    r.details["readerBody201"] = body[:200]
    r.check("reader shows article 201 content",
            "Explicit Sync" in body or "sync" in body.lower(), body[:200])
    tree3 = r.step("re-read feed tree after read", "text",
                   lambda: d.text("#feed-categories-tree"))
    r.check("Wayland Gazette unread now 2",
            "Wayland Gazette (2)" in norm(tree3), tree3)
    r.step("click Star button", "click", lambda: d.click("#btn-star-article"))
    starred = r.step("check star class", "eval",
                     lambda: d.eval(
                         "return document.querySelector('#btn-star-article').className"))
    r.details["starClass"] = starred
    r.check("star button highlighted", "starred" in str(starred), str(starred))
    r.step("open article 202", "click_js",
           lambda: click_by_text(d, "#articles-list-container .article-row",
                                 "Fractional Scaling Best Practices"))
    tree4 = r.step("re-read tree after 202 read", "text",
                   lambda: d.text("#feed-categories-tree"))
    r.check("Wayland Gazette unread now 1",
            "Wayland Gazette (1)" in norm(tree4), tree4)
    r.step("toggle 202 back to unread", "click", lambda: d.click("#btn-toggle-read"))
    tree5 = r.step("re-read tree after toggle", "text",
                   lambda: d.text("#feed-categories-tree"))
    r.details["treeAfterToggle"] = tree5
    r.check("Wayland Gazette unread back to 2",
            "Wayland Gazette (2)" in norm(tree5), tree5)
    row202_unread = r.step("check 202 row unread again", "eval",
                           lambda: d.eval(
                               "const rows=[...document.querySelectorAll('#articles-list-container .article-row')];"
                               "const row=rows.find(e=>e.textContent.includes('Fractional Scaling'));"
                               "return row ? row.className : 'NOT-FOUND'"))
    r.check("article 202 row regains unread class", "unread" in str(row202_unread),
            str(row202_unread))
    r.step("click All Articles", "click", lambda: d.click("#nav-all-articles"))
    all_n = r.step("count all articles", "eval",
                   lambda: d.eval(
                       "return document.querySelectorAll('#articles-list-container .article-row').length"))
    r.details["allArticles"] = all_n
    r.check("9 articles total", all_n == 9, str(all_n))
    r.step("click Mark All As Read", "click", lambda: d.click("#btn-mark-all-read"))
    badge2 = r.step("read badge after mark all", "text",
                    lambda: d.text("#badge-global-unread"))
    r.details["unreadAfterMarkAll"] = badge2
    r.check("badge drops to 0", badge2.strip() == "0", badge2)
    unread_left = r.step("count unread rows left", "eval",
                         lambda: d.eval(
                             "return document.querySelectorAll('#articles-list-container .article-row.unread').length"))
    r.check("no unread rows left", unread_left == 0, str(unread_left))
    r.step("click Starred nav", "click", lambda: d.click("#nav-starred-articles"))
    starred_rows = r.step("read starred rows", "eval",
                          lambda: d.eval(
                              "return [...document.querySelectorAll('#articles-list-container .article-row')]"
                              ".map(e=>e.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["starredRows"] = starred_rows
    r.check("starred view shows exactly 1 item", len(starred_rows) == 1,
            str(starred_rows))
    r.check("starred item is article 201",
            starred_rows and "Explicit Sync Lands in Mainline" in starred_rows[0],
            str(starred_rows))
    r.step("click Export Starred", "click", lambda: d.click("#btn-export-starred"))
    # NOTE: #export-markdown-content is a <textarea>: its content is in
    # .value, not .textContent. Reading .text returns "" even when the
    # export worked (first-run false FAIL, 21/11).
    md = r.step("read export markdown", "value",
                lambda: d.value("#export-markdown-content"))
    r.details["exportMarkdown"] = md
    r.check("export contains article 201 markdown link",
            "- [Explicit Sync Lands in Mainline](https://wayland.local/art-201)" in md,
            md)
    r.step("close export modal", "click", lambda: d.click("#btn-close-export-modal"))


def run_q04(r, d):
    url = r.base + "/agy-q/fixtures/test-04-notes-app.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
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
    # FIXTURE BUG (proven by probe 21/11, see report): renderPreview()
    # has double-escaped regexes (/\\[\\[.../ and /\\n\\n/), so the
    # [[WikiLink]] markup and paragraph breaks NEVER render. The preview
    # shows the raw [[Storage Engine]] text and no <a> element exists,
    # so spec steps 9-10 (click the rendered wiki link) CANNOT run as
    # written. Record the defect, then continue the flow via the sidebar
    # (which is the same navigation, minus the broken link rendering).
    # The backlink DATA (body includes [[...]]) still works and is
    # verified below at data level.
    r.step("switch to Preview tab", "click", lambda: d.click("#tab-preview-mode"))
    preview_html = r.step("read preview HTML", "eval",
                          lambda: d.eval(
                              "return document.querySelector('#rendered-markdown-content').innerHTML"))
    r.details["previewHtml"] = preview_html
    link_present = r.step("check wiki link rendered", "eval",
                          lambda: d.eval(
                              "return !!document.querySelector('[id=\"link-note-Storage Engine\"]')"))
    r.details["wikiLinkRendered"] = link_present
    r.check("FIXTURE BUG: wiki link renders in preview (see report)",
            link_present is True,
            "preview shows raw [[Storage Engine]] text, no <a> element; "
            "renderPreview regexes are double-escaped in the fixture")
    r.step("open Storage Engine via sidebar", "click_js",
           lambda: click_note_by_title(d, "Storage Engine"))
    title = r.step("read current note title", "value",
                   lambda: d.value("#input-note-title"))
    r.details["titleAfterSidebarNav"] = title
    r.check("navigated to Storage Engine", title == "Storage Engine", str(title))
    bl = r.step("read backlinks box", "text", lambda: d.text("#box-backlinks"))
    r.details["backlinksStorageEngine"] = bl
    r.check("backlink shows Memory Tiering RFC", "Memory Tiering RFC" in bl, bl)
    r.step("switch to Edit tab", "click", lambda: d.click("#tab-edit-mode"))
    r.step("append reciprocal link", "append",
           lambda: append_text(d, "#textarea-note-body",
                               "\n\nReference: [[Memory Tiering RFC]]."))
    r.step("click Save Note again", "click", lambda: d.click("#btn-save-note"))
    r.step("click Pin Note", "click", lambda: d.click("#btn-pin-note"))
    side = r.step("read sidebar after pin", "text", lambda: d.text("#sidebar"))
    r.details["sidebarAfterPin"] = side
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
    # Reciprocal backlink: re-open the new note and read its backlinks.
    r.step("re-open Memory Tiering RFC", "click_js",
           lambda: click_note_by_title(d, "Memory Tiering RFC"))
    bl2 = r.step("read backlinks of new note", "text", lambda: d.text("#box-backlinks"))
    r.details["backlinksNewNote"] = bl2
    r.check("reciprocal backlink shows Storage Engine",
            "Storage Engine" in bl2, bl2)


def run_q05(r, d):
    url = r.base + "/agy-q/fixtures/test-05-file-search.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    body = r.step("read page text", "eval",
                  lambda: d.eval("return document.body.innerText"))
    r.details["pageTextHead"] = body[:300]
    r.check("tree reports 15 files indexed", "Results (15)" in body,
            body[:300])
    checked = r.step("check Filename radio selected", "eval",
                     lambda: d.eval(
                         "return document.querySelector('#radio-search-name').checked"))
    r.details["filenameRadioChecked"] = checked
    r.check("default search mode is Filename", checked is True, str(checked))
    r.step("search compositor", "type",
           lambda: d.type_text("#input-file-search", "compositor"))
    rows = r.step("read filename results", "eval",
                  lambda: d.eval(
                      "return [...document.querySelectorAll('#results-table-body tr')]"
                      ".map(tr=>tr.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["filenameResults"] = rows
    r.check("filename search returns 2 files", len(rows) == 2, str(rows))
    # Row text is "filename folder ext" columns, e.g. "compositor.rs src/ .rs".
    r.check("results are compositor.rs + compositor.json",
            any("compositor.rs" in x for x in rows) and
            any("compositor.json" in x for x in rows), str(rows))
    # NOTE: Marionette cannot click a <tr> directly here ("could not be
    # scrolled into view", first run 21/11). Click the filename <td>
    # instead; the row's onclick fires on the bubbled click.
    r.step("click config/compositor.json row", "click",
           lambda: d.click("#row-file-6 td:nth-child(2)"))
    preview = r.step("read preview pane", "text", lambda: d.text("#preview-content-area"))
    r.details["previewHead"] = preview[:200]
    r.check("preview renders JSON content", "{" in preview and "}" in preview,
            preview[:200])
    fname = r.step("read preview filename", "text", lambda: d.text("#preview-filename"))
    r.check("preview filename is config/compositor.json",
            "config/compositor.json" in fname, fname)
    r.step("switch to Search by Content", "click",
           lambda: d.click("#radio-search-content"))
    r.step("search socket_path", "type",
           lambda: d.type_text("#input-file-search", "socket_path"))
    rows2 = r.step("read content results", "eval",
                   lambda: d.eval(
                       "return [...document.querySelectorAll('#results-table-body tr')]"
                       ".map(tr=>tr.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["contentResults"] = rows2
    r.check("content search returns 3 files", len(rows2) == 3, str(rows2))
    r.check("content results are server.rs, compositor.json, launch.sh",
            any("server.rs" in x for x in rows2) and
            any("compositor.json" in x for x in rows2) and
            any("launch.sh" in x for x in rows2), str(rows2))
    r.step("filter extension .json", "select",
           lambda: select_option(d, "#select-ext-filter", ".json"))
    rows3 = r.step("read filtered results", "eval",
                   lambda: d.eval(
                       "return [...document.querySelectorAll('#results-table-body tr')]"
                       ".map(tr=>tr.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["jsonFiltered"] = rows3
    r.check("extension filter isolates 1 result", len(rows3) == 1, str(rows3))
    r.check("isolated result is config/compositor.json",
            rows3 and "compositor.json" in rows3[0] and "config/" in rows3[0],
            str(rows3))
    r.step("click Rename File", "click", lambda: d.click("#btn-rename-file"))
    r.step("type new filename", "type",
           lambda: d.type_text("#input-new-filename", "wayland-compositor.json"))
    r.step("click Confirm Rename", "click", lambda: d.click("#btn-confirm-rename"))
    banner = r.step("read rename banner", "text",
                    lambda: d.text("#status-rename-banner"))
    r.details["renameBanner"] = banner
    r.check("banner confirms rename",
            banner == "File config/compositor.json renamed to config/wayland-compositor.json",
            banner)
    r.step("reset extension filter", "select",
           lambda: select_option(d, "#select-ext-filter", ""))
    r.step("switch back to Filename search", "click",
           lambda: d.click("#radio-search-name"))
    r.step("search wayland-compositor", "type",
           lambda: d.type_text("#input-file-search", "wayland-compositor"))
    rows4 = r.step("read post-rename results", "eval",
                   lambda: d.eval(
                       "return [...document.querySelectorAll('#results-table-body tr')]"
                       ".map(tr=>tr.textContent.trim().replace(/\\s+/g,' '))"))
    r.details["postRenameResults"] = rows4
    r.check("post-rename search returns exactly 1 result", len(rows4) == 1,
            str(rows4))
    r.check("renamed file in index",
            rows4 and "wayland-compositor.json" in rows4[0] and "config/" in rows4[0],
            str(rows4))
    r.step("click renamed row", "click_js",
           lambda: click_by_text(d, "#results-table-body tr",
                                 "wayland-compositor.json"))
    r.step("click Open in Editor", "click", lambda: d.click("#btn-open-file"))
    status = r.step("read editor status", "text",
                    lambda: d.text("#status-open-indicator"))
    r.details["editorStatus"] = status
    r.check("editor status names renamed file",
            status == "Active in editor: config/wayland-compositor.json", status)
    r.step("check renamed file checkbox", "click", lambda: d.click("#chk-file-6"))
    # NOTE: batch-action option values are ids (ro/rw), not display names.
    r.step("select Mark Read-Only action", "select",
           lambda: select_by_text(d, "#select-batch-action", "Mark Read-Only"))
    r.step("click Apply Action", "click", lambda: d.click("#btn-apply-batch"))
    badge = r.step("read preview RO badge", "text", lambda: d.text("#preview-badge-ro"))
    r.details["roBadge"] = badge
    # SPEC BUG (noted, not faked): the spec says the badge displays
    # "[RO]", but the fixture sets textContent to exactly "RO"
    # (fixture line 266: f.readOnly ? 'RO' : 'RW'). The read-only state
    # itself is proven by the audit summary below ("Read-Only Files: 1").
    r.check("preview badge shows RO (spec says [RO], fixture shows RO)",
            badge.strip() == "RO", badge)
    r.step("click Export Search Audit", "click", lambda: d.click("#btn-export-audit"))
    audit = r.step("read audit summary", "text", lambda: d.text("#audit-summary-line"))
    r.details["auditSummary"] = audit
    r.check("audit summary matches",
            audit == "Renamed: 1, Active Editor: config/wayland-compositor.json, Read-Only Files: 1",
            audit)
    r.step("close audit modal", "click", lambda: d.click("#btn-close-audit-modal"))


TESTS = {
    "q01": run_q01, "q02": run_q02, "q03": run_q03, "q04": run_q04,
    "q05": run_q05,
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
        print("usage: run_agyq.py <q01..q05 | all>", flush=True)
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
