# Architectural and Project Assumptions (AICMS)

This document tracks explicit assumptions made during the implementation of the AI-Powered Content Management System (AICMS), ensuring complete transparency with Phase 1 specifications and course deliverables.

---

## 1. Access Control and Permission Model (ADR-005)

- **Context**: The Phase 1 SRS specifies that only authorized users may retrieve document metadata or content, but does not specify the exact schema for document permissions.
- **Decision / Assumption**:
  - We establish an explicit access-control table `document_permissions(document_id, user_id, can_read, can_edit, can_delete)` in addition to the `owner_id` on the `documents` table.
  - System roles are:
    1. `user`: Can upload documents, search, and view/edit documents they own or have been granted access to.
    2. `editor`: Can review, edit AI-generated metadata, and manage categories across documents they have access to.
    3. `admin`: Has full CRUD permissions over taxonomy, users, re-indexing jobs, and document management.
    4. `auditor`: Read-only access to audit logs, execution registers, and system metrics. Auditors cannot view document content or embeddings unless explicitly granted.
  - Direct object access to a document that the user is unauthorized to see returns **404 Not Found** (instead of 403) to prevent leaking document existence (per SAD §4.2.2).

---

## 2. OCR and Scanned PDF Handling (F-007 / TC-EXT-03)

- **Context**: AICMS-F-007 states that OCR should be applied if a PDF contains only scanned raster images.
- **Decision / Assumption**:
  - Pure text extraction is performed via PyPDF and python-docx.
  - If a document contains zero extracted characters (scanned image PDF), the pipeline flags the document as `PROCESSING_FLAGGED_NEEDS_REVIEW` and routes it to an OCR processing queue.
  - If the host/container environment does not have Tesseract-OCR binary installed, the system gracefully logs an audit warning and marks TC-EXT-03 as Waived (`W`) per Master Prompt Section 6.2, rather than failing silently or fabricating OCR output.

---

## 3. High Availability and Long-Term Uptime (NF-002 / TC-OPS-03)

- **Context**: AICMS-NF-002 specifies 99.5% service availability.
- **Decision / Assumption**:
  - A multi-month availability figure cannot be genuinely measured within a short academic sprint cycle.
  - The system implements `/health`, `/metrics`, and Docker restart policies with synthetic uptime tracking.
  - TC-OPS-03 is documented as Waived (`W`) in the Test Execution Register and System Validation Report with explicit, honest justification.

---

## 4. Embedding Model and Deterministic CI (F-008 / NF-008)

- **Context**: AICMS-F-008 mandates `all-MiniLM-L6-v2` (384 dimensions) for vector representations.
- **Decision / Assumption**:
  - Local evaluation, search benchmarking, and production containers use the real HuggingFace `sentence-transformers/all-MiniLM-L6-v2` model.
  - For rapid CI execution (`.github/workflows/ci.yml`), an environment variable `EMBEDDER=stub` produces deterministic 384-dimensional normalized vectors from a seeded hash to keep CI fast and reliable without downloading large neural weights.

---

## 5. Synthetic Evaluation Data

- **Context**: Evaluation requires a dataset of labelled documents and queries.
- **Decision / Assumption**:
  - In compliance with Non-Negotiable Rule 6 (Synthetic data only), a 300-document synthetic corpus across 5 domain categories (e.g., Engineering, Finance, Legal, HR, Operations) is generated with realistic linguistic overlap and noise.
  - The System Validation Report explicitly discloses that accuracy figures derived from synthetic corpora may exceed real-world messy document collections.
