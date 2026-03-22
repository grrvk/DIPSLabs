import math
from argparse import ArgumentParser, Namespace

from src.shortest_path import shortest_path, visualize_directed_graph
from src.utils import generate_random_directed_graph, DIRECTED_GRAPHS


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Parallel shortest path")
    parser.add_argument(
        "--graph",
        choices=list(DIRECTED_GRAPHS.keys()) + ["random"],
        default="random",
        help="Which graph to use (default: small)",
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=6,
        help="Number of nodes for the random graph (default: 6)",
    )
    parser.add_argument(
        "--prob",
        type=float,
        default=0.4,
        help="Edge probability for the random graph (default: 0.4)",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Source vertex (default: first vertex of the chosen graph)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.graph == "random":
        graph = generate_random_directed_graph(args.nodes, args.prob, seed=42)
        graph_label = f"random graph"
        default_source = "0"
    else:
        graph = DIRECTED_GRAPHS[args.graph]
        graph_label = args.graph
        default_source = "0"

    source: str = args.source if args.source is not None else default_source

    if source not in graph:
        raise SystemExit(f"Source vertex '{source}' not in graph.")

    vertices = list(graph.keys())
    edges = [(u, v, w) for u, nbrs in graph.items() for v, w in nbrs.items()]
    print(f"Graph  : {graph_label}")
    print(f"Nodes  : {vertices}")
    print(f"Edges  : {edges}")
    print(f"Source : {source}")
    print()

    D = shortest_path(graph, source)

    print("Shortest distances from", source)
    for v in vertices:
        print(f"  D[{v}] = {'inf' if D[v] == math.inf else str(D[v])}")

    visualize_directed_graph(graph, source, D, title=f"Shortest path — {graph_label}")