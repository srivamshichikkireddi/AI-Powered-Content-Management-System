# AICMS Project Progress & Execution Log

**Last Updated**: 2026-10-31 (Checkpoint 2 / M2 Completed)

---

## 1. Current State
- **Active Milestone**: **M2 (Authentication, Sessions, RBAC & Lockout)** — Completed, awaiting user confirmation to proceed to M3.
- **Active Branch**: `feature/US-01-auth-security`
- **Docker Status**: All containers healthy and running (`aicms_db`, `aicms_redis`, `aicms_backend`, `aicms_worker`, `aicms_frontend`).
- **Test Evidence**: 13 automated tests passing with 75% coverage in `evidence/TC-SEC-07_08_09_ADM-03.txt` and `evidence/TC-SEC-07_08_09_ADM-03_junit.xml`.

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
- [x] **Password Hashing (AICMS-SR-007, TC-SEC-07)**: Implemented bcrypt with 12 rounds and salt; plain passwords never stored or logged.
- [x] **Account Lockout (AICMS-SR-008, TC-SEC-08)**: 5 consecutive failed login attempts trigger a 15-minute lockout; the 6th attempt returns `423 Locked` and records an audited security event.
- [x] **Server-Side Session Store & Idle Expiry (AICMS-SR-008, TC-SEC-09)**: Opaque 256-bit cryptographically secure session tokens in database; enforced 30-minute idle inactivity timeout; `/api/v1/auth/logout` explicitly revokes session.
- [x] **Role-Based Access Control (AICMS-F-024, TC-ADM-03)**:
  - System roles: `admin`, `editor`, `user`, `auditor`.
  - Initial system personas seeded on startup: `admin_user`, `editor_user`, `regular_user`, `auditor_user`.
  - Admin-only routes (`/api/v1/users`) reject regular users with `403 Forbidden` (`FORBIDDEN_ROLE`).
  - Auditor routes (`/api/v1/audit/logs`) restrict access to auditors and administrators.
- [x] **Audit Trail Core (AICMS-SR-001)**: Comprehensive audit logging table capturing login successes, failures, account lockouts, session expirations, and logouts with correlation ID tracking.
- [x] **Test Verification**:
  - All 13 tests passed (100% pass rate) with 75% line/branch coverage.
  - Verified live API endpoints via HTTP calls.
  - Raw evidence stored in `evidence/TC-SEC-07_08_09_ADM-03.txt`.

---

## 3. Next Milestone
- **Milestone 3 (Checkpoint 3)**: Document Intake, Multi-Format Validation (PDF/DOCX/TXT $\le$ 20MB), Extension + Magic Bytes Inspection, SHA-256 Deduplication (409 Conflict), and Queue Status Tracking (`TC-UP-01`, `TC-UP-02`, `TC-UP-03`, `TC-UP-04`, `TC-SEC-04`).

---

## 4. How to Run & Verify M2
```bash
# Run test suite
docker exec aicms_backend pytest /app/backend/tests -v --cov=/app/backend/app --cov-branch --cov-report=term-missing

# Test login API with admin user
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"admin_user","password":"AdminPass123!"}'
```
