# Perplexity-like Agent

A simple AI Agent built with the Gemini 2.0 API and LangGraph. This agent breaks down complex questions, researches each part using web search, and provides comprehensive answers.

## Features

- Breaks down complex questions into simpler subtasks
- Researches each subtask using Google Search
- Shows real-time progress in the Streamlit UI
- Provides a well-formatted comprehensive answer

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   Get your API key from [Google AI Studio](https://ai.google.dev/)

## Running the App

Start the Streamlit app:
```
streamlit run app.py
```

Then open your browser to at the address provided by the terminal.

## Project Structure

- `app.py` - Streamlit UI application
- `agent.py` - AI agent implementation using LangGraph
- `requirements.txt` - Project dependencies

## How It Works

1. **Question Analysis**: The agent breaks down your complex question into smaller subtasks.
   
2. **Research**: For each subtask, the agent uses Gemini with Google Search to find information.
   
3. **Synthesis**: Once done, the agent combines all the research results into a comprehensive final answer.

## Workshop Notes

This project demonstrates how to build AI agents that can break down complex tasks and use the web to find up-to-date information. The code is designed to be simple and easy to understand for beginners (hopefully).

Feel free to modify the agent's behavior or UI to experiment with different features! 