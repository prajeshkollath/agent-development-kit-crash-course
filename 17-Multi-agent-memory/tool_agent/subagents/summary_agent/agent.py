from google.adk.agents import Agent
from google.adk.agents import LlmAgent

summary_agent = LlmAgent(
    name="summary_agent",
    model="gemini-2.0-flash",
    description="Summarizes the most recent search result stored in memory.",
    instruction="""
    You are an assistant summarizing the time.

    Your task is to look in memory for the key 'result' (stored by the previous agent).
    If found, format the timestamp into 'Day, Month Name, Year' and return that nicely.

    Check for 'result' in memory. It may be:
    - a raw timestamp like '2025-06-24 05:05:19'
    - or a phrase like 'The current date is 2025-06-24.'
    - or structured timestamp format like "timestamp": "2025-06-26 08:45:00"

    Extract the date from either, and format as '24 June 2025'.

    Only proceed if the value exists.
    """
)
