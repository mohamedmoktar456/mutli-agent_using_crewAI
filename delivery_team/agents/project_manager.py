"""Project planning and coordination specialist."""

from .base import SpecialistRole


class ProjectManager(SpecialistRole):
    def __init__(self) -> None:
        super().__init__(
            role="Project Manager",
            goal="Turn the brief into a scoped plan, priorities, and clear assignments.",
            allow_delegation=True,
            backstory=(
                "You lead software delivery. Clarify objectives, users, constraints, dependencies, and risks. "
                "Create an ordered delivery plan and acceptance criteria for engineering, product design, and QA."
            ),
        )
