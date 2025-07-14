# API Agent with Authentication and Memory

This example demonstrates an agent that can access external APIs with authentication and maintain persistent memory across sessions using Supabase.

## Features

- **Weather Information**: Get current weather for supported cities
- **Task Management**: Authenticate with Firebase and fetch tasks
- **Google Calendar Integration**: Access calendar events using both service account and OAuth2 authentication
- **Persistent Memory**: Session state backed by Supabase for credential storage
- **Multi-User Support**: OAuth2 authentication for user-specific calendar access

## Authentication Methods

### 1. Service Account (Admin Access)
- Used for accessing admin/shared calendars
- Credentials stored securely in session state
- No user interaction required

### 2. OAuth2 (User-Specific Access)
- Users authenticate with their own Google accounts
- Access to personal calendars
- Secure token storage in session state

## Setup Instructions

### 1. Environment Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
GOOGLE_API_KEY=your_google_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 2. Google Cloud Setup

#### For Service Account (Admin Access):
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create a service account with Calendar API Admin role
5. Download the JSON key file
6. Share your calendar with the service account email

#### For OAuth2 (User Access):
1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Create OAuth 2.0 Client ID
3. Set authorized redirect URIs (e.g., `https://your-app-domain.com/oauth/callback`)
4. Note down Client ID and Client Secret

### 3. Update OAuth2 Configuration

Edit the agent file (`tool_agent/subagents/weather_agent/agent.py`) and replace:
- `YOUR_GOOGLE_CLIENT_ID` with your actual OAuth2 Client ID
- `YOUR_GOOGLE_CLIENT_SECRET` with your actual OAuth2 Client Secret
- `https://your-app-domain.com/oauth/callback` with your actual redirect URI

## Usage

### Running the Agent

1. Start the development server:
```bash
adk web
```

2. Access the web UI at `http://localhost:8000`

### Service Account Setup

To set up service account credentials:
```
Please set up Google Calendar service account credentials. Send me the JSON content of your service account key file.
```

### OAuth2 User Authentication

For user-specific calendar access:

1. **Generate Auth URL**:
```
Generate OAuth2 authorization URL for user@example.com
```

2. **User visits the URL** and authorizes access

3. **Handle callback** with the authorization code

4. **Access user's calendar**:
```
Get calendar events for user@example.com
```

## API Endpoints

### Calendar Events
- `get_calendar_events()`: Get events using service account
- `get_user_calendar_events(user_email)`: Get events for specific user
- `list_calendars()`: List available calendars
- `debug_calendar_access()`: Debug calendar access issues

### OAuth2 Authentication
- `get_oauth2_auth_url(user_email)`: Generate authorization URL
- `handle_oauth2_callback(user_email, auth_code, state)`: Handle OAuth2 callback
- `setup_user_oauth2_credentials(user_email, access_token, refresh_token)`: Store user credentials

### Other Tools
- `get_weather(city)`: Get weather information
- `get_tasks()`: Fetch tasks from Firebase API

## Security Considerations

1. **Service Account Keys**: Store securely, never commit to version control
2. **OAuth2 Tokens**: Encoded and stored in session state
3. **State Parameter**: Used to prevent CSRF attacks
4. **HTTPS**: Required for OAuth2 redirect URIs in production

## Deployment

### Cloud Run Deployment

1. Build and deploy:
```bash
gcloud run deploy your-app-name --source .
```

2. Set environment variables in Cloud Run:
```bash
gcloud run services update your-app-name --set-env-vars GOOGLE_API_KEY=your_key,SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

3. Update OAuth2 redirect URI to your Cloud Run URL

### Frontend Integration

For production use, you'll need a frontend that:
1. Initiates OAuth2 flow
2. Handles the callback
3. Sends tokens to your agent
4. Provides chat interface

## Troubleshooting

### Calendar Access Issues
- Use `debug_calendar_access()` to diagnose problems
- Check calendar sharing settings
- Verify service account permissions

### OAuth2 Issues
- Ensure redirect URI matches exactly
- Check client ID and secret
- Verify scopes are correct

## Example Conversations

### Service Account Setup
```
User: Set up Google Calendar access
Agent: I'll help you set up Google Calendar access. Please provide your service account JSON key file content.

User: {"type": "service_account", "project_id": "...", ...}
Agent: Service account credentials configured successfully. You can now access your calendar events.
```

### OAuth2 User Authentication
```
User: I want to access my calendar events
Agent: I'll help you access your calendar. What's your email address?

User: user@example.com
Agent: I'll generate an authorization URL for you. Please visit this URL to authorize access to your calendar: https://accounts.google.com/o/oauth2/v2/auth?...

User: I've authorized access. Here's the callback: https://your-app.com/oauth/callback?code=...&state=...
Agent: Authentication successful! I can now access your calendar events. Let me fetch them for you.
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Frontend │    │   ADK Agent      │    │   Google APIs   │
│                 │    │                  │    │                 │
│ - Chat UI       │◄──►│ - OAuth2 Tools   │◄──►│ - Calendar API  │
│ - OAuth2 Flow   │    │ - Service Account│    │ - Weather API   │
│ - Token Storage │    │ - Session State  │    │ - Firebase API  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Supabase       │
                       │                  │
                       │ - Session State  │
                       │ - Credentials    │
                       └──────────────────┘
```

## Next Steps

1. **Frontend Development**: Create a web UI for user interaction
2. **Token Refresh**: Implement automatic token refresh for OAuth2
3. **Multi-Tenant**: Support multiple users with separate session states
4. **Calendar Management**: Add create/update/delete calendar events
5. **Notifications**: Implement calendar event notifications