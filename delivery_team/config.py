"""LLM model selection from YAML and API credentials from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProviderSettings:
    """Selected provider, YAML model, and matching API key."""

    provider: str
    model: str
    api_key: str

    @classmethod
    def from_environment(
        cls,
        agent_key: str | None = None,
        configured_model: str | None = None,
    ) -> ProviderSettings:
        """Read provider/model from agents.yaml and credentials from .env."""
        if not configured_model or "/" not in configured_model:
            raise ValueError(
                "Each agent must define its provider and model in agents.yaml "
                "using the 'provider/model' format."
            )

        provider_name, model_name = configured_model.strip().split("/", maxsplit=1)
        provider = provider_name.strip().lower()
        model_name = model_name.strip()
        key_names = {
            "openai": ("OPENAI_API_KEY", None),
            "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        }
        if provider not in key_names or not model_name:
            supported = ", ".join(key_names)
            raise ValueError(
                f"Invalid agent model '{configured_model}'. Use 'provider/model' "
                f"with a supported provider: {supported}."
            )

        prefix = agent_key.upper() if agent_key else ""
        agent_api_key = os.getenv(f"{prefix}_API_KEY", "").strip() if prefix else ""
        key_name, alternate_key = key_names[provider]
        api_key = agent_api_key or os.getenv(key_name, "").strip()
        if alternate_key:
            api_key = api_key or os.getenv(alternate_key, "").strip()
        if not api_key:
            agent_key_name = f"{prefix}_API_KEY or " if prefix else ""
            alternate_name = f" or {alternate_key}" if alternate_key else ""
            raise ValueError(
                f"No API key found. Set {agent_key_name}{key_name}"
                f"{alternate_name} in .env for the '{provider}' model."
            )

        return cls(
            provider=provider,
            model=f"{provider}/{model_name}",
            api_key=api_key,
        )

    def create_llm(self) -> LLM:
        return LLM(model=self.model, api_key=self.api_key, timeout=45)


def configured_llm(agent_key: str | None = None, model: str | None = None) -> LLM:
    """Build the model defined for one agent in agents.yaml."""
    return ProviderSettings.from_environment(agent_key, model).create_llm()