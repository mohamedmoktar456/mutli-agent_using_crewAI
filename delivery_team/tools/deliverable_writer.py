"""Safely save the final delivery blueprint as a Markdown artifact."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeliveryBlueprintInput(BaseModel):
    project_name: str = Field(..., description="Short project name used as the report heading.")
    report_markdown: str = Field(..., description="Integrated Markdown report containing all agent deliverables.")


class DeliveryBlueprintWriterTool(BaseTool):
    name: str = "Save delivery blueprint"
    description: str = (
        "Save the integrated project plan, engineering blueprint, interface design, and quality review to the "
        "single fixed Markdown filename inside this run's designated deliverables folder. Never choose or alter a path."
    )
    args_schema: Type[BaseModel] = DeliveryBlueprintInput
    output_directory: str = Field(..., exclude=True)

    def _run(self, project_name: str, report_markdown: str) -> str:
        report = report_markdown.strip()
        if not report:
            return "Could not save the blueprint: report content was empty."
        if len(report) > 100_000:
            return "Could not save the blueprint: report exceeded the 100,000-character limit."

        heading = re.sub(r"[\r\n#]+", " ", project_name).strip()[:120] or "Project delivery blueprint"
        content = f"# {heading}\n\n{report}\n"
        output_directory = Path(self.output_directory).resolve()
        deliverables_root = Path(__file__).resolve().parents[2] / "deliverables"
        if output_directory == deliverables_root.resolve() or not output_directory.is_relative_to(deliverables_root.resolve()):
            return "Could not save the blueprint: output directory is outside the allowed deliverables folder."
        destination = output_directory / "delivery_blueprint.md"
        temporary = output_directory / ".delivery_blueprint.tmp"
        try:
            output_directory.mkdir(parents=True, exist_ok=True)
            temporary.write_text(content, encoding="utf-8")
            temporary.replace(destination)
        except OSError as error:
            return f"Could not save the blueprint: {error.__class__.__name__}."
        return "Delivery blueprint saved as deliverables/<run-id>/delivery_blueprint.md."
