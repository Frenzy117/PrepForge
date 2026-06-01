import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Results.css';

function Results({ data }) {
  if (!data) return null;

  return (
    <div id="results" className="results">
      <div className="divider"></div>

      <div className="section-header">
        <h2 className="section-title">Analysis Report</h2>
        <p className="section-subtitle">
          {data.overall_summary
            ? data.overall_summary.slice(0, 160) + (data.overall_summary.length > 160 ? '...' : '')
            : 'Detailed evaluation of your fit for each position'}
        </p>
      </div>

      {data.metrics && data.metrics.length > 0 && (
        <div className="metrics">
          {data.metrics.map((metric, index) => (
            <div key={index} className="metric">
              <div className="metric-value">{metric.value}</div>
              <div className="metric-label">{metric.label}</div>
            </div>
          ))}
        </div>
      )}

      {data.jobs && data.jobs.length > 0 && (
        <div className="job-matches">
          <h3 className="job-matches-title">Per-job match</h3>
          {data.jobs.map((job) => (
            <div key={job.job_id} className="job-match-card">
              <div className="job-match-header">
                <h4>{job.job_title}</h4>
                <span className="job-match-score">{job.match_score}%</span>
              </div>
              {job.company && <p className="job-match-company">{job.company}</p>}
              <div className="job-match-columns">
                <div>
                  <h5>Strengths</h5>
                  <div className="markdown-block">
                    {(() => {
                      const md = (job.strengths || []).map((it) => {
                        if (/\n/.test(it) && /\d+\.\s+/.test(it)) {
                          const parts = it.split('\n');
                          const first = parts.shift();
                          const rest = parts.map((l) => '  ' + l).join('\n');
                          return `- ${first}\n${rest}`;
                        }
                        return `- ${it}`;
                      }).join('\n');
                      return <ReactMarkdown>{md}</ReactMarkdown>;
                    })()}
                  </div>
                </div>
                <div>
                  <h5>Gaps</h5>
                  <div className="markdown-block">
                    {(() => {
                      const md = (job.gaps || []).map((it) => {
                        if (/\n/.test(it) && /\d+\.\s+/.test(it)) {
                          const parts = it.split('\n');
                          const first = parts.shift();
                          const rest = parts.map((l) => '  ' + l).join('\n');
                          return `- ${first}\n${rest}`;
                        }
                        return `- ${it}`;
                      }).join('\n');
                      return <ReactMarkdown>{md}</ReactMarkdown>;
                    })()}
                  </div>
                </div>
              </div>
              {job.recommendation && (
                <div className="job-match-recommendation">
                  <strong>Recommendation:</strong>
                  <div className="job-match-recommendation-text">
                    <ReactMarkdown>{job.recommendation}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="analysis">
        <div className="analysis-section">
          <h4>Strengths</h4>
          <ul>
            {(data.strengths || []).map((item, index) => (
              <li key={index}><ReactMarkdown>{item}</ReactMarkdown></li>
            ))}
          </ul>
        </div>

        <div className="analysis-section">
          <h4>Recommendations</h4>
          <ul>
            {(data.recommendations || []).map((item, index) => (
              <li key={index}><ReactMarkdown>{item}</ReactMarkdown></li>
            ))}
          </ul>
        </div>

        <div className="analysis-section">
          <h4>Areas for Development</h4>
          <ul>
            {(data.development || []).map((item, index) => (
              <li key={index}><ReactMarkdown>{item}</ReactMarkdown></li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Results;
