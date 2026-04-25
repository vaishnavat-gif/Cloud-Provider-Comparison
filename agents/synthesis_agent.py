from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """
You are a cloud expert.

Based on research:

1. Pick best provider
2. Rank all 3
3. Give short reason

Format:

Best Provider: <name>
Ranking: 1) <name> 2) <name> 3) <name>
Reason: <one line>
"""

class SynthesisAgent(BaseAgent):
    def __init__(self):
        super().__init__("Synthesis", SYSTEM_PROMPT)

    def run_synthesis(self, research, query):
        prompt = f"{query}\n\nResearch:\n{research}"
        return self.run(prompt)