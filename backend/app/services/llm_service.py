"""LLM provider abstraction and OpenAI implementation."""

from abc import ABC, abstractmethod

from openai import APIConnectionError, APIStatusError, OpenAI, OpenAIError

from app.core.config import settings


class LLMProvider(ABC):
    """Abstract interface for text-generation backends."""

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from system and user prompts."""


class OpenAIProvider(LLMProvider):
    """OpenAI Chat Completions API provider."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Set it in .env or docker-compose environment."
            )
        self._client = OpenAI(api_key=key)
        # Model from OPENAI_MODEL env var (see settings.OPENAI_MODEL)
        self._model = model or settings.OPENAI_MODEL

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
        except APIConnectionError as exc:
            raise RuntimeError("Failed to connect to OpenAI API.") from exc
        except APIStatusError as exc:
            raise RuntimeError(f"OpenAI API error: {exc.message}") from exc
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty response.")

        return content.strip()


class LLMService:
    """
    Facade for LLM text generation.

    Delegates to a pluggable provider so OpenAI can be swapped later
    (e.g. Azure OpenAI, Anthropic, local models) without changing callers.
    """

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or OpenAIProvider()

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        return self._provider.generate_text(system_prompt, user_prompt)
