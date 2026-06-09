"use client";

import { Database } from "lucide-react";

interface SampleDataButtonProps {
  onClick: () => void;
}

export function SampleDataButton({ onClick }: SampleDataButtonProps) {
  return (
    <button type="button" className="button secondary" onClick={onClick}>
      <Database size={16} />
      Load sample data
    </button>
  );
}
