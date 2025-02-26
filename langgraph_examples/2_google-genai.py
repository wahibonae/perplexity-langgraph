# 1.2_intro.py: Uses the Gemini API to generate content

from typing import Annotated
import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


load_dotenv()

# Configure the API key
api_key = os.environ.get("GOOGLE_API_KEY")
# Initialize the client
genai_client = genai.Client(api_key=api_key)

generate_config = types.GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=8192
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

model_id = "gemini-2.0-flash-thinking-exp-01-21"

def chatbot(state: State):
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="""Hello, how are you?"""
                ),
            ],
        ),
    ]

    response = []
    for chunk in genai_client.models.generate_content_stream(
        model=model_id,
        contents=contents,
        config=generate_config,
    ):
        response.append(chunk.text)

    return {"messages": ["".join(response)]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()

# Run the graph and print the result
result = graph.invoke({"messages": []})
print(result["messages"][0].content)