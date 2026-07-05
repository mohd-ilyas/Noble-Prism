"""
Backend-only OpenRouter integration.

The service keeps provider details and API keys away from the frontend, adds a
small in-memory cache to avoid duplicate calls, and logs failures without
including prompts or credentials.
"""
from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OpenRouterUnavailable(RuntimeError):
    """Raised when AI insights are requested without a configured provider."""


@dataclass
class _CacheEntry:
    expires_at: float
    value: str


class OpenRouterService:
    def __init__(self) -> None:
        self._cache: dict[str, _CacheEntry] = {}

    def _cache_key(self, messages: list[dict[str, str]], model: str) -> str:
        raw = repr((model, messages)).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 450,
    ) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise OpenRouterUnavailable("OPENROUTER_API_KEY is not configured")

        selected_model = model or settings.OPENROUTER_MODEL
        cache_key = self._cache_key(messages, selected_model)
        now = time.time()
        cached = self._cache.get(cache_key)
        if cached and cached.expires_at > now:
            return cached.value

        payload: dict[str, Any] = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://noble-prism.app",
            "X-Title": "Noble Prism",
        }

        last_error: Exception | None = None
        for attempt in range(settings.OPENROUTER_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.OPENROUTER_TIMEOUT_SECONDS) as client:
                    response = await client.post(
                        f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    self._cache[cache_key] = _CacheEntry(
                        expires_at=now + settings.OPENROUTER_CACHE_TTL_SECONDS,
                        value=content,
                    )
                    return content
            except (httpx.HTTPError, KeyError, IndexError) as exc:
                last_error = exc
                logger.warning(
                    "OpenRouter request failed on attempt %s/%s: %s",
                    attempt + 1,
                    settings.OPENROUTER_MAX_RETRIES + 1,
                    type(exc).__name__,
                )
                if attempt < settings.OPENROUTER_MAX_RETRIES:
                    await self._sleep_before_retry(attempt)

        raise OpenRouterUnavailable("OpenRouter request failed") from last_error

    async def _sleep_before_retry(self, attempt: int) -> None:
        import asyncio

        await asyncio.sleep(min(0.5 * (attempt + 1), 2.0))


openrouter_service = OpenRouterService()
