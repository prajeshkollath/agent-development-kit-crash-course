import os
from google.adk.cli.fast_api import get_fast_api_app
import uvicorn


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
