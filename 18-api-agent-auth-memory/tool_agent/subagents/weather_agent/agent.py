from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
import requests
import asyncio
from typing import Dict,Any,Optional
import itertools
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Get current weather for a supported city using Open-Meteo API."""

    city_coords = {
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "chennai": (13.0827, 80.2707)
    }

    coords = city_coords.get(city.lower())
    if not coords:
        return {
            "status": "error",
            "message": f"City '{city}' not supported. Choose from {', '.join(city_coords)}."
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
        weather = data.get("current_weather", {})

        return {
            "city": city.title(),
            "temperature": weather.get("temperature"),
            "windspeed": weather.get("windspeed"),
            "weather_code": weather.get("weathercode"),
            "timestamp": weather.get("time"),
            "message": f"The weather in {city.title()} is {weather.get('temperature')}°C with windspeed {weather.get('windspeed')} km/h."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch weather: {e}"
        }

# Wrap the function as a FunctionTool
weather_tool = FunctionTool(func=get_weather)



def get_tasks(tool_context: ToolContext) -> dict:
    """
    Authenticates with Firebase and calls a protected /tasks/ API.
    Caches the ID token in tool_context.state.
    """

    # 🔁 Replace with real values or environment variables
    email = "prajeshkollath@gmail.com"
    password = "Welcome@121"
    api_key = "AIzaSyBeI5LCY_lqAXxk_frwkqc1pEdrQAtA0C8"

    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    tasks_url = "https://fastapi-practise-720678319427.asia-south1.run.app/tasks/"
    TOKEN_CACHE_KEY = "firebase_id_token"

    # ✅ Step 1: Check if cached token exists
    token = tool_context.state.get(TOKEN_CACHE_KEY)

    if not token:
        try:
            auth_payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            auth_response = requests.post(auth_url, json=auth_payload)
            auth_response.raise_for_status()

            token = auth_response.json().get("idToken")
            if not token:
                return {"status": "error", "message": "Auth succeeded but no token returned."}

            # ✅ Step 2: Cache token in state
            tool_context.state[TOKEN_CACHE_KEY] = token

        except Exception as e:
            return {"status": "error", "message": f"Authentication failed: {e}"}

    # ✅ Step 3: Call protected API with bearer token
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(tasks_url, headers=headers)
        response.raise_for_status()

        return {
            "status": "success",
            "tasks": response.json()
        }

    except Exception as e:
        return {"status": "error", "message": f"API call failed: {e}"}
    

tasks_tool = FunctionTool(func=get_tasks)



# Helper function to set up Google Calendar service account credentials in session state
def setup_calendar_credentials(tool_context: ToolContext, service_account_json: str) -> dict:
    """Set up Google Calendar service account credentials in session state for Cloud Run deployment."""
    import json
    import base64
    
    SERVICE_ACCOUNT_KEY = "google_calendar_service_account"
    
    try:
        # Parse the service account JSON
        service_account_dict = json.loads(service_account_json)
        
        # Validate that it's a service account key
        if 'type' not in service_account_dict or service_account_dict['type'] != 'service_account':
            return {
                "status": "error",
                "message": "Invalid service account JSON. Please provide a valid service account key file content."
            }
        
        # Encode and store in session state
        service_account_data = base64.b64encode(json.dumps(service_account_dict).encode('utf-8')).decode('utf-8')
        tool_context.state[SERVICE_ACCOUNT_KEY] = service_account_data
        
        return {
            "status": "success",
            "message": "Google Calendar service account credentials configured in session state"
        }
        
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid JSON format. Please provide valid service account JSON."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set up service account credentials: {str(e)}"
        }

def setup_user_oauth2_credentials(tool_context: ToolContext, user_email: str, access_token: str, refresh_token: str = "") -> dict:
    """Set up OAuth2 credentials for a specific user to access their own calendar."""
    import json
    import base64
    
    USER_OAUTH2_KEY = f"user_oauth2_{user_email}"
    
    try:
        oauth2_data = {
            "user_email": user_email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Encode and store in session state
        oauth2_encoded = base64.b64encode(json.dumps(oauth2_data).encode('utf-8')).decode('utf-8')
        tool_context.state[USER_OAUTH2_KEY] = oauth2_encoded
        
        return {
            "status": "success",
            "message": f"OAuth2 credentials configured for user {user_email}",
            "user_email": user_email
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set up OAuth2 credentials: {str(e)}"
        }

def get_oauth2_auth_url(tool_context: ToolContext, user_email: str) -> dict:
    """Generate OAuth2 authorization URL for a user to authenticate with Google Calendar."""
    
    # OAuth2 configuration for Google Calendar
    CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("GOOGLE_OAUTH2_REDIRECT_URI", "https://tool-agent-service-720678319427.asia-south1.run.app/")
    
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly"
    ]
    
    try:
        from urllib.parse import urlencode
        import secrets
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state in session for verification
        tool_context.state[f"oauth_state_{user_email}"] = state
        
        # Build authorization URL
        auth_params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": " ".join(SCOPES),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"
        
        return {
            "status": "success",
            "auth_url": auth_url,
            "user_email": user_email,
            "message": f"Please visit this URL to authorize access to {user_email}'s calendar"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate OAuth2 URL: {str(e)}"
        }

def handle_oauth2_callback(tool_context: ToolContext, user_email: str, auth_code: str, state: str) -> dict:
    """Handle OAuth2 callback and exchange authorization code for access token."""
    
    CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("GOOGLE_OAUTH2_REDIRECT_URI", "https://tool-agent-service-720678319427.asia-south1.run.app/")
    
    try:
        # Verify state parameter
        stored_state = tool_context.state.get(f"oauth_state_{user_email}")
        if not stored_state or stored_state != state:
            return {
                "status": "error",
                "message": "Invalid state parameter. OAuth2 flow may have been tampered with."
            }
        
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }
        
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            return {
                "status": "error",
                "message": "No access token received from Google"
            }
        
        # Store OAuth2 credentials
        result = setup_user_oauth2_credentials(tool_context, user_email, access_token, refresh_token)
        
        # Clean up state by setting to None
        tool_context.state[f"oauth_state_{user_email}"] = ""
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to handle OAuth2 callback: {str(e)}"
        }

def get_user_calendar_events(tool_context: ToolContext, user_email: str) -> dict:
    """Get calendar events for a specific user using their OAuth2 credentials."""
    import json
    import base64
    from googleapiclient.discovery import build
    
    USER_OAUTH2_KEY = f"user_oauth2_{user_email}"
    
    try:
        # Check if we have OAuth2 credentials for this user
        oauth2_data = tool_context.state.get(USER_OAUTH2_KEY)
        if not oauth2_data:
            return {
                "status": "error",
                "message": f"No OAuth2 credentials found for {user_email}. Please authenticate first.",
                "needs_auth": True,
                "user_email": user_email
            }
        
        # Decode OAuth2 credentials
        oauth2_dict = json.loads(base64.b64decode(oauth2_data).decode('utf-8'))
        access_token = oauth2_dict.get('access_token')
        
        if not access_token:
            return {
                "status": "error",
                "message": f"No access token found for {user_email}. Please re-authenticate.",
                "needs_auth": True,
                "user_email": user_email
            }
        
        # Create credentials from access token
        from google.oauth2.credentials import Credentials
        
        CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
        CLIENT_SECRET = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
        
        credentials = Credentials(
            token=access_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get calendar events
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {
                "status": "success",
                "message": f"No upcoming events found for {user_email}",
                "events": [],
                "user_email": user_email
            }
        
        # Format events
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                "summary": event.get('summary', 'No title'),
                "start": start,
                "description": event.get('description', 'No description'),
                "location": event.get('location', 'No location')
            })
        
        return {
            "status": "success",
            "message": f"Found {len(formatted_events)} upcoming events for {user_email}",
            "events": formatted_events,
            "user_email": user_email
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch calendar events for {user_email}: {str(e)}",
            "user_email": user_email
        }

def debug_calendar_access(tool_context: ToolContext) -> dict:
    """Debug function to help troubleshoot calendar access issues."""
    import json
    import base64
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    # Session state keys for storing service account data
    SERVICE_ACCOUNT_KEY = "google_calendar_service_account"
    
    try:
        # Check if we have service account credentials in session state
        service_account_data = tool_context.state.get(SERVICE_ACCOUNT_KEY)
        if not service_account_data:
            return {
                "status": "error",
                "message": "Service account credentials not configured.",
                "debug_info": {}
            }
        
        # Decode service account credentials from session state
        service_account_dict = json.loads(base64.b64decode(service_account_data).decode('utf-8'))
        
        # Create credentials from service account
        credentials = service_account.Credentials.from_service_account_info(
            service_account_dict,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get service account info
        service_account_email = service_account_dict.get('client_email', 'Unknown')
        
        # Try to get calendar list
        try:
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list calendars: {str(e)}",
                "debug_info": {
                    "service_account_email": service_account_email,
                    "error": str(e)
                }
            }
        
        # Try to access primary calendar directly
        try:
            primary_calendar = service.calendars().get(calendarId='primary').execute()
            primary_access = "Success"
        except Exception as e:
            primary_access = f"Failed: {str(e)}"
        
        # Try to access user's calendar by email
        user_calendar_id = f"{service_account_email}"
        try:
            user_calendar = service.calendars().get(calendarId=user_calendar_id).execute()
            user_calendar_access = "Success"
        except Exception as e:
            user_calendar_access = f"Failed: {str(e)}"
        
        return {
            "status": "success",
            "message": "Calendar access debug information",
            "debug_info": {
                "service_account_email": service_account_email,
                "calendars_found": len(calendars),
                "primary_calendar_access": primary_access,
                "user_calendar_access": user_calendar_access,
                "available_calendars": [
                    {
                        "id": cal.get('id'),
                        "summary": cal.get('summary', 'No name'),
                        "access_role": cal.get('accessRole', 'unknown'),
                        "primary": cal.get('primary', False)
                    } for cal in calendars
                ]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Debug failed: {str(e)}",
            "debug_info": {}
        }

# Step 1: Create calendar functions
def get_calendar_events(tool_context: ToolContext) -> dict:
    """Get calendar events using Google Calendar API with service account credentials stored in session state."""
    import json
    import base64
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    # Session state keys for storing service account data
    SERVICE_ACCOUNT_KEY = "google_calendar_service_account"
    
    try:
        # Check if we have service account credentials in session state
        service_account_data = tool_context.state.get(SERVICE_ACCOUNT_KEY)
        if not service_account_data:
            return {
                "status": "error",
                "message": "Service account credentials not configured. Please set up Google Calendar service account credentials.",
                "events": [],
                "setup_required": True
            }
        
        # Decode service account credentials from session state
        service_account_dict = json.loads(base64.b64decode(service_account_data).decode('utf-8'))
        
        # Create credentials from service account
        credentials = service_account.Credentials.from_service_account_info(
            service_account_dict,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get service account email
        service_account_email = service_account_dict.get('client_email', 'Unknown')
        
        # First, let's see what calendars are available
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        # Try different calendar IDs - prioritize user's personal calendar
        calendar_ids_to_try = [
            'prajeshkollath@gmail.com',  # Your personal calendar (PRIORITY)
            'primary',  # Primary calendar
            service_account_email,  # Service account's own calendar (last resort)
        ]
        
        calendar_id = None
        calendar_name = None
        calendar_access_method = None
        
        # If we have calendars in the list, use the first one
        if calendars:
            calendar_id = calendars[0].get('id')
            calendar_name = calendars[0].get('summary', 'Unknown Calendar')
            calendar_access_method = "calendar_list"
        else:
            # Try to access calendars directly - prioritize user's calendar
            for test_calendar_id in calendar_ids_to_try:
                try:
                    calendar_info = service.calendars().get(calendarId=test_calendar_id).execute()
                    calendar_id = test_calendar_id
                    calendar_name = calendar_info.get('summary', test_calendar_id)
                    calendar_access_method = f"direct_access_{test_calendar_id}"
                    print(f"Successfully accessed calendar: {test_calendar_id} - {calendar_name}")
                    break
                except Exception as e:
                    print(f"Failed to access calendar {test_calendar_id}: {str(e)}")
                    continue
        
        if not calendar_id:
            return {
                "status": "error",
                "message": "No accessible calendars found. Please check calendar sharing settings.",
                "events": [],
                "available_calendars": [],
                "debug_info": {
                    "service_account_email": service_account_email,
                    "calendars_in_list": len(calendars),
                    "tried_calendar_ids": calendar_ids_to_try
                }
            }
        
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {
                "status": "success",
                "message": f"No upcoming events found in '{calendar_name}' (ID: {calendar_id}).",
                "events": [],
                "calendar_accessed": calendar_name,
                "calendar_id": calendar_id,
                "available_calendars": [cal.get('summary', cal.get('id')) for cal in calendars[:5]]
            }
        
        # Format events for response
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                "summary": event.get('summary', 'No title'),
                "start": start,
                "description": event.get('description', 'No description'),
                "location": event.get('location', 'No location')
            })
        
        return {
            "status": "success",
            "message": f"Found {len(formatted_events)} upcoming events in '{calendar_name}'",
            "events": formatted_events,
            "calendar_accessed": calendar_name,
            "calendar_id": calendar_id,
            "available_calendars": [cal.get('summary', cal.get('id')) for cal in calendars[:5]],
            "access_method": calendar_access_method
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch calendar events: {str(e)}",
            "events": []
        }

def list_calendars(tool_context: ToolContext) -> dict:
    """List all available calendars for the service account."""
    import json
    import base64
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    # Session state keys for storing service account data
    SERVICE_ACCOUNT_KEY = "google_calendar_service_account"
    
    try:
        # Check if we have service account credentials in session state
        service_account_data = tool_context.state.get(SERVICE_ACCOUNT_KEY)
        if not service_account_data:
            return {
                "status": "error",
                "message": "Service account credentials not configured. Please set up Google Calendar service account credentials first.",
                "calendars": []
            }
        
        # Decode service account credentials from session state
        service_account_dict = json.loads(base64.b64decode(service_account_data).decode('utf-8'))
        
        # Create credentials from service account
        credentials = service_account.Credentials.from_service_account_info(
            service_account_dict,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            return {
                "status": "info",
                "message": "No calendars found. The service account needs access to calendars.",
                "calendars": []
            }
        
        # Format calendar information
        formatted_calendars = []
        for cal in calendars:
            formatted_calendars.append({
                "id": cal.get('id'),
                "summary": cal.get('summary', 'No name'),
                "description": cal.get('description', 'No description'),
                "primary": cal.get('primary', False),
                "access_role": cal.get('accessRole', 'unknown')
            })
        
        return {
            "status": "success",
            "message": f"Found {len(formatted_calendars)} available calendars",
            "calendars": formatted_calendars
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list calendars: {str(e)}",
            "calendars": []
        }

# Step 2: Create the calendar tools
calendar_tool = FunctionTool(func=get_calendar_events)
list_calendars_tool = FunctionTool(func=list_calendars)
debug_calendar_tool = FunctionTool(func=debug_calendar_access)
setup_credentials_tool = FunctionTool(func=setup_calendar_credentials)

# OAuth2 tools for user-specific calendar access
oauth2_auth_url_tool = FunctionTool(func=get_oauth2_auth_url)
oauth2_callback_tool = FunctionTool(func=handle_oauth2_callback)
user_calendar_tool = FunctionTool(func=get_user_calendar_events)

print ("Calendar tools created")

# Step 3: Define the agent with all tools
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Agent that retrieves Google Calendar events using both service account and OAuth2 authentication. Supports both admin calendar access and user-specific calendar access.",
    instruction="You can use this to fetch tasks, weather, and calendar events. For admin calendar access, use the service account setup. For user-specific calendar access, use OAuth2 authentication. Users can authenticate with their own Google accounts to access their personal calendars.",
    tools=[
        calendar_tool, 
        list_calendars_tool, 
        debug_calendar_tool, 
        setup_credentials_tool,
        oauth2_auth_url_tool,
        oauth2_callback_tool,
        user_calendar_tool,
        tasks_tool, 
        weather_tool
    ],
    output_key="calendar_events",
)