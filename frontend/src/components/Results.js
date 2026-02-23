import React from 'react';
import './Results.css';

function Results({ data }) {
  if (!data) return null;

  return (
    <div id="results" className="results">
      <div className="divider"></div>

      <div className="section-header">
        <h2 className="section-title">Analysis Report</h2>
        <p className="section-subtitle">Detailed evaluation of your fit for the position</p>
      </div>

      <div className="metrics">
        {data.metrics.map((metric, index) => (
          <div key={index} className="metric">
            <div className="metric-value">{metric.value}</div>
            <div className="metric-label">{metric.label}</div>
          </div>
        ))}
      </div>

      <div className="analysis">
        <div className="analysis-section">
          <h4>Strengths</h4>
          <ul>
            {data.strengths.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="analysis-section">
          <h4>Recommendations</h4>
          <ul>
            {data.recommendations.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="analysis-section">
          <h4>Areas for Development</h4>
          <ul>
            {data.development.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Results;
