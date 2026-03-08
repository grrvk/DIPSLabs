import threading
import time
import random

from loguru import logger

class DiningPhilosophersV1:
    def __init__(self, num_philosophers=5):
        self.num_philosophers = num_philosophers

        self.semaphore = threading.Semaphore(num_philosophers - 1)
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
        self.semaphore.acquire()
        self.meal_count[philosopher_id] += 1
        logger.info(f"Philosopher {philosopher_id} eats.")
        time.sleep(random.uniform(1, 3))
        self.semaphore.release()

    def statistics(self):
        print("Solution 1 statistics")

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