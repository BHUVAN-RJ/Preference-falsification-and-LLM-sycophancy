from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.agent import Agent
from configs.personas import PERSONAS
from networks.graph import create_complete_graph
from simulation.engine import SimulationEngine
from prompts.social_pressure import PRESSURE_STRONG,PRESSURE_MODERATE, PRESSURE_NONE
import os

load_dotenv()

# --- Configuration ---
MODEL = "gemini-3.1-flash-lite-preview"
TEMPERATURE = 0.3
NUM_ROUNDS = 15
TRIGGER_ROUND = 6
TRIGGER_AGENT = "lin"

SEED_STATEMENTS = "\n".join([
    "- Company statement: 'The 737 MAX program represents the pinnacle of aviation safety and engineering excellence.'",
    "- Executive memo: 'Our cost-saving initiatives have strengthened our competitive position without compromising quality.'",
    "- Safety bulletin: 'All aircraft components meet or exceed regulatory standards.'",
    "- Leadership message: 'The production acceleration schedule reflects team confidence in our design integrity.'",
    "- Senior engineer Mike: 'I've reviewed the data thoroughly and I'm confident in our safety margins. We should be proud of this team's work.'",
    "- Your team lead: 'Let's focus on our delivery milestones. The safety concerns have been addressed at the executive level.'"
])

# --- Setup: one LLM client per agent ---
# Each agent can have its own API key, or fall back to a single shared key.
def get_api_key_for_agent(agent_id):
    """Return API key for the given agent.

    Tries agent-specific key first (GEMINI_API_KEY_SARAH, etc.),
    then falls back to a shared GEMINI_API_KEY.
    Raises ValueError if no key is found.
    """
    # Agent-specific key
    agent_key_name = f"GEMINI_API_KEY_{agent_id.upper()}"
    agent_key = os.getenv(agent_key_name)
    if agent_key:
        return agent_key
    # Shared key
    shared_key = os.getenv("GEMINI_API_KEY")
    if shared_key:
        return shared_key
    raise ValueError(
        f"No API key found for agent {agent_id}. "
        f"Set either {agent_key_name} or GEMINI_API_KEY in .env file."
    )

if __name__ == "__main__":
    agents = {}
    for agent_id, persona in PERSONAS.items():
        api_key = get_api_key_for_agent(agent_id)
        agent_llm = ChatGoogleGenerativeAI(
            model=MODEL,
            temperature=TEMPERATURE,
            google_api_key=api_key,
        )
        agents[agent_id] = Agent(agent_id, persona, agent_llm)

    graph = create_complete_graph(list(agents.keys()))

    with open("prompts/channel_a.txt") as f:
        channel_a = f.read()
    with open("prompts/channel_b.txt") as f:
        channel_b = f.read()

    # --- Run ---
    engine = SimulationEngine(
        agents=agents,
        graph=graph,
        channel_a_template=channel_a,
        channel_b_template=channel_b,
        social_pressure=PRESSURE_STRONG,
        seed_statements=SEED_STATEMENTS,
        trigger_round=TRIGGER_ROUND,
        trigger_agent=TRIGGER_AGENT,
    )

    results = engine.run(NUM_ROUNDS)

    # --- Save ---
    os.makedirs("results", exist_ok=True)
    results.to_csv("results/run_001.csv", index=False)
    print(f"\nSaved {len(results)} records to results/run_001.csv")

    # --- Summary ---
    print("\n--- Final Falsification Gaps ---")
    final_round = results[results["round"] == NUM_ROUNDS - 1]
    for _, row in final_round.iterrows():
        print(
            f"  {row['agent_id']}: priv={row['private_score']:+.0f} "
            f"pub={row['public_score']:+.0f} gap={row['falsification_gap']:.0f}"
        )

    avg_gap_pre = results[results["round"] < TRIGGER_ROUND]["falsification_gap"].mean()
    avg_gap_post = results[results["round"] >= TRIGGER_ROUND]["falsification_gap"].mean()
    print(f"\nAvg gap pre-trigger:  {avg_gap_pre:.2f}")
    print(f"Avg gap post-trigger: {avg_gap_post:.2f}")
    print(f"\nNow run: python analysis/plot_results.py results/run_001.csv")
