# Sprint-1 Demo Video Script (60 Seconds)

**Course Deliverable**: Part 2 Deliverables §2.g ("Record a minute video of the outcome of the first Sprint. It should be a working product.")  
**Project**: AI-Powered Content Management System (AICMS)  
**Target Video Duration**: 60 Seconds  
**Recorded By**: Team Member (Human Voiceover + Screen Capture)

---

## 1. Setup & Pre-Requisites Before Recording

1. Ensure the Docker containers are running:
   ```bash
   docker compose up -d
   ```
2. Seed the demo dataset:
   ```bash
   docker exec aicms_backend python -m backend.app.scripts.seed_demo
   ```
3. Open two browser tabs:
   - **Tab 1**: Frontend UI at `http://localhost:5173` (or API Docs at `http://localhost:8000/docs`)
   - **Tab 2**: Terminal showing live logs / container status

---

## 2. Minute-by-Minute Click Path & Script

| Time Window | Screen Action | Voiceover Script | Requirements Shown |
|---|---|---|---|
| **0:00 – 0:12** (12s) | Open UI / Swagger login endpoint. Authenticate with `username: regular_user`, `password: UserPass123!`. Show session token received and profile returned. | *"Welcome to the Sprint-1 demo of AICMS. We start by authenticating as regular_user. The backend securely checks bcrypt password hashes and issues a 30-minute server-side session token with automated lockout defense."* | `AICMS-F-023`, `SR-007`, `SR-008` (TC-SEC-07/08/09) |
| **0:12 – 0:28** (16s) | Click **Upload Document**, select a technical PDF or DOCX file (`fastapi_pgvector_spec.pdf`), click upload. Show status transition from `QUEUED` to `COMPLETED`. | *"Next, we upload a technical architecture PDF. The system checks extension and magic byte signatures to prevent malicious disguised files, computes SHA-256 for deduplication, and queues the document for async ingestion."* | `AICMS-F-001`, `F-004`, `SR-002`, `SR-004` (TC-UP-01..04) |
| **0:28 – 0:44** (16s) | Open the document metadata view. Show extracted text, auto-assigned category (`Engineering`, confidence: `94%`), and extracted keywords (`fastapi`, `pgvector`, `architecture`). | *"Once processed, our AI pipeline extracts the text and native metadata, computes 384-dimensional dense vectors using all-MiniLM-L6-v2, classifies the document into our approved taxonomy with confidence scores, and extracts keyphrases."* | `AICMS-F-005`, `F-008`, `F-009`, `F-010` (TC-EXT-01, TC-AI-01..03) |
| **0:44 – 0:54** (10s) | Type natural language query into Semantic Search: *"how does our database handle vector embeddings"*. Hit search. Show ranked result with similarity score (`0.88`) and highlighted snippet. | *"Now we test natural-language semantic search. We type a conceptual question without exact keyword matching. PostgreSQL with pgvector computes cosine distance, returning top-ranked results with contextual snippets."* | `AICMS-F-011`, `F-012`, `F-014` (TC-IDX-01, TC-SR-01) |
| **0:54 – 1:00** (6s) | Search for *"confidential executive memo"*. Show that zero restricted documents appear. Switch to admin account to show it exists. | *"Crucially, our ADR-002 pre-disclosure authorization filter guarantees that unauthorized documents are strictly excluded before snippets or titles are ever rendered. Thank you."* | `AICMS-SR-005` (TC-SEC-05) |

---

## 3. Video File Upload Instructions

1. Keep resolution at 1080p (30fps) with clear audio.
2. Ensure final MP4 file size is **under 50 MB** (e.g. using HandBrake or ffmpeg: `ffmpeg -i input.mp4 -vcodec libx264 -crf 24 sprint1_demo.mp4`).
3. Commit or upload to the repository under `docs/demo/sprint1_demo.mp4`.
