import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.disk.models import DiskConfig, Request
from src.disk.simulator import Simulator
from src.disk import policies
from src.eval.workloads import gen_uniform, gen_bursty
from src.eval.metrics import compute_metrics
from src.ai.ga import policy_ga

st.set_page_config(page_title="AI Disk Scheduling", layout="wide")

st.title("AI-Based Disk Scheduling Simulator")

with st.sidebar:
    st.header("Simulation Config")
    cylinders = st.slider("Cylinders", 50, 1000, 200, 10)
    head = st.slider("Start Head", 0, cylinders-1, cylinders//2, 1)
    workload = st.selectbox("Workload", ["uniform", "bursty"])
    num = st.slider("Requests", 50, 1000, 300, 10)
    rate = st.slider("Rate (arrivals/time)", 0.1, 3.0, 0.8, 0.1)
    scheduler = st.selectbox("Scheduler", ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK", "EDF", "GA"])
    run_btn = st.button("Run Simulation", type="primary")

cfg = DiskConfig(cylinders=cylinders, seek_per_cyl=0.1, service_time=1.0, start_head=head)

ALGOS = {
    "FCFS": policies.fcfs,
    "SSTF": policies.sstf,
    "SCAN": policies.scan,
    "C-SCAN": policies.cscan,
    "LOOK": policies.look,
    "C-LOOK": policies.clook,
    "EDF": policies.edf,
    "GA": policy_ga(window_size=6)
}

if run_btn:
    if workload == "uniform":
        reqs = gen_uniform(num=num, rate=rate, cylinders=cylinders, seed=0)
    else:
        reqs = gen_bursty(num=num, base_rate=rate, burst_factor=2.5, cylinders=cylinders, seed=0)

    sim = Simulator(cfg)
    res = sim.run(reqs, ALGOS[scheduler])
    completed = res["completed"]
    m = compute_metrics(completed)

    st.subheader("Metrics")
    st.write(pd.DataFrame([m]))

    # Head trajectory plot
    positions = [cfg.start_head] + [r.cylinder for (r, _, _) in completed]
    xs = list(range(len(positions)))
    fig = plt.figure()
    plt.plot(xs, positions, marker="o")
    plt.xlabel("Step")
    plt.ylabel("Head Position (cylinder)")
    plt.title("Head Movement Trajectory")
    st.pyplot(fig)

    st.subheader("Per-request summary (first 20)")
    table = []
    for (r, start, finish) in completed[:20]:
        table.append({
            "id": r.id, "arrival": round(r.arrival_time,2), "cyl": r.cylinder,
            "start": round(start,2), "finish": round(finish,2)
        })
    st.write(pd.DataFrame(table))
else:
    st.info("Configure parameters on the left, then click **Run Simulation**.")
