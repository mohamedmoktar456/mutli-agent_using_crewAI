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
- An API key for the selected hosted LLM provider, or a locally running Ollama model

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

Copy `.env.example` to `.env` and add the API key for your chosen provider:

```env
LLM_PROVIDER=openai
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=your-api-key-here
```

Start the application:

```bash
streamlit run app.py
```

## Switching providers

The app uses CrewAI's LLM interface with its provider integrations. Set `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY` in `.env`:

| Provider | `LLM_PROVIDER` | Example model |
|---|---|---|
| OpenAI | `openai` | `openai/gpt-4o-mini` |
| Google Gemini | `gemini` | `gemini/gemini-3.5-flash-lite` |
| Anthropic | `anthropic` | `anthropic/claude-haiku-4-5-20251001` |
| Ollama | `ollama` | `ollama/llama3.1` |
| OpenRouter | `openrouter` | `openrouter/openai/gpt-4o-mini` |

For example, to switch to Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-3.5-flash-lite
LLM_API_KEY=your-gemini-api-key
```

`LLM_API_KEY` is the provider-independent key setting. If it is empty, the app looks for the provider-specific environment variable (such as `GEMINI_API_KEY` or `OPENAI_API_KEY`). `LLM_BASE_URL` is optional and can point to a compatible endpoint or a local Ollama server. The requirements include CrewAI's OpenAI, Anthropic, Google Gen AI, and LiteLLM extras to support the provider choices above.

## Workflow

The crew uses `Process.sequential`. The project manager completes the plan first, the backend developer uses that plan, the UI/UX designer uses both previous outputs, and the QA engineer reviews the full set. Each task receives the original project brief and the outputs it depends on.

## Project files

- `app.py` — Streamlit interface and workflow results.
- `crew.py` — provider configuration, agents, tasks, and crew setup.
- `.env.example` — environment configuration template.
- `requirements.txt` — Python dependencies.
