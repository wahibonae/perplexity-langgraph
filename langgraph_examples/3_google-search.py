# 3_google-search.py: Uses the Gemini API with Google Search capabilities

from typing import Annotated
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.environ.get("GOOGLE_API_KEY")
# Initialize the client
genai_client = genai.Client(api_key=api_key)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str


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


def search_bot(state: State):
    """Process a query using Gemini with search capability."""
    # Get model config
    model_id, generate_config = get_model_config()
    
    # Construct prompt that will trigger search
    query = state.get("query", "What are the latest developments in AI?")
    
    # Create the content
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=query
                ),
            ],
        ),
    ]

    # Generate content with search capability
    response = genai_client.models.generate_content(
        model=model_id,
        contents=contents,
        config=generate_config
    )
    
    # Get the response text
    result = response.candidates[0].content.parts[0].text.strip()
    
    return {"messages": [result]}


# Set up the graph
graph_builder = StateGraph(State)
graph_builder.add_node("search_bot", search_bot)
graph_builder.set_entry_point("search_bot")
graph_builder.set_finish_point("search_bot")
graph = graph_builder.compile()

# Run the graph with a query that will benefit from search
sample_query = "What were the major tech announcements this week?"
result = graph.invoke({"messages": [], "query": sample_query})

print(f"Query: {sample_query}")
print("\nResponse:")
print(result["messages"][0])
