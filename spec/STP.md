Software Test Plan (STP)

AI-Powered Content Management System (AICMS)

Version: 1.0   |   Date: 09-10-2026   |   Status: Stage 1 – Proposed design / planning

Team / Author: Shreeverdhan M  |  SRN: PES1UG24AM265
Sripada Krishna Sameer Aditya  |  SRN: PES1UG24AM285
Srivamshi Chikkireddi  |  SRN: PES1UG24AM287
Shamanth SK  |  SRN: PES1UG24AM258

Submission boundary: This submission defines requirements, proposed design, and planned verification. It does not claim that a working implementation exists or that tests have been executed.

# Document Control

| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.0 | 09-10-2026 | AICMS Team (Shreeverdhan M, Sripada Krishna Sameer Aditya, Srivamshi Chikkireddi, Shamanth SK) | Stage 1 plan; test execution pending |


# 1. Introduction

## 1.1 Purpose

This Software Test Plan defines planned verification for AICMS, including scope, approach, environment, schedule, roles, risks, test data, case traceability, and exit criteria. It is a planning artifact; no implementation or execution result is claimed.

## 1.2 Scope

Testing is planned for document upload/validation, duplicate handling, text extraction/OCR, AI category and keyword/topic suggestions, embeddings, indexing, semantic search, filtering/ranking, metadata correction, authorization, audit, administration, deletion consistency, performance, accessibility, and error recovery.

## 1.3 References and Definitions

References: AICMS SRS v1.0 and AICMS Software Architecture and Design Specification v1.0. Definitions: SRS – Software Requirements Specification; STP – Software Test Plan; RTM – Requirements Traceability Matrix; OCR – Optical Character Recognition; RBAC – Role-Based Access Control; Precision@5 – fraction of the top five retrieved results judged relevant.

# 2. Test Items

- Web UI: upload, processing status, search, result display, metadata review, administrator views.
- Application APIs: document upload/detail, search, metadata update, re-index, deletion.
- Intake/validation, file/object storage, metadata database, and duplicate policy.
- Text extraction/OCR and asynchronous processing queue/worker.
- AI enrichment: categories, keywords/topics, embeddings, failure states.
- Search/retrieval: lexical/vector index, ranking, filters, authorization-before-disclosure; security/audit, metrics, logs, configuration, and recovery paths.
# 3. Features to be Tested

| Feature / SRS requirement IDs | Planned verification |
| --- | --- |
| AICMS-F-001–004 | Valid upload, invalid/oversize file, duplicate policy, visible processing states. |
| AICMS-F-005–007 | Text extraction, metadata extraction, OCR behavior and quality flags. |
| AICMS-F-008–010 | Category suggestions, keyword/topic output, embedding creation and model-failure behavior. |
| AICMS-F-011–015 | Indexing, natural-language query, ranking, filters, results/snippets. |
| AICMS-F-016–018, 023; AICMS-SR-001,004,006 | Metadata correction, login/logout, access enforcement, audit completeness, no search disclosure. |
| AICMS-F-019–022, 024 | Taxonomy changes, re-index jobs, deletion/index consistency, operational metrics, user and role administration. |
| AICMS-NF-001–010; AICMS-SR-002,003,005,007,008 | Latency, asynchronous responsiveness, accessibility, data integrity, secure uploads, TLS, and secret/log hygiene; categorization accuracy (≥ 80%), 10-page processing time (≤ 60 s), password storage, session expiry and login lock-out. |


# 4. Features Not to be Tested

- Correctness of third-party model internals beyond system-level evaluation of observable AICMS outputs.
- Provider internals of external identity, storage, model, or search services beyond their integration contracts.
- Production monthly availability before a representative deployment and observation period exist.
- File formats and languages explicitly outside the agreed supported scope.
- Real sensitive production documents; tests use synthetic or formally approved non-sensitive data.
# 5. Test Approach / Strategy

## 5.1 Test Levels and Types

- Unit tests: validators, metadata rules, permission decisions, ranking/filter logic, job-state transitions.
- Integration tests: API ↔ storage/database, parser/OCR adapter, model interface, queue/worker, and search index.
- System/end-to-end tests: upload → process → search → metadata edit → re-index/delete.
- Regression tests: re-run the affected smoke and high-priority cases after each defect fix or model/index configuration change.
- Acceptance tests (UAT): project representative runs the end-to-end flows against the acceptance criteria in SRS section 6.
- Negative tests: malformed/unsupported files, empty query, invalid payload, missing role, denied document, and model/index failure.
- Security tests: role bypass, direct document-ID access, restricted snippet leakage, file validation, TLS, secret/log inspection, rate limits.
- Performance tests: p90 search latency, concurrency, queue delay, large permitted upload, and job throughput.
- Accessibility tests: keyboard-only use, visible focus, labels, contrast, and safe errors in core workflows.
- AI/search quality tests: labelled query-document corpus; review category/keyword outcomes and report Precision@5 and relevant-document coverage.
## 5.2 Entry Criteria

- SRS, SAD, and test cases are reviewed and the target behavior is agreed.
- A testable implementation build and isolated environment are available in a later stage.
- Synthetic files, role-specific test accounts, expected metadata, and labelled search judgments are prepared.
- Required model/search/storage integrations or deterministic service stubs are configured securely.
- File types, size limits, languages, search benchmark, performance load, and accepted quality thresholds are documented.
## 5.3 Exit Criteria

- 100% of planned high-priority cases are executed or have an approved waiver with rationale.
- No unresolved critical defect remains; high-severity issues are dispositioned by the project representative.
- All high-priority functional and security requirements pass their acceptance criteria.
- No unresolved critical/high access-control or data-disclosure issue remains.
- Performance and search-quality results are recorded against the named dataset/environment; categorization accuracy ≥ 80% and a relevant document in the top 5 results for ≥ 80% of benchmark queries are achieved.
- RTM includes a status/evidence reference for every in-scope requirement.
## 5.4 Security Validation

- Validate authentication and role/document authorization, including direct ID, result title, snippet, metadata, edit, and deletion attempts.
- Verify unsupported, oversize, malformed, and disguised file handling; check parser/OCR isolation where available.
- Check HTTPS/TLS 1.2+ enforcement and ensure insecure transport is not accepted.
- Inspect application logs and client errors for credentials, tokens, unnecessary content, or sensitive embeddings.
- Verify audit coverage for access-relevant and administrative actions.
- Check rate limiting and safe errors for malformed or high-volume requests.
# 6. Test Environment

| Area | Planned setup |
| --- | --- |
| Hardware | Developer/test workstation (about 4 CPU cores, 8–16 GB RAM, no GPU required) and agreed hosting environment; no dedicated hardware is required. |
| Software | Application/API build, browser, metadata database, file/object storage, queue/worker, search index, and parser/OCR/model adapters or deterministic stubs. |
| Tools | Postman or equivalent for API checks; pytest/JUnit or equivalent for unit/integration tests; JMeter/k6 for load testing; browser accessibility tools; issue tracker. Tool choices are provisional. |
| Accounts | At minimum: general user with access, general user without access to a protected document, content editor, and administrator. Use synthetic identities. |
| Documents | Synthetic documents in each supported format, scanned samples if OCR is in scope, metadata-rich files, duplicate pairs, malformed files, and varied topics/categories. Proposed size: about 300 labelled documents (PDF/DOCX/TXT) in 5–6 categories, split about 70/30 into training and test sets. |
| Search corpus | About 20–50 reviewed natural-language queries with relevance labels and relevant/irrelevant documents. Record corpus, model, index, and configuration versions. |


# 7. Test Schedule

The schedule below is relative to build readiness and plan approval; the windows are indicative planning estimates, not claims of completed work.

| Milestone | Indicative timing | Output / gate |
| --- | --- | --- |
| Review requirements and design test cases | Week 1 after approval | Approved cases, RTM mapping, and benchmark plan. |
| Prepare test data and environment | Weeks 1–2 | Environment checklist, synthetic corpus, service stubs. |
| Unit and integration testing | Weeks 2–3 | Execution evidence and defect records. |
| System, security, and accessibility testing | Weeks 3–4 | End-to-end, security, and accessibility results. |
| Performance and AI/search quality evaluation | Week 4 | Benchmark results with dataset/configuration detail. |
| Regression and acceptance review | Week 5 | Updated RTM, open-defect disposition, test summary and sign-off. |


# 8. Test Deliverables

| Deliverable | Stage 1 disposition |
| --- | --- |
| Software Test Plan | Included in this submission. |
| Manual test cases / test case register | Included in Section 13 with expected results and requirement mappings. |
| Automated test scripts | Future deliverable after implementation language and APIs are finalized. |
| Test data catalogue | Specified in Section 6; synthetic files to be prepared for execution. |
| Test execution logs and evidence | Future deliverable; no test has been run in Stage 1. |
| Defect reports and retest records | Future deliverable if execution identifies defects. |
| Final Test Summary Report | Future deliverable after planned test execution. |


# 9. Roles and Responsibilities

| Role | Name | Responsibility |
| --- | --- | --- |
| QA / Test Lead | Shreeverdhan M | Own test plan, case coverage, execution coordination, status, summary reporting, and coordinate specialist security review where available. |
| Test Engineer | Sripada Krishna Sameer Aditya | Prepare test data, execute cases, capture evidence, log defects, and retest fixes. |
| Developer | Srivamshi Chikkireddi | Provide testable builds, support diagnosis, fix defects, and supply release notes. |
| Project / Product Representative | Shamanth SK | Clarify expected behavior, approve acceptance criteria and defect dispositions. |


# 10. Risks and Mitigation

| Risk | Mitigation |
| --- | --- |
| No representative document corpus | Create diverse synthetic samples and label a query-document relevance benchmark before judging search quality. |
| AI output varies by model or run | Record model/configuration version, define evaluation data, and treat enrichment as a suggestion. |
| Delayed build/environment | Prepare the case register and data in advance; do not mark unexecuted cases as passed. |
| External model/index outage | Use controlled stubs for deterministic tests and separately test timeouts, retries, and failure states. |
| Metadata/index drift after deletion | Test deletion and re-indexing, compare state across stores, and include reconciliation checks. |
| Restricted data leaks via search | Prioritize cross-role tests for IDs, titles, snippets, metadata, vectors, and file retrieval. |


# 11. Assumptions and Dependencies

- Supported formats, upload limits, and target languages will be agreed before test execution.
- A stable test build, isolated test environment, safe credentials, and synthetic data will be provided at Stage 2.
- AI/model and search-provider choices may change; acceptance tests should emphasize observable contracts.
- Search quality targets and the benchmark corpus must be agreed before results can be judged.
- The proposed calendar is dependent on build readiness, team availability, and upstream service access.
# 12. Suspension and Resumption Criteria

## 12.1 Suspend Testing If

- The test environment is unavailable for more than four working hours and no approved backup is available.
- The build is unstable enough to block more than 30% of planned cases because of a common failure.
- Test data or credentials may expose actual sensitive information.
- A critical defect makes continued testing unsafe or invalidates other results.
## 12.2 Resume Testing When

- Blocking defects are fixed or an explicitly approved workaround is documented.
- Environment health and smoke checks pass; required dependencies are stable.
- Credentials and test data are verified safe and valid.
- Tests affected by the failure are re-run and previous results are corrected where necessary.
# 13. Test Case Management and Traceability

Case IDs are stable and match the SRS acceptance references and RTM. Initial status for every case is “Not Run – planned.” During Stage 2, record execution date, build/model/index version, tester, actual result, evidence location, and defect ID. Status values: N = Not Run, P = Passed, F = Failed, B = Blocked, W = Waived.

| Test ID | Scenario / steps summary | Linked requirement(s) | Expected result | Initial status |
| --- | --- | --- | --- | --- |
| TC-UP-01 | Upload a valid supported document as an authorized user. | AICMS-F-001 | 202/accepted document ID returned; status is QUEUED or PROCESSING. | N – planned |
| TC-UP-02 | Upload an unsupported file and a file larger than configured limit. | AICMS-F-002; AICMS-SR-002 | Each invalid upload is rejected safely and not indexed. | N – planned |
| TC-UP-03 | Upload the same content twice under configured duplicate policy. | AICMS-F-003 | Configured duplicate warning or action occurs; no unexplained duplicate index entry. | N – planned |
| TC-UP-04 | Observe status from upload through completion; simulate processing error. | AICMS-F-004; AICMS-NF-008 | States are visible; failure is not marked complete and has a safe retry/error state. | N – planned |
| TC-EXT-01 | Upload text-based supported file with known body text. | AICMS-F-005 | Extracted text matches the expected content sufficiently for indexing. | N – planned |
| TC-EXT-02 | Upload document with title/author/date metadata and one without metadata. | AICMS-F-006 | Available metadata is stored; missing values remain empty rather than fabricated. | N – planned |
| TC-EXT-03 | Upload supported scan with OCR enabled and a low-quality scan. | AICMS-F-007 | OCR text is stored; poor extraction is marked for review/quality warning. | N – planned |
| TC-AI-01 | Process a labelled document whose topic/category is known. | AICMS-F-008 | A category suggestion and the chosen model/version or review metadata are recorded. | N – planned |
| TC-AI-02 | Process documents with distinct topics and inspect keywords/topics. | AICMS-F-009 | Representative terms/topics are stored; quality is judged against agreed examples. | N – planned |
| TC-AI-03 | Process eligible text and simulate embedding provider failure. | AICMS-F-010; AICMS-NF-008 | Embedding/index job succeeds or shows a visible retryable failure state. | N – planned |
| TC-AI-04 | Run the trained classifier on the held-out labelled test set (about 30% of the corpus) and compare suggestions with the reviewed labels. | AICMS-F-008; AICMS-NF-009 | At least 80% of test documents receive the correct category; per-category results are recorded. | N – planned |
| TC-IDX-01 | Search for exact and semantic concepts in a successfully processed document. | AICMS-F-011 | Document becomes discoverable after indexing completes. | N – planned |
| TC-SR-01 | Submit a valid natural-language query with expected results. | AICMS-F-012 | Authorized results or explicit no-results state is returned. | N – planned |
| TC-SR-02 | Use a reviewed query-document relevance set to inspect result order. | AICMS-F-013 | Relevant seeded documents rank above unrelated items according to agreed metric. | N – planned |
| TC-SR-03 | Combine category and file-type filters. | AICMS-F-014 | Every returned result satisfies all selected filters. | N – planned |
| TC-SR-04 | Inspect result title, snippet, category, missing metadata, and permission rules. | AICMS-F-015; AICMS-SR-004 | Fields are clear, safe, and only from authorized documents. | N – planned |
| TC-MD-01 | Editor modifies categories/keywords; non-editor attempts the same. | AICMS-F-016; AICMS-SR-006 | Authorized update persists and is audited; unauthorized edit is denied. | N – planned |
| TC-SEC-01 | Attempt read/edit/delete via direct document ID without permission. | AICMS-F-017; AICMS-SR-001 | Unauthorized operations are denied without revealing protected data. | N – planned |
| TC-SEC-02 | Perform metadata edit, taxonomy change, role change, and deletion. | AICMS-F-018; AICMS-SR-006 | Each action produces audit event with actor/time/action/outcome, no secrets. | N – planned |
| TC-SEC-03 | Inspect browser/API and service transport configuration. | AICMS-NF-003; AICMS-SR-003 | HTTPS/TLS 1.2+ enforced and insecure transport path disabled. | N – planned |
| TC-SEC-04 | Submit malformed/disguised content and supported large file. | AICMS-SR-002 | Unsafe files are rejected/isolated; valid in-limit file remains processable. | N – planned |
| TC-SEC-05 | Search as a user without access to a restricted document. | AICMS-F-017; AICMS-SR-004 | Restricted ID, title, snippet, metadata, embedding, and content are not exposed. | N – planned |
| TC-SEC-06 | Inspect server logs and client errors after auth/model/parser failures. | AICMS-NF-006; AICMS-SR-005 | No password/token or unnecessary raw document contents; correlation IDs support diagnosis. | N – planned |
| TC-SEC-07 | Inspect the user store, logs and API responses after registering users and logging in. | AICMS-SR-007 | Passwords exist only as salted hashes; none appear in logs or responses. | N – planned |
| TC-SEC-08 | Leave a session idle for 30 minutes; then make five consecutive failed logins followed by a sixth attempt. | AICMS-SR-008 | Idle session requires re-login; the sixth attempt is blocked temporarily and an audit event is recorded. | N – planned |
| TC-SEC-09 | Log in with valid and invalid credentials; log out; reuse the old session token. | AICMS-F-023; AICMS-SR-001 | Valid login creates a session; invalid login shows a generic error; logout invalidates the token. | N – planned |
| TC-ADM-01 | Non-admin and admin each attempt a category taxonomy change. | AICMS-F-019; AICMS-SR-001; AICMS-SR-006 | Only authorized admin change succeeds and generates audit event. | N – planned |
| TC-ADM-02 | Admin requests re-indexing following taxonomy/model configuration update. | AICMS-F-020 | Job ID/status is returned and eligible documents are queued. | N – planned |
| TC-ADM-03 | Admin creates a user, assigns and changes a role, and deactivates the account; non-admin attempts the same. | AICMS-F-024; AICMS-SR-001 | Only admin changes succeed, take effect on the next request, and are audited; deactivated user cannot log in. | N – planned |
| TC-DATA-01 | Delete a document then query matching terms. | AICMS-F-021; AICMS-NF-007 | After deletion completes, deleted document no longer appears in active search and action is audited. | N – planned |
| TC-OPS-01 | Simulate parser or model service failure. | AICMS-NF-008 | Failure state, safe error, and operational event appear; no false success. | N – planned |
| TC-OPS-02 | Inspect metrics for upload errors, job duration, search latency, and service errors. | AICMS-F-022 | Authorized admin can view aggregates without document secrets/content. | N – planned |
| TC-OPS-03 | Evaluate uptime measurement over a representative observation window. | AICMS-NF-002 | Availability percentage can be calculated with agreed maintenance treatment. | N – planned |
| TC-PERF-01 | Run the approved natural-language search load against the benchmark corpus. | AICMS-NF-001 | 90th percentile search response time ≤ 3 seconds under named conditions. | N – planned |
| TC-PERF-02 | Run long AI processing while making independent search/upload requests. | AICMS-NF-004 | Long job is queued and unrelated requests remain within agreed responsiveness targets. | N – planned |
| TC-PERF-03 | Upload a 10-page text-based document under normal test load and time extraction, enrichment and indexing to completion. | AICMS-NF-010 | Median and p90 processing time ≤ 60 seconds in the named environment. | N – planned |
| TC-UX-01 | Complete upload, search, filter, and metadata review with keyboard only. | AICMS-NF-005 | Focus is visible; controls are labelled and core flows can be operated. | N – planned |
| TC-DATA-02 | Modify metadata, re-index, delete, and run database/index reconciliation. | AICMS-NF-007 | No unexplained stale index entry or orphaned active record remains. | N – planned |


## 13.1 Test Data Catalogue

| Data group | Representative cases | Purpose / safety constraints |
| --- | --- | --- |
| Valid document corpus | At least two text documents per agreed format, varied topics, metadata present/absent. | Verify extraction, metadata, categorization, topic extraction, and indexing. Use synthetic/public-safe content. |
| Negative upload samples | Wrong extension/content signature, malformed file, over-limit file, duplicate pairs. | Validate intake safety and duplicate policy; never use malicious production data. |
| OCR set | Clear scan, skewed/low contrast scan, image-only page. | Check OCR route and quality-warning behavior if OCR is in scope. |
| Access-control records | User A allowed, User B not allowed, editor, administrator; at least one restricted document. | Exercise least privilege and prevent disclosure of restricted search results. |
| Search benchmark | Natural-language queries with reviewed relevant and irrelevant documents/labels. | Evaluate ranking with Precision@5/relevant coverage; record reviewer and version. |
| Failure simulations | Model unavailable, parser error, search index timeout, queue retry. | Verify sanitized errors, retry/failure state, audit/metrics, and no false success. |


# 14. Test Metrics and Reporting

- Execution progress = executed cases / planned cases × 100%.
- Pass rate = passed cases / executed cases × 100%; blocked and waived cases are reported separately.
- Requirement coverage = in-scope requirements mapped to test cases / total in-scope requirements × 100%.
- Defects: count by severity, age, component, reopen/retest status, and requirement impact.
- Search quality: Precision@5, relevant-result coverage (target: relevant document in the top 5 for ≥ 80% of queries), and category/keyword reviewer assessment on the agreed corpus.
- Categorization accuracy = documents with the correct top category / total labelled test documents × 100% (target ≥ 80%).
- Performance: p50/p90 search latency, error rate, queue delay, extraction/enrichment duration, and concurrency profile.
- Reports: execution status, defect summary, security findings, performance/relevance benchmark, and final test summary.
# 15. Approvals

| Role | Name | Signature / Date |
| --- | --- | --- |
| QA / Test Lead |  |  |
| Project Representative |  |  |
| Course Coordinator |  |  |

