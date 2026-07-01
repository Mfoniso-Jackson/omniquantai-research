from typing import Any, Dict


def render_investment_committee_memo(run: Dict[str, Any]) -> str:
    asset = run["asset"]
    recommendation = run["recommendation"]
    explanation = run["explanation"]
    portfolio = run.get("portfolio_context") or {}

    lines = [
        f"# Investment Committee Memo: {asset['company']} ({asset['ticker']})",
        "",
        f"Run ID: {run['run_id']}",
        f"Created: {run['created_at']}",
        "",
        "## Executive Summary",
        "",
        explanation["executive_summary"],
        "",
        "## Recommendation",
        "",
        f"- Action: {recommendation['action']}",
        f"- Confidence: {recommendation['confidence_score']}/100",
        f"- Position sizing: {recommendation['position_sizing']}",
        f"- Time horizon: {recommendation['time_horizon']}",
        "",
        "## Portfolio Context",
        "",
    ]

    if portfolio:
        for key, value in portfolio.items():
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    else:
        lines.append("- No portfolio context supplied.")

    lines.extend(["", "## Key Evidence", ""])
    for item in run["evidence"]:
        citation = f" Source: {item.get('source_url')}" if item.get("source_url") else ""
        timestamp = f" Timestamp: {item.get('timestamp')}" if item.get("timestamp") else ""
        detail = str(item["detail"]).rstrip(".")
        lines.append(f"- {item['stance'].title()} ({item['strength']}): {item['claim']} - {detail}.{citation}{timestamp}")

    lines.extend(["", "## Hypotheses", ""])
    for item in run["hypotheses"]:
        lines.append(f"- {item['name']} ({item['probability']}%, {item['confidence']}): {item['thesis']}")

    lines.extend(["", "## Risk Analysis", ""])
    risks = run["risks"]
    for key, value in risks.items():
        if isinstance(value, list):
            lines.append(f"- {key.replace('_', ' ').title()}:")
            for child in value:
                lines.append(f"  - {child}")
        else:
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")

    lines.extend(["", "## Counterarguments", ""])
    for item in explanation["counterarguments"]:
        lines.append(f"- {item}")

    lines.extend(["", "## What Would Change The Recommendation", ""])
    for item in explanation["what_would_change_the_recommendation"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Disclaimer", "", explanation["disclaimer"], ""])
    return "\n".join(lines)
