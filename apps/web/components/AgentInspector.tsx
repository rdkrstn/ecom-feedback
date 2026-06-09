import type { AgentEvent } from "../lib/types";
import type { AgentNode, AgentVisualStatus } from "../lib/agent-workflow";
import { JsonBlock } from "./JsonBlock";
import { StatusBadge } from "./StatusBadge";

interface AgentInspectorProps {
  agent: AgentNode;
  event?: AgentEvent;
  status: AgentVisualStatus;
}

export function AgentInspector({ agent, event, status }: AgentInspectorProps) {
  return (
    <aside className="agent-inspector">
      <div className="inspector-topline">
        <div>
          <p className="eyebrow">AGENT INSPECTOR</p>
          <h3>{agent.name}</h3>
        </div>
        <StatusBadge status={status} />
      </div>

      {event ? (
        <>
          <p className="inspector-summary">{event.summary}</p>
          <div className="inspector-meta-grid">
            <span>EVENT</span>
            <strong>{event.event_type}</strong>
            <span>SOURCES</span>
            <strong>{event.source_agents.length ? event.source_agents.join(", ") : "None"}</strong>
            <span>HANDOFF</span>
            <strong>{event.handoff_to.length ? event.handoff_to.join(", ") : "None"}</strong>
            <span>TIME</span>
            <strong>{new Date(event.created_at).toLocaleString()}</strong>
          </div>
          <details className="json-details inspector-json">
            <summary>Payload JSON</summary>
            <JsonBlock value={event.payload} />
          </details>
        </>
      ) : (
        <div className="inspector-empty">
          <p>{agent.role}</p>
          <p>Waiting for review event.</p>
          <p>
            Expected handoff:{" "}
            <strong>
              {agent.handoffTo.length
                ? agent.handoffTo.map((target) => target.replaceAll("_", " ")).join(", ")
                : "final output"}
            </strong>
          </p>
        </div>
      )}
    </aside>
  );
}
