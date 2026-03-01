import random
import networkx as nx
import matplotlib.pyplot as plt

from src.models import Tree, MISResult


BASE: dict[str, tuple[int, list[tuple[int, int]]]] = {
    "star": (6, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]),
    "binary": (7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]),
}


def get_base(name: str) -> Tree:
    if name not in BASE:
        raise ValueError(f"Unknown base '{name}'. Choose from: {list(BASE.keys())}")
    n, edges = BASE[name]
    return Tree.from_edges(n, edges)


def generate_random_tree(n: int, seed: int | None = 42) -> Tree:
    if n < 1:
        raise ValueError("Tree must have at least 1 node")
    if n == 1:
        return Tree.from_edges(1, [])
    rng = random.Random(seed)
    edges = []
    for i in range(1, n):
        parent = rng.randint(0, i - 1)
        edges.append((i, parent))
    return Tree.from_edges(n, edges)


def plot_tree(tree: Tree) -> None:
    graph = nx.Graph()
    graph.add_nodes_from(range(tree.n))
    for node in tree.nodes:
        for child_id in node.children:
            graph.add_edge(node.id, child_id)

    try:
        pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
    except ImportError:
        pos = nx.spring_layout(graph)

    plt.figure(figsize=(max(6, tree.n), 5))
    nx.draw(
        graph, pos,
        with_labels=True,
        labels={v: str(v) for v in range(tree.n)},
        node_size=800,
        font_color="white",
        font_weight="bold",
        edge_color="gray",
    )

    title = f"Tree (n={tree.n})"
    plt.title(title)
    plt.show()


def solve_mis(tree: Tree) -> MISResult:
    nodes = tree.nodes

    if tree.n == 0:
        return MISResult(size=0, nodes=[])
    if tree.n == 1:
        return MISResult(size=1, nodes=[0])

    order: list[int] = []
    stack: list[tuple[int, bool]] = [(0, False)]
    while stack:
        v, processed = stack.pop()
        if processed:
            order.append(v)
            continue
        stack.append((v, True))
        for child_id in nodes[v].children:
            stack.append((child_id, False))

    for v in order:
        node = nodes[v]
        node.mis_size_if_excluded = sum(
            max(nodes[c].mis_size_if_excluded, nodes[c].mis_size_if_included)
            for c in node.children
        )
        node.mis_size_if_included = 1 + sum(nodes[c].mis_size_if_excluded for c in node.children)

    root = nodes[0]
    mis_ids: list[int] = []
    recon: list[tuple[int, bool]] = [(0, root.mis_size_if_included >= root.mis_size_if_excluded)]
    while recon:
        v, include = recon.pop()
        node = nodes[v]
        if include:
            mis_ids.append(v)
        for child_id in node.children:
            child = nodes[child_id]
            child_include = False if include else (child.mis_size_if_included >= child.mis_size_if_excluded)
            recon.append((child_id, child_include))

    size = max(root.mis_size_if_excluded, root.mis_size_if_included)
    return MISResult(size=size, nodes=sorted(mis_ids))