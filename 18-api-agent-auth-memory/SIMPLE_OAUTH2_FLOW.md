# Simple OAuth2 Flow - No Manual Callback Sharing

This guide shows how to implement OAuth2 without requiring users to manually share callback URLs.

## Approach 1: Frontend-Handled Popup (Recommended)

### How It Works:
1. **User types**: "I want to access my calendar"
2. **Agent asks**: "What's your email?"
3. **User provides**: "user@example.com"
4. **Frontend automatically**:
   - Opens OAuth2 popup window
   - User authorizes in popup
   - Popup closes automatically
   - Frontend detects completion
   - Agent gets calendar events

### Benefits:
- ✅ **No manual URL sharing** required
- ✅ **Seamless user experience**
- ✅ **Automatic completion detection**
- ✅ **Works in any browser**

## Approach 2: Direct Redirect with Return

### How It Works:
1. **User types**: "I want to access my calendar"
2. **Agent asks**: "What's your email?"
3. **User provides**: "user@example.com"
4. **Frontend redirects** to OAuth2 URL
5. **User authorizes** on Google's page
6. **Google redirects back** to your app
7. **Your app handles** the callback automatically
8. **Agent gets** calendar events

### Implementation:

```javascript
// Simple redirect approach
async function initiateOAuth2(email) {
    // Get auth URL from agent
    const response = await fetch('/api/agent', {
        method: 'POST',
        body: JSON.stringify({
            message: `Generate OAuth2 authorization URL for ${email}`
        })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
        // Store email in localStorage for callback
        localStorage.setItem('pendingOAuthEmail', email);
        
        // Redirect to Google OAuth2
        window.location.href = result.auth_url;
    }
}

// Handle OAuth2 callback (runs when user returns from Google)
function handleOAuth2Callback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const email = localStorage.getItem('pendingOAuthEmail');
    
    if (code && email) {
        // Send callback to agent
        fetch('/api/agent', {
            method: 'POST',
            body: JSON.stringify({
                message: `Handle OAuth2 callback for ${email} with code ${code} and state ${state}`
            })
        }).then(() => {
            // Clear pending email
            localStorage.removeItem('pendingOAuthEmail');
            
            // Get calendar events
            return fetch('/api/agent', {
                method: 'POST',
                body: JSON.stringify({
                    message: `Get calendar events for ${email}`
                })
            });
        }).then(response => response.json())
        .then(result => {
            // Display calendar events
            displayCalendarEvents(result);
        });
    }
}

// Check if we're returning from OAuth2
if (window.location.search.includes('code=')) {
    handleOAuth2Callback();
}
```

## Approach 3: Inline OAuth2 (Most User-Friendly)

### How It Works:
1. **User types**: "I want to access my calendar"
2. **Agent asks**: "What's your email?"
3. **User provides**: "user@example.com"
4. **Frontend shows** embedded OAuth2 iframe/form
5. **User authorizes** inline
6. **Agent gets** calendar events immediately

### Implementation:

```html
<!-- Embedded OAuth2 form -->
<div id="oauthForm" style="display: none;">
    <h3>Authorize Calendar Access</h3>
    <form id="googleOAuthForm" action="https://accounts.google.com/o/oauth2/v2/auth" method="GET">
        <input type="hidden" name="client_id" value="YOUR_CLIENT_ID">
        <input type="hidden" name="redirect_uri" value="https://your-app.com/oauth/callback">
        <input type="hidden" name="scope" value="https://www.googleapis.com/auth/calendar.readonly">
        <input type="hidden" name="response_type" value="code">
        <input type="hidden" name="access_type" value="offline">
        <input type="hidden" name="prompt" value="consent">
        <input type="hidden" name="state" id="oauthState">
        
        <p>Click the button below to authorize access to your Google Calendar:</p>
        <button type="submit">Authorize Calendar Access</button>
    </form>
</div>

<script>
function showOAuth2Form(email) {
    // Generate state parameter
    const state = Math.random().toString(36).substring(7);
    document.getElementById('oauthState').value = state;
    
    // Store email and state
    localStorage.setItem('pendingOAuthEmail', email);
    localStorage.setItem('oauthState', state);
    
    // Show form
    document.getElementById('oauthForm').style.display = 'block';
}
</script>
```

## Recommended Implementation: Popup Approach

The popup approach (Approach 1) is recommended because:

### Advantages:
- ✅ **No page navigation** - user stays in chat
- ✅ **Automatic completion** detection
- ✅ **Better UX** - seamless flow
- ✅ **Works everywhere** - no special setup

### User Experience:
```
User: "I want to access my calendar"
Agent: "What's your email?"
User: "user@example.com"
Agent: "I'll help you authorize access to user@example.com's calendar. Opening authorization window..."
[Popup opens automatically]
User: [authorizes in popup]
[Popup closes automatically]
Agent: "Great! I can now access your calendar events. Here are your upcoming events..."
```

### Technical Implementation:

1. **Frontend detects** calendar requests
2. **Calls agent** to generate OAuth2 URL
3. **Opens popup** with OAuth2 URL
4. **Polls popup** for closure
5. **Automatically** gets calendar events
6. **No manual** callback handling needed

## Setup Steps:

### 1. Update OAuth2 Redirect URI
Set your redirect URI to a simple page that just closes the popup:

```html
<!-- oauth-callback.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Authorization Complete</title>
</head>
<body>
    <script>
        // Close popup and notify parent
        if (window.opener) {
            window.opener.postMessage({
                type: 'oauth2_complete',
                code: new URLSearchParams(window.location.search).get('code'),
                state: new URLSearchParams(window.location.search).get('state')
            }, '*');
            window.close();
        } else {
            // Fallback for non-popup
            window.location.href = '/?oauth_complete=true';
        }
    </script>
    <p>Authorization complete! You can close this window.</p>
</body>
</html>
```

### 2. Update Agent OAuth2 Configuration
```python
REDIRECT_URI = "https://your-app.com/oauth-callback.html"
```

### 3. Frontend Listens for Completion
```javascript
window.addEventListener('message', function(event) {
    if (event.data.type === 'oauth2_complete') {
        // Handle OAuth2 completion
        handleOAuth2Completion(event.data.code, event.data.state);
    }
});
```

## Result: Zero Manual Steps

With this approach, users never need to:
- ❌ Copy/paste callback URLs
- ❌ Manually share authorization codes
- ❌ Handle OAuth2 technical details
- ❌ Navigate away from your app

The entire OAuth2 flow is **completely automated** and **user-friendly**! 