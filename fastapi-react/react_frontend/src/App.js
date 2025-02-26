import React, { useState } from 'react';
import './App.css';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [subtasks, setSubtasks] = useState([]);
  const [results, setResults] = useState([]);
  const [finalAnswer, setFinalAnswer] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim() || isLoading) {
      return;
    }
    
    try {
      // Reset states
      setSubtasks([]);
      setResults([]);
      setFinalAnswer('');
      setError('');
      setIsLoading(true);
      
      // Make API request
      const response = await axios.post(`${API_URL}/query`, {
        query: query
      });
      
      // Update state with response data
      setSubtasks(response.data.subtasks);
      setResults(response.data.results);
      setFinalAnswer(response.data.answer);
      
    } catch (err) {
      console.error('Error processing query:', err);
      setError(err.response?.data?.detail || 'An error occurred processing your query.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleNewSearch = () => {
    // Reset all states and allow for a new search
    setQuery('');
    setSubtasks([]);
    setResults([]);
    setFinalAnswer('');
    setError('');
    // Focus on the input field
    document.querySelector('.query-input').focus();
  };
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>Perplexity-like Agent 🔍</h1>
        <p>Built with Gemini 2.0 and LangGraph</p>
      </header>
      
      <main className="App-main">
        <form onSubmit={handleSubmit} className="query-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask me anything..."
            disabled={isLoading}
            className="query-input"
          />
          <button 
            type="submit" 
            disabled={!query.trim() || isLoading}
            className="query-button"
          >
            {isLoading ? 'Processing...' : 'Send Query'}
          </button>
        </form>
        
        {isLoading && (
          <div className="status-container">
            <p className="status-message">Processing your query. This may take a minute...</p>
            <div className="loading-spinner"></div>
          </div>
        )}
        
        {error && (
          <div className="error-container">
            <p className="error-message">{error}</p>
          </div>
        )}
        
        {finalAnswer && (
          <>
            <div className="content-container">
              <div className="column research-column">
                <h2>Research Details</h2>
                
                {subtasks.length > 0 && (
                  <div className="subtasks-container">
                    <h3>Subtasks</h3>
                    <ul>
                      {subtasks.map((task, index) => (
                        <li key={index}><strong>Task {index + 1}:</strong> {task}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {results.length > 0 && (
                  <div className="results-container">
                    <h3>Task Results</h3>
                    {results.map((result, index) => (
                      <details key={index} className="result-expander">
                        <summary><strong>Task {index + 1}:</strong> {result.task}</summary>
                        <div className="result-content">
                          <ReactMarkdown>{result.result}</ReactMarkdown>
                        </div>
                      </details>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="column answer-column">
                <h2>Answer</h2>
                <div className="answer-container">
                  <ReactMarkdown>{finalAnswer}</ReactMarkdown>
                </div>
              </div>
            </div>
            
            <div className="new-search-container">
              <button 
                onClick={handleNewSearch}
                className="new-search-button"
              >
                New Search
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App; 