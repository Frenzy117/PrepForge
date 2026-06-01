import logging

from fastapi import APIRouter, HTTPException, Request, Response

from backend.api.models import ApiKeyRequest, ApiKeyResponse
from backend.api.session import ensure_session_cookie

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/settings/api_key", response_model=ApiKeyResponse)
async def set_api_key(req: ApiKeyRequest, request: Request, response: Response):
    """Store a per-session Mistral API key supplied by the user."""
    session_id, session = ensure_session_cookie(request, response)
    api_key = req.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")
    session.mistral_api_key = api_key
    logger.info("Session %s: stored user mistral_api_key (masked)", session_id)
    return ApiKeyResponse(status="success", message="API key stored for session")


@router.get("/settings/api_key", response_model=ApiKeyResponse)
async def get_api_key(request: Request):
    from backend.api.session import get_session_id_from_request, session_store

    session_id = get_session_id_from_request(request)
    if not session_id:
        raise HTTPException(status_code=404, detail="No session")
    session = session_store.get(session_id)
    if not session or not session.mistral_api_key:
        return ApiKeyResponse(status="empty", message="No API key set for this session")
    masked = session.mistral_api_key[:4] + "..." + session.mistral_api_key[-4:]
    return ApiKeyResponse(status="present", message=f"API key set (masked: {masked})")
