import os
from typing import Any, Dict


class MockMarketProvider:
    """Deterministic market snapshots that keep the demo reliable offline."""

    def get_market_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        ticker = ticker.upper()
        if ticker in {"NVDA", "NVIDIA"}:
            return {
                "price": 126.40,
                "currency": "USD",
                "recent_performance": "+12.8% over 3 months, +61.4% over 12 months",
                "volatility": "High; 30-day realized volatility near 42%",
                "momentum": "Positive but extended after AI infrastructure demand repricing",
                "valuation_snapshot": "Premium valuation versus semiconductors; revenue growth and margins must remain exceptional",
                "trend_summary": "Long-term uptrend intact, with short-term sensitivity to earnings revisions and rates.",
                "liquidity": "Very high large-cap liquidity",
            }

        seed = sum(ord(char) for char in ticker)
        price = round(38 + (seed % 220) * 1.13, 2)
        return {
            "price": price,
            "currency": "USD",
            "recent_performance": f"{(seed % 28) - 8:+.1f}% over 3 months, {(seed % 72) - 18:+.1f}% over 12 months",
            "volatility": "Moderate to high; profile inferred from sector and capitalization",
            "momentum": "Mixed; requires confirmation from earnings and sector flows",
            "valuation_snapshot": "Screened against growth, margin durability, and sector multiples",
            "trend_summary": "Trend evidence is directional and should be validated with live market data before action.",
            "liquidity": "Assumed adequate for institutional research demo",
        }


class MockNewsProvider:
    def get_news_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        if ticker.upper() in {"NVDA", "NVIDIA"}:
            return {
                "recent_news": [
                    "AI accelerator demand remains the central growth driver for Nvidia data center revenue.",
                    "Cloud hyperscalers continue to discuss elevated AI capex, supporting backlog visibility.",
                    "Export controls and supply chain capacity remain recurring investor concerns.",
                ],
                "earnings_themes": [
                    "Data center growth, gross margin durability, and Blackwell platform ramp.",
                    "Management commentary on supply constraints and customer concentration.",
                ],
                "analyst_commentary": "Broadly constructive, but debate centers on how long extraordinary AI infrastructure spending can compound.",
                "sector_developments": "Semiconductor leadership is concentrated in AI compute, memory, advanced packaging, and foundry capacity.",
            }

        return {
            "recent_news": [
                f"{company} has company-specific catalysts that should be verified against live filings.",
                "Sector commentary suggests investors are rewarding durable free cash flow and pricing power.",
                "News risk is treated as neutral until live sources are connected.",
            ],
            "earnings_themes": ["Revenue durability", "Margin trajectory", "Capital allocation"],
            "analyst_commentary": "Mock analyst tone is balanced with emphasis on execution risk.",
            "sector_developments": "Sector trends are simulated for this MVP and designed to be replaced by live feeds.",
        }


class MockMacroProvider:
    def get_macro_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        return {
            "interest_rate_environment": "Restrictive but potentially near the late stage of the cycle",
            "inflation_context": "Inflation has moderated from peak levels but remains relevant for discount rates and margins",
            "central_bank_outlook": "Policy path is data-dependent; higher-for-longer rates pressure long-duration growth equities",
            "asset_specific_macro_risks": [
                "Higher real rates compress valuation multiples for long-duration growth assets.",
                "Slower enterprise spending could delay AI infrastructure monetization.",
                "A stronger dollar can affect multinational revenue translation.",
            ],
        }


def provider_mode() -> str:
    keys = ["ALPHA_VANTAGE_API_KEY", "NEWS_API_KEY", "FRED_API_KEY"]
    configured = [key for key in keys if os.getenv(key)]
    if configured:
        return f"mock-first demo mode; detected optional keys: {', '.join(configured)}"
    return "deterministic mock data; no external API keys detected"
