# Formal System Validation Report

**Course**: UE22CS341AA / Software Engineering Mini-Project  
**Institution**: PES University  
**Project Title**: AI-Powered Content Management System (AICMS)  
**Document Identifier**: `AICMS-REP-SVR-01`  
**Version**: 1.0  
**Date**: 2026-10-31  
**Authors**: Shreeverdhan M (PES1UG24AM265), Sripada Aditya (PES1UG24AM285), Srivamshi Chikkireddi (PES1UG24AM287), Shamanth SK (PES1UG24AM258)  
**Repository Branch**: `feature/US-13-regression-reports`  
**Target Environments**: Docker Compose Stack (PostgreSQL 16 pgvector, Redis 7, FastAPI 0.110, Celery 5.3, React 18 / Vite 5, Nginx 1.25 TLS Proxy)  

---

## 1. Executive Summary

This formal **System Validation Report** presents the end-to-end integration and system-level acceptance verification of the **AI-Powered Content Management System (AICMS)** against the approved System Requirements Specification (`spec/SRS.md`) and Software Architecture Document (`spec/SAD.md`).

All 42 formalized requirements—comprising 24 functional specifications (`AICMS-F-001` to `AICMS-F-024`), 10 non-functional performance and quality constraints (`AICMS-NF-001` to `AICMS-NF-010`), and 8 security controls (`AICMS-SR-001` to `AICMS-SR-008`)—have been systematically validated through automated end-to-end test suites, penetration checks, and empirical performance benchmarks.

### Key Validation Outcomes
- **Total Requirements Validated**: 42 / 42 (100.0% Requirement Traceability).
- **Formal Test Cases Executed**: 38 test cases (`TC-UP-01` to `TC-UX-01`).
- **Pass Rate**: **100% (38/38 Passed)**.
- **Defects Discovered / Outstanding**: 0 Critical, 0 High, 0 Medium.
- **Empirical SLA Compliance**:
  - AI Categorization Accuracy: **96.67%** (Target: $\ge 80.0\%$).
  - Search Latency (p90): **71.09 ms** (Target: $\le 3000\text{ ms}$).
  - Concurrency Reliability: **100% success** under parallel workloads.
  - End-to-End Processing (10-Page Document): **0.1584 seconds** (Target: $\le 60.0\text{ s}$).
  - Information Retrieval (Precision@5): **95.00%**, Mean Reciprocal Rank (MRR): **0.7533**.
  - Operational Availability: **100.00%** (Target: $\ge 99.50\%$).

---

## 2. Requirement Traceability Matrix (RTM)

The matrix below maps each specification requirement defined in Phase 1 (`spec/SRS.md`) to its validating test case, target criteria, verified evidence, and compliance verdict.

### 2.1 Functional Requirements (`AICMS-F-001` to `AICMS-F-024`)

| Requirement ID | Description | Validating Test Case | Acceptance Criteria | Verified Result | Verdict |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `AICMS-F-001` | Supported Format Upload | `TC-UP-01` | Accept valid PDF, DOCX, TXT files; return HTTP 201 with document ID and status `QUEUED`. | Verified across 3 MIME types; status initialized to `QUEUED`. | **PASS** |
| `AICMS-F-002` | File Validation & Rejection | `TC-UP-02`, `TC-UP-04`, `TC-SEC-04` | Reject oversized files (>20MB) with 413, invalid extensions with 400, and spoofed magic bytes with 400. | All invalid and oversized submissions rejected safely. | **PASS** |
| `AICMS-F-003` | Duplicate Detection | `TC-UP-03` | Compute SHA-256 hash; reject identical uploads with HTTP 409 Conflict without duplicate indexation. | 409 Conflict returned on repeat submission; zero orphan records. | **PASS** |
| `AICMS-F-004` | Visible Document Lifecycle | `TC-UP-04`, `TC-OPS-01` | Provide observable transitions across `QUEUED`, `PROCESSING`, `COMPLETED`, and `FAILED`. | Status endpoint exposes real-time state; failures retain error log. | **PASS** |
| `AICMS-F-005` | Text Body Extraction | `TC-EXT-01` | Extract text body cleanly from supported documents. | Exact text recovered across TXT, DOCX, and PDF formats. | **PASS** |
| `AICMS-F-006` | Native Metadata Parsing | `TC-EXT-02` | Extract title/author from document headers; populate `None` when absent without fabricating values. | Non-fabrication rule preserved; plain text retains `None`. | **PASS** |
| `AICMS-F-007` | Scanned Document Detection | `TC-EXT-03` | Flag scanned or blank documents as `needs_ocr=True` for secondary OCR queue. | Scanned/blank pages trigger OCR fallback flag. | **PASS** |
| `AICMS-F-008` | Automated Categorization | `TC-AI-02`, `TC-AI-04` | Assign category from approved taxonomy with confidence score; achieve $\ge 80\%$ test accuracy. | 96.67% accuracy achieved across 30 held-out corpus items. | **PASS** |
| `AICMS-F-009` | Keyword & Topic Extraction | `TC-AI-03` | Extract 5–10 representative keyphrases and a topical descriptor. | TF-IDF extracts 5–10 keywords and non-empty topic tags. | **PASS** |
| `AICMS-F-010` | Dense Semantic Embeddings | `TC-AI-01` | Generate 384-dimensional unit-normalized embeddings. | Dimension 384 verified; L2 norm = $1.0 \pm 10^{-4}$. | **PASS** |
| `AICMS-F-011` | Vector Index Discoverability | `TC-IDX-01` | Documents become discoverable via pgvector immediately after enrichment finishes. | Search returns document within milliseconds of indexing. | **PASS** |
| `AICMS-F-012` | Natural Language Query Search | `TC-SR-01`, `TC-SR-03` | Free-text search matching semantic concepts without requiring exact keyword syntax. | Conceptual semantic retrieval verified. | **PASS** |
| `AICMS-F-013` | Cosine Similarity Ranking | `TC-SR-01`, `TC-SR-02` | Rank search results in descending semantic relevance using pgvector `<=>` cosine distance. | High relevance documents rank first (Precision@5: 95%). | **PASS** |
| `AICMS-F-014` | Faceted Filtering | `TC-SR-02` | Filter search queries by category name and file extension. | Returned items strictly satisfy all active filter constraints. | **PASS** |
| `AICMS-F-015` | Snippet & Pagination | `TC-SR-04` | Present contextual excerpts, confidence badges, and offset/limit pagination. | Snippets highlighted; limit/offset slices verified. | **PASS** |
| `AICMS-F-016` | Metadata Correction & Locks | `TC-MD-01` | Authorized editors modify tags; optimistic revision locking detects concurrent overwrites (409). | Conflict detected on stale revision; authorized update succeeds. | **PASS** |
| `AICMS-F-017` | Pre-Disclosure Authorization | `TC-SEC-01`, `TC-SEC-05` | Prevent unauthorized metadata disclosure; return 404 Not Found instead of 403 for restricted direct IDs. | Zero metadata leaked; non-permission documents omitted from search. | **PASS** |
| `AICMS-F-018` | Tamper-Evident Audit Trail | `TC-SEC-02` | Record actor, timestamp, action, outcome, and resource ID for all administrative and edit actions. | Audit events persisted with correlation IDs and zero passwords. | **PASS** |
| `AICMS-F-019` | Admin Taxonomy Management | `TC-ADM-01` | Admin creates/deletes categories; enforce referential integrity to block deletion of categories in active use. | In-use categories return 400 error; non-admin blocked with 403. | **PASS** |
| `AICMS-F-020` | Bulk Re-Indexing Pipeline | `TC-ADM-02` | Admin triggers asynchronous re-indexing queue returning job ID and audit record. | Re-index job queued; audit record created. | **PASS** |
| `AICMS-F-021` | Synchronous Document Deletion | `TC-DATA-01` | Delete document record, vectors, and disk file synchronously; purged documents vanish from search immediately. | Search yields zero matches immediately upon deletion. | **PASS** |
| `AICMS-F-022` | Operational Telemetry | `TC-OPS-02` | Expose uptime, error counts, latency percentiles, and request volume without revealing document content. | Prometheus `/metrics` and `/api/v1/admin/metrics` active. | **PASS** |
| `AICMS-F-023` | Server-Side Session Token | `TC-SEC-09` | 256-bit CSPRNG session tokens; instantaneous server-side revocation upon user logout. | Revoked token returns 401 Unauthorized immediately. | **PASS** |
| `AICMS-F-024` | User Role Governance | `TC-ADM-03` | Admin creates accounts, updates roles (`admin`, `editor`, `user`, `auditor`), and deactivates users. | Role permissions enforced; deactivated users blocked at login. | **PASS** |

---

### 2.2 Non-Functional Requirements (`AICMS-NF-001` to `AICMS-NF-010`)

| Requirement ID | Constraint Category | Target Specification | Measured Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| `AICMS-NF-001` | Search Latency | 90th percentile response time $\le 3000\text{ ms}$ under 50-query load. | **p90 = 71.09 ms (0.0711 s)**, Median = 45.42 ms. | **PASS** |
| `AICMS-NF-002` | High Availability | Monthly uptime $\ge 99.50\%$; exclude planned maintenance windows. | **100.00% Availability** (zero 5xx server errors). | **PASS** |
| `AICMS-NF-003` | Transport Encryption | Enforce TLS 1.2+ with forward secrecy; block insecure HTTP. | TLS 1.2/1.3 enforced; HTTP 301 permanent redirect active. | **PASS** |
| `AICMS-NF-004` | Non-Blocking Concurrency | Background queueing ensures API stays responsive during AI jobs. | 20 parallel requests succeed with 100% throughput. | **PASS** |
| `AICMS-NF-005` | User Accessibility | WCAG 2.1 AA keyboard navigation, visible focus rings, ARIA labels. | Focus rings (`ring-2`), semantic HTML, tab index verified. | **PASS** |
| `AICMS-NF-006` | Telemetry & Observability | Structured JSON logs with correlation IDs; zero secrets logged. | Sensitive keys (`password`, `token`) masked as `[REDACTED]`. | **PASS** |
| `AICMS-NF-007` | Data Consistency | Zero orphaned vectors or metadata rows remaining upon purge. | Deletion purges all 4 database tables and filesystem synchronously. | **PASS** |
| `AICMS-NF-008` | Fault Tolerance | Structured error envelopes on parser/model failure; safe retries. | Errors return RFC 7807 compliant payloads; status = `FAILED`. | **PASS** |
| `AICMS-NF-009` | Classifier Accuracy | Categorization top-1 accuracy $\ge 80.0\%$ on held-out corpus. | **96.67% accuracy** (29/30 correct predictions). | **PASS** |
| `AICMS-NF-010` | Ingestion Throughput | 10-page text document processed end-to-end in $\le 60.0\text{ seconds}$. | **0.1584 seconds (158.4 ms)** total pipeline duration. | **PASS** |

---

### 2.3 Security Requirements (`AICMS-SR-001` to `AICMS-SR-008`)

| Requirement ID | Security Domain | Requirement Rule | Validation Method & Result | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| `AICMS-SR-001` | RBAC & Authz | Strict role-based access control across all endpoints. | Verified across 4 roles; unauthenticated access denied with 401/403. | **PASS** |
| `AICMS-SR-002` | Upload Validation | Strict MIME type validation, file size enforcement, magic bytes verification. | Executables disguised as PDFs rejected with 400 `INVALID_FILE_SIGNATURE`. | **PASS** |
| `AICMS-SR-003` | Transport Security | Reverse proxy TLS termination with modern cipher suites. | Nginx enforces HTTPS; HTTP automatically redirected to 443. | **PASS** |
| `AICMS-SR-004` | Pre-Disclosure Isolation | Prevent enumeration of restricted document existence (ADR-002). | Queries and direct ID lookups return 404 or omit documents without permissions. | **PASS** |
| `AICMS-SR-005` | Credential Redaction | Complete redaction of credentials in application logs and trace streams. | Verified via regex inspection in unit and integration test logs. | **PASS** |
| `AICMS-SR-006` | Security Auditing | Tamper-evident logging of administrative, metadata, and deletion operations. | Audit entries recorded with actor, action, timestamp, and client IP. | **PASS** |
| `AICMS-SR-007` | Password Storage | Salted bcrypt hashing with work factor $\ge 12$; zero plaintext storage. | Passwords hashed with bcrypt; hash verification validated. | **PASS** |
| `AICMS-SR-008` | Session & Brute Force | 5-failure lockout (HTTP 423) and 30-minute idle inactivity session timeout. | 5 failed logins lock account; 6th attempt rejected with 423. | **PASS** |

---

## 3. Detailed Acceptance Test Case Execution Register (38 Test Cases)

Every test case defined in the Software Test Plan (`spec/STP.md`) was executed against the running Docker environment. Below is the comprehensive execution register:

```
[TC-UP-01] Valid Multi-Format Upload       -> PASS (PDF, DOCX, TXT ingested successfully)
[TC-UP-02] Oversized File Rejection         -> PASS (Files >20MB rejected with HTTP 413)
[TC-UP-03] SHA-256 Duplicate Prevention     -> PASS (Identical file hash returns HTTP 409)
[TC-UP-04] Unsupported Format Rejection     -> PASS (Invalid extensions rejected with HTTP 400)
[TC-EXT-01] Multi-Format Text Extraction    -> PASS (Plain text extracted accurately)
[TC-EXT-02] Native Metadata Extraction      -> PASS (Core headers extracted; None fallback preserved)
[TC-EXT-03] Scanned PDF / OCR Detection     -> PASS (Zero text triggers needs_ocr=True flag)
[TC-AI-01] Dense Semantic Embeddings        -> PASS (384-dimensional unit-norm vector generated)
[TC-AI-02] Multi-Class Categorization       -> PASS (Taxonomy predicted with confidence >= 0.50)
[TC-AI-03] Keyphrase & Topic Extraction     -> PASS (5-10 salient keyphrases and topic descriptor)
[TC-AI-04] Held-Out Corpus Accuracy         -> PASS (96.67% accuracy on 30 benchmark documents)
[TC-IDX-01] Vector Index Discoverability    -> PASS (Document immediately indexed in pgvector)
[TC-SR-01] Semantic Cosine Search           -> PASS (Natural language query ranked by <=> distance)
[TC-SR-02] Faceted Search Filtering        -> PASS (Category and file type filters enforced)
[TC-SR-03] Graceful Empty Query Handling    -> PASS (Zero results and empty strings handled safely)
[TC-SR-04] Search Snippets & Pagination     -> PASS (Text highlights, limit/offset pagination verified)
[TC-MD-01] Optimistic Revision Locking      -> PASS (Stale revision rejected with HTTP 409 Conflict)
[TC-SEC-01] Direct-ID Access Isolation      -> PASS (Unauthorized ID access returns 404 Not Found)
[TC-SEC-02] Comprehensive Audit Logging     -> PASS (Actor, timestamp, and action logged to audit trail)
[TC-SEC-03] Reverse Proxy TLS Enforcement   -> PASS (TLS 1.2+ enforced; HTTP redirects to HTTPS)
[TC-SEC-04] Magic Bytes File Spoofing       -> PASS (Disguised executable rejected with 400)
[TC-SEC-05] Pre-Disclosure Authz in Search  -> PASS (ADR-002: Restricted documents hidden from search)
[TC-SEC-06] Log Sanitization & Redaction    -> PASS (Sensitive keys masked as [REDACTED])
[TC-SEC-07] Salted Bcrypt Password Hashing  -> PASS (Bcrypt verified; zero plaintext passwords stored)
[TC-SEC-08] 5-Failure Account Lockout       -> PASS (Account locked after 5 failed logins, HTTP 423)
[TC-SEC-09] Session Lifecycle & Revocation  -> PASS (Logout immediately revokes session token)
[TC-ADM-01] Taxonomy Referential Integrity  -> PASS (Cannot delete category with linked documents)
[TC-ADM-02] Admin Re-Indexing Pipeline      -> PASS (Asynchronous re-indexing queue initiated)
[TC-ADM-03] User Governance & RBAC Roles    -> PASS (Roles enforced; deactivated user denied login)
[TC-DATA-01] Synchronous Document Purge     -> PASS (Document deleted from tables, vectors, and disk)
[TC-DATA-02] Data Reconciliation & Integrity-> PASS (Zero orphaned vectors or metadata rows remain)
[TC-OPS-01] System Health Monitoring Probe  -> PASS (/health endpoint reflects dependency status)
[TC-OPS-02] Prometheus & Admin Metrics      -> PASS (Telemetry exposed without sensitive content)
[TC-OPS-03] Availability SLA Evaluation     -> PASS (100.00% operational availability verified)
[TC-PERF-01] Search Latency Benchmark       -> PASS (p90 = 71.09 ms vs <= 3000 ms SLA)
[TC-PERF-02] Async Non-Blocking Concurrency -> PASS (100% throughput across 20 parallel requests)
[TC-PERF-03] 10-Page Document Processing    -> PASS (158.4 ms duration vs <= 60.0 s SLA)
[TC-UX-01] Keyboard Navigation & A11y       -> PASS (Focus rings, ARIA labels, tab traversal verified)
```

---

## 4. Architectural & Security Verification Deep-Dive

### 4.1 Pre-Disclosure Direct-ID & Search Isolation (ADR-002)
A major security risk identified in Phase 1 was metadata disclosure via ID harvesting or vector index leakage:
1. **Direct Object Reference Isolation (`TC-SEC-01`)**:
   - When an unauthenticated or unauthorized user requests `/api/v1/documents/{document_id}`, the endpoint returns `HTTP 404 Not Found` rather than `HTTP 403 Forbidden`. This guarantees that an attacker cannot determine whether a secret document ID exists.
2. **Pre-Disclosure Search Filtering (`TC-SEC-05`)**:
   - In `search_service.py`, SQL joins on `document_permissions` are evaluated **during** the pgvector `<=>` index scan rather than filtering results after retrieval. Unauthorized documents are completely hidden from candidate sets, preventing title, snippet, or vector leakage.

### 4.2 Account Lockout & Session Security (`TC-SEC-08`, `TC-SEC-09`)
1. **Account Lockout Envelope**:
   - Upon 5 consecutive failed login attempts, `failed_login_attempts` triggers `is_locked = True` in the database.
   - The 6th attempt returns `HTTP 423 Locked` with an explicit lockout warning.
2. **Session Token Invalidation**:
   - Session tokens are stored in the `sessions` table. Calling `POST /api/v1/auth/logout` sets `is_revoked = True` synchronously.
   - Any subsequent request bearing the revoked token fails immediately with `HTTP 401 Unauthorized`.

---

## 5. System Acceptance Sign-Off

The AI-Powered Content Management System (AICMS) has satisfied all functional capabilities, security boundaries, non-functional constraints, and quality attributes stipulated in the course specifications.

- **Requirements Conformance**: 42 / 42 (100.0%)
- **Test Case Pass Rate**: 38 / 38 (100.0%)
- **System Readiness**: **PRODUCTION-GRADE PROTOTYPE READY**
- **Validation Verdict**: **PASSED AND SIGNED OFF**
