import type { ReactNode } from "react";
import type { FinalReport as FinalReportType } from "../lib/types";
import { StatusBadge } from "./StatusBadge";

interface FinalReportProps {
  report: FinalReportType | null;
  status?: string;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="report-section">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

export function FinalReport({ report, status = "draft" }: FinalReportProps) {
  if (!report) {
    return (
      <div className="final-report">
        <div className="report-topline">
          <span className="mono">REVIEW STATUS</span>
          <StatusBadge status={status} />
        </div>
        <div className="empty-state">No final action plan yet.</div>
      </div>
    );
  }

  return (
    <div className="final-report">
      <div className="report-topline">
        <span className="mono">REVIEW STATUS</span>
        <StatusBadge status={report.status} />
      </div>
      <Section title="CUSTOMER ISSUE">
        <p className="lead">{report.primary_customer_issue}</p>
        <p>{report.executive_summary}</p>
        <p className="priority">PRIORITY: {report.priority.toUpperCase()}</p>
      </Section>
      <Section title="UGC BRIEFS">
        {report.ugc_briefs.map((brief) => (
          <div className="compact-block" key={brief.title}>
            <strong>{brief.title}</strong>
            <p>{brief.goal}</p>
          </div>
        ))}
      </Section>
      <Section title="SUPPORT MACROS">
        {report.support_macros.map((macro) => (
          <div className="compact-block" key={macro.name}>
            <strong>{macro.name}</strong>
            <p>{macro.use_case}</p>
          </div>
        ))}
      </Section>
      <Section title="FAQ UPDATES">
        {report.faq_updates.map((faq) => (
          <div className="compact-block" key={faq.question}>
            <strong>{faq.question}</strong>
            <p>{faq.answer}</p>
          </div>
        ))}
      </Section>
      <Section title="PRODUCT PAGE TASKS">
        {report.product_page_tasks.map((task) => (
          <div className="task-line" key={`${task.section}-${task.task}`}>
            <span>{task.section}</span>
            <p>{task.task}</p>
          </div>
        ))}
      </Section>
      <Section title="OWNER HANDOFF">
        {report.owner_handoff.map((task) => (
          <div className="task-line" key={`${task.owner}-${task.task}`}>
            <span>{task.owner}</span>
            <p>{task.task}</p>
          </div>
        ))}
      </Section>
      <Section title="SOURCE EVIDENCE">
        <ul className="evidence-list">
          {report.source_evidence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Section>
    </div>
  );
}
