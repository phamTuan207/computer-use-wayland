#!/usr/bin/env python3
"""Test 10, data dashboard: verify a filterable analytics dashboard.

Drives the offline fixture in a real browser. The test reads the
raw dataset JSON out of the page, recomputes every expectation
itself, and then checks the rendered dashboard against it: KPI
cards, table rows, sorting both ways, channel filter with
recomputed KPIs, search, a combined filter plus sort, a date range
that shrinks the view, a CSV export data URI that must match the
current view, and a full restore after clearing the filters.
"""

import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness import BrowserCase, fixture_uri

CHANNEL = "Paid"
SEARCH_TERM = "2026-11-1"


def kpis_for(rows):
    revenue = sum(r["revenue"] for r in rows)
    orders = sum(r["orders"] for r in rows)
    visitors = sum(r["visitors"] for r in rows)
    conversion = f"{orders / visitors * 100:.2f}%" if visitors else "0.00%"
    return {"revenue": str(revenue), "orders": str(orders),
            "visitors": str(visitors), "conversion": conversion}


def main():
    case = BrowserCase("test10", "Data dashboard")
    driver = case.start_browser()
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select

    def by_id(element_id):
        return driver.find_element(By.ID, element_id)

    def read_kpis():
        return {"revenue": by_id("kpiRevenue").text,
                "orders": by_id("kpiOrders").text,
                "visitors": by_id("kpiVisitors").text,
                "conversion": by_id("kpiConversion").text}

    def read_rows():
        rows = []
        for tr in driver.find_elements(By.CSS_SELECTOR, "#tableBody tr"):
            cells = [td.text for td in tr.find_elements(By.TAG_NAME, "td")]
            rows.append({"date": cells[0], "channel": cells[1],
                         "visitors": int(cells[2]), "orders": int(cells[3]),
                         "revenue": int(cells[4])})
        return rows

    case.step("load_fixture", lambda: driver.get(
        fixture_uri("test10_data_dashboard.html")) or {"title": driver.title})
    case.check("page_title", driver.title == "Data Dashboard Fixture",
               driver.title)

    dataset = case.step("read_dataset_json", lambda: json.loads(
        by_id("dataset-json").get_attribute("textContent")))
    case.check("dataset_has_at_least_12_rows", len(dataset) >= 12,
               f"rows={len(dataset)}")
    channels = sorted({r["channel"] for r in dataset})
    case.check("dataset_has_at_least_3_channels", len(channels) >= 3,
               f"channels={channels}")

    expected_all = kpis_for(dataset)
    initial_kpis = case.step("read_initial_kpis", read_kpis)
    case.check("kpi_revenue_matches_dataset_sum",
               initial_kpis["revenue"] == expected_all["revenue"],
               f"card={initial_kpis['revenue']} "
               f"expected={expected_all['revenue']}")
    case.check("kpi_orders_matches_dataset_sum",
               initial_kpis["orders"] == expected_all["orders"],
               f"card={initial_kpis['orders']} "
               f"expected={expected_all['orders']}")
    case.check("kpi_visitors_matches_dataset_sum",
               initial_kpis["visitors"] == expected_all["visitors"],
               f"card={initial_kpis['visitors']} "
               f"expected={expected_all['visitors']}")
    case.check("kpi_conversion_matches_dataset",
               initial_kpis["conversion"] == expected_all["conversion"],
               f"card={initial_kpis['conversion']} "
               f"expected={expected_all['conversion']}")

    initial_rows = case.step("read_initial_table_rows", read_rows)
    case.check("table_row_count_equals_dataset_size",
               len(initial_rows) == len(dataset),
               f"table={len(initial_rows)} dataset={len(dataset)}")
    case.check("row_count_label_full",
               by_id("rowCount").text
               == f"Showing {len(dataset)} of {len(dataset)} rows",
               by_id("rowCount").text)
    case.check("first_row_matches_dataset_order",
               initial_rows[0]["date"] == dataset[0]["date"]
               and initial_rows[0]["revenue"] == dataset[0]["revenue"])

    def click_header(key):
        driver.find_element(
            By.CSS_SELECTOR, f"th[data-sort='{key}']").click()
        return {"indicator": by_id(f"ind-{key}").text}

    desc_click = case.step("sort_revenue_descending",
                           lambda: click_header("revenue"))
    case.check("sort_indicator_desc", desc_click["indicator"] == "(desc)",
               desc_click["indicator"])
    desc_rows = case.step("read_rows_after_desc_sort", read_rows)
    revenues_desc = [r["revenue"] for r in desc_rows]
    case.check("first_row_revenue_is_dataset_max",
               revenues_desc[0] == max(r["revenue"] for r in dataset),
               f"first={revenues_desc[0]}")
    case.check("revenue_column_monotonic_desc",
               revenues_desc == sorted(revenues_desc, reverse=True),
               f"{revenues_desc}")

    asc_click = case.step("sort_revenue_ascending",
                          lambda: click_header("revenue"))
    case.check("sort_indicator_asc", asc_click["indicator"] == "(asc)",
               asc_click["indicator"])
    asc_rows = case.step("read_rows_after_asc_sort", read_rows)
    revenues_asc = [r["revenue"] for r in asc_rows]
    case.check("first_row_revenue_is_dataset_min",
               revenues_asc[0] == min(r["revenue"] for r in dataset),
               f"first={revenues_asc[0]}")
    case.check("revenue_column_monotonic_asc",
               revenues_asc == sorted(revenues_asc),
               f"{revenues_asc}")

    case.step("filter_channel_paid", lambda: Select(
        by_id("channelFilter")).select_by_value(CHANNEL) or CHANNEL)
    channel_rows_data = [r for r in dataset if r["channel"] == CHANNEL]
    filtered_rows = case.step("read_rows_after_channel_filter", read_rows)
    case.check("channel_filter_row_count_recomputed",
               len(filtered_rows) == len(channel_rows_data),
               f"table={len(filtered_rows)} "
               f"expected={len(channel_rows_data)}")
    case.check("all_filtered_rows_match_channel",
               all(r["channel"] == CHANNEL for r in filtered_rows))
    channel_kpis = case.step("read_kpis_after_channel_filter", read_kpis)
    expected_channel = kpis_for(channel_rows_data)
    case.check("channel_kpi_revenue_recomputed",
               channel_kpis["revenue"] == expected_channel["revenue"],
               f"card={channel_kpis['revenue']} "
               f"expected={expected_channel['revenue']}")
    case.check("channel_kpi_orders_recomputed",
               channel_kpis["orders"] == expected_channel["orders"],
               f"card={channel_kpis['orders']} "
               f"expected={expected_channel['orders']}")
    case.check("channel_kpi_conversion_recomputed",
               channel_kpis["conversion"] == expected_channel["conversion"],
               f"card={channel_kpis['conversion']} "
               f"expected={expected_channel['conversion']}")

    def type_search():
        box = by_id("searchBox")
        box.send_keys(SEARCH_TERM)
        return {"value": box.get_attribute("value")}
    case.step("type_search_term", type_search)
    search_expected = [r for r in channel_rows_data
                       if SEARCH_TERM in r["date"]
                       or SEARCH_TERM in r["channel"].lower()]
    search_rows = case.step("read_rows_after_search", read_rows)
    case.check("search_row_count_recomputed",
               len(search_rows) == len(search_expected),
               f"table={len(search_rows)} expected={len(search_expected)}")
    case.check("search_rows_all_match_term_and_channel",
               all(r["channel"] == CHANNEL and SEARCH_TERM in r["date"]
                   for r in search_rows),
               f"{[(r['date'], r['channel']) for r in search_rows]}")

    case.step("clear_search_term",
              lambda: by_id("searchBox").clear() or "cleared")
    combined_click = case.step("sort_visitors_with_channel_filter",
                               lambda: click_header("visitors"))
    case.check("combined_sort_indicator_desc",
               combined_click["indicator"] == "(desc)",
               combined_click["indicator"])
    combined_rows = case.step("read_rows_combined_filter_sort", read_rows)
    combined_visitors = [r["visitors"] for r in combined_rows]
    case.check("combined_rows_all_paid_and_counted",
               all(r["channel"] == CHANNEL for r in combined_rows)
               and len(combined_rows) == len(channel_rows_data),
               f"count={len(combined_rows)}")
    case.check("combined_visitors_monotonic_desc",
               combined_visitors == sorted(combined_visitors, reverse=True),
               f"{combined_visitors}")

    def set_range_last7():
        Select(by_id("channelFilter")).select_by_value("all")
        Select(by_id("rangeSelect")).select_by_value("last7")
        return {"range": by_id("rangeSelect").get_attribute("value")}
    case.step("set_date_range_last7", set_range_last7)
    range_rows = case.step("read_rows_after_range", read_rows)
    expected_dates = sorted(r["date"] for r in dataset[-7:])
    case.check("range_shrinks_to_last_7_entries",
               len(range_rows) == 7
               and sorted(r["date"] for r in range_rows) == expected_dates,
               f"count={len(range_rows)} "
               f"dates={[r['date'] for r in range_rows]}")
    case.check("row_count_label_after_range",
               by_id("rowCount").text
               == f"Showing 7 of {len(dataset)} rows",
               by_id("rowCount").text)

    def read_export():
        href = by_id("exportBtn").get_attribute("href")
        decoded = urllib.parse.unquote(href.split(",", 1)[1])
        return {"href_start": href[:21], "csv": decoded,
                "lines": decoded.strip().split("\n")}
    export = case.step("read_export_csv_href", read_export)
    case.check("export_is_csv_data_uri",
               export["href_start"] == "data:text/csv;charset",
               export["href_start"])
    case.check("export_header_matches",
               export["lines"][0] == "date,channel,visitors,orders,revenue",
               export["lines"][0])
    case.check("export_row_count_matches_current_view",
               len(export["lines"]) - 1 == len(range_rows),
               f"csv_rows={len(export['lines']) - 1} "
               f"view={len(range_rows)}")
    first = range_rows[0]
    expected_first = (f"{first['date']},{first['channel']},"
                      f"{first['visitors']},{first['orders']},"
                      f"{first['revenue']}")
    case.check("export_first_row_matches_table_first_row",
               export["lines"][1] == expected_first,
               f"csv={export['lines'][1]} expected={expected_first}")
    csv_rows = [line.split(",") for line in export["lines"][1:]]
    view_rows = [[r["date"], r["channel"], str(r["visitors"]),
                  str(r["orders"]), str(r["revenue"])]
                 for r in range_rows]
    case.check("export_all_rows_match_current_view",
               csv_rows == view_rows,
               f"csv={csv_rows} view={view_rows}")

    def clear_filters():
        Select(by_id("rangeSelect")).select_by_value("all")
        Select(by_id("channelFilter")).select_by_value("all")
        by_id("searchBox").clear()
        return {"channel": by_id("channelFilter").get_attribute("value"),
                "range": by_id("rangeSelect").get_attribute("value")}
    case.step("clear_all_filters", clear_filters)
    restored_rows = case.step("read_rows_after_clear", read_rows)
    restored_kpis = case.step("read_kpis_after_clear", read_kpis)
    case.check("full_row_count_restored",
               len(restored_rows) == len(dataset),
               f"rows={len(restored_rows)}")
    case.check("kpis_restored_to_dataset_totals",
               restored_kpis == expected_all,
               f"kpis={restored_kpis} expected={expected_all}")
    case.check("row_count_label_restored",
               by_id("rowCount").text
               == f"Showing {len(dataset)} of {len(dataset)} rows",
               by_id("rowCount").text)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
