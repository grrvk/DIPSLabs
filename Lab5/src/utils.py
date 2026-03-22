import random

from src.models import Graph, DirectedGraph


DIRECTED_GRAPHS: dict[str, DirectedGraph] = {
    "small": {
        "0": {"1": 1, "2": 4},
        "1": {"2": 2, "3": 5},
        "2": {"3": 1},
        "3": {},
    },
    "medium": {
        "0": {"1": 6, "2": 7},
        "1": {"2": 8, "3": 5, "4": -4},
        "2": {"3": 3, "4": 9},
        "3": {"0": 2, "5": 7},
        "4": {"3": 7, "5": 2},
        "5": {},
    },
}


GRAPHS: dict[str, Graph] = {
    "triangle": {
        "0": ["1", "2"],
        "1": ["0", "2"],
        "2": ["0", "1"],
    },
    "square": {
        "0": ["1", "3"],
        "1": ["0", "2"],
        "2": ["1", "3"],
        "3": ["2", "0"],
    },
    "k4": {
        "0": ["1", "2", "3"],
        "1": ["0", "2", "3"],
        "2": ["0", "1", "3"],
        "3": ["0", "1", "2"],
    },
    "petersen": {
        "0": ["1", "4", "5"],
        "1": ["0", "2", "6"],
        "2": ["1", "3", "7"],
        "3": ["2", "4", "8"],
        "4": ["3", "0", "9"],
        "5": ["0", "7", "8"],
        "6": ["1", "8", "9"],
        "7": ["2", "9", "5"],
        "8": ["3", "5", "6"],
        "9": ["4", "6", "7"],
    },
}


def generate_random_directed_graph(n: int, prob: float, max_weight: int = 10, seed: int = 42) -> Graph:
    rng = random.Random(seed)
    nodes = [str(i) for i in range(n)]
    graph: Graph = {v: {} for v in nodes}

    edges = set()

    for i in range(n):
        for j in range(i + 1, n):
            r = rng.random()
            if r < prob:
                w = rng.randint(1, max_weight)
                if rng.random() < 0.5:
                    graph[nodes[i]][nodes[j]] = w  # i → j
                    edges.add((i, j))
                else:
                    graph[nodes[j]][nodes[i]] = w  # j → i
                    edges.add((j, i))

    for i in range(n - 1):
        u_idx, v_idx = i, i + 1
        u, v = nodes[u_idx], nodes[v_idx]

        has_edge_uv = v in graph[u]
        has_edge_vu = u in graph[v]

        if not has_edge_uv and not has_edge_vu:
            w = rng.randint(1, max_weight)
            graph[u][v] = w
            edges.add((u_idx, v_idx))

        elif has_edge_vu:
            del graph[v][u]
            edges.discard((v_idx, u_idx))
            w = rng.randint(1, max_weight)
            graph[u][v] = w
            edges.add((u_idx, v_idx))

    return graph


def generate_random_undirected_graph(n: int, prob: float, seed: int = 42) -> Graph:
    rng = random.Random(seed)
    nodes = [str(i) for i in range(n)]
    adj: Graph = {v: [] for v in nodes}

    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < prob:
                adj[nodes[i]].append(nodes[j])
                adj[nodes[j]].append(nodes[i])

    for i in range(n - 1):
        u, v = nodes[i], nodes[i + 1]
        if v not in adj[u]:
            adj[u].append(v)
            adj[v].append(u)

    return adj