from argparse import ArgumentParser, Namespace

from src.functions import GRAPHS, generate_random_graph, run_luby, visualize


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Luby's MIS algorithm")
    parser.add_argument(
        "--graph",
        choices=list(GRAPHS.keys()) + ["random"],
        default="path5",
        help="Which graph to use (default: path5)",
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=10,
        help="Number of nodes for the random graph (default: 10)",
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
        graph = generate_random_graph(args.nodes, args.prob)
    else:
        graph = GRAPHS[args.graph]

    nodes = sorted(graph.keys())
    edges = [(u, v) for u in nodes for v in graph[u] if u < v]
    print(f"Graph : {len(nodes)} nodes, {len(edges)} edges")
    print(f"Edges : {edges}")

    mis, _ = run_luby(graph)

    print(f"\nMaximal Independent Set")
    print(f"  Size  : {len(mis)}")
    print(f"  Nodes : {mis}")

    visualize(graph, mis, title=args.graph)