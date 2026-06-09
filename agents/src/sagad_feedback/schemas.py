from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal[
    "draft",
    "running",
    "waiting_for_band",
    "changes_required",
    "completed",
    "failed",
]

EventType = Literal[
    "intake_summary",
    "feedback_analysis",
    "ugc_briefs",
    "support_assets",
    "product_page_tasks",
    "final_action_plan",
    "handoff",
    "error",
    "waiting",
]

Priority = Literal["low", "medium", "high"]
Frequency = Literal["low", "medium", "high"]
Owner = Literal["Content", "Support", "Storefront", "Operations"]


class FeedbackReviewInput(BaseModel):
    product_name: str
    product_category: str
    product_description: str | None = None
    support_tickets: str
    customer_reviews: str
    return_reasons: str | None = None
    social_comments: str | None = None
    current_faq: str | None = None
    product_page_copy: str | None = None
    main_business_concern: str | None = None


class DetectedIssue(BaseModel):
    issue: str
    frequency: Frequency
    source_types: list[str] = Field(default_factory=list)
    customer_language: list[str] = Field(default_factory=list)
    business_impact: list[str] = Field(default_factory=list)
    recommended_action: str


class UGCBrief(BaseModel):
    title: str
    goal: str
    source_issue: str
    creator_instructions: list[str] = Field(default_factory=list)
    hooks: list[str] = Field(default_factory=list)
    shot_list: list[str] = Field(default_factory=list)
    proof_needed: list[str] = Field(default_factory=list)


class SupportMacro(BaseModel):
    name: str
    use_case: str
    body: str
    related_issue: str


class FAQUpdate(BaseModel):
    question: str
    answer: str
    related_issue: str


class ProductPageTask(BaseModel):
    section: str
    task: str
    reason: str
    related_issue: str
    priority: Priority


class OwnerTask(BaseModel):
    owner: Owner
    task: str
    priority: Priority
    source_agent: str
    related_issue: str


class FinalReport(BaseModel):
    status: Literal["changes_required", "completed"]
    primary_customer_issue: str
    priority: Priority
    executive_summary: str
    detected_issues: list[DetectedIssue] = Field(default_factory=list)
    ugc_briefs: list[UGCBrief] = Field(default_factory=list)
    support_macros: list[SupportMacro] = Field(default_factory=list)
    faq_updates: list[FAQUpdate] = Field(default_factory=list)
    product_page_tasks: list[ProductPageTask] = Field(default_factory=list)
    owner_handoff: list[OwnerTask] = Field(default_factory=list)
    source_evidence: list[str] = Field(default_factory=list)
    next_review_recommendation: str


class ReviewRecord(BaseModel):
    id: str
    input: FeedbackReviewInput
    status: ReviewStatus
    final_report: FinalReport | None = None
    created_at: str
    updated_at: str


class AgentEventCreate(BaseModel):
    review_id: str
    agent_key: str
    agent_name: str
    event_type: EventType
    status: str
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source_agents: list[str] = Field(default_factory=list)
    handoff_to: list[str] = Field(default_factory=list)
    band_room_id: str | None = None
    band_message_id: str | None = None


class AgentEvent(AgentEventCreate):
    id: str
    created_at: str


class KickoffMessage(BaseModel):
    review_id: str
    kickoff_message: str
