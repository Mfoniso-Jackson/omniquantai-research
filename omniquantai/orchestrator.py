from dataclasses import asdict
from typing import Any, Dict
from uuid import uuid4

from .agents import (
    EvidenceAggregator,
    ExplanationAgent,
    HypothesisGenerator,
    MacroAgent,
    MarketAgent,
    NewsAgent,
    OrchestratorAgent,
    RecommendationAgent,
    RiskAnalysisAgent,
)
from .models import ResearchRun, utc_now
from .providers import provider_mode


WORKFLOW = [
    "User Request",
    "Orchestrator Agent",
    "Market Agent",
    "News Agent",
    "Macro Agent",
    "Evidence Aggregator",
    "Hypothesis Generator",
    "Risk Analysis Agent",
    "Recommendation Agent",
    "Explanation Agent",
    "Final Research Report",
]


class OmniQuantOrchestrator:
    def __init__(self, store):
        self.store = store
        self.orchestrator = OrchestratorAgent()
        self.market = MarketAgent()
        self.news = NewsAgent()
        self.macro = MacroAgent()
        self.aggregator = EvidenceAggregator()
        self.hypotheses = HypothesisGenerator()
        self.risk = RiskAnalysisAgent()
        self.recommendation = RecommendationAgent()
        self.explanation = ExplanationAgent()

    def run_research(self, query: str) -> Dict[str, Any]:
        asset = self.orchestrator.parse_request(query)
        market = self.market.run(asset)
        news = self.news.run(asset)
        macro = self.macro.run(asset)
        evidence = self.aggregator.run(market, news, macro)
        hypotheses = self.hypotheses.run(asset, evidence)
        risks = self.risk.run(market, macro)
        recommendation = self.recommendation.run(hypotheses, risks)
        explanation = self.explanation.run(asset, evidence, hypotheses, risks, recommendation)

        run = ResearchRun(
            run_id=str(uuid4()),
            created_at=utc_now(),
            query=query,
            asset=asset,
            market=market,
            news=news,
            macro=macro,
            evidence=evidence,
            hypotheses=hypotheses,
            risks=risks,
            recommendation=recommendation,
            explanation=explanation,
            workflow=WORKFLOW,
        )
        payload = asdict(run)
        payload["provider_mode"] = provider_mode()
        self.store.save(payload)
        return payload

    def run_scenario(self, scenario: str, run_id: str = None) -> Dict[str, Any]:
        base = self.store.get(run_id) if run_id else self.store.latest()
        if not base:
            raise ValueError("Run initial research before asking a scenario question.")

        scenario_context = self._parse_scenario(scenario)
        asset = base["asset"]
        market = base["market"]
        news = base["news"]
        macro = dict(base["macro"])

        if scenario_context.get("rate_shock_bps"):
            macro["interest_rate_environment"] = "Restrictive and tightening after a 100 bps upward shock"
            macro["central_bank_outlook"] = "Higher policy rates increase discount-rate pressure and reduce tolerance for premium valuations"
            macro["asset_specific_macro_risks"] = list(macro["asset_specific_macro_risks"]) + [
                "Scenario shock: a 1% rate increase makes long-duration growth cash flows less valuable today."
            ]

        evidence = self.aggregator.run(market, news, macro)
        if scenario_context.get("rate_shock_bps"):
            evidence.append(
                {
                    "stance": "bearish",
                    "claim": "Scenario shock raises discount-rate pressure",
                    "strength": "high",
                    "source": "Macro Agent",
                    "detail": "A 100 bps rate increase typically weighs on high-multiple growth equities.",
                }
            )

        from .models import Evidence

        normalized = [item if isinstance(item, Evidence) else Evidence(**item) for item in evidence]
        hypotheses = self.hypotheses.run(asset, normalized, scenario_context)
        risks = self.risk.run(market, macro, scenario_context)
        recommendation = self.recommendation.run(hypotheses, risks, scenario_context)
        explanation = self.explanation.run(asset, normalized, hypotheses, risks, recommendation, scenario_context)

        scenario_run = ResearchRun(
            run_id=str(uuid4()),
            created_at=utc_now(),
            query=f"{base['query']} | Scenario: {scenario}",
            asset=asset,
            market=market,
            news=news,
            macro=macro,
            evidence=normalized,
            hypotheses=hypotheses,
            risks=risks,
            recommendation=recommendation,
            explanation=explanation,
            workflow=WORKFLOW,
        )
        payload = asdict(scenario_run)
        payload["base_run_id"] = base["run_id"]
        payload["scenario"] = scenario
        payload["provider_mode"] = provider_mode()
        self.store.save(payload)
        return payload

    def _parse_scenario(self, scenario: str) -> Dict[str, Any]:
        lowered = scenario.lower()
        if "interest" in lowered and ("1%" in lowered or "100" in lowered or "one percent" in lowered):
            return {"rate_shock_bps": 100}
        if "rate" in lowered and ("rise" in lowered or "increase" in lowered or "higher" in lowered):
            return {"rate_shock_bps": 100}
        return {"custom": scenario}
