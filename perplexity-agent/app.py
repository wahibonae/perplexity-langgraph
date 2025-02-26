import streamlit as st
import os
from dotenv import load_dotenv
from agent import PerplexityAgent

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
)

# Add header with a nicer design
st.title("Perplexity-like Agent 🔍")
st.markdown("##### Built with Gemini 2.0 and LangGraph")

# Initialize session state for storing results and tracking process
if 'results' not in st.session_state:
    st.session_state.results = []
if 'running' not in st.session_state:
    st.session_state.running = False
if 'final_answer' not in st.session_state:
    st.session_state.final_answer = None
if 'subtasks' not in st.session_state:
    st.session_state.subtasks = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# Create UI layout with a cleaner design

# Create a text input for the user query
query = st.text_input("Ask me anything:", placeholder="Enter your question here...")

# Function to reset all results
def reset_results():
    st.session_state.results = []
    st.session_state.subtasks = []
    st.session_state.final_answer = None
    st.session_state.running = False

# Handle query submission when the query changes
if query != st.session_state.current_query and query:
    reset_results()
    st.session_state.current_query = query

# Add a dedicated "Send" button to control when the query is processed
send_button = st.button("Send Query", type="primary", disabled=st.session_state.running or not query)

# Initialize the agent
@st.cache_resource
def get_agent():
    return PerplexityAgent()

agent = get_agent()

# Main content area - use containers to better control UI updates
main_container = st.container()

with main_container:
    # Display final answer if available
    if st.session_state.final_answer:
        col1, col2 = st.columns([1, 1])
        
        with col2:
            # Display the final answer
            st.markdown("## Answer")
            st.markdown(st.session_state.final_answer)
        
        with col1:
            # Show the research details
            st.markdown("## Research Details")
            
            # Display subtasks
            st.markdown("### Subtasks")
            for i, task in enumerate(st.session_state.subtasks, 1):
                st.markdown(f"**Task {i}:** {task}")
            
            # Display results for each task
            st.markdown("### Task Results")
            for i, (t, r) in enumerate(st.session_state.results, 1):
                st.expander(f"Task {i}: {t}", expanded=False).markdown(r)

    # When the user clicks the Send button
    elif send_button and query and not st.session_state.running:
        # Mark as running to prevent multiple executions
        st.session_state.running = True
        
        # Create a 2-column layout for better organization
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create a container for the research with a better visual
            st.subheader("Research")
            status = st.empty()
            status.info("⏳ Analyzing your question...")
            
            # Create a container for subtasks
            st.markdown("### Subtasks")
            subtasks_placeholder = st.empty()
            
            # Create container for research results
            st.markdown("### Task Results")
            results_container = st.container()
        
        with col2:
            # Create a container for the final answer (prioritized)
            st.subheader("Answer")
            final_answer_placeholder = st.empty()
        
        # Define callback functions to update the UI in real-time
        def on_decompose_start():
            status.info("🔍 Breaking down your question into subtasks...")
        
        def on_subtasks(subtasks):
            # Store subtasks in session state
            st.session_state.subtasks = subtasks
            
            status.success("✅ Question broken down into subtasks")
            # Create a bulleted list of subtasks
            subtasks_markdown = ""
            for i, task in enumerate(subtasks, 1):
                subtasks_markdown += f"**Task {i}:** {task}\n\n"
            subtasks_placeholder.markdown(subtasks_markdown)
        
        def on_task_start(task):
            status.info(f"🔄 Researching: **{task}**")
        
        def on_task_complete(task, result):
            # Add the new result to session state
            st.session_state.results.append((task, result))
            
            # Get current task index (1-based)
            task_index = len(st.session_state.results)
                    
            # Display the new result in the results container
            with results_container:
                # Create a new expander (not nested) for this task result
                expander = st.expander(f"Task {task_index}: {task}", expanded=True)
                expander.markdown(result)
        
        def on_synthesize_start():
            status.info("🔄 Synthesizing final answer...")
            final_answer_placeholder.info("Creating your answer...")
        
        def on_answer_complete(answer):
            status.success("✅ Answer generated")
            # Store the final answer in session state
            st.session_state.final_answer = answer
            # Display the final answer with markdown
            final_answer_placeholder.markdown(answer)
            # Reset the running flag when complete
            st.session_state.running = False
        
        # Prepare callbacks dictionary
        callbacks = {
            "on_decompose_start": on_decompose_start,
            "on_subtasks": on_subtasks,
            "on_task_start": on_task_start,
            "on_task_complete": on_task_complete,
            "on_synthesize_start": on_synthesize_start,
            "on_answer_complete": on_answer_complete
        }
        
        # Process the query with our agent
        try:
            # Run the agent with the callbacks
            agent.run(query=query, callbacks=callbacks)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Reset the running flag on error
            st.session_state.running = False

# Add a "New Search" button to allow users to clear results and start fresh
if st.session_state.final_answer:
    if st.button("New Search", type="primary"):
        reset_results()
        st.experimental_rerun()

st.caption("Created by Mohamed Wahib ABKARI | GDGOnCampus EMSI Casablanca") 