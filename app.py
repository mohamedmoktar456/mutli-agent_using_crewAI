"""Streamlit interface for the CrewAI project delivery team."""

from __future__ import annotations

import os
from queue import Empty, Queue
from threading import Thread
from time import monotonic

import streamlit as st
from dotenv import load_dotenv

from delivery_team import build_crew

load_dotenv()
st.set_page_config(page_title="Northstar | Delivery Studio", page_icon="🧭", layout="wide")

st.markdown(
    """
<style>
:root { --ink:#13243a; --muted:#687a90; --line:#dce5ef; --blue:#2856c7; --teal:#247c79; }
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); }
[data-testid="stAppViewContainer"] { background:linear-gradient(180deg,#f2f6fb 0%,#f8fafc 360px,#fff 760px); }
[data-testid="stHeader"] { background:rgba(247,249,252,.94); }
[data-testid="stSidebar"] { background:#eef2f7; border-right:1px solid #dce4ee; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#192a42; }
.block-container { max-width:1160px; padding-top:1.5rem; padding-bottom:3rem; }
h1, h2, h3, .section-heading h2 { color:#13243a !important; letter-spacing:-.025em; }
.brand { display:flex; align-items:center; gap:.65rem; margin:0 0 1.1rem; color:#1a2e49; font-size:.88rem; font-weight:800; letter-spacing:.09em; }
.brand-icon { width:34px; height:34px; display:grid; place-items:center; color:#fff; background:linear-gradient(145deg,#315fcf,#25a2a0); border-radius:11px; font-size:1rem; }
.brand-sub { color:#8493a6; font-weight:600; letter-spacing:.08em; }
.hero { padding:2rem 2.15rem; border:1px solid #233e68; border-radius:22px; color:white; background:radial-gradient(ellipse at 90% 0%,rgba(70,204,190,.24),transparent 37%),linear-gradient(125deg,#14243c,#1d3a68 70%,#205476); box-shadow:0 16px 35px rgba(29,53,92,.13); }
.hero-kicker { margin-bottom:.65rem; color:#8de1d7; font-size:.69rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
.hero h1 { margin:0; color:#fff; font-size:clamp(1.6rem,3vw,2.25rem); line-height:1.16; font-weight:800; }
.hero p { max-width:690px; margin:.75rem 0 0; color:#d4e0f0; font-size:.98rem; line-height:1.6; }
.section-heading { margin:1.7rem 0 .75rem; }
.section-heading h2 { margin:0; font-size:1.15rem; font-weight:750; }
.section-heading p { margin:.25rem 0 0; color:var(--muted); font-size:.87rem; }
.role-num { color:#3c63c1; font-size:.68rem; letter-spacing:.12em; font-weight:800; }
.role-label { margin-top:.5rem; color:var(--teal); font-size:.64rem; letter-spacing:.1em; font-weight:800; text-transform:uppercase; }
.role-name { margin:.32rem 0 .45rem; color:#1b304d; font-size:1rem; line-height:1.25; font-weight:750; }
.role-copy { min-height:3.7rem; color:#687a90; font-size:.81rem; line-height:1.48; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line); border-radius:15px; background:rgba(255,255,255,.84); }
div[data-testid="stForm"] { border:0; padding:0; background:transparent; }
div[data-testid="stForm"] label { color:#253b58; font-weight:650; }
div[data-testid="stFormSubmitButton"] button { min-height:2.85rem; border:0; border-radius:10px; background:#2856c7; color:#fff; font-weight:750; }
div[data-testid="stFormSubmitButton"] button:hover { background:#1f46ad; color:#fff; }
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { border-radius:9px; }
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea { background:#fff !important; color:#192a42 !important; border-color:#cbd6e3 !important; }
[data-baseweb="select"] > div { background:#fff !important; color:#192a42 !important; border-color:#cbd6e3 !important; }
div[data-testid="stForm"] label, div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3 { color:#263a55 !important; }
div[data-testid="stMetric"] { padding:.8rem 1rem; border:1px solid var(--line); border-radius:13px; background:#fff; }
div[data-testid="stMetricLabel"] { color:#718197; }
@media (max-width: 760px) {
  .block-container { padding-top:.8rem; }
  .hero { padding:1.4rem; border-radius:16px; }
  .role-copy { min-height:0; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand"><span class="brand-icon">N</span><span>NORTHSTAR <span class="brand-sub">/ DELIVERY STUDIO</span></span></div>'
    '<div class="hero"><div class="hero-kicker">CrewAI · Software delivery workspace</div>'
    "<h1>From project idea to delivery blueprint.</h1>"
    "<p>Four specialists work through your brief in sequence, combining delivery planning, systems engineering, product design, and quality review.</p></div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(3)
for col, label, value in zip(
    metric_cols,
    ["DELIVERY TEAM", "WORKFLOW", "MODEL PROVIDERS"],
    ["4 specialists", "Hierarchical delegation", "OpenAI · Gemini"],
):
    with col:
        st.metric(label, value)

st.markdown(
    '<div class="section-heading"><h2>Meet your delivery team</h2><p>Each specialist owns a clear part of the project blueprint.</p></div>',
    unsafe_allow_html=True,
)
roles = [
    ("01", "PROJECT LEAD", "Project Manager", "Defines scope, delivery priorities, assumptions, and acceptance criteria."),
    ("02", "ENGINEERING", "Backend & Systems Engineer", "Plans architecture, data, APIs, business rules, security, and operations."),
    ("03", "PRODUCT DESIGN", "Product & UI/UX Designer", "Maps requirements to screens, responsive layouts, interactions, and accessibility."),
    ("04", "QUALITY", "Quality & Test Engineer", "Reviews coverage, edge cases, failure paths, risks, and project readiness."),
]
role_cols = st.columns(4, gap="small")
for col, (number, label, name, description) in zip(role_cols, roles):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="role-num">SPECIALIST {number}</div><div class="role-label">{label}</div><div class="role-name">{name}</div><div class="role-copy">{description}</div>',
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="section-heading"><h2>Start a project</h2><p>Share the goal, users, and constraints. The team will turn them into an engineering-focused plan.</p></div>',
    unsafe_allow_html=True,
)

quick_brief = (
    "Build a simple to-do list web app for one user. Let the user add tasks, mark them complete, "
    "and delete them. Save tasks in a local SQLite database. Show counts for open and completed tasks. "
    "No login, payments, or external integrations."
)
quick_left, quick_right = st.columns([1, 3])
with quick_left:
    if st.button("Fill a quick example", use_container_width=True):
        st.session_state["project_name_input"] = "Quick To-Do App"
        st.session_state["project_brief_input"] = quick_brief
        st.session_state["project_constraints_input"] = "Python and Streamlit; one-day prototype; no external services."
with quick_right:
    st.caption("Try a small to-do app brief to confirm the workflow before testing a larger idea.")

with st.container(border=True):
    with st.form("project_form"):
        top_left, top_right = st.columns([1.35, 1])
        with top_left:
            project_name = st.text_input("Project name", placeholder="e.g. Quick To-Do App", key="project_name_input")
        with top_right:
            platform = st.selectbox(
                "Product type",
                ["Web application", "Mobile application", "API or platform service", "Internal business tool", "Other"],
                key="product_type_input",
            )
        brief = st.text_area(
            "Project brief",
            placeholder="What should the first version do? Keep it to the main user and 2–4 essential features.",
            height=155,
            help="Include important workflows, integrations, technical preferences, and any known risks.",
            key="project_brief_input",
        )
        constraints = st.text_input(
            "Constraints or timeline (optional)",
            placeholder="e.g. Python and Streamlit; one-day prototype; no external services",
            key="project_constraints_input",
        )
        submitted = st.form_submit_button("Generate delivery blueprint", type="primary", use_container_width=True)

with st.sidebar:
    st.markdown("## Northstar")
    st.caption("AI-assisted software project planning")
    st.divider()
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    st.markdown("### Model configuration")
    st.caption(f"Provider: **{provider}**")
    st.caption(f"Model: **{model or 'provider default'}**")
    st.divider()
    st.markdown("### Workflow")
    for stage in ["01  Manager plans scope", "02  Manager delegates", "03  Specialists deliver", "04  Manager reviews"]:
        st.write(stage)

if submitted:
    if not brief.strip():
        st.warning("Add a project brief so the team has enough information to work from.")
    else:
        request = (
            f"Project name: {project_name.strip() or 'Untitled project'}\n"
            f"Product type: {platform}\n"
            f"Project brief: {brief.strip()}\n"
            f"Constraints: {constraints.strip() or 'Not specified'}"
        )
        try:
            stages = [
                "Project plan",
                "Engineering blueprint",
                "Product and interface design",
                "Quality review",
            ]
            completed: set[str] = set()
            progress_events: Queue[str] = Queue()
            crew, _, tasks = build_crew(request)

            def task_progress_callback(stage: str):
                def notify(_output) -> None:
                    progress_events.put(stage)

                return notify

            for stage, task in zip(stages, tasks):
                task.callback = task_progress_callback(stage)
            run_state: dict[str, object] = {}

            def run_crew() -> None:
                try:
                    run_state["result"] = crew.kickoff(inputs={"project_brief": request})
                except Exception as error:
                    run_state["error"] = error

            worker = Thread(target=run_crew, name="crewai-run", daemon=True)
            worker.start()

            with st.status("The project manager is coordinating the specialists…", expanded=True) as status:
                st.caption("The manager plans, delegates, and reviews. Stages are marked complete as CrewAI finishes each task.")
                progress_bar = st.progress(0, text="Waiting for the first task to complete")
                activity = st.empty()

                def render_progress() -> None:
                    lines = [
                        f"{'✓' if stage in completed else '○'}  {stage}"
                        for stage in stages
                    ]
                    activity.markdown("\n\n".join(lines))

                render_progress()
                started_at = monotonic()
                last_heartbeat = -1
                while worker.is_alive() or not progress_events.empty():
                    try:
                        stage = progress_events.get(timeout=0.35)
                    except Empty:
                        elapsed = int(monotonic() - started_at)
                        heartbeat = elapsed // 10
                        if heartbeat > last_heartbeat:
                            last_heartbeat = heartbeat
                            progress_bar.progress(
                                len(completed) / len(stages),
                                text=f"{len(completed)} of {len(stages)} tasks complete · {elapsed}s elapsed",
                            )
                        if elapsed >= 120 and not completed:
                            activity.warning("No task has finished yet. Check the terminal for model API or quota errors.")
                        continue
                    if stage in stages:
                        completed.add(stage)
                        progress_bar.progress(
                            len(completed) / len(stages),
                            text=f"{len(completed)} of {len(stages)} tasks complete",
                        )
                        render_progress()
                        status.update(label=f"Project workflow · {len(completed)}/{len(stages)} tasks complete")
                worker.join()

                if "error" in run_state:
                    status.update(label="The workflow stopped with an error", state="error")
                else:
                    progress_bar.progress(1.0, text="All tasks complete")
                    status.update(label="The delivery blueprint is ready", state="complete", expanded=False)

            if "error" in run_state:
                raise run_state["error"]  # surfaced in the user-facing error message below
            result = run_state["result"]

            st.markdown(
                '<div class="section-heading"><h2>Team deliverables</h2><p>Review each specialist’s contribution below.</p></div>',
                unsafe_allow_html=True,
            )
            tabs = st.tabs(["Project plan", "Engineering", "Product design", "Quality review"])
            for tab, task in zip(tabs, tasks):
                with tab:
                    st.caption(task.name)
                    output = getattr(task, "output", None)
                    st.markdown(str(output) if output else "No task output was returned.")
            with st.expander("View the integrated final response"):
                st.markdown(result.raw if hasattr(result, "raw") else str(result))
        except Exception as exc:
            error_text = str(exc)
            if "503" in error_text or "UNAVAILABLE" in error_text:
                st.error("Gemini is temporarily unavailable (503 UNAVAILABLE), so it could not finish this request.")
                st.info("This usually means temporary provider overload, not a quota response. Wait briefly and retry; you can change the model with `LLM_MODEL` in `.env`.")
            elif "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                st.error("The provider rate limit or quota was reached (429).")
                st.info("Wait for the limit to reset, or switch providers in `.env`.")
            else:
                st.error(f"The delivery workflow could not complete: {error_text}")
                st.info("Check that dependencies are installed and the selected provider and API key are configured in `.env`.")

st.divider()
st.caption("NORTHSTAR DELIVERY STUDIO  ·  CrewAI multi-agent project planning")
