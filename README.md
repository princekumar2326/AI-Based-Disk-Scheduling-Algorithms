# AI-Based Disk Scheduling Algorithms

A reproducible simulator comparing classical disk scheduling policies (FCFS, SSTF, SCAN, C‑SCAN, LOOK, C‑LOOK, EDF) against AI-based approaches (Genetic Algorithm and a minimal DQN).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run CLI experiment
python -m eval.run --workload uniform --rate 0.8 --cylinders 200 --seeds 3 --schedulers FCFS SSTF SCAN GA --out experiments/uniform_results.csv

# Launch Streamlit UI
streamlit run ui/app.py
```

## Project structure
```
ai-disk-scheduler/
  src/
    disk/           # core simulator + classic policies
    ai/             # AI methods: GA, RL
    eval/           # metrics, workloads, CLI
  ui/               # Streamlit app
  data/             # optional traces
  experiments/      # results
  tests/            # unit tests
```

## Notes
- RL (DQN) is intentionally minimal to keep the project lightweight. GA is fully functional.
- Workloads are synthetic by default; you can also provide CSV traces with columns:
  `arrival_time,cylinder,deadline,priority`.
