from typing import Dict, List, Tuple
import numpy as np
from ..disk.models import Request

def compute_metrics(completed: List[Tuple[Request, float, float]]) -> Dict[str, float]:
    # completed tuples: (req, start_time, finish_time)
    waits = []
    responses = []
    deadlines_missed = 0
    for req, start, finish in completed:
        wait = max(0.0, start - req.arrival_time)
        resp = finish - req.arrival_time
        waits.append(wait)
        responses.append(resp)
        if req.deadline is not None and finish > req.deadline:
            deadlines_missed += 1
    n = max(1, len(completed))
    return {
        "avg_wait": float(np.mean(waits)) if waits else 0.0,
        "p95_wait": float(np.percentile(waits, 95)) if waits else 0.0,
        "avg_resp": float(np.mean(responses)) if responses else 0.0,
        "p95_resp": float(np.percentile(responses, 95)) if responses else 0.0,
        "deadline_miss_rate": float(deadlines_missed / n),
        "throughput": float(n / (completed[-1][2] - completed[0][1])) if n > 1 else 0.0,
    }
