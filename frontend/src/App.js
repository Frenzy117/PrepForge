import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import Sidebar from './components/Sidebar';
import AgentsGrid from './components/AgentsGrid';
import Results from './components/Results';
import ChatInterface from './components/ChatInterface';
import LoadingScreen from './components/LoadingScreen';

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobUrls, setJobUrls] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [messages, setMessages] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);

  const handleResumeUpload = (file) => {
    setResumeFile(file);
  };

  const handleAddJobUrl = (url) => {
    if (url.trim() && !jobUrls.includes(url.trim())) {
      setJobUrls([...jobUrls, url.trim()]);
    }
  };

  const handleRemoveJobUrl = (index) => {
    setJobUrls(jobUrls.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (!resumeFile) {
      alert('Please upload your resume first');
      return;
    }

    if (jobUrls.length === 0) {
      alert('Please add at least one job posting URL');
      return;
    }

    setIsLoading(true);
    
    // Add system message
    const systemMessage = {
      role: 'assistant',
      content: `🔍 Analyzing your resume against ${jobUrls.length} job posting${jobUrls.length > 1 ? 's' : ''}...\n\nI'll process:\n${jobUrls.map((url, i) => `${i + 1}. ${url}`).join('\n')}`
    };
    setMessages([systemMessage]);

    // Simulate API call - replace with actual backend integration
    setTimeout(() => {
      const mockAnalysis = {
        metrics: [
          { value: '87%', label: 'Overall Match' },
          { value: '12', label: 'Skills Aligned' },
          { value: '3', label: 'Growth Areas' }
        ],
        strengths: [
          'Your technical foundation in React, Node.js, and TypeScript aligns directly with the core requirements',
          'Six years of full-stack development experience exceeds minimum requirements',
          'Mobile development expertise with React Native and Expo matches key technologies',
          'Testing experience with Jest demonstrates attention to code quality'
        ],
        recommendations: [
          'Emphasize your experience with NestJS prominently in your CV',
          'Highlight any fintech or trading platform experience',
          'Add specific examples of scalable solutions you\'ve architected',
          'Quantify your impact with metrics where possible'
        ],
        development: [
          'Consider building a small trading dashboard project to demonstrate domain knowledge',
          'Strengthen testing portfolio with integration test coverage',
          'Research market data providers and clearing firms'
        ]
      };

      setAnalysisData(mockAnalysis);
      setIsLoading(false);
      setShowResults(true);

      // Add completion message
      const completionMessage = {
        role: 'assistant',
        content: `✅ **Analysis Complete!**\n\nI've analyzed your resume against all ${jobUrls.length} job posting${jobUrls.length > 1 ? 's' : ''}. Your overall match score is **87%**.\n\nKey highlights:\n• **12 skills** align with requirements\n• **3 areas** identified for growth\n• Strong technical foundation in required technologies\n\nYou can view the detailed report below, or ask me any questions about the analysis!`
      };
      
      setMessages(prev => [...prev, completionMessage]);
      
      // Scroll to results
      setTimeout(() => {
        const resultsElement = document.getElementById('results');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }, 3000);
  };

  const handleSendMessage = (message) => {
    // Add user message
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);

    // Simulate AI response - replace with actual API call
    setTimeout(() => {
      const aiResponse = {
        role: 'assistant',
        content: generateResponse(message, analysisData, resumeFile, jobUrls)
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const generateResponse = (message, analysis, resume, urls) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('strength') || lowerMessage.includes('good')) {
      return `Based on my analysis, your key strengths include:\n\n${analysis?.strengths.map(s => `• ${s}`).join('\n\n')}\n\nThese align particularly well with the requirements I found in the job postings.`;
    } else if (lowerMessage.includes('improve') || lowerMessage.includes('weak') || lowerMessage.includes('gap')) {
      return `Here are the areas where you could strengthen your profile:\n\n${analysis?.development.map(d => `• ${d}`).join('\n\n')}\n\nThese improvements would increase your competitiveness for this role.`;
    } else if (lowerMessage.includes('recommend') || lowerMessage.includes('advice') || lowerMessage.includes('suggest')) {
      return `My recommendations for your application:\n\n${analysis?.recommendations.map(r => `• ${r}`).join('\n\n')}\n\nWould you like me to elaborate on any of these points?`;
    } else if (lowerMessage.includes('score') || lowerMessage.includes('match')) {
      return `Your match score is **87%**, which is quite strong! This means:\n\n• You meet or exceed most of the core requirements\n• Your experience level aligns well with what they're seeking\n• There are a few areas for improvement, but nothing that would disqualify you\n\nYou should feel confident applying to this position.`;
    } else if (lowerMessage.includes('cv') || lowerMessage.includes('resume') || lowerMessage.includes('tailor')) {
      return `To tailor your CV for these positions, I recommend:\n\n1. **Reorder your skills section** to put the most relevant technologies first (React, Node.js, TypeScript)\n2. **Add quantifiable achievements** to your experience section\n3. **Create a custom summary** that mirrors the job description language\n4. **Highlight mobile development** experience prominently\n\nWould you like me to help you draft any specific section?`;
    } else {
      return `I'm here to help you understand the analysis and prepare your application. You can ask me about:\n\n• Your **strengths** for this position\n• **Areas to improve**\n• **Recommendations** for your CV\n• Your **match score**\n• How to **tailor your application**\n\nWhat would you like to know more about?`;
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
            jobUrls={jobUrls}
            onAddJobUrl={handleAddJobUrl}
            onRemoveJobUrl={handleRemoveJobUrl}
            onAnalyze={handleAnalyze}
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
                disabled={isLoading}
              />
            )}

            {showResults && analysisData && <Results data={analysisData} />}
          </main>
        </div>
      </div>

      <LoadingScreen isActive={isLoading} />
    </div>
  );
}

export default App;
