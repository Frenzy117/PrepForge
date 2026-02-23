# PrepForge - AI Career Assistant

An intelligent career assistant that analyzes your resume against job postings, identifies opportunities, and guides you toward your next career milestone with clarity and precision.

## Features

### Core Functionality
- **Resume Parser Agent**: Extracts structured information from CVs in multiple formats (PDF, DOCX, DOC)
- **Job Analyzer Agent**: Scrapes and structures job posting requirements
- **Strategy Advisor Agent**: Provides semantic matching, gap analysis, and career guidance

### New Features
- **🆕 Multi-URL Support**: Add and analyze multiple job postings simultaneously
- **🆕 Interactive Chat**: Conversational interface with markdown support for asking questions about your analysis
- **Beautiful Japandi UI**: Minimalist design with terracotta accents
- **Responsive Layout**: Works seamlessly on desktop and mobile devices

## Tech Stack

- React 18
- react-markdown for rich text rendering
- CSS3 with CSS Variables
- Component-based architecture
- Modern JavaScript (ES6+)

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository or extract the project files

2. Navigate to the project directory:
```bash
cd prepforge-react
```

3. Install dependencies:
```bash
npm install
```

4. Start the development server:
```bash
npm start
```

5. Open [http://localhost:3000](http://localhost:3000) to view it in your browser

## Usage

### Analyzing Multiple Jobs

1. **Upload Resume**: Click the upload area to select your CV (PDF, DOCX, or DOC)
2. **Add Job URLs**: Enter job posting URLs one at a time and click "Add"
   - You can add multiple URLs
   - Remove any URL by clicking the × button
3. **Begin Analysis**: Click "Begin Analysis" to process all jobs
4. **View Results**: See metrics and detailed analysis for all positions
5. **Chat**: Ask questions about the analysis, request CV improvements, or get strategic advice

### Chat Examples

Ask questions like:
- "What are my key strengths for these positions?"
- "How can I improve my CV?"
- "What skills should I focus on developing?"
- "How should I tailor my application?"
- "Tell me more about the match score"

## Project Structure

```
prepforge-react/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js & .css
│   │   ├── Hero.js & .css
│   │   ├── Sidebar.js & .css (Multi-URL support)
│   │   ├── AgentsGrid.js & .css
│   │   ├── AgentCard.js & .css
│   │   ├── ChatInterface.js & .css (NEW)
│   │   ├── Results.js & .css
│   │   └── LoadingScreen.js & .css
│   ├── App.js (Enhanced with chat & multi-URL)
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
├── .gitignore
└── README.md
```

## Backend Integration

To connect this frontend to your Python backend:

### 1. API Endpoints

Create these endpoints in your backend:

```python
# Resume upload and parsing
POST /api/resume
- Input: multipart/form-data with resume file
- Output: { "resume_id": "...", "extracted_data": {...} }

# Job URLs batch analysis
POST /api/analyze
- Input: {
    "resume_id": "...",
    "job_urls": ["url1", "url2", ...]
  }
- Output: {
    "metrics": [...],
    "strengths": [...],
    "recommendations": [...],
    "development": [...]
  }

# Chat endpoint
POST /api/chat
- Input: {
    "resume_id": "...",
    "job_urls": [...],
    "message": "user question",
    "history": [previous messages]
  }
- Output: { "response": "AI response in markdown" }
```

### 2. Update App.js

Replace the mock API calls:

```javascript
// In handleAnalyze function
const formData = new FormData();
formData.append('resume', resumeFile);
formData.append('job_urls', JSON.stringify(jobUrls));

const response = await fetch('http://your-backend/api/analyze', {
  method: 'POST',
  body: formData,
});

const data = await response.json();
setAnalysisData(data);

// In handleSendMessage function
const response = await fetch('http://your-backend/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    resume_id: resumeId,
    job_urls: jobUrls,
    message: message,
    history: messages
  })
});

const data = await response.json();
return data.response;
```

### 3. Connect to Your LangGraph Agents

Your Python backend should:
1. Use the `extract_resume_text` tool to parse the uploaded CV
2. Call `get_job_summary` for each job URL in parallel
3. Use the main agent with `systemInstructionTemplate` to analyze and generate responses
4. Return structured data for the frontend

Example integration:

```python
from your_agents import extract_resume_text, get_job_summary, react_graph

@app.post("/api/analyze")
async def analyze(resume: UploadFile, job_urls: List[str]):
    # Parse resume
    resume_text = extract_resume_text(resume.filename)
    
    # Fetch all job postings
    job_summaries = await asyncio.gather(*[
        get_job_summary(url) for url in job_urls
    ])
    
    # Run analysis through LangGraph
    result = react_graph.invoke({
        "messages": [
            HumanMessage(content=f"""
                Analyze this resume against these {len(job_urls)} jobs:
                
                RESUME: {resume_text}
                
                JOBS: {job_summaries}
                
                Provide: metrics, strengths, recommendations, development areas
            """)
        ]
    })
    
    return parse_agent_response(result)
```

## Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000)

### `npm run build`
Builds the app for production to the `build` folder

### `npm test`
Launches the test runner

## Design Philosophy

PrepForge follows a **Japandi aesthetic** (Japanese + Scandinavian minimalism):
- Clean, breathing layouts with generous whitespace
- Natural, earthy color palette (Ink, Terracotta, Paper)
- Subtle interactions that feel tactile and intentional
- Typography balance with Crimson Pro and Work Sans
- Conversational UI that feels human and approachable

## Customization

### Colors

Edit CSS variables in `src/index.css`:

```css
:root {
  --ink: #2C2C2C;
  --terracotta: #C85A3C;
  --paper: #F5F3EE;
  --stone: #E8E4DC;
  /* ... */
}
```

### Agent Data

Edit `src/components/AgentsGrid.js` to modify agent descriptions

### Chat Responses

Edit the `generateResponse` function in `src/App.js` to customize AI responses

## License

This project is private and proprietary.

## Support

For issues or questions, please contact the development team.
