from argparse import ArgumentParser, Namespace

from src.graph_coloring import color_graph_parallel, visualize_undirected_graph
from src.utils import GRAPHS, generate_random_undirected_graph


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Parallel graph coloring minimization")
    parser.add_argument(
        "--graph",
        choices=list(GRAPHS.keys()) + ["random"],
        default="random",
        help="Which graph to use (default: petersen)",
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=8,
        help="Number of nodes for the random graph (default: 8)",
    )
    parser.add_argument(
        "--prob",
        type=float,
        default=0.4,
        help="Edge probability for the random graph (default: 0.4)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.graph == "random":
        adj = generate_random_undirected_graph(args.nodes, args.prob, seed=42)
        graph_label = f"random"
    else:
        adj = GRAPHS[args.graph]
        graph_label = args.graph

    vertices = list(adj.keys())
    edges = [(u, v) for u, nbrs in adj.items() for v in nbrs if u < v]
    print(f"Graph  : {graph_label}")
    print(f"Nodes  : {vertices}")
    print(f"Edges  : {edges}")
    print()

    colors, rounds = color_graph_parallel(adj)

    num_colors = max(colors.values())
    print(f"Converged in {rounds} round(s), {num_colors} color(s) used")
    print()
    print("Final coloring:")
    for v in vertices:
        print(f"  vertex {v} → color {colors[v]}")

    visualize_undirected_graph(adj, colors, title=f"Graph coloring — {graph_label}")