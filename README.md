# OmniQuantAI MVP

OmniQuantAI is an autonomous financial research and portfolio intelligence agent for investment teams that reduces the time needed to produce evidence-backed investment recommendations from hours to minutes.

This hackathon MVP does not execute trades. It produces human-reviewable research, risk analysis, and portfolio recommendations with uncertainty, counterarguments, and a required human-in-the-loop reminder.

## Run Locally

```bash
python3 app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

No dependencies are required beyond Python 3.9+. The app uses deterministic mock providers unless optional market/news/macro API keys are added later.

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
- `omniquantai/providers.py`: deterministic mocked data providers and future API-key detection.
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
- Mock data should be replaced or verified with live market/news/macro sources before real investment use.
