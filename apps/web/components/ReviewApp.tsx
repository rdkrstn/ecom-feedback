"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { AgentEvent, FeedbackReviewInput, ReviewRecord } from "../lib/types";
import { createReview, getEvents, getKickoffMessage, getReview, runLocalWorkflow } from "../lib/api";
import { sampleReviewInput } from "../lib/sample-data";
import { getVisibleEvents } from "../lib/agent-workflow";
import { AgentWorkflowBoard } from "./AgentWorkflowBoard";
import { BandSetupPanel } from "./BandSetupPanel";
import { FinalReport } from "./FinalReport";
import { ReviewForm } from "./ReviewForm";
import { ReviewTimeline } from "./ReviewTimeline";
import { StatusBadge } from "./StatusBadge";

const activeStatuses = new Set(["running", "waiting_for_band"]);

export function ReviewApp() {
  const [formValue, setFormValue] = useState<FeedbackReviewInput>(sampleReviewInput);
  const [review, setReview] = useState<ReviewRecord | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [kickoffMessage, setKickoffMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [replayIndex, setReplayIndex] = useState<number | null>(null);

  const hasFeedback = useMemo(() => {
    return Boolean(
      formValue.support_tickets.trim() ||
        formValue.customer_reviews.trim() ||
        (formValue.return_reasons || "").trim() ||
        (formValue.social_comments || "").trim()
    );
  }, [formValue]);

  const refreshReview = useCallback(async (reviewId: string) => {
    const [nextReview, nextEvents] = await Promise.all([getReview(reviewId), getEvents(reviewId)]);
    setReview(nextReview);
    setEvents(nextEvents);
  }, []);

  useEffect(() => {
    if (!review || !activeStatuses.has(review.status)) {
      return;
    }
    const timer = window.setInterval(() => {
      refreshReview(review.id).catch((err: Error) => setError(err.message));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [refreshReview, review]);

  useEffect(() => {
    if (replayIndex === null) {
      return;
    }
    if (events.length === 0 || replayIndex >= events.length - 1) {
      const endTimer = window.setTimeout(() => setReplayIndex(null), 650);
      return () => window.clearTimeout(endTimer);
    }
    const timer = window.setTimeout(() => setReplayIndex((current) => (current === null ? null : current + 1)), 650);
    return () => window.clearTimeout(timer);
  }, [events.length, replayIndex]);

  const handleCreateReview = async () => {
    setError("");
    if (!formValue.product_name.trim() || !formValue.product_category.trim() || !hasFeedback) {
      setError("Product name, product category, and at least one feedback field are required.");
      return;
    }
    setBusy(true);
    try {
      const created = await createReview(formValue);
      setReview(created);
      setEvents([]);
      setReplayIndex(null);
      const kickoff = await getKickoffMessage(created.id);
      setKickoffMessage(kickoff.kickoff_message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create review.");
    } finally {
      setBusy(false);
    }
  };

  const handleRunLocalWorkflow = async () => {
    if (!review) {
      return;
    }
    setError("");
    setBusy(true);
    try {
      const completed = await runLocalWorkflow(review.id);
      setReview(completed);
      const nextEvents = await getEvents(review.id);
      setEvents(nextEvents);
      setReplayIndex(nextEvents.length ? 0 : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not run local workflow.");
    } finally {
      setBusy(false);
    }
  };

  const handleCopyKickoff = async () => {
    if (!kickoffMessage) {
      return;
    }
    await navigator.clipboard.writeText(kickoffMessage);
  };

  const visibleEvents = getVisibleEvents(events, replayIndex);
  const visibleReport = replayIndex === null ? review?.final_report ?? null : null;

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">SAGADOS FEEDBACK REVIEW</p>
          <h1>ECOMMERCE FEEDBACK WORKFLOW</h1>
          <p className="subtitle">
            Customer feedback workflow for UGC, support, product page updates, and owner handoffs.
          </p>
        </div>
        <div className="status-pills">
          <span>TRACK 1</span>
          <span>BAND SDK</span>
          <span>6 AGENTS</span>
          {review ? <StatusBadge status={review.status} /> : null}
        </div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <AgentWorkflowBoard review={review} events={events} replayIndex={replayIndex} />

      <section className="workspace-grid">
        <aside className="panel input-panel clean-panel">
          <div className="panel-title-row">
            <div>
              <p className="eyebrow">CONTROL PANEL</p>
              <h2>Review Input</h2>
            </div>
          </div>
          <ReviewForm
            value={formValue}
            onChange={setFormValue}
            onCreateReview={handleCreateReview}
            onRunLocalWorkflow={handleRunLocalWorkflow}
            onCopyKickoff={handleCopyKickoff}
            canRun={Boolean(review)}
            canCopyKickoff={Boolean(kickoffMessage)}
            busy={busy}
          />
        </aside>

        <section className="panel timeline-panel clean-panel">
          <div className="panel-title-row">
            <div>
              <p className="eyebrow">EVENT LOG</p>
              <h2>Agent Activity</h2>
            </div>
            <span className="count-box">{visibleEvents.length}</span>
          </div>
          <ReviewTimeline events={visibleEvents} />
        </section>

        <aside className="panel final-panel clean-panel">
          <div className="panel-title-row">
            <div>
              <p className="eyebrow">OUTPUT</p>
              <h2>Final Action Plan</h2>
            </div>
          </div>
          <FinalReport report={visibleReport} status={review?.status ?? "draft"} />
        </aside>
      </section>

      <BandSetupPanel kickoffMessage={kickoffMessage} reviewId={review?.id} />
    </main>
  );
}
