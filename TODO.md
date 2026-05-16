# TODO - UI automation failure analysis & fixes

## Step 1: Evidence capture (completed)
- Parsed `reports/html/test_report_test_*.json` for `status == failed`.
- Identified highest-priority failures: login/auth flow cascading failures and fixture plumbing error.

## Step 2: Implement minimal fixes
1. Update `src/pages/login_page.py`
   - Improve waiting/recognition of successful login (welcome/error).
   - Reduce flakiness that causes `login_result['success']` to be `False`.
2. Fix fixture plumbing TypeError
   - Update `src/fixtures/test_data_fixtures.py` and/or relevant login comprehensive tests so `user_test_data` resolves to a dict, not a fixture function.

## Step 3: Validation
- Re-run focused suite: login tests and one dependent suite (accounts overview).
- Re-check JSON artifacts for reduced failed count.

