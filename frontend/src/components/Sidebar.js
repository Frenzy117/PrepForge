import React, { useRef, useState } from 'react';
import './Sidebar.css';
import ApiKeyModal from './ApiKeyModal';

function Sidebar({
  resumeFile,
  onResumeUpload,
  isUploadingResume,
  uploadError,
  jobs,
  onAddJob,
  onRemoveJob,
  onAnalyze,
  resumeUploaded,
  isLoading,
}) {
  const fileInputRef = useRef(null);
  const [inputMode, setInputMode] = useState('url');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [currentUrl, setCurrentUrl] = useState('');
  const [pasteTitle, setPasteTitle] = useState('');
  const [pasteText, setPasteText] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onResumeUpload(file);
    }
  };

  const handleUploadClick = () => {
    if (!isUploadingResume) {
      fileInputRef.current?.click();
    }
  };

  const handleAddUrl = () => {
    const url = currentUrl.trim();
    if (!url) return;
    onAddJob({ source: 'url', url, title: null, raw_text: null });
    setCurrentUrl('');
  };

  const handleAddPaste = () => {
    const text = pasteText.trim();
    if (!text) return;
    onAddJob({
      source: 'paste',
      url: null,
      title: pasteTitle.trim() || 'Pasted job',
      raw_text: text,
    });
    setPasteTitle('');
    setPasteText('');
  };

  const disabled = isUploadingResume || isLoading;
  const canAnalyze = resumeUploaded && jobs.length > 0 && !disabled;

  const jobLabel = (job) => {
    if (job.source === 'url') {
      const u = job.url || '';
      return u.length > 35 ? `${u.substring(0, 35)}...` : u;
    }
    return job.title || 'Pasted description';
  };

  return (
    <aside className="sidebar">
      <div style={{ marginBottom: 12 }}>
        <button
          type="button"
          className="analyze-button"
          onClick={() => setShowApiKeyModal(true)}
        >
          Set API Key
        </button>
        {showApiKeyModal && <ApiKeyModal onClose={() => setShowApiKeyModal(false)} />}
      </div>
      <div className="input-section">
        <label className="label">Resume</label>
        <div
          className={`upload-area ${isUploadingResume ? 'uploading' : ''} ${resumeUploaded ? 'uploaded' : ''}`}
          onClick={handleUploadClick}
          style={{
            cursor: isUploadingResume ? 'not-allowed' : 'pointer',
            opacity: isUploadingResume ? 0.6 : 1,
          }}
        >
          <div className="upload-icon">{isUploadingResume ? '⏳' : '📄'}</div>
          <p>
            <strong>{isUploadingResume ? 'Uploading...' : 'Upload your CV'}</strong>
            <br />
            {isUploadingResume ? 'Processing your resume...' : 'PDF or DOCX format'}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            style={{ display: 'none' }}
            onChange={handleFileChange}
            disabled={isUploadingResume}
          />
        </div>

        {uploadError && <div className="file-error">⚠️ {uploadError}</div>}

        {resumeFile && !uploadError && (
          <div className="file-status">
            <span className="file-icon">✓</span>
            <span className="file-name">{resumeFile.name}</span>
          </div>
        )}
      </div>

      <div className="input-section">
        <label className="label">Job Postings</label>

        <div className="job-mode-toggle">
          <button
            type="button"
            className={inputMode === 'url' ? 'mode-active' : ''}
            onClick={() => setInputMode('url')}
            disabled={disabled}
          >
            URL
          </button>
          <button
            type="button"
            className={inputMode === 'paste' ? 'mode-active' : ''}
            onClick={() => setInputMode('paste')}
            disabled={disabled}
          >
            Paste description
          </button>
        </div>

        {inputMode === 'url' ? (
          <>
            <p className="url-hint">
              Indeed links are supported. If a URL fails, use Paste description.
            </p>
            <div className="url-input-wrapper">
            <input
              type="text"
              value={currentUrl}
              onChange={(e) => setCurrentUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddUrl()}
              placeholder="Indeed or other job URL"
              disabled={disabled}
            />
            <button type="button" className="add-url-button" onClick={handleAddUrl} disabled={disabled}>
            Add
          </button>
        </div>
          </>
        ) : (
          <div className="paste-input-wrapper">
            <input
              type="text"
              value={pasteTitle}
              onChange={(e) => setPasteTitle(e.target.value)}
              placeholder="Optional label (e.g. Senior Engineer)"
              disabled={disabled}
              className="paste-title-input"
            />
            <textarea
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder="Paste the full job description here..."
              rows={5}
              disabled={disabled}
              className="paste-textarea"
            />
            <button type="button" className="add-url-button" onClick={handleAddPaste} disabled={disabled}>
              Add
            </button>
          </div>
        )}

        {jobs.length > 0 && (
          <div className="job-urls-list">
            {jobs.map((job, index) => (
              <div key={job.id || index} className="job-url-item">
                <span className="url-number">{job.source === 'url' ? '🔗' : '📝'}</span>
                <span className="url-text" title={job.source === 'url' ? job.url : job.raw_text}>
                  {jobLabel(job)}
                </span>
                <button
                  type="button"
                  className="remove-url-button"
                  onClick={() => onRemoveJob(index)}
                  aria-label="Remove job"
                  disabled={disabled}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {jobs.length > 0 && (
          <div className="url-count">
            {jobs.length} job{jobs.length !== 1 ? 's' : ''} added
          </div>
        )}
      </div>

      <div className="input-section">
        <button
          type="button"
          className="analyze-button"
          onClick={onAnalyze}
          disabled={!canAnalyze}
          title={!resumeUploaded ? 'Upload your resume first' : jobs.length === 0 ? 'Add at least one job' : ''}
        >
          <span>{isLoading ? 'Analyzing...' : '▶ Begin Analysis'}</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
