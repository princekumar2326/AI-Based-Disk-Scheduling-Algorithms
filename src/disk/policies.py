from typing import List, Optional
from .models import Request

def fcfs(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    return 0 if queue else None

def sstf(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    if not queue:
        return None
    dists = [abs(r.cylinder - head) for r in queue]
    return int(min(range(len(queue)), key=lambda i: dists[i]))

def _scan_pick(queue: List[Request], head: int, direction: int, max_cyl: int, circular=False, look=False) -> Optional[int]:
    if not queue:
        return None
    # candidates in current direction
    if direction > 0:
        cand = [ (i,r) for i,r in enumerate(queue) if r.cylinder >= head ]
        if cand:
            # choose nearest in direction
            return min(cand, key=lambda t: (t[1].cylinder - head, t[1].arrival_time))[0]
        # wrap or bounce
        if circular:
            # wrap to smallest cylinder request
            return min(range(len(queue)), key=lambda i: queue[i].cylinder)
        else:
            # bounce direction: choose nearest on the left
            cand = [ (i,r) for i,r in enumerate(queue) if r.cylinder < head ]
            if cand:
                return max(cand, key=lambda t: t[1].cylinder)[0]
    else:
        cand = [ (i,r) for i,r in enumerate(queue) if r.cylinder <= head ]
        if cand:
            return max(cand, key=lambda t: (t[1].cylinder, -t[1].arrival_time))[0]
        if circular:
            return max(range(len(queue)), key=lambda i: queue[i].cylinder)
        else:
            cand = [ (i,r) for i,r in enumerate(queue) if r.cylinder > head ]
            if cand:
                return min(cand, key=lambda t: t[1].cylinder)[0]
    return 0 if queue else None

def scan(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    return _scan_pick(queue, head, direction, max_cyl, circular=False, look=False)

def cscan(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    # direction is ignored; C-SCAN always moves upward and wraps to 0
    return _scan_pick(queue, head, +1, max_cyl, circular=True, look=False)

def look(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    return _scan_pick(queue, head, direction, max_cyl, circular=False, look=True)

def clook(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    return _scan_pick(queue, head, +1, max_cyl, circular=True, look=True)

def edf(queue: List[Request], head: int, direction: int, max_cyl: int) -> Optional[int]:
    # earliest deadline first (ties -> SSTF)
    with_deadline = [ (i,r) for i,r in enumerate(queue) if r.deadline is not None ]
    if with_deadline:
        best_deadline = min(with_deadline, key=lambda t: t[1].deadline)[1].deadline
        cand = [ (i,r) for i,r in enumerate(queue) if r.deadline == best_deadline ]
        if len(cand) == 1:
            return cand[0][0]
        # tie-breaker by distance
        return min([i for i,_ in cand], key=lambda i: abs(queue[i].cylinder - head))
    # fallback to SSTF if no deadlines
    return sstf(queue, head, direction, max_cyl)
