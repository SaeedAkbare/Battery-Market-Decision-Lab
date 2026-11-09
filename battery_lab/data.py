import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import requests

def parse_prices(payload):
    if (payload.get('endpoint'),payload.get('bidding_zone'),payload.get('unit'),payload.get('interval_minutes')) != ('price','DE-LU','EUR / MWh',60):
        raise ValueError('This first release requires hourly DE-LU 2024 prices')
    timestamps=[pd.Timestamp(r['timestamp']) for r in payload['data']]
    if any(t.tzinfo is None for t in timestamps): raise ValueError('Timezone missing')
    frame=pd.DataFrame({'price':[r['values']['day_ahead_price'] for r in payload['data']], 'hours':1.0},index=pd.to_datetime(timestamps,utc=True))
    if frame.index.duplicated().any(): raise ValueError('Duplicate price interval; source review required')
    expected=pd.date_range(pd.Timestamp('2024-01-01',tz='Europe/Berlin'),pd.Timestamp('2025-01-01',tz='Europe/Berlin'),freq='h',inclusive='left').tz_convert('UTC')
    frame=frame.sort_index()
    if not frame.index.equals(expected) or not np.isfinite(frame.price).all(): raise ValueError('Incomplete 2024 coverage')
    return frame

def load_prices():
    folder=Path('data'); folder.mkdir(exist_ok=True)
    path=folder/'prices_2024.json'; meta=folder/'prices_2024.meta.json'
    if not path.exists():
        r=requests.get('https://api.energy-charts.info/v2/price',params={'bzn':'DE-LU','start':'2024-01-01','end':'2024-12-31'},timeout=90)
        r.raise_for_status(); payload=r.json(); parse_prices(payload)
        path.write_bytes(r.content)
        meta.write_text(json.dumps({'url':r.url,'retrieved_utc':pd.Timestamp.now(tz='UTC').isoformat(),'sha256':hashlib.sha256(r.content).hexdigest(),'license':payload.get('license')},indent=2))
    if not meta.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=json.loads(meta.read_text())['sha256']:
        raise ValueError('Cache provenance missing or hash mismatch')
    return parse_prices(json.loads(path.read_bytes())),json.loads(meta.read_text())
