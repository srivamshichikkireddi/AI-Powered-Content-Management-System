# Project Execution Plan — AICMS Mini-Project

## 1. Project Goal and Architecture Baseline

The objective of this project is to implement a production-grade, fully functional academic instance of the **AI-Powered Content Management System (AICMS)**, satisfying all deliverables for Software Engineering Mini-Project Part 2 (Sprints, Git Project, Backlog, CI, PR Workflow, Demo Scripts) and Part 3 (Test Case Updates, Regression Register, and 4 Official Test Reports).

### System Architecture
- **Backend API**: Python 3.12 + FastAPI with strict Pydantic schemas, correlation-ID middleware, and standard error envelopes `{code, message, correlation_id}`.
- **Database & Vector Store**: PostgreSQL with `pgvector` extension for cosine distance search (`<=>`), storing users, sessions, documents, chunks, vectors, permissions, audit logs, and metrics.
- **Async Processing & Task Queue**: Celery with Redis for asynchronous ingestion, text parsing, embedding generation, and classification.
- **AI & NLP Pipeline**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions), scikit-learn Logistic Regression / SGD classifier, and TF-IDF keyphrase extraction.
- **Frontend Dashboard**: React 18 + Vite + Tailwind CSS / Accessible UI components providing Login, Live Ingestion Monitor, Semantic Search with Snippets, Document Detail & Metadata Editor, and Admin Console.
- **Infrastructure & Security**: Docker Compose multi-service architecture, dev TLS reverse proxy (Caddy/Nginx), bcrypt password hashing, 30-min idle session expiration, 5-failure account lockout (SR-008), and pre-disclosure document authorization filters (ADR-002).

---

## 2. Milestone Execution Roadmap

| Milestone | Target Sprint | Objectives & Scope | Verification Gate / Exit Criteria |
|---|---|---|---|
| **M0: Setup & Planning** *(Current)* | Baseline | Workspace reorganization, spec extraction, `PLAN.md`, `PROGRESS.md`, `backlog.csv`, `SPRINT_PLAN.md`, `ASSUMPTIONS.md`. | **STOP. Written user approval.** |
| **M1: Scaffolding & CI Pipeline** | Sprint-1 | FastAPI layout, React scaffold, Docker Compose, `.github/workflows/ci.yml`, PR template, CODEOWNERS, db migrations. | `docker compose up` healthy; CI configuration validated; baseline unit test passes. |
| **M2: Auth, Sessions & RBAC** | Sprint-1 | User management, bcrypt hashing, DB session store, 30-min idle timeout, 5-attempt lockout, audit trail. | TC-SEC-07, TC-SEC-08, TC-SEC-09, TC-ADM-03 pass with raw output in `evidence/`. |
| **M3: Document Intake & Storage** | Sprint-1 | Upload endpoint (PDF/DOCX/TXT $\le$ 20MB), file signature check, SHA-256 deduplication (409), status lifecycle. | TC-UP-01, TC-UP-02, TC-UP-03, TC-UP-04, TC-SEC-04 pass with evidence. |
| **M4: Extraction & AI Enrichment** | Sprint-1 | Text extraction, metadata parsing, `all-MiniLM-L6-v2` embeddings, scikit-learn categorization, error flags. | TC-EXT-01, TC-EXT-02, TC-AI-01, TC-AI-02, TC-AI-03 pass with evidence. |
| **M5: Semantic Vector Search & Demo 1** | Sprint-1 | Cosine vector search, server-side pre-authorization filtering, metadata filters, pagination, Sprint-1 60s demo script. | TC-IDX-01, TC-SR-01..04, TC-SEC-05 pass; `SPRINT1_DEMO_SCRIPT.md` validated. |
| **M6: Metadata, Admin, Purge & Metrics** | Sprint-2 | PATCH metadata with optimistic lock (409 on revision conflict), taxonomy CRUD, document purge, metrics endpoint. | TC-MD-01, TC-ADM-01/02, TC-DATA-01/02, TC-SEC-01/02/06, TC-OPS-01/02 pass. |
| **M7: Frontend Dashboard & Freeze** | Sprint-2 | Complete React UI (Upload, Search, Edit, Admin), accessibility compliance (axe), TLS termination, freeze tag. | TC-UX-01 pass; `v1.0-freeze` tagged; `FREEZE_NOTE.md` and `SPRINT2_DEMO_SCRIPT.md` ready. |
| **M8: Empirical Evaluation & Benchmarks** | Sprint-3 | 300-doc synthetic corpus, classifier accuracy evaluation (TC-AI-04), latency & throughput testing (TC-PERF-01..03). | Empirical measurements recorded with commit hash and tool outputs; no fabricated metrics. |
| **M9: Regression, Deliverables & 4 Reports** | Sprint-3 | Full execution of all 38 STP test cases, `Test_Execution_Register.csv`, Unit Test, System Validation, Line & Branch Coverage Reports. | Section 10 self-audit checklist 100% verified. |

---

## 3. Strict Operating Guidelines
1. **Zero Fabrication**: No test case is marked Passed (`P`) without a saved execution log in `evidence/`.
2. **Empirical Measurements**: All performance, accuracy, and coverage numbers are measured directly from executed tool commands.
3. **Sequential Gating**: We never advance to the next milestone until the current milestone's gate passes and user confirms.
