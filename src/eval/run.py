from typing import List
import csv
import math
import tyro
import numpy as np

from ..disk.models import DiskConfig
from ..disk.simulator import Simulator
from ..disk import policies
from ..eval.metrics import compute_metrics
from ..eval.workloads import gen_uniform, gen_bursty

def run(
    workload: str = "uniform",
    num: int = 400,
    rate: float = 0.8,
    cylinders: int = 200,
    seeds: int = 3,
    schedulers: List[str] = ["FCFS", "SSTF", "SCAN", "GA"],
    out: str = "experiments/results.csv",
):
    cfg = DiskConfig(cylinders=cylinders, seek_per_cyl=0.1, service_time=1.0, start_head=cylinders//2)
    algos = {
        "FCFS": policies.fcfs,
        "SSTF": policies.sstf,
        "SCAN": policies.scan,
        "C-SCAN": policies.cscan,
        "LOOK": policies.look,
        "C-LOOK": policies.clook,
        "EDF": policies.edf,
    }

    # try import GA policy
    from ..ai.ga import policy_ga
    algos["GA"] = policy_ga(window_size=6)

    rows = []
    for name in schedulers:
        if name not in algos:
            print(f"Unknown scheduler {name}, skipping.")
            continue
        for s in range(seeds):
            if workload == "uniform":
                reqs = gen_uniform(num=num, rate=rate, cylinders=cylinders, seed=s)
            elif workload == "bursty":
                reqs = gen_bursty(num=num, base_rate=rate, burst_factor=2.5, cylinders=cylinders, seed=s)
            else:
                raise ValueError("Unknown workload")
            sim = Simulator(cfg)
            res = sim.run(reqs, algos[name])
            m = compute_metrics(res["completed"])
            rows.append({
                "scheduler": name,
                "seed": s,
                "total_movement": res["total_movement"],
                **m,
            })
            print(f"{name} seed {s}: movement={res['total_movement']:.1f} avg_resp={m['avg_resp']:.2f}")

    # write CSV
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")

if __name__ == "__main__":
    tyro.cli(run)
