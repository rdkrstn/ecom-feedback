"use client";

import { Clipboard, Play, Plus } from "lucide-react";
import type { FeedbackReviewInput } from "../lib/types";
import { sampleReviewInput } from "../lib/sample-data";
import { SampleDataButton } from "./SampleDataButton";

interface ReviewFormProps {
  value: FeedbackReviewInput;
  onChange: (value: FeedbackReviewInput) => void;
  onCreateReview: () => void;
  onRunLocalWorkflow: () => void;
  onCopyKickoff: () => void;
  canRun: boolean;
  canCopyKickoff: boolean;
  busy: boolean;
}

const fields: Array<{ key: keyof FeedbackReviewInput; label: string; kind: "input" | "textarea"; required?: boolean }> = [
  { key: "product_name", label: "product_name", kind: "input", required: true },
  { key: "product_category", label: "product_category", kind: "input", required: true },
  { key: "product_description", label: "product_description", kind: "textarea" },
  { key: "support_tickets", label: "support_tickets", kind: "textarea" },
  { key: "customer_reviews", label: "customer_reviews", kind: "textarea" },
  { key: "return_reasons", label: "return_reasons", kind: "textarea" },
  { key: "social_comments", label: "social_comments", kind: "textarea" },
  { key: "current_faq", label: "current_faq", kind: "textarea" },
  { key: "product_page_copy", label: "product_page_copy", kind: "textarea" },
  { key: "main_business_concern", label: "main_business_concern", kind: "textarea" }
];

export function ReviewForm({
  value,
  onChange,
  onCreateReview,
  onRunLocalWorkflow,
  onCopyKickoff,
  canRun,
  canCopyKickoff,
  busy
}: ReviewFormProps) {
  const update = (key: keyof FeedbackReviewInput, nextValue: string) => {
    onChange({ ...value, [key]: nextValue });
  };

  return (
    <form
      className="form-stack"
      onSubmit={(event) => {
        event.preventDefault();
        onCreateReview();
      }}
    >
      <div className="button-row">
        <SampleDataButton onClick={() => onChange(sampleReviewInput)} />
        <button type="submit" className="button primary" disabled={busy}>
          <Plus size={16} />
          Create review
        </button>
      </div>

      <div className="button-row">
        <button type="button" className="button accent" onClick={onRunLocalWorkflow} disabled={!canRun || busy}>
          <Play size={16} />
          Run local mock workflow
        </button>
        <button type="button" className="button secondary" onClick={onCopyKickoff} disabled={!canCopyKickoff}>
          <Clipboard size={16} />
          Copy Band kickoff message
        </button>
      </div>

      {fields.map((field) => (
        <label className="field" key={field.key}>
          <span>
            {field.label}
            {field.required ? " *" : ""}
          </span>
          {field.kind === "input" ? (
            <input value={value[field.key] ?? ""} onChange={(event) => update(field.key, event.target.value)} />
          ) : (
            <textarea value={value[field.key] ?? ""} onChange={(event) => update(field.key, event.target.value)} rows={4} />
          )}
        </label>
      ))}
    </form>
  );
}
