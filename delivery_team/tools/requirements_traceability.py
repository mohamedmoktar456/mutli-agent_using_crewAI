"""Heuristic traceability hints for the quality review agent."""

from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RequirementsTraceabilityInput(BaseModel):
    project_brief: str = Field(..., description="Original project brief and constraints.")
    project_plan: str = Field("", description="Project manager plan.")
    engineering_blueprint: str = Field("", description="Engineering blueprint.")
    product_design: str = Field("", description="Product and interface design.")


_STOP_WORDS = {
    "about", "after", "also", "and", "are", "build", "can", "could", "from", "have", "into", "its",
    "make", "more", "must", "need", "not", "only", "our", "project", "should", "that", "their", "them",
    "then", "there", "this", "through", "under", "user", "users", "using", "want", "what", "when", "where",
    "which", "while", "with", "without", "would", "your",
}


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
        if len(token) > 2 and token not in _STOP_WORDS
    }


class RequirementsTraceabilityTool(BaseTool):
    name: str = "Requirements traceability check"
    description: str = (
        "Extract concise candidate requirements from the brief and compare their key words with the plan, "
        "engineering, and design outputs. Treat low lexical overlap as a possible gap only; manually verify "
        "synonyms and semantic coverage before reporting a defect."
    )
    args_schema: Type[BaseModel] = RequirementsTraceabilityInput

    def _run(
        self,
        project_brief: str,
        project_plan: str = "",
        engineering_blueprint: str = "",
        product_design: str = "",
    ) -> str:
        cleaned = re.sub(
            r"(?i)\b(project name|product type|project brief|constraints):\s*",
            "",
            project_brief,
        )
        candidates: list[str] = []
        for part in re.split(r"[\n.!?;؟؛]+", cleaned):
            item = re.sub(r"^\s*[-*•\d.)]+\s*", "", part).strip()
            if len(_tokens(item)) >= 3 and item not in candidates:
                candidates.append(item)
            if len(candidates) == 8:
                break

        output_tokens = _tokens("\n".join((project_plan, engineering_blueprint, product_design)))
        lines = ["Candidate requirement trace (lexical signal only; verify meaning manually):"]
        if not candidates:
            return lines[0] + "\n- No clear requirement sentences were extracted; review the brief directly."

        for index, item in enumerate(candidates, start=1):
            item_tokens = _tokens(item)
            overlap = len(item_tokens & output_tokens)
            signal = "possible gap" if item_tokens and overlap / len(item_tokens) < 0.25 else "text overlap found"
            lines.append(f"{index}. {item[:180]} — {signal} ({overlap}/{len(item_tokens)} key terms).")
        return "\n".join(lines)
