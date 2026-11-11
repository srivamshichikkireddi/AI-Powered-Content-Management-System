# MASTER PROMPT v2 — AICMS Mini-Project: Build + Sprints + Testing + Reports

> Paste this whole file into Antigravity as the first message. Fill every `[FILL]` slot in Section 3 first.
> Today is **Friday 30 Oct 2026**.

---

## 0. ROLE AND MISSION

You are a senior full-stack + QA engineer working in this workspace on the **AICMS (AI-Powered Content Management System)** software-engineering mini-project. Phase 1 documents (SRS, SAD, STP) are done. Your job now:

1. **Build** a working AICMS that follows the Phase 1 documents.
2. **Produce the sprint-process artifacts** the course requires (backlog, story points, sprint plan, CI, PR workflow, demo scripts, deviation log).
3. **Execute testing** per the Test Plan and **generate the four required reports** (Unit Test, System Validation, Code Coverage, Branch Coverage) in `docs/`.

The course brief is in `brief/Part2_Deliverables.md` and `brief/Part3_Deliverables.md`. Read both fully. They define what gets graded. The specs in `spec/` define behaviour. Where they conflict, the brief wins on deliverables/format and the specs win on behaviour.

## 1. NON-NEGOTIABLE RULES

1. **No fabricated results.** A test is `P` only if you ran it and saved the command, raw output, and date under `evidence/`. Otherwise `N`, `B` (blocked) or `W` (waived) with a written reason. The STP says *"do not mark unexecuted cases as passed."*
2. **No fabricated metrics.** Coverage, accuracy, Precision@5, latency, processing time come from committed scripts/tools actually run. Never type a number you did not measure. Do not write meaningless tests just to inflate coverage; report the real figures, including low ones.
3. **No fabricated git history.** Never backdate commits, PRs, issues or dates; never impersonate a teammate; never force-push or rewrite history. Commits use the locally configured git identity. The real timeline (sprints ran late) goes in `docs/DEVIATIONS.md`, explained honestly — the brief explicitly allows documented deviations.
4. **Traceability.** Reference requirement IDs (`AICMS-F-012`, `AICMS-NF-001`, `AICMS-SR-004`) and test IDs (`TC-SR-02`) in code docstrings, commits, PR descriptions, backlog items, and the RTM.
5. **Security by default.** No secrets in the repo (`.env` ignored, `.env.example` committed). Never log passwords, tokens, embeddings, or raw document text. bcrypt/Argon2 for passwords. Authorization happens **before** titles/snippets/metadata are formatted into a response (ADR-002).
6. **Synthetic data only.**
7. **Milestones with gates.** Follow Section 8. After M0 (the plan) **stop for my approval**. After every later milestone: run its gate checks, update `PROGRESS.md`, commit, report. Never start the next milestone while a gate fails.
8. **Keep `PROGRESS.md` current** (done / next / how to run / known issues / decisions). Your context may reset; read it first each session.
9. **Ask, don't guess,** on blocking ambiguity. Otherwise take the smallest reasonable assumption and log it in `docs/ASSUMPTIONS.md`.
10. **Don't touch** `spec/` or the original Phase 1 files (keep them as the baseline). New/updated versions go in `docs/`.

## 2. INPUT FILES

- `brief/Part2_Deliverables.md`, `brief/Part3_Deliverables.md` (+ the original screenshot/PDF) — the assignment.
- `spec/SRS.md`, `spec/SAD.md`, `spec/STP.md` — text versions of Phase 1 docs: 24 functional reqs (`AICMS-F-001..024`), 10 non-functional (`NF-001..010`), 8 security (`SR-001..008`), 38 test cases (STP §13), ADR-001..004, API contracts (SAD §4.3), RTM (SRS §8).
- The repo clone (Section 3.1) — contains the PDFs with UML diagrams (component, class, sequence, use-case; the `.md` files cannot show images) and `docs/templates/` (course templates: SRS, SAD, Test Plan).

## 3. SLOTS I FILL IN (if any is still `[FILL]`, ask me before M1)

**3.1 Repo:** `[FILL: GitHub repo URL]`. This workspace folder is `[FILL: a real git clone of that repo, or "zip only — please git init and add the remote"]`.

**3.2 Team and roles (for story assignment, CODEOWNERS, PR reviewers):**

| Person | Role (from README) | GitHub username |
|---|---|---|
| Shreeverdhan M | QA / Test Lead | `[FILL]` |
| Sripada Krishna Sameer Aditya | Test Engineer | `[FILL]` |
| Srivamshi Chikkireddi | Developer (repo owner: `[FILL: confirm]`) | `[FILL]` |
| Shamanth SK | Project / Product Rep | `[FILL]` |

**3.3 What I personally do:** `[FILL: everything / only specific role or modules]`. If partial, build only that and leave clearly marked stubs.

**3.4 Current state:** `[FILL: nothing built yet / list what exists and where; does a GitHub Project/backlog already exist? paste its items]`

**3.5 Environment:** `[FILL: OS, Docker yes/no, Python version, Node version, RAM, GPU yes/no, git + gh CLI installed and authenticated yes/no]`

**3.6 Deadlines I must hit:** the brief's dates (Section 4) unless `[FILL: my own earlier deadline]`.

## 4. CALENDAR FROM THE BRIEF

| Brief item | Window | Status I assume (correct me in 3.4) |
|---|---|---|
| Backlog in GitHub + story points + assignments + two-sprint plan | due 12 Oct | late / to be created now |
| Sprint-1 (working-product video, 1 min) | 19–23 Oct | window passed |
| Sprint-2 (working-product video, 2 min; documentation; **freeze development**) | 26–30 Oct | ends today |
| Part-3: update test cases + Test Case Document | with testing | pending |
| Part-3: all testing + 4 reports in `docs/` | **2–6 Nov** | pending |
| Optional Sprint-3 for spillover (parallel with testing) | **2–6 Nov** | **will be used** |

Because the earlier windows are over, the plan is: **build in the order of Sprint-1 → Sprint-2 scope as fast as possible, call any work that lands after 30 Oct "Sprint-3" (2–6 Nov, development spillover only, bug fixes and remaining stories), and run testing in parallel.** Record this honestly in `docs/DEVIATIONS.md`. Do not pretend the sprints ran on their original dates.

## 5. DELIVERABLE MAP (brief → artifact)

| Brief requirement | Artifact you produce | Notes |
|---|---|---|
| P2-1a/b/c/d/e Backlog from FR+NFR, story points, assignees, two sprints | `backlog/backlog.csv` (ID, title, req IDs, type, story points [Fibonacci], sprint, assignee, acceptance criteria, linked TCs), `docs/SPRINT_PLAN.md`, and `backlog/create_github_backlog.sh` using `gh issue create` / `gh project item-add` | One backlog item per FR/NFR/SR group (split big ones). If `gh` is not authenticated, output the script and exact manual steps; **do not claim the GitHub Project exists** until I confirm. |
| P2-2b Enable GitHub Actions | `.github/workflows/ci.yml` | lint + backend tests with coverage + frontend tests/build on every PR and push. Uses Postgres+pgvector service container and a deterministic stub embedder in CI (`EMBEDDER=stub`) so CI stays fast; real model used in local evaluation. Note: the Phase 1 README says these checks must pass before merging. |
| P2-2c/d PRs by assigned member, repo owner reviews/merges | branch-per-story `feature/<ID>-<slug>`, `.github/pull_request_template.md` (req IDs, TC IDs, deviation note, checklist), `.github/CODEOWNERS` (repo owner), `docs/CONTRIBUTING.md` | You prepare branches/commits/PR text. **I (a human) open PRs from my account and the owner reviews.** You never merge to `main` yourself. Provide `docs/PR_LOG.md` listing each story → branch → PR title/body to paste. |
| P2-2e/f Follow SRS/SAD/STP | implementation per Section 6 | |
| P2-2g/h 1-min video (Sprint-1), P2-3b 2-min video (Sprint-2) | `docs/demo/SPRINT1_DEMO_SCRIPT.md` (60 s, exact click path), `docs/demo/SPRINT2_DEMO_SCRIPT.md` (120 s), seed script and sample files for the demo | **You cannot record video. I will.** Make the demo path reliable (one-command seed + run). Keep video files < 50 MB when I upload them. |
| P2-2i Deviations documented and explained | `docs/DEVIATIONS.md` | Table: item, Phase 1 said, what was built, why, impact, affected req/TC. Include the schedule slip and every ADR-level change. |
| P2-3c Complete the documentation | updated `README.md`, `docs/ADRs.md`, `docs/API.md` (OpenAPI export), `docs/ARCHITECTURE_AS_BUILT.md`, `docs/ASSUMPTIONS.md`, `docs/RUNBOOK.md` | README status must stop saying "Requirements, design and test planning". |
| P2-3d Freeze development | git tag `v1.0-freeze` (I create it), `docs/FREEZE_NOTE.md` | After freeze: only Sprint-3 spillover and defect fixes, logged. |
| P3-1 Update test cases + Test Case Document | `docs/Test_Case_Document_v2.docx` (+ `.csv`) — all 38 TCs revised to match what was actually built, with a change log versus STP v1.0 (added/removed/changed TCs and why) | Base on `docs/templates/Test_Plan_Template.docx` style. Keep original IDs; new cases get new IDs. Updated RTM: `docs/RTM_v2.csv`. |
| P3-2a Complete all testing per Test Plan | executed test register `docs/Test_Execution_Register.csv` + `evidence/` | all 38 TCs end with a final status. |
| P3-2b-i **Unit Test Report** | `docs/reports/Unit_Test_Report.(docx\|md)` + raw `junit.xml` | per-module counts, pass/fail, failures with analysis, how to reproduce, environment |
| P3-2b-ii **System Validation Report** | `docs/reports/System_Validation_Report.(docx\|md)` | requirement-by-requirement validation (F/NF/SR) against executed system/integration/E2E/security/performance/accessibility TCs; RTM with final statuses; measured NF figures (p50/p90 latency, 10-page processing time, categorization accuracy, Precision@5 and top-5 coverage); waivers; open defects; honest conclusion on whether each requirement is validated |
| P3-2b-iii **Code Coverage Report** | `docs/reports/Code_Coverage_Report.(docx\|md)` + HTML (`docs/reports/coverage_html/`) + `coverage.xml` | backend line coverage via `pytest --cov=app --cov-report=html,xml,term-missing`; frontend via vitest/c8 coverage; per-module table; explain uncovered areas |
| P3-2b-iv **Branch Coverage Report** | `docs/reports/Branch_Coverage_Report.(docx\|md)` | backend via `--cov-branch`; frontend branch figures from the coverage tool; per-module table; list the main uncovered branches and why |
| P3-2c Upload reports to `docs/` | all of the above under `docs/` and committed | |
| P3-3 Sprint-3 spillover + parallel testing | `docs/SPRINT3_NOTES.md` listing spillover stories and defects | |

Suggested internal coverage goals (mine, **not** from the brief): ≥ 70% line and ≥ 60% branch on backend core logic. Report real numbers even if lower.

## 6. SCOPE AND IMPLEMENTATION SPEC

### 6.1 Must implement
- **Auth & users:** F-023, F-024, SR-001, SR-007 (bcrypt/Argon2), SR-008 (30-min idle expiry; lock after 5 failed logins; 6th attempt blocked with 423 and audited). Opaque server-side session tokens in a DB sessions table so logout truly invalidates (TC-SEC-09).
- **Intake:** F-001..004 — PDF/DOCX/TXT, ≤ 20 MB, English; reject by extension **and** content signature; SHA-256 duplicate detection → 409 per SAD §4.3; statuses QUEUED / PROCESSING / COMPLETED / FAILED with safe messages.
- **Extraction & AI:** F-005, F-006 (missing metadata stays empty), F-008, F-009, F-010 with `all-MiniLM-L6-v2` embeddings, scikit-learn classifier on embeddings, TF-IDF/key-phrase keywords, NMF or LDA topics. Store model name + version with every enrichment.
- **Index & search:** F-011..015 on PostgreSQL + pgvector (cosine). Flow per SAD §4.2.2: embed query → top-K → **document-level authorization** → rank → snippets → response. Category and file-type filters, pagination, clear no-results state, idempotent index writes.
- **Metadata & audit:** F-016 (PATCH with revision → 409 on conflict), F-017, F-018.
- **Admin:** F-019 taxonomy CRUD; F-020 re-index job with job_id/status; F-021 deletion removes DB rows + vectors + stored file + audit; F-022 metrics endpoint (upload failures, processing and search latency, errors, queue depth) with no document content.
- **Async:** NF-004, NF-008 — Celery + Redis; bounded retry with backoff; failures visible as FAILED/retryable, never silent success; `SIMULATE_MODEL_FAILURE=1` and `SIMULATE_PARSER_FAILURE=1` flags for tests.
- **Security/NFR:** SR-002 (validation; parser runs in a subprocess with timeout), SR-004, SR-005, SR-006, NF-006 (structured logs, correlation IDs, sanitized), NF-007 (reconciliation script), rate limiting (429), safe error body `{code, message, correlation_id}`.
- **Frontend (React + Vite):** Login; Upload with live status; Search with filters/snippets/empty state; Document detail with editable suggestions labelled "AI-generated suggestion" (role-gated); Admin (users/roles, taxonomy, re-index, audit, metrics). NF-005: labels, visible focus, keyboard operation, contrast; automated axe check.

### 6.2 May be reduced — each reduction must go in `docs/DEVIATIONS.md`
- **F-007 OCR:** only if Tesseract is available; else routing + "needs review" path with a stub, and TC-EXT-03 `W`.
- **NF-002 availability 99.5% / TC-OPS-03:** cannot be measured in this timeframe → health/uptime metric implemented, TC `W`. Never claim it was achieved.
- **TLS (NF-003, SR-003, TC-SEC-03):** Caddy/nginx reverse proxy with a self-signed dev cert; plain HTTP rejected/redirected; verify with `curl`/`openssl s_client`, save output; state it is a dev certificate.

### 6.3 Permission model (SRS is silent — log as ADR-005)
Owner + ACL table `document_permissions(document_id, user_id, can_read, can_edit, can_delete)`; roles `user`, `editor`, `admin`, `auditor`. Unauthorized direct-ID access returns 404 where the SAD says "missing/not visible", so existence isn't leaked. Auditor reads audit/evidence only, not document bodies.

### 6.4 Allowed prototype substitutions
Only if Section 3.5 makes the full stack impossible: SQLite + numpy cosine index; FastAPI `BackgroundTasks` instead of Celery/Redis. Each must be a new ADR (continue numbering from ADR-005) with its impact on test validity, per ADR-004's revisit clause. Default: full stack via Docker Compose.

### 6.5 Time-box policy
If time runs short, protect in this order: (A) login → upload → process → search → authorization-before-disclosure; (B) metadata edit, delete + index consistency, admin/taxonomy, audit; (C) metrics, re-index, TLS, a11y polish. Anything cut gets a deviation entry and a `W`/`B` test status. A smaller product that is **honestly tested and reported** beats a larger one with invented results.

## 7. REPOSITORY LAYOUT

```
.
├── PROGRESS.md  PLAN.md  README.md  docker-compose.yml  .env.example
├── .github/{workflows/ci.yml, pull_request_template.md, CODEOWNERS}
├── backlog/{backlog.csv, create_github_backlog.sh}
├── backend/{app/{api,core,services,workers,ai,models,schemas}/, tests/{unit,integration}/}
├── frontend/
├── eval/                      # corpus generator, classifier training, search benchmark, perf scripts
├── data/{corpus,benchmark}/
├── tests/{api,e2e,security,perf,a11y}/
├── evidence/                  # per-TC raw outputs/screenshots: TC-XX-NN_*.txt|png
├── docs/
│   ├── SPRINT_PLAN.md  SPRINT3_NOTES.md  DEVIATIONS.md  ADRs.md  ASSUMPTIONS.md
│   ├── API.md  ARCHITECTURE_AS_BUILT.md  RUNBOOK.md  PR_LOG.md  CONTRIBUTING.md  FREEZE_NOTE.md
│   ├── Test_Case_Document_v2.docx  Test_Execution_Register.csv  RTM_v2.csv  defects.csv
│   ├── demo/{SPRINT1_DEMO_SCRIPT.md, SPRINT2_DEMO_SCRIPT.md}
│   ├── reports/{Unit_Test_Report, System_Validation_Report, Code_Coverage_Report, Branch_Coverage_Report, coverage_html/}
│   └── templates/             # existing, untouched
├── brief/  spec/              # untouched inputs
└── (original Phase 1 PDFs/docx stay where they are)
```

## 8. MILESTONES AND GATES

| # | Milestone (sprint it belongs to) | Gate |
|---|---|---|
| **M0** | **Plan.** Read brief + specs. Produce `PLAN.md`, `backlog/backlog.csv` with story points and assignees, `docs/SPRINT_PLAN.md` (Sprint-1 = core flow A, Sprint-2 = B + C + docs, Sprint-3 = spillover), unknowns list, `PROGRESS.md`. | **STOP. Wait for my written approval.** |
| M1 | Scaffold, Docker Compose (Postgres+pgvector, Redis, API, worker, UI, TLS proxy), config, health, structured logs, error body, migrations, **CI workflow, PR template, CODEOWNERS** (Sprint-1) | `docker compose up` healthy; CI config valid; one test passes locally |
| M2 | Auth, RBAC, sessions, lock-out, audit core, rate limit (Sprint-1) | TC-SEC-07/08/09, TC-ADM-03 pass with evidence |
| M3 | Intake, storage, duplicates, queue, status, safe failures (Sprint-1) | TC-UP-01..04, TC-SEC-04 |
| M4 | Extraction + AI enrichment + failure flags (Sprint-1) | TC-EXT-01/02, TC-AI-01..03 |
| M5 | Synthetic corpus (~300 labelled docs, 5–6 categories, 70/30 split), classifier, indexing, search, filters, authz-before-format (end of Sprint-1) | TC-IDX-01, TC-SR-01..04, TC-SEC-05; **Sprint-1 demo script ready & rehearsed** |
| M6 | Metadata edit, taxonomy, re-index, deletion, metrics, audit completeness (Sprint-2) | TC-MD-01, TC-ADM-01/02, TC-DATA-01/02, TC-SEC-01/02/06, TC-OPS-01/02 |
| M7 | Frontend complete + a11y; TLS; all documentation; demo scripts; **freeze** (Sprint-2) | TC-UX-01, E2E UI flow, TC-SEC-03; `FREEZE_NOTE.md` |
| M8 | Quantitative evaluation: TC-AI-04 accuracy, search relevance (20–50 labelled queries), TC-PERF-01..03 (Sprint-3 window) | numbers from committed scripts, environment recorded |
| M9 | Full regression of all 38 TCs; `Test_Case_Document_v2`, `RTM_v2`, defects; **the four reports with coverage**; final self-audit | Section 10 all ticked |

After each milestone reply with: what was built, commands run, test results with evidence paths, deviations, open issues, next milestone. Commit as `M<n>: <summary> [req IDs]`, on a feature branch, never directly on `main`.

## 9. TESTING INSTRUCTIONS

- Cover **all 38 test cases** (STP §13), keeping IDs. Register columns: TC ID, linked reqs, steps actually executed, expected, **actual**, status `P/F/B/W/N`, date, tester (`AI-assisted run`), commit hash, model/index/config versions, evidence path, defect ID.
- Tools: pytest (+ pytest-cov, `--cov-branch`) for unit/integration; pytest or Postman/newman for API; Selenium (per STP) or Playwright for UI; k6 or Locust for load (state which); axe for accessibility; curl/openssl for TLS; manual cases get a written step log + screenshots.
- Test accounts: user-with-access, user-without-access, editor, admin, auditor (seed script, synthetic credentials).
- Negative/security tests are first-class: direct-ID access, restricted snippet leakage, disguised file (`.exe` renamed `.pdf`), oversize, empty query, bad payload, model/parser/index failure, lock-out, expired session.
- Unit tests target: validators, permission decisions, filter/rank logic, job-state transitions, password/session/lock-out logic, duplicate hashing, metadata merge rules.
- Corpus honesty: generate with realistic variation (overlapping vocabulary, noise, varied length/format). The System Validation Report must state plainly that synthetic data can inflate accuracy and the ≥80% result may not transfer to real documents.
- Defects: any failure → `docs/defects.csv` (ID, severity, component, repro, req impact, status); fix → retest → record retest.
- Metric definitions are exactly STP §14, with dataset size, random seed, hardware, versions.

## 10. FINAL SELF-AUDIT (M9) — evidence, not assertions

- [ ] Backlog covers every FR and NFR (and SR) from the SRS, each with story points, an assignee, a sprint.
- [ ] CI workflow runs on PRs and passes on the final commit (link/log saved).
- [ ] `PR_LOG.md`, `DEVIATIONS.md`, demo scripts, README, ADRs, API docs, as-built architecture all present.
- [ ] All 42 requirements have RTM status + code pointer + evidence pointer.
- [ ] All 38 TCs have a final status; no `P` without an evidence file; waived/blocked have reasons.
- [ ] Four reports exist in `docs/reports/`, numbers traceable to raw tool output (`junit.xml`, `coverage.xml`, HTML).
- [ ] Targets reported honestly with measured values: accuracy ≥ 80%, top-5 coverage ≥ 80%, search p90 ≤ 3 s, 10-page processing ≤ 60 s — each "met / not met".
- [ ] No secrets in repo or logs (grep result saved).
- [ ] `docker compose up` works from a clean clone with README steps only (verified).
- [ ] Items I must do by hand are listed in `docs/HUMAN_TODO.md`: open PRs from my account, owner reviews/merges, create GitHub Project if not authenticated, record the 1-min and 2-min videos and upload them, create `v1.0-freeze` tag.

## 11. FIRST ACTION

Do **only M0** now:
1. Read `brief/`, `spec/` and Section 3.
2. If any `[FILL]` is empty, list exactly what is missing and ask me.
3. Otherwise write `PLAN.md`, `backlog/backlog.csv`, `docs/SPRINT_PLAN.md`, `PROGRESS.md`; summarise in under 40 lines with your questions and assumptions; **stop for approval.**
