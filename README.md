# AIVOA CCMS — AI-Powered Customer Complaint Management System

An AI-assisted customer complaint intake system for a pharmaceutical API/FDF
manufacturing QMS. Upload or paste a raw complaint (email, letter, notes) and
a LangGraph pipeline extracts structured fields, scores completeness, and
assigns an AI risk classification — all surfaced live in a React form with a
chat assistant for follow-up questions.

## Architecture

```
frontend (React + Redux Toolkit)  <-->  backend (FastAPI)  <-->  LangGraph pipeline  <-->  Groq LLMs
                                              |
                                        SQLAlchemy / Postgres|MySQL
```

### LangGraph pipeline (`backend/app/graph/pipeline.py`)

```
START -> extract_fields -> completeness_check -> classify_risk -> finalize -> END
```

| Node | Model | Purpose |
|---|---|---|
| `extract_fields` | `gemma2-9b-it` | Pulls the 11 form fields out of raw complaint text |
| `completeness_check` | `llama-3.3-70b-versatile` | **Bonus: Completeness Checker** — scores 0-100 and lists missing/weak fields |
| `classify_risk` | `llama-3.3-70b-versatile` | **Bonus: AI Risk Classification** — severity, priority, risk tier + rationale, reasoned like a QMS reviewer (patient safety, regulatory exposure, batch scope) |
| `finalize` | — | Normalization pass; a slot for future nodes (duplicate detection, CAPA recommendation) without touching the earlier ones |

State flows through a single `TypedDict` (`ComplaintState`) so each node only
reads/writes the keys it owns — this is what makes it straightforward to bolt
on more bonus nodes later.

### Backend (`backend/`)

- **FastAPI** app (`app/main.py`) with CORS for the Vite dev server.
- **Routes**:
  - `POST /api/complaints/extract` — run the pipeline over pasted text, persist result.
  - `POST /api/complaints/extract-file` — same, but accepts an uploaded PDF/DOCX/TXT/EML.
  - `GET/PUT/DELETE /api/complaints/{id}` — standard CRUD once a record exists.
  - `POST /api/chat` — the "Ask me anything about this complaint" assistant, grounded in that complaint's extracted fields + raw source text.
- **Models** (`app/models/complaint.py`): one `Complaint` table matching the
  4 form sections in the reference UI, plus AI-derived columns
  (`completeness_score`, `missing_fields`, `risk_classification`,
  `risk_rationale`, `duplicate_of`).
- **DB**: SQLAlchemy, defaults to SQLite for local dev; point
  `DATABASE_URL` at Postgres or MySQL for anything beyond local testing.
- File parsing (`app/services/file_extraction.py`) handles PDF/DOCX/EML/TXT —
  intentionally simple, since production-grade OCR is explicitly out of scope.

### Frontend (`frontend/`)

- **React 18 + Redux Toolkit.** Two slices:
  - `complaintSlice` — form fields + AI metadata (completeness score, risk tier, missing fields), driven by `extractFromText` / `extractFromFile` / `saveComplaint` thunks.
  - `chatSlice` — assistant conversation state.
- **Components**:
  - `ComplaintForm.jsx` — the 4-section form from the reference screenshot, plus a live completeness bar and risk pill once extraction runs.
  - `AIAssistantPanel.jsx` — drag-and-drop upload, paste-text box, extraction progress, and chat.
- Font: Google **Inter**, loaded via `index.html`.
- No backend framework lock-in on the client: a tiny `fetch`-based API client (`src/api/client.js`) — no axios needed for this scope.

## Setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set GROQ_API_KEY, and DATABASE_URL if using Postgres/MySQL instead of SQLite
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# opens on http://localhost:5173, proxies /api to http://localhost:8000
```

## Using it

1. Paste a complaint email/letter into the text box, or drag in a PDF/DOCX/TXT/EML — you can generate a few realistic sample pharma complaints yourself for demo purposes (as permitted by the assignment).
2. The pipeline runs and the form on the left populates automatically, along with a completeness score and AI risk tier.
3. Edit any field manually and click **Save Complaint** to persist overrides.
4. Ask the chat assistant follow-up questions about that specific complaint (e.g. "what's missing?", "why was this flagged high risk?").

## Notes on design decisions

- **Why a 4-node graph instead of one big LLM call?** Each node has a single
  reviewer-style responsibility (extract, judge completeness, judge risk) so
  each can use the right model for the job (fast extraction model vs. the
  stronger reasoning model), and so failures/hallucinations in one stage don't
  silently corrupt the others — you can log/inspect state after every node.
- **Why gemma2-9b-it for extraction but llama-3.3-70b-versatile for
  judgment?** Extraction is a narrow, mostly-mechanical task; the reasoning
  needed to score completeness or reason about patient-safety risk benefits
  from a stronger model.
- **Bonus features implemented**: Completeness Checker and AI Risk
  Classification, chosen over the other options (duplicate detection, CAPA
  recommendation, summary) because they're the two most directly tied to how
  a real QMS reviewer triages a complaint, and they compose cleanly as graph
  nodes for the demo video walkthrough.
