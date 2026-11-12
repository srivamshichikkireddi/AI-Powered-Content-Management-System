# AICMS Test Evidence

Raw outputs of the 31 Oct 2026 regression run, kept so the reports in
[`../reports/`](../reports/) can be traced back to real execution logs.

## Files

| File(s) | Contents |
|---|---|
| `REGRESSION_TEST_REGISTER.md` | The 38-test-case register mapping test cases to requirements |
| `FULL_REGRESSION_SUITE_RUN.txt`, `full_regression_junit.xml` | Full pytest run: 47 tests collected, 47 passed, 0 failed |
| `coverage.xml`, `COVERAGE_TERMINAL_SUMMARY.txt` | Coverage output: 1,490 statements, 80.13% line rate, 125 of 248 branches covered |
| `TC-<ID>_*.txt` and `TC-<ID>_*_junit.xml` | One console log and one JUnit result per test-case group, named by the test-case IDs it covers (for example `TC-EXT-01_02_AI-01_02_03`) |

## Notes

- `htmlcov/` (the HTML coverage browser) is not tracked in git because coverage.py
  generates its own `.gitignore` inside it. Regenerate it with
  `pytest --cov=backend/app --cov-branch --cov-report=html`.
- Everything here is a snapshot of one run. Re-run the commands in
  `docs/CONTRIBUTING.md` (section 4) to reproduce the results.
