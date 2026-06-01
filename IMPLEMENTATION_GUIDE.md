# PrepForge Phase A — Implementation Guide

## What Phase A Delivers

- **Session-scoped state** via `prepforge_session` HTTP-only cookie (in-memory store; resets on server restart)
- **Resume upload** (`POST /api/upload`) — PDF/DOCX only; text stored server-side (not returned in full)
- **Job postings** — URL and pasted descriptions supported equally (`POST /api/jobs`)
- **Indeed URLs** — fetched via `curl_cffi` (not Playwright; Indeed returns 403 to headless browsers)
- **Deterministic analysis** (`POST /api/analyze`) — ingests all jobs, returns structured JSON + markdown report
- **Chat follow-ups** (`POST /api/query`) — uses session context, prior analysis, and conversation history
- **Frontend** — dual job input, real Results panel (no mock metrics), `credentials: 'include'` for cookies

---

## How to Run

### 1. Backend

```bash
cd "/Users/asroot/AI Bootcamp/Agentic AI/Job_Agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Edit .env and set MISTRAL_API_KEY

python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000

### 3. User flow

1. Upload resume (PDF or DOCX)
2. Add jobs via **URL** or **Paste description** tabs
3. Click **Begin Analysis**
4. Review the Analysis Report and per-job match cards
5. Chat for follow-up questions (session retains context)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload resume; sets session cookie |
| POST | `/api/jobs` | Replace job list `{ "jobs": [...] }` |
| GET | `/api/jobs` | List jobs for session |
| DELETE | `/api/jobs/{job_id}` | Remove one job |
| POST | `/api/analyze` | Ingest jobs + run analysis |
| GET | `/api/analyze/results` | Results view JSON for current session |
| POST | `/api/query` | Chat `{ "query": "..." }` |

All `/api/*` routes (except upload) expect the session cookie. The React app sends `credentials: 'include'`.

### Job entry shape

```json
{
  "id": "optional-uuid",
  "source": "url",
  "url": "https://www.indeed.com/viewjob?jk=...",
  "title": null,
  "raw_text": null
}
```

```json
{
  "source": "paste",
  "title": "Senior Engineer",
  "raw_text": "Full job description text..."
}
```

### Upload response

```json
{
  "status": "success",
  "message": "...",
  "file_name": "resume.pdf",
  "file_size": 152340,
  "character_count": 4200,
  "session_id": "uuid"
}
```

### Analyze response

```json
{
  "analysis": {
    "overall_summary": "...",
    "best_fit_job_id": "...",
    "jobs": [{ "job_id", "job_title", "match_score", "strengths", "gaps", "recommendation" }],
    "metrics": [{ "value": "85%", "label": "Best Match" }],
    "development_areas": ["..."]
  },
  "markdown_report": "## Analysis Summary\n..."
}
```

---

## Architecture

```
backend/
├── main.py
├── config.py
├── agents/
│   ├── builder.py          # LangGraph ReAct agent
│   ├── prompts/templates.py
│   └── tools/
│       ├── resume_extractor.py
│       └── job_reader.py
├── api/
│   ├── models.py
│   ├── session.py
│   └── routes/
│       ├── upload.py
│       ├── jobs.py
│       ├── analyze.py
│       └── query.py
└── services/
    ├── job_ingest.py
    └── analyze.py
```

**Analysis pipeline:** `ingest_all_jobs` (parallel) → single LLM JSON call → `AnalysisResult` stored on session.

**Chat pipeline:** session context + chat history → LangGraph agent.

---

## Environment variables

See `.env.example`:

- `MISTRAL_API_KEY` (required)
- `CORS_ORIGINS` (default includes localhost:3000)
- `PLAYWRIGHT_HEADLESS` (default `true`; set `false` to debug scraping locally)

---

## Testing

```bash
pip install pytest
pytest tests/test_phase_a.py -q
```

Manual curl (after upload, save cookie from `-c`):

```bash
curl -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/upload -F "file=@resume.pdf"
curl -b cookies.txt -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"jobs":[{"source":"paste","raw_text":"Python developer needed","title":"Dev"}]}'
curl -b cookies.txt -X POST http://localhost:8000/api/analyze
```

---

## Known limitations (Phase A)

- In-memory sessions only (not shared across workers or restarts)
- Indeed-optimized URL scraping; other boards may need paste
- No auth, rate limits, or export PDF
- Analysis quality depends on Mistral API availability

---

## Troubleshooting

- **CORS / cookies:** Frontend must use `credentials: 'include'` and backend `allow_credentials=True`
- **Upload 400:** Use PDF or DOCX only
- **Scrape fails / Indeed 403:** Run `pip install curl_cffi beautifulsoup4 lxml`, restart the backend, and retry. If it still fails, paste the job description instead.
- **Analysis 400:** Upload resume and add at least one job first
- **MISTRAL_API_KEY:** Required in `.env`
