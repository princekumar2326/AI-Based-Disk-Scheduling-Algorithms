from typing import List, Optional
import numpy as np
from ..disk.models import Request

def gen_uniform(num: int, rate: float, cylinders: int, seed: int = 0, with_deadlines=False) -> List[Request]:
    """
    Poisson arrivals with exponential inter-arrival of mean 1/rate.
    """
    rng = np.random.default_rng(seed)
    t = 0.0
    reqs = []
    for i in range(num):
        t += rng.exponential(1.0 / max(1e-9, rate))
        cyl = int(rng.integers(0, cylinders))
        deadline = t + rng.uniform(10, 40) if with_deadlines else None
        reqs.append(Request(arrival_time=t, cylinder=cyl, deadline=deadline, id=i))
    return reqs

def gen_bursty(num: int, base_rate: float, burst_factor: float, cylinders: int, seed: int = 0) -> List[Request]:
    rng = np.random.default_rng(seed)
    t = 0.0
    reqs = []
    for i in range(num):
        rate = base_rate * (burst_factor if rng.random() < 0.2 else 1.0)
        t += rng.exponential(1.0 / max(1e-9, rate))
        cyl = int(rng.integers(0, cylinders))
        reqs.append(Request(arrival_time=t, cylinder=cyl, id=i))
    return reqs

def from_csv(path: str) -> List[Request]:
    import pandas as pd
    df = pd.read_csv(path)
    reqs = []
    for i, row in df.iterrows():
        reqs.append(Request(
            arrival_time=float(row["arrival_time"]),
            cylinder=int(row["cylinder"]),
            deadline=float(row["deadline"]) if "deadline" in df.columns and not pd.isna(row["deadline"]) else None,
            priority=int(row["priority"]) if "priority" in df.columns and not pd.isna(row["priority"]) else 0,
            id=int(i)
        ))
    return reqs
