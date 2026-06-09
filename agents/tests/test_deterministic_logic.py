from sagad_feedback.deterministic_logic import build_final_report, detect_issues
from sagad_feedback.seed import SAMPLE_REVIEW_INPUT


def test_sample_input_returns_detected_issues():
    issues = detect_issues(SAMPLE_REVIEW_INPUT)

    assert len(issues) >= 3


def test_sample_input_returns_sizing_issue():
    report = build_final_report(SAMPLE_REVIEW_INPUT)

    assert "sizing" in report.primary_customer_issue.lower()
    assert any("sizing" in issue.issue.lower() for issue in report.detected_issues)


def test_sample_input_returns_at_least_one_ugc_brief():
    report = build_final_report(SAMPLE_REVIEW_INPUT)

    assert report.ugc_briefs
    assert any("sizing" in brief.title.lower() for brief in report.ugc_briefs)


def test_sample_input_returns_at_least_one_support_macro():
    report = build_final_report(SAMPLE_REVIEW_INPUT)

    assert report.support_macros
    assert any("sizing" in macro.name.lower() for macro in report.support_macros)


def test_sample_input_returns_at_least_one_product_page_task():
    report = build_final_report(SAMPLE_REVIEW_INPUT)

    assert report.product_page_tasks
    assert any("size guide" in task.task.lower() for task in report.product_page_tasks)
