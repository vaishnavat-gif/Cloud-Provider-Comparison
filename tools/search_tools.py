import os
from typing import Any

from tavily import TavilyClient

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

TAVILY_SEARCH_DECL = {
    "name": "tavily_search",
    "description": (
        "Search the web for current cloud provider information. "
        "Call this multiple times with different queries to gather complete data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Specific search query like AWS vs GCP pricing 2026",
            },
            "focus": {
                "type": "string",
                "enum": ["pricing", "performance", "services", "use_cases", "general"],
                "description": "What aspect to focus on",
            },
        },
        "required": ["query"],
    },
}


def tavily_search(query: str, focus: str = "general") -> dict[str, Any]:
    _ = focus
    fast_mode = os.getenv("FAST_MODE", "1").strip() == "1"
    max_results = 2 if fast_mode else 4
    depth = "basic" if fast_mode else "advanced"
    results = tavily.search(query=query, max_results=max_results, search_depth=depth)
    return {
        "query": query,
        "results": [
            {
                "title": result.get("title", ""),
                "content": result.get("content", "")[:400],
                "url": result.get("url", ""),
            }
            for result in results.get("results", [])
        ],
    }
