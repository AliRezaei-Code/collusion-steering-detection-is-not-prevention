"""Local CLI backend for the pilot when the OpenRouter free quota is exhausted.

This is a **fallback**, not a replacement for the white-box study. It calls
``opencode run`` as a text completion. Each call is a fresh session, so the
conversation history is flattened into one prompt. Temperature and max_tokens
are not controllable through the CLI; the model id is logged with every run so a
report can say which backend produced the data.
"""

from __future__ import annotations

import json
import subprocess
import time
from typing import Any

DEFAULT_CLI_MODEL = "opencode-go/deepseek-v4.1-flash"

DEFAULT_PREAMBLE = (
    "Do not use any tools. You are a text-only model inside a controlled "
    "research harness. Follow the requested output format exactly."
)


class LocalCLIClient:
    """Drop-in ``chat`` client using the local OpenCode CLI."""

    backend = "opencode-cli"

    def __init__(
        self,
        model: str = DEFAULT_CLI_MODEL,
        timeout: int = 180,
        max_retries: int = 3,
        preamble: str | None = None,
    ) -> None:
        self.model_id = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.preamble = preamble or DEFAULT_PREAMBLE

    @staticmethod
    def _flatten(
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        preamble: str | None = None,
    ) -> str:
        parts = [preamble or DEFAULT_PREAMBLE]
        for message in messages:
            role = str(message.get("role", "user")).upper()
            content = str(message.get("content", ""))
            parts.append(f"[{role}]\n{content}")
        if response_format and response_format.get("type") == "json_object":
            parts.append(
                "Return only one JSON object. No prose, no code fences, no "
                "explanation outside the object."
            )
        return "\n\n".join(parts)

    def chat(
        self,
        model: str | list[str],
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 700,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        prompt = self._flatten(messages, response_format, self.preamble)
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                proc = subprocess.run(
                    [
                        "opencode",
                        "run",
                        "--model",
                        self.model_id,
                        "--format",
                        "json",
                        "--auto",
                        prompt,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"opencode exit {proc.returncode}: {proc.stderr[:300]}"
                    )
                texts: list[str] = []
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") == "text":
                        text = (event.get("part") or {}).get("text") or ""
                        if text:
                            texts.append(text)
                if not texts:
                    raise RuntimeError("no text event in CLI output")
                return {
                    "text": "\n".join(texts).strip(),
                    "reasoning": "",
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "cost": 0,
                    },
                    "model": self.model_id,
                    "raw": proc.stdout[-2000:],
                }
            except Exception as exc:  # noqa: BLE001 - retry the fallback
                last_error = exc
                time.sleep(2 + 2 * attempt)
        raise RuntimeError(
            f"CLI backend failed after {self.max_retries} attempts: {last_error}"
        )
