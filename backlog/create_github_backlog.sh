#!/usr/bin/env bash
# create_github_backlog.sh
# Script to create GitHub Issues for AICMS backlog using GitHub CLI (gh)
# Usage: ./create_github_backlog.sh <repo-owner/repo-name>

REPO="${1:-}"

if [ -z "$REPO" ]; then
    echo "Usage: ./create_github_backlog.sh <owner/repo>"
    echo "Example: ./create_github_backlog.sh svmx1718x/AI-Powered-Content-Management-System"
    exit 1
fi

echo "Creating backlog issues in $REPO..."

# Milestone definitions
gh milestone create -R "$REPO" --title "Sprint-1" --description "Core pipeline, Auth, Intake, AI Enrichment, Search" || true
gh milestone create -R "$REPO" --title "Sprint-2" --description "Metadata, Admin, Deletion, UI, Security, Freeze" || true
gh milestone create -R "$REPO" --title "Sprint-3" --description "Spillover, Benchmarks, 38 TCs, Reports" || true

# Helper to create issue
create_issue() {
    local title="$1"
    local body="$2"
    local milestone="$3"
    local label="$4"
    gh issue create -R "$REPO" --title "$title" --body "$body" --milestone "$milestone" --label "$label"
}

create_issue "[US-01] User Authentication, Session Security & Lockout" \
"**Requirements**: AICMS-F-023, AICMS-F-024, AICMS-SR-001, AICMS-SR-007, AICMS-SR-008
**Points**: 5 | **Assignee**: Srivamshi Chikkireddi
**Acceptance Criteria**: Passwords hashed with bcrypt; server-side session token revoked on logout; 30-min idle timeout; account locked after 5 failed login attempts with 423 status returned on 6th attempt; all events audited.
**Linked TCs**: TC-SEC-07, TC-SEC-08, TC-SEC-09, TC-ADM-03" \
"Sprint-1" "security,backend"

create_issue "[US-02] Secure Document Intake, Validation & Deduplication" \
"**Requirements**: AICMS-F-001, AICMS-F-002, AICMS-F-003, AICMS-F-004, AICMS-SR-002, AICMS-SR-004
**Points**: 5 | **Assignee**: Srivamshi Chikkireddi
**Acceptance Criteria**: Accepts PDF, DOCX, TXT <= 20MB; validates extension and magic bytes; rejects disguised files; computes SHA-256 and returns 409 on duplicate upload; tracks QUEUED/PROCESSING/COMPLETED/FAILED lifecycle.
**Linked TCs**: TC-UP-01, TC-UP-02, TC-UP-03, TC-UP-04, TC-SEC-04" \
"Sprint-1" "feature,backend"

create_issue "[US-03] Document Parsing and Author/Title Metadata Extraction" \
"**Requirements**: AICMS-F-005, AICMS-F-006, AICMS-F-007
**Points**: 3 | **Assignee**: Sripada Krishna Sameer Aditya
**Acceptance Criteria**: Extracts full text and native metadata (title, author, creation date) across supported formats; missing metadata stays null/empty; parser runs in bounded execution sandbox; OCR routing fallback provided.
**Linked TCs**: TC-EXT-01, TC-EXT-02, TC-EXT-03" \
"Sprint-1" "feature,backend"

create_issue "[US-04] AI Semantic Embeddings, Categorization & Keyword Extraction" \
"**Requirements**: AICMS-F-008, AICMS-F-009, AICMS-F-010, AICMS-NF-008
**Points**: 5 | **Assignee**: Shreeverdhan M
**Acceptance Criteria**: Generates 384-dim embeddings via all-MiniLM-L6-v2; categorizes text using classifier with confidence score; extracts 5-10 keywords via TF-IDF/keyphrase; stores model name and version; supports simulated failure flags.
**Linked TCs**: TC-AI-01, TC-AI-02, TC-AI-03, TC-AI-04" \
"Sprint-1" "ai,ml"

create_issue "[US-05] Vector Indexing, Semantic Search & Access Control Filter" \
"**Requirements**: AICMS-F-011, AICMS-F-012, AICMS-F-013, AICMS-F-014, AICMS-F-015, AICMS-SR-005, AICMS-NF-001
**Points**: 8 | **Assignee**: Srivamshi Chikkireddi
**Acceptance Criteria**: Indexes document embeddings in vector store; converts natural language query into embedding; ranks by cosine similarity; strictly performs user authorization before returning snippet/title (ADR-002); supports category/file-type filters, pagination, and empty state.
**Linked TCs**: TC-IDX-01, TC-SR-01, TC-SR-02, TC-SR-03, TC-SR-04, TC-SEC-05" \
"Sprint-1" "feature,search"

create_issue "[US-06] Metadata Review, Editing & Optimistic Concurrency Control" \
"**Requirements**: AICMS-F-016, AICMS-F-017, AICMS-F-018
**Points**: 3 | **Assignee**: Shamanth SK
**Acceptance Criteria**: Authorized users can view and edit title, author, category, keywords; AI-generated items clearly labelled; PATCH with version revision checks detects conflicts and returns 409; logs revision history in audit log.
**Linked TCs**: TC-MD-01, TC-DATA-01" \
"Sprint-2" "feature,backend"

create_issue "[US-07] Category Taxonomy Management & Collection Re-Indexing" \
"**Requirements**: AICMS-F-019, AICMS-F-020
**Points**: 3 | **Assignee**: Shamanth SK
**Acceptance Criteria**: Admin can perform CRUD on category taxonomy; re-indexing job endpoint triggers batch re-embedding with unique job_id and queryable progress status.
**Linked TCs**: TC-ADM-01, TC-ADM-02" \
"Sprint-2" "admin,backend"

create_issue "[US-08] Secure Document Deletion & Vector Purge" \
"**Requirements**: AICMS-F-021, AICMS-SR-006
**Points**: 3 | **Assignee**: Srivamshi Chikkireddi
**Acceptance Criteria**: Deleting a document purges stored file, database metadata, vector index embeddings, and permission entries; emits audit event; purged documents immediately disappear from search.
**Linked TCs**: TC-DATA-02, TC-SEC-02" \
"Sprint-2" "feature,security"

create_issue "[US-09] System Observability, Performance Metrics & Audit Logs" \
"**Requirements**: AICMS-F-022, AICMS-NF-006, AICMS-NF-007, AICMS-SR-001
**Points**: 3 | **Assignee**: Shreeverdhan M
**Acceptance Criteria**: Admin/Auditor metrics endpoint exposes ingestion counts, error rates, p50/p90 latency, and queue depth without leaking document content; structured correlation-ID logs; data reconciliation script.
**Linked TCs**: TC-OPS-01, TC-OPS-02, TC-SEC-01, TC-SEC-06" \
"Sprint-2" "observability"

create_issue "[US-10] Frontend Web Application & WCAG 2.1 AA Accessibility" \
"**Requirements**: AICMS-NF-005, AICMS-F-013, AICMS-F-014, AICMS-F-016
**Points**: 8 | **Assignee**: Shamanth SK
**Acceptance Criteria**: React dashboard with Login, Live Ingestion Queue, Semantic Search with snippets, Document Viewer/Editor, and Admin Console; keyboard navigable, visible focus, ARIA tags, contrast compliant.
**Linked TCs**: TC-UX-01" \
"Sprint-2" "frontend"

create_issue "[US-11] API Hardening, Rate Limiting & TLS Termination" \
"**Requirements**: AICMS-NF-003, AICMS-NF-009, AICMS-NF-010, AICMS-SR-003
**Points**: 3 | **Assignee**: Srivamshi Chikkireddi
**Acceptance Criteria**: Rate limiting (429 Too Many Requests); standardized error format {code, message, correlation_id}; TLS reverse proxy with dev certificate; plain HTTP redirected.
**Linked TCs**: TC-SEC-03" \
"Sprint-2" "security,infra"

create_issue "[US-12] Performance, Reliability & Scalability Validation" \
"**Requirements**: AICMS-NF-002, AICMS-NF-004
**Points**: 5 | **Assignee**: Shreeverdhan M
**Acceptance Criteria**: Search latency p90 <= 3s under concurrent load; 10-page document ingestion <= 60s; async worker backoff and dead-letter handling measured and verified.
**Linked TCs**: TC-PERF-01, TC-PERF-02, TC-PERF-03, TC-OPS-03" \
"Sprint-3" "qa,perf"

create_issue "[US-13] System Validation, Traceability Matrix & Test Report Generation" \
"**Requirements**: AICMS-F-001..024, AICMS-NF-001..010, AICMS-SR-001..008
**Points**: 5 | **Assignee**: Sripada Krishna Sameer Aditya
**Acceptance Criteria**: Execute all 38 STP test cases with stored evidence; produce Unit Test Report, System Validation Report, Code Coverage Report (>=70%), and Branch Coverage Report (>=60%); RTM v2 finalized.
**Linked TCs**: All 38 Test Cases" \
"Sprint-3" "qa,reports"

echo "All 13 backlog items submitted."
