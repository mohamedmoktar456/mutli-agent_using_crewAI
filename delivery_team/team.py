"""Hierarchical CrewAI team assembly and project workflow."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task

from .agents import BackendEngineer, ProductDesigner, ProjectManager, QualityEngineer
from .config import configured_llm


class ProjectDeliveryTeam:
    """Build the project manager and specialists for hierarchical delegation."""

    def __init__(self, llm: LLM, progress_callback: Callable[[str], None] | None = None) -> None:
        self.llm = llm
        self.progress_callback = progress_callback
        self.manager_role = ProjectManager()
        self.specialist_roles = [BackendEngineer(), ProductDesigner(), QualityEngineer()]

    def _task_completed(self, stage: str) -> Callable[[Any], None] | None:
        if self.progress_callback is None:
            return None

        def notify(_output: Any) -> None:
            self.progress_callback(stage)

        return notify

    def build(self, project_brief: str) -> tuple[Crew, list[Agent], list[Task]]:
        if not project_brief.strip():
            raise ValueError("Enter a project description first.")

        manager = self.manager_role.create_agent(self.llm)
        engineers, designer, qa = [role.create_agent(self.llm) for role in self.specialist_roles]

        plan_task = Task(
            name="Project plan",
            description=(
                "Analyze this project brief: {project_brief}\n\n"
                "As project manager, define the objective, users, scope, constraints, assumptions, and risks. "
                "Create the work plan and acceptance criteria that will guide your specialist team. "
                "Keep the plan to 4 bullets and under 90 words."
            ),
            expected_output="A project plan of 4 bullets or fewer, under 90 words.",
            agent=manager,
            callback=self._task_completed("Project plan"),
        )
        engineering_task = Task(
            name="Engineering blueprint",
            description=(
                "Create the simplest suitable backend design. Cover the architecture, data model, main operations, "
                "and one key security concern. Skip optional infrastructure and keep it under 120 words.\n\n"
                "Project brief: {project_brief}"
            ),
            expected_output="A concise engineering design under 120 words.",
            context=[plan_task],
            callback=self._task_completed("Engineering blueprint"),
        )
        design_task = Task(
            name="Product and interface design",
            description=(
                "Define only the essential screens and interactions for the first version. Include one accessibility "
                "consideration and the main empty or error state. Keep it under 120 words.\n\n"
                "Project brief: {project_brief}"
            ),
            expected_output="A concise first-version UI specification under 120 words.",
            context=[plan_task],
            callback=self._task_completed("Product and interface design"),
        )
        qa_task = Task(
            name="Quality review",
            description=(
                "Review the plan, engineering blueprint, and product design. Trace requirements to acceptance "
                "checks. Include functional, edge, security, and accessibility checks; identify gaps and recommend "
                "up to two fixes. End with a readiness assessment. Keep it under 140 words.\n\n"
                "Project brief: {project_brief}"
            ),
            expected_output="A brief quality review with 3 checks or fewer and a readiness status, under 140 words.",
            context=[plan_task, engineering_task, design_task],
            callback=self._task_completed("Quality review"),
        )

        agents = [manager, engineers, designer, qa]
        tasks = [plan_task, engineering_task, design_task, qa_task]
        crew = Crew(
            agents=[engineers, designer, qa],
            tasks=tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )
        return crew, agents, tasks


def build_crew(
    project_brief: str,
    llm: LLM | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> tuple[Crew, list[Agent], list[Task]]:
    """Construct the hierarchical project delivery crew."""
    return ProjectDeliveryTeam(llm or configured_llm(), progress_callback).build(project_brief)


def run_project(project_brief: str) -> Any:
    crew, _, _ = build_crew(project_brief)
    return crew.kickoff(inputs={"project_brief": project_brief.strip()})
