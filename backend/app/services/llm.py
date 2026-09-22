from __future__ import annotations

import json
import logging

import httpx

from app.config import settings

log = logging.getLogger("aadhyatmik.llm")


class LLMError(RuntimeError):
    pass


def llm_configured() -> bool:
    return bool(settings.llm_api_key and settings.llm_api_base)


def _base() -> str:
    if settings.llm_api_base:
        return settings.llm_api_base
    provider = settings.llm_provider.lower()
    if provider == "groq":
        return "https://api.groq.com/openai/v1"
    if provider == "ollama":
        return "http://127.0.0.1:11434/v1"
    if provider in {"openai", "openai_compatible"} and settings.llm_api_key:
        return "https://api.openai.com/v1"
    return ""


async def complete_json(system: str, user: str) -> dict | None:
    base = _base()
    if not settings.llm_api_key or not base:
        return None
    url = base + "/chat/completions"
    payload = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
    last_error = None
    for attempt in (1, 2):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                log.error("llm_http status=%s body=%s", resp.status_code, resp.text[:400])
                last_error = f"HTTP {resp.status_code}"
                continue
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            log.exception("llm_attempt_failed attempt=%s", attempt)
    raise LLMError(last_error or "llm failed")
