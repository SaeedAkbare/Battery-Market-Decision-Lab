# From market analysis to decision support

Status: stage 1 implementation and verification first; subsequent stages are planned, not completed. Primary initial user: analyst comparing battery configurations. Trading decisions and investment decisions need separate evaluation.

| Gap | Deliverable | Acceptance condition |
|---|---|---|
| 1. Defined decision and timing | User, market, horizon, available information, decision and constraints | Explicit decision contract; no ambiguity between historical screening, pre-auction bidding and post-auction operation |
| 2. Battery physics | Power, energy, efficiency, SOC, connection and cycling limits | Independent conservation checks; no simultaneous charge/discharge or free terminal energy |
| 3. Decision-time data | Price history plus archived forecasts with publication/revision timestamps | Every model feature demonstrably available before its decision; no realised future fundamentals |
| 4. Realistic costs | Fees, losses, degradation, availability and applicable settlement costs | Cash-flow reconciliation; assumptions traceable to dated sources or user inputs |
| 5. Dispatch optimisation | Feasible charging/discharging schedules | Solver status checked and outputs independently validated |
| 6. Comparators | Idle, simple rule and perfect-foresight ceiling | Same physics and cost assumptions; hindsight clearly labelled |
| 7. Chronological evaluation | Walk-forward forecasts and trading simulation with untouched test period | Out-of-sample net margin, forecast error and risk versus baseline; no tuning on test results |
| 8. Uncertainty | Price/cost scenarios, downside and sensitivity | Decision stability reported; scenario bands not mislabelled as statistical confidence |
| 9. Investment economics | CAPEX, OPEX, replacement, financing, lifetime cash flows, NPV and break-even | Discounting and terminal assumptions tested; multi-year revenue scenarios; historical margin not called ROI |
| 10. Additional markets | Intraday and ancillary qualification, availability and joint dispatch | No double allocation of capacity or addition of incompatible revenue estimates |
| 11. Explainable output | Decision, reasons, uncertainty and abstention | User can inspect assumptions and recreate the result; stale data blocks recommendations |
| 12. Operational reliability | Versioned datasets/models, monitoring, recovery and paper operation | Failure tests and sustained paper results before any live execution integration |

## Development sequence

**Stage 1 — implemented first:** DE-LU 2024 historical arbitrage screening, 1 MW batteries of 1/2/4 MWh, assumed variable costs, fixed schedule and daily perfect foresight. This narrows the first deliverable; it does not complete the entire decision-support roadmap.

**Stage 2 — next discussion:** confirm battery and fee assumptions; add sensitivity to efficiency, cycle budgets and degradation costs; improve robustness across historical years and native market resolutions. Agree whether the next user is an investor screening capacity or an operator bidding day ahead.

**Stage 3 — trading track:** archived pre-decision information, simple price forecasts, walk-forward evaluation, forecast-based dispatch/bidding assumptions, imbalance and uncertainty. Published day-ahead prices may be used for post-auction operations only with actual market access and position constraints, not retroactively treated as pre-auction knowledge.

**Stage 4 — investment track:** cost scenarios, lifetime capacity fade/replacement, discounted cash flows and break-even analysis. Do not extrapolate a single historical year as a guaranteed annuity. Avoid false precision without site, interconnection and financing assumptions.

**Stage 5 — operational track:** paper operation, monitoring and audit; live orders are explicitly outside current scope.

## Reference foundations

- [NREL SAM battery model](https://sam.nrel.gov/index.php?Itemid=360&id=94&option=com_content&view=article): physics, degradation and financial-model separation.
- [Nord Pool day-ahead market](https://www.nordpoolgroup.com/en/the-power-market/Day-ahead-market/): bids precede auction outcomes.
- [Energy-Charts documentation](https://api.energy-charts.info/): timestamps, intervals, data access and licenses.

Reviewed 9 November 2026. Market rules, tariffs and supplier inputs must be rechecked for the deployment date and location.
