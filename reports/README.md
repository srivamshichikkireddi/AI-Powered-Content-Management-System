# AICMS Course Reports

Formal reports for UE22CS341AA (Software Engineering Mini-Project), generated from the
test runs recorded in [`../evidence/`](../evidence/). Each report is dated 2026-10-31 and
reflects the code and test run at that date.

| Report | Document ID | What it covers |
|---|---|---|
| [Unit_Test_Report.md](Unit_Test_Report.md) | `AICMS-REP-UTR-01` | Unit testing strategy, test suites and execution verdict |
| [Code_Coverage_Report.md](Code_Coverage_Report.md) | `AICMS-REP-CCR-01` | Statement coverage per module and analysis of missing lines |
| [Branch_Coverage_Report.md](Branch_Coverage_Report.md) | `AICMS-REP-BCR-01` | Decision-level coverage and uncovered-branch justifications |
| [System_Validation_Report.md](System_Validation_Report.md) | `AICMS-REP-SVR-01` | Requirement traceability matrix and the 38-test-case register |

## Where the numbers come from

- Coverage figures are taken from `evidence/coverage.xml` and
  `evidence/COVERAGE_TERMINAL_SUMMARY.txt`.
- Test counts and results are taken from `evidence/full_regression_junit.xml` and
  `evidence/FULL_REGRESSION_SUITE_RUN.txt`.
- The 38-test-case register is `evidence/REGRESSION_TEST_REGISTER.md`.

## Note

The reports are a snapshot of the 31 Oct 2026 run. Tests added afterwards (for example
`backend/tests/unit/test_extraction_edge_cases.py`) are not reflected in the figures above.
Line numbers quoted in the "missing lines" tables refer to the code as it was on that date.
