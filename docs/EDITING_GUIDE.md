# Editing Guide

| What to change | File | Notes |
| --- | --- | --- |
| Agent prompts | `agents/src/sagad_feedback/prompts.py` | Edit role, output, handoff behavior |
| Agent business logic | `agents/src/sagad_feedback/agent_handlers.py` | Edit each agent's processing |
| Workflow order | `agents/src/sagad_feedback/workflow.py` | Edit dependencies and handoff sequence |
| AI provider | `agents/src/sagad_feedback/llm.py` | Add OpenAI, AI/ML API, Featherless, custom base URL |
| Mock logic | `agents/src/sagad_feedback/deterministic_logic.py` | Edit keyword rules and fallback output |
| Band SDK behavior | `agents/src/sagad_feedback/band_agent.py` and `agents/src/sagad_feedback/band_gateway.py` | Edit real agent connection and message posting |
| API routes | `agents/src/sagad_feedback/api.py` | Edit backend endpoints |
| Database | `agents/src/sagad_feedback/db.py` | Edit SQLite schema |
| Frontend API client | `apps/web/lib/api.ts` | Edit API calls |
| Frontend UI | `apps/web/components` | Edit display components |
| Design tokens | `apps/web/app/globals.css` | Edit colors, borders, typography |
