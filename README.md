# PrepForge

**An Agentic AI prototype for resume–job fit analysis.** PrepForge compares your CV against multiple job postings and recommends the best match based on your experience.

Built as a **ReAct-style agent** with tool use: the LLM decides when to read your resume, fetch job details from URLs, and synthesize a structured recommendation.

---

## What It Does

- **Resume extraction** — Reads your CV (PDF, DOCX, DOC) and extracts plain text
- **Job posting retrieval** — Fetches and summarizes Indeed job pages from URLs
- **Comparative analysis** — Compares your profile to job requirements and recommends the most suitable role
- **Structured output** — Returns strengths, gaps, and recommendations with evidence from your CV and the job postings

---

## Architecture

PrepForge is a **ReAct (Reason + Act) agent** built with LangGraph:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PrepForge Agent                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐                      ┌──────────────┐            │
│   │   START      │ ──────────────────►  │   assistant  │            │
│   └──────────────┘                      │   (Mistral)  │            │
│          │                              └──────┬───────┘            │
│          ▼                                     │                    │
│   ┌──────────────┐     messages                │                    │
│   │   assistant  │ ◄───────────────────────────┤                    │
│   │   (Mistral)  │     ◄───────────────────────┘                    │
│   └──────┬───────┘            │                                     │
│          │                    │ tools_condition                     │
│          │ tool_calls         ▼                                     │
│          │              ┌──────────────┐                            │
│          └─────────────►│    tools     │                            │
│                         │  ToolNode    │                            │
│                         └──────┬───────┘                            │
│                                │                                    │
│                    ┌───────────┴───────────┐                        │
│                    ▼                       ▼                        │
│            extract_resume_text      get_job_summary                 │
│            (PDF/DOCX/DOC)           (Playwright + LLM)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

- **assistant** — Mistral-based LLM with tool binding; reasons and chooses tools
- **tools** — Executes `extract_resume_text` and `get_job_summary`
- **MessagesState** — Holds the full conversation and tool results
- **Conditional edges** — Agent loops until it has enough information to answer

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Agent orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) — StateGraph, ToolNode, ReAct loop |
| **LLM** | [Mistral AI](https://mistral.ai/) (`mistral-medium-2508`) via LangChain |
| **Web scraping** | [Playwright](https://playwright.dev/python/) — Fetches Indeed job pages |
| **Resume parsing** | [pdfplumber](https://github.com/jsvine/pdfplumber), [python-docx](https://python-docx.readthedocs.io/) |
| **Tool framework** | [LangChain](https://github.com/langchain-ai/langchain) — `@tool` decorator, messages |
| **Observability** | [LangSmith](https://smith.langchain.com/) — Tracing, run visualization, debugging |
| **CLI** | `argparse` |
| **Config** | `python-dotenv` (API keys) |

---

## Project Structure

```
PrepForge/
├── main.py                 # CLI entry point, invokes agent
├── backend/
│   ├── Builder.py          # LangGraph graph definition, ReAct agent
│   ├── PromptRepository.py # System prompts (career assistant, job reader)
│   ├── ResumeExtractor.py  # Tool: CV text extraction (PDF/DOCX/DOC)
│   └── JobReader.py        # Tool: Indeed job scraping + LLM summarization
├── .env                    # MISTRAL_API_KEY, LANGSMITH_* (optional tracing)
└── README.md
```

---

## Setup

1. **Clone and enter the project**
   ```bash
   git clone https://github.com/<your-username>/PrepForge.git
   cd PrepForge
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install langchain langchain-core langchain-mistralai langgraph langsmith python-dotenv playwright pdfplumber python-docx
   playwright install chromium
   ```

4. **Configure environment variables**
   
   Create a `.env` file with:
   ```bash
   MISTRAL_API_KEY=your_mistral_key_here
   
   # Optional: LangSmith tracing (for observability and debugging)
   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_API_KEY=your_langsmith_key_here
   LANGSMITH_PROJECT=PrepForge
   ```
   
   Get a LangSmith API key at [smith.langchain.com](https://smith.langchain.com/).

---

## Usage

```bash
python main.py --resume path/to/your_resume.pdf --jobs "https://www.indeed.com/viewjob?jk=..." "https://www.indeed.com/viewjob?jk=..."
```

**Example:**
```bash
python main.py --resume Aman_Saxena_02_12_2026.pdf --jobs \
  "https://www.indeed.com/viewjob?jk=40781386989fa311" \
  "https://www.indeed.com/viewjob?jk=ad7e3ed1af2823b4" \
  "https://www.indeed.com/viewjob?jk=348becd57110a790"
```

The agent will:
1. Parse your resume
2. Visit each job URL, extract content, and summarize it (a Chromium window may appear briefly)
3. Compare your profile to each role and print a recommendation

---

## Design Choices

- **Tool-based ReAct** — The LLM selects tools and processes their outputs instead of relying on fixed pipelines.
- **External tools** — Resume extraction and job scraping are separate tools; the agent decides when and how often to call them.
- **Structured prompts** — System prompts enforce factual, evidence-based answers and consistent formatting.
- **Async execution** — `ainvoke` and async tools support scalable, non-blocking workflows.
- **LangSmith tracing** — Agent runs are traced end-to-end; the assistant node is instrumented with `@traceable` for run visualization and debugging in LangSmith.

---

## Observability (LangSmith)

PrepForge uses [LangSmith](https://smith.langchain.com/) for tracing. When `LANGSMITH_TRACING=true` and credentials are set in `.env`:

- **LLM calls** — Token usage, latency, and input/output
- **Tool invocations** — `extract_resume_text` and `get_job_summary` runs
- **Agent graph** — Step-by-step flow (assistant → tools → assistant)
- **Custom spans** — The assistant node is wrapped with `@traceable(name="Prep Forge")` for clear run grouping

View traces in your LangSmith project dashboard to debug, profile, and iterate on prompts.

---

## Roadmap

- [x] Backend API (FastAPI)
- [x] Web frontend
- [ ] Support for additional job boards
- [ ] Resume enhancement suggestions

---
