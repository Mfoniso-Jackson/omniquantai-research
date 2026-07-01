# Architecture Summary

OmniQuantAI is structured as a modular agent pipeline with a thin local web shell.

## Runtime

The MVP runs with one command:

```bash
python3 app.py
```

`app.py` serves the static UI and exposes research, scenario, and export endpoints:

- `POST /api/research`: runs a new investment research workflow.
- `POST /api/scenario`: reruns the workflow with a follow-up scenario applied to the latest or selected run.
- `GET /api/memo?run_id=...`: downloads a Markdown investment committee memo.

## Agent Flow

1. Orchestrator Agent parses the request and identifies the asset.
2. Market Agent collects or simulates price, performance, volatility, momentum, valuation, liquidity, and trend evidence.
3. News Agent collects or simulates recent news, earnings themes, analyst commentary, and sector developments.
4. Macro Agent collects or simulates rates, inflation, central bank outlook, and macro risks.
5. Evidence Aggregator converts agent outputs into bullish, bearish, and neutral evidence with source labels, citations, and timestamps.
6. Hypothesis Generator creates bull, base, and bear hypotheses with probabilities and confidence.
7. Risk Analysis Agent evaluates market, valuation, macro, liquidity, concentration, downside, and invalidation risks.
8. Recommendation Agent produces BUY, HOLD, REDUCE, or SELL, plus confidence, sizing, time horizon, and controls. Optional portfolio context adjusts sizing language.
9. Explanation Agent produces the final professional research report with counterarguments and disclaimer.

## Data Strategy

The MVP defaults to deterministic mock data so hackathon demos are reliable offline. `providers.py` detects optional environment variables such as `ALPHA_VANTAGE_API_KEY`, `NEWS_API_KEY`, and `FRED_API_KEY`. When present, the app attempts live calls to Alpha Vantage, NewsAPI, and FRED using Python standard library HTTP utilities. Failures are captured as provider warnings and fall back to deterministic mock data.

Runs are persisted to `data/runs.json` for local inspection and scenario continuity.

## Portfolio Context

The UI accepts current position weight, maximum mandate weight, and mandate text. These inputs are stored with each run and included in recommendation sizing and memo export. The system still does not execute trades.

## Memo Export

`omniquantai/exporters.py` renders each research run as a Markdown investment committee memo containing executive summary, recommendation, portfolio context, evidence with citations/timestamps, hypotheses, risk analysis, counterarguments, change triggers, and disclaimer.

## Scenario Handling

The scenario parser recognizes rate-shock prompts such as “What if interest rates increase by 1%?” and applies a 100 bps macro shock. The workflow then revises macro evidence, hypothesis probabilities, risk severity, recommendation confidence, and sizing guidance.
