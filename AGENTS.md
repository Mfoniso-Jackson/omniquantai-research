# OmniQuantAI Agent Market

This MVP models a CoralOS-style financial intelligence marketplace.

## Buyer Agent

The buyer broadcasts:

> Should our fund increase exposure to Nvidia over the next 6 months?

It evaluates seller bids using relevance, expected quality, confidence, domain fit, delivery time, price, and explanation quality.

## Seller Agents

- Market Analyst Agent: market structure, momentum, valuation snapshot.
- News & Earnings Agent: recent news, earnings themes, analyst/company developments.
- Macro Risk Agent: rates, inflation, liquidity, macro risk.
- Portfolio Risk Agent: downside scenarios, concentration, controls, invalidation triggers.

## Settlement

The current deployed repo simulates Solana devnet escrow references because no existing escrow adapter was present in this codebase. The module is isolated in `omniquantai/marketplace.py` so a real Solana escrow adapter can replace it without changing the dashboard contract.
