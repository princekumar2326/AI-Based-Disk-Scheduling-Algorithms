from typing import Callable, Dict, List, Tuple, Optional
from .models import Request, DiskConfig
import heapq

PolicyFn = Callable[[List[Request], int, int, int], Optional[int]]

class Simulator:
    """
    Event-driven simulator with arrival events and service completion.
    Simplified timing model:
      - Move time = seek_per_cyl * |delta cylinders|
      - Service time = fixed service_time
    """
    def __init__(self, config: DiskConfig):
        self.cfg = config
        self.reset()

    def reset(self):
        self.time = 0.0
        self.head = self.cfg.start_head
        self.direction = self.cfg.start_dir
        self.queue: List[Request] = []
        self.completed: List[Tuple[Request, float, float]] = []  # (req, start_time, finish_time)

    def run(self, arrivals: List[Request], policy: PolicyFn) -> Dict:
        # arrivals must be sorted by arrival_time
        arrivals = sorted(arrivals, key=lambda r: r.arrival_time)
        i = 0
        self.reset()

        while i < len(arrivals) or self.queue:
            # bring in all arrivals up to current time
            if i < len(arrivals) and (not self.queue):
                # jump to next arrival if idle
                self.time = max(self.time, arrivals[i].arrival_time)
            while i < len(arrivals) and arrivals[i].arrival_time <= self.time:
                self.queue.append(arrivals[i])
                i += 1

            if not self.queue:
                continue

            # pick next
            idx = policy(self.queue, self.head, self.direction, self.cfg.cylinders)
            idx = 0 if idx is None else idx
            req = self.queue.pop(idx)

            # move head
            delta = abs(req.cylinder - self.head)
            move_time = self.cfg.seek_per_cyl * delta
            start_time = max(self.time, req.arrival_time) + move_time
            finish_time = start_time + self.cfg.service_time

            # update head, time, direction
            self.direction = +1 if req.cylinder >= self.head else -1
            self.head = req.cylinder
            self.time = finish_time

            self.completed.append((req, start_time - move_time, finish_time))

        return {
            "completed": self.completed,
            "total_movement": self._total_head_movement(self.completed),
            "makespan": self.time,
        }

    def _total_head_movement(self, completed: List[Tuple[Request, float, float]]) -> int:
        if not completed:
            return 0
        pos = self.cfg.start_head
        move = 0
        for (r, _, _) in completed:
            move += abs(r.cylinder - pos)
            pos = r.cylinder
        return move
