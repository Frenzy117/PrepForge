from backend.agents.tools.indeed_fetch import parse_indeed_html

SAMPLE_HTML = """
<html><body>
<h1 class="jobsearch-JobInfoHeader-title">Software Engineer</h1>
<div data-testid="inlineHeader-companyName">Acme Corp</div>
<div id="jobDescriptionText"><p>Build APIs with Python.</p></div>
</body></html>
"""


def test_parse_indeed_html():
    text = parse_indeed_html(SAMPLE_HTML)
    assert text is not None
    assert "Software Engineer" in text
    assert "Acme Corp" in text
    assert "Build APIs" in text
