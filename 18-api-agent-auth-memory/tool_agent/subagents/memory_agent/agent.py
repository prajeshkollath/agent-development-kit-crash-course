from google.adk.agents import LlmAgent
#from google.adk.tools.base_tool import BaseTool
#from google.adk.tools.tool_context import ToolContext
from google.adk.tools import FunctionTool
from sqlalchemy import create_engine, text
from typing import Dict
import psycopg2
import json


# Reuse this across both queries
DB_URL = "postgresql+psycopg2://postgres:Welcome%40121@db.ftypcbopqkaconymxvyo.supabase.co:5432/postgres"

def fetch_test_rows() -> Dict:

    try:
        engine = create_engine(DB_URL)

        test_rows = []
        session_results = []

        with engine.connect() as conn:

            # Fetch rows from memory_test
            test_result = conn.execute(text("""
                SELECT id, user_id, note, created_at
                FROM memory_test
                ORDER BY created_at
            """)).fetchall()

            test_rows = [f"{row.user_id}: {row.note}" for row in test_result] if test_result else ["No test notes found."]

            # Fetch session states with result
            session_result = conn.execute(text("""
                SELECT state
                FROM sessions
                WHERE user_id = :user_id
                AND (state::jsonb ? 'result' OR state::jsonb ? 'last_time_check')
                ORDER BY update_time
            """), {"user_id": "user"}).fetchall()

            for row in session_result:
                try:
                    state = row.state if isinstance(row.state, dict) else json.loads(row.state)
                    if "result" in state:
                        session_results.append(state["result"])
                    if "last_time_check" in state:
                        session_results.append(state["last_time_check"])        # appending last time check key
                except Exception as e:
                    session_results.append(f"Error parsing state: {e}")

        return {
            "test_rows": test_rows,
            "session_results": session_results or ["No past session results found."]
        }

    except Exception as e:
        return {
            "error": str(e),
            "test_rows": [],
            "session_results": []
        }


memory_tool = FunctionTool(func=fetch_test_rows)


memory_agent = LlmAgent(
    name="memory_agent",
    model="gemini-2.0-flash",
    tools=[memory_tool],
    description="recall the user's past time queries.",
    instruction="""

    Use the fetch_test_rows tool to
    - retrieve all notes in the test table and also state from users past session results where key is result or last_time_check
      Display both sections separately.
    """,
#    output_key="time_history"

)

# original function body
"""
    try:
        engine = create_engine("postgresql+psycopg2://postgres:Welcome%40121@db.ftypcbopqkaconymxvyo.supabase.co:5432/postgres")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, user_id, note, created_at FROM memory_test ORDER BY created_at"))
            rows = result.fetchall()

        return {
            "test_rows": [f"{row.user_id}: {row.note}" for row in rows] or ["No rows found."]
        }
    except Exception as e:
        print("❌ SQLAlchemy DB ERROR:", str(e))
        return {"test_rows": [f"ERROR: {str(e)}"]}
"""