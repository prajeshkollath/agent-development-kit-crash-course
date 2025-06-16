from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import google_search


def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS.
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


root_agent = Agent(
    name="tool_agent",
    description="An agent that can use tools to answer questions.",
    model="gemini-2.0-flash",
    instruction="""
    You are a helpful assistant that can use the following tools:
    - get_current_time: Get the current time.
    - google_search
    """,
    # tools=[google_search],
    tools=[get_current_time],
    # tools=[get_current_time, google_search],  <--- doesn't work (more than one tool not supported yet in ADK)
)
