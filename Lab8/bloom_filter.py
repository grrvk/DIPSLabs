import hashlib
import math
import random
import string
import matplotlib.pyplot as plt


class BloomFilter:
    def __init__(self, m: int, k: int):
        self.m = m
        self.k = k
        self.bits = bytearray(m)

    def _hashes(self, item: str):
        # Double hashing: h_i = (h1 + i * h2) % m
        encoded = item.encode()
        h1 = int(hashlib.md5(b"seed1" + encoded).hexdigest(), 16)
        h2 = int(hashlib.md5(b"seed2" + encoded).hexdigest(), 16)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str):
        for pos in self._hashes(item):
            self.bits[pos] = 1

    def contains(self, item: str) -> bool:
        return all(self.bits[pos] for pos in self._hashes(item))


def random_string(rng: random.Random, length: int = 16) -> str:
    return "".join(rng.choices(string.ascii_letters + string.digits, k=length))


def run_experiment():
    SEED = 42
    m = 10_000
    n = 1_000
    k_values = range(1, 21)
    n_queries = 10_000

    rng = random.Random(SEED)

    in_set = [random_string(rng) for _ in range(n)]
    out_set = [random_string(rng) for _ in range(n_queries)]

    k_opt_theory = (m / n) * math.log(2)

    print(f"{'k':>4} | {'ε_empirical':>12} | {'ε_theory':>10}")
    print("-" * 35)

    empirical_rates = []
    theoretical_rates = []

    for k in k_values:
        bf = BloomFilter(m, k)
        for item in in_set:
            bf.add(item)

        false_positives = sum(1 for item in out_set if bf.contains(item))
        eps_empirical = false_positives / n_queries
        eps_theory = (1 - math.exp(-k * n / m)) ** k

        empirical_rates.append(eps_empirical)
        theoretical_rates.append(eps_theory)

        print(f"{k:>4} | {eps_empirical:>12.6f} | {eps_theory:>10.6f}")

    best_k = list(k_values)[empirical_rates.index(min(empirical_rates))]
    print()
    print(f"Optimal k (empirical minimum): {best_k}")
    print(f"Theoretical optimum k_opt = (m/n) * ln(2) = {k_opt_theory:.4f}  ≈ {round(k_opt_theory)}")

    k_list = list(k_values)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(k_list, empirical_rates, marker="o", label="Empirical FPR", linewidth=2)
    ax.plot(k_list, theoretical_rates, marker="s", linestyle="--", label="Theoretical FPR", linewidth=2)
    ax.axvline(x=k_opt_theory, color="red", linestyle=":", linewidth=1.5,
               label=f"Theoretical optimum k = {k_opt_theory:.2f}")
    ax.set_xlabel("Number of hash functions k")
    ax.set_ylabel("False Positive Rate ε")
    ax.set_title("Bloom Filter False Positive Rate vs Number of Hash Functions\n"
                 f"(m={m}, n={n})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("bloom_fpr.png", dpi=150)
    print("\nPlot saved to bloom_fpr.png")


if __name__ == "__main__":
    run_experiment()
