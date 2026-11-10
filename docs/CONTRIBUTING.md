# Contributing Guidelines — AICMS Project

## 1. Branch Strategy and Workflow

All team members must follow a structured Git branching workflow:

- `main`: Production-ready, stable codebase. Direct commits to `main` are restricted.
- `feature/<ID>-<slug>`: Feature branches created for individual user stories from `backlog/backlog.csv` (e.g., `feature/US-01-auth-lockout`, `feature/US-02-intake-storage`).
- `milestone/M<n>-<slug>`: Milestone aggregation branches.

---

## 2. Commit Message Guidelines

Every commit must be traceable to the requirement IDs and test case IDs it addresses:

```text
M<n>: <Imperative summary> [AICMS-F-NNN, TC-XX-NN]

- Bulleted list of concrete changes
- Verification commands executed
```

Example:
```text
M1: Scaffolding, Docker Compose, and CI pipeline [AICMS-NF-006, TC-OPS-01]
```

---

## 3. Pull Request Requirements

1. Use `.github/pull_request_template.md` for all PRs.
2. Cite all requirement and test case IDs.
3. Include raw execution logs in `evidence/`.
4. Ensure CI pipeline checks (lint, tests, coverage, build) pass with 100% green status.
5. Must be reviewed and approved by the repo owner (`@Srivamshi-Chikkireddi`) before merge.

---

## 4. Local Testing & Verification

```bash
# Run backend tests with coverage
pytest backend/tests/ --cov=backend/app --cov-branch --cov-report=term-missing

# Run frontend dev server
cd frontend && npm run dev
```
