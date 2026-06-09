from sagad_feedback.db import Database
from sagad_feedback.schemas import AgentEventCreate
from sagad_feedback.seed import SAMPLE_REVIEW_INPUT
from sagad_feedback.workflow import can_run_agent, run_local_workflow


def test_local_workflow_creates_six_events(tmp_path):
    db = Database(tmp_path / "reviews.db")
    review = db.create_review(SAMPLE_REVIEW_INPUT)

    completed = run_local_workflow(review.id, db=db)
    events = db.list_events(review.id)

    assert completed.status in {"completed", "changes_required"}
    assert len(events) == 6
    assert [event.agent_key for event in events] == [
        "intake_review",
        "customer_feedback_review",
        "ugc_review",
        "support_review",
        "product_page_review",
        "action_review",
    ]


def test_local_workflow_creates_final_report(tmp_path):
    db = Database(tmp_path / "reviews.db")
    review = db.create_review(SAMPLE_REVIEW_INPUT)

    completed = run_local_workflow(review.id, db=db)

    assert completed.final_report is not None
    assert completed.final_report.owner_handoff
    assert "sizing" in completed.final_report.primary_customer_issue.lower()


def test_action_review_only_completes_when_dependencies_exist():
    partial_events = [
        AgentEventCreate(
            review_id="review-1",
            agent_key="intake_review",
            agent_name="Intake Review",
            event_type="intake_summary",
            status="completed",
            summary="Intake complete",
            payload={},
            source_agents=[],
            handoff_to=["Customer Feedback Review"],
        )
    ]

    assert can_run_agent("action_review", partial_events) is False
