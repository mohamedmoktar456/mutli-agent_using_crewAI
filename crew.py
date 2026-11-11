"""CrewAI project team with provider selection controlled by .env."""

from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()


def configured_llm() -> LLM:
    """Build a CrewAI LLM using the provider and model in .env."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()

    defaults = {
        "openai": ("gpt-4o-mini", "OPENAI_API_KEY"),
        "gemini": ("gemini/gemini-2.0-flash", "GEMINI_API_KEY"),
        "anthropic": ("claude-3-5-haiku-latest", "ANTHROPIC_API_KEY"),
        "ollama": ("ollama/llama3.1", ""),
        "openrouter": ("openrouter/openai/gpt-4o-mini", "OPENROUTER_API_KEY"),
    }
    if provider not in defaults:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose: {', '.join(defaults)}"
        )
    default_model, provider_key = defaults[provider]
    api_key = api_key or (os.getenv(provider_key, "").strip() if provider_key else "")
    if provider != "ollama" and not api_key:
        raise ValueError(
            f"No API key found. Set LLM_API_KEY or {provider_key} in .env."
        )

    kwargs: dict[str, Any] = {"model": model or default_model, "verbose": False}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return LLM(**kwargs)


def build_crew(project_brief: str, llm: LLM | None = None) -> tuple[Crew, list[Agent], list[Task]]:
    """Create four collaborating agents and a sequential, inspectable workflow."""
    llm = llm or configured_llm()

    planner = Agent(
        role="مدير المشروع ومخطط الفريق",
        goal="فهم طلب المستخدم وتحويله إلى خطة دقيقة ومهام واضحة للفريق",
        backstory=(
            "أنت مدير مشاريع تقني تحلل احتياجات المستخدم، تحدد النطاق والافتراضات، "
            "ثم توزع العمل على المطور ومصمم الواجهة ومختبر الجودة. تكتب بالعربية الواضحة."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    developer = Agent(
        role="مطور Backend ومنطق الأعمال",
        goal="اقتراح بنية خلفية عملية وتنفيذ منطق التطبيق وفق الخطة",
        backstory=(
            "أنت مطور Python خبير. تحدد المكونات والبيانات والواجهات والمنطق، "
            "وتشرح التنفيذ بوضوح مع مراعاة الأمان والأخطاء والحالات الطرفية."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    designer = Agent(
        role="مصمم واجهات وتجربة مستخدم",
        goal="تصميم تجربة استخدام سهلة ومتناسقة تدعم احتياج المستخدم",
        backstory=(
            "أنت مصمم منتجات رقمية. تقترح هيكل الشاشات والتفاعلات والحالات "
            "والنصوص وإرشادات الوصول، بما يتماشى مع احتياجات المشروع."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    qa = Agent(
        role="مختبر جودة وضمان المتطلبات",
        goal="مراجعة الخطة والحل وتصميم التجربة واكتشاف المخاطر والفجوات",
        backstory=(
            "أنت مهندس جودة دقيق. تحول المتطلبات إلى معايير قبول وحالات اختبار، "
            "وتراجع مخرجات الفريق وتكشف العيوب مع خطوات قابلة للتحقق."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    plan_task = Task(
        description=(
            "حلل وصف المشروع التالي: {project_brief}\n\n"
            "اكتب ملخص الهدف والمستخدمين والوظائف الأساسية والقيود والافتراضات. "
            "وزع العمل في خطة مرتبة تتضمن مهام Backend والواجهة والجودة ومعايير القبول."
        ),
        expected_output="خطة مشروع عربية منظمة، بمهام ومعايير قبول واضحة.",
        agent=planner,
    )
    backend_task = Task(
        description=(
            "اعتماداً على طلب المستخدم وخطة مدير المشروع السابقة، صمم الحل الخلفي. "
            "حدد المكونات والبيانات والواجهات وتدفق العمل، وقدّم مقتطفات تنفيذ عند الحاجة. "
            "اذكر معالجة الأخطاء والاعتبارات الأمنية.\n\nطلب المستخدم: {project_brief}"
        ),
        expected_output="تصميم Backend عملي وخطوات تنفيذ متوافقة مع الخطة.",
        agent=developer,
        context=[plan_task],
    )
    ui_task = Task(
        description=(
            "اعتماداً على طلب المستخدم والخطة وتصميم Backend، اقترح تجربة الواجهة. "
            "صف الشاشات والمكونات والتفاعلات والحالات الفارغة والأخطاء والنصوص. "
            "اجعل التصميم قابلاً للتنفيذ ومناسباً للمستخدم.\n\nطلب المستخدم: {project_brief}"
        ),
        expected_output="مواصفات واجهة وتجربة استخدام متكاملة ومفهومة.",
        agent=designer,
        context=[plan_task, backend_task],
    )
    qa_task = Task(
        description=(
            "راجع الطلب وخطة المشروع وحل Backend وتجربة الواجهة. استخرج معايير القبول، "
            "واكتب حالات تحقق عملية، ثم اذكر الفجوات والمخاطر واقتراحات إصلاحها. "
            "اختم بحكم واضح على جاهزية المقترح والمتطلبات المتبقية.\n\nطلب المستخدم: {project_brief}"
        ),
        expected_output="مراجعة جودة نهائية مع معايير قبول وحالات اختبار وفجوات واضحة.",
        agent=qa,
        context=[plan_task, backend_task, ui_task],
    )
    crew = Crew(
        agents=[planner, developer, designer, qa],
        tasks=[plan_task, backend_task, ui_task, qa_task],
        process=Process.sequential,
        verbose=False,
    )
    return crew, [planner, developer, designer, qa], [plan_task, backend_task, ui_task, qa_task]


def run_project(project_brief: str) -> Any:
    if not project_brief.strip():
        raise ValueError("اكتب وصف المشروع أولاً.")
    crew, _, _ = build_crew(project_brief)
    return crew.kickoff(inputs={"project_brief": project_brief.strip()})
