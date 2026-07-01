import os
import json
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_json(url: str, timeout: int = 8) -> Dict[str, Any]:
    request = Request(url, headers={"User-Agent": "OmniQuantAI-Research/0.2"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def source(name: str, url: str = "") -> Dict[str, str]:
    return {"name": name, "url": url, "timestamp": utc_now()}


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
                "source_metadata": source("Mock Market Provider"),
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
            "source_metadata": source("Mock Market Provider"),
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
                "source_metadata": source("Mock News Provider"),
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
            "source_metadata": source("Mock News Provider"),
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
            "source_metadata": source("Mock Macro Provider"),
        }


class AlphaVantageMarketProvider:
    def __init__(self, fallback=None):
        self.fallback = fallback or MockMarketProvider()

    def get_market_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not key:
            return self.fallback.get_market_snapshot(ticker, company)

        url = "https://www.alphavantage.co/query?" + urlencode(
            {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": key}
        )
        try:
            payload = fetch_json(url)
            quote = payload.get("Global Quote", {})
            price = float(quote.get("05. price", 0) or 0)
            change_pct = quote.get("10. change percent", "n/a")
            if not price:
                raise ValueError("Alpha Vantage quote was empty")
            return {
                "price": round(price, 2),
                "currency": "USD",
                "recent_performance": f"Latest quote change: {change_pct}",
                "volatility": "Live quote connected; realized volatility requires historical provider extension",
                "momentum": f"Latest session change is {change_pct}",
                "valuation_snapshot": "Live valuation multiples not connected; use filings or a fundamentals provider before investment action",
                "trend_summary": "Live quote available; trend should be confirmed with historical price data.",
                "liquidity": f"Latest volume: {quote.get('06. volume', 'n/a')}",
                "source_metadata": source("Alpha Vantage Global Quote", url),
            }
        except Exception as exc:
            snapshot = self.fallback.get_market_snapshot(ticker, company)
            snapshot["provider_warning"] = f"Alpha Vantage failed; using mock fallback: {exc}"
            return snapshot


class NewsApiProvider:
    def __init__(self, fallback=None):
        self.fallback = fallback or MockNewsProvider()

    def get_news_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        key = os.getenv("NEWS_API_KEY")
        if not key:
            return self.fallback.get_news_snapshot(ticker, company)

        query = f'"{company}" OR {ticker}'
        url = "https://newsapi.org/v2/everything?" + urlencode(
            {"q": query, "sortBy": "publishedAt", "language": "en", "pageSize": 5, "apiKey": key}
        )
        try:
            payload = fetch_json(url)
            articles = payload.get("articles", [])[:5]
            if not articles:
                raise ValueError("NewsAPI returned no articles")
            headlines = [item.get("title", "Untitled article") for item in articles[:3]]
            first_url = articles[0].get("url", url)
            return {
                "recent_news": headlines,
                "earnings_themes": [
                    "Live headlines connected; earnings themes should be validated against filings and transcripts.",
                    "Monitor management commentary, guidance revisions, and analyst estimate changes.",
                ],
                "analyst_commentary": "Live news connected; dedicated analyst feed not configured in this MVP.",
                "sector_developments": "Derived from recent headlines; add sector-specific data feeds for production use.",
                "source_metadata": source("NewsAPI recent articles", first_url),
            }
        except Exception as exc:
            snapshot = self.fallback.get_news_snapshot(ticker, company)
            snapshot["provider_warning"] = f"NewsAPI failed; using mock fallback: {exc}"
            return snapshot


class FredMacroProvider:
    def __init__(self, fallback=None):
        self.fallback = fallback or MockMacroProvider()

    def get_macro_snapshot(self, ticker: str, company: str) -> Dict[str, Any]:
        key = os.getenv("FRED_API_KEY")
        if not key:
            return self.fallback.get_macro_snapshot(ticker, company)

        base = "https://api.stlouisfed.org/fred/series/observations"
        try:
            fed_url = base + "?" + urlencode(
                {"series_id": "FEDFUNDS", "api_key": key, "file_type": "json", "sort_order": "desc", "limit": 1}
            )
            cpi_url = base + "?" + urlencode(
                {"series_id": "CPIAUCSL", "api_key": key, "file_type": "json", "sort_order": "desc", "limit": 2}
            )
            fed = fetch_json(fed_url)
            cpi = fetch_json(cpi_url)
            fed_value = fed.get("observations", [{}])[0].get("value", "n/a")
            cpi_obs = cpi.get("observations", [])
            inflation_text = "Latest CPI observation unavailable"
            if cpi_obs:
                inflation_text = f"Latest CPI index reading: {cpi_obs[0].get('value', 'n/a')}"
            return {
                "interest_rate_environment": f"Latest effective federal funds rate from FRED: {fed_value}%",
                "inflation_context": inflation_text,
                "central_bank_outlook": "Live FRED data connected; policy interpretation remains model-generated and requires human review",
                "asset_specific_macro_risks": [
                    "Higher real rates can compress valuation multiples for long-duration growth assets.",
                    "Inflation surprises can change discount-rate assumptions and margin expectations.",
                    "Macro data should be reviewed against current central bank communication.",
                ],
                "source_metadata": source("FRED FEDFUNDS/CPIAUCSL", "https://fred.stlouisfed.org/"),
            }
        except Exception as exc:
            snapshot = self.fallback.get_macro_snapshot(ticker, company)
            snapshot["provider_warning"] = f"FRED failed; using mock fallback: {exc}"
            return snapshot


def provider_mode() -> str:
    keys = ["ALPHA_VANTAGE_API_KEY", "NEWS_API_KEY", "FRED_API_KEY"]
    configured = [key for key in keys if os.getenv(key)]
    if configured:
        return f"live-if-available mode; detected optional keys: {', '.join(configured)}"
    return "deterministic mock data; no external API keys detected"
