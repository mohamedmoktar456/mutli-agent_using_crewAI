"""Streamlit interface for the CrewAI four-agent project team."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from crew import build_crew

load_dotenv()
st.set_page_config(page_title="CrewAI Project Team", page_icon="🤖", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero { padding: 2rem 2.2rem; border-radius: 22px; background: linear-gradient(125deg,#101b3d,#2357a5 65%,#36a6b5); color:white; margin-bottom:1.2rem; }
.hero h1 { font-size:2.4rem; margin:0; color:white; }
.hero p { font-size:1.05rem; opacity:.9; margin:.6rem 0 0; }
.agent-card { background:#f3f6fb; border:1px solid #e2e8f0; border-radius:16px; padding:1rem 1.1rem; min-height:145px; }
.agent-card h3 { margin:0 0 .35rem; font-size:1.05rem; color:#172b4d; }
.agent-card p { margin:0; color:#52627a; font-size:.9rem; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>🤖 Your AI Project Team</h1>'
    "<p>Four specialized agents work together to turn your idea into a coordinated plan, design, and quality review.</p></div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Model settings")
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    st.caption(f"Provider from `.env`: **{provider}**")
    st.caption(f"Model: **{model or 'provider default'}**")
    st.info("To change providers, edit `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY` in `.env`, then restart the app.")
    st.caption("Supported: OpenAI · Gemini · Anthropic · Ollama · OpenRouter")
    st.divider()
    st.caption("Workflow: Plan → Backend → UI/UX → Quality review")

st.markdown("### 👥 Meet the team")
cols = st.columns(4)
cards = [
    ("🧭", "Project Manager", "Analyzes requirements, plans the work, and defines acceptance criteria."),
    ("⚙️", "Backend Developer", "Designs the business logic, data model, and API architecture."),
    ("🎨", "UI/UX Designer", "Plans screens, interactions, and a clear user experience."),
    ("🧪", "QA Engineer", "Reviews the work, defines checks, and identifies risks and gaps."),
]
for col, (icon, title, description) in zip(cols, cards):
    with col:
        st.markdown(
            f'<div class="agent-card"><h3>{icon} {title}</h3><p>{description}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown("### 🚀 Describe your project")
with st.form("project_form"):
    brief = st.text_area(
        "What would you like to build?",
        placeholder=(
            "Example: I want a task management app for a small team, with sign-in, task lists, "
            "assignees, due dates, and a progress dashboard..."
        ),
        height=145,
        help="Describe the idea, required features, and any technical preferences you have.",
    )
    submitted = st.form_submit_button(
        "✨ Start the team workflow", type="primary", use_container_width=True
    )

if submitted:
    if not brief.strip():
        st.warning("Enter a project description before starting the team.")
    else:
        try:
            crew, agents, tasks = build_crew(brief)
            status = st.status("The four-agent workflow is running…", expanded=True)
            with st.spinner("The agents are collaborating. This may take a few minutes…"):
                result = crew.kickoff(inputs={"project_brief": brief.strip()})
            status.update(label="The team has completed its review", state="complete", expanded=False)
            st.markdown("### 📋 Team results")
            st.markdown(result.raw if hasattr(result, "raw") else str(result))
            with st.expander("Task outputs and agent roles"):
                for agent, task in zip(agents, tasks):
                    st.markdown(f"**{agent.role}** — {task.expected_output}")
                    output = getattr(task, "output", None)
                    if output:
                        st.write(str(output))
        except Exception as exc:
            st.error(f"The team could not run: {exc}")
            st.info("Check that dependencies are installed and the provider and API key are configured in `.env`.")

st.divider()
st.markdown(
    '<div style="text-align:center;color:#8391a7">Built with CrewAI · Four roles · A coordinated workflow · Switchable LLM provider</div>',
    unsafe_allow_html=True,
)
