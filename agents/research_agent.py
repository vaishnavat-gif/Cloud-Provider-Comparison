from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """
You are a cloud research assistant.

Compare AWS, GCP, Azure.

Give structured output:

AWS:
Pricing: ...
Compute: ...
Storage: ...
AI/ML: ...
Use Cases: ...

GCP:
...

Azure:
...

Rules:
- Always fill all fields
- Keep answers short
- No "insufficient data"
"""

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research", SYSTEM_PROMPT)

    def run_research(self, query):
        return self.run(query)