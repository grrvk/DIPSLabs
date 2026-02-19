from src.functions import create_ring


def build_args():
    import argparse

    parser = argparse.ArgumentParser(description='Ring leader election')
    parser.add_argument('-n', '--nodes', type=int, default=1, help='Number of nodes')

    return parser.parse_args()

def main(args):
    create_ring(args.nodes)


if __name__ == "__main__":
    main(build_args())
