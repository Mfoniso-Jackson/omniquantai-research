from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


REQUEST = "Should our fund increase exposure to Nvidia over the next 6 months?"


@dataclass
class SellerPersona:
    id: str
    name: str
    domain: str
    price_sol: float
    speed_seconds: int
    relevance: int
    expected_quality: int
    confidence: int
    domain_fit: int
    explanation_quality: int
    bid_reasoning: str


SELLERS = [
    SellerPersona(
        "market-analyst",
        "Market Analyst Agent",
        "Price action, momentum, valuation snapshot, technical market view",
        0.18,
        18,
        92,
        86,
        78,
        96,
        82,
        "NVDA has strong momentum but valuation sensitivity makes market structure essential to the 6-month question.",
    ),
    SellerPersona(
        "news-earnings",
        "News & Earnings Agent",
        "Recent news, earnings themes, analyst sentiment, company developments",
        0.16,
        22,
        90,
        88,
        80,
        94,
        86,
        "The request depends heavily on AI demand, earnings revisions, and hyperscaler capex commentary.",
    ),
    SellerPersona(
        "macro-risk",
        "Macro Risk Agent",
        "Rates, inflation, liquidity, sector and macro risk assessment",
        0.12,
        16,
        82,
        80,
        74,
        88,
        78,
        "NVDA is a long-duration growth asset, so rates and liquidity can change the risk/reward quickly.",
    ),
    SellerPersona(
        "portfolio-risk",
        "Portfolio Risk Agent",
        "Downside scenarios, concentration risk, risk controls, invalidation triggers",
        0.20,
        24,
        95,
        92,
        84,
        98,
        90,
        "A fund exposure decision needs position sizing, drawdown scenarios, concentration controls, and thesis invalidation triggers.",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def score_bid(seller: SellerPersona) -> Dict[str, Any]:
    price_score = max(0, 100 - int(seller.price_sol * 240))
    speed_score = max(0, 100 - seller.speed_seconds)
    weighted = round(
        seller.relevance * 0.18
        + seller.expected_quality * 0.2
        + seller.confidence * 0.16
        + seller.domain_fit * 0.18
        + speed_score * 0.1
        + price_score * 0.08
        + seller.explanation_quality * 0.1,
        2,
    )
    return {
        "value_score": weighted,
        "price_score": price_score,
        "speed_score": speed_score,
        "decision": "accepted" if weighted >= 80 else "rejected",
        "reason": (
            f"Scores {weighted}/100 after weighting relevance, expected quality, confidence, "
            f"domain fit, speed, price, and explanation quality."
        ),
    }


def deliver_service(seller: SellerPersona, request: str) -> Dict[str, Any]:
    reports = {
        "market-analyst": {
            "key_evidence": ["NVDA momentum remains positive", "Valuation premium raises downside sensitivity"],
            "bullish_points": ["AI accelerator demand supports trend", "Liquidity is deep for institutional sizing"],
            "bearish_points": ["Multiple compression risk is elevated", "Short-term expectations are demanding"],
            "risks": ["Earnings miss", "Factor rotation out of mega-cap growth"],
            "recommendation_contribution": "Constructive but add gradually; avoid chasing extended rallies.",
        },
        "news-earnings": {
            "key_evidence": ["AI capex commentary remains supportive", "Earnings debate centers on durability of data center growth"],
            "bullish_points": ["Hyperscaler demand supports backlog visibility", "Product cycle can extend leadership"],
            "bearish_points": ["Export controls can pressure revenue", "Customer concentration remains material"],
            "risks": ["Guidance reset", "Supply constraints", "Analyst downgrade cycle"],
            "recommendation_contribution": "Positive if earnings revisions keep rising and capex commentary stays firm.",
        },
        "macro-risk": {
            "key_evidence": ["Higher rates pressure long-duration growth multiples", "Liquidity conditions affect risk appetite"],
            "bullish_points": ["Stable or falling rates would support premium growth assets"],
            "bearish_points": ["A rate shock can compress multiples even if fundamentals remain strong"],
            "risks": ["Inflation surprise", "Higher real rates", "Dollar strength"],
            "recommendation_contribution": "Hold/add only with rate sensitivity controls and scenario review.",
        },
        "portfolio-risk": {
            "key_evidence": ["Single-name concentration can dominate portfolio risk", "Downside case requires explicit sizing discipline"],
            "bullish_points": ["Core position can be justified for long-term growth mandates"],
            "bearish_points": ["Adding above mandate cap creates asymmetric portfolio risk"],
            "risks": ["25-40% drawdown scenario", "Crowded positioning", "Thesis invalidation after two weak quarters"],
            "recommendation_contribution": "Increase only if current weight is below cap; use staged entries and review triggers.",
        },
    }
    report = reports[seller.id]
    return {
        "agent_name": seller.name,
        "request_understood": request,
        "confidence_score": seller.confidence,
        "what_would_change_view": [
            "Material earnings revision change",
            "Major shift in interest-rate expectations",
            "Evidence of AI capex slowdown or acceleration",
        ],
        "disclaimer": "Not financial advice. This is human-reviewable research and does not execute trades.",
        **report,
    }


def synthesize(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "executive_summary": (
            "OmniQuantAI recommends HOLD-to-BUY bias for increasing NVDA exposure over 6 months, "
            "but only if position size remains below mandate cap and macro sensitivity is monitored."
        ),
        "evidence_table": [
            {"stance": "bullish", "evidence": "AI demand and product-cycle leadership remain supportive", "source": report["agent_name"]},
            {"stance": "bearish", "evidence": "Premium valuation and rate sensitivity limit margin of safety", "source": report["agent_name"]},
            {"stance": "neutral", "evidence": "Outcome depends on earnings revisions and hyperscaler capex", "source": report["agent_name"]},
        ],
        "hypotheses": [
            {"case": "Bull", "probability": 34, "thesis": "AI demand compounds and earnings revisions rise."},
            {"case": "Base", "probability": 46, "thesis": "Fundamentals stay strong but returns moderate from high valuation."},
            {"case": "Bear", "probability": 20, "thesis": "Rates, competition, or capex digestion reset expectations."},
        ],
        "risk_analysis": report["risks"],
        "recommendation": "HOLD",
        "confidence_score": 72,
        "human_approval_reminder": "Human portfolio manager approval required before any allocation change.",
        "disclaimer": "Not financial advice. OmniQuantAI does not execute trades.",
    }


def run_marketplace_demo(request: str = REQUEST) -> Dict[str, Any]:
    session_id = f"coral-session-{uuid4().hex[:10]}"
    bids = []
    for seller in SELLERS:
        bid = asdict(seller)
        bid["bid_id"] = f"bid-{seller.id}-{uuid4().hex[:6]}"
        bid.update(score_bid(seller))
        bids.append(bid)

    winner = max(bids, key=lambda item: item["value_score"])
    seller = next(item for item in SELLERS if item.id == winner["id"])
    delivery = deliver_service(seller, request)
    reference = uuid4().hex
    escrow = {
        "network": "solana-devnet",
        "status": "released",
        "amount_sol": winner["price_sol"],
        "reference": reference,
        "settlement_link": f"https://explorer.solana.com/address/{reference}?cluster=devnet",
        "note": "Simulated devnet escrow reference in this repo; replace with the existing Solana escrow adapter when available.",
    }
    synthesis = synthesize(delivery)
    return {
        "created_at": utc_now(),
        "buyer_request": request,
        "coralos": {
            "session_id": session_id,
            "coordination_pattern": "buyer broadcast -> seller bid messages -> buyer selection -> seller delivery",
            "simulated": True,
        },
        "bids": bids,
        "selection": {
            "selected_winner": winner,
            "final_reasoning": (
                f"{winner['name']} wins because it has the strongest value score, domain fit, "
                "confidence, and explanation quality for a fund exposure decision."
            ),
            "rejected_bids": [item for item in bids if item["id"] != winner["id"]],
        },
        "escrow": escrow,
        "delivery": delivery,
        "final_report": synthesis,
    }
