from src.disk.models import DiskConfig, Request
from src.disk.simulator import Simulator
from src.disk import policies

def test_sstf_better_than_fcfs_on_tiny_queue():
    cfg = DiskConfig(cylinders=200, start_head=50, seek_per_cyl=1.0, service_time=0.0)
    sim = Simulator(cfg)
    reqs = [
        Request(0, 10, id=0),
        Request(0, 30, id=1),
        Request(0, 70, id=2),
    ]
    res_fcfs = sim.run(reqs, policies.fcfs)
    sim.reset()
    res_sstf = sim.run(reqs, policies.sstf)
    assert res_sstf["total_movement"] <= res_fcfs["total_movement"]
