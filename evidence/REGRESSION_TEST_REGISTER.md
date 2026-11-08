# AICMS 38 Test Cases Regression Register & Verification Matrix

**Project**: AI-Powered Content Management System (AICMS)  
**Academic Course**: Software Engineering Mini-Project, PES University  
**Specification Reference**: `spec/STP.md` & `spec/SRS.md`  
**Execution Date**: 2026-10-31  
**Execution Environment**: Docker Compose Linux Container (`aicms_backend`)  
**Total Test Cases**: 38  
**Passed**: 38 (100%)  
**Failed**: 0  
**Blocked / Skipped**: 0  

---

## 1. Traceability & Regression Verification Matrix

| Test Case ID | Test Category | Specification & Objective | Linked SRS Requirements | Implemented Test Method | Test Verdict | Raw Evidence File |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **TC-UP-01** | Ingestion | Upload valid PDF, DOCX, and TXT files as authorized user. | `AICMS-F-001`, `AICMS-SR-001` | `test_intake_api.py::test_upload_supported_formats_tc_up_01` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-UP-02** | Ingestion | Reject oversized files exceeding configured 20 MB limit with HTTP 413. | `AICMS-F-002`, `AICMS-SR-002` | `test_intake_api.py::test_file_size_limit_rejection_tc_up_02` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-UP-03** | Ingestion | Prevent duplicate uploads via SHA-256 fingerprinting returning HTTP 409 Conflict. | `AICMS-F-003` | `test_intake_api.py::test_duplicate_document_rejection_tc_up_03` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-UP-04** | Ingestion | Reject unsupported file extensions (.csv, .zip, .exe) with HTTP 400. | `AICMS-F-002`, `AICMS-SR-002` | `test_intake_api.py::test_unsupported_format_rejection_tc_up_04` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-EXT-01** | Extraction | Extract body text from TXT, DOCX, and PDF documents. | `AICMS-F-005` | `test_extraction.py::test_txt_extraction_tc_ext_01`, `test_docx_extraction_and_metadata_tc_ext_01_02`, `test_pdf_extraction_and_metadata_tc_ext_01_02` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-EXT-02** | Extraction | Extract native metadata (title, author) with non-fabricating `None` fallback. | `AICMS-F-006` | `test_extraction.py::test_docx_extraction_and_metadata_tc_ext_01_02`, `test_pdf_extraction_and_metadata_tc_ext_01_02` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-EXT-03** | Extraction | Detect scanned documents and flag `needs_ocr=True` for secondary review. | `AICMS-F-007` | `test_extraction.py::test_pdf_extraction_and_metadata_tc_ext_01_02` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-AI-01** | AI Pipeline | Generate 384-dimensional unit-normalized semantic embeddings. | `AICMS-F-010` | `test_ai_enrichment.py::test_embedding_dimensions_and_norm_tc_ai_01` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-AI-02** | AI Pipeline | Multi-class category classification against approved taxonomy with confidence score. | `AICMS-F-008` | `test_ai_enrichment.py::test_category_classification_confidence_tc_ai_02` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-AI-03** | AI Pipeline | Extract 5–10 salient keyphrases and dominant topic descriptor via TF-IDF. | `AICMS-F-009` | `test_ai_enrichment.py::test_keyword_and_topic_extraction_tc_ai_03` | **PASS** | [`evidence/TC-EXT-01_02_AI-01_02_03.txt`](file:///d:/se_mp/evidence/TC-EXT-01_02_AI-01_02_03.txt) |
| **TC-AI-04** | AI Benchmark | Evaluate categorization accuracy on 30 held-out test documents ($\ge 80.0\%$ target). | `AICMS-F-008`, `AICMS-NF-009` | `test_ai_benchmark_tc_ai_04.py::test_ai_categorization_accuracy_benchmark_tc_ai_04` | **PASS** (96.67%) | [`evidence/TC-AI-04_categorization_benchmark.txt`](file:///d:/se_mp/evidence/TC-AI-04_categorization_benchmark.txt) |
| **TC-IDX-01** | Indexing | Vector indexing in pgvector; verify document discoverability post-indexing. | `AICMS-F-011` | `test_search_api.py::test_natural_language_semantic_search_ranking_tc_sr_01_and_tc_idx_01` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-SR-01** | Search | Execute natural language semantic query ranked by cosine similarity `<=>`. | `AICMS-F-012`, `AICMS-F-013` | `test_search_api.py::test_natural_language_semantic_search_ranking_tc_sr_01_and_tc_idx_01` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-SR-02** | Search | Multi-criteria faceted search filtering by category and file type. | `AICMS-F-014` | `test_search_api.py::test_search_filters_category_and_file_type_tc_sr_02` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-SR-03** | Search | Graceful zero-results handling and empty search input validation. | `AICMS-F-012` | `test_search_api.py::test_empty_query_and_no_results_state_tc_sr_03` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-SR-04** | Search | Paginated search results with configurable offset and limit envelopes. | `AICMS-F-015` | `test_search_api.py::test_search_pagination_tc_sr_04` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-MD-01** | Metadata | Authorized editor modifies metadata; optimistic revision locking (HTTP 409 on conflict). | `AICMS-F-016`, `AICMS-SR-006` | `test_metadata_admin_api.py::test_metadata_correction_and_concurrency_tc_md_01` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-SEC-01** | Security | Pre-disclosure direct-ID access denial: return 404 instead of 403 to prevent ID harvesting. | `AICMS-F-017`, `AICMS-SR-001` | `test_intake_api.py::test_document_lifecycle_status_and_authz_isolation` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-SEC-02** | Security | Tamper-evident audit logging for metadata edits, taxonomy changes, and purges. | `AICMS-F-018`, `AICMS-SR-006` | `test_metadata_admin_api.py::test_metadata_correction_and_concurrency_tc_md_01` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-SEC-03** | Security | Transport security enforcement: TLS 1.2+ and HTTP 301 redirection to HTTPS port 443. | `AICMS-NF-003`, `AICMS-SR-003` | `test_security_and_ux.py::test_reverse_proxy_tls_enforcement_tc_sec_03` | **PASS** | [`evidence/TC-SEC-03_UX-01.txt`](file:///d:/se_mp/evidence/TC-SEC-03_UX-01.txt) |
| **TC-SEC-04** | Security | Magic bytes validation rejecting disguised executable/zip files (.exe disguised as .pdf). | `AICMS-SR-002` | `test_intake_api.py::test_disguised_malicious_file_rejection_tc_sec_04` | **PASS** | [`evidence/TC-UP-01_02_03_04_SEC-04.txt`](file:///d:/se_mp/evidence/TC-UP-01_02_03_04_SEC-04.txt) |
| **TC-SEC-05** | Security | Pre-disclosure authorization check in vector similarity search (ADR-002). | `AICMS-F-017`, `AICMS-SR-004` | `test_search_api.py::test_predisclosure_authorization_filter_tc_sec_05` | **PASS** | [`evidence/TC-IDX-01_SR-01_04_SEC-05.txt`](file:///d:/se_mp/evidence/TC-IDX-01_SR-01_04_SEC-05.txt) |
| **TC-SEC-06** | Security | Sensitive data redaction in structured logs (passwords, tokens masked). | `AICMS-NF-006`, `AICMS-SR-005` | `test_config.py::test_structured_logging_redacts_sensitive_keys` | **PASS** | [`evidence/TC-SEC-07_08_09_ADM-03.txt`](file:///d:/se_mp/evidence/TC-SEC-07_08_09_ADM-03.txt) |
| **TC-SEC-07** | Security | Password hashing using salted bcrypt; zero plain-text storage. | `AICMS-SR-007` | `test_security.py::test_password_hashing_bcrypt_tc_sec_07` | **PASS** | [`evidence/TC-SEC-07_08_09_ADM-03.txt`](file:///d:/se_mp/evidence/TC-SEC-07_08_09_ADM-03.txt) |
| **TC-SEC-08** | Security | Account lockout after 5 consecutive failed authentications (HTTP 423 Locked). | `AICMS-SR-008` | `test_auth_api.py::test_account_lockout_after_5_failed_attempts_tc_sec_08` | **PASS** | [`evidence/TC-SEC-07_08_09_ADM-03.txt`](file:///d:/se_mp/evidence/TC-SEC-07_08_09_ADM-03.txt) |
| **TC-SEC-09** | Security | Session token lifecycle: server-side revocation on logout & 30-min idle timeout. | `AICMS-F-023`, `AICMS-SR-001` | `test_auth_api.py::test_logout_invalidates_session_tc_sec_09`, `test_session_idle_timeout_tc_sec_09` | **PASS** | [`evidence/TC-SEC-07_08_09_ADM-03.txt`](file:///d:/se_mp/evidence/TC-SEC-07_08_09_ADM-03.txt) |
| **TC-ADM-01** | Admin | Category taxonomy management with referential integrity guard against deletion of in-use tags. | `AICMS-F-019`, `AICMS-SR-001` | `test_metadata_admin_api.py::test_taxonomy_administration_rbac_and_integrity_tc_adm_01` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-ADM-02** | Admin | Admin triggers asynchronous re-indexing queue with job identifier generation. | `AICMS-F-020` | `test_metadata_admin_api.py::test_admin_reindexing_job_tc_adm_02` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-ADM-03** | Admin | RBAC role governance (admin, editor, user, auditor) and user status deactivation. | `AICMS-F-024`, `AICMS-SR-001` | `test_auth_api.py::test_role_based_access_control_tc_adm_03` | **PASS** | [`evidence/TC-SEC-07_08_09_ADM-03.txt`](file:///d:/se_mp/evidence/TC-SEC-07_08_09_ADM-03.txt) |
| **TC-DATA-01** | Data Purge | Complete document purge: removal from relational tables, pgvector index, and storage disk. | `AICMS-F-021`, `AICMS-NF-007` | `test_metadata_admin_api.py::test_document_deletion_and_vector_purge_tc_data_01_and_02` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-DATA-02** | Data Integrity | Index and database reconciliation: zero orphaned vector or metadata records remain. | `AICMS-NF-007` | `test_metadata_admin_api.py::test_document_deletion_and_vector_purge_tc_data_01_and_02` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-OPS-01** | Operations | Health monitoring probe (`/health`) with graceful degradation when services are unreachable. | `AICMS-NF-008` | `test_health.py::test_health_endpoint`, `test_health_degraded_when_service_down` | **PASS** | [`evidence/TC-OPS-01_health_check.txt`](file:///d:/se_mp/evidence/TC-OPS-01_health_check.txt) |
| **TC-OPS-02** | Operations | Prometheus and JSON telemetry endpoints exposing throughput and latency without secrets. | `AICMS-F-022` | `test_metadata_admin_api.py::test_operational_metrics_and_availability_tc_ops_02_and_03` | **PASS** | [`evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt`](file:///d:/se_mp/evidence/TC-MD-01_ADM-01_02_DATA-01_02_OPS-02_03.txt) |
| **TC-OPS-03** | Operations | Evaluation of system availability and uptime calculation against $\ge 99.50\%$ SLA target. | `AICMS-NF-002` | `test_availability_tc_ops_03.py::test_service_availability_calculation_tc_ops_03` | **PASS** (100%) | [`evidence/TC-OPS-03_availability_benchmark.txt`](file:///d:/se_mp/evidence/TC-OPS-03_availability_benchmark.txt) |
| **TC-PERF-01** | Performance | Search response latency benchmark under 50 queries: p90 $\le 3000\text{ ms}$ SLA. | `AICMS-NF-001` | `test_perf_search_tc_perf_01.py::test_search_latency_p90_benchmark_tc_perf_01` | **PASS** (71.09 ms) | [`evidence/TC-PERF-01_02_03_performance_benchmarks.txt`](file:///d:/se_mp/evidence/TC-PERF-01_02_03_performance_benchmarks.txt) |
| **TC-PERF-02** | Performance | Asynchronous pipeline queue concurrency: non-blocking API access under parallel operations. | `AICMS-NF-004` | `test_perf_async_concurrency_tc_perf_02.py::test_async_pipeline_nonblocking_concurrency_tc_perf_02` | **PASS** (100% succ) | [`evidence/TC-PERF-01_02_03_performance_benchmarks.txt`](file:///d:/se_mp/evidence/TC-PERF-01_02_03_performance_benchmarks.txt) |
| **TC-PERF-03** | Performance | 10-page document end-to-end processing benchmark: execution time $\le 60.0\text{ s}$ SLA. | `AICMS-NF-010` | `test_perf_end_to_end_tc_perf_03.py::test_ten_page_document_processing_time_tc_perf_03` | **PASS** (0.1584 s) | [`evidence/TC-PERF-01_02_03_performance_benchmarks.txt`](file:///d:/se_mp/evidence/TC-PERF-01_02_03_performance_benchmarks.txt) |
| **TC-UX-01** | Frontend/UX | Keyboard accessibility, tab navigation, and focus ring visibility across UI dashboard. | `AICMS-NF-005` | `test_security_and_ux.py::test_frontend_accessibility_and_contrast_tc_ux_01` | **PASS** | [`evidence/TC-SEC-03_UX-01.txt`](file:///d:/se_mp/evidence/TC-SEC-03_UX-01.txt) |

---

## 2. Requirement Traceability Matrix (42 SRS Requirements)

| Requirement ID | Requirement Summary | Validated by Test Cases | Verdict |
| :--- | :--- | :--- | :---: |
| `AICMS-F-001` | Supported format upload (PDF, DOCX, TXT) | `TC-UP-01` | **PASS** |
| `AICMS-F-002` | Unsupported file and size limit rejection | `TC-UP-02`, `TC-UP-04`, `TC-SEC-04` | **PASS** |
| `AICMS-F-003` | Duplicate document detection via SHA-256 | `TC-UP-03` | **PASS** |
| `AICMS-F-004` | Visible document processing lifecycle states | `TC-UP-04`, `TC-OPS-01` | **PASS** |
| `AICMS-F-005` | Text body extraction from supported files | `TC-EXT-01` | **PASS** |
| `AICMS-F-006` | Native metadata parsing with None fallback | `TC-EXT-02` | **PASS** |
| `AICMS-F-007` | Scanned PDF detection and OCR fallback flag | `TC-EXT-03` | **PASS** |
| `AICMS-F-008` | Automated multi-class categorization | `TC-AI-02`, `TC-AI-04` | **PASS** |
| `AICMS-F-009` | Keyphrase and topic descriptor extraction | `TC-AI-03` | **PASS** |
| `AICMS-F-010` | Dense semantic embedding generation | `TC-AI-01`, `TC-AI-03` | **PASS** |
| `AICMS-F-011` | Vector index persistence and discoverability | `TC-IDX-01` | **PASS** |
| `AICMS-F-012` | Natural language query search engine | `TC-SR-01`, `TC-SR-03` | **PASS** |
| `AICMS-F-013` | Semantic cosine similarity ranking | `TC-SR-01`, `TC-SR-02` | **PASS** |
| `AICMS-F-014` | Faceted search filtering by category & type | `TC-SR-02`, `TC-SR-03` | **PASS** |
| `AICMS-F-015` | Snippet generation and paginated search | `TC-SR-04` | **PASS** |
| `AICMS-F-016` | Optimistic locking metadata correction | `TC-MD-01` | **PASS** |
| `AICMS-F-017` | Direct object ID authorization protection | `TC-SEC-01`, `TC-SEC-05` | **PASS** |
| `AICMS-F-018` | Immutable tamper-evident audit logging | `TC-SEC-02` | **PASS** |
| `AICMS-F-019` | Admin taxonomy management & integrity | `TC-ADM-01` | **PASS** |
| `AICMS-F-020` | Bulk re-indexing pipeline execution | `TC-ADM-02` | **PASS** |
| `AICMS-F-021` | Document deletion with synchronous purge | `TC-DATA-01` | **PASS** |
| `AICMS-F-022` | Telemetry & operational metrics endpoint | `TC-OPS-02` | **PASS** |
| `AICMS-F-023` | Server-side session token management | `TC-SEC-09` | **PASS** |
| `AICMS-F-024` | User role assignment and lifecycle state | `TC-ADM-03` | **PASS** |
| `AICMS-NF-001` | Search response latency $\le 3\text{ seconds}$ | `TC-PERF-01` | **PASS** |
| `AICMS-NF-002` | Service availability $\ge 99.50\%$ SLA | `TC-OPS-03` | **PASS** |
| `AICMS-NF-003` | TLS 1.2+ secure transport encryption | `TC-SEC-03` | **PASS** |
| `AICMS-NF-004` | Asynchronous non-blocking queueing | `TC-PERF-02` | **PASS** |
| `AICMS-NF-005` | WCAG 2.1 AA keyboard accessibility | `TC-UX-01` | **PASS** |
| `AICMS-NF-006` | Log redaction and trace correlation IDs | `TC-SEC-06` | **PASS** |
| `AICMS-NF-007` | Zero-orphan data consistency on purge | `TC-DATA-01`, `TC-DATA-02` | **PASS** |
| `AICMS-NF-008` | Safe failure recovery without silent errors | `TC-UP-04`, `TC-OPS-01` | **PASS** |
| `AICMS-NF-009` | Categorization classification accuracy $\ge 80\%$ | `TC-AI-04` | **PASS** |
| `AICMS-NF-010` | 10-page document processing $\le 60\text{ seconds}$ | `TC-PERF-03` | **PASS** |
| `AICMS-SR-001` | Role-based authorization & permission checks | `TC-SEC-01`, `TC-SEC-09`, `TC-ADM-01`, `TC-ADM-03` | **PASS** |
| `AICMS-SR-002` | File validation, size limits & magic bytes | `TC-UP-02`, `TC-UP-04`, `TC-SEC-04` | **PASS** |
| `AICMS-SR-003` | Transport layer encryption (HTTPS TLS 1.2+) | `TC-SEC-03` | **PASS** |
| `AICMS-SR-004` | Pre-disclosure authorization filtering (ADR-002) | `TC-SEC-01`, `TC-SEC-05` | **PASS** |
| `AICMS-SR-005` | Redaction of credentials from all log outputs | `TC-SEC-06` | **PASS** |
| `AICMS-SR-006` | Audit trail for security-critical operations | `TC-MD-01`, `TC-SEC-02`, `TC-ADM-01` | **PASS** |
| `AICMS-SR-007` | Salted bcrypt password hashing | `TC-SEC-07` | **PASS** |
| `AICMS-SR-008` | 5-failure lockout & 30-min idle timeout | `TC-SEC-08`, `TC-SEC-09` | **PASS** |
