# Perplexity-like Research Agent

A Perplexity-like research agent built with Gemini 2.0 and LangGraph. This application acts like perplexity.ai by breaking down a query into subtasks, researching each one using web search, and then synthesizing a comprehensive answer.

## Project Structure

This project is organized into three implementations:

- **`perplexity-agent/`**: The Streamlit implementation (easy to run and visualize the process)
  - `app.py`: The Streamlit UI for the agent
  - `agent.py`: Core agent logic using LangGraph

- **`fastapi-react/`**: The FastAPI + React implementation (production-like setup)
  - `fastapi_backend/`: Backend implementation with FastAPI
    - `fastapi_app.py`: API server that handles query processing
  - `react_frontend/`: Frontend implementation with React
    - `src/`: React source code
    - `public/`: Public assets

- **`langgraph_examples/`**: Example implementations of LangGraph concepts

## Features

- **Task Decomposition**: Breaks down complex queries into simpler subtasks
- **Web Research**: Researches each subtask using Gemini 2.0's web search capabilities
- **Answer Synthesis**: Synthesizes a final answer based on all research findings
- **Real-time Feedback**: Shows the process of research as it happens (in Streamlit version)
- **Clean UI**: Provides a clean, user-friendly interface in both implementations

## Setup

### Prerequisites

- Python 3.7+
- Node.js and npm (for the React implementation)
- Google API key with access to Gemini 2.0

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd build-with-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the Implementations

### Streamlit Implementation

The Streamlit implementation provides a simple, interactive UI that shows the research process in real-time:

```bash
cd perplexity-agent
streamlit run app.py
```

This will start the Streamlit app, which you can access at http://localhost:8501.

#### How to Use the Streamlit App

1. Enter your query in the input field
2. Click "Send Query"
3. Watch as the agent:
   - Breaks down your query into subtasks
   - Researches each subtask one by one
   - Synthesizes a final answer
4. Review the results in the expandable sections
5. Start a new search by clicking "New Search" or entering a new query

### FastAPI + React Implementation

The FastAPI + React implementation provides a more production-like setup:

1. Start the FastAPI backend:
```bash
cd fastapi-react/fastapi_backend
uvicorn fastapi_app:app --reload
```

2. In a new terminal, install the React frontend dependencies and start the server:
```bash
cd fastapi-react/react_frontend
npm install
npm start
```

This will start the React app, which you can access at http://localhost:3000.

## How It Works

The agent follows a four-step process powered by LangGraph:

1. **Decompose**: Breaks down the user query into smaller, focused subtasks
2. **Route**: Determines which subtask to process next
3. **Research**: Uses Gemini 2.0 with web search capability to research the current subtask
4. **Synthesize**: Combines all research results to generate a comprehensive final answer

## Architecture

The LangGraph-powered agent architecture provides:

- **Structured Workflow**: Clear steps for processing complex queries
- **Modular Design**: Separation of concerns between different stages of processing
- **Callback-Based UI Updates**: Real-time feedback as processing happens
- **State Management**: Tracking of subtasks, results, and progress

## Workshop Information

This project was created for the "Build with AI: Building a Perplexity Agent using Gemini 2.0 and LangGraph" workshop at EMSI Casablanca GDGOnCampus.

## Credits

Created by Mohamed Wahib ABKARI & Anass Amazzar | GDGOnCampus EMSI Casablanca 
