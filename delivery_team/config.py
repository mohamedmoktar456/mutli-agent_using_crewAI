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
    def from_environment(
        cls,
        agent_key: str | None = None,
        configured_model: str | None = None,
    ) -> ProviderSettings:
        """Resolve a YAML model with optional per-agent and global overrides.

        Agent overrides use ``<AGENT_KEY>_PROVIDER``, ``_MODEL``, and
        ``_API_KEY``. For example, ``backend_engineer`` maps to
        ``BACKEND_ENGINEER_PROVIDER``. YAML ``llm`` settings are the default;
        environment settings can change the provider or model.
        """
        global_provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        defaults = {
            "openai": ("openai/gpt-4o-mini", "OPENAI_API_KEY", None),
            "gemini": ("gemini/gemini-3.5-flash-lite", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
        }
        if global_provider not in defaults:
            raise ValueError(f"Unknown LLM_PROVIDER '{global_provider}'. Choose: {', '.join(defaults)}")

        prefix = agent_key.upper() if agent_key else ""
        agent_provider = os.getenv(f"{prefix}_PROVIDER", "").strip().lower() if prefix else ""
        agent_model = os.getenv(f"{prefix}_MODEL", "").strip() if prefix else ""

        def model_provider(model: str) -> str:
            return model.partition("/")[0].strip().lower() if "/" in model else ""

        yaml_provider = model_provider(configured_model or "")
        agent_model_provider = model_provider(agent_model)
        provider = agent_provider or agent_model_provider or yaml_provider or global_provider
        if provider not in defaults:
            setting = f"{prefix}_PROVIDER" if prefix else "LLM_PROVIDER"
            raise ValueError(f"Unknown {setting} '{provider}'. Choose: {', '.join(defaults)}")
        if agent_provider and agent_model_provider and agent_provider != agent_model_provider:
            raise ValueError(
                f"{prefix}_MODEL uses '{agent_model_provider}' but {prefix}_PROVIDER is '{agent_provider}'."
            )

        default_model, key_name, alternate_key = defaults[provider]
        global_model = os.getenv("LLM_MODEL", "").strip()
        if agent_model:
            model = agent_model
        elif configured_model and (not yaml_provider or provider == yaml_provider):
            model = configured_model
        elif configured_model or (agent_provider and provider != global_provider):
            # A provider override should not inherit a model for another provider.
            model = default_model
        else:
            model = global_model or default_model

        agent_api_key = os.getenv(f"{prefix}_API_KEY", "").strip() if prefix else ""
        shared_api_key = os.getenv("LLM_API_KEY", "").strip() if provider == global_provider else ""
        api_key = agent_api_key or shared_api_key or os.getenv(key_name, "").strip()
        if alternate_key:
            api_key = api_key or os.getenv(alternate_key, "").strip()
        if not api_key:
            key_names = f"{prefix}_API_KEY, {key_name}" if prefix else f"LLM_API_KEY or {key_name}"
            if prefix and provider == global_provider:
                key_names += " or LLM_API_KEY"
            if alternate_key:
                key_names += f" or {alternate_key}"
            raise ValueError(f"No API key found. Set {key_names} in .env.")

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
        )

    def create_llm(self) -> LLM:
        return LLM(model=self.model, api_key=self.api_key, timeout=45)


def configured_llm(agent_key: str | None = None, model: str | None = None) -> LLM:
    """Build the model configured for one agent, with environment overrides."""
    return ProviderSettings.from_environment(agent_key, model).create_llm()
