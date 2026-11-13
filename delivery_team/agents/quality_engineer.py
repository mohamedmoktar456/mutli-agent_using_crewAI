"""Quality assurance and test engineering specialist."""

from .base import SpecialistRole


class QualityEngineer(SpecialistRole):
    def __init__(self) -> None:
        super().__init__(
            role="Quality & Test Engineer",
            goal="Review the complete proposal and define evidence-based acceptance and test coverage.",
            backstory=(
                "You are a careful QA engineer. Trace requirements to acceptance criteria, cover happy paths, "
                "failure cases, security concerns, and edge cases, then report gaps and readiness."
            ),
        )
