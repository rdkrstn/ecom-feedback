from __future__ import annotations

import json

import httpx

from .schemas import AgentEventCreate
from .utils import mention


class BandSDKUnavailable(Exception):
    pass


class LocalBandMirror:
    @staticmethod
    async def mirror_event(api_url: str, event: AgentEventCreate) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{api_url.rstrip('/')}/internal/agent-events",
                json=event.model_dump(mode="json"),
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def mirror_event_sync(api_url: str, event: AgentEventCreate) -> dict:
        with httpx.Client(timeout=20) as client:
            response = client.post(
                f"{api_url.rstrip('/')}/internal/agent-events",
                json=event.model_dump(mode="json"),
            )
            response.raise_for_status()
            return response.json()


class BandMessageBuilder:
    @staticmethod
    def build_handoff_mentions(handoff_to: list[str]) -> str:
        return " ".join(mention(agent) for agent in handoff_to)

    @staticmethod
    def build_agent_message(event: AgentEventCreate) -> str:
        mentions = BandMessageBuilder.build_handoff_mentions(event.handoff_to)
        handoff = f" Handing off to {mentions}." if mentions else ""
        readable = (
            f"{event.agent_name} completed. Main issue: {event.summary}.{handoff}"
            if event.status != "waiting"
            else f"{event.agent_name} is waiting. {event.summary}. {mentions}"
        )
        payload = {
            "review_id": event.review_id,
            "agent_key": event.agent_key,
            "status": event.status,
            "summary": event.summary,
            "source_agents": event.source_agents,
            "handoff_to": event.handoff_to,
            "payload": event.payload,
        }
        return f"{readable}\n\n```json\n{json.dumps(payload, indent=2)}\n```"
