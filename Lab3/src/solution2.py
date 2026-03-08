import threading
import random
import time

from loguru import logger


class DiningPhilosophersV2:
    def __init__(self, num_philosophers=5):
        self.num_philosophers = num_philosophers

        self.mutex = threading.Lock()
        self.forks = [threading.Semaphore(1) for _ in range(num_philosophers)]
        self.meal_count = [0] * num_philosophers
        self.start_time = None

    def philosopher(self, philosopher_id):
        if self.start_time is None:
            self.start_time = time.time()
        while True:
            self.think(philosopher_id)
            self.eat(philosopher_id)

    def think(self, philosopher_id):
        logger.info(f"Philosopher {philosopher_id} thinks.")
        time.sleep(random.uniform(1, 3))

    def eat(self, philosopher_id):
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers

        with self.mutex:
            self.forks[left_fork].acquire()
            logger.info(f"Philosopher {philosopher_id} took left fork to eat.")

            self.forks[right_fork].acquire()
            logger.info(f"Philosopher {philosopher_id} took right fork to eat.")

        self.meal_count[philosopher_id] += 1

        logger.info(f"Philosopher {philosopher_id} eats.")
        time.sleep(random.uniform(1, 3))

        self.forks[left_fork].release()
        logger.info(f"Philosopher {philosopher_id} returned left fork.")
        self.forks[right_fork].release()
        logger.info(f"Philosopher {philosopher_id} returned right fork.")

    def statistics(self):
        print("Solution 2 statistics")

        total_meals = sum(self.meal_count)
        runtime = time.time() - self.start_time if self.start_time else 0

        print(f"Runtime: {runtime:.1f} seconds")
        print(f"Total meals eaten: {total_meals}")
        print(f"Average meals/second: {total_meals / runtime:.2f}" if runtime > 0 else "N/A")
        print("\nPer philosopher:")
        for i, meals in enumerate(self.meal_count):
            print(f"  Philosopher {i}: {meals} meals")

        if self.meal_count:
            max_meals = max(self.meal_count)
            min_meals = min(self.meal_count)
            if max_meals > 0:
                fairness = min_meals / max_meals
                print(f"\nFairness ratio (min/max): {fairness:.2f}")
        print()