import threading

import matplotlib.pyplot as plt
import networkx as nx

from src.models import Graph, Vertex


def _find_independent_sets(adj: Graph) -> list[list[str]]:
    remaining = set(adj.keys())
    sets: list[list[str]] = []
    while remaining:
        independent: list[str] = []
        blocked: set[str] = set()
        for v in remaining:
            if v not in blocked:
                independent.append(v)
                blocked.update(adj[v])
        sets.append(independent)
        remaining -= set(independent)
    return sets


def color_graph_parallel(adj: Graph) -> tuple[dict[str, int], int]:
    vertices = list(adj.keys())

    vertex_map: dict[str, Vertex] = {
        v: Vertex(id=v, color=i + 1) for i, v in enumerate(vertices)
    }

    independent_sets = _find_independent_sets(adj)

    rounds = 0
    while True:
        any_change = False

        for group in independent_sets:
            snapshot: dict[str, int] = {v: vertex_map[v].color for v in vertices}
            results: list[int] = [0] * len(group)

            def compute(v: str, slot: int) -> None:
                used = {snapshot[nb] for nb in adj[v]}
                c = 1
                while c in used:
                    c += 1
                results[slot] = c

            threads = [
                threading.Thread(target=compute, args=(v, i), daemon=True)
                for i, v in enumerate(group)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            for i, v in enumerate(group):
                if vertex_map[v].color != results[i]:
                    vertex_map[v].color = results[i]
                    any_change = True

        rounds += 1
        if not any_change:
            break

    return {v: vertex_map[v].color for v in vertices}, rounds


def visualize_undirected_graph(adj: Graph, colors: dict[str, int], title: str = "Graph Coloring") -> None:
    G = nx.Graph()
    G.add_nodes_from(adj.keys())
    for u, neighbors in adj.items():
        for v in neighbors:
            if not G.has_edge(u, v):
                G.add_edge(u, v)

    num_colors = max(colors.values(), default=1)
    cmap = plt.cm.get_cmap("viridis", num_colors)
    node_colors = [cmap(colors[v] - 1) for v in G.nodes()]
    labels = {v: f"{v}\nc={colors[v]}" for v in G.nodes()}

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(
        G, pos,
        labels=labels,
        node_color=node_colors,
        node_size=1000,
        font_size=9,
        font_color="white",
        edge_color="#888888",
        width=1.5,
    )
    plt.title(f"{title}  |  {num_colors} color(s) used")
    plt.show()