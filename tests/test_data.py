import pandas as pd
import pytest
from battery_lab.data import parse_prices

def full_year():
    idx=pd.date_range('2024-01-01','2025-01-01',freq='h',tz='Europe/Berlin',inclusive='left')
    return dict(endpoint='price',bidding_zone='DE-LU',unit='EUR / MWh',interval_minutes=60,
        data=[{'timestamp':t.isoformat(),'values':{'day_ahead_price':-1.0}} for t in idx])

def test_full_year_keeps_both_autumn_hours():
    frame=parse_prices(full_year())
    assert len(frame)==8784
    assert frame.index.is_unique
    counts=frame.groupby(frame.index.tz_convert('Europe/Berlin').date).size()
    assert sorted(counts.unique())==[23,24,25]

def test_missing_duplicate_units_and_resolution():
    p=full_year(); p['data'].pop()
    with pytest.raises(ValueError): parse_prices(p)
    p=full_year(); p['data'].append(p['data'][0])
    with pytest.raises(ValueError): parse_prices(p)
    for key,value in [('unit','EUR/kWh'),('interval_minutes',15),('bidding_zone','FR')]:
        p=full_year(); p[key]=value
        with pytest.raises(ValueError): parse_prices(p)
