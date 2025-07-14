from datetime import datetime
#from copy import deepcopy
from typing import Dict, Any, Optional
from pydantic import BaseModel


from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
#from google.adk.agents import SequentialAgent
#from .subagents.summary_agent.agent import summary_agent


def get_current_time():
    return {"result": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# Wrap the function as a FunctionTool
time_tool = FunctionTool(func=get_current_time)


'''
# After-tool callback
def store_result_after_tool(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Args used: {args}")
    print(f"[Callback] Original tool_response: {tool_response}")

    result = tool_response.get("result", "")
    if tool_name == "get_current_time" and result:
        state = tool_context.state
        state["last_time_check"] = result
        print(f"[Callback] Stored time result in memory.")
        print(f"[Callback] Memory snippet: {result}")
    else:
        print("[Callback] No result stored.")

    return None
'''
# Define the agent
time_agent = Agent(
    name="time_agent",
    model="gemini-2.0-flash",
    description="Tool agent that remembers the time check result",
    instruction="You are a helpful assistant that can report the current time.",
    tools=[time_tool],
    output_key="result",
)


