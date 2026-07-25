"""
Thin wrapper around the Groq SDK.

- `gemma2-9b-it`: fast/cheap model, used for structured field extraction.
- `llama-3.3-70b-versatile`: stronger reasoning model, used for risk classification,
  completeness reasoning, and the free-form chat assistant.
"""
import json
from groq import Groq

from app.config import settings

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def call_json(system_prompt: str, user_prompt: str, model: str) -> dict:
    """Call Groq and force a JSON object back. Raises if the model doesn't comply."""
    client = get_client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content
    return json.loads(content)


def call_text(system_prompt: str, user_prompt: str, model: str) -> str:
    client = get_client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return completion.choices[0].message.content
