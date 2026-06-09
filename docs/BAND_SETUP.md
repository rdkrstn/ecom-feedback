# Band Setup

## Prerequisites

- Band account
- Six Band Remote Agents
- Python environment with `uv`
- FastAPI running and reachable from each agent runner
- LLM provider key for real Band mode

## Create Remote Agents

Create these six remote agents in Band:

- Intake Review
- Customer Feedback Review
- UGC Review
- Support Review
- Product Page Review
- Action Review

Copy each Agent UUID and API key.

## agent_config.yaml

Create `agents/agent_config.yaml` from `agents/agent_config.example.yaml`:

```yaml
intake_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
customer_feedback_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
ugc_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
support_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
product_page_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
action_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
```

## .env

Create `agents/.env`:

```bash
THENVOI_REST_URL=https://app.band.ai/
THENVOI_WS_URL=wss://app.band.ai/api/v1/socket/websocket
PUBLIC_API_URL=http://localhost:8000
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
```

For AI/ML API, Featherless, or a custom OpenAI-compatible endpoint, set the matching provider variables from `.env.example`.

## Commands

```bash
cd agents
uv sync
uv run python -m sagad_feedback.band_agent --all
```

Run one agent:

```bash
uv run python -m sagad_feedback.band_agent --agent intake_review
```

## Manual Room Setup

1. Create a Band room manually.
2. Add all six remote agents.
3. Create a review in the web UI.
4. Copy the kickoff message.
5. Paste it into the Band room.

## Kickoff Message

```text
@Intake Review Start ecommerce feedback review.
review_id=<review_id>
api_url=<PUBLIC_API_URL_OR_LOCALHOST>
Start with Intake Review. Then hand off to @Customer Feedback Review.
Use JSON output and mention the next agent.
```

## @mentions

Band only routes work to a remote agent when the message mentions that agent. Every handoff message must include the next agent names with @mentions.

## Troubleshooting

- If agents connect but do not respond, confirm they are in the room and mentioned.
- If the SDK import fails, install the LangGraph SDK extra. The pasted brief uses `band-sdk[langgraph]`; current SDK docs may use `thenvoi-sdk[langgraph]`.
- If no UI events appear, confirm `PUBLIC_API_URL` points to the running FastAPI backend.
