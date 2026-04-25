import os
import requests


class BaseAgent:
    def __init__(self, name, system_prompt):
        self.name = name
        self.system_prompt = system_prompt

        # Detect which provider to use
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def _chat_ollama(self, messages):
        try:
            res = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=30,
            )
            res.raise_for_status()
            return res.json()["message"]["content"]
        except Exception:
            raise RuntimeError("❌ Ollama not running")

    def _chat_gemini(self, messages):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"

        prompt = "\n".join([m["content"] for m in messages])

        res = requests.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            },
            timeout=30,
        )

        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _chat(self, messages):
        # Priority: Gemini (for Render) → Ollama (for local)
        if self.gemini_api_key:
            return self._chat_gemini(messages)
        else:
            return self._chat_ollama(messages)

    def run(self, user_input):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]
        return self._chat(messages)