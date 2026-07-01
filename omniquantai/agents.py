from typing import Any, Dict, List

from .models import Evidence, Hypothesis, Recommendation
from .providers import MockMacroProvider, MockMarketProvider, MockNewsProvider


class OrchestratorAgent:
    def parse_request(self, query: str) -> Dict[str, str]:
        lowered = query.lower()
        if "nvidia" in lowered or "nvda" in lowered:
            return {"ticker": "NVDA", "company": "Nvidia", "asset_class": "Equity"}

        token = query.replace("?", " ").replace(".", " ").split()
        ticker = next((part.strip(",").upper() for part in token if 1 <= len(part.strip(",")) <= 5 and part.strip(",").isalpha()), "DEMO")
        company = ticker if ticker != "DEMO" else "Demo Asset"
        return {"ticker": ticker, "company": company, "asset_class": "Equity"}


class MarketAgent:
    def __init__(self, provider=None):
        self.provider = provider or MockMarketProvider()

    def run(self, asset: Dict[str, str]) -> Dict[str, Any]:
        return self.provider.get_market_snapshot(asset["ticker"], asset["company"])


class NewsAgent:
    def __init__(self, provider=None):
        self.provider = provider or MockNewsProvider()

    def run(self, asset: Dict[str, str]) -> Dict[str, Any]:
        return self.provider.get_news_snapshot(asset["ticker"], asset["company"])


class MacroAgent:
    def __init__(self, provider=None):
        self.provider = provider or MockMacroProvider()

    def run(self, asset: Dict[str, str]) -> Dict[str, Any]:
        return self.provider.get_macro_snapshot(asset["ticker"], asset["company"])


class EvidenceAggregator:
    def run(self, market: Dict[str, Any], news: Dict[str, Any], macro: Dict[str, Any]) -> List[Evidence]:
        evidence = [
            Evidence("bullish", "Positive long-term momentum", "medium", "Market Agent", market["trend_summary"]),
            Evidence("bearish", "Premium valuation leaves less room for disappointment", "high", "Market Agent", market["valuation_snapshot"]),
            Evidence("bullish", "AI infrastructure demand remains a structural revenue driver", "high", "News Agent", news["recent_news"][0]),
            Evidence("neutral", "Analyst debate focuses on durability of the current growth curve", "medium", "News Agent", news["analyst_commentary"]),
            Evidence("bearish", "Higher real rates could compress multiples", "medium", "Macro Agent", macro["asset_specific_macro_risks"][0]),
            Evidence("neutral", "Central bank path remains data dependent", "medium", "Macro Agent", macro["central_bank_outlook"]),
        ]
        return evidence


class HypothesisGenerator:
    def run(self, asset: Dict[str, str], evidence: List[Evidence], scenario: Dict[str, Any] = None) -> List[Hypothesis]:
        rate_shock = bool(scenario and scenario.get("rate_shock_bps", 0) >= 100)
        bull_prob = 36 if not rate_shock else 29
        base_prob = 44 if not rate_shock else 45
        bear_prob = 20 if not rate_shock else 26
        company = asset["company"]
        return [
            Hypothesis(
                "Bull case",
                f"{company} compounds earnings as AI infrastructure demand broadens and margins remain resilient.",
                [item.claim for item in evidence if item.stance == "bullish"],
                [item.claim for item in evidence if item.stance == "bearish"],
                bull_prob,
                "Medium",
            ),
            Hypothesis(
                "Base case",
                f"{company} remains a high-quality long-term holding, but returns moderate as valuation catches up with fundamentals.",
                [item.claim for item in evidence if item.stance in {"bullish", "neutral"}],
                ["Premium valuation limits near-term upside asymmetry"],
                base_prob,
                "Medium-high",
            ),
            Hypothesis(
                "Bear case",
                f"Growth expectations reset lower because capex digestion, competition, or macro tightening weakens investor appetite.",
                [item.claim for item in evidence if item.stance == "bearish"],
                [item.claim for item in evidence if item.stance == "bullish"],
                bear_prob,
                "Medium",
            ),
        ]


class RiskAnalysisAgent:
    def run(self, market: Dict[str, Any], macro: Dict[str, Any], scenario: Dict[str, Any] = None) -> Dict[str, Any]:
        rate_shock = scenario and scenario.get("rate_shock_bps", 0) >= 100
        macro_risk = "High" if rate_shock else "Medium"
        downside = "Multiple compression plus slower AI capex could create a 25-35% drawdown scenario."
        if rate_shock:
            downside = "A 100 bps rate increase raises discount-rate pressure and could push the downside case toward 30-40%."

        return {
            "market_risk": f"{market['volatility']}; position sizing should assume sharp factor reversals.",
            "valuation_risk": market["valuation_snapshot"],
            "macro_risk": f"{macro_risk}: {macro['central_bank_outlook']}",
            "liquidity_risk": market["liquidity"],
            "concentration_risk": "Customer and supplier concentration should be monitored, especially hyperscaler demand and advanced packaging capacity.",
            "downside_scenarios": [
                downside,
                "Export restrictions or supply constraints delay revenue conversion.",
                "Competitive accelerators reduce pricing power faster than expected.",
            ],
            "invalidation_triggers": [
                "Data center growth decelerates for two consecutive reporting periods.",
                "Gross margins fall materially without a clear temporary cause.",
                "AI capex commentary from major customers turns cautious.",
                "Real rates rise further while earnings revisions flatten.",
            ],
        }


class RecommendationAgent:
    def run(self, hypotheses: List[Hypothesis], risks: Dict[str, Any], scenario: Dict[str, Any] = None) -> Recommendation:
        rate_shock = scenario and scenario.get("rate_shock_bps", 0) >= 100
        base = next(item for item in hypotheses if item.name == "Base case")
        bull = next(item for item in hypotheses if item.name == "Bull case")
        bear = next(item for item in hypotheses if item.name == "Bear case")

        if rate_shock:
            action = "HOLD"
            confidence = 64
            sizing = "Maintain existing strategic exposure; avoid adding until valuation or rate pressure improves."
        elif bull.probability + base.probability >= 75 and bear.probability <= 22:
            action = "BUY"
            confidence = 72
            sizing = "Add gradually up to a risk-budgeted core position; avoid oversized single-name exposure."
        else:
            action = "HOLD"
            confidence = 66
            sizing = "Keep exposure close to benchmark or mandate target until evidence improves."

        return Recommendation(
            action,
            confidence,
            sizing,
            "3-5 years, reviewed after earnings and major macro shifts",
            [
                "Use staged entries rather than a single full allocation.",
                "Set review triggers around earnings revisions, margins, and macro rates.",
                "Cap single-name exposure according to mandate concentration limits.",
            ],
            "This is research support only. A human investment professional must review before any portfolio action.",
        )


class ExplanationAgent:
    def run(
        self,
        asset: Dict[str, str],
        evidence: List[Evidence],
        hypotheses: List[Hypothesis],
        risks: Dict[str, Any],
        recommendation: Recommendation,
        scenario: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        scenario_note = None
        if scenario:
            scenario_note = "Scenario applied: interest rates increase by 1%, raising macro risk and lowering bull-case probability."

        return {
            "executive_summary": (
                f"OmniQuantAI rates {asset['company']} ({asset['ticker']}) as {recommendation.action}. "
                "The thesis is supported by durable AI demand and market leadership, but valuation and macro sensitivity require disciplined sizing."
            ),
            "key_evidence": [f"{item.stance.title()}: {item.claim} ({item.strength}, {item.source})" for item in evidence],
            "hypothesis_summary": [
                f"{item.name}: {item.probability}% probability, {item.confidence} confidence. {item.thesis}"
                for item in hypotheses
            ],
            "risk_summary": risks,
            "recommendation_rationale": (
                f"The recommendation is {recommendation.action} with {recommendation.confidence_score}/100 confidence because "
                "the combined bull and base cases outweigh the bear case, while risks are meaningful enough to require staged exposure."
            ),
            "counterarguments": [
                "The market may already discount several years of exceptional AI growth.",
                "Competitive pressure or customer capex digestion could reset expectations.",
                "Macro tightening can reduce willingness to pay premium multiples for growth.",
            ],
            "what_would_change_the_recommendation": [
                "Upgrade: stronger-than-expected earnings revisions with stable or lower valuation multiples.",
                "Downgrade: slowing data center growth, margin compression, or a sustained increase in real rates.",
                "Reduce/Sell: thesis invalidation from customer demand weakness or structural loss of pricing power.",
            ],
            "scenario_note": scenario_note,
            "disclaimer": "Not financial advice. This MVP provides research support for human review and must not execute trades.",
        }
