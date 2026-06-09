import { AGENT_NODES, type HandoffEdge } from "../lib/agent-workflow";

interface HandoffPathProps {
  edge: HandoffEdge;
}

export function HandoffPath({ edge }: HandoffPathProps) {
  const from = AGENT_NODES.find((agent) => agent.key === edge.from);
  const to = AGENT_NODES.find((agent) => agent.key === edge.to);

  if (!from || !to) {
    return null;
  }

  return (
    <line
      className={`handoff-line ${edge.active ? "handoff-line-active" : ""}`}
      x1={from.x}
      y1={from.y + 7}
      x2={to.x}
      y2={to.y + 7}
      vectorEffect="non-scaling-stroke"
    />
  );
}
