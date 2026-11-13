"""Local security and privacy trigger scan for project briefs."""

from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SecurityRiskScanInput(BaseModel):
    project_brief: str = Field(..., description="Project brief and technical constraints to scan.")


_RISK_RULES = (
    (
        "Accounts or authentication",
        r"\b(login|log in|sign in|account|password|authentication|session|role|permission)\b|تسجيل الدخول|حساب|كلمة المرور|مصادقة|جلسة|صلاحية|دور",
        "Define authorization boundaries, secure session handling, and account recovery behavior.",
    ),
    (
        "Personal or sensitive data",
        r"\b(personal data|pii|email address|phone number|location|health|medical|financial data)\b|بيانات شخصية|بريد إلكتروني|رقم الهاتف|الموقع|صحي|طبي|مالي",
        "Minimize collected data, limit access, define retention, and avoid logging sensitive values.",
    ),
    (
        "Payments or billing",
        r"\b(payment|payments|billing|checkout|subscription|credit card)\b|دفع|مدفوعات|فوترة|اشتراك|بطاقة ائتمان",
        "Use a compliant payment provider; never store raw card details in the application.",
    ),
    (
        "File uploads or attachments",
        r"\b(upload|uploads|file|files|attachment|attachments)\b|رفع|ملفات|مرفقات",
        "Validate file type and size, use safe storage names, and prevent executable content from being served.",
    ),
    (
        "External services or integrations",
        r"\b(integration|integrations|webhook|third.party|external api|oauth|api key)\b|تكامل|ويب هوك|واجهة برمجة|مفتاح api",
        "Keep credentials server-side, validate inbound data, and set timeouts and failure handling.",
    ),
)


class SecurityRiskScanTool(BaseTool):
    name: str = "Security and privacy risk scan"
    description: str = (
        "Scan a project brief for common security and privacy trigger areas, then return practical controls. "
        "This local keyword scan is a prompt for engineering judgment, not a security certification."
    )
    args_schema: Type[BaseModel] = SecurityRiskScanInput

    def _run(self, project_brief: str) -> str:
        findings: list[str] = []
        for label, pattern, recommendation in _RISK_RULES:
            if re.search(pattern, project_brief, re.IGNORECASE):
                findings.append(f"- {label} mentioned: {recommendation}")

        if not findings:
            findings.append("- No common high-risk trigger was found; still validate inputs and avoid exposing secrets.")
        findings.append("Confirm whether each detected area is in scope or explicitly excluded.")
        return "Local security and privacy scan (heuristic):\n" + "\n".join(findings)
