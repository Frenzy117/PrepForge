"""Phase A unit tests (no Playwright, no live LLM)."""

from backend.api.models import AnalysisResult, JobEntry, JobEntryInput, ResultsViewData
from backend.services.analyze import _extract_json, _fallback_analysis
from backend.services.job_ingest import jobs_from_inputs


def test_jobs_from_inputs_paste():
    entries = jobs_from_inputs(
        [
            JobEntryInput(
                source="paste",
                raw_text="Senior Python Developer at Acme Corp",
                title="Python Dev",
            )
        ]
    )
    assert len(entries) == 1
    assert entries[0].source == "paste"
    assert entries[0].raw_text.startswith("Senior")


def test_extract_json_from_fence():
    raw = '```json\n{"overall_summary": "ok", "jobs": [], "metrics": [], "development_areas": []}\n```'
    data = _extract_json(raw)
    assert data["overall_summary"] == "ok"


def test_fallback_analysis():
    jobs = [
        JobEntry(id="1", source="paste", raw_text="test", title="Role A"),
    ]
    result = _fallback_analysis(jobs, "partial")
    assert isinstance(result, AnalysisResult)
    assert len(result.jobs) == 1


def test_results_view_from_analysis():
    analysis = AnalysisResult(
        overall_summary="Good fit overall.",
        jobs=[
            {
                "job_id": "1",
                "job_title": "Engineer",
                "match_score": 80,
                "strengths": ["Python"],
                "gaps": ["K8s"],
                "recommendation": "Apply",
            }
        ],
        metrics=[{"value": "80%", "label": "Best Match"}],
        development_areas=["Learn K8s"],
    )
    view = ResultsViewData.from_analysis(analysis)
    assert view.metrics[0]["value"] == "80%"
    assert len(view.jobs) == 1
