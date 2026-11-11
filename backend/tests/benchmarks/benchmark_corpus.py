"""
Reviewed benchmark corpus for quantitative evaluation of AICMS (Phase 3).
Traceability: AICMS-NF-001, AICMS-NF-009, AICMS-NF-010, TC-AI-04, TC-PERF-01..03.
"""

LABELED_CORPUS = [
    # Engineering (5 items)
    {
        "id": "ENG_01",
        "ground_truth": "Engineering",
        "text": "Microservices backend architecture using FastAPI, asynchronous coroutines, and PostgreSQL with pgvector for high throughput vector indexing.",
    },
    {
        "id": "ENG_02",
        "ground_truth": "Engineering",
        "text": "Continuous integration CI pipeline with automated unit testing, branch coverage analysis, code quality linting, and Docker container build.",
    },
    {
        "id": "ENG_03",
        "ground_truth": "Engineering",
        "text": "Database schema migration, relational foreign key constraints, connection pooling algorithms, and Redis pub/sub queue performance tuning.",
    },
    {
        "id": "ENG_04",
        "ground_truth": "Engineering",
        "text": "REST API development guidelines, JSON response validation schemas, HTTP status codes, and distributed microservices error handling.",
    },
    {
        "id": "ENG_05",
        "ground_truth": "Engineering",
        "text": "Frontend single-page application SPA built using React, Vite, Tailwind CSS components, and browser event listeners for keyboard navigation.",
    },

    # Finance (5 items)
    {
        "id": "FIN_01",
        "ground_truth": "Finance",
        "text": "Quarterly financial budget report showing operating revenue, gross profit margins, capital expenditure, and balance sheet depreciation.",
    },
    {
        "id": "FIN_02",
        "ground_truth": "Finance",
        "text": "Annual corporate tax accounting, audited fiscal balance statements, dividend distribution, and statutory treasury compliance.",
    },
    {
        "id": "FIN_03",
        "ground_truth": "Finance",
        "text": "Vendor invoice reconciliation, purchase orders, account payable disbursements, cash flow projection, and expense management.",
    },
    {
        "id": "FIN_04",
        "ground_truth": "Finance",
        "text": "Venture capital investment portfolio allocation, equity valuation multiples, financial risk hedging, and quarterly EBITDA forecasts.",
    },
    {
        "id": "FIN_05",
        "ground_truth": "Finance",
        "text": "Internal financial audit findings, expense discrepancy review, payroll general ledger accounts, and fiscal budget variances.",
    },

    # Legal (5 items)
    {
        "id": "LEG_01",
        "ground_truth": "Legal",
        "text": "Master services agreement contract terms, limitation of liability clauses, governing law jurisdiction, and confidentiality compliance.",
    },
    {
        "id": "LEG_02",
        "ground_truth": "Legal",
        "text": "Intellectual property licensing rights, proprietary trademark assignments, patent governance, and commercial dispute arbitration.",
    },
    {
        "id": "LEG_03",
        "ground_truth": "Legal",
        "text": "Regulatory compliance policy, data privacy protection standards, non-disclosure agreement obligations, and contractual breach remedies.",
    },
    {
        "id": "LEG_04",
        "ground_truth": "Legal",
        "text": "Corporate merger and acquisition contract, shareholder rights warranties, escrow terms, and antitrust regulatory filings.",
    },
    {
        "id": "LEG_05",
        "ground_truth": "Legal",
        "text": "Vendor software service level agreement SLA breach clauses, warranty disclaimers, indemnification provisions, and legal dispute settlement.",
    },

    # Human Resources (5 items)
    {
        "id": "HR_01",
        "ground_truth": "Human Resources",
        "text": "Employee onboarding manual, corporate benefits enrollment, health insurance coverage, and annual leave policy guidelines.",
    },
    {
        "id": "HR_02",
        "ground_truth": "Human Resources",
        "text": "Personnel recruitment workflow, candidate hiring interviews, job offer letters, talent acquisition, and staffing assessments.",
    },
    {
        "id": "HR_03",
        "ground_truth": "Human Resources",
        "text": "Annual employee performance appraisal review, talent retention, leadership training, compensation grading, and workplace conduct rules.",
    },
    {
        "id": "HR_04",
        "ground_truth": "Human Resources",
        "text": "Corporate payroll administration, salary deductions, employee bonuses, overtime reimbursement, and statutory pension contributions.",
    },
    {
        "id": "HR_05",
        "ground_truth": "Human Resources",
        "text": "Workplace harassment prevention policy, equal opportunity employment guidelines, employee grievance procedures, and personnel records.",
    },

    # Operations (5 items)
    {
        "id": "OPS_01",
        "ground_truth": "Operations",
        "text": "Warehouse supply chain logistics, inventory replenishment workflows, order dispatch schedules, and freight transport monitoring.",
    },
    {
        "id": "OPS_02",
        "ground_truth": "Operations",
        "text": "Datacenter facility maintenance protocols, backup generator inspection, HVAC cooling systems, and physical security procedures.",
    },
    {
        "id": "OPS_03",
        "ground_truth": "Operations",
        "text": "Manufacturing plant assembly line maintenance, machinery calibration schedules, operational downtime tracking, and quality control.",
    },
    {
        "id": "OPS_04",
        "ground_truth": "Operations",
        "text": "Fleet vehicle dispatch operations, fuel consumption monitoring, maintenance servicing logs, and delivery route optimization.",
    },
    {
        "id": "OPS_05",
        "ground_truth": "Operations",
        "text": "Enterprise procurement workflow, supplier vendor management, inventory audits, and operational asset tracking.",
    },

    # General (5 items)
    {
        "id": "GEN_01",
        "ground_truth": "General",
        "text": "Weekly cross-departmental team meeting minutes, general organizational updates, project executive summary, and action item notes.",
    },
    {
        "id": "GEN_02",
        "ground_truth": "General",
        "text": "Corporate all-hands address transcript, company vision statements, general announcements, and quarterly milestone summary.",
    },
    {
        "id": "GEN_03",
        "ground_truth": "General",
        "text": "Office relocation notice, general facility guidelines, desk booking procedures, and internal contact directory reference.",
    },
    {
        "id": "GEN_04",
        "ground_truth": "General",
        "text": "Employee recreational social club guidelines, company picnic announcements, holiday calendar overview, and informal committee notes.",
    },
    {
        "id": "GEN_05",
        "ground_truth": "General",
        "text": "General business correspondence overview, executive greeting notes, high-level project summary documentation, and reference guide.",
    },
]

SEARCH_BENCHMARK_QUERIES = [
    {"query": "how to build microservices with fastapi", "target_category": "Engineering", "expected_match": "FastAPI"},
    {"query": "continuous integration ci docker testing pipeline", "target_category": "Engineering", "expected_match": "Architecture"},
    {"query": "quarterly budget financial revenue statement", "target_category": "Finance", "expected_match": "Financial"},
    {"query": "corporate tax accounting profit margins", "target_category": "Finance", "expected_match": "Revenue"},
    {"query": "master services agreement contract compliance liability", "target_category": "Legal", "expected_match": "Contract"},
    {"query": "intellectual property patent licensing dispute", "target_category": "Legal", "expected_match": "Compliance"},
    {"query": "employee health insurance benefits onboarding policy", "target_category": "Human Resources", "expected_match": "Benefits"},
    {"query": "payroll compensation appraisal talent hiring", "target_category": "Human Resources", "expected_match": "Workplace"},
    {"query": "supply chain warehouse inventory logistics dispatch", "target_category": "Operations", "expected_match": "Architecture"},
    {"query": "facility maintenance cooling power datacenter", "target_category": "Operations", "expected_match": "Architecture"},
    {"query": "python async api web framework", "target_category": "Engineering", "expected_match": "FastAPI"},
    {"query": "annual fiscal balance depreciation capital", "target_category": "Finance", "expected_match": "Financial"},
    {"query": "non disclosure confidentiality agreement breach", "target_category": "Legal", "expected_match": "Contract"},
    {"query": "recruitment hiring candidate interview process", "target_category": "Human Resources", "expected_match": "Policy"},
    {"query": "procurement supplier vendor operational delivery", "target_category": "Operations", "expected_match": "Spec"},
    {"query": "rest api status code error envelope", "target_category": "Engineering", "expected_match": "FastAPI"},
    {"query": "ebitda profit forecast equity valuation", "target_category": "Finance", "expected_match": "Revenue"},
    {"query": "terms and conditions regulatory jurisdiction clause", "target_category": "Legal", "expected_match": "Compliance"},
    {"query": "leave policy paid time off vacation rules", "target_category": "Human Resources", "expected_match": "Leave"},
    {"query": "plant machinery calibration maintenance downtime", "target_category": "Operations", "expected_match": "Spec"},
]

TEN_PAGE_SPECIFICATION_TEXT = "\n\n".join([
    f"=== SECTION {i+1}: ENTERPRISE PLATFORM SPECIFICATION PART {i+1} ===\n"
    f"This section details architectural design patterns, distributed consensus protocols, and operational workflows. "
    f"Subsystem {i+1} implements fault-tolerant microservices, resilient event streaming with Apache Kafka, "
    f"and pgvector high-dimensional indexing for deep semantic search. Storage subsystem guarantees ACID transactions, "
    f"strict foreign key referential integrity, and AES-256 at-rest encryption. "
    f"Security auditing complies with SOC 2 Type II and ISO 27001 standards, tracking every access and administrative mutation. "
    f"Resource allocation monitors CPU utilization, garbage collection pauses, and network I/O throughput to sustain "
    f"sub-second latency at 99th percentile load across geographically distributed availability zones."
    for i in range(10)
])
