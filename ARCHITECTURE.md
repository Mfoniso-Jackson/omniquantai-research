# Architecture Summary

OmniQuantAI is structured as a modular agent pipeline with a thin local web shell.

## Runtime

The MVP runs with one command:

```bash
python3 app.py
```

`app.py` serves the static UI and exposes two JSON endpoints:

- `POST /api/research`: runs a new investment research workflow.
- `POST /api/scenario`: reruns the workflow with a follow-up scenario applied to the latest or selected run.

## Agent Flow

1. Orchestrator Agent parses the request and identifies the asset.
2. Market Agent collects or simulates price, performance, volatility, momentum, valuation, liquidity, and trend evidence.
3. News Agent collects or simulates recent news, earnings themes, analyst commentary, and sector developments.
4. Macro Agent collects or simulates rates, inflation, central bank outlook, and macro risks.
5. Evidence Aggregator converts agent outputs into bullish, bearish, and neutral evidence.
6. Hypothesis Generator creates bull, base, and bear hypotheses with probabilities and confidence.
7. Risk Analysis Agent evaluates market, valuation, macro, liquidity, concentration, downside, and invalidation risks.
8. Recommendation Agent produces BUY, HOLD, REDUCE, or SELL, plus confidence, sizing, time horizon, and controls.
9. Explanation Agent produces the final professional research report with counterarguments and disclaimer.

## Data Strategy

The MVP defaults to deterministic mock data so hackathon demos are reliable offline. `providers.py` detects optional environment variables such as `ALPHA_VANTAGE_API_KEY`, `NEWS_API_KEY`, and `FRED_API_KEY`, but live integrations are intentionally left as a clean extension point.

Runs are persisted to `data/runs.json` for local inspection and scenario continuity.

## Scenario Handling

The scenario parser recognizes rate-shock prompts such as “What if interest rates increase by 1%?” and applies a 100 bps macro shock. The workflow then revises macro evidence, hypothesis probabilities, risk severity, recommendation confidence, and sizing guidance.
