import math
from dataclasses import dataclass, field


DirectedGraph = dict[str, dict[str, float]]

Graph = dict[str, list[str]]


@dataclass
class Vertex:
    id: str
    color: int = 0