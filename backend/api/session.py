import uuid
from dataclasses import dataclass, field
from typing import Optional

from fastapi import HTTPException, Request, Response

from backend.api.models import AnalysisResult, JobEntry

SESSION_COOKIE = "prepforge_session"
MAX_CHAT_MESSAGES = 20


@dataclass
class SessionData:
    resume_text: Optional[str] = None
    resume_file_name: Optional[str] = None
    # Per-session Mistral API key (allows users to provide their own key)
    mistral_api_key: Optional[str] = None
    jobs: list[JobEntry] = field(default_factory=list)
    analysis: Optional[AnalysisResult] = None
    chat_messages: list[dict] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, SessionData] = {}

    def create(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SessionData()
        return session_id

    def get(self, session_id: str) -> Optional[SessionData]:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: Optional[str]) -> tuple[str, SessionData]:
        if session_id and session_id in self._sessions:
            return session_id, self._sessions[session_id]
        new_id = self.create()
        return new_id, self._sessions[new_id]

    def delete_job(self, session_id: str, job_id: str) -> bool:
        session = self.get(session_id)
        if not session:
            return False
        before = len(session.jobs)
        session.jobs = [j for j in session.jobs if j.id != job_id]
        return len(session.jobs) < before


# Process-wide store (Phase A)
session_store = SessionStore()


def get_session_id_from_request(request: Request) -> Optional[str]:
    return request.cookies.get(SESSION_COOKIE)


def resolve_session(request: Request, response: Optional[Response] = None) -> tuple[str, SessionData]:
    cookie_id = get_session_id_from_request(request)
    session_id, data = session_store.get_or_create(cookie_id)
    if response is not None and cookie_id != session_id:
        _set_session_cookie(response, session_id)
    return session_id, data


def ensure_session_cookie(request: Request, response: Response) -> tuple[str, SessionData]:
    cookie_id = get_session_id_from_request(request)
    if cookie_id and session_store.get(cookie_id):
        return cookie_id, session_store.get(cookie_id)
    session_id, data = session_store.get_or_create(cookie_id)
    _set_session_cookie(response, session_id)
    return session_id, data


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )


def require_resume(session: SessionData) -> None:
    if not session.resume_text:
        raise HTTPException(status_code=400, detail="Upload a resume before continuing.")


def require_jobs(session: SessionData) -> None:
    if not session.jobs:
        raise HTTPException(status_code=400, detail="Add at least one job posting.")
