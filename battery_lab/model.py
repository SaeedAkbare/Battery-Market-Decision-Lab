from dataclasses import dataclass, asdict
import math
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

@dataclass(frozen=True)
class Battery:
    power_mw: float = 1.0
    capacity_mwh: float = 2.0
    round_trip_efficiency: float = .90
    min_soc: float = .10
    max_soc: float = .90
    fee_eur_mwh: float = 1.0
    wear_eur_mwh_discharged: float = 5.0
    daily_cycles: float = 1.0

    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('Battery parameters must be finite')
        if self.power_mw<=0 or self.capacity_mwh<=0 or not 0<self.round_trip_efficiency<=1:
            raise ValueError('Invalid power, energy or efficiency')
        if not 0<=self.min_soc<self.max_soc<=1 or min(self.fee_eur_mwh,self.wear_eur_mwh_discharged,self.daily_cycles)<0:
            raise ValueError('Invalid state-of-charge, costs or cycle limit')

    @property
    def eta(self): return math.sqrt(self.round_trip_efficiency)

    @property
    def usable(self): return self.capacity_mwh*(self.max_soc-self.min_soc)

def validate_day(day):
    if not isinstance(day.index,pd.DatetimeIndex) or day.index.tz is None:
        raise ValueError('Timezone-aware delivery index required')
    if not day.index.is_unique or not day.index.is_monotonic_increasing or day.empty:
        raise ValueError('Invalid delivery ordering')
    if not np.isfinite(day[['price','hours']].to_numpy()).all() or not day.hours.isin([.25,.5,1.0]).all():
        raise ValueError('Invalid price or interval duration')
    local=day.index.tz_convert('Europe/Berlin')
    a=local[0].normalize(); b=a+pd.DateOffset(days=1)
    starts=day.index.tz_convert('UTC')
    ends=starts+pd.to_timedelta(day.hours.to_numpy(),unit='h')
    if starts[0]!=a or ends[-1]!=b or not (ends[:-1]==starts[1:]).all():
        raise ValueError('Each optimisation must cover one complete local day without gaps')

def dispatch(day,battery,strategy):
    """Daily reset to minimum SOC; hindsight optimum is explicitly not tradable."""
    validate_day(day)
    b=battery; n=len(day); dt=day.hours.to_numpy(); p=day.price.to_numpy()
    e0=b.capacity_mwh*b.min_soc; emax=b.capacity_mwh*b.max_soc
    if strategy=='perfect_foresight':
        # Variables: grid charging MW, grid discharge MW, end-of-interval MWh, charging-mode binary.
        c=np.r_[(p+b.fee_eur_mwh)*dt,(-p+b.fee_eur_mwh+b.wear_eur_mwh_discharged)*dt,np.zeros(2*n)]
        A=lil_matrix((3*n+2,4*n)); lower=np.full(3*n+2,-np.inf); upper=np.full(3*n+2,np.inf)
        for i in range(n):
            A[i,i]=-b.eta*dt[i]; A[i,n+i]=dt[i]/b.eta; A[i,2*n+i]=1
            if i: A[i,2*n+i-1]=-1
            lower[i]=upper[i]=e0 if i==0 else 0
            A[n+i,i]=1; A[n+i,3*n+i]=-b.power_mw; upper[n+i]=0
            A[2*n+i,n+i]=1; A[2*n+i,3*n+i]=b.power_mw; upper[2*n+i]=b.power_mw
        A[3*n,3*n-1]=1; lower[3*n]=upper[3*n]=e0
        A[3*n+1,n:2*n]=dt/b.eta; upper[3*n+1]=b.usable*b.daily_cycles
        result=milp(c,integrality=np.r_[np.zeros(3*n),np.ones(n)],
            bounds=Bounds(np.r_[np.zeros(2*n),np.full(n,e0),np.zeros(n)],np.r_[np.full(2*n,b.power_mw),np.full(n,emax),np.ones(n)]),
            constraints=LinearConstraint(A.tocsr(),lower,upper),options={'time_limit':30,'mip_rel_gap':1e-8})
        if not result.success: raise RuntimeError('Optimisation did not reach an accepted optimum')
        charge=result.x[:n]; discharge=result.x[n:2*n]
    elif strategy in ('fixed_schedule','idle'):
        charge=np.zeros(n); discharge=np.zeros(n); energy=e0; discharged=0
        for i,t in enumerate(day.index.tz_convert('Europe/Berlin')):
            if strategy=='fixed_schedule' and 0<=t.hour<4:
                charge[i]=min(b.power_mw,(emax-energy)/(b.eta*dt[i]), max(0,b.usable*b.daily_cycles-(energy-e0))/(b.eta*dt[i]))
            if strategy=='fixed_schedule' and 17<=t.hour<21:
                discharge[i]=min(b.power_mw,(energy-e0)*b.eta/dt[i],max(0,b.usable*b.daily_cycles-discharged)*b.eta/dt[i])
            energy+=charge[i]*dt[i]*b.eta-discharge[i]*dt[i]/b.eta
            discharged+=discharge[i]*dt[i]/b.eta
        if abs(energy-e0)>1e-6: raise ValueError('Fixed windows cannot restore terminal SOC for this configuration')
    else: raise ValueError('Unknown strategy')
    frame=day.copy(); frame['charge_mw']=charge; frame['discharge_mw']=discharge
    frame['soc_mwh']=e0+np.cumsum((charge*b.eta-discharge/b.eta)*dt)
    frame['gross_eur']=(discharge-charge)*p*dt
    frame['fees_eur']=(charge+discharge)*dt*b.fee_eur_mwh
    frame['wear_eur']=discharge*dt*b.wear_eur_mwh_discharged
    frame['net_eur']=frame.gross_eur-frame.fees_eur-frame.wear_eur
    check_dispatch(frame,b)
    return frame

def check_dispatch(frame,b):
    tol=1e-5; c=frame.charge_mw; d=frame.discharge_mw; dt=frame.hours
    e0=b.capacity_mwh*b.min_soc
    if min(c.min(),d.min()) < -tol or max(c.max(),d.max())>b.power_mw+tol or ((c>tol)&(d>tol)).any():
        raise ValueError('Invalid dispatch power or simultaneous charging')
    expected=e0+((c*b.eta-d/b.eta)*dt).cumsum()
    if not np.allclose(expected,frame.soc_mwh,atol=tol,rtol=0): raise ValueError('Energy balance failed')
    if expected.min()<e0-tol or expected.max()>b.capacity_mwh*b.max_soc+tol or abs(expected.iloc[-1]-e0)>tol:
        raise ValueError('SOC boundary failed')
    if (d*dt/b.eta).sum()>b.usable*b.daily_cycles+tol: raise ValueError('Cycle budget exceeded')
