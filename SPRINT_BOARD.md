# AICMS Sprint-4 Board

**Sprint window**: Mon 23 Nov – Fri 4 Dec 2026 (10 working days)
**Status**: Planned, not started. Every ticket begins in **To Do**.

**Sprint goal**: Make the repository match what `docs/SPRINT_PLAN.md` already promises. Write the documents it references but the repo lacks, refresh the reports that predate later tests, and lift the four weakest API modules in coverage.

Sprints 1 to 3 (US-01 to US-13) are complete; see `docs/SPRINT_PLAN.md` and `docs/PR_LOG.md`. This board covers only the follow-up work found when comparing the plan with the repository.

---

## 1. Workload

Work is split evenly: **4 tickets and 13 story points per person**, 52 points in total.

| Team member | Role | Tickets | Points | Focus this sprint |
|---|---|---|---|---|
| Srivamshi Chikkireddi | Developer (repo owner) | 4 | 13 | Document and user API coverage, freeze note, README |
| Shamanth SK | Product / Front-End | 4 | 13 | Demo script, deviations log, accessibility re-check, UI guide |
| Shreeverdhan M | QA / Test Lead | 4 | 13 | Category and admin coverage, CI coverage gate, report refresh |
| Sripada Krishna Sameer Aditya | Test Engineer | 4 | 13 | Extraction edge cases, execution register, reports path, progress log |
| **Total** | | **16** | **52** | |

---

## 2. Board

Move a ticket key between columns in the same pull request that changes its status.

| To Do | In Progress | In Review | Done |
|---|---|---|---|
| T4-01, T4-02, T4-03, T4-04, T4-05, T4-06, T4-07, T4-08, T4-09, T4-10, T4-11, T4-12, T4-13, T4-14, T4-15, T4-16 | | | |

---

## 3. Tickets

Estimates use the 1 / 2 / 3 / 5 scale from the backlog. Branches follow `docs/CONTRIBUTING.md`.

### Srivamshi Chikkireddi (13 pts)

| ID | Ticket | Pts | Traceability | Branch |
|---|---|---|---|---|
| T4-01 | Raise `api/documents.py` coverage above 70% (currently 40%): list, fetch and error paths | 5 | AICMS-F-021, AICMS-SR-005, TC-DATA-02, TC-SEC-05 | `feature/T4-01-documents-coverage` |
| T4-02 | Cover the user-management paths in `api/users.py` (currently 44%) | 3 | AICMS-F-024, TC-ADM-03 | `feature/T4-02-users-coverage` |
| T4-03 | Write `docs/FREEZE_NOTE.md` describing the scope frozen at the `v1.0-freeze` tag | 2 | Sprint-2 gate, US-10 | `feature/T4-03-freeze-note` |
| T4-04 | Update the README: project status still says "requirements, design and test planning"; add how to run and test | 3 | README, `docs/ENVIRONMENT.md` | `feature/T4-04-readme-status` |

### Shamanth SK (13 pts)

| ID | Ticket | Pts | Traceability | Branch |
|---|---|---|---|---|
| T4-05 | Write `docs/demo/SPRINT2_DEMO_SCRIPT.md`, a 2-minute walkthrough of the web UI | 3 | US-10, Sprint-2 gate | `feature/T4-05-sprint2-demo-script` |
| T4-06 | Write `docs/DEVIATIONS.md` recording the schedule shifts that `SPRINT_PLAN.md` refers to | 3 | `SPRINT_PLAN.md` §1 | `feature/T4-06-deviations-log` |
| T4-07 | Re-run the accessibility check on the React UI and store the output in `evidence/` | 5 | AICMS-NF-005, TC-UX-01 | `feature/T4-07-a11y-recheck` |
| T4-08 | Write a short user guide for the persona switcher and the five UI tabs | 2 | US-10 | `feature/T4-08-ui-guide` |

### Shreeverdhan M (13 pts)

| ID | Ticket | Pts | Traceability | Branch |
|---|---|---|---|---|
| T4-09 | Add tests for `api/categories.py` (52%) and `api/admin.py` (66%) | 5 | AICMS-F-019, AICMS-F-020, TC-ADM-01, TC-ADM-02 | `feature/T4-09-categories-admin-coverage` |
| T4-10 | Make CI fail when total coverage drops below 70%; `ci.yml` has no coverage threshold today | 3 | STP coverage target | `feature/T4-10-ci-coverage-gate` |
| T4-11 | Re-run the full regression suite and refresh the four reports; they reflect the 31 Oct run only | 3 | `reports/README.md` note | `feature/T4-11-refresh-reports` |
| T4-12 | Replace the `file:///d:/se_mp/...` links in `reports/Code_Coverage_Report.md` with repo-relative links, and check the other three reports | 2 | AICMS-REP-CCR-01 | `feature/T4-12-fix-report-links` |

### Sripada Krishna Sameer Aditya (13 pts)

| ID | Ticket | Pts | Traceability | Branch |
|---|---|---|---|---|
| T4-13 | Extend extraction tests: corrupt PDF and DOCX, empty TXT, scanned PDF flagged `needs_ocr` | 5 | AICMS-F-005, F-006, F-007, TC-EXT-01..03 | `feature/T4-13-extraction-edge-tests` |
| T4-14 | Create `docs/Test_Execution_Register.csv` from `evidence/REGRESSION_TEST_REGISTER.md` | 3 | US-13, 38 test cases | `feature/T4-14-execution-register` |
| T4-15 | Settle where reports live: `SPRINT_PLAN.md` and `ci.yml` say `docs/reports/`, the files are in `reports/`; align paths and links | 2 | US-13 | `feature/T4-15-reports-path` |
| T4-16 | Clean up `PROGRESS.md` (duplicated header lines, stops at M8) and record M9 as merged | 3 | `docs/PR_LOG.md` PR-09 | `feature/T4-16-progress-log` |

---

## 4. Dependencies

- T4-11 (refresh reports) runs after T4-01, T4-02 and T4-09, so the new coverage figures are included.
- T4-12 and T4-15 both touch `reports/`; do T4-15 first so links are fixed once.
- T4-14 feeds the regression run in T4-11.

## 5. Definition of Done

Same as `docs/SPRINT_PLAN.md` §4. In short: requirement and test-case IDs cited in the commit and PR, CI green, evidence saved under `evidence/` for any measured number, and a reviewer other than the author approves before merge.
