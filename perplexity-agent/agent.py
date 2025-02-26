import os
import json
from typing import Dict, List, Optional, TypedDict, Callable
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langgraph.graph import END, StateGraph, START

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.environ.get("GOOGLE_API_KEY")
# Initialize the client
genai_client = genai.Client(api_key=api_key)

# Define the typed state for our agent
class AgentState(TypedDict):
    query: str  # The user's query
    subtasks: Optional[List[str]]  # The list of subtasks to complete
    results: Dict[str, str]  # The results of each subtask
    current_subtask: Optional[str]  # The subtask currently being processed
    final_answer: Optional[str]  # The final answer to the user's query
    callbacks: Optional[Dict[str, Callable]]  # Callbacks for UI updates


def get_model_config():
    """Get a model configuration with search enabled."""
    # Model configuration
    model_id = "gemini-2.0-pro-exp-02-05"
    
    # Define generation config
    generate_config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=8192,
        tools=[
            types.Tool(google_search=types.GoogleSearch())
        ],
        system_instruction="""
        You are an AI assistant that can search the web for information.
        When asked questions about recent events, facts, or topics that require up-to-date information,
        use the Google Search tool to find relevant information before responding.
        Do not include or mention your sources in your responses.
        """
    )
    
    return model_id, generate_config


def decompose(state: AgentState) -> AgentState:
    """Break down the query into subtasks."""
    query = state["query"]
    callbacks = state.get("callbacks", {})
    
    if "on_decompose_start" in callbacks:
        callbacks["on_decompose_start"]()
    
    try:
        # Get model config
        model_id, generate_config = get_model_config()
        
        prompt = f"""
        Break down the following query into 1-3 simple if necessary, high-level subtasks that need to be completed to answer it effectively:
        
        Query: {query}
        
        Return a JSON array of subtask strings. Each subtask should be a clear, focused question that addresses a key aspect of the main query.
        Example format: ["subtask 1", "subtask 2", "subtask 3"]
        """
        
        # Create the content
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        
        # Generate content
        response = genai_client.models.generate_content(
            model=model_id,
            contents=contents,
            config=generate_config
        )
        
        # Parse the response
        response_text = response.candidates[0].content.parts[0].text.strip()
        
        # Extract JSON array
        start_index = response_text.find("[")
        end_index = response_text.rfind("]") + 1
        
        if start_index != -1 and end_index != -1:
            json_str = response_text[start_index:end_index]
            subtasks = json.loads(json_str)
        else:
            # Use the original query as a fallback
            subtasks = [query]
        
    except Exception:
        # Simple fallback
        subtasks = [query]
    
    # Update the state
    new_state = state.copy()
    new_state["subtasks"] = subtasks
    new_state["results"] = {}
    
    if "on_subtasks" in callbacks:
        callbacks["on_subtasks"](subtasks)
    
    return new_state


def route(state: AgentState) -> AgentState:
    """Determine the next subtask to process."""
    new_state = state.copy()
    subtasks = state.get("subtasks", [])
    results = state.get("results", {})
    
    # Find any unprocessed subtask
    for subtask in subtasks:
        if subtask not in results:
            new_state["current_subtask"] = subtask
            return new_state
    
    # No more subtasks to process
    new_state["current_subtask"] = None
    return new_state


def research(state: AgentState) -> AgentState:
    """Process the current subtask using Gemini with search."""
    new_state = state.copy()
    current_subtask = state.get("current_subtask")
    callbacks = state.get("callbacks", {})
    
    # Skip if there's no current subtask or if it's already been processed
    if not current_subtask or current_subtask in state.get("results", {}):
        new_state["current_subtask"] = None
        return new_state
    
    if "on_task_start" in callbacks:
        callbacks["on_task_start"](current_subtask)
    
    try:
        # Get model config
        model_id, generate_config = get_model_config()
        
        # Enhanced prompt that will trigger search
        prompt = f"""
        {current_subtask}
        
        Research this question thoroughly and provide a detailed, accurate answer with facts and specific information.
        Include relevant recent developments on this topic.
        """
        
        # Create the content
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        
        # Generate with search capability
        response = genai_client.models.generate_content(
            model=model_id,
            contents=contents,
            config=generate_config
        )
        
        # Get the response text
        result = response.candidates[0].content.parts[0].text.strip()
        
    except Exception:
        # Simple error message
        result = "I couldn't retrieve information for this subtask due to a technical issue."
    
    # Store the result
    results = new_state.get("results", {})
    results[current_subtask] = result
    new_state["results"] = results
    
    if "on_task_complete" in callbacks:
        callbacks["on_task_complete"](current_subtask, result)
    
    return new_state


def synthesize(state: AgentState) -> AgentState:
    """Generate the final answer based on subtask results."""
    new_state = state.copy()
    query = state["query"]
    results = state.get("results", {})
    callbacks = state.get("callbacks", {})
    
    if "on_synthesize_start" in callbacks:
        callbacks["on_synthesize_start"]()
    
    try:
        # Prepare the context from the results
        context_parts = []
        for subtask, result in results.items():
            # Limit length to keep context manageable
            truncated_result = result[:1500]
            context_parts.append(f"Context for '{subtask}':\n{truncated_result}")
        
        context = "\n\n".join(context_parts)
        
        # Get model config
        model_id, generate_config = get_model_config()
        
        # Using the user-provided prompt format
        prompt = f"""
        Given a user question and some context, please write a clean, concise and accurate answer to the question based on the context. You will be given a set of related contexts to the question. Please use the context when crafting your answer.

        Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

        Here are the set of contexts:
        {context}

        Remember, don't blindly repeat the contexts verbatim and don't tell the user how you used the citations – just respond with the answer. It is very important for my career that you follow these instructions. Here is the user question: {query}
        """
        
        # Create the content
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        
        # Generate content
        response = genai_client.models.generate_content(
            model=model_id,
            contents=contents,
            config=generate_config
        )
        
        final_answer = response.candidates[0].content.parts[0].text.strip()
        
    except Exception:
        # Simple fallback
        final_answer = f"# Answer to: {query}\n\n"
        final_answer += "Based on the information gathered:\n\n"
        
        # Add a summary of each result
        for subtask, result in results.items():
            first_paragraph = result.split("\n")[0]
            final_answer += f"- **{subtask}**: {first_paragraph}\n\n"
    
    new_state["final_answer"] = final_answer
    
    if "on_answer_complete" in callbacks:
        callbacks["on_answer_complete"](final_answer)
    
    return new_state


class PerplexityAgent:
    """A simple agent that uses Gemini to process queries."""
    
    def __init__(self):
        # Set up the workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph."""
        # Initialize the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each step
        workflow.add_node("decompose", decompose)
        workflow.add_node("route", route)
        workflow.add_node("research", research)
        workflow.add_node("synthesize", synthesize)
        
        # Define the edges
        workflow.add_edge(START, "decompose")
        workflow.add_edge("decompose", "route")
        
        # Routing logic
        workflow.add_conditional_edges(
            "route",
            lambda state: "synthesize" if state["current_subtask"] is None else "research",
            {
                "synthesize": "synthesize",
                "research": "research"
            }
        )
        
        workflow.add_edge("research", "route")
        workflow.add_edge("synthesize", END)
        
        return workflow
    
    def run(self, query: str, callbacks: Optional[Dict[str, Callable]] = None) -> str:
        """Run the agent to process a query and return the answer."""
        try:
            # Initialize the state
            state = {
                "query": query,
                "results": {},
                "callbacks": callbacks or {}
            }
            
            # Execute the workflow
            result = self.app.invoke(state)
            
            # Return the final answer
            if "final_answer" in result and result["final_answer"]:
                return result["final_answer"]
            
            return "Failed to generate an answer."
        
        except Exception as e:
            return f"Error: {str(e)}" 