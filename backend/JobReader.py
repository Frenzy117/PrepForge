"""Backward-compatible re-export. Prefer backend.agents.tools.job_reader."""
from backend.agents.tools.job_reader import get_job_summary, scrape_and_summarize, summarize_job_description

__all__ = ["get_job_summary", "scrape_and_summarize", "summarize_job_description"]
