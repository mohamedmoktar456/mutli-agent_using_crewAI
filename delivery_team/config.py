"""LLM provider configuration loaded from the local environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProviderSettings:
    """Selected provider, model, and matching API key."""

    provider: str
    model: str
    api_key: str

    @classmethod
    def from_environment(cls) -> ProviderSettings:
        provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        defaults = {
            "openai": ("openai/gpt-4o-mini", "OPENAI_API_KEY", None),
            "gemini": ("gemini/gemini-3.5-flash-lite", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
        }
        if provider not in defaults:
            raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Choose: {', '.join(defaults)}")

        default_model, key_name, alternate_key = defaults[provider]
        api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv(key_name, "").strip()
        if alternate_key:
            api_key = api_key or os.getenv(alternate_key, "").strip()
        if not api_key:
            key_names = f"LLM_API_KEY or {key_name}"
            if alternate_key:
                key_names += f" or {alternate_key}"
            raise ValueError(f"No API key found. Set {key_names} in .env.")

        return cls(
            provider=provider,
            model=os.getenv("LLM_MODEL", "").strip() or default_model,
            api_key=api_key,
        )

    def create_llm(self) -> LLM:
        return LLM(model=self.model, api_key=self.api_key, timeout=45)


def configured_llm() -> LLM:
    """Build the configured OpenAI or Gemini model."""
    return ProviderSettings.from_environment().create_llm()
