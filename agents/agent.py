import json
import re
import time
from langchain_google_genai import ChatGoogleGenerativeAI


class Agent:
    def __init__(self, agent_id: str, persona: str, llm: ChatGoogleGenerativeAI):
        self.agent_id = agent_id
        self.persona = persona
        self.llm = llm

        # State
        self.private_score = 0
        self.private_thought = ""
        self.public_score = 0
        self.public_statement = ""

        # History
        self.history = []

    def _parse_json(self, text) -> dict:
        """Extract JSON from LLM response, handling markdown wrapping."""
        if isinstance(text, list):
            text=" ".join(part["text"] if isinstance(part, dict) and "text" in part else str(part) for part in text)
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    def private_reflect(self, channel_a_template: str) -> dict:
        """Channel A: Private honest reflection."""
        prompt = channel_a_template.format(persona=self.persona)
        response = self.llm.invoke(prompt)
        time.sleep(1)
        parsed = self._parse_json(response.content)

        self.private_score = int(parsed["score"])
        self.private_thought = parsed["private_thought"]
        return parsed

    def public_express(
        self,
        channel_b_template: str,
        social_pressure: str,
        neighbor_statements: str,
    ) -> dict:
        """Channel B: Public expression under social context."""
        prompt = channel_b_template.format(
            persona=self.persona,
            social_pressure=social_pressure,
            neighbor_statements=neighbor_statements,
            private_thought=self.private_thought,
            private_score=self.private_score,
        )
        response = self.llm.invoke(prompt)
        time.sleep(1)
        parsed = self._parse_json(response.content)

        self.public_score = int(parsed["score"])
        self.public_statement = parsed["public_statement"]
        return parsed

    def record_round(self, round_num: int):
        """Save this round's state to history."""
        self.history.append(
            {
                "round": round_num,
                "agent_id": self.agent_id,
                "private_score": self.private_score,
                "private_thought": self.private_thought,
                "public_score": self.public_score,
                "public_statement": self.public_statement,
                "falsification_gap": abs(self.private_score - self.public_score),
            }
        )
