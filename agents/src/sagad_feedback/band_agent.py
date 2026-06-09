from __future__ import annotations

import argparse
import asyncio
import logging
import os
from pathlib import Path
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv

from .agent_handlers import HANDLERS
from .band_gateway import BandMessageBuilder, BandSDKUnavailable, LocalBandMirror
from .llm import get_langchain_model_kwargs
from .prompts import PROMPTS_BY_AGENT
from .schemas import AgentEvent, ReviewRecord
from .settings import AGENTS_DIR
from .utils import AGENTS, AGENT_KEYS


LOGGER = logging.getLogger("sagad_feedback.band_agent")
SDK_INSTALL_MESSAGE = 'Band SDK not installed. Run: uv add "band-sdk[langgraph]"'


def load_sdk_objects() -> dict[str, Any]:
    try:
        from langchain_core.tools import tool
        from langchain_openai import ChatOpenAI
        from langgraph.checkpoint.memory import InMemorySaver
        from thenvoi import Agent
        from thenvoi.adapters import LangGraphAdapter

        try:
            from thenvoi.config import load_agent_config
        except Exception:
            load_agent_config = None
    except ImportError as exc:
        raise BandSDKUnavailable(SDK_INSTALL_MESSAGE) from exc
    return {
        "tool": tool,
        "ChatOpenAI": ChatOpenAI,
        "InMemorySaver": InMemorySaver,
        "Agent": Agent,
        "LangGraphAdapter": LangGraphAdapter,
        "load_agent_config": load_agent_config,
    }


def load_local_agent_config(config_path: Path) -> dict[str, dict[str, str]]:
    if not config_path.exists():
        raise FileNotFoundError(f"agent_config.yaml missing. Copy agent_config.example.yaml to {config_path.name}.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    missing = [key for key in AGENT_KEYS if key not in data]
    if missing:
        raise ValueError(f"agent_config.yaml is missing keys: {', '.join(missing)}")
    for key in AGENT_KEYS:
        if not data[key].get("agent_id") or not data[key].get("api_key"):
            raise ValueError(f"agent_config.yaml missing agent_id or api_key for {key}")
    return data


def build_review_handler_tool(agent_key: str, sdk_tool):
    @sdk_tool("run_sagad_feedback_review")
    def run_sagad_feedback_review(review_id: str, api_url: str) -> str:
        """Fetch the review, run this agent's handler, mirror the event, and return the Band message to post."""
        api_base = api_url.rstrip("/")
        with httpx.Client(timeout=30) as client:
            review_response = client.get(f"{api_base}/reviews/{review_id}")
            review_response.raise_for_status()
            events_response = client.get(f"{api_base}/reviews/{review_id}/events")
            events_response.raise_for_status()
        review = ReviewRecord.model_validate(review_response.json())
        events = [AgentEvent.model_validate(item) for item in events_response.json()]
        event = HANDLERS[agent_key](review, events)
        LocalBandMirror.mirror_event_sync(api_base, event)
        LOGGER.info("Posted event to local mirror for %s", event.agent_name)
        return BandMessageBuilder.build_agent_message(event)

    return run_sagad_feedback_review


def build_custom_section(agent_key: str) -> str:
    agent_name = AGENTS[agent_key]
    return f"""
You are {agent_name} in SagadOS Feedback Review.

Use this project prompt:
{PROMPTS_BY_AGENT[agent_key]}

When a Band room message mentions @{agent_name} and includes review_id and api_url:
1. Call the run_sagad_feedback_review tool with the exact review_id and api_url.
2. The tool will fetch FastAPI review data, run {agent_name}'s local handler, and mirror the event into the web UI.
3. Post the exact message returned by the tool into the same Band room using thenvoi_send_message.
4. Include every handoff @mention from the returned message.

Do not create a final action plan unless you are Action Review.
Do not claim Shopify, Zendesk, TikTok, Instagram, or other systems are connected.
"""


def create_band_agent(agent_key: str, config: dict[str, dict[str, str]], sdk: dict[str, Any]):
    ChatOpenAI = sdk["ChatOpenAI"]
    InMemorySaver = sdk["InMemorySaver"]
    Agent = sdk["Agent"]
    LangGraphAdapter = sdk["LangGraphAdapter"]
    sdk_tool = sdk["tool"]
    load_agent_config = sdk["load_agent_config"]

    model_kwargs = get_langchain_model_kwargs()
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(**model_kwargs),
        checkpointer=InMemorySaver(),
        custom_section=build_custom_section(agent_key),
        additional_tools=[build_review_handler_tool(agent_key, sdk_tool)],
    )

    rest_url = os.getenv("THENVOI_REST_URL") or None
    ws_url = os.getenv("THENVOI_WS_URL") or None
    if load_agent_config:
        try:
            load_agent_config("agent_config.yaml")
        except TypeError:
            load_agent_config()
        except Exception:
            LOGGER.debug("SDK config loader was present but local YAML validation already handled config.", exc_info=True)

    if hasattr(Agent, "from_config"):
        return Agent.from_config(agent_key, adapter=adapter, rest_url=rest_url, ws_url=ws_url)

    agent_config = config[agent_key]
    return Agent.create(
        adapter=adapter,
        agent_id=agent_config["agent_id"],
        api_key=agent_config["api_key"],
        rest_url=rest_url,
        ws_url=ws_url,
    )


async def run_agent(agent_key: str, config: dict[str, dict[str, str]], sdk: dict[str, Any]) -> None:
    LOGGER.info("Starting %s Band agent", AGENTS[agent_key])
    agent = create_band_agent(agent_key, config, sdk)
    LOGGER.info("Connected to Band as %s", AGENTS[agent_key])
    LOGGER.info("Waiting for @mentions")
    await agent.run()


async def async_main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO)
    env_path = AGENTS_DIR / ".env"
    if not env_path.exists():
        raise FileNotFoundError("agents/.env missing. Copy .env.example to .env for real Band mode.")
    load_dotenv(env_path)
    config_path = AGENTS_DIR / "agent_config.yaml"
    config = load_local_agent_config(config_path)
    sdk = load_sdk_objects()

    selected = AGENT_KEYS if args.all else [args.agent]
    tasks = [asyncio.create_task(run_agent(agent_key, config, sdk)) for agent_key in selected]
    await asyncio.gather(*tasks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SagadOS Feedback Review Band agents")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--agent", choices=AGENT_KEYS)
    group.add_argument("--all", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(async_main(args))
    except BandSDKUnavailable as exc:
        print(str(exc))
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        print("Stopped Band agent runner.")
    except Exception as exc:
        print(f"Band agent runner failed: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
