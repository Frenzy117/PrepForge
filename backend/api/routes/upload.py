import logging

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile

from backend.agents.tools.resume_extractor import extract_resume_text_bytes
from backend.api.models import ResumeUploadResponse
from backend.api.session import ensure_session_cookie

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
):
    """Upload a resume (PDF or DOCX) and store it on the session."""
    file_name = file.filename or "resume"
    file_extension = None
    lower_name = file_name.lower()
    for ext in ALLOWED_EXTENSIONS:
        if lower_name.endswith(ext):
            file_extension = ext
            break

    if not file_extension:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB",
        )
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    resume_text = extract_resume_text_bytes(file_content, file_name)
    if not resume_text or resume_text.startswith(("Unsupported", "Error", "DOC format")):
        raise HTTPException(
            status_code=400,
            detail=resume_text or "Failed to extract text from resume",
        )

    session_id, session = ensure_session_cookie(request, response)
    session.resume_text = resume_text
    session.resume_file_name = file_name
    session.analysis = None

    logger.info("Session %s: resume uploaded (%d chars)", session_id, len(resume_text))

    return ResumeUploadResponse(
        status="success",
        message=f"Resume '{file_name}' uploaded and processed successfully",
        file_name=file_name,
        file_size=file_size,
        character_count=len(resume_text),
        session_id=session_id,
    )
