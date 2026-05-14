# TODO - Generate HTML report of all passed testcases

- [ ] Confirm where the framework writes per-test JSON artifacts (e.g., reports/html/test_report_*.json).
- [x] Add script `generate_pass_html_report.py` that parses `test_report_*.json`, filters status == "passed", and generates `reports/html/passed_testcases.html`.
- [x] Run the script to generate the HTML report.
- [ ] Verify the generated HTML exists and lists only passed tests.


