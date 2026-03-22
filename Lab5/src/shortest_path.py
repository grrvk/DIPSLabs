
import math
import threading

import matplotlib.pyplot as plt
import networkx as nx

from src.models import DirectedGraph


def shortest_path(graph: DirectedGraph, source: str) -> dict[str, float]:
    vertices = list(graph.keys())
    n = len(vertices)
    idx: dict[str, int] = {v: i for i, v in enumerate(vertices)}

    in_edges: dict[str, list[tuple[str, float]]] = {v: [] for v in vertices}
    for u in vertices:
        for w, cost in graph[u].items():
            in_edges[w].append((u, cost))

    INF = math.inf
    D: list[float] = [INF] * n
    D[idx[source]] = 0.0
    D_next: list[float] = D[:]

    barrier = threading.Barrier(n)

    def worker(v: str) -> None:
        i = idx[v]
        for _ in range(n):
            best = D[i]
            for u, cost in in_edges[v]:
                d = D[idx[u]]
                if d != INF:
                    candidate = d + cost
                    if candidate < best:
                        best = candidate
            D_next[i] = best

            barrier.wait()

            if i == 0:
                D[:] = D_next

            barrier.wait()

    threads = [threading.Thread(target=worker, args=(v,), daemon=True) for v in vertices]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return {v: D[idx[v]] for v in vertices}


def visualize_directed_graph(graph: DirectedGraph, source: str, distances: dict[str, float], title: str = "Shortest Path") -> None:
    INF = math.inf

    G = nx.DiGraph()
    G.add_nodes_from(graph.keys())
    for u, nbrs in graph.items():
        for v, w in nbrs.items():
            G.add_edge(u, v, weight=w)

    sp_edges: set[tuple[str, str]] = set()
    for v, d in distances.items():
        if v == source or d == INF:
            continue
        for u, w in graph.items():
            if v in w and distances.get(u, INF) != INF and distances[u] + w[v] == d:
                sp_edges.add((u, v))
                break

    max_d = max((d for d in distances.values() if d != INF), default=1) or 1
    node_colors = []
    for v in G.nodes():
        if v == source:
            node_colors.append("#FFC107")
        elif distances.get(v, INF) == INF:
            node_colors.append("#F44336")
        else:
            intensity = 0.3 + 0.5 * (1 - distances[v] / max_d)
            node_colors.append(plt.cm.Greens(intensity))

    pos = nx.spring_layout(G, seed=42)

    edge_colors = ["#1565C0" if (u, v) in sp_edges else "#AAAAAA" for u, v in G.edges()]
    edge_widths = [2.5 if (u, v) in sp_edges else 1.0 for u, v in G.edges()]
    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}

    labels = {
        v: f"{v}\n{'∞' if distances.get(v, INF) == INF else distances[v]}"
        for v in G.nodes()
    }

    plt.figure(figsize=(8, 6))
    nx.draw(
        G, pos,
        labels=labels,
        node_color=node_colors,
        node_size=1000,
        font_size=9,
        font_color="white",
        edge_color=edge_colors,
        width=edge_widths,
        arrows=True,
        arrowsize=20,
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title(f"{title}  |  source = {source}")
    plt.show()
