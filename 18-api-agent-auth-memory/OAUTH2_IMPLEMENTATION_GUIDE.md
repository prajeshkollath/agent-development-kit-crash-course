# OAuth2 Implementation Guide for User Calendar Access

This guide explains how to implement OAuth2 authentication for users to access their own Google Calendars through your AI agent.

## Problem Solved

**The Issue**: Service accounts require manual calendar sharing, which is not user-friendly for a multi-user application.

**The Solution**: OAuth2 allows users to authenticate with their own Google accounts and grant access to their calendars directly.

## Implementation Overview

### 1. User Flow
```
1. User provides email → Agent generates OAuth2 URL
2. User visits URL → Google OAuth2 consent screen
3. User authorizes → Google redirects with auth code
4. Agent exchanges code → Gets access/refresh tokens
5. Agent stores tokens → Can access user's calendar
```

### 2. Technical Components

#### OAuth2 Tools Added:
- `get_oauth2_auth_url()`: Generate authorization URL
- `handle_oauth2_callback()`: Exchange auth code for tokens
- `setup_user_oauth2_credentials()`: Store user credentials
- `get_user_calendar_events()`: Access user's calendar

#### Session State Storage:
- User OAuth2 tokens stored per email: `user_oauth2_{email}`
- OAuth2 state parameter: `oauth_state_{email}`
- Base64 encoded for security

## Setup Steps

### 1. Google Cloud Console Setup

1. **Create OAuth 2.0 Client ID**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Web application"

2. **Configure OAuth Consent Screen**:
   - Add your app name and description
   - Add authorized domains
   - Add scopes: `https://www.googleapis.com/auth/calendar.readonly`

3. **Set Redirect URIs**:
   - Add your callback URL: `https://your-app-domain.com/oauth/callback`
   - For development: `http://localhost:8000/oauth/callback`

4. **Note Credentials**:
   - Client ID: `your-client-id.apps.googleusercontent.com`
   - Client Secret: `your-client-secret`

### 2. Update Agent Configuration

Edit `tool_agent/subagents/weather_agent/agent.py`:

```python
# Replace these placeholders with your actual values
CLIENT_ID = "your-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "https://your-app-domain.com/oauth/callback"
```

### 3. Frontend Integration

You'll need a frontend to handle the OAuth2 flow:

```javascript
// Example frontend code
async function initiateOAuth2(userEmail) {
    // Call your agent to generate auth URL
    const response = await fetch('/api/agent', {
        method: 'POST',
        body: JSON.stringify({
            message: `Generate OAuth2 authorization URL for ${userEmail}`
        })
    });
    
    const result = await response.json();
    const authUrl = result.auth_url;
    
    // Redirect user to Google OAuth2
    window.location.href = authUrl;
}

// Handle OAuth2 callback
function handleOAuth2Callback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const userEmail = localStorage.getItem('userEmail');
    
    // Send callback to your agent
    fetch('/api/agent', {
        method: 'POST',
        body: JSON.stringify({
            message: `Handle OAuth2 callback for ${userEmail} with code ${code} and state ${state}`
        })
    });
}
```

## Usage Examples

### 1. Generate Authorization URL

**User Message**: "I want to access my calendar events"

**Agent Response**: 
```
I'll help you access your calendar. What's your email address?

User: user@example.com

Agent: I'll generate an authorization URL for you. Please visit this URL to authorize access to your calendar:

https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...&response_type=code&access_type=offline&prompt=consent&state=...
```

### 2. Handle OAuth2 Callback

**User Message**: "I've authorized access. Here's the callback: https://your-app.com/oauth/callback?code=4/0AfJohXn...&state=abc123..."

**Agent Response**:
```
Authentication successful! I can now access your calendar events. Let me fetch them for you.

Found 3 upcoming events for user@example.com:
1. Team Meeting - Tomorrow at 10:00 AM
2. Lunch with Client - Tomorrow at 12:00 PM  
3. Project Review - Friday at 2:00 PM
```

### 3. Access User Calendar

**User Message**: "Show my calendar events"

**Agent Response**:
```
I'll fetch your calendar events using your OAuth2 credentials.

Found 5 upcoming events for user@example.com:
1. Morning Standup - Today at 9:00 AM
2. Client Call - Today at 2:00 PM
3. Team Meeting - Tomorrow at 10:00 AM
4. Lunch with Client - Tomorrow at 12:00 PM
5. Project Review - Friday at 2:00 PM
```

## Security Considerations

### 1. State Parameter
- Generated using `secrets.token_urlsafe(32)`
- Stored in session state
- Verified on callback to prevent CSRF attacks

### 2. Token Storage
- Access tokens and refresh tokens encoded in base64
- Stored in session state per user email
- Never logged or exposed in responses

### 3. HTTPS Required
- OAuth2 redirect URIs must use HTTPS in production
- Local development can use HTTP

### 4. Token Expiration
- Access tokens expire in 1 hour
- Refresh tokens can be used to get new access tokens
- Implement token refresh logic for production

## Production Deployment

### 1. Environment Variables
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH2_REDIRECT_URI=https://your-app-domain.com/oauth/callback
```

### 2. Update Agent Code
```python
import os

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") 
REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI")
```

### 3. Frontend Deployment
- Deploy frontend to handle OAuth2 flow
- Set up proper routing for callback
- Implement secure token handling

## Troubleshooting

### Common Issues:

1. **"Invalid redirect_uri"**
   - Ensure redirect URI matches exactly in Google Console
   - Check for trailing slashes or protocol differences

2. **"Invalid client_id"**
   - Verify client ID is correct
   - Check that OAuth2 client is properly configured

3. **"Access token not found"**
   - User needs to re-authenticate
   - Check if tokens were properly stored

4. **"Calendar access denied"**
   - User needs to grant calendar permissions
   - Check OAuth2 scopes are correct

### Debug Commands:
```python
# Check if user has OAuth2 credentials
debug_calendar_access()

# List available calendars
list_calendars()

# Get user-specific calendar events
get_user_calendar_events("user@example.com")
```

## Next Steps

1. **Token Refresh**: Implement automatic token refresh
2. **Error Handling**: Add better error messages and recovery
3. **User Management**: Add user registration and management
4. **Calendar Management**: Add create/update/delete events
5. **Notifications**: Implement calendar event notifications

## Benefits of This Approach

✅ **User-Friendly**: No manual calendar sharing required
✅ **Secure**: OAuth2 tokens stored securely
✅ **Scalable**: Supports multiple users
✅ **Standard**: Uses industry-standard OAuth2 flow
✅ **Flexible**: Can access any calendar user has permission for 