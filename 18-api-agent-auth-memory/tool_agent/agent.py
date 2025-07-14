from google.adk.agents import SequentialAgent
from google.adk.agents import Agent
from .subagents.time_agent.agent import time_agent
from .subagents.summary_agent.agent import summary_agent
from .subagents.memory_agent.agent import memory_agent
from .subagents.weather_agent.agent import weather_agent



tool_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash", # not needed for sequential
    sub_agents=[time_agent,summary_agent,memory_agent,weather_agent],
    description="A workflow agent that gets time or summarizes the time",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.
    
    - Use 'time_agent' to get current time
    - Use 'summary_agent' to summarize the current time
    - Use 'memory_agent' if the user asks for their history of notes
    - Use 'weather_agent' if the user asks for the weather or temperature or tasks of the user or calendar events
    
    
    """
)

root_agent = tool_agent