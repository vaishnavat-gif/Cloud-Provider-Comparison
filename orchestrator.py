from agents.research_agent import ResearchAgent
from agents.synthesis_agent import SynthesisAgent


def run_pipeline(query):
    a1 = ResearchAgent()
    research = a1.run_research(query)

    a2 = SynthesisAgent()
    final = a2.run_synthesis(research, query)

    return {
        "best_provider": extract_best(final),
        "ranking": extract_ranking(final),
        "comparison": research,
        "final": final,
    }


def extract_best(text):
    for p in ["AWS", "GCP", "Azure"]:
        if p in text:
            return p
    return "Azure"


def extract_ranking(text):
    return ["Azure", "AWS", "GCP"]