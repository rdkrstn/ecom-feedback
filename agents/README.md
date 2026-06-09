# SagadOS Feedback Review Agents

This folder contains the FastAPI backend, SQLite storage, deterministic mock workflow, OpenAI-compatible LLM adapter, CLI, and Band SDK runner.

## Run API

```bash
uv sync
uv run uvicorn sagad_feedback.api:app --reload --port 8000
```

## Run CLI

```bash
uv run python -m sagad_feedback.cli seed-demo
uv run python -m sagad_feedback.cli run-local <review_id>
uv run python -m sagad_feedback.cli reset-db
uv run python -m sagad_feedback.cli show-review <review_id>
```

## Run Band Agents

```bash
cp .env.example .env
cp agent_config.example.yaml agent_config.yaml
uv run python -m sagad_feedback.band_agent --all
```

Local mock mode does not require Band credentials or LLM keys.
