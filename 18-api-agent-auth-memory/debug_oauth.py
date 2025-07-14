#!/usr/bin/env python3
"""
Debug script to test OAuth2 URL generation
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import secrets

# Load environment variables
load_dotenv()

print("=== OAuth2 Debug Test ===")

# Get OAuth2 configuration
CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_OAUTH2_REDIRECT_URI")

print(f"CLIENT_ID: {CLIENT_ID}")
print(f"CLIENT_SECRET: {CLIENT_SECRET}")
print(f"REDIRECT_URI: {REDIRECT_URI}")

# Test URL generation
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly"
]

# Generate state parameter
state = secrets.token_urlsafe(32)

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

print(f"\n=== Generated OAuth2 URL ===")
print(auth_url)

print(f"\n=== URL Parameters ===")
for key, value in auth_params.items():
    print(f"{key}: {value}")

print(f"\n=== Troubleshooting ===")
print("1. Check if CLIENT_ID ends with .apps.googleusercontent.com")
print("2. Verify REDIRECT_URI matches exactly in Google Cloud Console")
print("3. Ensure OAuth consent screen is configured")
print("4. Make sure Google Calendar API is enabled") 