import React from 'react';
import './AgentCard.css';

function AgentCard({ title, subtitle, description, capabilities }) {
  return (
    <article className="agent-card">
      <div className="agent-header">
        <div className="agent-info">
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <div className="agent-badge">ACTIVE</div>
      </div>
      <p className="agent-description">{description}</p>
      <div className="capabilities">
        {capabilities.map((capability, index) => (
          <div key={index} className="capability">
            {capability}
          </div>
        ))}
      </div>
    </article>
  );
}

export default AgentCard;
