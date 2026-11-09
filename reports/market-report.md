# Battery Market Decision Lab — first-stage results

Historical DE-LU 2024 screening. All configurations have 1 MW grid power. Monetary values are EUR, after assumed fees and linear cycling cost, before fixed costs, taxes, financing and capital expenditure.

| Capacity (MWh) | Fixed schedule margin | Perfect-foresight ceiling |
|---|---:|---:|
| 1 | 1,333.00 | 26,987.93 |
| 2 | 6,993.57 | 51,134.31 |
| 4 | 27,599.49 | 89,177.14 |

Idle earns zero. More capacity is not automatically a better investment: additional capital and fixed costs are not included. The fixed schedule is an illustrative, untrained rule, not an independently validated trading strategy. The perfect-foresight result knows every price of each delivery day and is an upper bound only for the stated daily-reset model. It is not attainable forecast revenue.

Assumptions: 90% round-trip efficiency; 10–90% SOC; EUR 1/MWh fee on both charge and discharge energy; EUR 5/MWh discharged linear wear allowance; one equivalent cycle per usable capacity per day; each day starts and ends at minimum SOC. These are editable illustrative inputs, not supplier quotes. No simultaneous charge/discharge. All trades assumed to clear at published day-ahead prices; no market impact, availability losses, imbalance or intraday/ancillary income.

Source: Energy-Charts.info; DE-LU prices attributed to Bundesnetzagentur | SMARD.de, CC BY 4.0. Data transformed into simulated dispatch and cash flows; source retrieval date/hash are in assumptions.json.

Next: agree the battery assumptions and extend to price forecasts available before bidding, chronological backtesting and uncertainty. Investment valuation is a separate later stage.