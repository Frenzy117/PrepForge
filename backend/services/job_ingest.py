import asyncio
import logging
import uuid

from backend.agents.tools.job_reader import scrape_and_summarize, summarize_job_description
from backend.api.models import JobEntry, JobEntryInput

logger = logging.getLogger(__name__)


def _normalize_input(entry: JobEntryInput) -> JobEntry:
    job_id = entry.id or str(uuid.uuid4())
    return JobEntry(
        id=job_id,
        source=entry.source,
        url=entry.url,
        title=entry.title,
        raw_text=entry.raw_text,
        summary=None,
    )


async def ingest_job(entry: JobEntry) -> JobEntry:
    """Ingest a single job from URL or pasted text."""
    if entry.source == "paste":
        if not entry.raw_text or not entry.raw_text.strip():
            entry.summary = "No job description text provided."
            return entry
        entry.summary = summarize_job_description(entry.raw_text)
        return entry

    if entry.source == "url":
        if not entry.url or not entry.url.strip():
            entry.summary = "No job URL provided."
            return entry
        entry.summary = await scrape_and_summarize(entry.url.strip())
        return entry

    entry.summary = "Unknown job source."
    return entry


async def ingest_all_jobs(jobs: list[JobEntry]) -> list[JobEntry]:
    return list(await asyncio.gather(*[ingest_job(j) for j in jobs]))


def jobs_from_inputs(inputs: list[JobEntryInput]) -> list[JobEntry]:
    return [_normalize_input(j) for j in inputs]
