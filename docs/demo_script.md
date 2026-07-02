# OmniQuantAI Demo Script

## 1. Problem

Investment research is fragmented and slow. Portfolio teams need market, news, macro, and risk views, but those workflows often live in separate tools.

## 2. Solution

OmniQuantAI creates a market where specialist agents compete to sell financial intelligence. A buyer agent broadcasts a research request, seller agents bid, the buyer selects the best value, the winning agent delivers research, and settlement is represented through a Solana devnet escrow reference.

## 3. Request

Run:

```text
Should our fund increase exposure to Nvidia over the next 6 months?
```

## 4. Seller Bids

Show the Market Analyst, News & Earnings, Macro Risk, and Portfolio Risk bids with prices, speed, confidence, and bid reasoning.

## 5. Buyer Selection

Explain that the buyer does not choose the cheapest seller. It scores relevance, expected quality, confidence, domain fit, delivery time, price, and explanation quality.

## 6. Escrow

Show the Solana devnet escrow status and reference link. In this repo the escrow reference is simulated because no existing Solana adapter was present.

## 7. Delivered Intelligence

Show the winning seller report with evidence, bullish and bearish points, risks, confidence, recommendation contribution, and disclaimer.

## 8. Final Recommendation

Show the final OmniQuantAI synthesis: evidence table, bull/base/bear hypotheses, risk analysis, recommendation, confidence, human approval reminder, and not-financial-advice disclaimer.

## 9. Close

This is the foundation for an autonomous financial intelligence economy where agents can earn by producing useful research.
