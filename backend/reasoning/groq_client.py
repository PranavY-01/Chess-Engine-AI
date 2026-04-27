"""Async-friendly Groq AI client wrapper using OpenAI-compatible SDK."""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class GroqClient:
    """Thin wrapper around Groq's OpenAI-compatible chat completions API."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if self._client is not None:
            return self._client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return self._client

    async def explain(self, prompt: str) -> str:
        """Send a prompt to Groq and return the explanation text."""
        try:
            def _call() -> str:
                client = self._get_client()
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a chess algorithm demonstrator. "
                                "Give only 2-3 short sentences. "
                                "Explain the algorithm's decision process — "
                                "evaluation score, search depth, pruning, "
                                "or branch quality. Tie it to the current "
                                "game state. Never give chess strategy advice."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=200,
                )
                text = response.choices[0].message.content
                return text.strip() if text else ""

            text = await asyncio.to_thread(_call)
            return text or "The demonstrator is thinking too hard right now — try again."
        except Exception:
            return "The demonstrator is thinking too hard right now — try again."
