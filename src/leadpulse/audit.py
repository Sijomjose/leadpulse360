import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from leadpulse.routing import RoutingDecision
from leadpulse.schemas import InboundLead
from leadpulse.scoring import ScoreResult

DEFAULT_AUDIT_LOG_PATH = Path("data/decision_audit_trail.jsonl")


class LeadAuditRecord(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    lead: InboundLead
    score_result: ScoreResult
    routing_decision: RoutingDecision


class AuditLogger:
    def __init__(self, log_path: Path = DEFAULT_AUDIT_LOG_PATH):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_decision(
        self, lead: InboundLead, score_result: ScoreResult, routing_decision: RoutingDecision
    ) -> LeadAuditRecord:
        record = LeadAuditRecord(
            lead=lead, score_result=score_result, routing_decision=routing_decision
        )
        with open(self.log_path, mode="a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")
        return record

    def read_records(self) -> List[LeadAuditRecord]:
        if not self.log_path.exists():
            return []
        records = []
        with open(self.log_path, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(LeadAuditRecord.model_validate_json(line))
        return records
