from __future__ import annotations

from dataclasses import dataclass

from .schemas import (
    DetectedIssue,
    FAQUpdate,
    FeedbackReviewInput,
    FinalReport,
    OwnerTask,
    ProductPageTask,
    SupportMacro,
    UGCBrief,
)
from .utils import compact_snippets


@dataclass(frozen=True)
class FeedbackLine:
    source_type: str
    text: str


@dataclass(frozen=True)
class IssueRule:
    issue: str
    keywords: tuple[str, ...]
    recommended_action: str
    business_impact: tuple[str, ...]


SOURCE_FIELDS = {
    "support_tickets": "support ticket",
    "customer_reviews": "customer review",
    "return_reasons": "return reason",
    "social_comments": "social comment",
}

ISSUE_RULES = [
    IssueRule(
        issue="Sizing uncertainty",
        keywords=(
            "size",
            "sizing",
            "fit",
            "between sizes",
            "body type",
            "curvy",
            "short girls",
            "height",
            "waistband",
            "roll down",
            "compressed",
            "compression",
        ),
        recommended_action="Add clearer size guidance, body type examples, and support macros for fit questions.",
        business_impact=(
            "Repeated support questions before purchase",
            "Wrong-size returns",
            "Lower buyer confidence on product page",
        ),
    ),
    IssueRule(
        issue="Shipping timeline confusion",
        keywords=("shipping", "shipped", "delivery", "tracking", "delay", "arrive", "longer"),
        recommended_action="Add a plain shipping timeline block and macro for order status questions.",
        business_impact=("Repeated order status tickets", "Purchase hesitation", "Post-purchase frustration"),
    ),
    IssueRule(
        issue="Squat-proof and proof concerns",
        keywords=("squat", "see-through", "proof", "opacity", "trust", "does it work", "show"),
        recommended_action="Create proof-focused UGC and add product page proof blocks for opacity and performance.",
        business_impact=("Buyer hesitation", "UGC does not answer objections", "Potential abandoned carts"),
    ),
    IssueRule(
        issue="Fabric and care detail gaps",
        keywords=("fabric", "material", "wash", "washing", "care", "cleaning", "ingredients", "sensitivity"),
        recommended_action="Add fabric, opacity, and care instructions to FAQ and product page copy.",
        business_impact=("Avoidable support tickets", "Unclear quality expectations", "Return risk"),
    ),
    IssueRule(
        issue="Return and exchange confidence",
        keywords=("return", "refund", "exchange", "wrong size", "don't fit", "doesn't fit"),
        recommended_action="Clarify return and exchange rules near size guidance and support macros.",
        business_impact=("Fit-related purchase anxiety", "Support escalation risk", "Customer confidence gap"),
    ),
    IssueRule(
        issue="Product scale and dimensions uncertainty",
        keywords=("dimension", "size in hand", "scale", "length", "width", "height and size"),
        recommended_action="Add model measurements, scale references, and product dimensions where useful.",
        business_impact=("Unclear expectations", "More pre-purchase questions"),
    ),
    IssueRule(
        issue="Price and value hesitation",
        keywords=("price", "value", "discount", "expensive", "worth"),
        recommended_action="Show proof of value through benefits, durability, and social proof.",
        business_impact=("Discount dependency", "Lower conversion from value-sensitive buyers"),
    ),
    IssueRule(
        issue="Expected versus actual mismatch",
        keywords=("expected", "actual", "mismatch", "different", "not what", "thicker"),
        recommended_action="Make expectation-setting copy more specific before purchase.",
        business_impact=("Return risk", "Review quality risk", "Customer trust issue"),
    ),
]


def split_feedback_lines(review_input: FeedbackReviewInput) -> list[FeedbackLine]:
    lines: list[FeedbackLine] = []
    for field_name, source_type in SOURCE_FIELDS.items():
        raw = getattr(review_input, field_name) or ""
        for line in raw.splitlines():
            cleaned = " ".join(line.strip(" -\t\r\n").split())
            if cleaned:
                lines.append(FeedbackLine(source_type=source_type, text=cleaned))
    return lines


def _score_issue(rule: IssueRule, lines: list[FeedbackLine]) -> tuple[int, list[FeedbackLine]]:
    matched: list[FeedbackLine] = []
    for line in lines:
        text = line.text.lower()
        if any(keyword in text for keyword in rule.keywords):
            matched.append(line)
    return len(matched), matched


def _frequency(score: int) -> str:
    if score >= 5:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def detect_issues(review_input: FeedbackReviewInput) -> list[DetectedIssue]:
    lines = split_feedback_lines(review_input)
    scored: list[tuple[int, IssueRule, list[FeedbackLine]]] = []
    for rule in ISSUE_RULES:
        score, matched = _score_issue(rule, lines)
        if score > 0:
            scored.append((score, rule, matched))
    scored.sort(key=lambda item: item[0], reverse=True)

    if lines and len(scored) < 3:
        used = {rule.issue for _, rule, _ in scored}
        for rule in ISSUE_RULES:
            if rule.issue not in used:
                scored.append((1, rule, lines[:2]))
                used.add(rule.issue)
            if len(scored) >= 3:
                break

    issues: list[DetectedIssue] = []
    for score, rule, matched in scored:
        issues.append(
            DetectedIssue(
                issue=rule.issue,
                frequency=_frequency(score),
                source_types=sorted({line.source_type for line in matched}),
                customer_language=compact_snippets((line.text for line in matched), limit=5),
                business_impact=list(rule.business_impact),
                recommended_action=rule.recommended_action,
            )
        )
    return issues


def build_ugc_briefs(issues: list[DetectedIssue]) -> list[UGCBrief]:
    issue_names = {issue.issue.lower(): issue for issue in issues}
    briefs: list[UGCBrief] = []

    sizing_issue = next((issue for name, issue in issue_names.items() if "sizing" in name), None)
    proof_issue = next((issue for name, issue in issue_names.items() if "proof" in name or "squat" in name), None)
    fabric_issue = next((issue for name, issue in issue_names.items() if "fabric" in name), None)

    if sizing_issue:
        briefs.append(
            UGCBrief(
                title="Sizing confidence video",
                goal="Reduce buyer uncertainty around size selection before purchase.",
                source_issue=sizing_issue.issue,
                creator_instructions=[
                    "State height, usual size, ordered size, and fit preference.",
                    "Compare size-up versus size-down guidance using customer language.",
                    "Show waistband behavior during walking and light movement.",
                ],
                hooks=[
                    "If you are between sizes, this is how these leggings fit.",
                    "Here is what I would order if I wanted more compression.",
                ],
                shot_list=[
                    "Creator states measurements and selected size",
                    "Front, side, and movement fit check",
                    "Close-up of waistband staying in place",
                ],
                proof_needed=["Model height and size", "Size guide reference", "Fit preference guidance"],
            )
        )
        briefs.append(
            UGCBrief(
                title="Body type fit comparison video",
                goal="Show the product on different body types so shoppers can compare fit.",
                source_issue=sizing_issue.issue,
                creator_instructions=[
                    "Include creators with different heights and body types.",
                    "Use plain fit notes instead of generic compliments.",
                    "Address short and curvy buyer questions directly.",
                ],
                hooks=[
                    "Three body types, one pair of compression leggings.",
                    "Short, curvy, and between sizes: how the fit changes.",
                ],
                shot_list=[
                    "Side-by-side creator measurements",
                    "Fit notes on waistband and length",
                    "Movement check from each creator",
                ],
                proof_needed=["Creator measurements", "Ordered sizes", "Fit notes by body type"],
            )
        )

    if proof_issue:
        briefs.append(
            UGCBrief(
                title="Squat-proof proof video",
                goal="Answer opacity and workout proof objections with a visible test.",
                source_issue=proof_issue.issue,
                creator_instructions=[
                    "Show a clear squat test in bright lighting.",
                    "Avoid unsupported performance claims.",
                    "State what the viewer should look for in the test.",
                ],
                hooks=[
                    "Here is the squat test everyone asked for.",
                    "Are they see-through? Watch this before buying.",
                ],
                shot_list=[
                    "Bright-light squat test",
                    "Close-up fabric stretch check",
                    "Workout movement sequence",
                ],
                proof_needed=["Opacity demonstration", "Lighting condition", "Fabric stretch view"],
            )
        )

    if fabric_issue and len(briefs) < 4:
        briefs.append(
            UGCBrief(
                title="Fabric and care walkthrough",
                goal="Explain fabric feel, opacity, and washing expectations before purchase.",
                source_issue=fabric_issue.issue,
                creator_instructions=[
                    "Describe fabric feel in practical terms.",
                    "Show care label or explain washing steps.",
                    "Connect fabric details to customer concerns.",
                ],
                hooks=["What the fabric actually feels like.", "How I wash these after workouts."],
                shot_list=["Fabric close-up", "Stretch and opacity check", "Care instruction view"],
                proof_needed=["Fabric details", "Care instructions", "Opacity reference"],
            )
        )

    if not briefs and issues:
        top = issues[0]
        briefs.append(
            UGCBrief(
                title=f"{top.issue} objection video",
                goal="Address the top customer issue using customer language.",
                source_issue=top.issue,
                creator_instructions=["Use the exact objection from customers.", "Show the proof needed to answer it."],
                hooks=[f"Customers keep asking about {top.issue.lower()}."],
                shot_list=["State objection", "Show product proof", "Close with buying guidance"],
                proof_needed=top.customer_language[:2],
            )
        )

    return briefs[:4]


def build_support_macros(issues: list[DetectedIssue]) -> list[SupportMacro]:
    macros: list[SupportMacro] = []
    names = [issue.issue.lower() for issue in issues]

    if any("sizing" in name for name in names):
        macros.append(
            SupportMacro(
                name="Sizing question",
                use_case="Customer is between sizes or unsure about fit.",
                body=(
                    "Thanks for checking before ordering. If you are between sizes, choose based on fit preference: "
                    "size down for stronger compression or size up for more comfort. We recommend reviewing the size "
                    "guide and model height/size notes before checkout."
                ),
                related_issue="Sizing uncertainty",
            )
        )
    if any("shipping" in name for name in names):
        macros.append(
            SupportMacro(
                name="Shipping timeline",
                use_case="Customer asks when the order ships or arrives.",
                body=(
                    "Shipping timing depends on destination and fulfillment status. Once your order ships, you will "
                    "receive tracking details. We are adding clearer timeline guidance to the product page and FAQ."
                ),
                related_issue="Shipping timeline confusion",
            )
        )
    if any("return" in name for name in names) or any("sizing" in name for name in names):
        macros.append(
            SupportMacro(
                name="Return/exchange fit issue",
                use_case="Customer asks whether they can return leggings that do not fit.",
                body=(
                    "If the fit is not right, returns are available within the stated return window. Please keep the "
                    "item in return-eligible condition and contact support with your order number so we can help with "
                    "the next step."
                ),
                related_issue="Return and exchange confidence",
            )
        )
    if any("fabric" in name for name in names):
        macros.append(
            SupportMacro(
                name="Washing/care instructions",
                use_case="Customer asks how to wash or care for the leggings.",
                body=(
                    "For care, wash cold with similar colors and avoid high heat drying. We recommend adding the full "
                    "care instructions to the product page so customers can review them before buying."
                ),
                related_issue="Fabric and care detail gaps",
            )
        )
    return macros


def build_faq_updates(issues: list[DetectedIssue]) -> list[FAQUpdate]:
    updates: list[FAQUpdate] = []
    names = [issue.issue.lower() for issue in issues]
    if any("sizing" in name for name in names):
        updates.append(
            FAQUpdate(
                question="How should I choose a size if I am between sizes?",
                answer="Use the size guide first, then choose based on fit preference: size down for more compression or size up for more comfort.",
                related_issue="Sizing uncertainty",
            )
        )
    if any("proof" in name or "squat" in name for name in names):
        updates.append(
            FAQUpdate(
                question="Are the leggings squat-proof?",
                answer="Add an opacity and squat-test answer that references verified product proof, fabric details, and lighting conditions.",
                related_issue="Squat-proof and proof concerns",
            )
        )
    if any("return" in name for name in names):
        updates.append(
            FAQUpdate(
                question="Can I return or exchange them if the fit is wrong?",
                answer="Returns are available within the return window when the item meets return eligibility rules. Include a direct support path for fit issues.",
                related_issue="Return and exchange confidence",
            )
        )
    if any("fabric" in name for name in names):
        updates.append(
            FAQUpdate(
                question="How should I wash and care for the leggings?",
                answer="Wash cold with similar colors and avoid high heat drying. Add any fabric-specific restrictions from the product team.",
                related_issue="Fabric and care detail gaps",
            )
        )
    if any("shipping" in name for name in names):
        updates.append(
            FAQUpdate(
                question="How long does shipping take?",
                answer="Show the standard processing and delivery timeline by destination, plus when customers receive tracking.",
                related_issue="Shipping timeline confusion",
            )
        )
    return updates


def build_product_page_tasks(review_input: FeedbackReviewInput, issues: list[DetectedIssue]) -> list[ProductPageTask]:
    page_text = f"{review_input.current_faq or ''}\n{review_input.product_page_copy or ''}".lower()
    names = [issue.issue.lower() for issue in issues]
    tasks: list[ProductPageTask] = []

    if any("sizing" in name for name in names):
        tasks.append(
            ProductPageTask(
                section="Add-to-cart area",
                task="Add size guide near add-to-cart",
                reason="Sizing questions are repeated across support tickets, reviews, returns, and social comments.",
                related_issue="Sizing uncertainty",
                priority="high",
            )
        )
        tasks.append(
            ProductPageTask(
                section="Fit proof",
                task="Add model height/size examples",
                reason="Customers ask what size creators are wearing and need body type references.",
                related_issue="Sizing uncertainty",
                priority="high",
            )
        )
    if any("shipping" in name for name in names) and "timeline" not in page_text:
        tasks.append(
            ProductPageTask(
                section="Shipping",
                task="Add shipping timeline block",
                reason="Customers ask how long shipping takes and whether orders have shipped.",
                related_issue="Shipping timeline confusion",
                priority="medium",
            )
        )
    if any("fabric" in name for name in names) or any("proof" in name for name in names):
        tasks.append(
            ProductPageTask(
                section="Product details",
                task="Add fabric opacity and care section",
                reason="Customers ask about material, washing, and see-through concerns before buying.",
                related_issue="Fabric and care detail gaps",
                priority="high",
            )
        )
    if issues:
        tasks.append(
            ProductPageTask(
                section="FAQ",
                task="Add FAQ for sizing, returns, squat-proof, washing",
                reason="Current FAQ does not answer the repeated questions shown in feedback.",
                related_issue=issues[0].issue,
                priority="high",
            )
        )
    return tasks


def build_owner_handoff(issues: list[DetectedIssue]) -> list[OwnerTask]:
    related = issues[0].issue if issues else "Customer feedback review"
    return [
        OwnerTask(
            owner="Content",
            task="Create UGC briefs for sizing confidence, squat-proof proof, and body type fit comparison.",
            priority="high",
            source_agent="UGC Review",
            related_issue=related,
        ),
        OwnerTask(
            owner="Support",
            task="Publish macros for sizing, shipping, return/exchange fit issues, and washing instructions.",
            priority="high",
            source_agent="Support Review",
            related_issue=related,
        ),
        OwnerTask(
            owner="Storefront",
            task="Update product page and FAQ with size guide, fit proof, shipping timeline, and fabric/care details.",
            priority="high",
            source_agent="Product Page Review",
            related_issue=related,
        ),
        OwnerTask(
            owner="Operations",
            task="Review shipping timeline clarity and return reason tracking for wrong-size orders.",
            priority="medium",
            source_agent="Action Review",
            related_issue=related,
        ),
    ]


def build_final_report(review_input: FeedbackReviewInput) -> FinalReport:
    issues = detect_issues(review_input)
    primary = issues[0].issue if issues else "No recurring customer issue detected"
    priority = "high" if issues and issues[0].frequency == "high" else "medium"
    source_evidence = compact_snippets(
        snippet for issue in issues[:5] for snippet in issue.customer_language
    )
    ugc_briefs = build_ugc_briefs(issues)
    support_macros = build_support_macros(issues)
    faq_updates = build_faq_updates(issues)
    product_page_tasks = build_product_page_tasks(review_input, issues)
    owner_handoff = build_owner_handoff(issues)

    return FinalReport(
        status="completed" if issues else "changes_required",
        primary_customer_issue=primary,
        priority=priority,
        executive_summary=(
            f"{review_input.product_name} feedback shows {primary.lower()} as the highest-priority issue. "
            "The recommended workflow connects content, support, storefront, and operations so repeated "
            "questions become UGC briefs, macros, FAQ updates, product page tasks, and owner handoffs."
        ),
        detected_issues=issues,
        ugc_briefs=ugc_briefs,
        support_macros=support_macros,
        faq_updates=faq_updates,
        product_page_tasks=product_page_tasks,
        owner_handoff=owner_handoff,
        source_evidence=source_evidence,
        next_review_recommendation=(
            "Run another feedback review after the product page updates and new UGC are live, then compare "
            "support ticket frequency and return reasons against this baseline."
        ),
    )
