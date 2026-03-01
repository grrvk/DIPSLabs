from dataclasses import dataclass, field


@dataclass
class Node:
    id: int
    parent: int = -1
    children: list[int] = field(default_factory=list)

    mis_size_if_excluded: int = 0
    mis_size_if_included: int = 1


@dataclass
class Tree:
    nodes: list[Node]

    @property
    def n(self) -> int:
        return len(self.nodes)

    @classmethod
    def from_edges(cls, n: int, edges: list[tuple[int, int]], root: int = 0) -> "Tree":
        nodes = [Node(id=i) for i in range(n)]

        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        visited = [False] * n
        stack = [root]
        visited[root] = True
        while stack:
            v = stack.pop()
            for u in adj[v]:
                if not visited[u]:
                    visited[u] = True
                    nodes[u].parent = v
                    nodes[v].children.append(u)
                    stack.append(u)

        return cls(nodes=nodes)


@dataclass(frozen=True)
class MISResult:
    size: int
    nodes: list[int] = field(default_factory=list)
