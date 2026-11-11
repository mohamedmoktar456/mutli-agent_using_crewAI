"""CrewAI project team with provider selection controlled by .env."""

from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def configured_llm() -> LLM:
    """Build a CrewAI LLM using the provider and model in .env."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()

    defaults = {
        "openai": ("openai/gpt-4o-mini", "OPENAI_API_KEY"),
        "gemini": ("gemini/gemini-3.5-flash-lite", "GEMINI_API_KEY"),
        "anthropic": (
            "anthropic/claude-haiku-4-5-20251001",
            "ANTHROPIC_API_KEY",
        ),
        "ollama": ("ollama/llama3.1", ""),
        "openrouter": ("openrouter/openai/gpt-4o-mini", "OPENROUTER_API_KEY"),
    }
    if provider not in defaults:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose: {', '.join(defaults)}"
        )
    default_model, provider_key = defaults[provider]
    api_key = api_key or (os.getenv(provider_key, "").strip() if provider_key else "")
    if provider != "ollama" and not api_key:
        raise ValueError(
            f"No API key found. Set LLM_API_KEY or {provider_key} in .env."
        )

    kwargs: dict[str, Any] = {"model": model or default_model}
    if provider == "anthropic":
        kwargs["max_tokens"] = 4096
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return LLM(**kwargs)


def build_crew(project_brief: str, llm: LLM | None = None) -> tuple[Crew, list[Agent], list[Task]]:
    """Create four collaborating agents and a sequential, inspectable workflow."""
    if not project_brief.strip():
        raise ValueError("Enter a project description first.")
    llm = llm or configured_llm()

    planner = Agent(
        role="Project Manager and Team Planner",
        goal="Understand the user's request and turn it into a clear plan and work assignments.",
        backstory=(
            "You are an experienced technical project manager. Analyze user needs, define scope and assumptions, "
            "then assign work to the backend developer, UI/UX designer, and QA engineer. Write clearly in English."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    developer = Agent(
        role="Backend Developer",
        goal="Design a practical backend architecture and business logic that follows the project plan.",
        backstory=(
            "You are an experienced Python developer. Define components, data, APIs, and business logic. "
            "Explain implementation clearly and account for security, errors, and edge cases."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    designer = Agent(
        role="UI/UX Designer",
        goal="Design an accessible, consistent user experience that meets the user's needs.",
        backstory=(
            "You are a digital product designer. Propose screen structure, interactions, interface states, "
            "copy, and accessibility guidance that fit the project requirements."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    qa = Agent(
        role="QA Engineer and Requirements Reviewer",
        goal="Review the plan, backend design, and user experience; identify risks and gaps.",
        backstory=(
            "You are a detail-oriented quality engineer. Turn requirements into acceptance criteria and test cases, "
            "review team outputs, and report defects with reproducible checks."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    plan_task = Task(
        description=(
            "Analyze the following project brief: {project_brief}\n\n"
            "Summarize the goal, users, core features, constraints, and assumptions. "
            "Create an ordered plan with backend, UI/UX, and QA assignments plus acceptance criteria."
        ),
        expected_output="An organized project plan with clear assignments and acceptance criteria.",
        agent=planner,
    )
    backend_task = Task(
        description=(
            "Using the user's request and the project manager's plan, design the backend solution. "
            "Define components, data, APIs, and workflow; include implementation snippets where useful. "
            "Address error handling and security.\n\nUser request: {project_brief}"
        ),
        expected_output="A practical backend design and implementation outline aligned with the plan.",
        agent=developer,
        context=[plan_task],
    )
    ui_task = Task(
        description=(
            "Using the user's request, the plan, and the backend design, propose the user experience. "
            "Describe screens, components, interactions, empty and error states, and interface copy. "
            "Make the design practical and suitable for the intended users.\n\nUser request: {project_brief}"
        ),
        expected_output="A complete, understandable UI and user experience specification.",
        agent=designer,
        context=[plan_task, backend_task],
    )
    qa_task = Task(
        description=(
            "Review the request, project plan, backend solution, and user experience. Extract acceptance criteria, "
            "write practical verification cases, and report gaps and risks with proposed fixes. "
            "Conclude with a clear assessment of readiness and remaining requirements.\n\nUser request: {project_brief}"
        ),
        expected_output="A final quality review with acceptance criteria, test cases, and clearly reported gaps.",
        agent=qa,
        context=[plan_task, backend_task, ui_task],
    )
    crew = Crew(
        agents=[planner, developer, designer, qa],
        tasks=[plan_task, backend_task, ui_task, qa_task],
        process=Process.sequential,
        verbose=False,
    )
    return crew, [planner, developer, designer, qa], [plan_task, backend_task, ui_task, qa_task]


def run_project(project_brief: str) -> Any:
    if not project_brief.strip():
        raise ValueError("Enter a project description first.")
    crew, _, _ = build_crew(project_brief)
    return crew.kickoff(inputs={"project_brief": project_brief.strip()})
