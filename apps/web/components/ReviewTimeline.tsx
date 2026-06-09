import type { AgentEvent } from "../lib/types";
import { AgentCard } from "./AgentCard";

interface ReviewTimelineProps {
  events: AgentEvent[];
}

export function ReviewTimeline({ events }: ReviewTimelineProps) {
  if (events.length === 0) {
    return <div className="empty-state">No review activity yet.</div>;
  }

  return (
    <div className="timeline">
      {events.map((event) => (
        <AgentCard event={event} key={event.id} />
      ))}
    </div>
  );
}
