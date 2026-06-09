from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import get_db
from .schemas import AgentEvent, AgentEventCreate, FeedbackReviewInput, KickoffMessage, ReviewRecord
from .settings import get_public_api_url
from .workflow import finalize_review_if_action_done, run_local_workflow


app = FastAPI(title="SagadOS Feedback Review API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "sagad-feedback-review"}


@app.post("/reviews", response_model=ReviewRecord)
def create_review(payload: FeedbackReviewInput) -> ReviewRecord:
    return get_db().create_review(payload)


@app.get("/reviews/{review_id}", response_model=ReviewRecord)
def get_review(review_id: str) -> ReviewRecord:
    try:
        return get_db().get_review(review_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/reviews/{review_id}/events", response_model=list[AgentEvent])
def get_events(review_id: str) -> list[AgentEvent]:
    try:
        get_db().get_review(review_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return get_db().list_events(review_id)


@app.post("/reviews/{review_id}/run-local", response_model=ReviewRecord)
def run_review_local(review_id: str) -> ReviewRecord:
    try:
        return run_local_workflow(review_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/internal/agent-events", response_model=AgentEvent)
def mirror_agent_event(payload: AgentEventCreate) -> AgentEvent:
    database = get_db()
    try:
        database.get_review(payload.review_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    event = database.create_event(payload)
    if payload.event_type == "final_action_plan":
        finalize_review_if_action_done(payload.review_id, database)
    elif payload.status == "waiting":
        database.update_review(payload.review_id, status="waiting_for_band")
    else:
        database.update_review(payload.review_id, status="running")
    return event


@app.get("/reviews/{review_id}/kickoff-message", response_model=KickoffMessage)
def get_kickoff_message(review_id: str) -> KickoffMessage:
    try:
        get_db().get_review(review_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    api_url = get_public_api_url()
    message = (
        "@Intake Review Start ecommerce feedback review.\n"
        f"review_id={review_id}\n"
        f"api_url={api_url}\n"
        "Start with Intake Review. Then hand off to @Customer Feedback Review.\n"
        "Use JSON output and mention the next agent."
    )
    return KickoffMessage(review_id=review_id, kickoff_message=message)


@app.post("/demo/reset")
def reset_demo() -> dict:
    get_db().reset()
    return {"ok": True}
