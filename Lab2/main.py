import argparse

from src.functions import generate_random_tree, get_base, solve_mis, BASE, plot_tree


def build_args():
    parser = argparse.ArgumentParser(description="Maximum Independent Set in a tree")

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "-n", type=int, default=10,
        help="Number of nodes for random tree generation",
    )
    source.add_argument(
        "--base", choices=list(BASE.keys()),
        help="Use a test tree",
    )

    return parser.parse_args()


def main():
    args = build_args()

    if args.base:
        tree = get_base(args.base)
    else:
        tree = generate_random_tree(args.nodes)

    plot_tree(tree)
    result = solve_mis(tree)

    print(f"MIS size: {result.size}")
    print(f"MIS nodes: {result.nodes}")


if __name__ == "__main__":
    main()