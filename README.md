# CrewAI Multi-Agent Project Team

A Streamlit application that demonstrates a four-agent CrewAI workflow. Describe a project idea and the team produces a coordinated project plan, backend design, UI/UX specification, and quality review.

## Team roles

1. **Project Manager** analyzes the brief, defines scope and assumptions, and creates the work plan and acceptance criteria.
2. **Backend Developer** proposes the application architecture, data model, business logic, and API design.
3. **UI/UX Designer** describes screens, interactions, interface states, and accessibility considerations.
4. **QA Engineer** reviews the preceding work and identifies acceptance checks, risks, and gaps.

The application generates a project specification and review. It does not generate or deploy a finished application codebase.

## Requirements

- Python 3.10–3.13
- An OpenAI or Gemini API key

## Setup

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI and Gemini keys. It defaults to Gemini and uses whichever provider is selected in `LLM_PROVIDER`:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-3.5-flash-lite
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

Start the application:

```bash
streamlit run app.py
```

## Switch between OpenAI and Gemini

Change `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY` in `.env`:

| Provider | `LLM_PROVIDER` | Example model |
|---|---|---|
| Gemini | `gemini` | `gemini/gemini-3.5-flash-lite` |
| OpenAI | `openai` | `openai/gpt-4o-mini` |

To use OpenAI, set:

```env
LLM_PROVIDER=openai
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=your-openai-api-key-here
```

The app uses `GEMINI_API_KEY` for Gemini and `OPENAI_API_KEY` for OpenAI. You can use a single generic `LLM_API_KEY` instead. The project only supports OpenAI and Gemini API providers.

Gemini offers a limited free tier for eligible models and accounts; quotas and model access apply. OpenAI API calls are billed according to your OpenAI API account's pricing and credits. A key by itself does not guarantee free usage, so check billing before selecting OpenAI if you must avoid charges.

## Workflow

The crew uses `Process.hierarchical`. The project manager is the CrewAI manager agent: it prepares the project plan, delegates engineering, product design, and quality work to the specialists, and coordinates the final review. Specialist tasks are not hard-wired to a specific worker; the manager assigns them based on role and task requirements.

For a quick first run, use the app's **Fill a quick example** button. It supplies a small to-do list project with no login or external integrations. Agent responses are kept short, and execution limits stop unusually long agent runs.

## Code structure

```text
delivery_team/
├── config.py                 # Provider settings and LLM setup
├── team.py                   # Hierarchical crew and task assembly
└── agents/
    ├── base.py               # Shared specialist agent behavior
    ├── project_manager.py    # Planning and coordination role
    ├── backend_engineer.py   # Systems and backend engineering role
    ├── product_designer.py   # Product and UI/UX role
    └── quality_engineer.py   # QA and test engineering role
```

Each specialist lives in its own file. `crew.py` remains as a compatibility import, while the Streamlit app uses `delivery_team` directly.

The engineering output is a detailed design and implementation blueprint. The agents do not create or deploy application source code.

## Project files

- `app.py` — Streamlit interface and workflow results.
- `crew.py` — provider configuration, agents, tasks, and crew setup.
- `.env.example` — OpenAI and Gemini environment template.
- `requirements.txt` — Python dependencies.
