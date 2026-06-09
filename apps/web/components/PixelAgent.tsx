"use client";

import type { CSSProperties } from "react";
import type { AgentNode, AgentVisualStatus } from "../lib/agent-workflow";

interface PixelAgentProps {
  agent: AgentNode;
  status: AgentVisualStatus;
  selected: boolean;
  onSelect: () => void;
}

export function PixelAgent({ agent, status, selected, onSelect }: PixelAgentProps) {
  return (
    <button
      type="button"
      className={`pixel-agent pixel-agent-${status} ${selected ? "pixel-agent-selected" : ""}`}
      style={{ left: `${agent.x}%`, top: `${agent.y}%`, "--agent-accent": agent.accent } as CSSProperties}
      onClick={onSelect}
      aria-label={`Select ${agent.name}`}
    >
      <span className="pixel-body" aria-hidden="true">
        <span className="pixel-head">
          <span className="pixel-eye pixel-eye-left" />
          <span className="pixel-eye pixel-eye-right" />
        </span>
        <span className="pixel-torso" />
        <span className="pixel-shadow" />
      </span>
      <span className="pixel-agent-copy">
        <strong>{agent.name}</strong>
        <span>{agent.role}</span>
      </span>
      <span className="pixel-status">{status}</span>
    </button>
  );
}
