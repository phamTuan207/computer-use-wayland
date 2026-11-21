#!/usr/bin/env python3
"""Test 09, code review diff, batch 3.

Drives a real offline code review page in a real browser: read the
PR header and status badge, count diff lines by type from the DOM,
toggle context lines, switch files, post two line comments through
the composer, exercise the review submit rules (blocked with no
decision, request changes allowed with comments but no summary),
then submit a second review approving the PR and verify the badge
and the review history. The fixture allows multiple reviews, each
submission appends to the history and moves the badge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import BrowserCase, fixture_uri

COMMENT_1 = "Please cap the retries at 3 and add a backoff."
COMMENT_2 = "This return sits inside the loop, is that intended?"
SUMMARY_2 = "Approving after re-checking the retry logic."


def main():
    case = BrowserCase("test09", "code review diff")
    driver = case.start_browser()
    from selenium.webdriver.common.by import By

    def counts(section_id):
        return driver.execute_script(
            "var s = document.getElementById(arguments[0]);"
            "function n(sel) { return s.querySelectorAll(sel).length; }"
            "return {add: n('.diff-line.add'),"
            " remove: n('.diff-line.remove'),"
            " context: n('.diff-line.context'),"
            " total: n('.diff-line')};", section_id)

    def visible_context(section_id):
        return driver.execute_script(
            "var s = document.getElementById(arguments[0]);"
            "var lines = s.querySelectorAll('.diff-line.context');"
            "var v = 0;"
            "lines.forEach(function (l) {"
            "  if (getComputedStyle(l).display !== 'none') { v++; }"
            "});"
            "return v;", section_id)

    def badge():
        el = driver.find_element(By.ID, "status-badge")
        return {"status": el.get_attribute("data-status"),
                "text": el.text}

    def history():
        return driver.execute_script(
            "return Array.prototype.map.call("
            "document.querySelectorAll('#review-history .review-entry'),"
            "function (e) { return {text: e.textContent,"
            " decision: e.getAttribute('data-decision')}; });")

    def comment_texts(line_id):
        return driver.execute_script(
            "var l = document.getElementById(arguments[0]);"
            "return Array.prototype.map.call("
            "l.querySelectorAll('.line-comments .comment'),"
            "function (e) { return e.textContent; });", line_id)

    def comment_count():
        return int(driver.find_element(By.ID, "comment-count").text)

    try:
        case.step("load_fixture",
                  lambda: (driver.get(fixture_uri(
                      "test09_code_review.html")), driver.title)[1])

        header = case.step("read_header", lambda: {
            "title": driver.find_element(By.ID, "pr-title").text,
            "author": driver.find_element(By.ID, "pr-author").text,
            "badge": badge()})
        case.check("pr_title_exact",
                   header["title"] == "Add retry logic to the payment client",
                   f"title={header['title']!r}")
        case.check("initial_status_open",
                   header["badge"]["status"] == "open"
                   and header["badge"]["text"] == "Open",
                   f"badge={header['badge']}")

        c1 = case.step("count_file1_diff_lines", lambda: counts("file1"))
        case.check("file1_line_counts_by_type",
                   c1 == {"add": 4, "remove": 2, "context": 4, "total": 10},
                   f"counts={c1}")

        case.step("toggle_context_off",
                  lambda: driver.find_element(
                      By.ID, "toggle-context").click())
        vis_off = case.step("count_visible_context_off",
                            lambda: visible_context("file1"))
        case.check("context_lines_hidden", vis_off == 0,
                   f"visible_context={vis_off}")

        case.step("toggle_context_on",
                  lambda: driver.find_element(
                      By.ID, "toggle-context").click())
        vis_on = case.step("count_visible_context_on",
                           lambda: visible_context("file1"))
        case.check("context_lines_restored", vis_on == 4,
                   f"visible_context={vis_on}")

        case.step("switch_to_file2",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".file-tab[data-target='file2']")
                  .click())
        f2 = case.step("verify_file2", lambda: {
            "file2_shown": driver.find_element(By.ID, "file2").is_displayed(),
            "file1_shown": driver.find_element(By.ID, "file1").is_displayed(),
            "name": driver.find_element(
                By.CSS_SELECTOR, "#file2 .file-name").text,
            "line4": driver.find_element(
                By.CSS_SELECTOR, "#f2-l4 .code").text})
        case.check("file2_header_and_known_line",
                   f2["file2_shown"] and not f2["file1_shown"]
                   and f2["name"] == "src/client.py"
                   and "Session(timeout=10)" in f2["line4"],
                   f"file2={f2}")

        case.step("switch_back_to_file1",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".file-tab[data-target='file1']")
                  .click())

        case.step("open_composer_line5",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR,
                      ".line-comment-btn[data-line-id='f1-l5']").click())
        comp = case.step("verify_composer_target", lambda: {
            "shown": driver.find_element(By.ID, "composer").is_displayed(),
            "host_line": driver.execute_script(
                "return document.getElementById('composer')"
                ".closest('.diff-line').id;")})
        case.check("composer_opens_under_line5",
                   comp["shown"] and comp["host_line"] == "f1-l5",
                   f"composer={comp}")

        case.step("type_comment_1",
                  lambda: driver.find_element(
                      By.ID, "composer-text").send_keys(COMMENT_1))
        case.step("post_comment_1",
                  lambda: driver.find_element(
                      By.ID, "composer-post").click())
        got1 = case.step("read_comments_line5",
                         lambda: comment_texts("f1-l5"))
        case.check("comment_1_posted_under_line5", got1 == [COMMENT_1],
                   f"comments={got1}")
        case.check("counter_is_1", comment_count() == 1,
                   f"count={comment_count()}")

        case.step("open_composer_line9",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR,
                      ".line-comment-btn[data-line-id='f1-l9']").click())
        case.step("type_comment_2",
                  lambda: driver.find_element(
                      By.ID, "composer-text").send_keys(COMMENT_2))
        case.step("post_comment_2",
                  lambda: driver.find_element(
                      By.ID, "composer-post").click())
        got2 = case.step("read_comments_line9",
                         lambda: comment_texts("f1-l9"))
        case.check("comment_2_posted_under_line9", got2 == [COMMENT_2],
                   f"comments={got2}")
        case.check("counter_is_2", comment_count() == 2,
                   f"count={comment_count()}")

        case.step("submit_review_no_option",
                  lambda: driver.find_element(
                      By.ID, "submit-review").click())
        blocked = case.step("verify_submit_blocked", lambda: {
            "badge": badge(),
            "history_len": len(history()),
            "error": driver.find_element(By.ID, "review-error").text})
        case.check("submit_without_option_blocked",
                   blocked["badge"]["status"] == "open"
                   and blocked["history_len"] == 0
                   and "Choose" in blocked["error"],
                   f"blocked={blocked}")

        case.step("choose_request_changes",
                  lambda: driver.find_element(
                      By.ID, "decision-request").click())
        case.step("submit_request_changes_empty_summary",
                  lambda: driver.find_element(
                      By.ID, "submit-review").click())
        after_req = case.step("verify_request_submitted", lambda: {
            "badge": badge(), "history": history()})
        case.check("request_changes_allowed_with_comments_no_summary",
                   after_req["badge"]["status"] == "changes_requested"
                   and after_req["badge"]["text"] == "Changes requested",
                   f"badge={after_req['badge']}")
        case.check("history_has_request_entry",
                   len(after_req["history"]) == 1
                   and after_req["history"][0]["decision"] == "request",
                   f"history={after_req['history']}")

        case.step("choose_approve",
                  lambda: driver.find_element(
                      By.ID, "decision-approve").click())
        case.step("write_approval_summary",
                  lambda: driver.find_element(
                      By.ID, "review-summary").send_keys(SUMMARY_2))
        case.step("submit_approval",
                  lambda: driver.find_element(
                      By.ID, "submit-review").click())
        final = case.step("verify_approved", lambda: {
            "badge": badge(), "history": history()})
        case.check("badge_approved_after_second_review",
                   final["badge"]["status"] == "approved"
                   and final["badge"]["text"] == "Approved",
                   f"badge={final['badge']}")
        case.check("history_second_entry_has_summary",
                   len(final["history"]) == 2
                   and final["history"][1]["decision"] == "approve"
                   and SUMMARY_2 in final["history"][1]["text"],
                   f"history={final['history']}")
    except Exception as exc:
        print(f"  test aborted: {type(exc).__name__}: {exc}", flush=True)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
