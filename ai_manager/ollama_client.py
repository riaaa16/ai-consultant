from __future__ import annotations

import json
from typing import Any

import requests


class OllamaError(RuntimeError):
    pass


def chat(
    *,
    prompt: str,
    model: str,
    host: str = "http://localhost:11434",
) -> str:
    url = f"{host.rstrip('/')}/api/chat"
    body: dict[str, Any] = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Output only a single JSON object. No markdown, no prose.",
            },
            {"role": "user", "content": prompt},
        ],
        "options": {
            "temperature": 0.2
        },
    }

    try:
        res = requests.post(url, json=body, timeout=60)
    except Exception as e:
        raise OllamaError(f"Failed to connect to Ollama at {host}: {e}") from e

    if res.status_code != 200:
        raise OllamaError(f"Ollama HTTP {res.status_code}: {res.text[:200]}")

    data = res.json()
    message = data.get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise OllamaError("Ollama response missing message.content")
    return content


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from model text.

    Accepts either a raw JSON object or content wrapped in ``` fences.
    """

    s = text.strip()
    if s.startswith("```"):
        # Remove first fence line and trailing fence.
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()

    # If model returned extra text, try to locate the first '{' ... last '}'
    if not s.startswith("{"):
        first = s.find("{")
        last = s.rfind("}")
        if first != -1 and last != -1 and last > first:
            s = s[first : last + 1]

    try:
        obj = json.loads(s)
    except Exception as e:
        raise OllamaError(f"Model did not return valid JSON: {e}") from e

    if not isinstance(obj, dict):
        raise OllamaError("Model JSON must be an object")

    return obj
