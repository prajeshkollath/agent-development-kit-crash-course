import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import question_answering_agent

load_dotenv()


# Create an async main function to properly handle all async operations
async def main():
    # Create a new session service to store state
    session_service_stateful = InMemorySessionService()

    initial_state = {
        "user_name": "Brandon Hancock",
        "user_preferences": """
            I like to play Pickleball, Disc Golf, and Tennis.
            My favorite food is Mexican.
            My favorite TV show is Game of Thrones.
            Loves it when people like and subscribe to his YouTube channel.
        """,
    }

    # Create a NEW session (properly awaited)
    APP_NAME = "Brandon Bot"
    USER_ID = "brandon_hancock"
    SESSION_ID = str(uuid.uuid4())

    await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print("CREATED NEW SESSION:")
    print(f"\tSession ID: {SESSION_ID}")

    runner = Runner(
        agent=question_answering_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Brandon's favorite TV show?")]
    )

    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response: {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")

    # Create an async function to get and work with the session
    async def get_session_data():
        session = await session_service_stateful.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

        # Now we can access session.state safely
        print("=== Final Session State ===")
        for key, value in session.state.items():
            print(f"{key}: {value}")

    # Run the async function
    await get_session_data()

# Entry point for the async script
if __name__ == "__main__":
    asyncio.run(main())
