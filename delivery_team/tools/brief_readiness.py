"""Deterministic completeness hints for project briefs."""

from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class BriefReadinessInput(BaseModel):
    project_brief: str = Field(..., description="Project name, product type, brief, and constraints.")


class BriefReadinessTool(BaseTool):
    name: str = "Project brief readiness scan"
    description: str = (
        "Run a local heuristic scan before planning. It highlights whether the brief explicitly mentions users, "
        "the desired outcome, core behavior, constraints, and success checks. Treat missing signals as questions, "
        "not as proof that a requirement is absent."
    )
    args_schema: Type[BaseModel] = BriefReadinessInput

    def _run(self, project_brief: str) -> str:
        checks = (
            ("Target users", r"\b(user|users|customer|customers|admin|staff|team|audience)\b|مستخدم|عميل|مسؤول|فريق"),
            ("Desired outcome", r"\b(goal|solve|help|enable|allow|manage|track|build|create|provide)\b|هدف|حل|يساعد|إدارة|تتبع|إنشاء|بناء"),
            ("Core behavior", r"\b(add|create|edit|update|delete|search|view|save|submit|send|upload|export)\b|إضافة|إنشاء|تعديل|تحديث|حذف|بحث|عرض|حفظ|إرسال|رفع|تصدير"),
            ("Constraints", r"\b(python|streamlit|react|mobile|web|api|database|timeline|week|day|budget|must|no )\b|بايثون|موبايل|ويب|قاعدة بيانات|موعد|أيام|أسابيع|ميزانية|يجب|بدون"),
            ("Acceptance or success signal", r"\b(acceptance|success|complete when|must be|should be|within|under \d+)\b|معيار قبول|نجاح|مكتمل عندما|يجب أن|ضمن"),
        )
        present: list[str] = []
        unclear: list[str] = []
        for label, pattern in checks:
            (present if re.search(pattern, project_brief, re.IGNORECASE) else unclear).append(label)

        lines = ["Local brief readiness scan (heuristic; confirm with the requester):"]
        if present:
            lines.append("Signals found: " + ", ".join(present) + ".")
        if unclear:
            lines.append("Not explicit; record as an assumption or ask: " + ", ".join(unclear) + ".")
        return "\n".join(lines)
