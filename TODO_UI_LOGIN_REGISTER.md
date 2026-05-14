# TODO - Fix UI login & registration and generate HTML report

## Goal
Fix all failing UI login + registration tests and generate an HTML report that includes executed tests with their status.

## Steps
1. Update `src/pages/registration_page.py` to fix comprehensive registration failures:
   - Correct/robust wait for registration completion (success header or error element).
   - Align `is_registration_successful()` and failure handling.
   - Make XSS/SQLi assertions compatible with how ParaBank renders/escapes payloads.

2. Update `src/pages/login_page.py` if needed:
   - Diagnose why `test_login_with_valid_credentials` gets ParaBank “internal error”.
   - If it is only a locator/wait issue, fix it; otherwise document that backend returns internal error.

3. Re-run exactly these test selections:
   - `pytest tests/ui/login/test_login.py`
   - `pytest tests/ui/registration/test_registration.py`
   - `pytest tests/ui/registration/test_registration_comprehensive.py`

4. Generate HTML report including exact executed tests and their status:
   - If framework produces JSON artifacts `reports/html/test_report_<test>.json`, ensure `generate_pass_html_report.py` reads them correctly.
   - Modify/add report generator if needed so it lists **PASS/FAIL** (not only PASS).

5. Verify generated HTML is created under `reports/html/` and includes correct statuses.

