Software Requirements Specification (SRS)

AI-Powered Content Management System (AICMS)

Version: 1.0   |   Date: 09-10-2026   |   Status: Stage 1 – Proposed design / planning

Team / Author: Shreeverdhan M  |  SRN: PES1UG24AM265
Sripada Krishna Sameer Aditya  |  SRN: PES1UG24AM285
Srivamshi Chikkireddi  |  SRN: PES1UG24AM287
Shamanth SK  |  SRN: PES1UG24AM258

Submission boundary: This submission defines requirements, proposed design, and planned verification. It does not claim that a working implementation exists or that tests have been executed.

# Revision History

| Version | Date | Author | Change summary | Approval |
| --- | --- | --- | --- | --- |
| 1.0 | 09-10-2026 | AICMS Team (Shreeverdhan M, Sripada Krishna Sameer Aditya, Srivamshi Chikkireddi, Shamanth SK) | Initial Stage 1 SRS for AICMS | Pending |


# Approvals

| Role | Name | Signature / Email | Date |
| --- | --- | --- | --- |
| Course Coordinator |  |  |  |
| Team Representative |  |  |  |


# Table of Contents

- 1. Introduction
- 2. Overall description
- 3. External interface requirements
- 4. System features (detailed)
- 5. Non-functional requirements (detailed)
- 5.1 Security objectives and requirements
- 6. Quality attributes and acceptance tests
- 7. System models and diagrams
- 8. Requirements Traceability Matrix (RTM)
# 1. Introduction

## 1.1 Purpose

This Software Requirements Specification (SRS) defines the proposed requirements, interfaces, acceptance criteria, and verification references for the AI-Powered Content Management System (AICMS).

## 1.2 Scope

AICMS is a document organization and discovery layer. It accepts supported documents, extracts text and available metadata, suggests categories, extracts keywords/topics, creates semantic embeddings, indexes searchable content, and supports natural-language search. Authorized users can review and correct AI-generated metadata. The system does not replace a source-of-truth repository or perform unrelated content authoring in this Stage 1 scope.

## 1.3 Audience

Project evaluators, end users, content editors, administrators, security reviewers, developers, testers, and future maintainers.

## 1.4 Definitions

| Term | Definition |
| --- | --- |
| AICMS | AI-Powered Content Management System. |
| Semantic search | Retrieval based on meaning/context in addition to exact keyword matches. |
| Embedding | A numeric vector representation of text used for semantic comparison. |
| OCR | Optical Character Recognition for text extraction from scanned pages. |
| RBAC | Role-Based Access Control. |
| API | Application Programming Interface. |
| RTM | Requirements Traceability Matrix. |
| PII | Personally Identifiable Information. |
| TLS | Transport Layer Security. |
| WCAG | Web Content Accessibility Guidelines. |
| p90 | 90th percentile: 90% of measured values are at or below this value. |
| STP | Software Test Plan. |


# 2. Overall Description

## 2.1 Product Perspective

AICMS is proposed as a browser-based system with a server-side API, file/object storage, metadata database, document-processing workers, AI enrichment services, and a search index. The high-level pipeline is upload and validation → extraction → AI enrichment → metadata/index update → permission-filtered semantic search. Processing is asynchronous to accommodate variable parser and model latency.

## 2.2 Major Product Functions (Detailed)

- Upload and validate supported documents; detect probable duplicates.
- Extract document text and available metadata; optionally use OCR for scans.
- Suggest categories and extract keywords/topics; generate document embeddings.
- Index eligible text and metadata for semantic retrieval.
- Accept natural-language queries and return relevance-ranked results.
- Filter results by approved metadata fields.
- Allow authorized editors to correct AI-generated metadata.
- Enforce authentication and document-level authorization.
- Maintain audit events, processing states, operational metrics, taxonomy administration, and re-index jobs.
- Support deletion from active indexes in accordance with a future-approved retention policy.
## 2.3 User Roles and Characteristics

| Role | Needs and permitted activities |
| --- | --- |
| General user | Upload permitted documents, search accessible documents, view authorized result details. |
| Content editor | Review and correct AI-generated categories, keywords, topics, and allowed metadata. |
| Administrator | Manage roles and taxonomy, request re-indexing, inspect system metrics and audit records. |
| Auditor / evaluator | Review approved audit/traceability evidence without unauthorized content modification. |


## 2.4 Operating Environment

A modern browser communicates with a secured API. The server-side environment comprises a relational metadata store, protected document storage, background job execution, document parsing/OCR adapters, an approved model/embedding service, a search index, and monitoring/logging. Deployment may be institution-approved cloud or on-premises; the final target is not yet selected.

## 2.5 Constraints and Assumptions

- Only defined and tested file types, languages, and upload-size limits will be supported; the proposed initial scope is PDF, DOCX and TXT files up to 20 MB, English language.
- AI-generated labels are suggestions, not guaranteed facts; authorized human correction is supported.
- Search quality depends on extraction quality, language, model selection, and the evaluation corpus.
- Document permission checks must occur before returning result titles, snippets, embeddings, or content.
- Any external model service must be approved for the data classification and retention policy.
# 3. External Interface Requirements

## 3.1 User Interfaces

- Upload view: supported formats, progress, processing state, and safe validation errors.
- Search view: natural-language query, filters, relevance-ranked results, snippet, category, and clear no-results state.
- Document detail/editor view: available metadata and editable AI suggestions gated by role.
- Administration view: user/role management, taxonomy, re-index job status, audit, and aggregated metrics.
- Accessibility: keyboard navigation, visible focus, clear labels, adequate contrast, and understandable error/empty states.
## 3.2 Hardware Interfaces

No dedicated end-user hardware is required beyond a browser-capable device. Optional OCR or model acceleration hardware is a deployment choice and is not an assumed Stage 1 dependency.

## 3.3 Software Interfaces

- Document parser and optional OCR adapter for agreed file types.
- Approved model interface for categorization, keyword/topic extraction, and text/query embeddings.
- Metadata database and protected file/object storage.
- Search/index service supporting vector similarity and metadata filters.
- Optional institution identity provider.
- Logging, metrics, alerting, and background-job queue interfaces.
## 3.4 Communications

Browser/API and service-to-service traffic shall use HTTPS/TLS 1.2 or higher. Protected APIs require authentication and authorization, validate inputs, apply suitable request limits, and use sanitized errors. Logs shall not contain credentials or unnecessary raw document content.

# 4. System Features (Detailed)

Each functional requirement uses a stable AICMS-F identifier and includes a priority, stakeholder/source, measurable acceptance criterion, test-case reference, and dependency note.

## 4.1 Document Intake and Validation

| Req ID | Requirement (shall...) | Type | Priority | Source / Stakeholder | Acceptance criteria / Test case reference | Comments / Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-001 | The system shall allow an authenticated user to upload a supported document. | Functional | High | Content users | A valid supported file is accepted and assigned a unique document ID. Test: TC-UP-01 | Requires authenticated session and storage. |
| AICMS-F-002 | The system shall reject unsupported file types and files exceeding the configured size limit. | Functional | High | Security / operations | The file is rejected before processing and a safe explanatory message is displayed. Test: TC-UP-02 | Allowed types and size limit must be configured. |
| AICMS-F-003 | The system shall detect probable duplicate uploads using a configured content fingerprint or metadata policy. | Functional | Medium | Content users | Duplicate content triggers the configured warning or duplicate-handling action. Test: TC-UP-03 | Duplicate policy is a configuration decision. |
| AICMS-F-004 | The system shall show each uploaded document’s processing status and any safe, actionable failure reason. | Functional | Medium | Content users | Queued, processing, completed, and failed states are distinguishable. Test: TC-UP-04 | Avoid exposing internal stack traces. |


## 4.2 Text Extraction and AI Enrichment

| Req ID | Requirement (shall...) | Type | Priority | Source / Stakeholder | Acceptance criteria / Test case reference | Comments / Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-005 | The system shall extract searchable text from supported text-based documents. | Functional | High | Content discovery | Text is linked to the correct document and can be indexed. Test: TC-EXT-01 | Depends on supported format parsers. |
| AICMS-F-006 | The system shall extract available document metadata such as title, author, creation date, and file type. | Functional | Medium | Content discovery | Available metadata is stored; unavailable fields remain empty rather than being invented. Test: TC-EXT-02 | Metadata availability varies by format. |
| AICMS-F-007 | The system shall route scanned documents through OCR when OCR is enabled for the file type. | Functional | Medium | Content discovery | OCR text is stored and uncertain/poor extraction is marked for review. Test: TC-EXT-03 | OCR may be an optional integration. |
| AICMS-F-008 | The system shall suggest one or more categories for a processable document. | Functional | High | Content editors | A category suggestion and model/version or review information is stored. Test: TC-AI-01 | Suggestions are not guaranteed to be correct. |
| AICMS-F-009 | The system shall extract representative keywords and topics from document text. | Functional | High | Content editors | Keywords/topics are stored for documents with sufficient extractable text. Test: TC-AI-02 | Language/model coverage must be evaluated. |
| AICMS-F-010 | The system shall generate semantic embeddings for eligible document content. | Functional | High | Search users | Embedding creation succeeds or a visible retryable/failed processing state is recorded. Test: TC-AI-03 | Depends on approved embedding model/service. |


## 4.3 Indexing and Semantic Search

| Req ID | Requirement (shall...) | Type | Priority | Source / Stakeholder | Acceptance criteria / Test case reference | Comments / Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-011 | The system shall index extracted text and approved metadata for search. | Functional | High | Search users | A successfully processed document becomes discoverable through the search interface. Test: TC-IDX-01 | Index writes must be idempotent. |
| AICMS-F-012 | The system shall accept natural-language queries for document discovery. | Functional | High | Search users | A valid query returns authorized results or an understandable no-results state. Test: TC-SR-01 | Depends on availability of search index. |
| AICMS-F-013 | The system shall order semantic search results using a defined relevance-scoring strategy. | Functional | High | Search users | Relevant seeded documents rank above unrelated items in the agreed test set. Test: TC-SR-02 | Ranking quality target requires benchmark corpus. |
| AICMS-F-014 | The system shall support filtering search results by supported metadata fields, including category and file type. | Functional | Medium | Search users | Returned results satisfy all selected filter conditions. Test: TC-SR-03 | Filterable fields must be defined. |
| AICMS-F-015 | The system shall show authorized result titles, relevant snippets, categories, and available metadata. | Functional | Medium | Search users | Only permitted fields appear and empty/missing metadata is handled gracefully. Test: TC-SR-04 | Authorization must be applied before formatting results. |


## 4.4 Metadata, Permissions, and Audit

| Req ID | Requirement (shall...) | Type | Priority | Source / Stakeholder | Acceptance criteria / Test case reference | Comments / Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-016 | The system shall allow authorized content editors to correct AI-generated categories, keywords, and topics. | Functional | Medium | Content editors | Changes persist and are reflected in subsequent details/search indexing. Test: TC-MD-01 | Edits require role authorization and audit. |
| AICMS-F-017 | The system shall enforce user- and document-level access permissions for reading, editing, and deleting content. | Functional | High | Data owners | Unauthorized requests reveal no document body, title, snippet, or protected metadata. Test: TC-SEC-01; TC-SEC-05 | Permission filtering applies to direct IDs and search. |
| AICMS-F-018 | The system shall audit document access and administrative actions with actor, timestamp, action, and outcome. | Functional | High | Administrators / auditors | Representative actions create searchable audit events without logging credentials or raw secrets. Test: TC-SEC-02 | Retention duration is policy-dependent. |
| AICMS-F-023 | The system shall allow a registered user to log in and log out with credentials (or the institution identity provider) and shall establish an authenticated session. | Functional | High | All users | Valid credentials create a session; invalid credentials are rejected with a generic error; logout invalidates the session. Test: TC-SEC-09 | Credential storage and lock-out per AICMS-SR-007 and SR-008. |


## 4.5 Administration, Re-indexing, Deletion, and Monitoring

| Req ID | Requirement (shall...) | Type | Priority | Source / Stakeholder | Acceptance criteria / Test case reference | Comments / Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-019 | The system shall allow an authorized administrator to manage the approved category taxonomy. | Functional | Medium | Administrators | Only administrators can create, edit, or deactivate categories; changes are validated and audited. Test: TC-ADM-01 | Taxonomy changes may trigger re-indexing. |
| AICMS-F-020 | The system shall allow an authorized administrator to request re-indexing after taxonomy or model configuration changes. | Functional | Medium | Administrators | A re-index job is queued with visible status and a traceable job identifier. Test: TC-ADM-02 | Requires background job processing. |
| AICMS-F-021 | The system shall remove a deleted document from searchable results and associated indexes, subject to approved retention policy. | Functional | High | Data owners | Deleted content is not returned by search after deletion completes, and the event is audited. Test: TC-DATA-01 | Backups/retention exceptions must be defined. |
| AICMS-F-022 | The system shall expose basic operational metrics for upload failures, processing latency, search latency, and errors. | Functional | Medium | Administrators | Authorized administrators can inspect aggregated metrics without sensitive document content. Test: TC-OPS-02 | Requires monitoring integration. |
| AICMS-F-024 | The system shall allow an authorized administrator to create and deactivate user accounts and assign roles. | Functional | High | Administrators | Only administrators can change accounts or roles; changes take effect on the user's next request and are audited. Test: TC-ADM-03 | Underpins RBAC (AICMS-SR-001); initial admin account seeded at deployment. |


# 5. Non-functional Requirements (Detailed)

The following targets are proposed acceptance targets for a later test environment. The availability target requires an operating period to measure and is not asserted as achieved.

| Req ID | Requirement | Category | Priority | Acceptance criteria / Measurement |
| --- | --- | --- | --- | --- |
| AICMS-NF-001 | For the agreed benchmark corpus and normal test load, 90% of search requests shall return results within 3 seconds. | Performance | High | p90 search latency is ≤ 3 s in the documented test environment. Test: TC-PERF-01 |
| AICMS-NF-002 | The proposed service shall target at least 99.5% monthly availability, excluding approved maintenance. | Reliability | Medium | Availability is calculable from monitoring records over a representative operating period. Test: TC-OPS-03 |
| AICMS-NF-003 | All browser-to-service and service-to-service network communications shall use HTTPS/TLS 1.2 or higher. | Security | High | Transport configuration review confirms modern TLS is enforced. Test: TC-SEC-03 |
| AICMS-NF-004 | Document parsing and AI enrichment shall run asynchronously so long-running jobs do not block unrelated upload or search requests. | Scalability | High | A long processing job is queued while independent API requests remain responsive under the agreed load. Test: TC-PERF-02 |
| AICMS-NF-005 | Core workflows shall support keyboard navigation, visible focus, accessible labels, and adequate contrast consistent with WCAG 2.1 AA where applicable. | Accessibility | Medium | Accessibility review finds no critical barrier in upload, search, and metadata-edit flows. Test: TC-UX-01 |
| AICMS-NF-006 | Logs shall include timestamps and correlation IDs but shall exclude passwords, authentication tokens, and unnecessary raw document content. | Privacy / maintainability | High | Representative logs support diagnosis without secrets or excess content. Test: TC-SEC-06 |
| AICMS-NF-007 | Document records, metadata, and search indexes shall remain consistent after successful update and deletion operations. | Data integrity | High | Consistency checks find no stale deleted entries or untracked orphan records. Test: TC-DATA-02 |
| AICMS-NF-008 | The system shall clearly identify failed AI processing and shall not silently represent incomplete enrichment as successful. | Reliability | High | Simulated model failure produces a failed/retryable state and operational event. Test: TC-OPS-01 |
| AICMS-NF-009 | For the agreed labelled test set, at least 80% of documents shall receive a correct top category suggestion (matching the reviewed label). | Accuracy / AI quality | High | Accuracy >= 80% on the held-out labelled test set. Test: TC-AI-04 |
| AICMS-NF-010 | Automatic processing of a 10-page text-based document (extraction, categorization, keywords/topics, embedding, indexing) shall complete within 60 seconds under normal test load. | Performance | Medium | Median and p90 processing time <= 60 s in the named environment. Test: TC-PERF-03 |


# 5.1 Security Objectives and Requirements

## 5.1.1 Security Objectives

1. Confidentiality: only authenticated, authorized users may discover, preview, download, edit, or delete a document and its protected metadata.

2. Integrity and accountability: metadata, indexes, permissions, and administrative changes shall be protected from unauthorized modification and critical actions shall be auditable.

3. Availability: the system shall resist abusive input and request patterns (oversized or malicious uploads, repeated invalid logins, request flooding) so that legitimate users can continue to upload and search.

## 5.1.2 Security Requirements

| Req ID | Requirement (shall...) | Type | Priority | Acceptance criteria / Test case reference |
| --- | --- | --- | --- | --- |
| AICMS-SR-001 | The system shall authenticate users and enforce least-privilege, role-based, document-level authorization for each protected operation. | Security – Access control | High | Unauthorized read/edit/delete and search attempts are denied. Test: TC-SEC-01 |
| AICMS-SR-002 | The system shall validate uploaded content and isolate parsers/OCR components when handling untrusted files. | Security – Input safety | High | Malformed, disguised, or disallowed files are rejected or safely contained. Test: TC-SEC-04 |
| AICMS-SR-003 | The system shall encrypt network traffic using HTTPS/TLS 1.2 or higher and shall disable insecure transport paths. | Security – Transport security | High | Configuration scan confirms secure transport; insecure requests are rejected or redirected safely. Test: TC-SEC-03 |
| AICMS-SR-004 | The system shall not disclose restricted document IDs, names, snippets, metadata, embeddings, or content in search results. | Security – Information protection | High | Cross-role tests reveal no restricted document information. Test: TC-SEC-05 |
| AICMS-SR-005 | The system shall store secrets in approved secret/configuration storage and shall not emit them in logs or client errors. | Security – Secrets management | High | Secret/configuration and error/log inspection reveals no credential leakage. Test: TC-SEC-06 |
| AICMS-SR-006 | The system shall record permission changes, taxonomy changes, metadata edits, and document deletion in an auditable event trail. | Security – Auditability | Medium | Each action produces an event with actor, time, action, and outcome. Test: TC-SEC-02 |
| AICMS-SR-007 | The system shall store user passwords only as salted hashes (e.g., bcrypt or Argon2) and shall never display or log them. | Security – Credential protection | High | User store contains no plaintext passwords; passwords are absent from logs and responses. Test: TC-SEC-07 |
| AICMS-SR-008 | The system shall expire inactive sessions after 30 minutes and temporarily lock an account after 5 consecutive failed login attempts. | Security – Session protection | Medium | Expired session requires re-login; the 6th attempt after five failures is blocked and audited. Test: TC-SEC-08 |


# 6. Quality Attributes and Acceptance Tests

| Quality attribute | Verification approach | Proposed acceptance / exit criterion |
| --- | --- | --- |
| Functional completeness | Run mapped functional cases from the test register. | All high-priority requirements pass; failures are logged and triaged. |
| Search relevance | Evaluate a reviewed query-document benchmark. | Evaluate about 20–50 reviewed queries; target: a relevant document in the top 5 results for at least 80% of queries. Report Precision@5 and relevant-document coverage. |
| Performance | Run a documented search workload and concurrent processing workload. | AICMS-NF-001 and AICMS-NF-004 meet the targets in the named environment. |
| Security / privacy | Run role-bypass, upload-safety, transport, secret/log, and restricted-snippet tests. | No unresolved critical/high confidentiality or access-control defect at release gate. |
| Accessibility / usability | Keyboard-only checks and accessibility review of upload/search/edit flows. | No critical blockers; documented issues are remediated or formally accepted. |
| Data integrity | Update and delete documents; reconcile database metadata against search index. | No deleted document appears in search after completed deletion; reconciliation exceptions are handled. |


Acceptance exit criteria: high-priority functional and security requirements are verified; no critical defects remain open; non-functional test results are recorded; and the RTM contains a disposition for every in-scope requirement. These are future release criteria, not current test results.

# 7. System Models and Diagrams

## 7.1 UML Use-Case Diagram 1 — General User and Content Editor

Figure 1. User/editor use cases within the AICMS system boundary.

## 7.2 UML Use-Case Diagram 2 — Administrator

Figure 2. Administration use cases; privileged actions require administrator authorization.

## 7.3 Use-Case Notes

| Use case | Precondition | Main success path | Alternative / exception |
| --- | --- | --- | --- |
| UC-01 Upload and process | User is authenticated and has upload permission. | Select file → validate → store → queue processing → extract/enrich/index → show status. | Unsupported file, duplicate policy, parser/model failure, or permission failure is shown safely. |
| UC-02 Search documents | User has an authenticated session if the repository is protected. | Enter natural-language query → embed/retrieve → apply permission filters → rank → display authorized snippets. | No results, index outage, timeout, or empty query produces a clear response. |
| UC-03 Review metadata | Editor has permission for the target document. | Review categories/keywords/topics → edit → validate → save → update index/audit. | Unauthorized edit is denied; re-index failure is visible. |
| UC-04 Administer system | Administrator is authenticated with required privileges. | Manage roles/taxonomy → request re-index → inspect audit/metrics. | Invalid changes are rejected; each administrative action is audited. |


# 8. Requirements Traceability Matrix (RTM)

Status legend: N = Not run / planned; P = test passed; A = formally accepted by the project authority. All entries are currently N because no implementation or test execution is in scope for Stage 1.

| Req ID | Requirement short | Section ref / Design Spec | Module | Test case(s) | Status (N/P/A) | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| AICMS-F-001 | Upload supported document | 4.1 / SAD §3.4 | Web UI; Application API; Document Intake | TC-UP-01 | N | Planned; Requires authenticated session and storage. |
| AICMS-F-002 | Reject invalid files | 4.1 / SAD §3.4 | Document Intake | TC-UP-02 | N | Planned; Allowed types and size limit must be configured. |
| AICMS-F-003 | Detect duplicate uploads | 4.1 / SAD §3.4 | Document Intake; Metadata Service / DB | TC-UP-03 | N | Planned; Duplicate policy is a configuration decision. |
| AICMS-F-004 | Show processing status | 4.1 / SAD §3.4 | Web UI; Async Queue / Worker | TC-UP-04 | N | Planned; Avoid exposing internal stack traces. |
| AICMS-F-005 | Extract document text | 4.2 / SAD §3.4 | Text Extraction / OCR | TC-EXT-01 | N | Planned; Depends on supported format parsers. |
| AICMS-F-006 | Extract document metadata | 4.2 / SAD §3.4 | Text Extraction / OCR; Metadata Service / DB | TC-EXT-02 | N | Planned; Metadata availability varies by format. |
| AICMS-F-007 | OCR for scanned files | 4.2 / SAD §3.4 | Text Extraction / OCR | TC-EXT-03 | N | Planned; OCR may be an optional integration. |
| AICMS-F-008 | Suggest categories | 4.2 / SAD §3.4 | AI Enrichment Pipeline | TC-AI-01; TC-AI-04 | N | Planned; Suggestions are not guaranteed to be correct. |
| AICMS-F-009 | Extract keywords and topics | 4.2 / SAD §3.4 | AI Enrichment Pipeline | TC-AI-02 | N | Planned; Language/model coverage must be evaluated. |
| AICMS-F-010 | Generate embeddings | 4.2 / SAD §3.4 | AI Enrichment Pipeline; Search Index | TC-AI-03 | N | Planned; Depends on approved embedding model/service. |
| AICMS-F-011 | Index text and metadata | 4.3 / SAD §3.4 | Search Index; Async Queue / Worker | TC-IDX-01 | N | Planned; Index writes must be idempotent. |
| AICMS-F-012 | Natural-language query | 4.3 / SAD §3.4 | Search / Retrieval API; Web UI | TC-SR-01 | N | Planned; Depends on availability of search index. |
| AICMS-F-013 | Rank results by relevance | 4.3 / SAD §3.4 | Search / Retrieval API; Search Index | TC-SR-02 | N | Planned; Ranking quality target requires benchmark corpus. |
| AICMS-F-014 | Filter search results | 4.3 / SAD §3.4 | Search / Retrieval API | TC-SR-03 | N | Planned; Filterable fields must be defined. |
| AICMS-F-015 | Show authorized result details | 4.3 / SAD §3.4 | Search / Retrieval API; Web UI | TC-SR-04 | N | Planned; Authorization must be applied before formatting results. |
| AICMS-F-016 | Correct AI-generated metadata | 4.4 / SAD §3.4 | Metadata Service / DB; Web UI | TC-MD-01 | N | Planned; Edits require role authorization and audit. |
| AICMS-F-017 | Document-level access control | 4.4 / SAD §3.4 | Application API (RBAC); Metadata Service / DB | TC-SEC-01; TC-SEC-05 | N | Planned; Permission filtering applies to direct IDs and search. |
| AICMS-F-018 | Audit access and admin actions | 4.4 / SAD §3.4 | Audit / Observability | TC-SEC-02 | N | Planned; Retention duration is policy-dependent. |
| AICMS-F-023 | Login / logout and session | 4.4 / SAD §3.4 | Web UI; Application API (authentication) | TC-SEC-09 | N | Planned; Credential rules per SR-007/SR-008. |
| AICMS-F-019 | Manage category taxonomy | 4.5 / SAD §3.4 | Admin UI; Metadata Service / DB | TC-ADM-01 | N | Planned; Taxonomy changes may trigger re-indexing. |
| AICMS-F-020 | Request re-indexing | 4.5 / SAD §3.4 | Admin UI; Async Queue / Worker; Search Index | TC-ADM-02 | N | Planned; Requires background job processing. |
| AICMS-F-021 | Remove deleted documents from index | 4.5 / SAD §3.4 | Metadata Service / DB; Search Index; Async Queue / Worker | TC-DATA-01 | N | Planned; Backups/retention exceptions must be defined. |
| AICMS-F-022 | Operational metrics | 4.5 / SAD §3.4 | Audit / Observability | TC-OPS-02 | N | Planned; Requires monitoring integration. |
| AICMS-F-024 | Manage users and roles | 4.5 / SAD §3.4 | Admin UI; Application API (RBAC); Metadata Service / DB | TC-ADM-03 | N | Planned; Underpins RBAC. |
| AICMS-NF-001 | Search p90 response time <= 3 seconds | 5 / SAD §3.4 | Search / Retrieval API; Search Index | TC-PERF-01 | N | Planned verification |
| AICMS-NF-002 | Monthly availability target >= 99.5% | 5 / SAD §3.4 | Whole system; Audit / Observability | TC-OPS-03 | N | Planned verification |
| AICMS-NF-003 | HTTPS/TLS 1.2+ for network traffic | 5 / SAD §3.4 | Application API | TC-SEC-03 | N | Planned verification |
| AICMS-NF-004 | Asynchronous processing for long-running jobs | 5 / SAD §3.4 | Async Queue / Worker | TC-PERF-02 | N | Planned verification |
| AICMS-NF-005 | Accessible keyboard, focus, labels and contrast | 5 / SAD §3.4 | Web UI | TC-UX-01 | N | Planned verification |
| AICMS-NF-006 | Sanitized logs with timestamps and correlation IDs | 5 / SAD §3.4 | Audit / Observability | TC-SEC-06 | N | Planned verification |
| AICMS-NF-007 | Consistency across records, metadata and index | 5 / SAD §3.4 | Metadata Service / DB; Search Index | TC-DATA-01; TC-DATA-02 | N | Planned verification |
| AICMS-NF-008 | Visible/retryable AI failure; no false success | 5 / SAD §3.4 | AI Enrichment Pipeline; Async Queue / Worker | TC-AI-03; TC-OPS-01; TC-UP-04 | N | Planned verification |
| AICMS-NF-009 | ≥ 80% categorization accuracy | 5 / SAD §3.4 | AI Enrichment Pipeline | TC-AI-04 | N | Planned verification |
| AICMS-NF-010 | Processing ≤ 60 s per 10-page document | 5 / SAD §3.4 | Async Queue / Worker; AI Enrichment Pipeline | TC-PERF-03 | N | Planned verification |
| AICMS-SR-001 | Authentication and least-privilege document-level RBAC | 5.1 / SAD §3.9 | Application API (RBAC) | TC-ADM-01; TC-ADM-03; TC-SEC-01; TC-SEC-09 | N | Planned verification |
| AICMS-SR-002 | Validate uploads and isolate parsers/OCR | 5.1 / SAD §3.9 | Document Intake; Text Extraction / OCR | TC-SEC-04; TC-UP-02 | N | Planned verification |
| AICMS-SR-003 | Encrypt traffic using HTTPS/TLS 1.2+ | 5.1 / SAD §3.9 | Application API; network configuration | TC-SEC-03 | N | Planned verification |
| AICMS-SR-004 | No restricted data in results or snippets | 5.1 / SAD §3.9 | Search / Retrieval API | TC-SEC-05; TC-SR-04 | N | Planned verification |
| AICMS-SR-005 | Secure secret storage; exclude secrets from logs | 5.1 / SAD §3.9 | Configuration / secrets; Audit / Observability | TC-SEC-06 | N | Planned verification |
| AICMS-SR-006 | Audit permission, taxonomy, metadata and deletion changes | 5.1 / SAD §3.9 | Audit / Observability | TC-ADM-01; TC-MD-01; TC-SEC-02 | N | Planned verification |
| AICMS-SR-007 | Salted password hashing | 5.1 / SAD §3.9 | Application API (authentication) | TC-SEC-07 | N | Planned verification |
| AICMS-SR-008 | Session expiry and account lock-out | 5.1 / SAD §3.9 | Application API (authentication) | TC-SEC-08 | N | Planned verification |


# Appendix A — References

- ISO/IEC/IEEE 29148, requirements engineering (reference framework).
- OWASP Application Security Verification Standard and File Upload guidance.
- W3C Web Content Accessibility Guidelines (WCAG) 2.1.
- Selected parser, OCR, model, database, and search documentation to be confirmed when technology decisions are made.