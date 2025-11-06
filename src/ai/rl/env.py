from typing import List, Tuple, Optional
import numpy as np
from ...disk.models import Request, DiskConfig
from ...disk.simulator import Simulator

class RLEnv:
    """
    Simple environment wrapper: present a fixed queue and head position.
    One step chooses the next request index to serve.
    This is a myopic environment (single decision), used as a placeholder.
    """
    def __init__(self, head: int, requests: List[Request], cfg: DiskConfig):
        self.head = head
        self.requests = requests
        self.cfg = cfg

    def state(self):
        # features: normalized head, normalized request cylinders
        H = self.cfg.cylinders
        x = [self.head / max(1, H-1)]
        for r in self.requests:
            x.append(r.cylinder / max(1, H-1))
        return np.array(x, dtype=float)

    def valid_actions(self):
        return list(range(len(self.requests)))

    def step(self, action: int) -> Tuple[float, bool]:
        r = self.requests[action]
        move = abs(r.cylinder - self.head)
        reward = -move
        done = True
        return reward, done
