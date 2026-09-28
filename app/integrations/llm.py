"""LLM abstraction (OpenAI-compatible chat completions over HTTP).

Works with vLLM, Ollama's OpenAI-compatible endpoint and external
OpenAI-compatible APIs, selected purely through configuration
(LLM_BASE_URL / LLM_API_KEY / LLM_MODEL). Nothing is hardcoded to one
provider, and no LLM is required for the service to start or report
health. Only this module knows the HTTP details.
"""

import json
from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

_JSON_INSTRUCTION = (
    "Respond with a single valid JSON object that conforms to the requested "
    "schema. No prose, no markdown, no code fences."
)


class LLMError(Exception):
    """Raised when the LLM is not configured, unreachable, or unusable."""


def _strip_code_fence(text: str) -> str:
    """Best-effort removal of markdown JSON code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1 :]
        if cleaned.endswith("```"):
            cleaned = cleaned[: -len("```")]
    return cleaned.strip()


class LLMClient:
    """Minimal OpenAI-compatible chat client."""

    def __init__(
        self,
        *,
        base_url: str | None,
        api_key: str | None,
        model: str | None,
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/") if base_url else None
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._http = httpx.AsyncClient(base_url=self._base_url, headers=headers, timeout=timeout)

    @property
    def is_configured(self) -> bool:
        return bool(self._base_url and self._model)

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a chat completion and return the message content."""
        if not self.is_configured:
            raise LLMError("LLM is not configured: set LLM_BASE_URL and LLM_MODEL.")
        payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        try:
            response = await self._http.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM request failed: {exc.__class__.__name__}") from exc
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("LLM response did not contain a chat completion.") from exc
        if not isinstance(content, str):
            raise LLMError("LLM returned an unexpected content type.")
        return content

    async def structured(
        self,
        messages: list[dict[str, str]],
        schema: type[T],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> T:
        """Generate JSON and validate it against a Pydantic schema."""
        prompt_messages = [*messages, {"role": "system", "content": _JSON_INSTRUCTION}]
        content = await self.generate(
            prompt_messages, temperature=temperature, max_tokens=max_tokens
        )
        try:
            parsed = json.loads(_strip_code_fence(content))
        except json.JSONDecodeError as exc:
            raise LLMError("LLM did not return valid JSON.") from exc
        return schema.model_validate(parsed)

    async def close(self) -> None:
        await self._http.aclose()


def get_llm_client(settings: Settings) -> LLMClient:
    """Build an LLM client from settings."""
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key.get_secret_value() if settings.llm_api_key else None,
        model=settings.llm_model,
    )