"""Context-aware accessibility checklist for interface planning."""

from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class AccessibilityChecklistInput(BaseModel):
    project_brief: str = Field(..., description="Project brief used to tailor the interface checklist.")


class AccessibilityChecklistTool(BaseTool):
    name: str = "Interface accessibility checklist"
    description: str = (
        "Return a concise, locally generated accessibility checklist tailored to the project brief. "
        "Use it while designing screens and interaction states."
    )
    args_schema: Type[BaseModel] = AccessibilityChecklistInput

    def _run(self, project_brief: str) -> str:
        checks = [
            "Every form control needs a visible label; explain validation errors in text near the relevant field.",
            "Support keyboard operation with a clear focus indicator and logical focus order.",
            "Do not use color alone to communicate status; keep text and controls easy to distinguish.",
            "Provide clear empty, loading, success, and error states where the workflow needs them.",
        ]
        if re.search(r"\b(mobile|phone|tablet|responsive)\b", project_brief, re.IGNORECASE):
            checks.append("Keep layouts usable on narrow screens and make touch controls comfortably targetable.")
        if re.search(r"\b(web|website|browser|web application)\b", project_brief, re.IGNORECASE):
            checks.append("Use semantic headings and descriptive names for interactive controls.")
        return "Interface accessibility checklist:\n" + "\n".join(f"- {item}" for item in checks)
