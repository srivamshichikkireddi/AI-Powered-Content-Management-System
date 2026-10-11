# AI-Powered Content Management System (AICMS)

## Project Overview

AICMS is a software engineering mini-project for managing a document collection with AI assistance. Users upload documents; the system automatically assigns categories, extracts keywords and topics, and indexes the content so people can find relevant documents by typing questions in natural language instead of guessing exact keywords.

## Objectives

- Accept PDF, DOCX and TXT uploads and extract their text.
- Categorize each document against an administrator-approved category taxonomy.
- Extract keywords and topics, and let users review and correct the AI-generated metadata.
- Support semantic search using natural-language queries, with filters.
- Return only the documents a user is authorized to see.
- Let administrators manage users, roles, categories and re-indexing.
- Keep audit logs and service metrics without storing secrets or sensitive content in logs.

## Key Features

- **Upload and processing:** Validation, text extraction, AI enrichment and indexing run as an asynchronous pipeline.
- **Auto-categorization:** Category suggestions with confidence scores, drawn from the approved taxonomy.
- **Keywords and topics:** Extracted automatically and editable by users.
- **Semantic search:** Embedding-based retrieval over document content, ranked and permission-filtered.
- **Access control:** Login, role-based access, and server-side authorization before any result is shown.
- **Administration:** User and role management, taxonomy management, re-index requests, audit log and metrics review.
- **Deletion:** Deleted documents are removed from search results and indexes.

## Intended Users

- General users and content editors
- Administrators
- Data owners

## Technology Stack

As proposed in the SAD (ADR-004):

- **Frontend:** React
- **Backend:** FastAPI (Python), REST APIs
- **Database / search:** PostgreSQL with pgvector
- **Background jobs:** Celery with Redis
- **AI components:** all-MiniLM-L6-v2 embeddings, scikit-learn classifier
- **Transport security:** TLS 1.2 or higher
- **Testing:** Postman, JMeter, Selenium
- **Design tools:** PlantUML, draw.io
- **Version control:** Git and GitHub

## Project Documentation

| Document | PDF | Editable source |
|---|---|---|
| Software Requirements Specification (SRS) | [SRS_AICMS.pdf](SRS_AICMS.pdf) | [docs/SRS_AICMS.docx](docs/SRS_AICMS.docx) |
| Software Architecture and Design Specification (SAD) | [SAD_AICMS.pdf](SAD_AICMS.pdf) | [docs/SAD_AICMS.docx](docs/SAD_AICMS.docx) |
| Software Test Plan (STP) | [STP_AICMS.pdf](STP_AICMS.pdf) | [docs/STP_AICMS.docx](docs/STP_AICMS.docx) |

The course templates these documents follow are in [docs/templates](docs/templates).

## Development and Collaboration

- Work on each feature or fix in its own branch.
- Open a Pull Request into `main` and have at least one teammate review it.
- The repository checks in `.github/workflows` should pass before merging.
- Avoid pushing directly to `main`; pull the latest `main` after each merge.
- Reference requirement and test-case IDs (for example `AICMS-F-012`, `TC-SR-02`) in PR descriptions.

## Project Scope

AICMS covers document upload, AI enrichment, semantic search, access control and basic administration. It is not a general-purpose enterprise document platform: it supports English-language PDF, DOCX and TXT files, and does not include real-time collaborative editing or external system integrations beyond those defined in the SRS.

## Project Status

**Current phase:** Requirements, design and test planning. Implementation and test execution follow the specifications in the SRS, SAD and STP.

## Team and Roles

| Role | Name | SRN |
|---|---|---|
| QA / Test Lead | Shreeverdhan M | PES1UG24AM265 |
| Test Engineer | Sripada Krishna Sameer Aditya | PES1UG24AM285 |
| Developer | Srivamshi Chikkireddi | PES1UG24AM287 |
| Project / Product Representative | Shamanth SK | PES1UG24AM258 |

---

*Academic Software Engineering Mini-Project — AI-Powered Content Management System (AICMS).*
