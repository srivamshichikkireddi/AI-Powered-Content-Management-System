# AICMS Sprint Plan (Part 2 & Part 3 Deliverables)

## 1. Executive Summary & Timeline Alignment

This document details the multi-sprint execution plan for the **AI-Powered Content Management System (AICMS)**, mapping the functional (24), non-functional (10), and security (8) requirements specified in Phase 1 into actionable development sprints.

### Sprint Calendar & Schedule Reconciliation

As noted in the project governance baseline, while the original syllabus windows occurred in mid-to-late October 2026, execution follows an accelerated pipeline with spillover into Sprint-3 as explicitly authorized by course guidelines. All timeline nuances and scheduling shifts are tracked in `docs/DEVIATIONS.md`.

| Sprint | Historical Course Window | Target Focus & Milestone Scope | Target Story Points | Key Deliverables |
|---|---|---|---|---|
| **Sprint-1** | 19 Oct – 23 Oct 2026 | Core End-to-End Flow: Auth, Intake, Extraction, AI Enrichment, Semantic Vector Search | 26 pts | Working pipeline, vector search API, 1-min demo script (`SPRINT1_DEMO_SCRIPT.md`), CI baseline |
| **Sprint-2** | 26 Oct – 30 Oct 2026 | Full Web UI (React), Metadata CRUD, Category Admin, Purge/Delete, Rate Limits, Audit Logs | 20 pts | Full web frontend dashboard, Dev freeze (`v1.0-freeze`), 2-min demo script (`SPRINT2_DEMO_SCRIPT.md`), initial docs |
| **Sprint-3** | 02 Nov – 06 Nov 2026 | Spillover, Quantitative Evaluation (TC-AI-04, TC-PERF-01..03), Full 38 TCs & 4 Course Reports | 13 pts | Full test register, Unit Test Report, System Validation Report, Code Coverage & Branch Coverage Reports |
| **Total** | — | **Full Project Lifecycle** | **59 pts** | **All 42 Reqs + 38 TCs Verified** |

---

## 2. Team Capacity and Allocation

| Team Member | Primary Role | Assigned Areas | Sprint 1 Pts | Sprint 2 Pts | Sprint 3 Pts | Total Pts |
|---|---|---|---|---|---|---|
| **Srivamshi Chikkireddi** | Developer (Repo Owner) | Auth, Ingestion, Vector Search, Deletion, TLS | 18 | 6 | 0 | **24** |
| **Shamanth SK** | Product / Front-End Rep | Metadata editing, Taxonomy Admin, React Web UI | 0 | 14 | 0 | **14** |
| **Shreeverdhan M** | QA / Test Lead | AI models, Observability, Performance & Scalability | 5 | 3 | 5 | **13** |
| **Sripada Krishna Sameer Aditya** | Test Engineer | Parsers, Regression Suite, Traceability & Reports | 3 | 0 | 5 | **8** |
| **Total** | | | **26** | **23** | **10** | **59** |

---

## 3. Sprint Breakdown

### Sprint-1: Core Ingestion & Semantic Search Pipeline (26 Story Points)
- **Goal**: Enable authenticated users to ingest PDF/DOCX/TXT files, run text extraction, compute vector embeddings using `all-MiniLM-L6-v2`, index them in PostgreSQL + pgvector, and perform cosine semantic search with strict pre-disclosure authorization checks.
- **Stories**:
  - `US-01`: User Authentication, Session Security & Lockout (5 pts) — *Assignee: Srivamshi Chikkireddi* [AICMS-F-023, F-024, SR-001, SR-007, SR-008]
  - `US-02`: Secure Document Intake, Validation & Deduplication (5 pts) — *Assignee: Srivamshi Chikkireddi* [AICMS-F-001..004, SR-002, SR-004]
  - `US-03`: Document Parsing and Author/Title Metadata Extraction (3 pts) — *Assignee: Sripada Krishna Sameer Aditya* [AICMS-F-005..007]
  - `US-04`: AI Semantic Embeddings, Categorization & Keyword Extraction (5 pts) — *Assignee: Shreeverdhan M* [AICMS-F-008..010, NF-008]
  - `US-05`: Vector Indexing, Semantic Search & Access Control Filter (8 pts) — *Assignee: Srivamshi Chikkireddi* [AICMS-F-011..015, SR-005, NF-001]
- **Gate / DoD**:
  - `docker-compose.yml` launches healthy Postgres (pgvector), Redis, API, and Celery worker.
  - End-to-end ingestion and search verified via automated integration tests.
  - Sprint-1 1-minute video demo script validated and reproducible.

### Sprint-2: Metadata, Administration, Full Web UI & Freeze (20 Story Points)
- **Goal**: Deliver a polished, accessible React dashboard allowing document upload, search, metadata editing with concurrency control, admin taxonomy operations, document deletion with vector purge, and system freeze.
- **Stories**:
  - `US-06`: Metadata Review, Editing & Optimistic Concurrency Control (3 pts) — *Assignee: Shamanth SK* [AICMS-F-016..018]
  - `US-07`: Category Taxonomy Management & Collection Re-Indexing (3 pts) — *Assignee: Shamanth SK* [AICMS-F-019..020]
  - `US-08`: Secure Document Deletion & Vector Purge (3 pts) — *Assignee: Srivamshi Chikkireddi* [AICMS-F-021, SR-006]
  - `US-09`: System Observability, Performance Metrics & Audit Logs (3 pts) — *Assignee: Shreeverdhan M* [AICMS-F-022, NF-006, NF-007, SR-001]
  - `US-10`: Frontend Web Application & WCAG 2.1 AA Accessibility (8 pts) — *Assignee: Shamanth SK* [AICMS-NF-005, F-013, F-014, F-016]
  - `US-11`: API Hardening, Rate Limiting & TLS Termination (3 pts) — *Assignee: Srivamshi Chikkireddi* [AICMS-NF-003, NF-009, NF-010, SR-003]
- **Gate / DoD**:
  - Frontend operational with live ingestion status, search results, and admin panels.
  - Development tagged as `v1.0-freeze`; `FREEZE_NOTE.md` recorded.
  - Sprint-2 2-minute video demo script validated.

### Sprint-3: Spillover, Empirical Evaluation & Deliverable Reports (13 Story Points)
- **Goal**: Run empirical accuracy and load benchmarks, execute all 38 test cases from STP §13, and compile the 4 formal course test reports.
- **Stories**:
  - `US-12`: Performance, Reliability & Scalability Validation (5 pts) — *Assignee: Shreeverdhan M* [AICMS-NF-002, NF-004]
  - `US-13`: System Validation, Traceability Matrix & Test Report Generation (5 pts) — *Assignee: Sripada Krishna Sameer Aditya* [All 42 Requirements & 38 Test Cases]
- **Gate / DoD**:
  - Execution of 38 Test Cases recorded in `docs/Test_Execution_Register.csv` with evidence files in `evidence/`.
  - The 4 reports committed to `docs/reports/`:
    1. Unit Test Report
    2. System Validation Report
    3. Code Coverage Report (line coverage)
    4. Branch Coverage Report
  - Final self-audit checklist completed with zero fabricated data.

---

## 4. Definition of Done (DoD)

A backlog item or story is considered **Done** only when:
1. Code is implemented and adheres to architectural principles (ADR-001 to ADR-005).
2. Requirement IDs and Test Case IDs are explicitly referenced in docstrings, test names, and commit messages.
3. Automated unit and integration tests pass locally and in CI.
4. Authorization checks are strictly enforced before content/snippet disclosure.
5. All failure paths (invalid signatures, oversized files, duplicate SHA-256, model timeouts) produce standardized error responses `{code, message, correlation_id}`.
6. Documentation is updated in corresponding markdown files under `docs/`.
