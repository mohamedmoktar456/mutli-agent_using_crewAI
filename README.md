# CrewAI Multi-Agent Project Team

A Streamlit application that demonstrates a four-agent CrewAI engineering workflow. The Engineering Lead coordinates backend, frontend, and test engineers to produce a design, Python modules, a Gradio app, and unit tests.

## Team roles

1. **Engineering Lead** defines module boundaries and acceptance criteria, then delegates implementation work.
2. **Backend Engineer** writes the business logic in `backend.py`.
3. **Frontend Engineer** writes a Gradio interface in `app.py` that uses the backend module.
4. **Test Engineer** writes standard-library unit tests in `test_backend.py`.

Each run saves `design.md`, `backend.py`, `app.py`, and `test_backend.py` together under `output/Hierarchical/<run-id>/` or `output/Sequential/<run-id>/`, then adds `README.md`, `requirements.txt`, and `pyproject.toml` for `uv`. The app checks that the four agent deliverables exist and checks Python syntax. It shows the output folder path; it does not preview or download generated files. Tests are generated but are not executed automatically; no custom agent tools or sandbox execution are enabled.

## Requirements

- Python 3.10–3.13
- A Gemini API key for the included free-tier configuration; an OpenAI key is optional for alternate setups

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

Copy `.env.example` to `.env` and add the API keys for the providers configured in `delivery_team/crew_config/agents.yaml`. The YAML file is the only source for each agent's provider and model; `.env` supplies credentials only:

```env
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

Start the application:

```bash
streamlit run app.py
```

## Configure providers per agent

Edit the `llm` value for each agent in `delivery_team/crew_config/agents.yaml`. Use one of these `provider/model` formats:

| Provider | Example YAML `llm` |
|---|---|---|
| Gemini | `gemini/gemini-3.5-flash-lite` |
| OpenAI | `openai/gpt-5.4-mini` |

For example, to use OpenAI for the lead and Gemini for the engineers, configure the YAML like this:

```yaml
engineering_lead:
  llm: openai/gpt-5.4-mini
backend_engineer:
  llm: gemini/gemini-3.5-flash-lite
```

The app reads each model from YAML and matches it to `OPENAI_API_KEY` or `GEMINI_API_KEY` (`GOOGLE_API_KEY` also works for Gemini). Optional `<AGENT>_API_KEY` variables can supply separate credentials; provider and model environment overrides are not used. Keep API keys in `.env`, never in YAML.

Gemini 3.5 Flash-Lite is listed with free input and output on the Gemini API free tier, subject to usage quotas and project availability. OpenAI API calls use separate API billing and may fail if the organization has no credits.

## Workflow

Choose **Hierarchical**, **Sequential**, or **Compare both** in the form; the app requires an explicit choice. Hierarchical mode lets the Engineering Lead coordinate the specialists; Sequential mode runs the defined task order. Each run has an elapsed-time timer. Compare both runs the same brief twice, reports both durations, and saves files separately under `output/Hierarchical/<run-id>/` and `output/Sequential/<run-id>/`; it uses twice the model quota. Each folder's README and design.md also identify its workflow mode.

In either mode, the Engineering Lead writes `design.md` first as the execution contract: it defines module interfaces, assignments, and acceptance criteria. Each specialist receives that design as task context and has a fixed deliverable: Backend Engineer writes `backend.py`, Frontend Engineer writes `app.py` using the backend contract, and Test Engineer writes `test_backend.py` against the backend implementation. CrewAI saves each deliverable in the corresponding output folder.

For a quick first run, use the app's **Fill a quick example** button. It supplies a small to-do list project with no login or external integrations. Each task output is saved by CrewAI to its own file in the shared run directory.

## Code structure

```text
delivery_team/
├── config.py                 # Provider settings and LLM setup
├── team.py                   # Crew process selection and shared output workflow
└── crew_config/
    ├── agents.yaml            # All four engineering roles in one file
    └── tasks.yaml             # Design, backend, frontend, and test tasks
```

`crew.py` remains as a compatibility import, while the Streamlit app uses `delivery_team` directly.

All four agent definitions are kept together in `delivery_team/crew_config/agents.yaml`; their tasks are in `delivery_team/crew_config/tasks.yaml`. The application code reads both YAML files to assemble the selected crew process: Hierarchical or Sequential.

To run generated files, open the displayed mode-labeled folder under `output/` and run `uv sync` followed by `uv run python app.py`. You can also install `requirements.txt` with pip and run `python app.py`. Run generated backend tests manually with `python -m unittest -v test_backend.py`; the workflow does not execute generated code.

## Project files

- `app.py` — Streamlit interface and workflow results.
- `crew.py` — compatibility exports for the CrewAI workflow.
- `delivery_team/crew_config/agents.yaml` — all four engineering role definitions.
- `delivery_team/crew_config/tasks.yaml` — design, backend, frontend, and test tasks.
- `output/` — each run's complete project files, kept in its own subfolder.
- `.env.example` — OpenAI and Gemini environment template.
- `requirements.txt` — Python dependencies.
