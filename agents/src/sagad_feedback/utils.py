from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


AGENTS: dict[str, str] = {
    "intake_review": "Intake Review",
    "customer_feedback_review": "Customer Feedback Review",
    "ugc_review": "UGC Review",
    "support_review": "Support Review",
    "product_page_review": "Product Page Review",
    "action_review": "Action Review",
}

AGENT_KEYS = list(AGENTS.keys())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_snippets(items: Iterable[str], limit: int = 5) -> list[str]:
    seen: set[str] = set()
    snippets: list[str] = []
    for item in items:
        cleaned = " ".join(str(item).strip(" -\t\r\n").split())
        if not cleaned or cleaned.lower() in seen:
            continue
        seen.add(cleaned.lower())
        snippets.append(cleaned[:220])
        if len(snippets) >= limit:
            break
    return snippets


def mention(agent_name: str) -> str:
    return agent_name if agent_name.startswith("@") else f"@{agent_name}"
