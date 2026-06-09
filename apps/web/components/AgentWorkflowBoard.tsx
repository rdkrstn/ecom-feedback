"use client";

import { useMemo, useState } from "react";
import {
  AGENT_NODES,
  getActiveAgentKey,
  getActiveHandoffs,
  getAgentNode,
  getAgentStatus,
  getLatestEventForAgent,
  getPacketPosition,
  getVisibleEvents,
  type AgentKey
} from "../lib/agent-workflow";
import type { AgentEvent, ReviewRecord } from "../lib/types";
import { AgentInspector } from "./AgentInspector";
import { HandoffPath } from "./HandoffPath";
import { PixelAgent } from "./PixelAgent";
import { WorkPacket } from "./WorkPacket";

interface AgentWorkflowBoardProps {
  review: ReviewRecord | null;
  events: AgentEvent[];
  replayIndex: number | null;
}

export function AgentWorkflowBoard({ review, events, replayIndex }: AgentWorkflowBoardProps) {
  const [selectedAgentKey, setSelectedAgentKey] = useState<AgentKey>("intake_review");
  const visibleEvents = useMemo(() => getVisibleEvents(events, replayIndex), [events, replayIndex]);
  const activeAgentKey = getActiveAgentKey(visibleEvents, replayIndex);
  const handoffs = getActiveHandoffs(events, replayIndex);
  const packetPosition = getPacketPosition(events, replayIndex);
  const selectedAgent = getAgentNode(selectedAgentKey) || AGENT_NODES[0];
  const selectedEvent = getLatestEventForAgent(selectedAgentKey, visibleEvents);
  const visualReviewStatus = replayIndex !== null ? "running" : review?.status;
  const selectedStatus = getAgentStatus(selectedAgentKey, visibleEvents, visualReviewStatus, activeAgentKey);
  const running = replayIndex !== null || review?.status === "running" || review?.status === "waiting_for_band";

  return (
    <section className="workflow-shell">
      <div className="workflow-board">
        <div className="workflow-board-header">
          <div>
            <p className="eyebrow">AGENT WORKFLOW</p>
            <h2>PIXEL REVIEW SIMULATOR</h2>
          </div>
          <div className="workflow-stats">
            <span>{visibleEvents.length}/6 events</span>
            <span>{review ? review.status.replaceAll("_", " ") : "no review"}</span>
          </div>
        </div>

        <div className="agent-stage" aria-label="Agent workflow board">
          <svg className="handoff-layer" viewBox="0 0 100 80" preserveAspectRatio="none" aria-hidden="true">
            {handoffs.map((edge) => (
              <HandoffPath edge={edge} key={`${edge.from}-${edge.to}`} />
            ))}
          </svg>
          <WorkPacket x={packetPosition.x} y={packetPosition.y} running={running} />
          {AGENT_NODES.map((agent) => (
            <PixelAgent
              agent={agent}
              status={getAgentStatus(agent.key, visibleEvents, visualReviewStatus, activeAgentKey)}
              selected={selectedAgentKey === agent.key}
              onSelect={() => setSelectedAgentKey(agent.key)}
              key={agent.key}
            />
          ))}
        </div>
      </div>

      <AgentInspector agent={selectedAgent} event={selectedEvent} status={selectedStatus} />
    </section>
  );
}
