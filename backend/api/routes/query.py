import logging

from fastapi import APIRouter, HTTPException, Request, Response
from langchain_core.messages import AIMessage, HumanMessage

from backend.api.models import QueryRequest, QueryResponse
from backend.api.session import ensure_session_cookie, require_resume
from backend.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_HISTORY = 20


def _build_context(session) -> str:
    parts = []
    if session.analysis:
        parts.append(f"## Previous analysis\n{session.analysis.overall_summary}\n")
        for job in session.analysis.jobs:
            parts.append(
                f"- {job.job_title} ({job.match_score}%): "
                f"strengths={', '.join(job.strengths[:2])}; gaps={', '.join(job.gaps[:2])}"
            )
    if session.jobs:
        parts.append("\n## Job postings\n")
        for j in session.jobs:
            label = j.title or j.url or j.id
            parts.append(f"### {label} (id={j.id})\n{j.summary or 'No summary yet.'}\n")
    if session.resume_text:
        parts.append(f"\n## Resume\n{session.resume_text[:8000]}\n")
    return "\n".join(parts)


@router.post("/query", response_model=QueryResponse)
async def run_query(req: QueryRequest, request: Request, response: Response):
    """Chat follow-up with session context and conversation history."""
    try:
        session_id, session = ensure_session_cookie(request, response)
        require_resume(session)

        react_graph = request.app.state.react_graph
        context = _build_context(session)

        # Apply per-session Mistral API key if present
        settings = get_settings()
        if getattr(session, "mistral_api_key", None):
            settings.mistral_api_key = session.mistral_api_key

        session.chat_messages.append({"role": "user", "content": req.query})
        session.chat_messages = session.chat_messages[-MAX_HISTORY:]

        messages = []
        if context:
            messages.append(
                HumanMessage(
                    content=f"Use this session context when answering:\n\n{context}"
                )
            )
        for turn in session.chat_messages[:-1]:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        messages.append(HumanMessage(content=req.query))

        result = await react_graph.ainvoke({"messages": messages})
        last_message = result["messages"][-1]
        response_text = (
            last_message.content if hasattr(last_message, "content") else str(last_message)
        )

        session.chat_messages.append({"role": "assistant", "content": response_text})
        session.chat_messages = session.chat_messages[-MAX_HISTORY:]

        logger.info("Session %s: query answered", session_id)
        return QueryResponse(response=response_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
