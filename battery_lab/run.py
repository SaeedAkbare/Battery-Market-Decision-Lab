from pathlib import Path
from dataclasses import asdict
import json
import pandas as pd
from .data import load_prices
from .model import Battery, dispatch

def run():
    prices,provenance=load_prices()
    out=Path('reports'); out.mkdir(exist_ok=True)
    rows=[]; configs=[]
    for capacity in [1.,2.,4.]:
        b=Battery(capacity_mwh=capacity); configs.append(asdict(b))
        for strategy in ['idle','fixed_schedule','perfect_foresight']:
            for date,day in prices.groupby(prices.index.tz_convert('Europe/Berlin').date):
                f=dispatch(day,b,strategy)
                rows.append(dict(date=str(date),capacity_mwh=capacity,strategy=strategy,
                    gross_eur=f.gross_eur.sum(),fees_eur=f.fees_eur.sum(),wear_eur=f.wear_eur.sum(),net_eur=f.net_eur.sum(),
                    charged_mwh=(f.charge_mw*f.hours).sum(),discharged_mwh=(f.discharge_mw*f.hours).sum()))
                if capacity==2 and str(date)=='2024-12-12': f.to_csv(out/f'example_{strategy}.csv',index_label='utc')
        print(f'Completed 1 MW / {capacity:g} MWh',flush=True)
    daily=pd.DataFrame(rows); daily.to_csv(out/'daily.csv',index=False)
    annual=daily.groupby(['capacity_mwh','strategy']).sum(numeric_only=True)
    annual.to_csv(out/'annual.csv')
    (out/'assumptions.json').write_text(json.dumps({'battery_scenarios':configs,'provenance':provenance,'period':'2024','scope':'Historical day-ahead arbitrage screening; no investment valuation'},indent=2))
    lines=['# Battery Market Decision Lab — first-stage results','','Historical DE-LU 2024 screening. All configurations have 1 MW grid power. Monetary values are EUR, after assumed fees and linear cycling cost, before fixed costs, taxes, financing and capital expenditure.','','| Capacity (MWh) | Fixed schedule margin | Perfect-foresight ceiling |','|---|---:|---:|']
    for cap in [1.,2.,4.]:
        lines.append(f'| {cap:g} | {annual.loc[(cap,"fixed_schedule"),"net_eur"]:,.2f} | {annual.loc[(cap,"perfect_foresight"),"net_eur"]:,.2f} |')
    lines+=['','Idle earns zero. More capacity is not automatically a better investment: additional capital and fixed costs are not included. The fixed schedule is an illustrative, untrained rule, not an independently validated trading strategy. The perfect-foresight result knows every price of each delivery day and is an upper bound only for the stated daily-reset model. It is not attainable forecast revenue.','','Assumptions: 90% round-trip efficiency; 10–90% SOC; EUR 1/MWh fee on both charge and discharge energy; EUR 5/MWh discharged linear wear allowance; one equivalent cycle per usable capacity per day; each day starts and ends at minimum SOC. These are editable illustrative inputs, not supplier quotes. No simultaneous charge/discharge. All trades assumed to clear at published day-ahead prices; no market impact, availability losses, imbalance or intraday/ancillary income.','','Source: Energy-Charts.info; DE-LU prices attributed to Bundesnetzagentur | SMARD.de, CC BY 4.0. Data transformed into simulated dispatch and cash flows; source retrieval date/hash are in assumptions.json.','', 'Next: agree the battery assumptions and extend to price forecasts available before bidding, chronological backtesting and uncertainty. Investment valuation is a separate later stage.']
    (out/'market-report.md').write_text('\n'.join(lines),encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,5))
    annual.net_eur.unstack().drop(columns='idle').rename(columns={'fixed_schedule':'Fixed schedule','perfect_foresight':'Perfect-foresight ceiling'}).div(1000).plot.bar(ax=ax,color=['#176B87','#b36b32'],rot=0)
    ax.set(xlabel='Nameplate capacity (MWh), all at 1 MW',ylabel='2024 modelled margin (thousand EUR)',title='Historical battery screening — DE-LU 2024')
    fig.text(.08,.02,'Energy-Charts / SMARD | Illustrative costs | Before CAPEX and fixed costs',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1)); fig.savefig(out/'comparison.png',dpi=160); plt.close(fig)

if __name__=='__main__': run()
