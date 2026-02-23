import React from 'react';
import './LoadingScreen.css';

function LoadingScreen({ isActive }) {
  return (
    <div className={`loading-screen ${isActive ? 'active' : ''}`}>
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <div className="loading-text">Analyzing</div>
        <div className="loading-subtext">Processing your resume and job requirements</div>
      </div>
    </div>
  );
}

export default LoadingScreen;
