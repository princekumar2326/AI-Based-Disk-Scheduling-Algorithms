from typing import List, Callable, Optional
import numpy as np
from ..disk.models import Request, DiskConfig
from ..disk.simulator import Simulator, PolicyFn

def ga_schedule(window: List[Request], head: int) -> List[int]:
    """
    Run a small GA to order requests in a window by minimizing head movement.
    Returns indices into `window` describing serving order.
    """
    n = len(window)
    if n <= 1:
        return list(range(n))
    rng = np.random.default_rng()
    pop_size = min(40, max(10, 2 * n))
    gens = min(60, 5 * n)
    # initialize population as permutations
    pop = [np.random.permutation(n) for _ in range(pop_size)]

    def cost(order):
        pos = head
        move = 0
        for idx in order:
            move += abs(window[idx].cylinder - pos)
            pos = window[idx].cylinder
        return move

    for _ in range(gens):
        fitness = np.array([ -cost(ind) for ind in pop ])  # larger is better
        # selection: tournament
        new_pop = []
        for _ in range(pop_size//2):
            a, b = pop[rng.integers(pop_size)], pop[rng.integers(pop_size)]
            c, d = pop[rng.integers(pop_size)], pop[rng.integers(pop_size)]
            p1 = a if ( -cost(a) ) > ( -cost(b) ) else b
            p2 = c if ( -cost(c) ) > ( -cost(d) ) else d
            # crossover: ordered crossover
            cut1, cut2 = sorted(rng.integers(0, n, size=2))
            child = [-1]*n
            child[cut1:cut2] = p1[cut1:cut2]
            fill = [x for x in p2 if x not in child]
            it = iter(fill)
            child = [next(it) if x == -1 else x for x in child]
            # mutation: swap two genes
            if rng.random() < 0.3:
                i, j = rng.integers(0, n, size=2)
                child[i], child[j] = child[j], child[i]
            new_pop.extend([np.array(child), p1.copy()])
        pop = new_pop[:pop_size]

    # best individual
    best = min(pop, key=lambda ind: sum(abs(window[ind[k]].cylinder - (window[ind[k-1]].cylinder if k>0 else head)) for k in range(n)))
    return list(map(int, best))

def policy_ga(window_size: int = 6) -> PolicyFn:
    """
    GA-based policy: at each decision, compute an order for the next window_size requests
    (by arrival time) and pick the first one from that order.
    """
    def policy(queue, head, direction, max_cyl):
        if not queue:
            return None
        # take earliest-arrived first window
        window = sorted(list(enumerate(queue)), key=lambda t: t[1].arrival_time)[:window_size]
        idxs = [i for i,_ in window]
        reqs = [r for _, r in window]
        order = ga_schedule(reqs, head)
        return idxs[order[0]]
    return policy
