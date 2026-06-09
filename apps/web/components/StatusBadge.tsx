import type { ReviewStatus } from "../lib/types";

interface StatusBadgeProps {
  status: ReviewStatus | string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`status-badge status-${status}`}>{status.replaceAll("_", " ").toUpperCase()}</span>;
}
