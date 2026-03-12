import random

from src.models import Node

# Adjacency-list representation: node id → list of neighbour ids
Graph = dict[int, list[int]]

GRAPHS: dict[str, Graph] = {
    "path5": {0: [1], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3]},
    "cycle6": {0: [1, 5], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3, 5], 5: [4, 0]},
    "k4": {0: [1, 2, 3], 1: [0, 2, 3], 2: [0, 1, 3], 3: [0, 1, 2]},
    "tree7": {0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6], 3: [1], 4: [1], 5: [2], 6: [2]},
    "petersen": {0: [1, 4, 5], 1: [0, 2, 6], 2: [1, 3, 7], 3: [2, 4, 8], 4: [3, 0, 9],
                 5: [0, 7, 8], 6: [1, 8, 9], 7: [2, 9, 5], 8: [3, 5, 6], 9: [4, 6, 7]},
}


def generate_random_graph(n: int, edge_prob: float = 0.4) -> Graph:
    adj: Graph = {i: [] for i in range(n)}
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                adj[u].append(v)
                adj[v].append(u)
    return adj


def run_luby(graph: Graph) -> tuple[list[int], int]:
    nodes = {uid: Node(uid, neighbours) for uid, neighbours in graph.items()}
    round_num = 0

    while any(n.active for n in nodes.values()):
        round_num += 1

        active_nodes = [n for n in nodes.values() if n.active]

        for node in active_nodes:
            node.pick_random()

        active_values = {n.uid: n.random_value for n in active_nodes}

        joining = {n.uid for n in active_nodes if n.is_local_max(active_values)}

        for uid in joining:
            nodes[uid].active = False
            nodes[uid].in_mis = True

        for uid in joining:
            for nb in nodes[uid].neighbours:
                if nodes[nb].active:
                    nodes[nb].active = False

    mis = sorted(uid for uid, n in nodes.items() if n.in_mis)
    return mis, round_num


def visualize(graph: Graph, mis: list[int], title: str = "Luby's MIS") -> None:
    """Draw the graph with MIS nodes in green and removed nodes in red."""
    import networkx as nx
    import matplotlib.pyplot as plt

    mis_set = set(mis)
    G = nx.Graph()
    G.add_nodes_from(graph.keys())
    for u, neighbours in graph.items():
        for v in neighbours:
            if u < v:
                G.add_edge(u, v)

    colors = ["#4CAF50" if n in mis_set else "#F44336" for n in G.nodes()]
    labels = {n: f"{n}\n(MIS)" if n in mis_set else str(n) for n in G.nodes()}

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(7, 5))
    nx.draw(G, pos, labels=labels, node_color=colors,
            node_size=900, font_size=9, font_color="white",
            edge_color="#888", width=1.5)
    plt.title(f"{title}  —  MIS size {len(mis)}: {sorted(mis)}")
    plt.show()