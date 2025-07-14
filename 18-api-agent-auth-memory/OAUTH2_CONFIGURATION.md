# OAuth2 Configuration Guide

This guide shows you how to configure the OAuth2 environment variables for user calendar access.

## Environment Variables Setup

Create a `.env` file in your project root with the following variables:

```bash
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Supabase Configuration (for session state)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# OAuth2 Configuration for User Calendar Access
GOOGLE_OAUTH2_CLIENT_ID=your_oauth2_client_id_here.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your_oauth2_client_secret_here
GOOGLE_OAUTH2_REDIRECT_URI=https://your-app-domain.com/oauth-callback.html

# Firebase Configuration (for tasks API)
FIREBASE_EMAIL=your_firebase_email_here
FIREBASE_PASSWORD=your_firebase_password_here
FIREBASE_API_KEY=your_firebase_api_key_here
```

## Getting Your OAuth2 Credentials

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client ID**

### 2. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Fill in required information:
   - App name: "Calendar Agent"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events.readonly`

### 3. Create OAuth 2.0 Client ID

1. Go back to **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client ID**
3. Choose **Web application**
4. Set authorized redirect URIs:
   - `https://your-app-domain.com/oauth-callback.html`
   - `http://localhost:8000/oauth-callback.html` (for development)
5. Click **Create**

### 4. Copy Your Credentials

After creation, you'll see:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

## Update Your Environment Variables

Replace the placeholder values in your `.env` file:

```bash
GOOGLE_OAUTH2_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_OAUTH2_REDIRECT_URI=https://your-app-domain.com/oauth-callback.html
```

## For Development

If you're testing locally, use:

```bash
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/oauth-callback.html
```

## For Production

For production deployment:

```bash
GOOGLE_OAUTH2_REDIRECT_URI=https://your-actual-domain.com/oauth-callback.html
```

## Security Notes

1. **Never commit** your `.env` file to version control
2. **Keep your client secret** secure
3. **Use HTTPS** for production redirect URIs
4. **Rotate secrets** regularly

## Testing Your Configuration

1. Start your agent:
```bash
adk web
```

2. Test OAuth2 flow:
```
User: "I want to access my calendar"
Agent: "What's your email?"
User: "your-email@gmail.com"
```

3. The agent should generate an OAuth2 URL and open a popup for authorization.

## Troubleshooting

### "Invalid redirect_uri"
- Ensure the redirect URI in Google Console matches exactly
- Check for trailing slashes or protocol differences

### "Invalid client_id"
- Verify your client ID is correct
- Check that OAuth2 client is properly configured

### "Access denied"
- Ensure you've added the required scopes
- Check that your app is not in testing mode (if using external users) 