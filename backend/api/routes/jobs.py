import logging

from fastapi import APIRouter, HTTPException, Request, Response

from backend.api.models import JobEntry, JobsRequest, JobsResponse
from backend.api.session import ensure_session_cookie, session_store
from backend.services.job_ingest import jobs_from_inputs

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/jobs", response_model=JobsResponse)
async def set_jobs(req: JobsRequest, request: Request, response: Response):
    """Replace session job list with the provided entries."""
    if not req.jobs:
        raise HTTPException(status_code=400, detail="At least one job is required.")

    for job in req.jobs:
        if job.source == "url" and not (job.url and job.url.strip()):
            raise HTTPException(status_code=400, detail="URL jobs must include a url.")
        if job.source == "paste" and not (job.raw_text and job.raw_text.strip()):
            raise HTTPException(status_code=400, detail="Pasted jobs must include raw_text.")

    session_id, session = ensure_session_cookie(request, response)
    session.jobs = jobs_from_inputs(req.jobs)
    logger.info("Session %s: stored %d jobs", session_id, len(session.jobs))
    return JobsResponse(jobs=session.jobs)


@router.get("/jobs", response_model=JobsResponse)
async def get_jobs(request: Request):
    from backend.api.session import get_session_id_from_request

    session_id = get_session_id_from_request(request)
    if not session_id:
        return JobsResponse(jobs=[])
    session = session_store.get(session_id)
    if not session:
        return JobsResponse(jobs=[])
    return JobsResponse(jobs=session.jobs)


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, request: Request):
    from backend.api.session import get_session_id_from_request

    session_id = get_session_id_from_request(request)
    if not session_id or not session_store.delete_job(session_id, job_id):
        raise HTTPException(status_code=404, detail="Job or session not found.")
    return {"status": "deleted", "job_id": job_id}
