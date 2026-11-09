# Stage 1 model specification

Time steps are the native hourly 2024 price intervals in UTC, grouped into Europe/Berlin delivery days of 23, 24 or 25 hours. Every interval must be present. The input loader rejects duplicated, nonfinite, wrong-unit and wrong-zone prices. No price interpolation.

Grid-side charge c and discharge d are in MW. Stored energy E is MWh; step length dt is hours. Equal charging and discharging efficiencies eta = sqrt(round-trip efficiency).

`E[t+1] = E[t] + eta*c[t]*dt[t] - d[t]*dt[t]/eta`.

Energy is constrained to min/max SOC times nameplate capacity. Both power directions are limited to rated grid power. A binary charge-mode variable enforces mutual exclusivity, including when negative prices could otherwise reward artificial simultaneous dissipation. Daily internal discharged energy cannot exceed usable capacity times the cycle budget. The day begins and ends at minimum SOC; there is no free initial energy and no carry across days. That restriction makes this a daily-reset ceiling, not an unrestricted lifetime optimum.

Objective: maximise sum of `(d-c)*price*dt - (c+d)*fee*dt - d*wear*dt`. Wear is a linear allowance per grid-side MWh discharged, not a calibrated life model. It does not physically reduce capacity. Daily mixed-integer problems use SciPy/HiGHS; unsuccessful/time-limited solves stop the run. An independent validator recomputes energy and checks power, SOC, exclusivity, terminal state and cycle budget.

Fixed schedule: charge within local hours 00–04 until maximum permitted energy; discharge during 17–21 to initial SOC. No observed price determines this policy. If those windows cannot restore SOC for an input configuration, the model rejects it rather than silently discarding stored energy. DST repeats count as real delivery intervals. Idle is zero dispatch and zero margin.

Outputs include daily and annual margins, charged/discharged energy, costs, example-day dispatch, source provenance and chart. Reported margin is neither investment profit nor ROI. Perfect foresight assumes knowledge unavailable to a pre-auction bidder; published prices do not prove orders would have been accepted at arbitrary size. All configurations are price takers with assumed full access and availability.
