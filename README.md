# SagadOS Feedback Review

Public hackathon title: Ecommerce Feedback Workflow

A multi-agent ecommerce workflow that turns support tickets, reviews, return reasons, and social comments into UGC briefs, support macros, FAQ updates, product page tasks, and internal owner handoffs.

## Problem

Ecommerce teams already collect useful customer feedback in support tickets, reviews, return reasons, surveys, social comments, and product page questions. That feedback often stays in support instead of becoming work for Content, Support, Storefront, and Operations.

SagadOS Feedback Review creates a structured Band workflow where specialized agents analyze the feedback, hand work to each other, and produce a final business action plan.

## Agents

- Intake Review
- Customer Feedback Review
- UGC Review
- Support Review
- Product Page Review
- Action Review

## Architecture

```text
Next.js demo UI
  -> FastAPI backend
  -> SQLite reviews and agent_events
  -> Local mock workflow
  -> Agent handlers and prompts

Band room
  -> six Remote Agents
  -> @mention routing through Band
  -> Python Band SDK runners
  -> /internal/agent-events mirror
  -> same UI timeline and final report
```

Band is the collaboration layer in real mode. It owns the shared room, @mentions, agent-to-agent handoffs, room history, and visible coordination. The local mock workflow mirrors the same six-step event order without requiring Band keys.

## Local Setup

Install frontend:

```bash
cd apps/web
pnpm install
pnpm dev
```

Install agents/backend:

```bash
cd agents
uv sync
uv run uvicorn sagad_feedback.api:app --reload --port 8000
```

Run local mock mode:

1. Open the web app.
2. Load sample data.
3. Create review.
4. Click Run local mock workflow.

## Real Band Mode

1. Create Band account.
2. Create six Remote Agents:
   - Intake Review
   - Customer Feedback Review
   - UGC Review
   - Support Review
   - Product Page Review
   - Action Review
3. Copy each Agent UUID and API key.
4. Create `agents/agent_config.yaml` from `agents/agent_config.example.yaml`.
5. Add LLM provider key to `agents/.env`.
6. Run:

```bash
cd agents
uv run python -m sagad_feedback.band_agent --all
```

7. Create a Band room manually.
8. Add all six remote agents.
9. Create a review in the web app.
10. Copy the kickoff message from the UI.
11. Paste it into the Band room.
12. Watch agents coordinate through Band and mirror outputs into the web UI.

The pasted brief references `band-sdk[langgraph]`. Current public SDK examples may use `thenvoi-sdk[langgraph]` while Python imports still come from `thenvoi`. The runner isolates this package boundary in `agents/src/sagad_feedback/band_agent.py`.

## Environment Variables

Root:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Agents:

```bash
THENVOI_REST_URL=https://app.band.ai/
THENVOI_WS_URL=wss://app.band.ai/api/v1/socket/websocket
PUBLIC_API_URL=http://localhost:8000
LLM_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
AIMLAPI_API_KEY=
AIMLAPI_BASE_URL=
AIMLAPI_MODEL=
FEATHERLESS_API_KEY=
FEATHERLESS_BASE_URL=
FEATHERLESS_MODEL=
CUSTOM_API_KEY=
CUSTOM_BASE_URL=
CUSTOM_MODEL=
```

## Commands

Run frontend:

```bash
cd apps/web
pnpm dev
```

Run backend:

```bash
cd agents
uv run uvicorn sagad_feedback.api:app --reload --port 8000
```

Run one agent:

```bash
cd agents
uv run python -m sagad_feedback.band_agent --agent intake_review
```

Run all agents:

```bash
cd agents
uv run python -m sagad_feedback.band_agent --all
```

Run tests:

```bash
cd agents
uv run pytest
```

## Where To Edit

- Agent prompts: `agents/src/sagad_feedback/prompts.py`
- AI provider logic: `agents/src/sagad_feedback/llm.py`
- Workflow order and dependencies: `agents/src/sagad_feedback/workflow.py`
- Agent business logic: `agents/src/sagad_feedback/agent_handlers.py`
- Deterministic mock logic: `agents/src/sagad_feedback/deterministic_logic.py`
- Band SDK behavior: `agents/src/sagad_feedback/band_agent.py` and `agents/src/sagad_feedback/band_gateway.py`
- Frontend UI: `apps/web/components`
- API client: `apps/web/lib/api.ts`
- Design tokens: `apps/web/app/globals.css`

## Demo Flow

1. Start FastAPI and Next.js.
2. Load the sample compression leggings data.
3. Create a review.
4. Run local mock workflow to show the six-agent event timeline.
5. Review the final action plan: UGC briefs, support macros, FAQ updates, product page tasks, and owner handoff.
6. Show the Band kickoff message and explain how real mode uses Band room @mentions.

## Hackathon Submission Text

Project Title: Ecommerce Feedback Workflow

Short Description: A Band-powered multi-agent workflow that turns ecommerce support tickets, reviews, return reasons, and customer comments into UGC briefs, support macros, FAQ updates, product page tasks, and owner handoffs.

Long Description: Ecommerce Feedback Workflow helps ecommerce teams turn scattered customer feedback into operational action. The system creates a shared Band review workflow where Intake Review structures the input, Customer Feedback Review identifies recurring customer issues, UGC Review turns customer language into creator briefs, Support Review creates macros and FAQ updates, Product Page Review converts objections into storefront tasks, and Action Review prioritizes the final handoff. The result is a practical internal workflow for ecommerce teams that keeps customer support, content, and storefront improvements connected.
