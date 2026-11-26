#!/usr/bin/env python3
"""Regression tests for rung3-ci/tier-a-check.py (R5, 2026-11-27).

Covers the formats that produced Tier A false negatives in R3-L3 and
forced tiebreakers or scorer overrides:

- json-errors: Vietnamese and English error-position forms
  (bilingual union fixed 2026-11-25; these tests lock it in).
- R3-021 (sql-order-total): headerless quoted CSV counted as if it
  had a header row; with-header CSV must keep working.
- R3-072 (image-sizes): pipe-separated table rows
  ("1 | d72-anh-1.png | 800 x 600") and numbered dash rows.
- R3-076 (report-consistency): section labels "Free on /:" and
  "Free (free column):" plus pipe-separated process rows.
- DP-02 (keyword-counts): the task brief requires only the 5-row
  summary table, grand total and files-with-keyword count; the
  per-file detail block is optional as a whole (the fixture recount
  already verifies the per-file matrix). Detail lines without the
  "(N dong)" parenthetical are accepted. A partial detail block or
  a wrong detail value still FAILS.

Mutation controls: wrong values must still FAIL (off-by-one line or
column, wrong number, missing row, wrong size, wrong PID).

Forward only: these tests and the accompanying parser broadening
apply to future grading. Already-graded R3-L3 results are not
changed or re-graded.

Run: python3 -m unittest rung3-ci/test_tier_a_check.py
     (or: python3 rung3-ci/test_tier_a_check.py)
Standard library only. No personal info in this file.
"""
import importlib.util
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tier_a_check", os.path.join(HERE, "tier-a-check.py"))
tac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tac)


class JsonErrorsTest(unittest.TestCase):
    KEY = {"rows": [{"line": 1, "col": 27}, {"line": 1, "col": 50},
                    {"line": 1, "col": 26}]}

    def check(self, text):
        reasons = []
        tac.check_json_errors(text, self.KEY, reasons)
        return reasons

    def test_vietnamese_form(self):
        text = ("dong loi 1, cot loi 27\n"
                "dong loi 1, cot loi 50\n"
                "dong loi 1, cot loi 26\n")
        self.assertEqual(self.check(text), [])

    def test_english_comma_form(self):
        text = "line 1, col 27\nline 1, col 50\nline 1, col 26\n"
        self.assertEqual(self.check(text), [])

    def test_english_column_word_form(self):
        text = ("line 1 column 27\nline 1 column 50\n"
                "line 1 column 26\n")
        self.assertEqual(self.check(text), [])

    def test_english_error_line_column_form(self):
        text = ("Error line 1, Error column 27\n"
                "Error line 1, Error column 50\n"
                "Error line 1, Error column 26\n")
        self.assertEqual(self.check(text), [])

    def test_mixed_forms(self):
        text = ("dong loi 1, cot loi 27\n"
                "line 1, col 50\n"
                "Error line 1 Error column 26\n")
        self.assertEqual(self.check(text), [])

    def test_mutation_off_by_one_col_fails(self):
        text = ("dong loi 1, cot loi 28\n"
                "dong loi 1, cot loi 50\n"
                "dong loi 1, cot loi 26\n")
        self.assertNotEqual(self.check(text), [])

    def test_mutation_off_by_one_line_fails(self):
        text = ("line 2, col 27\nline 1, col 50\nline 1, col 26\n")
        self.assertNotEqual(self.check(text), [])

    def test_mutation_missing_row_fails(self):
        text = "dong loi 1, cot loi 27\ndong loi 1, cot loi 50\n"
        self.assertNotEqual(self.check(text), [])


class SqlOrderTotalTest(unittest.TestCase):
    KEY = {"order": [["Giuong", 600], ["Tu", 400], ["Ghe", 250],
                     ["Ban", 150]], "total": 6750}
    KET_QUA = ("Giuong 600\nTu 400\nGhe 250\nBan 150\n6750\n"
               "CREATE TABLE san_pham (id INTEGER PRIMARY KEY, "
               "ten TEXT, gia INTEGER, so_luong INTEGER);\n"
               "Ban, 150, 10\nGhe, 250, 5\nDen, 80, 20\n"
               "Tu, 400, 3\nGiuong, 600, 2\n")

    def check(self, ket_qua, csv_text):
        reasons = []
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ket-qua-truy-van.csv"), "w",
                      encoding="utf-8", newline="") as f:
                f.write(csv_text)
            tac.check_sql_order_total(ket_qua, self.KEY, reasons, d)
        return reasons

    def test_headerless_quoted_csv_real_sample(self):
        # Exact R3-021-L3 evidence shape: quoted, CRLF, no header.
        csv_text = ('"Giuong","600"\r\n"Tu","400"\r\n'
                    '"Ghe","250"\r\n"Ban","150"\r\n')
        self.assertEqual(self.check(self.KET_QUA, csv_text), [])

    def test_headerless_plain_csv(self):
        csv_text = "Giuong,600\nTu,400\nGhe,250\nBan,150\n"
        self.assertEqual(self.check(self.KET_QUA, csv_text), [])

    def test_with_header_csv_still_passes(self):
        csv_text = ("ten,gia\nGiuong,600\nTu,400\nGhe,250\nBan,150\n")
        self.assertEqual(self.check(self.KET_QUA, csv_text), [])

    def test_with_header_quoted_csv_still_passes(self):
        csv_text = ('"ten","gia"\n"Giuong","600"\n"Tu","400"\n'
                    '"Ghe","250"\n"Ban","150"\n')
        self.assertEqual(self.check(self.KET_QUA, csv_text), [])

    def test_mutation_missing_csv_row_fails(self):
        csv_text = '"Giuong","600"\n"Tu","400"\n"Ghe","250"\n'
        self.assertNotEqual(self.check(self.KET_QUA, csv_text), [])

    def test_mutation_extra_csv_row_fails(self):
        csv_text = ('"Giuong","600"\n"Tu","400"\n"Ghe","250"\n'
                    '"Ban","150"\n"Den","80"\n')
        self.assertNotEqual(self.check(self.KET_QUA, csv_text), [])

    def test_mutation_wrong_number_fails(self):
        bad = self.KET_QUA.replace("Giuong 600", "Giuong 601", 1)
        csv_text = "Giuong,600\nTu,400\nGhe,250\nBan,150\n"
        self.assertNotEqual(self.check(bad, csv_text), [])

    def test_mutation_missing_total_fails(self):
        bad = self.KET_QUA.replace("6750\n", "")
        csv_text = "Giuong,600\nTu,400\nGhe,250\nBan,150\n"
        self.assertNotEqual(self.check(bad, csv_text), [])


class ImageSizesTest(unittest.TestCase):
    KEY = {"rows": [
        {"file": "d72-anh-1.png", "size": "800x600"},
        {"file": "d72-anh-2.png", "size": "1024x768"},
        {"file": "d72-anh-3.png", "size": "640x480"},
        {"file": "d72-anh-4.png", "size": "1280x720"},
        {"file": "d72-anh-5.png", "size": "400x400"},
    ]}

    def check(self, text):
        reasons = []
        tac.check_image_sizes(text, self.KEY, reasons)
        return reasons

    def test_plain_form_still_passes(self):
        text = ("d72-anh-1.png 800x600\nd72-anh-2.png 1024x768\n"
                "d72-anh-3.png 640x480\nd72-anh-4.png 1280x720\n"
                "d72-anh-5.png 400x400\n")
        self.assertEqual(self.check(text), [])

    def test_pipe_table_real_sample(self):
        # Exact R3-072-L3 ket-qua.txt shape.
        text = ("index | file name | size\n\n--- | --- | ---\n\n"
                "1 | d72-anh-1.png | 800 x 600\n\n"
                "2 | d72-anh-2.png | 1024 x 768\n\n"
                "3 | d72-anh-3.png | 640 x 480\n\n"
                "4 | d72-anh-4.png | 1280 x 720\n\n"
                "5 | d72-anh-5.png | 400 x 400")
        self.assertEqual(self.check(text), [])

    def test_numbered_dash_form(self):
        text = ("1. d72-anh-1.png - 800 x 600\n"
                "2. d72-anh-2.png - 1024 x 768\n"
                "3. d72-anh-3.png - 640 x 480\n"
                "4. d72-anh-4.png - 1280 x 720\n"
                "5. d72-anh-5.png - 400 x 400\n")
        self.assertEqual(self.check(text), [])

    def test_mutation_wrong_size_fails(self):
        text = ("1 | d72-anh-1.png | 801 x 600\n"
                "2 | d72-anh-2.png | 1024 x 768\n"
                "3 | d72-anh-3.png | 640 x 480\n"
                "4 | d72-anh-4.png | 1280 x 720\n"
                "5 | d72-anh-5.png | 400 x 400\n")
        self.assertNotEqual(self.check(text), [])

    def test_mutation_missing_row_fails(self):
        text = ("1 | d72-anh-1.png | 800 x 600\n"
                "2 | d72-anh-2.png | 1024 x 768\n"
                "3 | d72-anh-3.png | 640 x 480\n"
                "4 | d72-anh-4.png | 1280 x 720\n")
        self.assertNotEqual(self.check(text), [])


class ReportConsistencyTest(unittest.TestCase):
    LENH_DIA = ("2026-11-26T21:40:54+07:00\n"
                "Filesystem Size Used Avail Use% Mounted on\n"
                "/dev/mapper/root 385G 157G 225G 42% /\n")
    LENH_RAM = ("2026-11-26T21:41:19+07:00\n"
                " total used free shared buff/cache available\n"
                "Mem: 30Gi 12Gi 1.3Gi 1.4Gi 20Gi 18Gi\n")
    LENH_PROC = ("2026-11-26T21:54:34+07:00\n"
                 "COMMAND PID %CPU %MEM RSS\n"
                 "zen-bin 578117 2.7 2.4 806632\n"
                 "Hyprland 1756 1.9 0.6 209600\n"
                 "quickshell 1866 0.9 2.2 718316\n"
                 "python3 3455932 0.8 0.1 60292\n"
                 "chromium 12605 0.7 0.7 242240\n")
    BAO_REAL = ("Disk\nFree on /: 225G\n\nRAM\n"
                "Free (free column): 1.3Gi\nAvailable: 18Gi\n\n"
                "Top 5 processes by CPU\n"
                "Name | PID | CPU % | RAM RSS (KiB; %MEM)\n"
                "zen-bin | 578117 | 2.7 | 806632 (2.4%)\n"
                "Hyprland | 1756 | 1.9 | 209600 (0.6%)\n"
                "quickshell | 1866 | 0.9 | 718316 (2.2%)\n"
                "python3 | 3455932 | 0.8 | 60292 (0.1%)\n"
                "chromium | 12605 | 0.7 | 242240 (0.7%)\n\n"
                "Recording time: 2026-11-26T21:55:26+07:00\n")
    BAO_OLD = ("Dia con trong: 225G\nRAM con trong: 1.3Gi\n"
               "zen-bin 578117 2.7 2.4\n"
               "Hyprland 1756 1.9 0.6\n"
               "quickshell 1866 0.9 2.2\n"
               "python3 3455932 0.8 0.1\n"
               "chromium 12605 0.7 0.7\n")

    def check(self, bao):
        reasons = []
        with tempfile.TemporaryDirectory() as d:
            for name, text in (("d42-bao-cao.txt", bao),
                               ("d42-lenh-dia.txt", self.LENH_DIA),
                               ("d42-lenh-ram.txt", self.LENH_RAM),
                               ("d42-lenh-tien-trinh.txt",
                                self.LENH_PROC)):
                with open(os.path.join(d, name), "w",
                          encoding="utf-8") as f:
                    f.write(text)
            tac.check_report_consistency(d, {}, reasons)
        return reasons

    def test_real_sample_labels_and_pipes(self):
        self.assertEqual(self.check(self.BAO_REAL), [])

    def test_old_labels_still_pass(self):
        self.assertEqual(self.check(self.BAO_OLD), [])

    def test_mutation_wrong_disk_value_fails(self):
        bad = self.BAO_REAL.replace("225G", "999G")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_wrong_ram_value_fails(self):
        bad = self.BAO_REAL.replace("1.3Gi", "9.9Gi")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_missing_process_row_fails(self):
        bad = self.BAO_REAL.replace(
            "chromium | 12605 | 0.7 | 242240 (0.7%)\n", "")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_wrong_pid_fails(self):
        bad = self.BAO_REAL.replace("578117", "578118")
        self.assertNotEqual(self.check(bad), [])


DP02_KEY = {
    "type": "keyword-counts",
    "grand_total": 54,
    "files_with_keyword": 12,
    "keywords": [
        {"keyword": "alpha7", "total": 12,
         "top_file": "dp02-01.txt", "top_count": 4},
        {"keyword": "bravo21", "total": 9,
         "top_file": "dp02-02.txt", "top_count": 3},
        {"keyword": "charlie9", "total": 15,
         "top_file": "dp02-03.txt", "top_count": 5},
        {"keyword": "delta42", "total": 7,
         "top_file": "dp02-06.txt", "top_count": 3},
        {"keyword": "echo13", "total": 11,
         "top_file": "dp02-04.txt", "top_count": 4},
    ],
    "per_file": {
        "dp02-01.txt": {"alpha7": 4, "bravo21": 0, "charlie9": 3,
                        "delta42": 0, "echo13": 0},
        "dp02-02.txt": {"alpha7": 3, "bravo21": 3, "charlie9": 0,
                        "delta42": 1, "echo13": 0},
        "dp02-03.txt": {"alpha7": 2, "bravo21": 0, "charlie9": 5,
                        "delta42": 0, "echo13": 0},
        "dp02-04.txt": {"alpha7": 2, "bravo21": 0, "charlie9": 2,
                        "delta42": 0, "echo13": 4},
        "dp02-05.txt": {"alpha7": 1, "bravo21": 2, "charlie9": 0,
                        "delta42": 0, "echo13": 2},
        "dp02-06.txt": {"alpha7": 0, "bravo21": 2, "charlie9": 0,
                        "delta42": 3, "echo13": 0},
        "dp02-07.txt": {"alpha7": 0, "bravo21": 1, "charlie9": 0,
                        "delta42": 1, "echo13": 0},
        "dp02-08.txt": {"alpha7": 0, "bravo21": 1, "charlie9": 0,
                        "delta42": 1, "echo13": 0},
        "dp02-09.txt": {"alpha7": 0, "bravo21": 0, "charlie9": 2,
                        "delta42": 0, "echo13": 2},
        "dp02-10.txt": {"alpha7": 0, "bravo21": 0, "charlie9": 2,
                        "delta42": 0, "echo13": 2},
        "dp02-11.txt": {"alpha7": 0, "bravo21": 0, "charlie9": 1,
                        "delta42": 0, "echo13": 1},
        "dp02-12.txt": {"alpha7": 0, "bravo21": 0, "charlie9": 0,
                        "delta42": 1, "echo13": 0},
    },
}

DP02_SUMMARY = ("alpha7: tong 12, file nhieu hit nhat dp02-01.txt "
                "(4 hit)\n"
                "bravo21: tong 9, file nhieu hit nhat dp02-02.txt "
                "(3 hit)\n"
                "charlie9: tong 15, file nhieu hit nhat dp02-03.txt "
                "(5 hit)\n"
                "delta42: tong 7, file nhieu hit nhat dp02-06.txt "
                "(3 hit)\n"
                "echo13: tong 11, file nhieu hit nhat dp02-04.txt "
                "(4 hit)\n"
                "Tong chung: 54\n"
                "So file chua it nhat 1 tu khoa: 12\n")


def dp02_detail_lines(with_dong=True):
    lines = []
    for name in sorted(DP02_KEY["per_file"]):
        counts = DP02_KEY["per_file"][name]
        rest = ", ".join("%s %d" % (kw, counts[kw])
                         for kw in ("alpha7", "bravo21", "charlie9",
                                    "delta42", "echo13"))
        if with_dong:
            lines.append("%s (40 dong): %s" % (name, rest))
        else:
            lines.append("%s: %s" % (name, rest))
    return "\n".join(lines) + "\n"


class KeywordCountsTest(unittest.TestCase):
    def check(self, report):
        reasons = []
        with tempfile.TemporaryDirectory() as d:
            code_dir = os.path.join(d, "dp02-code")
            os.makedirs(code_dir)
            for name, counts in DP02_KEY["per_file"].items():
                body = []
                for kw, n in counts.items():
                    body.extend(["tu khoa %s o dong nay" % kw] * n)
                with open(os.path.join(code_dir, name), "w",
                          encoding="utf-8") as f:
                    f.write("\n".join(body) + "\n")
            with open(os.path.join(d, "bao-cao.txt"), "w",
                      encoding="utf-8") as f:
                f.write(report)
            tac.check_keyword_counts(d, DP02_KEY, reasons)
        return reasons

    def test_summary_only_real_sample(self):
        # Exact DP-02-L3 report shape: brief requires no detail.
        self.assertEqual(self.check(DP02_SUMMARY), [])

    def test_with_full_detail_block_still_passes(self):
        self.assertEqual(
            self.check(DP02_SUMMARY + dp02_detail_lines()), [])

    def test_detail_without_dong_parenthetical(self):
        self.assertEqual(
            self.check(DP02_SUMMARY + dp02_detail_lines(False)), [])

    def test_mutation_wrong_total_fails(self):
        bad = DP02_SUMMARY.replace("alpha7: tong 12", "alpha7: tong 13")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_missing_keyword_row_fails(self):
        bad = DP02_SUMMARY.replace(
            "echo13: tong 11, file nhieu hit nhat dp02-04.txt "
            "(4 hit)\n", "")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_wrong_grand_total_fails(self):
        bad = DP02_SUMMARY.replace("Tong chung: 54", "Tong chung: 55")
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_partial_detail_block_fails(self):
        detail = dp02_detail_lines().splitlines(True)
        bad = DP02_SUMMARY + "".join(detail[:-1])
        self.assertNotEqual(self.check(bad), [])

    def test_mutation_wrong_detail_value_fails(self):
        detail = dp02_detail_lines().replace("alpha7 4", "alpha7 5", 1)
        self.assertNotEqual(self.check(DP02_SUMMARY + detail), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
