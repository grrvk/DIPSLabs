import random


class Node:

    def __init__(self, uid: int, neighbours: list[int]):
        self.uid = uid
        self.neighbours = list(neighbours)
        self.active = True
        self.in_mis = False
        self.random_value: float = 0.0

    def pick_random(self) -> None:
        self.random_value = random.random()

    def is_local_max(self, active_values: dict[int, float]) -> bool:
        my_key = (self.random_value, self.uid)
        return all(
            my_key > (active_values[nb], nb)
            for nb in self.neighbours
            if nb in active_values
        )