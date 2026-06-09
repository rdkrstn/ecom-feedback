interface WorkPacketProps {
  x: number;
  y: number;
  running: boolean;
}

export function WorkPacket({ x, y, running }: WorkPacketProps) {
  return (
    <div
      className={`work-packet ${running ? "work-packet-running" : ""}`}
      style={{ left: `${x}%`, top: `${y}%` }}
      aria-label="Review packet"
    >
      <span />
      <strong>CASE</strong>
    </div>
  );
}
