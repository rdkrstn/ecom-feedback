from __future__ import annotations

from .agent_handlers import HANDLERS
from .db import Database, get_db
from .schemas import AgentEvent, AgentEventCreate, ReviewRecord
from .utils import AGENTS


LOCAL_WORKFLOW_ORDER = [
    "intake_review",
    "customer_feedback_review",
    "ugc_review",
    "support_review",
    "product_page_review",
    "action_review",
]

DEPENDENCIES = {
    "intake_review": [],
    "customer_feedback_review": ["intake_summary"],
    "ugc_review": ["feedback_analysis"],
    "support_review": ["feedback_analysis"],
    "product_page_review": ["feedback_analysis", "ugc_briefs", "support_assets"],
    "action_review": ["feedback_analysis", "ugc_briefs", "support_assets", "product_page_tasks"],
}

DEPENDENCY_OWNERS = {
    "intake_summary": "Intake Review",
    "feedback_analysis": "Customer Feedback Review",
    "ugc_briefs": "UGC Review",
    "support_assets": "Support Review",
    "product_page_tasks": "Product Page Review",
}


def get_required_dependencies(agent_key: str) -> list[str]:
    return DEPENDENCIES.get(agent_key, [])


def can_run_agent(agent_key: str, events: list[AgentEvent | AgentEventCreate]) -> bool:
    completed = {event.event_type for event in events if event.status in {"completed", "changes_required"}}
    return all(dep in completed for dep in get_required_dependencies(agent_key))


def create_waiting_event(review_id: str, agent_key: str, missing_dependencies: list[str]) -> AgentEventCreate:
    missing_agents = [DEPENDENCY_OWNERS.get(dep, dep) for dep in missing_dependencies]
    return AgentEventCreate(
        review_id=review_id,
        agent_key=agent_key,
        agent_name=AGENTS[agent_key],
        event_type="waiting",
        status="waiting",
        summary=f"{AGENTS[agent_key]} is waiting for {', '.join(missing_dependencies)}.",
        payload={"missing_dependencies": missing_dependencies},
        source_agents=[],
        handoff_to=missing_agents,
    )


def finalize_review_if_action_done(review_id: str, db: Database | None = None) -> ReviewRecord:
    database = db or get_db()
    review = database.get_review(review_id)
    events = database.list_events(review_id)
    action_event = next((event for event in reversed(events) if event.event_type == "final_action_plan"), None)
    if action_event and "final_report" in action_event.payload:
        return database.update_review(
            review_id,
            status=action_event.payload.get("status", "completed"),
            final_report=action_event.payload["final_report"],
        )
    return review


def run_local_workflow(review_id: str, db: Database | None = None) -> ReviewRecord:
    database = db or get_db()
    database.update_review(review_id, status="running")
    for agent_key in LOCAL_WORKFLOW_ORDER:
        review = database.get_review(review_id)
        events = database.list_events(review_id)
        missing = [
            dep
            for dep in get_required_dependencies(agent_key)
            if dep not in {event.event_type for event in events if event.status in {"completed", "changes_required"}}
        ]
        if missing:
            database.create_event(create_waiting_event(review_id, agent_key, missing))
            database.update_review(review_id, status="waiting_for_band")
            continue
        event = HANDLERS[agent_key](review, events)
        database.create_event(event)
        database.update_review(review_id, status="running")
    return finalize_review_if_action_done(review_id, database)
