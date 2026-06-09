from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from .schemas import AgentEvent, AgentEventCreate, FeedbackReviewInput, FinalReport, ReviewRecord
from .settings import DEFAULT_DB_PATH
from .utils import now_iso


class Database:
    def __init__(self, path: str | Path = DEFAULT_DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    input_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    final_report_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_events (
                    id TEXT PRIMARY KEY,
                    review_id TEXT NOT NULL,
                    agent_key TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    source_agents_json TEXT NOT NULL,
                    handoff_to_json TEXT NOT NULL,
                    band_room_id TEXT,
                    band_message_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_review(self, payload: FeedbackReviewInput | dict[str, Any]) -> ReviewRecord:
        review_input = payload if isinstance(payload, FeedbackReviewInput) else FeedbackReviewInput.model_validate(payload)
        timestamp = now_iso()
        review_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reviews (id, input_json, status, final_report_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    json.dumps(review_input.model_dump(mode="json")),
                    "draft",
                    None,
                    timestamp,
                    timestamp,
                ),
            )
            conn.commit()
        return self.get_review(review_id)

    def get_review(self, review_id: str) -> ReviewRecord:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
        if row is None:
            raise KeyError(f"Review not found: {review_id}")
        final_raw = row["final_report_json"]
        return ReviewRecord(
            id=row["id"],
            input=FeedbackReviewInput.model_validate(json.loads(row["input_json"])),
            status=row["status"],
            final_report=FinalReport.model_validate(json.loads(final_raw)) if final_raw else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_review(
        self,
        review_id: str,
        *,
        status: str | None = None,
        final_report: FinalReport | dict[str, Any] | None = None,
    ) -> ReviewRecord:
        current = self.get_review(review_id)
        next_status = status or current.status
        final_json = None
        if final_report is None:
            final_json = (
                json.dumps(current.final_report.model_dump(mode="json"))
                if current.final_report is not None
                else None
            )
        else:
            report = final_report if isinstance(final_report, FinalReport) else FinalReport.model_validate(final_report)
            final_json = json.dumps(report.model_dump(mode="json"))
        with self._connect() as conn:
            conn.execute(
                "UPDATE reviews SET status = ?, final_report_json = ?, updated_at = ? WHERE id = ?",
                (next_status, final_json, now_iso(), review_id),
            )
            conn.commit()
        return self.get_review(review_id)

    def create_event(self, payload: AgentEventCreate | dict[str, Any]) -> AgentEvent:
        event = payload if isinstance(payload, AgentEventCreate) else AgentEventCreate.model_validate(payload)
        event_id = str(uuid.uuid4())
        timestamp = now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_events (
                    id, review_id, agent_key, agent_name, event_type, status, summary,
                    payload_json, source_agents_json, handoff_to_json, band_room_id,
                    band_message_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    event.review_id,
                    event.agent_key,
                    event.agent_name,
                    event.event_type,
                    event.status,
                    event.summary,
                    json.dumps(event.payload),
                    json.dumps(event.source_agents),
                    json.dumps(event.handoff_to),
                    event.band_room_id,
                    event.band_message_id,
                    timestamp,
                ),
            )
            conn.commit()
        return AgentEvent(id=event_id, created_at=timestamp, **event.model_dump(mode="json"))

    def list_events(self, review_id: str) -> list[AgentEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_events WHERE review_id = ? ORDER BY created_at ASC",
                (review_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def reset(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM agent_events")
            conn.execute("DELETE FROM reviews")
            conn.commit()

    def _row_to_event(self, row: sqlite3.Row) -> AgentEvent:
        return AgentEvent(
            id=row["id"],
            review_id=row["review_id"],
            agent_key=row["agent_key"],
            agent_name=row["agent_name"],
            event_type=row["event_type"],
            status=row["status"],
            summary=row["summary"],
            payload=json.loads(row["payload_json"]),
            source_agents=json.loads(row["source_agents_json"]),
            handoff_to=json.loads(row["handoff_to_json"]),
            band_room_id=row["band_room_id"],
            band_message_id=row["band_message_id"],
            created_at=row["created_at"],
        )


_db: Database | None = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
