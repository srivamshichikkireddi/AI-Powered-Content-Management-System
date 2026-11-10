# Sample Test Documents for AICMS Intake & Testing

This folder contains realistic sample business documents designed for testing the **AI-Powered Content Management System (AICMS)**.

---

## 1. File Inventory & Expected AI Behavior

| File Name | Format | Domain | What the AI Does Automatically | How to Test Search After Upload |
| :--- | :---: | :---: | :--- | :--- |
| `cloud_computing_architecture.txt` | `.txt` | Engineering | Categorizes as **Engineering**, extracts cloud/microservice keywords, generates 384-d vector. | Search `"FastAPI cloud infrastructure"` |
| `employee_workplace_policy.txt` | `.txt` | Human Resources | Categorizes as **Human Resources**, extracts leave/healthcare terms. | Search `"paternity leave and healthcare insurance"` |
| `annual_budget_and_revenue_report.txt` | `.txt` | Finance | Categorizes as **Finance**, extracts fiscal growth/revenue metrics. | Search `"quarterly financial revenue surplus"` |
| `master_software_license_agreement.docx` | `.docx` | Legal | Extracts native metadata (`title` & `author`), categorizes as **Legal**, extracts GDPR/arbitration terms. | Search `"intellectual property GDPR terms"` |
| `incident_response_playbook.docx` | `.docx` | Operations | Extracts native properties, categorizes as **Operations**, extracts triage/failover keywords. | Search `"production downtime failover"` |
| `quarterly_security_audit.pdf` | `.pdf` | Engineering / Security | Extracts PDF body text, title, and author, vectorizes text for instant retrieval. | Search `"cybersecurity penetration testing"` |
| `malicious_disguised_file.pdf` | `.pdf` | **Malicious Test** | **Rejected immediately!** This is an `.exe` file disguised as `.pdf`. Magic bytes check blocks it with `HTTP 400 (INVALID_FILE_SIGNATURE)`. | Try uploading in UI $\rightarrow$ observe instant rejection |

---

## 2. Test Walkthrough: 4 Things to Try

### Test A: Normal Upload & Auto-Enrichment
1. Open the UI at [http://localhost:5173/](http://localhost:5173/).
2. Go to **"Intake & Upload"**.
3. Drag & drop `cloud_computing_architecture.txt` (or click and select it).
4. Click **"Upload & Start AI Processing"**.
5. Go to **"Document Explorer"** to see it listed with the **Engineering** category.
6. Go to **"Semantic Search"**, type `"microservices API"`, and see it ranked at the top!

### Test B: Duplicate Detection Shield (TC-UP-03)
1. Go to **"Intake & Upload"**.
2. Try uploading `cloud_computing_architecture.txt` **a second time**.
3. Observe: The upload is blocked and a **409 Conflict Duplicate Alert** is displayed with its SHA-256 hash.

### Test C: Security Spoofing Check (TC-SEC-04)
1. Go to **"Intake & Upload"**.
2. Upload `malicious_disguised_file.pdf`.
3. Observe: The system analyzes the raw binary magic bytes, detects that it is an executable disguised as a PDF, and rejects it with **HTTP 400 Bad Request**.

### Test D: Native Word Metadata Extraction (TC-EXT-02)
1. Upload `master_software_license_agreement.docx`.
2. Open **"Document Explorer"**.
3. Click on the document: notice that the Author (`Corporate Legal Counsel`) and Title (`Master Software Licensing and Services Agreement`) were extracted directly from the Word file headers without any human typing!
