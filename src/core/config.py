from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class QUERY_TYPE(Enum):
    RADIUS = "radius"
    K = "k"


class INTERPOLATION_KERNEL(Enum):
    DISTANCE_WEIGHTED = "distance_weighted"
    FEM = "fem"


@dataclass
class InterpolationConfig:
    method: QUERY_TYPE
    param: int | float
    max_distance: float
    coincidence_tolerance: float
    kernel: INTERPOLATION_KERNEL
    multithread: bool

    def __post_init__(self):
        if self.method == QUERY_TYPE.K:
            try:
                self.param = int(self.param)
            except TypeError:
                raise ValueError("Parameter for K query must be an integer.")

    @classmethod
    def from_yaml(cls, filepath: Path) -> "InterpolationConfig":
        pass
