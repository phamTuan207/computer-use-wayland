#!/usr/bin/env python3
"""Test 01, PDF form fill: complete a simulated PDF application form.

Drives the offline fixture in a real browser: empty submit shows
every validation error, fields are filled one by one while the PDF
preview mirrors the values live, an invalid email is corrected and
its error clears, and a valid submit produces a success panel with
a reference code, a read only summary, and a data URI download
link holding the submitted values.
"""

import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness import BrowserCase, fixture_uri

FULL_NAME = "Nguyen Van An"
BAD_EMAIL = "notanemail"
GOOD_EMAIL = "vanan@example.com"
DOB = "1990-05-15"
COUNTRY = "Japan"
NOTES = "Please contact me by email."
REF_RE = re.compile(r"^REF-[A-Z0-9]{8}$")


def main():
    case = BrowserCase("test01", "PDF form fill")
    driver = case.start_browser()
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select

    def by_id(element_id):
        return driver.find_element(By.ID, element_id)

    def error_fields():
        items = driver.find_elements(By.CSS_SELECTOR, "#errorList li")
        return [li.get_attribute("data-field") for li in items]

    case.step("load_fixture", lambda: driver.get(
        fixture_uri("test01_pdf_form_fill.html")) or {"title": driver.title})
    case.check("page_title", driver.title == "PDF Form Fill Fixture",
               driver.title)

    def initial_state():
        return {"name": by_id("fullName").get_attribute("value"),
                "email": by_id("email").get_attribute("value"),
                "pv_name": by_id("pvFullName").text,
                "pv_country": by_id("pvCountry").text,
                "success_displayed": by_id("successPanel").is_displayed()}
    initial = case.step("verify_initial_empty_state", initial_state)
    case.check("fields_start_empty",
               initial["name"] == "" and initial["email"] == "")
    case.check("preview_placeholders_shown",
               initial["pv_name"] == "(not provided)"
               and initial["pv_country"] == "(not selected)",
               f"pv_name={initial['pv_name']} pv_country={initial['pv_country']}")
    case.check("success_panel_hidden_initially",
               initial["success_displayed"] is False)

    case.step("attempt_submit_empty",
              lambda: by_id("submitBtn").click() or "clicked")
    fields = case.step("read_error_summary_fields", error_fields)
    case.check("error_summary_visible",
               by_id("errorSummary").is_displayed())
    case.check("all_invalid_fields_listed",
               set(fields) == {"fullName", "email", "dob", "country",
                               "accountType", "signature", "agree"},
               f"fields={fields}")
    case.check("success_still_hidden_after_bad_submit",
               by_id("successPanel").is_displayed() is False)

    def fill_name():
        box = by_id("fullName")
        box.send_keys(FULL_NAME)
        return {"preview": by_id("pvFullName").text,
                "errors": error_fields()}
    name_result = case.step("fill_full_name", fill_name)
    case.check("preview_mirrors_full_name",
               name_result["preview"] == FULL_NAME, name_result["preview"])
    case.check("name_error_cleared_live",
               "fullName" not in name_result["errors"],
               f"errors={name_result['errors']}")

    def fill_bad_email():
        box = by_id("email")
        box.send_keys(BAD_EMAIL)
        return {"preview": by_id("pvEmail").text, "errors": error_fields()}
    bad = case.step("fill_invalid_email", fill_bad_email)
    case.check("preview_mirrors_invalid_email", bad["preview"] == BAD_EMAIL)
    case.check("email_error_present_for_invalid_email",
               "email" in bad["errors"], f"errors={bad['errors']}")

    def correct_email():
        box = by_id("email")
        box.clear()
        box.send_keys(GOOD_EMAIL)
        return {"value": box.get_attribute("value"),
                "preview": by_id("pvEmail").text,
                "errors": error_fields()}
    fixed = case.step("correct_email", correct_email)
    case.check("email_value_corrected", fixed["value"] == GOOD_EMAIL)
    case.check("preview_mirrors_corrected_email",
               fixed["preview"] == GOOD_EMAIL)
    case.check("email_error_cleared_after_correction",
               "email" not in fixed["errors"], f"errors={fixed['errors']}")

    def fill_dob():
        box = by_id("dob")
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            box, DOB)
        return {"value": box.get_attribute("value"),
                "preview": by_id("pvDob").text}
    dob_result = case.step("fill_date_of_birth", fill_dob)
    case.check("dob_value_set", dob_result["value"] == DOB,
               dob_result["value"])
    case.check("preview_mirrors_dob", dob_result["preview"] == DOB)

    def pick_country():
        Select(by_id("country")).select_by_visible_text(COUNTRY)
        return {"value": by_id("country").get_attribute("value"),
                "preview": by_id("pvCountry").text}
    country_result = case.step("select_country", pick_country)
    case.check("country_selected", country_result["value"] == COUNTRY)
    case.check("preview_mirrors_country",
               country_result["preview"] == COUNTRY)

    def pick_account_type():
        radio = by_id("acctBusiness")
        radio.click()
        return {"selected": radio.is_selected(),
                "preview": by_id("pvAccountType").text}
    acct = case.step("choose_account_type_business", pick_account_type)
    case.check("business_radio_selected", acct["selected"] is True)
    case.check("preview_mirrors_account_type", acct["preview"] == "Business")

    def fill_notes():
        box = by_id("notes")
        box.send_keys(NOTES)
        return {"preview": by_id("pvNotes").text}
    notes_result = case.step("fill_notes", fill_notes)
    case.check("preview_mirrors_notes", notes_result["preview"] == NOTES)

    def fill_signature():
        box = by_id("signature")
        box.send_keys(FULL_NAME)
        return {"preview": by_id("pvSignature").text}
    sig = case.step("fill_signature", fill_signature)
    case.check("preview_mirrors_signature", sig["preview"] == FULL_NAME)

    def check_agree():
        box = by_id("agree")
        box.click()
        return {"checked": box.is_selected(),
                "preview": by_id("pvAgree").text}
    agree_result = case.step("check_agree_box", check_agree)
    case.check("agree_checked", agree_result["checked"] is True)
    case.check("preview_mirrors_agree", agree_result["preview"] == "Yes")

    def valid_state():
        return {"data_valid": driver.find_element(
                    By.ID, "appForm").get_attribute("data-valid"),
                "submit_enabled": by_id("submitBtn").is_enabled(),
                "errors": error_fields(),
                "error_displayed": by_id("errorSummary").is_displayed()}
    valid = case.step("verify_form_fully_valid", valid_state)
    case.check("form_reports_valid", valid["data_valid"] == "true",
               f"data_valid={valid['data_valid']}")
    case.check("submit_enabled_when_valid", valid["submit_enabled"] is True)
    case.check("no_errors_remain",
               valid["errors"] == [] and valid["error_displayed"] is False,
               f"errors={valid['errors']}")

    case.step("submit_form",
              lambda: by_id("submitBtn").click() or "clicked")
    case.check("success_panel_visible",
               by_id("successPanel").is_displayed())

    ref = case.step("read_reference_code",
                    lambda: by_id("refCode").text.strip())
    case.check("reference_code_format", bool(REF_RE.match(ref)), ref)

    summary = case.step("read_success_summary",
                        lambda: by_id("successSummary").text)
    case.check("summary_has_all_values",
               all(part in summary for part in
                   [FULL_NAME, GOOD_EMAIL, DOB, COUNTRY, "Business",
                    NOTES, ref]),
               summary.replace("\n", " | ")[:200])

    def download_content():
        href = by_id("downloadLink").get_attribute("href")
        return {"href_start": href[:21],
                "decoded": urllib.parse.unquote(href.split(",", 1)[1])}
    download = case.step("read_download_link", download_content)
    case.check("download_is_data_uri",
               download["href_start"] == "data:text/plain;chars",
               download["href_start"])
    case.check("download_contains_submitted_values",
               FULL_NAME in download["decoded"]
               and GOOD_EMAIL in download["decoded"]
               and ref in download["decoded"],
               download["decoded"].replace("\n", " | ")[:200])

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
