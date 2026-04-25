# Cloud Provider Comparison Agentic AI

This project follows an end-to-end agentic pipeline:

- `A1 Research Agent` uses Tavily search in a ReAct loop.
- `A2 Synthesis Agent` builds a structured cloud comparison using formatting tools.
- `A3 Evaluation Agent` acts as LLM-as-Judge, scores quality, and can request retry.
- `orchestrator.py` chains `A1 -> A2 -> A3` with retry support.
- `app.py` provides a Streamlit UI for the full workflow.

## Project Structure

- `agents/base_agent.py` - shared Ollama ReAct loop
- `agents/research_agent.py` - A1 with `tavily_search`
- `agents/synthesis_agent.py` - A2 with `format_comparison` and `add_recommendation`
- `agents/eval_agent.py` - A3 with `score_rubric` and `request_retry`
- `tools/search_tools.py` - Tavily declaration + executor
- `tools/format_tools.py` - comparison row/recommendation tools
- `tools/eval_tools.py` - rubric scoring and retry signal tools
- `orchestrator.py` - sequential pipeline + retry loop
- `app.py` - Streamlit frontend

## Prerequisites

- Python 3.10+
- Tavily API key (required)
- Ollama installed locally

## Setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set environment variables:

```powershell
$env:TAVILY_API_KEY="YOUR_TAVILY_KEY"
$env:OLLAMA_MODEL="llama3.2:3b"
# Optional (default shown)
$env:OLLAMA_BASE_URL="http://localhost:11434"
```
Agents call local Ollama (`$env:OLLAMA_BASE_URL/api/chat`) for all LLM requests.

## Run

```powershell
ollama pull llama3.2:3b
ollama serve
streamlit run app.py
```

## Deployment (Railway)

- Push repository to GitHub
- Create project on Railway from GitHub repo
- Set env vars `TAVILY_API_KEY`, `GROQ_API_KEY`, and `GROQ_MODEL` (or `OLLAMA_MODEL` alias)
- Start command:
  - `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Deployment (Render)

- Push repository to GitHub.
- Create a new **Web Service** in Render from this repo.
- Render will auto-detect `render.yaml` from the project root.
- Set required environment variables in Render dashboard:
  - `TAVILY_API_KEY`
  - `GROQ_API_KEY`
  - `GROQ_MODEL` (recommended: `llama-3.1-8b-instant`)
- Deploy and open the generated `onrender.com` URL.

## Submission Checklist

- [ ] GitHub repository with clean code and this README
- [ ] Problem statement document
- [ ] Task decomposition/spec document
- [ ] Architecture diagram (`User -> A1 -> A2 -> A3 -> UI`)
- [ ] Working agent with Groq + Tavily + LLM-as-Judge
- [ ] Deployed public app URL (Railway or Vercel)
- [ ] Loom video link (about 3 minutes)
- [ ] Team ready for viva and able to explain all components

