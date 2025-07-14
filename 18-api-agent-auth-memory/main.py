import os
from google.adk.cli.fast_api import get_fast_api_app
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DB_URL = "postgresql+psycopg2://postgres:Welcome%40121@db.ftypcbopqkaconymxvyo.supabase.co:5432/postgres"
ALLOWED_ORIGINS = ["*"]
SERVE_WEB_INTERFACE = True

app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Mount static files
app.mount("/static", StaticFiles(directory=AGENT_DIR), name="static")

# Serve oauth-callback.html
@app.get("/oauth-callback.html")
async def oauth_callback():
    return FileResponse(os.path.join(AGENT_DIR, "oauth-callback.html"))

# Serve the frontend example
@app.get("/frontend.html")
async def frontend():
    return FileResponse(os.path.join(AGENT_DIR, "FRONTEND_OAUTH2_EXAMPLE.html"))

# Serve the OAuth2 handler JavaScript
@app.get("/oauth-handler.js")
async def oauth_handler():
    return FileResponse(os.path.join(AGENT_DIR, "oauth-handler.js"), media_type="application/javascript")

# Inject OAuth2 handler into ADK web interface
@app.middleware("http")
async def inject_oauth_handler(request, call_next):
    response = await call_next(request)
    
    # Only inject for the main ADK interface
    if request.url.path == "/" and "text/html" in response.headers.get("content-type", ""):
        # Read the OAuth2 handler script
        oauth_handler_path = os.path.join(AGENT_DIR, "oauth-handler.js")
        if os.path.exists(oauth_handler_path):
            with open(oauth_handler_path, 'r') as f:
                oauth_script = f.read()
            
            # Inject the script into the HTML response
            content = response.body.decode('utf-8')
            if '</body>' in content:
                script_tag = f'<script>{oauth_script}</script>'
                content = content.replace('</body>', f'{script_tag}</body>')
                response.body = content.encode('utf-8')
    
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
