import logging

from fastapi import APIRouter, Request, Response

from backend.api.models import AnalyzeResponse, ResultsViewData
from backend.api.session import ensure_session_cookie, require_jobs, require_resume
from backend.services.analyze import run_analysis
from backend.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: Request, response: Response):
    """Run job ingest + structured analysis for the current session."""
    session_id, session = ensure_session_cookie(request, response)
    require_resume(session)
    require_jobs(session)

    logger.info("Session %s: starting analysis for %d jobs", session_id, len(session.jobs))

    # If the user has provided a per-session Mistral API key, use it for this run
    settings = get_settings()
    if getattr(session, "mistral_api_key", None):
        settings.mistral_api_key = session.mistral_api_key

    analysis, markdown, ingested = await run_analysis(session.resume_text, list(session.jobs))
    session.jobs = ingested
    session.analysis = analysis
    session.chat_messages = [
        {"role": "assistant", "content": markdown},
    ]

    return AnalyzeResponse(analysis=analysis, markdown_report=markdown)


@router.get("/analyze/results")
async def get_results_view(request: Request):
    """Return analysis formatted for the Results UI component."""
    from backend.api.session import get_session_id_from_request, session_store

    session_id = get_session_id_from_request(request)
    if not session_id:
        return {"error": "No session"}
    session = session_store.get(session_id)
    if not session or not session.analysis:
        return {"error": "No analysis available"}
    return ResultsViewData.from_analysis(session.analysis).model_dump()
