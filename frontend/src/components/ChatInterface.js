import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

function ChatInterface({ messages, onSendMessage, disabled }) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e) => {
    setInputValue(e.target.value);
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
  };

  return (
    <div className="chat-interface">
      <div className="divider"></div>
      
      <div className="chat-header">
        <h3 className="chat-title">Conversation</h3>
        <p className="chat-subtitle">Ask questions about your analysis</p>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`chat-message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <ReactMarkdown
                components={{
                  p: ({node, ...props}) => <p className="markdown-paragraph" {...props} />,
                  strong: ({node, ...props}) => <strong className="markdown-strong" {...props} />,
                  ul: ({node, ...props}) => <ul className="markdown-list" {...props} />,
                  ol: ({node, ...props}) => <ol className="markdown-list" {...props} />,
                  li: ({node, ...props}) => <li className="markdown-list-item" {...props} />,
                  code: ({node, inline, ...props}) => 
                    inline ? 
                      <code className="markdown-inline-code" {...props} /> : 
                      <code className="markdown-code-block" {...props} />
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your analysis, get recommendations, or request help tailoring your CV..."
            disabled={disabled}
            rows={1}
          />
          <button 
            type="submit" 
            disabled={disabled || !inputValue.trim()}
            className="send-button"
          >
            <span className="send-icon">→</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
