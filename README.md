# CrewAI Multi-Agent Project Team

A Streamlit application that demonstrates a four-agent CrewAI engineering workflow. The Engineering Lead coordinates backend, frontend, and test engineers to produce a design, Python modules, a Gradio app, and unit tests.

## Team roles

1. **Engineering Lead** defines module boundaries and acceptance criteria, then delegates implementation work.
2. **Backend Engineer** writes the business logic in `backend.py`.
3. **Frontend Engineer** writes a Gradio interface in `app.py` that uses the backend module.
4. **Test Engineer** writes standard-library unit tests in `test_backend.py`.

Each run saves `design.md`, `backend.py`, `app.py`, and `test_backend.py` together under its own `output/<run-id>/` folder, then adds `README.md`, `requirements.txt`, and `pyproject.toml` for `uv`. The app checks that the four agent deliverables exist, checks Python syntax, lists the saved files, and offers a ZIP download. Tests are generated but are not executed automatically; no custom agent tools or sandbox execution are enabled.

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

Copy `.env.example` to `.env` and add your OpenAI and Gemini keys. Each agent's default model is in `delivery_team/crew_config/agents.yaml`; `.env` provides provider/model overrides and fallback settings. The Engineering Lead and Backend Engineer use OpenAI in the example, while Frontend and Test use Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-3.5-flash-lite
ENGINEERING_LEAD_PROVIDER=openai
BACKEND_ENGINEER_PROVIDER=openai
FRONTEND_ENGINEER_PROVIDER=gemini
TEST_ENGINEER_PROVIDER=gemini
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

Start the application:

```bash
streamlit run app.py
```

## Assign providers per agent

Set an agent-specific provider in `.env`. Supported agent names are `ENGINEERING_LEAD`, `BACKEND_ENGINEER`, `FRONTEND_ENGINEER`, and `TEST_ENGINEER`:

| Provider | Value for `*_PROVIDER` or YAML `llm` | Example model |
|---|---|---|
| Gemini | `gemini` | `gemini/gemini-3.5-flash-lite` |
| OpenAI | `openai` | `openai/gpt-4o-mini` |

For example, assign OpenAI to the Engineering Lead and Backend Engineer, and Gemini to the Frontend and Test Engineers:

```env
LLM_PROVIDER=gemini
BACKEND_ENGINEER_PROVIDER=openai
ENGINEERING_LEAD_PROVIDER=openai
FRONTEND_ENGINEER_PROVIDER=gemini
TEST_ENGINEER_PROVIDER=gemini
```

CrewAI's `llm` field in `agents.yaml` defines each role's default provider and model. Each role can override it through `<AGENT>_PROVIDER` or `<AGENT>_MODEL`; for example, `BACKEND_ENGINEER_MODEL=openai/gpt-5.4-mini`. If an agent has no YAML or role-specific setting, it inherits `LLM_PROVIDER` and `LLM_MODEL`. The app selects `OPENAI_API_KEY` or `GEMINI_API_KEY`/`GOOGLE_API_KEY` to match each role's provider. API keys remain in `.env`, not YAML. A shared `LLM_API_KEY` is used only for roles that use the global provider. The project supports OpenAI and Gemini.

Gemini offers a limited free tier for eligible models and accounts; quotas and model access apply. OpenAI API calls are billed according to your OpenAI API account's pricing and credits. A key by itself does not guarantee free usage, so check billing before selecting OpenAI if you must avoid charges.

## Workflow

The crew uses `Process.hierarchical`. First, the Engineering Lead writes `design.md` as the execution contract: it defines module interfaces, assignments, and acceptance criteria. Each specialist receives that design as task context and has a fixed deliverable: Backend Engineer writes `backend.py`, Frontend Engineer writes `app.py` using the backend contract, and Test Engineer writes `test_backend.py` against the backend implementation. CrewAI saves each deliverable in the same `output/<run-id>/` folder.

For a quick first run, use the app's **Fill a quick example** button. It supplies a small to-do list project with no login or external integrations. Each task output is saved by CrewAI to its own file in the shared run directory.

## Code structure

```text
delivery_team/
├── config.py                 # Provider settings and LLM setup
├── team.py                   # Hierarchical crew and shared output workflow
└── crew_config/
    ├── agents.yaml            # All four engineering roles in one file
    └── tasks.yaml             # Design, backend, frontend, and test tasks
```

`crew.py` remains as a compatibility import, while the Streamlit app uses `delivery_team` directly.

All four agent definitions are kept together in `delivery_team/crew_config/agents.yaml`; their tasks are in `delivery_team/crew_config/tasks.yaml`. The application code reads both YAML files to assemble the hierarchical crew.

To run generated files, open the displayed `output/<run-id>/` folder and run `uv sync` followed by `uv run python app.py`. You can also install `requirements.txt` with pip and run `python app.py`. Run generated backend tests manually with `python -m unittest -v test_backend.py`; the workflow does not execute generated code.

## Project files

- `app.py` — Streamlit interface and workflow results.
- `crew.py` — compatibility exports for the CrewAI workflow.
- `delivery_team/crew_config/agents.yaml` — all four engineering role definitions.
- `delivery_team/crew_config/tasks.yaml` — design, backend, frontend, and test tasks.
- `output/` — each run's complete project files and downloadable archive, kept in its own subfolder.
- `.env.example` — OpenAI and Gemini environment template.
- `requirements.txt` — Python dependencies.
