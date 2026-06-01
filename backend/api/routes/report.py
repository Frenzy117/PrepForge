import logging
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException, Request, Response

from backend.api.models import BugReportRequest, BugReportResponse
from backend.api.session import ensure_session_cookie
from backend.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/report", response_model=BugReportResponse)
async def report_bug(req: BugReportRequest, request: Request, response: Response):
    """Accept a bug report and email it to the configured recipient if available.

    If SMTP is not configured, the bug will be logged instead.
    """
    session_id, session = ensure_session_cookie(request, response)
    settings = get_settings()

    recipient = getattr(settings, "bug_report_recipient", "")
    smtp_server = getattr(settings, "smtp_server", "")
    smtp_port = getattr(settings, "smtp_port", 0)
    smtp_user = getattr(settings, "smtp_user", "")
    smtp_password = getattr(settings, "smtp_password", "")
    use_tls = getattr(settings, "smtp_use_tls", True)

    subject = f"[Bug Report] {req.subject} (session {session_id})"
    body_lines = [
        f"Session ID: {session_id}",
        f"Contact: {req.contact_email or 'N/A'}",
        "",
        "Description:",
        req.description,
    ]
    body = "\n".join(body_lines)

    if smtp_server and recipient:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = smtp_user or "noreply@example.com"
            msg["To"] = recipient
            msg.set_content(body)

            if use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port or 587, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_server, smtp_port or 25, timeout=10)
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            logger.info("Session %s: bug report emailed to %s", session_id, recipient)
            return BugReportResponse(status="sent", message="Bug report emailed")
        except Exception as e:
            logger.exception("Failed to send bug report email: %s", e)
            # fall through to logging

    # If SMTP not configured or sending failed, log the report for manual review
    logger.warning("Bug report (session %s): %s", session_id, body)
    return BugReportResponse(status="logged", message="Bug report logged (SMTP not configured or failed)")
