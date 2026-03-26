"""Quick sanity check — each agent calls the Gemini API once."""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time

load_dotenv()

MODEL = "gemini-3.1-flash-lite-preview"

def get_api_key_for_agent(agent_id):
    """Return API key for the given agent.

    Tries agent-specific key first (GEMINI_API_KEY_SARAH, etc.),
    then falls back to a shared GEMINI_API_KEY.
    Raises ValueError if no key is found.
    """
    agent_key_name = f"GEMINI_API_KEY_{agent_id.upper()}"
    agent_key = os.getenv(agent_key_name)
    if agent_key:
        return agent_key
    shared_key = os.getenv("GEMINI_API_KEY")
    if shared_key:
        return shared_key
    raise ValueError(
        f"No API key found for agent {agent_id}. "
        f"Set either {agent_key_name} or GEMINI_API_KEY in .env file."
    )

agents = ["sarah", "james", "priya", "tom", "lin"]
all_passed = True

for agent_id in agents:
    try:
        api_key = get_api_key_for_agent(agent_id)
    except ValueError as e:
        print(f"[FAIL] {agent_id}: {e}")
        all_passed = False
        continue

    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL,
            temperature=0.7,
            google_api_key=api_key,
        )
        response = llm.invoke("Reply with exactly: OK")
        time.sleep(1)
        print(f"[PASS] {agent_id}: {response.content.strip()}")
    except Exception as error:
        print(f"[FAIL] {agent_id}: {error}")
        all_passed = False

print()
if all_passed:
    print("All APIs OK — ready to run the simulation.")
else:
    print("One or more APIs failed. Fix the errors above before running the simulation.")
