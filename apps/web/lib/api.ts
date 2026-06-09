import type { AgentEvent, FeedbackReviewInput, KickoffMessage, ReviewRecord } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {})
    }
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function healthCheck(): Promise<{ ok: boolean; service: string }> {
  return request("/health");
}

export function createReview(payload: FeedbackReviewInput): Promise<ReviewRecord> {
  return request("/reviews", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getReview(id: string): Promise<ReviewRecord> {
  return request(`/reviews/${id}`);
}

export function getEvents(reviewId: string): Promise<AgentEvent[]> {
  return request(`/reviews/${reviewId}/events`);
}

export function runLocalWorkflow(reviewId: string): Promise<ReviewRecord> {
  return request(`/reviews/${reviewId}/run-local`, { method: "POST" });
}

export function resetDemo(): Promise<{ ok: boolean }> {
  return request("/demo/reset", { method: "POST" });
}

export function getKickoffMessage(reviewId: string): Promise<KickoffMessage> {
  return request(`/reviews/${reviewId}/kickoff-message`);
}
