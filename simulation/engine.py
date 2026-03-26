import pandas as pd
from typing import Dict, Optional
from agents.agent import Agent
from networks.graph import get_neighbors


class SimulationEngine:
    def __init__(
        self,
        agents: Dict[str, Agent],
        graph,
        channel_a_template: str,
        channel_b_template: str,
        social_pressure: str,
        seed_statements: str,
        trigger_round: Optional[int] = None,
        trigger_agent: Optional[str] = None,
    ):
        self.agents = agents
        self.graph = graph
        self.channel_a_template = channel_a_template
        self.channel_b_template = channel_b_template
        self.social_pressure = social_pressure
        self.seed_statements = seed_statements
        self.trigger_round = trigger_round
        self.trigger_agent = trigger_agent

    def _get_neighbor_statements(self, agent_id: str, round_num: int) -> str:
        if round_num == 0:
            return self.seed_statements

        neighbors = get_neighbors(self.graph, agent_id)
        statements = []
        for nid in neighbors:
            for entry in reversed(self.agents[nid].history):
                if entry["round"] == round_num - 1:
                    statements.append(f"- {nid}: '{entry['public_statement']}'")
                    break

        if not statements:
            return self.seed_statements
        return "\n".join(statements)

    def _is_triggered(self, agent_id: str, round_num: int) -> bool:
        return (
            self.trigger_round is not None
            and round_num >= self.trigger_round
            and agent_id == self.trigger_agent
        )

    def run_round(self, round_num: int):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}")
        print(f"{'='*60}")

        # Phase 1: Private reflection
        for agent_id, agent in self.agents.items():
            try:
                agent.private_reflect(self.channel_a_template)
            except Exception as e:
                print(f"  [ERROR] {agent_id} private_reflect: {e}")

        # Phase 2: Public expression
        for agent_id, agent in self.agents.items():
            neighbor_stmts = self._get_neighbor_statements(agent_id, round_num)

            if self._is_triggered(agent_id, round_num):
                print(f"  *** TRIGGER: {agent_id} breaks ranks! ***")
                agent.public_score = agent.private_score
                agent.public_statement = (
                    f"I need to be honest. {agent.private_thought} "
                    f"I can't stay silent about this anymore."
                )
            else:
                try:
                    agent.public_express(
                        self.channel_b_template,
                        self.social_pressure,
                        neighbor_stmts,
                    )
                except Exception as e:
                    print(f"  [ERROR] {agent_id} public_express: {e}")

            agent.record_round(round_num)

        # Print summary
        for agent_id, agent in self.agents.items():
            gap = abs(agent.private_score - agent.public_score)
            marker = " <<< TRIGGERED" if self._is_triggered(agent_id, round_num) else ""
            print(
                f"  {agent_id}: priv={agent.private_score:+d} "
                f"pub={agent.public_score:+d} gap={gap}{marker}"
            )

    def run(self, num_rounds: int) -> pd.DataFrame:
        for r in range(num_rounds):
            self.run_round(r)
        return self.get_results()

    def get_results(self) -> pd.DataFrame:
        all_records = []
        for agent in self.agents.values():
            all_records.extend(agent.history)
        return pd.DataFrame(all_records)
