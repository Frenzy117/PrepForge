"""Backward-compatible re-export. Prefer backend.agents.tools.resume_extractor."""
from backend.agents.tools.resume_extractor import (
    extract_resume_text,
    extract_resume_text_bytes,
    extract_resume_text_from_path,
)

__all__ = ["extract_resume_text", "extract_resume_text_bytes", "extract_resume_text_from_path"]
