import React from 'react';
import AgentCard from './AgentCard';
import './AgentsGrid.css';

const agentsData = [
  {
    title: 'Resume Parser',
    subtitle: 'Document Intelligence',
    description: 'Extracts structured information from your CV across multiple formats. Identifies key experience markers, technical skills, educational background, and career trajectory to build a comprehensive professional profile.',
    capabilities: [
      'Multi-format support',
      'Skills extraction',
      'Experience mapping',
      'Timeline analysis'
    ]
  },
  {
    title: 'Job Analyzer',
    subtitle: 'Requirements Intelligence',
    description: 'Navigates job boards and extracts comprehensive posting details. Structures requirements, responsibilities, qualifications, and compensation data into analyzable components for precise matching.',
    capabilities: [
      'Web scraping',
      'Requirement parsing',
      'Role classification',
      'Benefit analysis'
    ]
  },
  {
    title: 'Strategy Advisor',
    subtitle: 'Career Intelligence',
    description: 'Orchestrates the analysis pipeline, performs semantic matching between your profile and job requirements, identifies skill gaps, and provides strategic guidance tailored to your career objectives.',
    capabilities: [
      'Match scoring',
      'Gap identification',
      'CV optimization',
      'Strategic advice'
    ]
  }
];

function AgentsGrid() {
  return (
    <div className="agents-grid">
      {agentsData.map((agent, index) => (
        <AgentCard key={index} {...agent} />
      ))}
    </div>
  );
}

export default AgentsGrid;
