"""Shared pytest fixtures and helpers."""

from app.services.llm_service import LLMProvider, LLMService


class MockLLMProvider(LLMProvider):
    """Test double for LLM text generation."""

    def __init__(self, response: str = "Mock insight answer.") -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.response


def make_llm_service(response: str = "Mock insight answer.") -> LLMService:
    return LLMService(provider=MockLLMProvider(response))
