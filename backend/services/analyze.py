import json
import logging
import re

from langchain_mistralai import ChatMistralAI

from backend.agents.prompts.templates import analysisJsonPrompt
from backend.api.models import AnalysisResult, JobEntry, JobMatch, MetricItem
from backend.services.job_ingest import ingest_all_jobs

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _build_markdown_report(analysis: AnalysisResult, jobs: list[JobEntry]) -> str:
    lines = [f"## Analysis Summary\n\n{analysis.overall_summary}\n"]
    job_titles = {j.id: j.title or j.url or j.id for j in jobs}
    for match in analysis.jobs:
        title = job_titles.get(match.job_id, match.job_title)
        lines.append(f"\n### {title} — {match.match_score}% match\n")
        if match.company:
            lines.append(f"**Company:** {match.company}\n")
        lines.append("\n**Strengths:**\n")
        for s in match.strengths:
            lines.append(f"- {s}\n")
        lines.append("\n**Gaps:**\n")
        for g in match.gaps:
            lines.append(f"- {g}\n")
        lines.append(f"\n**Recommendation:** {match.recommendation}\n")
    if analysis.development_areas:
        lines.append("\n### Areas for Development\n")
        for d in analysis.development_areas:
            lines.append(f"- {d}\n")
    return "".join(lines)


async def run_analysis(resume_text: str, jobs: list[JobEntry]) -> tuple[AnalysisResult, str, list[JobEntry]]:
    """Ingest jobs then produce structured analysis."""
    ingested = await ingest_all_jobs(jobs)

    jobs_payload = [
        {
            "job_id": j.id,
            "title": j.title or (j.url or "Pasted job"),
            "summary": j.summary or "No summary available.",
        }
        for j in ingested
    ]

    from backend.config import get_settings

    settings = get_settings()
    llm = ChatMistralAI(
        model="mistral-medium-2508",
        api_key=settings.mistral_api_key,
    )
    prompt = analysisJsonPrompt.invoke(
        {
            "resume_text": resume_text[:12000],
            "jobs_json": json.dumps(jobs_payload, indent=2),
        }
    )
    raw = llm.invoke(prompt).content
    try:
        data = _extract_json(raw)
        analysis = AnalysisResult.model_validate(data)
    except Exception as e:
        logger.warning("Failed to parse analysis JSON: %s", e)
        analysis = _fallback_analysis(ingested, raw)

    if not analysis.metrics:
        best = max((j.match_score for j in analysis.jobs), default=0)
        analysis.metrics = [
            MetricItem(value=f"{best}%", label="Best Match"),
            MetricItem(value=str(len(analysis.jobs)), label="Jobs Compared"),
            MetricItem(value=str(len(analysis.development_areas)), label="Growth Areas"),
        ]

    markdown = _build_markdown_report(analysis, ingested)
    return analysis, markdown, ingested


def _fallback_analysis(jobs: list[JobEntry], raw_text: str) -> AnalysisResult:
    matches = [
        JobMatch(
            job_id=j.id,
            job_title=j.title or j.url or "Job",
            company=None,
            match_score=50,
            strengths=["Analysis could not be fully structured."],
            gaps=["Re-run analysis or try a shorter job description."],
            recommendation="Review the job summary manually.",
        )
        for j in jobs
    ]
    return AnalysisResult(
        overall_summary=raw_text[:2000] if raw_text else "Analysis completed with limited structure.",
        best_fit_job_id=jobs[0].id if jobs else None,
        jobs=matches,
        metrics=[
            MetricItem(value="—", label="Overall Match"),
            MetricItem(value=str(len(jobs)), label="Jobs Compared"),
            MetricItem(value="—", label="Growth Areas"),
        ],
        development_areas=["Retry analysis for structured scores."],
    )
