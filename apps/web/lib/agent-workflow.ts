import type { AgentEvent, ReviewStatus } from "./types";

export type AgentKey =
  | "intake_review"
  | "customer_feedback_review"
  | "ugc_review"
  | "support_review"
  | "product_page_review"
  | "action_review";

export type AgentVisualStatus = "idle" | "active" | "completed" | "waiting" | "error";

export interface AgentNode {
  key: AgentKey;
  name: string;
  role: string;
  accent: string;
  x: number;
  y: number;
  handoffTo: AgentKey[];
}

export interface HandoffEdge {
  from: AgentKey;
  to: AgentKey;
  active: boolean;
}

const statusRank: Record<AgentVisualStatus, number> = {
  idle: 0,
  completed: 1,
  waiting: 2,
  active: 3,
  error: 4
};

export const AGENT_NODES: AgentNode[] = [
  {
    key: "intake_review",
    name: "Intake Review",
    role: "Structures input",
    accent: "#4c7dff",
    x: 12,
    y: 24,
    handoffTo: ["customer_feedback_review"]
  },
  {
    key: "customer_feedback_review",
    name: "Customer Feedback Review",
    role: "Finds issues",
    accent: "#00a884",
    x: 34,
    y: 24,
    handoffTo: ["ugc_review", "support_review", "product_page_review"]
  },
  {
    key: "ugc_review",
    name: "UGC Review",
    role: "Builds briefs",
    accent: "#ffbf3f",
    x: 58,
    y: 12,
    handoffTo: ["product_page_review", "action_review"]
  },
  {
    key: "support_review",
    name: "Support Review",
    role: "Writes macros",
    accent: "#ff6b6b",
    x: 58,
    y: 44,
    handoffTo: ["product_page_review", "action_review"]
  },
  {
    key: "product_page_review",
    name: "Product Page Review",
    role: "Creates PDP tasks",
    accent: "#9b6cff",
    x: 78,
    y: 28,
    handoffTo: ["action_review"]
  },
  {
    key: "action_review",
    name: "Action Review",
    role: "Finalizes plan",
    accent: "#101828",
    x: 92,
    y: 62,
    handoffTo: []
  }
];

export const AGENT_ORDER = AGENT_NODES.map((agent) => agent.key);

export function getAgentNode(agentKey: string): AgentNode | undefined {
  return AGENT_NODES.find((agent) => agent.key === agentKey);
}

export function getAgentKeyByName(name: string): AgentKey | undefined {
  const normalized = name.trim().toLowerCase();
  return AGENT_NODES.find((agent) => agent.name.toLowerCase() === normalized)?.key;
}

export function getVisibleEvents(events: AgentEvent[], replayIndex: number | null): AgentEvent[] {
  if (replayIndex === null) {
    return events;
  }
  return events.slice(0, Math.min(events.length, replayIndex + 1));
}

export function getLatestEventForAgent(agentKey: string, events: AgentEvent[]): AgentEvent | undefined {
  return [...events].reverse().find((event) => event.agent_key === agentKey);
}

export function getActiveAgentKey(events: AgentEvent[], replayIndex: number | null): AgentKey {
  if (events.length === 0) {
    return "intake_review";
  }
  if (replayIndex !== null) {
    return (events[Math.min(replayIndex, events.length - 1)]?.agent_key as AgentKey) || "intake_review";
  }
  const latest = events[events.length - 1];
  return (latest.agent_key as AgentKey) || "intake_review";
}

export function getAgentStatus(
  agentKey: AgentKey,
  events: AgentEvent[],
  reviewStatus?: ReviewStatus | string,
  activeAgentKey?: AgentKey
): AgentVisualStatus {
  const latest = getLatestEventForAgent(agentKey, events);
  let status: AgentVisualStatus = "idle";

  if (latest?.status === "failed" || latest?.event_type === "error") {
    status = "error";
  } else if (latest?.status === "waiting" || reviewStatus === "waiting_for_band") {
    status = "waiting";
  } else if (latest) {
    status = "completed";
  }

  if (
    activeAgentKey === agentKey &&
    Boolean(reviewStatus) &&
    reviewStatus !== "completed" &&
    reviewStatus !== "changes_required"
  ) {
    status = maxStatus(status, "active");
  }

  return status;
}

export function getActiveHandoffs(events: AgentEvent[], replayIndex: number | null): HandoffEdge[] {
  const visibleEvents = getVisibleEvents(events, replayIndex);
  const latest = visibleEvents[visibleEvents.length - 1];

  return AGENT_NODES.flatMap((agent) =>
    agent.handoffTo.map((target) => ({
      from: agent.key,
      to: target,
      active:
        Boolean(latest) &&
        latest.agent_key === agent.key &&
        latest.handoff_to.some((handoffName) => getAgentKeyByName(handoffName) === target)
    }))
  );
}

export function getPacketPosition(events: AgentEvent[], replayIndex: number | null): { x: number; y: number } {
  const activeAgentKey = getActiveAgentKey(events, replayIndex);
  const node = getAgentNode(activeAgentKey) || AGENT_NODES[0];
  return { x: node.x, y: node.y };
}

function maxStatus(current: AgentVisualStatus, next: AgentVisualStatus): AgentVisualStatus {
  return statusRank[next] > statusRank[current] ? next : current;
}
