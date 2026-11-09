import numpy as np
import pandas as pd
import pytest
from battery_lab.model import Battery,dispatch,validate_day

def day(date='2024-01-01',price=0):
    a=pd.Timestamp(date,tz='Europe/Berlin'); b=a+pd.DateOffset(days=1)
    idx=pd.date_range(a,b,freq='h',inclusive='left').tz_convert('UTC')
    return pd.DataFrame({'price':price,'hours':1.0},index=idx)

def test_known_arbitrage():
    x=day(); x.iloc[0,0]=-10; x.iloc[-1,0]=100
    b=Battery(capacity_mwh=1,round_trip_efficiency=1,min_soc=0,max_soc=1,fee_eur_mwh=0,wear_eur_mwh_discharged=0)
    f=dispatch(x,b,'perfect_foresight')
    assert f.net_eur.sum()==pytest.approx(110)
    assert f.soc_mwh.iloc[-1]==pytest.approx(0)

def test_loss_and_fees():
    x=day(price=50); b=Battery()
    f=dispatch(x,b,'fixed_schedule')
    incoming=(f.charge_mw*f.hours).sum(); outgoing=(f.discharge_mw*f.hours).sum()
    assert outgoing/incoming==pytest.approx(.9)
    assert f.net_eur.sum()==pytest.approx(50*(outgoing-incoming)-(incoming+outgoing)-5*outgoing)
    assert dispatch(x,b,'perfect_foresight').net_eur.sum()==pytest.approx(0)

@pytest.mark.parametrize('date,hours',[('2024-03-31',23),('2024-10-27',25)])
def test_dst(date,hours):
    x=day(date); assert len(x)==hours
    dispatch(x,Battery(),'fixed_schedule')
    dispatch(x,Battery(),'perfect_foresight')

def test_negative_prices_do_not_allow_simultaneous_operation():
    f=dispatch(day(price=-100),Battery(),'perfect_foresight')
    assert not ((f.charge_mw>1e-6)&(f.discharge_mw>1e-6)).any()
    assert (f.discharge_mw*f.hours/Battery().eta).sum()<=Battery().usable+1e-6

def test_upper_bound_and_idle():
    x=day(); x['price']=np.sin(np.arange(len(x)))*100
    b=Battery()
    assert dispatch(x,b,'perfect_foresight').net_eur.sum()>=dispatch(x,b,'fixed_schedule').net_eur.sum()-1e-5
    assert dispatch(x,b,'idle').net_eur.sum()==0

def test_invalid_inputs():
    with pytest.raises(ValueError): Battery(round_trip_efficiency=1.1)
    with pytest.raises(ValueError): validate_day(day().iloc[1:])
    x=day(); x.iloc[0,0]=np.nan
    with pytest.raises(ValueError): validate_day(x)
