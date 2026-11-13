"""CrewAI engineering team and shared-output workflow."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from crewai import Agent, Crew, LLM, Process, Task

from .config import configured_llm


class ProjectDeliveryTeam:
    """Create the engineering lead and three collaborating engineers."""

    def __init__(
        self,
        llm: LLM | None = None,
        progress_callback: Callable[[str], None] | None = None,
        output_directory: str | Path | None = None,
    ) -> None:
        self.llm = llm
        self.progress_callback = progress_callback
        self.config_directory = Path(__file__).resolve().parent / "crew_config"
        self.agents_config = yaml.safe_load((self.config_directory / "agents.yaml").read_text(encoding="utf-8"))
        self.tasks_config = yaml.safe_load((self.config_directory / "tasks.yaml").read_text(encoding="utf-8"))

        output_root = Path(__file__).resolve().parents[1] / "output"
        if output_directory is None:
            self.output_directory = output_root / uuid4().hex
        else:
            requested = Path(output_directory).resolve()
            resolved_root = output_root.resolve()
            if requested == resolved_root or not requested.is_relative_to(resolved_root):
                raise ValueError("Generated files must stay inside the project's output directory.")
            self.output_directory = requested

    def _create_agent(self, key: str, *, lead: bool = False) -> Agent:
        config = self.agents_config[key]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm or configured_llm(key, config.get("llm")),
            allow_delegation=lead,
            max_iter=6 if lead else 2,
            max_execution_time=90 if lead else 60,
            verbose=True,
        )

    def _task_completed(self, stage: str) -> Callable[[Any], None] | None:
        if self.progress_callback is None:
            return None

        def notify(_output: Any) -> None:
            self.progress_callback(stage)

        return notify

    def _create_task(
        self,
        key: str,
        filename: str,
        *,
        agent: Agent | None = None,
        context: list[Task] | None = None,
        markdown: bool = False,
    ) -> Task:
        config = self.tasks_config[key]
        return Task(
            name=config["name"],
            description=config["description"],
            expected_output=config["expected_output"],
            agent=agent,
            context=context,
            output_file=str(self.output_directory / filename),
            create_directory=True,
            markdown=markdown,
            callback=self._task_completed(config["name"]),
        )

    def build(self, project_brief: str, process_mode: str = "hierarchical") -> tuple[Crew, list[Agent], list[Task]]:
        if not project_brief.strip():
            raise ValueError("Enter a project description first.")
        processes = {
            "hierarchical": Process.hierarchical,
            "sequential": Process.sequential,
        }
        if process_mode not in processes:
            raise ValueError("process_mode must be 'hierarchical' or 'sequential'.")
        self.tasks_config["design_task"]["description"] = self.tasks_config["design_task"]["description"].replace(
            "{workflow_mode}",
            process_mode.title(),
        )

        engineering_lead = self._create_agent("engineering_lead", lead=True)
        backend_engineer = self._create_agent("backend_engineer")
        frontend_engineer = self._create_agent("frontend_engineer")
        test_engineer = self._create_agent("test_engineer")

        design_task = self._create_task(
            "design_task",
            "design.md",
            agent=engineering_lead,
            markdown=True,
        )
        backend_task = self._create_task(
            "code_task",
            "backend.py",
            agent=backend_engineer,
            context=[design_task],
        )
        frontend_task = self._create_task(
            "frontend_task",
            "app.py",
            agent=frontend_engineer,
            context=[design_task, backend_task],
        )
        test_task = self._create_task(
            "test_task",
            "test_backend.py",
            agent=test_engineer,
            context=[design_task, backend_task],
        )

        agents = [engineering_lead, backend_engineer, frontend_engineer, test_engineer]
        tasks = [design_task, backend_task, frontend_task, test_task]
        hierarchical = process_mode == "hierarchical"
        crew = Crew(
            agents=[backend_engineer, frontend_engineer, test_engineer]
            if hierarchical
            else agents,
            tasks=tasks,
            process=processes[process_mode],
            manager_agent=engineering_lead if hierarchical else None,
            verbose=True,
        )
        return crew, agents, tasks


def build_crew(
    project_brief: str,
    llm: LLM | None = None,
    progress_callback: Callable[[str], None] | None = None,
    output_directory: str | Path | None = None,
    process_mode: str = "hierarchical",
) -> tuple[Crew, list[Agent], list[Task]]:
    """Construct the engineering crew and its configured tasks."""
    return ProjectDeliveryTeam(
        llm=llm,
        progress_callback=progress_callback,
        output_directory=output_directory,
    ).build(project_brief, process_mode=process_mode)


def run_project(project_brief: str) -> Any:
    crew, _, _ = build_crew(project_brief)
    return crew.kickoff(inputs={"project_brief": project_brief.strip()})
