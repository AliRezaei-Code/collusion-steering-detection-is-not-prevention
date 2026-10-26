"""OpenRouter client with retries and reasoning-token handling."""

from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path
from typing import Any

import requests

RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504}
AUTH_PATH = Path.home() / ".local/share/opencode/auth.json"


class OpenRouterError(RuntimeError):
    """Raised when an OpenRouter call cannot be completed."""


def load_api_key() -> str:
    """Read the key from the environment, then the local OpenCode auth store."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    if AUTH_PATH.exists():
        try:
            data = json.loads(AUTH_PATH.read_text())
            key = (data.get("openrouter") or {}).get("key", "").strip()
        except Exception:
            key = ""
    if not key:
        raise OpenRouterError(
            "No OpenRouter key. Set OPENROUTER_API_KEY or add one to "
            f"{AUTH_PATH} under the 'openrouter' entry."
        )
    return key


class OpenRouterClient:
    """Minimal chat-completions client.

    The free-tier models used in the pilot spend most tokens on hidden
    reasoning. If the visible content is empty, the client retries with a larger
    ``max_tokens`` before giving up.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 120,
        max_retries: int = 5,
    ) -> None:
        self.api_key = api_key or load_api_key()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/openresearch/collusion-steering",
                "X-Title": "Collusion Steering Pilot",
            }
        )

    def chat(
        self,
        model: str | list[str],
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 700,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return ``{text, reasoning, usage, model, raw}``.

        ``model`` may be a list. On a failed attempt the client rotates to the
        next model, which spreads free-tier upstream rate limits.
        """
        models = [model] if isinstance(model, str) else list(model)
        if not models:
            raise OpenRouterError("no model specified")

        max_tokens_current = max_tokens
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            current_model = models[attempt % len(models)]
            payload: dict[str, Any] = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens_current,
            }
            if response_format is not None:
                payload["response_format"] = response_format
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=(10, 30),
                    stream=True,
                )
                if response.status_code in RETRYABLE_STATUS:
                    body = response.text[:240]
                    response.close()
                    raise OpenRouterError(f"HTTP {response.status_code}: {body}")
                response.raise_for_status()

                # Enforce a total deadline. A slow provider can keep the socket
                # alive indefinitely while streaming, which a per-read timeout
                # does not catch.
                chunks: list[bytes] = []
                started = time.time()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        chunks.append(chunk)
                    if time.time() - started > self.timeout:
                        response.close()
                        raise OpenRouterError(
                            f"total response timeout after {self.timeout}s"
                        )
                response.close()
                data = json.loads(b"".join(chunks))
                if "error" in data:
                    raise OpenRouterError(str(data["error"])[:300])

                choice = data["choices"][0]["message"]
                content = (choice.get("content") or "").strip()
                reasoning = (choice.get("reasoning") or "").strip()

                if not content:
                    # The model may have spent the whole budget on reasoning.
                    if max_tokens_current < 2400:
                        max_tokens_current = min(2400, max_tokens_current * 2)
                        raise OpenRouterError(
                            "empty visible content (reasoning-only); retrying "
                            f"with max_tokens={max_tokens_current}"
                        )
                    raise OpenRouterError("empty visible content after retries")

                return {
                    "text": content,
                    "reasoning": reasoning,
                    "usage": data.get("usage") or {},
                    "model": data.get("model", current_model),
                    "raw": data,
                }
            except Exception as exc:  # noqa: BLE001 - retry everything transient
                last_error = exc
                if attempt == self.max_retries - 1:
                    break
                delay = min(20.0, (2 ** min(attempt, 4)) + random.random())
                time.sleep(delay)

        raise OpenRouterError(
            f"OpenRouter call failed after {self.max_retries} attempts: {last_error}"
        )
