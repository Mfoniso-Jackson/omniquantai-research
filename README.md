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

## Deploy

The app is deployment-ready for simple Python web hosts. It binds to `0.0.0.0` and reads the platform `PORT` environment variable.

### Render

1. Create a new Render Web Service from this GitHub repo.
2. Render can use `render.yaml`, or configure manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python3 app.py`
   - Health check path: `/health`
3. Add optional environment variables for live providers:
   - `ALPHA_VANTAGE_API_KEY`
   - `NEWS_API_KEY`
   - `FRED_API_KEY`

### Railway

Railway can use the included `Procfile`:

```bash
web: python3 app.py
```

Add the optional API keys in Railway variables if you want live data.

### Fly.io

The included `fly.toml` runs the app on port `8080`. After installing the Fly CLI:

```bash
fly launch
fly deploy
```

For a hackathon demo, Render is usually the quickest path.

## OmniQuantAI Demo

OmniQuantAI is a no-trade autonomous financial intelligence marketplace. A buyer agent broadcasts a research request, specialist seller agents compete to deliver the work, the buyer selects the best value, and the winning agent delivers human-reviewable financial intelligence.

This fits **agents that earn** because the seller agents are modeled as paid service providers. They bid with price, speed, confidence, domain fit, and reasoning. The buyer does not simply choose the cheapest seller; it selects the highest-value intelligence provider.

### CoralOS Usage

The current deployed repo did not contain existing CoralOS integration files, so the demo models the CoralOS coordination pattern in `omniquantai/marketplace.py`:

```text
buyer broadcast -> seller bid messages -> buyer selection -> seller delivery
```

The dashboard displays a CoralOS-style session id and coordination pattern. A production version should replace this simulator with the intended CoralOS session/thread/message APIs.

### Solana Escrow Usage

The current deployed repo did not contain existing Solana Pay or escrow files, so the demo preserves the settlement concept with a deterministic Solana devnet-style escrow reference. The dashboard shows:

- escrow status,
- SOL amount,
- unique reference,
- devnet reference link.

This is simulated in this repo. A production version should replace the simulator with the existing Solana escrow adapter when available.

### Run Setup

```bash
python3 app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Demo Prompt

```text
Should our fund increase exposure to Nvidia over the next 6 months?
```

### Expected Flow

1. Buyer request appears as a financial intelligence auction.
2. Market Analyst, News & Earnings, Macro Risk, and Portfolio Risk agents submit bids.
3. Buyer scores bids by relevance, quality, confidence, domain fit, delivery time, price, and explanation quality.
4. A winner is selected.
5. Escrow is shown as released with a devnet-style reference link.
6. The winning seller delivers structured intelligence.
7. OmniQuantAI synthesizes a final investment thesis with recommendation, confidence, risks, human approval reminder, and not-financial-advice disclaimer.

### Limitations

- CoralOS coordination is simulated because this repository did not include CoralOS SDK/integration files.
- Solana escrow is simulated because this repository did not include a working escrow adapter.
- Market/news/macro data remains deterministic unless optional API keys are configured.
- OmniQuantAI does not execute trades.

### Future Roadmap

- Multi-winner research bundles.
- Agent reputation and slashing for low-quality delivery.
- Real CoralOS session/thread/message coordination.
- Real Solana devnet escrow adapter with refund path for failed delivery.
- Sui settlement adapter as a future payment rail.
- Portfolio-aware research requests and institution-specific mandate policies.

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
