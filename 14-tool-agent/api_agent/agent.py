from google.adk.agents import Agent
from google.adk.tools import google_search
import requests

# def get_current_time() -> dict:
#     """
#     Get the current time in the format YYYY-MM-DD HH:MM:SS
#     """
#     return {
#         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }


def check_api_status():
    url = "https://fastapi-practise-720678319427.asia-south1.run.app/tasks/histogram"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ API is working (200 OK)")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    

root_agent = Agent(
    name="api_agent",
    model="gemini-2.0-flash",
    description="API status check agent",
    instruction="""
    You are a helpful assistant that can check the API status and confirm if the API is working
    """,
    tools=[check_api_status],
    # tools=[get_current_time],
    # tools=[google_search, get_current_time], # <--- Doesn't work
)


