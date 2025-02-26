# 1_intro.py: Uses the Langchain interface to interact with Gemini

from typing import Annotated
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


load_dotenv()

# Configure the API key
api_key = os.environ.get("GOOGLE_API_KEY")


class State(TypedDict):
    # Messages have the type "list".
    # The `add_messages` function in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Initialize the LangChain Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-thinking-exp-01-21",  # Using flash model for faster responses
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key,
)


def chatbot(state: State):
    # Get the LLM response
    response = llm.invoke(state["messages"])
    # Return the updated messages
    return {"messages": [response]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()

# Run the graph with a properly formatted message
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
result = graph.invoke({"messages": messages})

# Extract just the content from the AI message
print(result["messages"][2].content)

