#!/usr/bin/env python3
"""Diagnostic: f01 flow with LOWERCASE formula refs (Worker P, 21/11).
Mirrors run_f01 exactly except formulas are lowercase (=c2*d2 etc).
The spec's uppercase =C2*D2 fails because the fixture's evalFormula
looks up cells['C2'] (keys are lowercase) -> #ERR. This probe confirms
the rest of the flow passes with lowercase. NOT the official f01 result
(official = as-specced, FAIL)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_live as rl


def main():
    httpd, base = rl.start_server()
    print("server:", base, flush=True)
    r = rl.Runner("f01-diag-lower", base)
    with rl.WD() as d:
        try:
            r.step("open fixture", "goto",
                   lambda: d.new_tab(base + "/fcc-k/test-01-spreadsheet.html"))
            # Lowercase formulas only; everything else identical to run_f01.
            rows = [("a2", "2026-11-16"), ("b2", "Widget"), ("c2", "12"),
                    ("d2", "45000"), ("e2", "=c2*d2"),
                    ("a3", "2026-11-17"), ("b3", "Gadget"), ("c3", "7"),
                    ("d3", "82000"), ("e3", "=c3*d3"),
                    ("a4", "2026-11-18"), ("b4", "Tool"), ("c4", "5"),
                    ("d4", "150000"), ("e4", "=c4*d4"),
                    ("e5", "=SUM(E2:E4)"), ("e6", "=AVERAGE(E2:E4)"),
                    ("e7", "=COUNT(E2:E4)")]
            for cell, val in rows:
                r.step(f"select {cell.upper()}", "click",
                       lambda c=cell: d.click(rl._fcc_cell_btn(c)))
                r.step(f"type {val} into {cell.upper()}", "type",
                       lambda v=val: d.type_text("#typed", v))
                r.step(f"press type for {cell.upper()}", "click",
                       lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'type').click()"))
                if val.startswith("="):
                    r.step(f"press Enter for {cell.upper()}", "click",
                           lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'Enter').click()"))
            e7 = r.step("read E7 after wrong formula", "text", lambda: d.text("#e7"))
            r.check("E7 shows COUNT text after wrong formula", e7 == "COUNT text", e7)
            r.step("select E7", "click", lambda: d.click(rl._fcc_cell_btn("e7")))
            r.step("type corrected formula", "type",
                   lambda: d.type_text("#typed", "=COUNTA(E2:E4)"))
            r.step("press type for correction", "click",
                   lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'type').click()"))
            r.step("press Enter for correction", "click",
                   lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'Enter').click()"))
            end = r.step("read end state", "eval",
                         lambda: d.eval("return {c2: document.querySelector('#c2').textContent, c3: document.querySelector('#c3').textContent, c4: document.querySelector('#c4').textContent, e2: document.querySelector('#e2').textContent, e3: document.querySelector('#e3').textContent, e4: document.querySelector('#e4').textContent, e5: document.querySelector('#e5').textContent, e6: document.querySelector('#e6').textContent, e7: document.querySelector('#e7').textContent}"))
            r.details["endState"] = end
            print("END STATE:", end, flush=True)
            r.check("E2 == 540000", end["e2"] == "540000", end["e2"])
            r.check("E3 == 574000", end["e3"] == "574000", end["e3"])
            r.check("E4 == 750000", end["e4"] == "750000", end["e4"])
            r.check("E5 == 1864000", end["e5"] == "1864000", end["e5"])
            r.check("E6 == 621333", end["e6"] == "621333", end["e6"])
        except Exception as e:
            r.failures.append(f"RUNNER ERROR: {type(e).__name__}: {e}")
        finally:
            d.close()
    print("DIAG RESULT pass=%s failures=%s" % (not r.failures, r.failures), flush=True)
    if httpd is not None:
        httpd.shutdown()


if __name__ == "__main__":
    main()
