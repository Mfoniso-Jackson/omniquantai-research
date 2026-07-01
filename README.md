# OmniQuantAI MVP

OmniQuantAI is an autonomous financial research and portfolio intelligence agent for investment teams that reduces the time needed to produce evidence-backed investment recommendations from hours to minutes.

This hackathon MVP does not execute trades. It produces human-reviewable research, risk analysis, and portfolio recommendations with uncertainty, counterarguments, and a required human-in-the-loop reminder.

## Run Locally

```bash
python3 app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

No dependencies are required beyond Python 3.9+. The app uses deterministic mock providers by default and can use live providers when optional API keys are present:

```bash
export ALPHA_VANTAGE_API_KEY=...
export NEWS_API_KEY=...
export FRED_API_KEY=...
python3 app.py
```

If a live provider fails or a key is absent, OmniQuantAI falls back to deterministic mock data so the demo remains reliable.

## Demo Prompts

Initial prompt:

```text
Analyse Nvidia as a long-term investment.
```

Follow-up scenario:

```text
What if interest rates increase by 1%?
```

Expected behavior: the scenario raises macro risk, lowers the bull-case probability, increases the bear-case probability, and can shift the recommendation from BUY to HOLD with lower confidence and tighter sizing guidance.

Optional portfolio context:

```text
Current weight: 3.5%
Max weight: 7.5%
Mandate: Long-term growth portfolio
```

The recommendation uses this context to adjust position-sizing language and flag when current exposure is already at or above the stated cap.

Use **Export Memo** after a run to download a Markdown investment committee memo.

## Workflow

```text
User Request
-> Orchestrator Agent
-> Market Agent
-> News Agent
-> Macro Agent
-> Evidence Aggregator
-> Hypothesis Generator
-> Risk Analysis Agent
-> Recommendation Agent
-> Explanation Agent
-> Final Research Report
```

## Files

- `app.py`: local HTTP server and API routes.
- `omniquantai/agents.py`: modular agent implementations.
- `omniquantai/orchestrator.py`: end-to-end workflow coordination.
- `omniquantai/providers.py`: optional live providers for Alpha Vantage, NewsAPI, and FRED with deterministic mock fallback.
- `omniquantai/exporters.py`: Markdown investment committee memo export.
- `omniquantai/models.py`: research dataclasses.
- `omniquantai/storage.py`: JSON run persistence.
- `static/`: polished browser UI.
- `ARCHITECTURE.md`: architecture summary.
- `SAMPLE_REPORT.md`: sample Nvidia research output.
- `DEMO_SCRIPT.md`: short hackathon judge script.

## Product Guardrails

- No trade execution.
- No guaranteed returns.
- Human approval is always required before portfolio action.
- Recommendations include risks, counterarguments, and invalidation triggers.
- Evidence includes source labels, timestamps, and citations where live providers return URLs.
- Live or mock data should be independently verified before real investment use.
