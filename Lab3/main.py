from argparse import ArgumentParser, Namespace
import time
import threading

from src import solution1, solution2, solution1opt

def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "--solution",
        choices=["1", "2", "1.1"],
        default="1",
        help="Which solution to run (default: 1)",
    )

    return parser.parse_args()


def run_simulation(dining_class, n_philosophers=5, duration=15):
    print(f"Running solution {dining_class.__name__}")
    dining = dining_class(n_philosophers)

    philosophers = []
    for i in range(n_philosophers):
        thread = threading.Thread(target=dining.philosopher, args=(i,))
        thread.daemon = True
        philosophers.append(thread)
        thread.start()

    time.sleep(duration)

    dining.statistics()
    print(f"Done running solution {dining_class.__name__}\n")


if __name__ == "__main__":
    args = parse_arguments()

    if args.solution == "1":
        dining_class = solution1.DiningPhilosophersV1
    elif args.solution == "2":
        dining_class = solution2.DiningPhilosophersV2
    else:
        dining_class = solution1opt.DiningPhilosophersV1_optimized

    run_simulation(dining_class)