# Troubleshooting

## Band SDK missing

Install the LangGraph SDK extra. The pasted brief uses:

```bash
uv add "band-sdk[langgraph]"
```

Current public examples may use:

```bash
uv add "thenvoi-sdk[langgraph]"
```

The Python import remains `thenvoi`.

## agent_config.yaml missing

Copy the example file:

```bash
cd agents
cp agent_config.example.yaml agent_config.yaml
```

Then add the six Band Agent UUIDs and API keys.

## Invalid Band API key

Regenerate the key in Band, update `agent_config.yaml`, and restart the agent runner.

## OpenAI key missing

Local mock mode still works. For real Band mode, add an OpenAI-compatible key to `agents/.env`.

## No events showing in UI

Confirm FastAPI is running on `http://localhost:8000`, `PUBLIC_API_URL` points to it, and Band agents can reach that URL.

## CORS issue

The FastAPI app allows all origins for hackathon demo use. If you restrict CORS, add the Next.js origin.

## Frontend cannot reach backend

Set this in root `.env.local` or your shell:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## SQLite file permissions

Delete `agents/data/reviews.db` if it was created with the wrong permissions, then restart FastAPI.

## Agents not responding because they were not @mentioned

Band routes messages to remote agents through @mentions. Include `@Intake Review` in the kickoff and every downstream agent mention in handoffs.
