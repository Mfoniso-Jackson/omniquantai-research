from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class Evidence:
    stance: str
    claim: str
    strength: str
    source: str
    detail: str
    source_url: str = ""
    timestamp: str = ""


@dataclass
class Hypothesis:
    name: str
    thesis: str
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    probability: int
    confidence: str


@dataclass
class Recommendation:
    action: str
    confidence_score: int
    position_sizing: str
    time_horizon: str
    risk_controls: List[str]
    human_approval_reminder: str


@dataclass
class ResearchRun:
    run_id: str
    created_at: str
    query: str
    asset: Dict[str, str]
    market: Dict[str, Any]
    news: Dict[str, Any]
    macro: Dict[str, Any]
    evidence: List[Evidence]
    hypotheses: List[Hypothesis]
    risks: Dict[str, Any]
    recommendation: Recommendation
    explanation: Dict[str, Any]
    portfolio_context: Dict[str, Any] = field(default_factory=dict)
    workflow: List[str] = field(default_factory=list)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
