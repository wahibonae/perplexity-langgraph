from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

# Add parent directory to path to be able to import the agent module
perplexity_agent_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "perplexity-agent")
sys.path.append(perplexity_agent_path)
from agent import PerplexityAgent

# Initialize FastAPI app
app = FastAPI(title="Perplexity Agent API")

# Add CORS middleware to allow cross-origin requests from the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create agent instance
agent = PerplexityAgent()

# Define request model
class QueryRequest(BaseModel):
    query: str

# Define response model
class QueryResult(BaseModel):
    subtasks: List[str]
    results: List[Dict[str, str]]  # List of task and result pairs
    answer: str

# API routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Perplexity Agent API is running"}

@app.post("/query", response_model=QueryResult)
async def process_query(request: QueryRequest):
    """Process a query and return the results"""
    try:
        # Store results
        subtasks_list = []
        results_list = []
        final_answer = ""
        
        # Define callback functions to collect results
        def on_subtasks(subtasks: List[str]):
            nonlocal subtasks_list
            subtasks_list = subtasks
        
        def on_task_complete(task: str, result: str):
            results_list.append({"task": task, "result": result})
        
        def on_answer_complete(answer: str):
            nonlocal final_answer
            final_answer = answer
        
        # Create callbacks dictionary
        callbacks = {
            "on_decompose_start": lambda: None,
            "on_subtasks": on_subtasks,
            "on_task_start": lambda task: None,
            "on_task_complete": on_task_complete,
            "on_synthesize_start": lambda: None,
            "on_answer_complete": on_answer_complete
        }
        
        # Run the agent with the callbacks
        agent.run(query=request.query, callbacks=callbacks)
        
        # Return the results
        return QueryResult(
            subtasks=subtasks_list,
            results=results_list,
            answer=final_answer
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Run with: uvicorn fastapi_app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True) 