from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Request:
    arrival_time: float
    cylinder: int
    deadline: Optional[float] = None
    priority: int = 0
    id: int = field(default_factory=int)

@dataclass
class DiskConfig:
    cylinders: int = 200
    seek_per_cyl: float = 1.0  # time units per cylinder moved
    service_time: float = 1.0  # fixed time to service a request once the head is on the cylinder
    start_head: int = 0
    start_dir: int = +1  # +1 to the right, -1 to the left
