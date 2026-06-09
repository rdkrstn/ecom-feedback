"use client";

import { ChevronDown } from "lucide-react";
import type { AgentEvent } from "../lib/types";
import { JsonBlock } from "./JsonBlock";
import { StatusBadge } from "./StatusBadge";

interface AgentCardProps {
  event: AgentEvent;
}

export function AgentCard({ event }: AgentCardProps) {
  return (
    <article className="agent-card">
      <div className="agent-card-header">
        <div>
          <h3>{event.agent_name}</h3>
          <p className="mono">{event.event_type}</p>
        </div>
        <StatusBadge status={event.status} />
      </div>
      <p>{event.summary}</p>
      <div className="chip-group">
        {event.source_agents.map((agent) => (
          <span className="chip" key={`source-${event.id}-${agent}`}>
            source: {agent}
          </span>
        ))}
        {event.handoff_to.map((agent) => (
          <span className="chip teal" key={`handoff-${event.id}-${agent}`}>
            handoff: {agent}
          </span>
        ))}
      </div>
      <p className="timestamp">{new Date(event.created_at).toLocaleString()}</p>
      <details className="json-details">
        <summary>
          <ChevronDown size={15} />
          Payload JSON
        </summary>
        <JsonBlock value={event.payload} />
      </details>
    </article>
  );
}
