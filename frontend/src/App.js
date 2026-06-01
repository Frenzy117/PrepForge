import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import Sidebar from './components/Sidebar';
import AgentsGrid from './components/AgentsGrid';
import Results from './components/Results';
import ChatInterface from './components/ChatInterface';
import LoadingScreen from './components/LoadingScreen';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const fetchOpts = { credentials: 'include' };

function generateId() {
  return `job-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function analysisToResultsView(analysis) {
  const allStrengths = [];
  const allRecommendations = [];
  for (const job of analysis.jobs || []) {
    for (const s of (job.strengths || []).slice(0, 2)) {
      allStrengths.push(`[${job.job_title}] ${s}`);
    }
    if (job.recommendation) {
      allRecommendations.push(`[${job.job_title}] ${job.recommendation}`);
    }
  }
  return {
    metrics: (analysis.metrics || []).map((m) => ({
      value: m.value,
      label: m.label,
    })),
    strengths: allStrengths.length ? allStrengths : ['See per-job breakdown below.'],
    recommendations: allRecommendations.length
      ? allRecommendations
      : ['Review each job match for tailored advice.'],
    development: analysis.development_areas || [],
    jobs: analysis.jobs || [],
    overall_summary: analysis.overall_summary || '',
  };
}

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadingResume, setIsUploadingResume] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [messages, setMessages] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);

  const handleResumeUpload = async (file) => {
    setIsUploadingResume(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        ...fetchOpts,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload resume');
      }

      const data = await response.json();
      setResumeFile(file);
      setUploadError(null);

      const successMessage = {
        role: 'assistant',
        content: `Resume uploaded successfully.\n\n**File:** ${data.file_name}\n**Size:** ${(data.file_size / 1024).toFixed(2)} KB\n**Extracted:** ${data.character_count} characters\n\nAdd job URLs or paste descriptions, then click Begin Analysis.`,
      };
      setMessages([successMessage]);
    } catch (error) {
      console.error('Resume upload error:', error);
      setUploadError(error.message);
      setMessages([
        {
          role: 'assistant',
          content: `**Upload Failed**\n\n${error.message}\n\nPlease use PDF or DOCX format.`,
        },
      ]);
    } finally {
      setIsUploadingResume(false);
    }
  };

  const handleAddJob = (jobEntry) => {
    setJobs((prev) => [...prev, { ...jobEntry, id: jobEntry.id || generateId() }]);
  };

  const handleRemoveJob = (index) => {
    setJobs((prev) => prev.filter((_, i) => i !== index));
  };

  const jobsToApiPayload = () =>
    jobs.map((j) => ({
      id: j.id,
      source: j.source,
      url: j.source === 'url' ? j.url : null,
      title: j.title || null,
      raw_text: j.source === 'paste' ? j.raw_text : null,
    }));

  const handleAnalyze = async () => {
    if (!resumeFile) {
      setUploadError('Please upload your resume first');
      return;
    }
    if (jobs.length === 0) {
      setUploadError('Add at least one job URL or pasted description');
      return;
    }

    setIsLoading(true);
    setUploadError(null);

    const jobLabels = jobs.map((j, i) => {
      const label =
        j.source === 'url'
          ? j.url
          : j.title || `Pasted description (${(j.raw_text || '').slice(0, 40)}...)`;
      return `${i + 1}. ${label}`;
    });

    setMessages([
      {
        role: 'assistant',
        content: `Analyzing your resume against ${jobs.length} job posting${jobs.length > 1 ? 's' : ''}...\n\n${jobLabels.join('\n')}`,
      },
    ]);

    try {
      const jobsRes = await fetch(`${API_BASE_URL}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jobs: jobsToApiPayload() }),
        ...fetchOpts,
      });
      if (!jobsRes.ok) {
        const err = await jobsRes.json();
        throw new Error(err.detail || 'Failed to save jobs');
      }

      const analyzeRes = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        ...fetchOpts,
      });
      if (!analyzeRes.ok) {
        const err = await analyzeRes.json();
        throw new Error(err.detail || 'Analysis failed');
      }

      const data = await analyzeRes.json();
      const resultsView = analysisToResultsView(data.analysis);
      setAnalysisData(resultsView);
      setShowResults(true);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.markdown_report || data.analysis.overall_summary,
        },
      ]);

      setTimeout(() => {
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (error) {
      console.error('Analysis error:', error);
      setUploadError(error.message);
      setMessages([
        {
          role: 'assistant',
          content: `**Analysis Failed**\n\n${error.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message) => {
    if (!resumeFile) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Please upload your resume first before asking questions.' },
      ]);
      return;
    }

    setMessages((prev) => [...prev, { role: 'user', content: message }]);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message }),
        ...fetchOpts,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to process message');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Message error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${error.message}` },
      ]);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <Header />
        <Hero />

        <div className="workspace">
          <Sidebar
            resumeFile={resumeFile}
            onResumeUpload={handleResumeUpload}
            isUploadingResume={isUploadingResume}
            uploadError={uploadError}
            jobs={jobs}
            onAddJob={handleAddJob}
            onRemoveJob={handleRemoveJob}
            onAnalyze={handleAnalyze}
            resumeUploaded={!!resumeFile}
            isLoading={isLoading}
          />

          <main className="content">
            <div className="section-header">
              <h2 className="section-title">System Overview</h2>
              <p className="section-subtitle">
                Three specialized agents working in concert to evaluate your candidacy
              </p>
            </div>

            <AgentsGrid />

            {messages.length > 0 && (
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                disabled={isLoading || isUploadingResume}
              />
            )}

            {showResults && analysisData && <Results data={analysisData} />}
          </main>
        </div>
      </div>

      <LoadingScreen isActive={isLoading || isUploadingResume} />
    </div>
  );
}

export default App;
