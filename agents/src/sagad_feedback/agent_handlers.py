from __future__ import annotations

from typing import Callable

from .deterministic_logic import (
    build_faq_updates,
    build_final_report,
    build_product_page_tasks,
    build_support_macros,
    build_ugc_briefs,
    detect_issues,
    split_feedback_lines,
)
from .llm import LLMClient
from .prompts import (
    ACTION_REVIEW_PROMPT,
    CUSTOMER_FEEDBACK_REVIEW_PROMPT,
    INTAKE_REVIEW_PROMPT,
    PRODUCT_PAGE_REVIEW_PROMPT,
    SUPPORT_REVIEW_PROMPT,
    UGC_REVIEW_PROMPT,
)
from .schemas import AgentEvent, AgentEventCreate, FinalReport, ReviewRecord
from .utils import AGENTS


def _event(
    review: ReviewRecord,
    agent_key: str,
    event_type: str,
    summary: str,
    payload: dict,
    source_agents: list[str],
    handoff_to: list[str],
    status: str = "completed",
) -> AgentEventCreate:
    return AgentEventCreate(
        review_id=review.id,
        agent_key=agent_key,
        agent_name=AGENTS[agent_key],
        event_type=event_type,
        status=status,
        summary=summary,
        payload=payload,
        source_agents=source_agents,
        handoff_to=handoff_to,
    )


def _llm_or_fallback(
    llm: LLMClient | None,
    prompt: str,
    user_payload: dict,
    fallback_fn: Callable[[], dict],
) -> dict:
    client = llm or LLMClient()
    result = client.generate_json(prompt, user_payload, fallback_fn)
    return result if isinstance(result, dict) else result.model_dump(mode="json")


def _prior_payloads(events: list[AgentEvent]) -> dict:
    return {event.event_type: event.payload for event in events}


def run_intake_review(review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None) -> AgentEventCreate:
    def fallback() -> dict:
        lines = split_feedback_lines(review.input)
        source_summary: dict[str, int] = {}
        for line in lines:
            source_summary[line.source_type] = source_summary.get(line.source_type, 0) + 1
        raw_themes = [issue.issue for issue in detect_issues(review.input)]
        missing_inputs = [
            label
            for label, value in {
                "return reasons": review.input.return_reasons,
                "social comments": review.input.social_comments,
                "current FAQ": review.input.current_faq,
                "product page copy": review.input.product_page_copy,
            }.items()
            if not value
        ]
        return {
            "product_summary": {
                "product_name": review.input.product_name,
                "product_category": review.input.product_category,
                "description": review.input.product_description,
            },
            "source_summary": source_summary,
            "detected_raw_themes": raw_themes,
            "missing_inputs": missing_inputs,
            "recommended_next_agent": "Customer Feedback Review",
            "handoff_to": ["Customer Feedback Review"],
        }

    payload = _llm_or_fallback(
        llm,
        INTAKE_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "events": [event.model_dump(mode="json") for event in events]},
        fallback,
    )
    return _event(
        review,
        "intake_review",
        "intake_summary",
        f"Intake Review structured {review.input.product_name} feedback and handed off to Customer Feedback Review.",
        payload,
        source_agents=[],
        handoff_to=["Customer Feedback Review"],
    )


def run_customer_feedback_review(
    review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None
) -> AgentEventCreate:
    def fallback() -> dict:
        issues = detect_issues(review.input)
        evidence_by_source: dict[str, list[str]] = {}
        for issue in issues:
            for source in issue.source_types:
                evidence_by_source.setdefault(source, [])
            for snippet in issue.customer_language:
                evidence_by_source.setdefault("customer language", []).append(snippet)
        return {
            "top_detected_issues": [issue.model_dump(mode="json") for issue in issues],
            "evidence_by_source": evidence_by_source,
            "business_impact": [impact for issue in issues for impact in issue.business_impact],
            "handoff_to": ["UGC Review", "Support Review", "Product Page Review"],
        }

    payload = _llm_or_fallback(
        llm,
        CUSTOMER_FEEDBACK_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "prior_events": _prior_payloads(events)},
        fallback,
    )
    top_issue = payload.get("top_detected_issues", [{}])[0].get("issue", "customer feedback themes")
    return _event(
        review,
        "customer_feedback_review",
        "feedback_analysis",
        f"Customer Feedback Review identified {top_issue} as the main recurring issue.",
        payload,
        source_agents=["Intake Review"],
        handoff_to=["UGC Review", "Support Review", "Product Page Review"],
    )


def run_ugc_review(review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None) -> AgentEventCreate:
    def fallback() -> dict:
        issues = detect_issues(review.input)
        briefs = build_ugc_briefs(issues)
        return {
            "ugc_briefs": [brief.model_dump(mode="json") for brief in briefs],
            "claims_for_product_page_review": [
                "Verify size guide and model measurement support.",
                "Verify squat-proof, opacity, fabric, and care details before publishing claims.",
            ],
            "handoff_to": ["Product Page Review", "Action Review"],
        }

    payload = _llm_or_fallback(
        llm,
        UGC_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "prior_events": _prior_payloads(events)},
        fallback,
    )
    count = len(payload.get("ugc_briefs", []))
    return _event(
        review,
        "ugc_review",
        "ugc_briefs",
        f"UGC Review created {count} creator briefs from customer objections.",
        payload,
        source_agents=["Customer Feedback Review"],
        handoff_to=["Product Page Review", "Action Review"],
    )


def run_support_review(review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None) -> AgentEventCreate:
    def fallback() -> dict:
        issues = detect_issues(review.input)
        macros = build_support_macros(issues)
        faq_updates = build_faq_updates(issues)
        return {
            "repeated_questions": [snippet for issue in issues for snippet in issue.customer_language[:2]],
            "support_macros": [macro.model_dump(mode="json") for macro in macros],
            "faq_updates": [faq.model_dump(mode="json") for faq in faq_updates],
            "escalation_risks": ["Wrong-size return questions", "Order status questions", "Unsupported product claims"],
            "handoff_to": ["Product Page Review", "Action Review"],
        }

    payload = _llm_or_fallback(
        llm,
        SUPPORT_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "prior_events": _prior_payloads(events)},
        fallback,
    )
    count = len(payload.get("support_macros", []))
    return _event(
        review,
        "support_review",
        "support_assets",
        f"Support Review created {count} support macros and FAQ updates for repeated questions.",
        payload,
        source_agents=["Customer Feedback Review"],
        handoff_to=["Product Page Review", "Action Review"],
    )


def run_product_page_review(
    review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None
) -> AgentEventCreate:
    def fallback() -> dict:
        issues = detect_issues(review.input)
        tasks = build_product_page_tasks(review.input, issues)
        return {
            "missing_product_page_sections": ["Size guide", "Model height/size examples", "Shipping timeline", "Fabric and care details"],
            "weak_or_confusing_claims": ["Comfortable and stylish does not answer sizing, opacity, shipping, or care objections."],
            "faq_gaps": ["Sizing", "Returns for fit", "Squat-proof proof", "Washing", "Shipping timeline"],
            "product_page_tasks": [task.model_dump(mode="json") for task in tasks],
            "proof_blocks_needed": ["Fit proof", "Squat-proof proof", "Fabric/care proof", "Shipping timeline"],
            "handoff_to": ["Action Review"],
        }

    payload = _llm_or_fallback(
        llm,
        PRODUCT_PAGE_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "prior_events": _prior_payloads(events)},
        fallback,
    )
    count = len(payload.get("product_page_tasks", []))
    return _event(
        review,
        "product_page_review",
        "product_page_tasks",
        f"Product Page Review created {count} storefront and FAQ update tasks.",
        payload,
        source_agents=["Customer Feedback Review", "UGC Review", "Support Review"],
        handoff_to=["Action Review"],
    )


def run_action_review(review: ReviewRecord, events: list[AgentEvent], llm: LLMClient | None = None) -> AgentEventCreate:
    def fallback_report() -> FinalReport:
        return build_final_report(review.input)

    client = llm or LLMClient()
    report = client.generate_json(
        ACTION_REVIEW_PROMPT,
        {"review": review.model_dump(mode="json"), "prior_events": [event.model_dump(mode="json") for event in events]},
        fallback_report,
        schema_model=FinalReport,
    )
    if isinstance(report, dict):
        report = FinalReport.model_validate(report)

    payload = {
        "status": report.status,
        "primary_customer_issue": report.primary_customer_issue,
        "priority": report.priority,
        "final_report": report.model_dump(mode="json"),
        "owner_handoff": [task.model_dump(mode="json") for task in report.owner_handoff],
        "informed_by_agents": ["Customer Feedback Review", "UGC Review", "Support Review", "Product Page Review"],
    }
    return _event(
        review,
        "action_review",
        "final_action_plan",
        f"Action Review finalized the plan around {report.primary_customer_issue}.",
        payload,
        source_agents=["Customer Feedback Review", "UGC Review", "Support Review", "Product Page Review"],
        handoff_to=[],
        status=report.status,
    )


HANDLERS = {
    "intake_review": run_intake_review,
    "customer_feedback_review": run_customer_feedback_review,
    "ugc_review": run_ugc_review,
    "support_review": run_support_review,
    "product_page_review": run_product_page_review,
    "action_review": run_action_review,
}
