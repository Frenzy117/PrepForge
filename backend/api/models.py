from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    response: str


class ResumeUploadResponse(BaseModel):
    status: str
    message: str
    file_name: str
    file_size: int
    character_count: int
    session_id: str


class ResumeUploadError(BaseModel):
    status: str
    message: str
    detail: Optional[str] = None


class JobEntryInput(BaseModel):
    id: Optional[str] = None
    source: Literal["url", "paste"]
    url: Optional[str] = None
    title: Optional[str] = None
    raw_text: Optional[str] = None


class JobEntry(BaseModel):
    id: str
    source: Literal["url", "paste"]
    url: Optional[str] = None
    title: Optional[str] = None
    raw_text: Optional[str] = None
    summary: Optional[str] = None


class JobsRequest(BaseModel):
    jobs: list[JobEntryInput]


class JobsResponse(BaseModel):
    jobs: list[JobEntry]


class JobMatch(BaseModel):
    job_id: str
    job_title: str
    company: Optional[str] = None
    match_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommendation: str = ""


class MetricItem(BaseModel):
    value: str
    label: str


class AnalysisResult(BaseModel):
    overall_summary: str
    best_fit_job_id: Optional[str] = None
    jobs: list[JobMatch] = Field(default_factory=list)
    metrics: list[MetricItem] = Field(default_factory=list)
    development_areas: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    analysis: AnalysisResult
    markdown_report: str


class ResultsViewData(BaseModel):
    """Shape expected by the frontend Results component."""
    metrics: list[dict[str, str]]
    strengths: list[str]
    recommendations: list[str]
    development: list[str]
    jobs: list[JobMatch] = Field(default_factory=list)
    overall_summary: str = ""

    @classmethod
    def from_analysis(cls, analysis: AnalysisResult) -> "ResultsViewData":
        all_strengths: list[str] = []
        all_recommendations: list[str] = []
        for job in analysis.jobs:
            for s in job.strengths[:2]:
                label = job.job_title
                all_strengths.append(f"[{label}] {s}")
            if job.recommendation:
                all_recommendations.append(f"[{job.job_title}] {job.recommendation}")

        return cls(
            metrics=[m.model_dump() for m in analysis.metrics],
            strengths=all_strengths or ["See per-job breakdown below."],
            recommendations=all_recommendations or ["Review each job match for tailored advice."],
            development=analysis.development_areas,
            jobs=analysis.jobs,
            overall_summary=analysis.overall_summary,
        )


class ApiKeyRequest(BaseModel):
    api_key: str


class ApiKeyResponse(BaseModel):
    status: str
    message: str


class BugReportRequest(BaseModel):
    subject: str
    description: str
    contact_email: Optional[str] = None


class BugReportResponse(BaseModel):
    status: str
    message: str
