import React, { useRef, useState } from 'react';
import './Sidebar.css';

function Sidebar({ resumeFile, onResumeUpload, jobUrls, onAddJobUrl, onRemoveJobUrl, onAnalyze }) {
  const fileInputRef = useRef(null);
  const [currentUrl, setCurrentUrl] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    console.log(file);
    
    if (file) {
      onResumeUpload(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleAddUrl = () => {
    if (currentUrl.trim()) {
      onAddJobUrl(currentUrl);
      setCurrentUrl('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddUrl();
    }
  };

  return (
    <aside className="sidebar">
      <div className="input-section">
        <label className="label">Resume</label>
        <div className="upload-area" onClick={handleUploadClick}>
          <div className="upload-icon">📄</div>
          <p>
            <strong>Upload your CV</strong><br />
            PDF, DOCX, or DOC format
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>
        {resumeFile && (
          <div className="file-status">
            <span className="file-icon">✓</span>
            <span className="file-name">{resumeFile.name}</span>
          </div>
        )}
      </div>

      <div className="input-section">
        <label className="label">Job Postings</label>
        <div className="url-input-wrapper">
          <input
            type="text"
            value={currentUrl}
            onChange={(e) => setCurrentUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter job posting URL"
          />
          <button className="add-url-button" onClick={handleAddUrl}>
            Add
          </button>
        </div>
        
        {jobUrls.length > 0 && (
          <div className="job-urls-list">
            {jobUrls.map((url, index) => (
              <div key={index} className="job-url-item">
                <span className="url-number">{index + 1}</span>
                <span className="url-text" title={url}>
                  {url.length > 35 ? url.substring(0, 35) + '...' : url}
                </span>
                <button 
                  className="remove-url-button"
                  onClick={() => onRemoveJobUrl(index)}
                  aria-label="Remove URL"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        
        {jobUrls.length > 0 && (
          <div className="url-count">
            {jobUrls.length} job{jobUrls.length !== 1 ? 's' : ''} added
          </div>
        )}
      </div>

      <div className="input-section">
        <button className="analyze-button" onClick={onAnalyze}>
          <span>Begin Analysis</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
