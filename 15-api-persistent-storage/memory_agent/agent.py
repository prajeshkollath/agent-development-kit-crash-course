from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import requests
from datetime import datetime

def get_temperature(city: str, tool_context: ToolContext) -> dict:
    """Fetch current temperature from Open-Meteo API based on city and store in state.

    Args:
        city: The name of the city to get temperature for
        tool_context: Context for accessing and updating session state

    Returns:
        A dictionary containing the latest temperature and a message
    """
    print(f"--- Tool: get_temperature called for city '{city}' ---")

    # Simple city-to-coordinates map (extend as needed)
    city_coords = {
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "chennai": (13.0827, 80.2707)
    }

    coords = city_coords.get(city.lower())
    if not coords:
        return {
            "action": "get_temperature",
            "status": "error",
            "message": f"City '{city}' not found in supported cities."
        }

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "current_weather": "true"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        current_weather = data.get("current_weather", {})
        temperature = current_weather.get("temperature")
        timestamp = current_weather.get("time")

        if temperature is not None and timestamp:
            temperature_log = tool_context.state.get("temperature_log", [])
            temperature_log.append({
                "city": city,
                "temperature": temperature,
                "time": timestamp
            })
            tool_context.state["temperature_log"] = temperature_log

            return {
                "action": "get_temperature",
                "temperature": temperature,
                "time": timestamp,
                "city": city,
                "message": f"Current temperature in {city.title()} is {temperature} °C at {timestamp}",
            }
        else:
            return {
                "action": "get_temperature",
                "status": "error",
                "message": "Temperature or time data not found in API response."
            }

    except Exception as e:
        return {
            "action": "get_temperature",
            "status": "error",
            "message": f"API call failed: {e}"
        }

def view_temperatures(tool_context: ToolContext) -> dict:
    """View all recorded temperatures from session state.

    Args:
        tool_context: Context for accessing session state

    Returns:
        A dictionary containing all logged temperatures
    """
    print("--- Tool: view_temperatures called ---")

    temperature_log = tool_context.state.get("temperature_log", [])
    return {
        "action": "view_temperatures",
        "temperatures": temperature_log,
        "count": len(temperature_log)
    }

memory_agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    description="An agent that logs temperature requests in persistent memory",
    instruction="""
    You are a weather tracking assistant.
    Your job is to fetch and log current temperatures when asked by the user.
    Store every temperature and its corresponding time you fetch into a list so that you can show them later.

    You can:
    1. Fetch the current temperature (user provides a city name like 'Delhi')
    2. View all previously fetched temperatures

    Always greet the user politely and let them know what you’re doing.
    """,
    tools=[
        get_temperature,
        view_temperatures,
    ],
)
