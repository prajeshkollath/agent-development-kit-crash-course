#!/usr/bin/env python3
"""
Test script for Google Calendar integration
"""

import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from tool_agent.subagents.weather_agent.agent import weather_agent

async def test_calendar_agent():
    """Test the calendar agent functionality"""
    
    print("Testing Calendar Agent...")
    print("=" * 50)
    
    # Create a runner for the agent
    runner = InMemoryRunner(weather_agent, app_name="CalendarTest")
    
    # Create a test message
    content = types.Content(
        role="user", 
        parts=[types.Part.from_text("Get my upcoming calendar events")]
    )
    
    # Test the agent
    events = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=content
    ):
        events.append(event)
        if event.content:
            print(f"Agent Response: {event.content.parts[0].text}")
    
    print("=" * 50)
    print(f"Total events generated: {len(events)}")

if __name__ == "__main__":
    asyncio.run(test_calendar_agent()) 