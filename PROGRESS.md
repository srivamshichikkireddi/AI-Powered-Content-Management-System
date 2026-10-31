# AICMS Project Progress & Execution Log

**Last Updated**: 2026-10-31 (Checkpoint 3 / M3 Completed)

---

## 1. Current State
- **Active Milestone**: **M3 (Document Intake, Validation & Deduplication)** — Completed, awaiting user confirmation to proceed to M4.
- **Active Branch**: `feature/US-02-intake-storage`
- **Docker Status**: All containers healthy and running (`aicms_db`, `aicms_redis`, `aicms_backend`, `aicms_worker`, `aicms_frontend`).
- **Test Evidence**: 19 automated tests passing with 74% coverage in `evidence/TC-UP-01_02_03_04_SEC-04.txt` and `evidence/TC-UP-01_02_03_04_SEC-04_junit.xml`.

---

## 2. Completed Milestones

### Milestone 0: Setup & Planning (Checkpoint 0)
- [x] Workspace structure reorganized to standard root directory layout.
- [x] Full text and tabular extraction of Phase 1 specifications (`spec/SRS.md`, `spec/SAD.md`, `spec/STP.md`).
- [x] Created `backlog/backlog.csv` (13 user stories, 59 story points, full traceability, assignees).
- [x] Created `backlog/create_github_backlog.ps1` and `backlog/create_github_backlog.sh`.
- [x] Produced `docs/SPRINT_PLAN.md`, `docs/ASSUMPTIONS.md`, `PLAN.md`.

### Milestone 1: Scaffolding, Docker Compose & CI Workflow (Checkpoint 1)
- [x] Multi-service architecture scaffolded: FastAPI backend, React Vite UI, Nginx TLS reverse proxy, Postgres+pgvector, Redis, and Celery.
- [x] CI/CD pipeline (`.github/workflows/ci.yml`), PR template, CODEOWNERS, contribution guidelines.
- [x] Baseline health endpoints verified and committed on `feature/M1-scaffold-ci`.

### Milestone 2: Authentication, Sessions, RBAC & Account Lockout (Checkpoint 2)
- [x] Password hashing with bcrypt (AICMS-SR-007, TC-SEC-07).
- [x] Account lockout after 5 consecutive failed attempts with HTTP 423 on 6th attempt (AICMS-SR-008, TC-SEC-08).
- [x] Server-side session store with 30-min idle timeout and revocation (AICMS-SR-008, TC-SEC-09).
- [x] Role-Based Access Control (`admin`, `editor`, `user`, `auditor`) and Audit Trail (AICMS-F-024, AICMS-SR-001, TC-ADM-03).

### Milestone 3: Document Intake, Validation & Deduplication (Checkpoint 3)
- [x] **Multi-Format Intake (AICMS-F-001, TC-UP-01)**: PDF, DOCX, TXT accepted and queued with status `QUEUED`.
- [x] **Size Limit Enforcement (AICMS-F-002, TC-UP-02)**: Files > 20 MB strictly rejected with `HTTP 413 Payload Too Large`.
- [x] **SHA-256 Deduplication (AICMS-SR-004, TC-UP-03)**: Duplicate document content rejected with `HTTP 409 Conflict` referencing existing document.
- [x] **Format Whitelist & Integrity (AICMS-F-003, TC-UP-04)**: Unsupported formats (`.csv`, `.zip`, `.py`) rejected with `HTTP 400 UNSUPPORTED_FORMAT`.
- [x] **Magic Bytes & Disguised File Defense (AICMS-SR-002, TC-SEC-04)**: Executables (`MZ`), invalid headers, and disguised binaries rejected with `HTTP 400 INVALID_FILE_SIGNATURE`.
- [x] **Pre-Disclosure Document Authorization (ADR-002, ADR-005)**: Direct-ID queries without permission return `404 Not Found` to prevent leaking document existence.
- [x] **Test Verification**:
  - 19 automated tests passing (100% pass rate) with 74% coverage.
  - Raw evidence stored in `evidence/TC-UP-01_02_03_04_SEC-04.txt`.

---

## 3. Next Milestone
- **Milestone 4 (Checkpoint 4)**: Text Extraction (PyPDF, python-docx), AI Semantic Embeddings (`all-MiniLM-L6-v2`), Scikit-learn Categorization Classifier, TF-IDF Keyphrase/Topic Extraction, and Simulated Failure Injection Flags (`TC-EXT-01`, `TC-EXT-02`, `TC-AI-01`, `TC-AI-02`, `TC-AI-03`).

---

## 4. How to Run & Verify M3
```bash
# Run test suite
docker exec aicms_backend pytest /app/backend/tests -v --cov=/app/backend/app --cov-branch --cov-report=term-missing
```
