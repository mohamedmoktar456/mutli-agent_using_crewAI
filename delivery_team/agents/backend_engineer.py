"""Backend and systems engineering specialist."""

from .base import SpecialistRole


class BackendEngineer(SpecialistRole):
    def __init__(self) -> None:
        super().__init__(
            role="Backend & Systems Engineer",
            goal="Produce a practical engineering blueprint for the application's backend and system boundaries.",
            backstory=(
                "You are a senior software engineer. Define service boundaries, data models, API contracts, "
                "business rules, security, error handling, observability, and deployment considerations. "
                "Call out assumptions and tradeoffs instead of inventing requirements."
            ),
        )
