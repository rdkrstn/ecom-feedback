# Architecture

## Frontend

The frontend is a Next.js App Router application in `apps/web`. It renders one operational review screen with input, timeline, final action plan, and Band setup. It talks to FastAPI through `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://localhost:8000`.

## FastAPI Backend

The backend lives in `agents/src/sagad_feedback/api.py`. It creates reviews, returns events, runs the local workflow, receives mirrored Band agent events, and generates kickoff messages.

## SQLite Store

SQLite is created automatically at `agents/data/reviews.db`. It stores:

- `reviews`
- `agent_events`

The timeline and final report both read from these records.

## Local Mock Mode

Local mock mode uses deterministic logic in `deterministic_logic.py`. It works without LLM keys or Band credentials. It creates the same six event types that real Band mode mirrors into the UI.

## Real Band Mode

Real mode uses six Band Remote Agents. Each agent is added to a manually created Band room. A kickoff message mentions Intake Review with `review_id` and `api_url`. Each agent is woken by @mention, runs its role, posts a structured handoff in Band, and mirrors the event into FastAPI through `/internal/agent-events`.

## Agents

The six agents are:

- Intake Review
- Customer Feedback Review
- UGC Review
- Support Review
- Product Page Review
- Action Review

Each agent has a prompt in `prompts.py` and handler in `agent_handlers.py`.

## Event Mirror

The local UI does not replace Band. It mirrors the agent events that occur through Band so the demo can show a visible timeline and final report. The single mirror endpoint is `/internal/agent-events`.

## Why Band Is Central

Band provides the room, @mention routing, visible agent collaboration, agent identity, and shared coordination history. The backend stores review state, but Band is the collaboration surface for real mode.

## Why Human API Is Not Required

The project does not rely on Human API room creation. The user creates a Band room manually, adds six remote agents, copies a kickoff message from the UI, and pastes it into the room.
