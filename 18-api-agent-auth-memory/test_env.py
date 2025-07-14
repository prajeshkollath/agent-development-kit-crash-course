#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables Test ===")
print(f"GOOGLE_OAUTH2_CLIENT_ID: {os.getenv('GOOGLE_OAUTH2_CLIENT_ID', 'NOT_FOUND')}")
print(f"GOOGLE_OAUTH2_CLIENT_SECRET: {os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', 'NOT_FOUND')}")
print(f"GOOGLE_OAUTH2_REDIRECT_URI: {os.getenv('GOOGLE_OAUTH2_REDIRECT_URI', 'NOT_FOUND')}")

# Check if values look correct
client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
if client_id and client_id != 'NOT_FOUND':
    if client_id.endswith('.apps.googleusercontent.com'):
        print("✅ CLIENT_ID format looks correct")
    else:
        print("❌ CLIENT_ID format looks incorrect")
else:
    print("❌ CLIENT_ID not found")

client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
if client_secret and client_secret != 'NOT_FOUND':
    if client_secret.startswith('GOCSPX-'):
        print("✅ CLIENT_SECRET format looks correct")
    else:
        print("❌ CLIENT_SECRET format looks incorrect")
else:
    print("❌ CLIENT_SECRET not found")

redirect_uri = os.getenv('GOOGLE_OAUTH2_REDIRECT_URI')
if redirect_uri and redirect_uri != 'NOT_FOUND':
    if redirect_uri.endswith('/oauth-callback.html'):
        print("✅ REDIRECT_URI format looks correct")
    else:
        print("❌ REDIRECT_URI format looks incorrect")
else:
    print("❌ REDIRECT_URI not found") 